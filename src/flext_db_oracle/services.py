"""Generic Oracle Database services delegating to flext-core and SQLAlchemy.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import hashlib
import time
from collections.abc import Generator
from contextlib import contextmanager
from importlib import import_module
from typing import Self
from urllib.parse import quote_plus

from flext_core import r, t
from flext_core.service import FlextService
from flext_db_oracle.models import m as m_db_oracle
from flext_db_oracle.settings import FlextDbOracleSettings
from pydantic import BaseModel, ConfigDict, RootModel, TypeAdapter, ValidationError


class _StrictIntValue(BaseModel):
    """Strict integer payload model."""

    model_config = ConfigDict(strict=True)
    value: int


class _CountValue(BaseModel):
    """Count payload accepting integer or numeric string."""

    value: int | str


class _ObjectRows(RootModel[list[object]]):
    """Pydantic root model for generic list payloads."""

    root: list[object]


_STRING_LIST_ADAPTER = TypeAdapter(list[str])


def _validate_config_map(value: object) -> t.ConfigMap | None:
    """Validate arbitrary mapping input as ConfigMap."""
    try:
        return t.ConfigMap.model_validate(value)
    except ValidationError:
        return None


def _normalize_params(params: t.ConfigMap | None) -> t.ConfigMap:
    """Normalize optional parameters into ConfigMap."""
    if params is not None:
        return params
    return t.ConfigMap(root={})


def _parse_rowcount(value: object) -> int:
    """Parse strict integer rowcount via Pydantic."""
    try:
        return _StrictIntValue.model_validate({"value": value}).value
    except ValidationError:
        return 0


def _parse_count_value(value: object) -> int:
    """Parse row count value accepting int or numeric string."""
    try:
        validated = _CountValue.model_validate({"value": value}).value
    except ValidationError:
        return 0

    try:
        return int(validated)
    except (TypeError, ValueError):
        return 0


def _normalize_singer_type(value: str | list[str]) -> str:
    """Normalize Singer type input to a single string value."""
    try:
        values = _STRING_LIST_ADAPTER.validate_python(value)
    except ValidationError:
        return str(value)
    return values[0] if values else "string"


def _extract_object_rows(value: object) -> list[object]:
    """Extract list payload using Pydantic validation."""
    try:
        return _ObjectRows.model_validate(value).root
    except ValidationError:
        return []


def _sqlalchemy_create_engine(url: str) -> object:
    """Create SQLAlchemy engine via runtime import to keep type boundaries explicit."""
    sqlalchemy_module = import_module("sqlalchemy")
    create_engine_func = getattr(sqlalchemy_module, "create_engine", None)
    if not callable(create_engine_func):
        msg = "sqlalchemy.create_engine unavailable"
        raise TypeError(msg)
    return create_engine_func(
        url,
        pool_pre_ping=True,
        pool_recycle=3600,
        echo=False,
    )


def _sqlalchemy_text(statement: str) -> object:
    """Build SQL text object via runtime import."""
    sqlalchemy_module = import_module("sqlalchemy")
    text_func = getattr(sqlalchemy_module, "text", None)
    if not callable(text_func):
        msg = "sqlalchemy.text unavailable"
        raise TypeError(msg)
    return text_func(statement)


def _engine_connect(engine: object) -> object:
    """Open connection context manager from engine."""
    connect_method = getattr(engine, "connect", None)
    if not callable(connect_method):
        msg = "Database engine does not expose connect()"
        raise TypeError(msg)
    return connect_method()


def _engine_begin(engine: object) -> object:
    """Open transaction context manager from engine."""
    begin_method = getattr(engine, "begin", None)
    if not callable(begin_method):
        msg = "Database engine does not expose begin()"
        raise TypeError(msg)
    return begin_method()


def _context_enter(context_manager: object) -> object:
    """Enter dynamic context manager and return inner object."""
    enter_method = getattr(context_manager, "__enter__", None)
    if not callable(enter_method):
        msg = "Context manager does not expose __enter__()"
        raise TypeError(msg)
    return enter_method()


def _context_exit(context_manager: object) -> None:
    """Exit dynamic context manager safely."""
    exit_method = getattr(context_manager, "__exit__", None)
    if callable(exit_method):
        _ = exit_method(None, None, None)


def _engine_dispose(engine: object) -> None:
    """Dispose engine resources through dynamic method lookup."""
    dispose_method = getattr(engine, "dispose", None)
    if callable(dispose_method):
        dispose_method()


def _connection_execute(
    connection: object,
    statement: object,
    parameters: t.ConfigMap | None = None,
) -> object:
    """Execute statement on dynamic SQL connection."""
    execute_method = getattr(connection, "execute", None)
    if not callable(execute_method):
        msg = "Database connection does not expose execute()"
        raise TypeError(msg)
    normalized_params = _normalize_params(parameters)
    return execute_method(statement, normalized_params.root)


class FlextDbOracleServices(FlextService[FlextDbOracleSettings]):
    """Generic Oracle database services using flext-core patterns."""

    def __init__(self, config: FlextDbOracleSettings) -> None:
        """Initialize with configuration."""
        super().__init__()
        self._db_config = config  # Use separate attribute for Oracle-specific config
        self._engine: object | None = None
        self._operations: list[m_db_oracle.DbOracle.OperationRecord] = []

    def _build_connection_url(self) -> r[str]:
        """Build Oracle connection URL from configuration."""
        try:
            password = self._db_config.password.get_secret_value()
            if not password:
                return r.fail("Password is required for database connection")
            encoded_password = quote_plus(password)
            db_id = self._db_config.sid or self._db_config.service_name
            url = f"oracle+oracledb://{self._db_config.username}:{encoded_password}@{self._db_config.host}:{self._db_config.port}/{db_id}"
            return r.ok(url)
        except Exception as e:
            return r.fail(f"Failed to build connection URL: {e}")

    def _get_engine(self) -> r[object]:
        """Get database engine."""
        if not self._engine or not self.is_connected():
            return r.fail("Not connected to database")
        return r.ok(self._engine)

    # Connection Management
    def connect(self) -> r[Self]:
        """Establish Oracle database connection."""
        url_result = self._build_connection_url()
        if url_result.is_failure:
            return r.fail(
                url_result.error or "Failed to build connection URL",
            )
        self._engine = _sqlalchemy_create_engine(url_result.value)
        # Test connection
        try:
            connect_ctx = _engine_connect(self._engine)
            conn = _context_enter(connect_ctx)
            try:
                _ = _connection_execute(conn, _sqlalchemy_text("SELECT 1 FROM dual"))
            finally:
                _context_exit(connect_ctx)
            self.logger.info(f"Connected to Oracle database: {self._db_config.host}")
            return r.ok(self)
        except Exception as e:
            self.logger.exception("Oracle connection failed")
            return r.fail(f"Connection failed: {e}")

    def disconnect(self) -> r[None]:
        """Disconnect from Oracle database."""
        engine = self._engine
        if engine is not None:
            _engine_dispose(engine)
            self._engine = None
            self.logger.info("Disconnected from Oracle database")
        return r[None].ok(None)

    def is_connected(self) -> bool:
        """Check if connected to Oracle database."""
        return self._engine is not None

    def test_connection(self) -> r[bool]:
        """Test Oracle database connection."""
        engine_result = self._get_engine()
        if engine_result.is_failure:
            return r.fail("Not connected to database")
        try:
            connect_ctx = _engine_connect(engine_result.value)
            conn = _context_enter(connect_ctx)
            try:
                _ = _connection_execute(conn, _sqlalchemy_text("SELECT 1 FROM dual"))
            finally:
                _context_exit(connect_ctx)
            return r.ok(True)
        except Exception as e:
            return r.fail(f"Connection test failed: {e}")

    @contextmanager
    def get_connection(self) -> Generator[object]:
        """Get database connection context manager."""
        engine = self._engine
        if engine is None:
            msg = "No database connection established"
            raise RuntimeError(msg)
        connect_ctx = _engine_connect(engine)
        connection = _context_enter(connect_ctx)
        try:
            yield connection
        finally:
            _context_exit(connect_ctx)

    def transaction(self) -> Generator[object]:
        """Get transaction context for database operations."""
        engine = self._engine
        if engine is None:
            msg = "No database connection established"
            raise RuntimeError(msg)
        transaction_ctx = _engine_begin(engine)
        transaction = _context_enter(transaction_ctx)
        try:
            yield transaction
        finally:
            _context_exit(transaction_ctx)

    # Query Operations
    def execute_query(
        self,
        sql: str,
        params: t.ConfigMap | None = None,
    ) -> r[list[t.Dict]]:
        """Execute SQL query and return results."""
        engine_result = self._get_engine()
        if engine_result.is_failure:
            return r.fail(
                engine_result.error or "Failed to get database engine",
            )
        try:
            connect_ctx = _engine_connect(engine_result.value)
            conn = _context_enter(connect_ctx)
            try:
                result = _connection_execute(conn, _sqlalchemy_text(sql), params)
                rows: list[t.Dict] = self._normalize_query_rows(result)
                return r.ok(rows)
            finally:
                _context_exit(connect_ctx)
        except Exception as e:
            return r.fail(f"Query execution failed: {e}")

    def execute_statement(
        self,
        sql: str,
        params: t.ConfigMap | None = None,
    ) -> r[int]:
        """Execute SQL statement and return affected rows."""
        engine_result = self._get_engine()
        if engine_result.is_failure:
            return r.fail(
                engine_result.error or "Failed to get database engine",
            )
        try:
            connect_ctx = _engine_connect(engine_result.value)
            conn = _context_enter(connect_ctx)
            try:
                result = _connection_execute(conn, _sqlalchemy_text(sql), params)
                rowcount_raw = getattr(result, "rowcount", 0)
                rowcount = _parse_rowcount(rowcount_raw)
                return r.ok(rowcount)
            finally:
                _context_exit(connect_ctx)
        except Exception as e:
            return r.fail(f"Statement execution failed: {e}")

    def execute_many(
        self,
        sql: str,
        params_list: list[t.ConfigMap],
    ) -> r[int]:
        """Execute SQL statement multiple times."""
        engine_result = self._get_engine()
        if engine_result.is_failure:
            return r.fail(
                engine_result.error or "Failed to get database engine",
            )
        try:
            connect_ctx = _engine_connect(engine_result.value)
            conn = _context_enter(connect_ctx)
            try:
                total_affected = 0
                for params in params_list:
                    result = _connection_execute(conn, _sqlalchemy_text(sql), params)
                    rowcount_raw = getattr(result, "rowcount", 0)
                    total_affected += _parse_rowcount(rowcount_raw)
                return r.ok(total_affected)
            finally:
                _context_exit(connect_ctx)
        except Exception as e:
            return r.fail(f"Bulk execution failed: {e}")

    def fetch_one(
        self,
        sql: str,
        params: t.ConfigMap | None = None,
    ) -> r[t.Dict | None]:
        """Execute query and return first result."""
        return self.execute_query(sql, params).map(
            lambda rows: rows[0] if rows else None,
        )

    # Schema Operations
    def get_schemas(self) -> r[list[str]]:
        """Get list of Oracle schemas."""
        sql = "SELECT username as schema_name FROM all_users WHERE username NOT IN ('SYS', 'SYSTEM', 'ANONYMOUS', 'XDB', 'CTXSYS', 'MDSYS', 'WMSYS') ORDER BY username"
        return self.execute_query(sql).map(
            lambda rows: [str(row.root["schema_name"]) for row in rows],
        )

    def get_tables(self, schema: str | None = None) -> r[list[str]]:
        """Get list of tables in Oracle schema."""
        if schema:
            sql = "SELECT table_name FROM all_tables WHERE owner = UPPER(:schema_name) ORDER BY table_name"
            params: t.ConfigMap | None = t.ConfigMap(root={"schema_name": schema})
        else:
            sql = "SELECT table_name FROM user_tables ORDER BY table_name"
            params = None
        return self.execute_query(sql, params).map(
            lambda rows: [str(row.root["table_name"]) for row in rows],
        )

    def get_columns(
        self,
        table_name: str,
        schema_name: str | None = None,
    ) -> r[list[m_db_oracle.DbOracle.Column]]:
        """Get column information for Oracle table."""
        if schema_name:
            sql = """
SELECT column_name, data_type, data_length, data_precision, data_scale, nullable
FROM all_tab_columns
WHERE table_name = UPPER(:table_name) AND owner = UPPER(:schema_name)
ORDER BY column_id
"""
            params = t.ConfigMap(
                root={
                    "table_name": table_name,
                    "schema_name": schema_name,
                }
            )
        else:
            sql = """
SELECT column_name, data_type, data_length, data_precision, data_scale, nullable
FROM user_tab_columns
WHERE table_name = UPPER(:table_name)
ORDER BY column_id
"""
            params = t.ConfigMap(root={"table_name": table_name})
        return self.execute_query(sql, params).map(
            lambda rows: [
                m_db_oracle.DbOracle.Column(
                    name=str(row.root.get("column_name", "")),
                    data_type=str(row.root.get("data_type", "")),
                    nullable=str(row.root.get("nullable", "Y")) == "Y",
                    default_value=str(row.root.get("data_default", "")),
                )
                for row in rows
            ]
        )

    def get_primary_keys(
        self,
        table_name: str,
        schema: str | None = None,
    ) -> r[list[str]]:
        """Get primary key column names for specified table."""
        try:
            if schema:
                sql = """
                SELECT column_name
                FROM all_constraints c, all_cons_columns cc
                WHERE c.constraint_type = 'P'
                AND c.constraint_name = cc.constraint_name
                AND c.table_name = UPPER(:table_name)
                AND c.owner = UPPER(:schema)
                ORDER BY cc.position
                """
                params = t.ConfigMap(
                    root={
                        "table_name": table_name,
                        "schema": schema,
                    }
                )
            else:
                sql = """
                SELECT column_name
                FROM user_constraints c, user_cons_columns cc
                WHERE c.constraint_type = 'P'
                AND c.constraint_name = cc.constraint_name
                AND c.table_name = UPPER(:table_name)
                ORDER BY cc.position
                """
                params = t.ConfigMap(root={"table_name": table_name})

            return self.execute_query(sql, params).map(
                lambda rows: [str(row.root["column_name"]) for row in rows],
            )
        except Exception as e:
            return r.fail(f"Failed to get primary keys: {e}")

    def get_table_metadata(
        self,
        table_name: str,
        schema: str | None = None,
    ) -> r[m_db_oracle.DbOracle.TableMetadata]:
        """Get complete table metadata."""
        try:
            return self.get_columns(table_name, schema).flat_map(
                lambda columns: self.get_primary_keys(table_name, schema).map(
                    lambda pk: m_db_oracle.DbOracle.TableMetadata(
                        table_name=table_name,
                        schema_name=schema or "",
                        columns=[
                            {
                                "name": column.name,
                                "data_type": column.data_type,
                                "nullable": column.nullable,
                                "default_value": column.default_value,
                            }
                            for column in columns
                        ],
                        primary_keys=pk,
                    ),
                ),
            )
        except Exception as e:
            return r.fail(f"Failed to get table metadata: {e}")

    # Service
    def execute(self, **_kwargs: t.JsonValue) -> r[FlextDbOracleSettings]:
        """Execute main domain service operation - return config."""
        test_result = self.test_connection()
        if test_result.is_success:
            return r.ok(self._db_config)
        return r.fail(test_result.error or "Connection test failed")

    # Placeholder methods for compatibility - delegate to simpler implementations
    def build_select(
        self,
        table_name: str,
        schema_name: str | None = None,
        columns: list[str] | None = None,
        conditions: t.ConfigMap | None = None,
    ) -> r[str]:
        """Build SELECT query - simplified implementation."""
        cols = ", ".join(columns) if columns else "*"
        where = f" WHERE {conditions}" if conditions else ""
        schema = f"{schema_name}." if schema_name else ""
        sql = f"SELECT {cols} FROM {schema}{table_name}{where}"  # nosec B608
        return r.ok(sql)

    def build_insert_statement(
        self,
        table_name: str,
        columns: list[str],
        schema: str | None = None,
        returning_columns: list[str] | None = None,
    ) -> r[str]:
        """Build INSERT statement - simplified."""
        cols = ", ".join(columns)
        vals = ", ".join(f":{col}" for col in columns)
        schema_prefix = f"{schema}." if schema else ""
        sql = f"INSERT INTO {schema_prefix}{table_name} ({cols}) VALUES ({vals})"  # nosec B608
        if returning_columns:
            ret = ", ".join(returning_columns)
            sql += f" RETURNING {ret}"
        return r.ok(sql)

    def build_update_statement(
        self,
        table_name: str,
        set_columns: list[str],
        where_columns: list[str],
        schema: str | None = None,
    ) -> r[str]:
        """Build UPDATE statement - simplified."""
        sets = ", ".join(f"{col} = :{col}" for col in set_columns)
        wheres = " AND ".join(f"{col} = :where_{col}" for col in where_columns)
        schema_prefix = f"{schema}." if schema else ""
        sql = f"UPDATE {schema_prefix}{table_name} SET {sets} WHERE {wheres}"  # nosec B608
        return r.ok(sql)

    def build_delete_statement(
        self,
        table_name: str,
        where_columns: list[str],
        schema: str | None = None,
    ) -> r[str]:
        """Build DELETE statement - simplified."""
        wheres = " AND ".join(f"{col} = :{col}" for col in where_columns)
        schema_prefix = f"{schema}." if schema else ""
        sql = f"DELETE FROM {schema_prefix}{table_name} WHERE {wheres}"  # nosec B608
        return r.ok(sql)

    def build_create_index_statement(self, _config: t.JsonValue) -> r[str]:
        """Build CREATE INDEX statement - placeholder."""
        return r.ok("CREATE INDEX statement")

    def create_table_ddl(
        self,
        table_name: str,
        columns: list[m_db_oracle.DbOracle.Column],
        schema: str | None = None,
    ) -> r[str]:
        """Generate CREATE TABLE DDL - simplified."""
        col_defs: list[str] = []
        for col in columns:
            name = col.name or "unknown"
            data_type = col.data_type or "VARCHAR2(255)"
            nullable = "" if col.nullable else " NOT NULL"
            col_defs.append(f"{name} {data_type}{nullable}")
        schema_prefix = f"{schema}." if schema else ""
        ddl = f"CREATE TABLE {schema_prefix}{table_name} (\n  {', '.join(col_defs)}\n)"
        return r.ok(ddl)

    def drop_table_ddl(
        self,
        table_name: str,
        schema: str | None = None,
    ) -> r[str]:
        """Generate DROP TABLE DDL."""
        schema_prefix = f"{schema}." if schema else ""
        ddl = f"DROP TABLE {schema_prefix}{table_name}"
        return r.ok(ddl)

    def convert_singer_type(
        self,
        singer_type: str | list[str] = "string",
        _format_hint: str | None = None,
    ) -> r[str]:
        """Convert Singer type to Oracle type - simplified."""
        singer_type = _normalize_singer_type(singer_type)
        type_map = {
            "string": "VARCHAR2(255)",
            "integer": "NUMBER",
            "number": "NUMBER",
            "boolean": "NUMBER(1)",
        }
        oracle_type = type_map.get(singer_type, "VARCHAR2(255)")
        return r.ok(oracle_type)

    def map_singer_schema(
        self,
        singer_schema: m_db_oracle.DbOracle.SingerSchema,
    ) -> r[m_db_oracle.DbOracle.TypeMapping]:
        """Map Singer schema to Oracle types - simplified."""
        mapping = t.ConfigMap(root={})
        for field_name, field_def in singer_schema.properties.items():
            conversion = self.convert_singer_type(field_def.type)
            if conversion.is_success:
                mapping.root[field_name] = conversion.value
        normalized_mapping = {key: str(value) for key, value in mapping.items()}
        return r.ok(m_db_oracle.DbOracle.TypeMapping(mapping=normalized_mapping))

    # Placeholder methods for compatibility
    def generate_query_hash(
        self,
        sql: str = "",
        params: t.ConfigMap | None = None,
    ) -> r[str]:
        """Generate query hash - simplified."""
        hash_input = f"{sql}_{params!s}"
        return r.ok(hashlib.sha256(hash_input.encode()).hexdigest()[:16])

    def get_connection_status(
        self,
    ) -> r[m_db_oracle.DbOracle.ConnectionStatus]:
        """Get connection status - simplified."""
        return r.ok(
            m_db_oracle.DbOracle.ConnectionStatus(
                is_connected=self.is_connected(),
                host=self._db_config.host,
                port=self._db_config.port,
                service_name=self._db_config.service_name,
                username=self._db_config.username,
                error_message="" if self.is_connected() else "Connection unavailable",
            )
        )

    @staticmethod
    def record_metric(
        _name: str,
        _value: float,
        _tags: t.ConfigMap | None = None,
    ) -> r[None]:
        """Record metric - placeholder."""
        return r[None].ok(None)

    def get_metrics(self) -> r[m_db_oracle.DbOracle.HealthStatus]:
        """Get metrics - placeholder."""
        return r.ok(
            m_db_oracle.DbOracle.HealthStatus(
                status="connected" if self.is_connected() else "disconnected",
                timestamp=self._get_current_timestamp(),
            )
        )

    def health_check(self) -> r[m_db_oracle.DbOracle.HealthStatus]:
        """Perform health check."""
        return r.ok(
            m_db_oracle.DbOracle.HealthStatus(
                status="healthy" if self.is_connected() else "unhealthy",
                timestamp=self._get_current_timestamp(),
            )
        )

    def register_plugin(self, _name: str, _plugin: t.JsonValue) -> r[None]:
        """Register plugin - placeholder."""
        return r[None].ok(None)

    def unregister_plugin(self, _name: str) -> r[None]:
        """Unregister plugin - placeholder."""
        return r[None].ok(None)

    def list_plugins(self) -> r[t.ConfigMap]:
        """List plugins - placeholder."""
        return r[t.ConfigMap].ok(t.ConfigMap(root={}))

    def get_plugin(self, _name: str) -> r[t.JsonValue]:
        """Get plugin - placeholder implementation.

        Args:
            _name: Plugin name (reserved for future implementation)

        """
        return r[t.JsonValue].ok(True)

    def get_primary_key_columns(
        self,
        table_name: str,
        schema_name: str | None = None,
    ) -> r[list[str]]:
        """Alias for get_primary_keys."""
        return self.get_primary_keys(table_name, schema_name)

    def get_table_row_count(
        self,
        table_name: str,
        schema_name: str | None = None,
    ) -> r[int]:
        """Get row count - simplified."""
        try:
            schema = f"{schema_name}." if schema_name else ""
            sql = f"SELECT COUNT(*) as count FROM {schema}{table_name}"  # nosec B608
            return self.execute_query(sql).map(
                self._parse_count_from_rows,
            )
        except Exception as e:
            return r.fail(f"Failed to get row count: {e}")

    def track_operation(
        self,
        operation_type: str = "",
        duration: float = 0.0,
        *,
        success: bool = True,
        metadata: t.ConfigMap | None = None,
    ) -> r[None]:
        """Track database operation for monitoring."""
        try:
            metadata_value = metadata or t.ConfigMap(root={})
            operation = m_db_oracle.DbOracle.OperationRecord(
                operation_type=operation_type,
                duration=duration,
                success=success,
                metadata_info=str(metadata_value),
                timestamp=self._get_current_timestamp(),
            )
            self._operations.append(operation)
            return r[None].ok(None)
        except Exception as e:
            return r.fail(f"Failed to track operation: {e}")

    def get_operations(self) -> r[list[m_db_oracle.DbOracle.OperationRecord]]:
        """Get tracked operations."""
        return r.ok(self._operations.copy())

    def _normalize_query_rows(self, query_result: object) -> list[t.Dict]:
        """Normalize SQLAlchemy query result rows into typed mapping models."""
        mappings_method = getattr(query_result, "mappings", None)
        if not callable(mappings_method):
            return []
        mapping_result = mappings_method()
        return [
            self._normalize_row(row)
            for row in self._extract_mapping_rows(mapping_result)
        ]

    def _extract_mapping_rows(self, mapping_result: object) -> list[object]:
        """Extract all SQLAlchemy mapping rows from a mapping result."""
        all_method = getattr(mapping_result, "all", None)
        if not callable(all_method):
            return []
        rows = all_method()
        return _extract_object_rows(rows)

    def _normalize_row(self, row: object) -> t.Dict:
        """Normalize a single SQLAlchemy mapping row into a typed map."""
        mapping = getattr(row, "_mapping", None)
        validated_mapping = _validate_config_map(mapping)
        if validated_mapping is None:
            return t.Dict(root={})
        return t.Dict(
            root={str(key): value for key, value in validated_mapping.items()}
        )

    def _parse_count_from_rows(self, rows: list[t.Dict]) -> int:
        """Parse COUNT(*) value from normalized query rows."""
        if not rows:
            return 0
        count_value = rows[0].root.get("count")
        if count_value is None:
            return 0
        return _parse_count_value(count_value)

    def _get_current_timestamp(self) -> str:
        """Get current timestamp for operation tracking."""
        return str(int(time.time()))


# Export the single refactored class following flext-core pattern
__all__ = ["FlextDbOracleServices"]
