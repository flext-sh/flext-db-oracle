"""Generic Oracle Database services delegating to flext-core and SQLAlchemy.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import hashlib
import time
from collections.abc import Generator, Mapping, Sequence
from contextlib import contextmanager
from importlib import import_module
from typing import Self, override
from urllib.parse import quote_plus

import oracledb
from flext_core import FlextService, r, t
from pydantic import BaseModel, ConfigDict, RootModel, TypeAdapter, ValidationError
from sqlalchemy.exc import (
    DatabaseError as SQLAlchemyDatabaseError,
    OperationalError as SQLAlchemyOperationalError,
    SQLAlchemyError,
)

from flext_db_oracle.models import FlextDbOracleModels, m
from flext_db_oracle.settings import FlextDbOracleSettings

OracleDatabaseError: type[Exception] = oracledb.DatabaseError
OracleInterfaceError: type[Exception] = oracledb.InterfaceError


class _StrictIntValue(BaseModel):
    """Strict integer payload model."""

    model_config = ConfigDict(strict=True)
    value: int


class _CountValue(BaseModel):
    """Count payload accepting integer or numeric string."""

    value: int | str


class _ObjectRows(RootModel[list[t.ContainerValue]]):
    """Pydantic root model for generic list payloads."""

    root: list[t.ContainerValue]


_STRING_LIST_ADAPTER = TypeAdapter(list[str])


def _validate_config_map(value: object) -> m.ConfigMap | None:
    """Validate arbitrary mapping input as ConfigMap."""
    try:
        return m.ConfigMap.model_validate(value)
    except ValidationError:
        return None


def _normalize_params(params: m.ConfigMap | None) -> m.ConfigMap:
    """Normalize optional parameters into ConfigMap."""
    if params is not None:
        return params
    return m.ConfigMap(root={})


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


def _extract_object_rows(value: object) -> list[t.ContainerValue]:
    """Extract list payload using Pydantic validation."""
    return _ObjectRows.model_validate(value).root


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
    parameters: m.ConfigMap | None = None,
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
        self._db_config = config
        self._config = config
        self._engine: object | None = None
        self._operations: list[FlextDbOracleModels.DbOracle.OperationRecord] = []
        self._plugins: dict[str, t.JsonValue] = {}
        self._metrics: dict[str, t.JsonValue] = {}

    def build_create_index_statement(self, _config: t.JsonValue) -> r[str]:
        """Build Oracle CREATE INDEX statement from configuration."""
        try:
            config = FlextDbOracleModels.DbOracle.CreateIndexConfig.model_validate(
                _config,
            )
            if not config.columns:
                return r.fail("Index definition requires at least one column")

            schema_prefix = f"{config.schema_name}." if config.schema_name else ""
            unique_prefix = "UNIQUE " if config.unique else ""
            columns = ", ".join(config.columns)
            sql = (
                f"CREATE {unique_prefix}INDEX {config.index_name} "
                f"ON {schema_prefix}{config.table_name} ({columns})"
            )

            if config.tablespace:
                sql = f"{sql} TABLESPACE {config.tablespace}"
            if config.parallel > 1:
                sql = f"{sql} PARALLEL {config.parallel}"
            return r.ok(sql)
        except ValidationError as e:
            return r.fail(f"Invalid CREATE INDEX config: {e}")

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

    def build_select(
        self,
        table_name: str,
        columns: list[str] | None = None,
        conditions: m.ConfigMap | t.ConfigurationMapping | None = None,
        schema_name: str | None = None,
    ) -> r[str]:
        """Build SELECT query - simplified implementation."""
        typed_conditions = (
            conditions
            if isinstance(conditions, m.ConfigMap) or conditions is None
            else m.ConfigMap.model_validate(conditions)
        )
        cols = ", ".join(columns) if columns else "*"
        if typed_conditions and typed_conditions.root:
            where_pairs = [f"{k} = :{k}" for k in typed_conditions.root]
            where = f" WHERE {' AND '.join(where_pairs)}"
        else:
            where = ""
        schema_prefix = f"{schema_name.upper()}." if schema_name else ""
        sql = f"SELECT {cols} FROM {schema_prefix}{table_name.upper()}{where}"  # nosec B608
        return r.ok(sql)

    def build_update_statement(
        self,
        table_name: str,
        set_columns: list[str],
        where_columns: list[str],
        schema: str | None = None,
    ) -> r[str]:
        """Build UPDATE statement - simplified."""
        sets = ", ".join(f"{col}=:{col}" for col in set_columns)
        wheres = " AND ".join(f"{col} = :{col}" for col in where_columns)
        schema_prefix = f"{schema}." if schema else ""
        sql = f"UPDATE {schema_prefix}{table_name} SET {sets} WHERE {wheres}"  # nosec B608
        return r.ok(sql)

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
        except (
            OracleDatabaseError,
            OracleInterfaceError,
            ConnectionError,
            SQLAlchemyDatabaseError,
            SQLAlchemyOperationalError,
            SQLAlchemyError,
            OSError,
        ) as e:
            self._engine = None
            self.logger.exception("Oracle connection failed")
            return r.fail(f"Connection failed: {e}")

    def convert_singer_type(
        self,
        singer_type: str | list[str] = "string",
        _format_hint: str | None = None,
    ) -> r[str]:
        """Convert Singer type to Oracle type - simplified."""
        singer_type = _normalize_singer_type(singer_type)
        if _format_hint == "date-time":
            return r.ok("TIMESTAMP")
        type_map = {
            "string": "VARCHAR2(4000)",
            "integer": "NUMBER(38)",
            "number": "NUMBER",
            "boolean": "NUMBER(1)",
            "date-time": "TIMESTAMP",
        }
        oracle_type = type_map.get(singer_type, "VARCHAR2(255)")
        return r.ok(oracle_type)

    def create_table_ddl(
        self,
        table_name: str,
        columns: Sequence[FlextDbOracleModels.DbOracle.Column | t.ConfigurationMapping],
        schema: str | None = None,
    ) -> r[str]:
        """Generate CREATE TABLE DDL - simplified."""
        col_defs: list[str] = []
        primary_keys: list[str] = []
        for col in columns:
            if isinstance(col, FlextDbOracleModels.DbOracle.Column):
                name = col.name or "unknown"
                data_type = col.data_type or "VARCHAR2(255)"
                nullable = "" if col.nullable else " NOT NULL"
                if getattr(col, "primary_key", False):
                    primary_keys.append(name)
            else:
                name_value = col.get("name") or col.get("column_name")
                data_type_value = col.get("data_type")
                nullable_value = col.get("nullable", True)
                name = str(name_value) if name_value is not None else "unknown"
                data_type = (
                    str(data_type_value)
                    if data_type_value is not None
                    else "VARCHAR2(255)"
                )
                nullable = "" if bool(nullable_value) else " NOT NULL"
                if bool(col.get("primary_key", False)):
                    primary_keys.append(name)
            col_defs.append(f"{name} {data_type}{nullable}")
        if primary_keys:
            col_defs.append(f"PRIMARY KEY ({', '.join(primary_keys)})")
        schema_prefix = f"{schema}." if schema else ""
        ddl = f"CREATE TABLE {schema_prefix}{table_name} (\n  {', '.join(col_defs)}\n)"
        return r.ok(ddl)

    def disconnect(self) -> r[bool]:
        """Disconnect from Oracle database."""
        engine = self._engine
        if engine is not None:
            _engine_dispose(engine)
            self._engine = None
            self.logger.info("Disconnected from Oracle database")
        return r[bool].ok(True)

    def drop_table_ddl(
        self,
        table_name: str,
        schema: str | None = None,
    ) -> r[str]:
        """Generate DROP TABLE DDL."""
        schema_prefix = f"{schema}." if schema else ""
        ddl = f"DROP TABLE {schema_prefix}{table_name}"
        return r.ok(ddl)

    # Service
    @override
    def execute(self, **_kwargs: t.JsonValue) -> r[FlextDbOracleSettings]:
        """Execute main domain service operation - return config."""
        test_result = self.test_connection()
        if test_result.is_success:
            return r.ok(self._db_config)
        return r.fail(test_result.error or "Connection test failed")

    def execute_many(
        self,
        sql: str,
        params_list: Sequence[Mapping[str, t.ContainerValue] | m.ConfigMap],
    ) -> r[int]:
        """Execute SQL statement multiple times."""
        if not self.is_connected():
            return r.fail("Not connected to database")
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
                    typed_params = (
                        params
                        if isinstance(params, m.ConfigMap)
                        else m.ConfigMap.model_validate(params)
                    )
                    result = _connection_execute(
                        conn,
                        _sqlalchemy_text(sql),
                        typed_params,
                    )
                    rowcount_raw = getattr(result, "rowcount", 0)
                    total_affected += _parse_rowcount(rowcount_raw)
                return r.ok(total_affected)
            finally:
                _context_exit(connect_ctx)
        except (
            OracleDatabaseError,
            OracleInterfaceError,
            ConnectionError,
            SQLAlchemyDatabaseError,
            SQLAlchemyOperationalError,
            SQLAlchemyError,
            OSError,
        ) as e:
            return r.fail(f"Bulk execution failed: {e}")

    # Query Operations
    def execute_query(
        self,
        sql: str,
        params: m.ConfigMap | None = None,
    ) -> r[list[m.Dict]]:
        """Execute SQL query and return results."""
        if not self.is_connected():
            return r.fail("Not connected to database")
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
                rows: list[m.Dict] = self._normalize_query_rows(result)
                return r.ok(rows)
            finally:
                _context_exit(connect_ctx)
        except (
            OracleDatabaseError,
            OracleInterfaceError,
            ConnectionError,
            SQLAlchemyDatabaseError,
            SQLAlchemyOperationalError,
            SQLAlchemyError,
            OSError,
        ) as e:
            return r.fail(f"Query execution failed: {e}")

    def execute_statement(
        self,
        sql: str,
        params: m.ConfigMap | None = None,
    ) -> r[int]:
        """Execute SQL statement and return affected rows."""
        if not self.is_connected():
            return r.fail("Not connected to database")
        engine_result = self._get_engine()
        if engine_result.is_failure:
            return r.fail(
                engine_result.error or "Failed to get database engine",
            )
        try:
            transaction_ctx = _engine_begin(engine_result.value)
            conn = _context_enter(transaction_ctx)
            try:
                result = _connection_execute(conn, _sqlalchemy_text(sql), params)
                rowcount_raw = getattr(result, "rowcount", 0)
                rowcount = _parse_rowcount(rowcount_raw)
                return r.ok(rowcount)
            finally:
                _context_exit(transaction_ctx)
        except (
            OracleDatabaseError,
            OracleInterfaceError,
            ConnectionError,
            SQLAlchemyDatabaseError,
            SQLAlchemyOperationalError,
            SQLAlchemyError,
            OSError,
        ) as e:
            return r.fail(f"Statement execution failed: {e}")

    def fetch_one(
        self,
        sql: str,
        params: m.ConfigMap | None = None,
    ) -> r[m.Dict | None]:
        """Execute query and return first result."""
        return self.execute_query(sql, params).map(
            lambda rows: rows[0] if rows else None,
        )

    def generate_query_hash(
        self,
        sql: str = "",
        params: m.ConfigMap | t.ConfigurationMapping | None = None,
    ) -> r[str]:
        """Generate query hash - simplified."""
        typed_params = (
            params
            if isinstance(params, m.ConfigMap) or params is None
            else m.ConfigMap.model_validate(params)
        )
        hash_input = f"{sql}_{typed_params!s}"
        return r.ok(hashlib.sha256(hash_input.encode()).hexdigest()[:16])

    def get_columns(
        self,
        table_name: str,
        schema_name: str | None = None,
    ) -> r[list[FlextDbOracleModels.DbOracle.Column]]:
        """Get column information for Oracle table."""
        if schema_name:
            sql = """
SELECT column_name, data_type, data_length, data_precision, data_scale, nullable
FROM all_tab_columns
WHERE table_name = UPPER(:table_name) AND owner = UPPER(:schema_name)
ORDER BY column_id
"""
            params = m.ConfigMap(
                root={
                    "table_name": table_name,
                    "schema_name": schema_name,
                },
            )
        else:
            sql = """
SELECT column_name, data_type, data_length, data_precision, data_scale, nullable
FROM user_tab_columns
WHERE table_name = UPPER(:table_name)
ORDER BY column_id
"""
            params = m.ConfigMap(root={"table_name": table_name})
        return self.execute_query(sql, params).map(
            lambda rows: [
                FlextDbOracleModels.DbOracle.Column(
                    name=str(row.root.get("column_name", "")),
                    data_type=str(row.root.get("data_type", "")),
                    nullable=str(row.root.get("nullable", "Y")) == "Y",
                    default_value=str(row.root.get("data_default", "")),
                )
                for row in rows
            ],
        )

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

    def get_connection_status(
        self,
    ) -> r[FlextDbOracleModels.DbOracle.ConnectionStatus]:
        """Get connection status - simplified."""
        return r.ok(
            FlextDbOracleModels.DbOracle.ConnectionStatus(
                is_connected=self.is_connected(),
                host=self._db_config.host,
                port=self._db_config.port,
                service_name=self._db_config.service_name,
                username=self._db_config.username,
                error_message="" if self.is_connected() else "Connection unavailable",
            ),
        )

    def get_metrics(self) -> r[FlextDbOracleModels.DbOracle.HealthStatus]:
        """Get metrics status with explicit observability integration check."""
        try:
            observability_module = import_module("flext_observability")
        except ModuleNotFoundError:
            return r.fail(
                "flext-observability integration unavailable; install flext-observability",
            )

        metric_factory = getattr(observability_module, "flext_metric", None)
        if not callable(metric_factory):
            return r.fail("flext-observability does not expose flext_metric")

        status = "connected" if self.is_connected() else "disconnected"
        return r.ok(
            FlextDbOracleModels.DbOracle.HealthStatus(
                status=f"{status}_with_observability",
                timestamp=self._get_current_timestamp(),
                service="oracle",
                database=self._db_config.service_name,
                metrics=dict(self._metrics),
            ),
        )

    def get_operations(self) -> r[list[FlextDbOracleModels.DbOracle.OperationRecord]]:
        """Get tracked operations."""
        return r.ok(self._operations.copy())

    def get_plugin(self, _name: str) -> r[t.JsonValue]:
        """Get plugin data from local service registry."""
        if not _name:
            return r.fail("Plugin name is required")
        try:
            _ = import_module("flext_plugin.api")
        except ModuleNotFoundError:
            return r.fail("flext-plugin integration unavailable; install flext-plugin")
        if _name not in self._plugins:
            return r.fail(f"Plugin '{_name}' not found")
        return r[t.JsonValue].ok(self._plugins[_name])

    def get_primary_key_columns(
        self,
        table_name: str,
        schema_name: str | None = None,
    ) -> r[list[str]]:
        """Alias for get_primary_keys."""
        return self.get_primary_keys(table_name, schema_name)

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
                params = m.ConfigMap(
                    root={
                        "table_name": table_name,
                        "schema": schema,
                    },
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
                params = m.ConfigMap(root={"table_name": table_name})

            return self.execute_query(sql, params).map(
                lambda rows: [str(row.root["column_name"]) for row in rows],
            )
        except (
            OracleDatabaseError,
            OracleInterfaceError,
            ConnectionError,
            SQLAlchemyDatabaseError,
            SQLAlchemyOperationalError,
            SQLAlchemyError,
            OSError,
        ) as e:
            return r.fail(f"Failed to get primary keys: {e}")

    # Schema Operations
    def get_schemas(self) -> r[list[str]]:
        """Get list of Oracle schemas."""
        sql = "SELECT username as schema_name FROM all_users WHERE username NOT IN ('SYS', 'SYSTEM', 'ANONYMOUS', 'XDB', 'CTXSYS', 'MDSYS', 'WMSYS') ORDER BY username"
        return self.execute_query(sql).map(
            lambda rows: [str(row.root["schema_name"]) for row in rows],
        )

    def get_table_metadata(
        self,
        table_name: str,
        schema: str | None = None,
    ) -> r[FlextDbOracleModels.DbOracle.TableMetadata]:
        """Get complete table metadata."""
        try:
            return self.get_columns(table_name, schema).flat_map(
                lambda columns: self.get_primary_keys(table_name, schema).map(
                    lambda pk: FlextDbOracleModels.DbOracle.TableMetadata(
                        table_name=table_name,
                        schema_name=schema or "",
                        columns=[
                            FlextDbOracleModels.DbOracle.ColumnMetadata(
                                name=column.name,
                                data_type=column.data_type,
                                nullable=column.nullable,
                            )
                            for column in columns
                        ],
                        primary_keys=pk,
                    ),
                ),
            )
        except (
            OracleDatabaseError,
            OracleInterfaceError,
            ConnectionError,
            SQLAlchemyOperationalError,
            OSError,
        ) as e:
            return r.fail(f"Failed to get table metadata: {e}")

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
        except (
            OracleDatabaseError,
            OracleInterfaceError,
            ConnectionError,
            SQLAlchemyOperationalError,
            OSError,
        ) as e:
            return r.fail(f"Failed to get row count: {e}")

    def get_tables(self, schema: str | None = None) -> r[list[str]]:
        """Get list of tables in Oracle schema."""
        if schema:
            sql = "SELECT table_name FROM all_tables WHERE owner = UPPER(:schema_name) ORDER BY table_name"
            params: m.ConfigMap | None = m.ConfigMap(root={"schema_name": schema})
        else:
            sql = "SELECT table_name FROM user_tables ORDER BY table_name"
            params = None
        return self.execute_query(sql, params).map(
            lambda rows: [str(row.root["table_name"]) for row in rows],
        )

    def health_check(self) -> r[FlextDbOracleModels.DbOracle.HealthStatus]:
        """Perform health check."""
        return r.ok(
            FlextDbOracleModels.DbOracle.HealthStatus(
                status="healthy" if self.is_connected() else "unhealthy",
                timestamp=self._get_current_timestamp(),
                service="oracle",
                database=self._db_config.service_name,
                metrics={
                    "connected": self.is_connected(),
                    "host": self._db_config.host,
                    "port": self._db_config.port,
                },
            ),
        )

    def is_connected(self) -> bool:
        """Check if connected to Oracle database."""
        return self._engine is not None

    def list_plugins(self) -> r[m.ConfigMap]:
        """List plugin names from local service registry."""
        try:
            _ = import_module("flext_plugin.api")
        except ModuleNotFoundError:
            return r.fail("flext-plugin integration unavailable; install flext-plugin")
        plugin_names = list(self._plugins.keys())
        return r[m.ConfigMap].ok(m.ConfigMap(root=dict.fromkeys(plugin_names, True)))

    def map_singer_schema(
        self,
        singer_schema: FlextDbOracleModels.DbOracle.SingerSchema
        | t.ConfigurationMapping
        | Mapping[str, t.ContainerValue],
    ) -> r[FlextDbOracleModels.DbOracle.TypeMapping]:
        """Map Singer schema to Oracle types - simplified."""
        if isinstance(singer_schema, FlextDbOracleModels.DbOracle.SingerSchema):
            schema_model = singer_schema
        else:
            raw_properties = singer_schema.get("properties", {})
            if not isinstance(raw_properties, Mapping):
                return r.fail("Singer schema properties must be a mapping")
            normalized_properties: dict[
                str, FlextDbOracleModels.DbOracle.SingerField
            ] = {}
            for field_name, field_def in raw_properties.items():
                if isinstance(field_def, Mapping):
                    normalized_properties[str(field_name)] = (
                        FlextDbOracleModels.DbOracle.SingerField(
                            type=field_def.get("type", "string"),
                        )
                    )
                else:
                    normalized_properties[str(field_name)] = (
                        FlextDbOracleModels.DbOracle.SingerField(type="string")
                    )
            schema_model = FlextDbOracleModels.DbOracle.SingerSchema(
                properties=normalized_properties,
            )
        mapping = m.ConfigMap(root={})
        for field_name, field_def in schema_model.properties.items():
            raw_field = (
                raw_properties.get(field_name) if "raw_properties" in locals() else None
            )
            format_hint = (
                raw_field.get("format") if isinstance(raw_field, Mapping) else None
            )
            conversion = self.convert_singer_type(field_def.type, format_hint)
            if conversion.is_success:
                mapping.root[field_name] = conversion.value
        normalized_mapping = {key: str(value) for key, value in mapping.root.items()}
        type_mapping = FlextDbOracleModels.DbOracle.TypeMapping.model_validate({
            "mapping": normalized_mapping,
        })
        return r.ok(type_mapping)

    def record_metric(
        self,
        _name: str,
        _value: float,
        _tags: m.ConfigMap | t.ConfigurationMapping | None = None,
    ) -> r[bool]:
        """Record metric through flext-observability when available."""
        if not _name:
            return r.fail("Metric name is required")

        try:
            observability_module = import_module("flext_observability")
        except ModuleNotFoundError:
            return r.fail(
                "flext-observability integration unavailable; install flext-observability",
            )

        metric_factory = getattr(observability_module, "flext_metric", None)
        if not callable(metric_factory):
            return r.fail("flext-observability does not expose flext_metric")

        typed_tags = (
            _tags
            if isinstance(_tags, m.ConfigMap) or _tags is None
            else m.ConfigMap.model_validate(_tags)
        )
        tags_payload = (
            typed_tags.root if typed_tags is not None else dict[str, t.JsonValue]()
        )
        metric_result = metric_factory(
            name=_name,
            value=_value,
            tags=m.Dict.model_validate(tags_payload),
        )
        if getattr(metric_result, "is_failure", False):
            return r.fail(
                getattr(
                    metric_result,
                    "error",
                    "Metric recording failed in observability",
                ),
            )
        self._metrics[_name] = {
            "value": _value,
            "tags": tags_payload,
            "timestamp": self._get_current_timestamp(),
        }
        return r[bool].ok(True)

    def register_plugin(self, _name: str, _plugin: t.JsonValue) -> r[bool]:
        """Register plugin via flext-plugin when available."""
        if not _name:
            return r.fail("Plugin name is required")

        plugin_payload = _validate_config_map(_plugin)
        if plugin_payload is None:
            return r.fail("Plugin payload must be a mapping")

        try:
            _ = import_module("flext_plugin.api")
            _ = import_module("flext_plugin.models")
        except ModuleNotFoundError:
            return r.fail("flext-plugin integration unavailable; install flext-plugin")

        payload = dict(plugin_payload.root)
        payload["name"] = str(payload.get("name", _name))
        self._plugins[_name] = payload
        return r[bool].ok(True)

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
        except (
            OracleDatabaseError,
            OracleInterfaceError,
            ConnectionError,
            SQLAlchemyDatabaseError,
            SQLAlchemyOperationalError,
            SQLAlchemyError,
            OSError,
        ) as e:
            return r.fail(f"Connection test failed: {e}")

    def track_operation(
        self,
        operation_type: str = "",
        duration: float = 0.0,
        *,
        success: bool = True,
        metadata: m.ConfigMap | t.ConfigurationMapping | None = None,
    ) -> r[bool]:
        """Track database operation for monitoring."""
        try:
            metadata_value = (
                metadata
                if isinstance(metadata, m.ConfigMap)
                else m.ConfigMap.model_validate(metadata or {})
            )
            operation = FlextDbOracleModels.DbOracle.OperationRecord(
                operation_type=operation_type,
                duration=duration,
                success=success,
                metadata_info=str(metadata_value),
                timestamp=self._get_current_timestamp(),
            )
            self._operations.append(operation)
            return r[bool].ok(True)
        except (
            OracleDatabaseError,
            OracleInterfaceError,
            ConnectionError,
            SQLAlchemyOperationalError,
            OSError,
        ) as e:
            return r.fail(f"Failed to track operation: {e}")

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

    def unregister_plugin(self, _name: str) -> r[bool]:
        """Unregister plugin from local service registry."""
        if not _name:
            return r.fail("Plugin name is required")
        try:
            _ = import_module("flext_plugin.api")
        except ModuleNotFoundError:
            return r.fail("flext-plugin integration unavailable; install flext-plugin")
        if _name not in self._plugins:
            return r.fail(f"Plugin '{_name}' not found")
        self._plugins.pop(_name)
        return r[bool].ok(True)

    def _build_connection_url(self) -> r[str]:
        """Build Oracle connection URL from configuration."""
        try:
            password = self._db_config.password
            if not password:
                return r.fail("Password is required for database connection")
            encoded_password = quote_plus(str(password).encode())
            service_name = self._db_config.service_name
            base = f"oracle+oracledb://{self._db_config.username}:{encoded_password}@{self._db_config.host}:{self._db_config.port}"
            url = f"{base}/?service_name={service_name}"
            return r.ok(url)
        except (
            OracleDatabaseError,
            OracleInterfaceError,
            ConnectionError,
            SQLAlchemyDatabaseError,
            SQLAlchemyOperationalError,
            SQLAlchemyError,
            OSError,
        ) as e:
            return r.fail(f"Failed to build connection URL: {e}")

    def _extract_mapping_rows(self, mapping_result: object) -> list[t.ContainerValue]:
        """Extract all SQLAlchemy mapping rows from a mapping result."""
        all_method = getattr(mapping_result, "all", None)
        if not callable(all_method):
            return []
        rows = all_method()
        return _extract_object_rows(rows)

    def _get_current_timestamp(self) -> str:
        """Get current timestamp for operation tracking."""
        return str(int(time.time()))

    def _get_engine(self) -> r[object]:
        """Get database engine."""
        if not self._engine or not self.is_connected():
            return r.fail("Not connected to database")
        return r.ok(self._engine)

    def _normalize_query_rows(self, query_result: object) -> list[m.Dict]:
        """Normalize SQLAlchemy query result rows into typed mapping models."""
        mappings_method = getattr(query_result, "mappings", None)
        if not callable(mappings_method):
            return []
        mapping_result = mappings_method()
        return [
            self._normalize_row(row)
            for row in self._extract_mapping_rows(mapping_result)
        ]

    def _normalize_row(self, row: object) -> m.Dict:
        """Normalize a single SQLAlchemy mapping row into a typed map."""
        mapping = row if isinstance(row, Mapping) else getattr(row, "_mapping", None)
        validated_mapping = _validate_config_map(mapping)
        if validated_mapping is None:
            return m.Dict(root={})
        return m.Dict(
            root={str(key): value for key, value in validated_mapping.root.items()},
        )

    def _parse_count_from_rows(self, rows: list[m.Dict]) -> int:
        """Parse COUNT(*) value from normalized query rows."""
        if not rows:
            return 0
        count_value = rows[0].root.get("count")
        if count_value is None:
            return 0
        return _parse_count_value(count_value)


# Export the single refactored class following flext-core pattern
__all__ = ["FlextDbOracleServices"]
