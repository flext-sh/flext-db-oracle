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
from typing import Protocol
from urllib.parse import quote_plus

from flext_core import r, t
from flext_core.service import FlextService
from flext_db_oracle.settings import FlextDbOracleSettings


class _DbContextManager(Protocol):
    """Protocol for context-managed DB connection/transaction objects."""

    def __enter__(self) -> object: ...

    def __exit__(self, exc_type: object, exc: object, tb: object) -> bool | None: ...


def _sqlalchemy_create_engine(url: str) -> object:
    """Create SQLAlchemy engine via runtime import to keep type boundaries explicit."""
    sqlalchemy_module = import_module("sqlalchemy")
    create_engine_func = getattr(sqlalchemy_module, "create_engine", None)
    if not callable(create_engine_func):
        msg = "sqlalchemy.create_engine unavailable"
        raise RuntimeError(msg)
    engine_obj = create_engine_func(
        url,
        pool_pre_ping=True,
        pool_recycle=3600,
        echo=False,
    )
    return engine_obj


def _sqlalchemy_text(statement: str) -> object:
    """Build SQL text object via runtime import."""
    sqlalchemy_module = import_module("sqlalchemy")
    text_func = getattr(sqlalchemy_module, "text", None)
    if not callable(text_func):
        msg = "sqlalchemy.text unavailable"
        raise RuntimeError(msg)
    return text_func(statement)


def _engine_connect(engine: object) -> object:
    """Open connection context manager from engine."""
    connect_method = getattr(engine, "connect", None)
    if not callable(connect_method):
        msg = "Database engine does not expose connect()"
        raise RuntimeError(msg)
    return connect_method()


def _engine_begin(engine: object) -> object:
    """Open transaction context manager from engine."""
    begin_method = getattr(engine, "begin", None)
    if not callable(begin_method):
        msg = "Database engine does not expose begin()"
        raise RuntimeError(msg)
    return begin_method()


def _context_enter(context_manager: object) -> object:
    """Enter dynamic context manager and return inner object."""
    enter_method = getattr(context_manager, "__enter__", None)
    if not callable(enter_method):
        msg = "Context manager does not expose __enter__()"
        raise RuntimeError(msg)
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
    parameters: dict[str, t.JsonValue] | None = None,
) -> object:
    """Execute statement on dynamic SQL connection."""
    execute_method = getattr(connection, "execute", None)
    if not callable(execute_method):
        msg = "Database connection does not expose execute()"
        raise RuntimeError(msg)
    return execute_method(statement, parameters or {})


class FlextDbOracleServices(FlextService[FlextDbOracleSettings]):
    """Generic Oracle database services using flext-core patterns."""

    def __init__(self, config: FlextDbOracleSettings) -> None:
        """Initialize with configuration."""
        super().__init__()
        self._db_config = config  # Use separate attribute for Oracle-specific config
        self._engine: object | None = None
        self._operations: list[dict[str, t.JsonValue]] = []

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
    def connect(self) -> r[FlextDbOracleServices]:
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
        params: dict[str, t.JsonValue] | None = None,
    ) -> r[list[dict[str, t.JsonValue]]]:
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
                result = _connection_execute(conn, _sqlalchemy_text(sql), params or {})
                rows: list[dict[str, t.JsonValue]] = []
                if isinstance(result, list):
                    for row in result:
                        if isinstance(row, dict):
                            rows.append(row)
                return r.ok(rows)
            finally:
                _context_exit(connect_ctx)
        except Exception as e:
            return r.fail(f"Query execution failed: {e}")

    def execute_statement(
        self,
        sql: str,
        params: dict[str, t.JsonValue] | None = None,
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
                result = _connection_execute(conn, _sqlalchemy_text(sql), params or {})
                rowcount_raw = getattr(result, "rowcount", 0)
                rowcount = rowcount_raw if isinstance(rowcount_raw, int) else 0
                return r.ok(rowcount)
            finally:
                _context_exit(connect_ctx)
        except Exception as e:
            return r.fail(f"Statement execution failed: {e}")

    def execute_many(
        self,
        sql: str,
        params_list: list[dict[str, t.JsonValue]],
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
                    if isinstance(rowcount_raw, int):
                        total_affected += rowcount_raw
                return r.ok(total_affected)
            finally:
                _context_exit(connect_ctx)
        except Exception as e:
            return r.fail(f"Bulk execution failed: {e}")

    def fetch_one(
        self,
        sql: str,
        params: dict[str, t.JsonValue] | None = None,
    ) -> r[dict[str, t.JsonValue] | None]:
        """Execute query and return first result."""
        return self.execute_query(sql, params).map(
            lambda rows: rows[0] if rows else None,
        )

    # Schema Operations
    def get_schemas(self) -> r[list[str]]:
        """Get list of Oracle schemas."""
        sql = "SELECT username as schema_name FROM all_users WHERE username NOT IN ('SYS', 'SYSTEM', 'ANONYMOUS', 'XDB', 'CTXSYS', 'MDSYS', 'WMSYS') ORDER BY username"
        return self.execute_query(sql).map(
            lambda rows: [str(row["schema_name"]) for row in rows],
        )

    def get_tables(self, schema: str | None = None) -> r[list[str]]:
        """Get list of tables in Oracle schema."""
        if schema:
            sql = "SELECT table_name FROM all_tables WHERE owner = UPPER(:schema_name) ORDER BY table_name"
            params: dict[str, t.JsonValue] | None = {"schema_name": schema}
        else:
            sql = "SELECT table_name FROM user_tables ORDER BY table_name"
            params = None
        return self.execute_query(sql, params).map(
            lambda rows: [str(row["table_name"]) for row in rows],
        )

    def get_columns(
        self,
        table_name: str,
        schema_name: str | None = None,
    ) -> r[list[dict[str, t.JsonValue]]]:
        """Get column information for Oracle table."""
        if schema_name:
            sql = """
SELECT column_name, data_type, data_length, data_precision, data_scale, nullable
FROM all_tab_columns
WHERE table_name = UPPER(:table_name) AND owner = UPPER(:schema_name)
ORDER BY column_id
"""
            params: dict[str, t.JsonValue] = {
                "table_name": table_name,
                "schema_name": schema_name,
            }
        else:
            sql = """
SELECT column_name, data_type, data_length, data_precision, data_scale, nullable
FROM user_tab_columns
WHERE table_name = UPPER(:table_name)
ORDER BY column_id
"""
            params = {"table_name": table_name}
        return self.execute_query(sql, params)

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
                params: dict[str, t.JsonValue] = {
                    "table_name": table_name,
                    "schema": schema,
                }
            else:
                sql = """
                SELECT column_name
                FROM user_constraints c, user_cons_columns cc
                WHERE c.constraint_type = 'P'
                AND c.constraint_name = cc.constraint_name
                AND c.table_name = UPPER(:table_name)
                ORDER BY cc.position
                """
                params = {"table_name": table_name}

            return self.execute_query(sql, params).map(
                lambda rows: [str(row["column_name"]) for row in rows],
            )
        except Exception as e:
            return r.fail(f"Failed to get primary keys: {e}")

    def get_table_metadata(
        self,
        table_name: str,
        schema: str | None = None,
    ) -> r[dict[str, t.JsonValue]]:
        """Get complete table metadata."""
        try:
            return self.get_columns(table_name, schema).flat_map(
                lambda columns: self.get_primary_keys(table_name, schema).map(
                    lambda pk: {
                        "table_name": table_name,
                        "schema": schema,
                        "columns": columns,
                        "primary_keys": pk,
                    },
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
        conditions: dict[str, t.JsonValue] | None = None,
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
        columns: list[dict[str, t.JsonValue]],
        schema: str | None = None,
    ) -> r[str]:
        """Generate CREATE TABLE DDL - simplified."""
        col_defs: list[str] = []
        for col in columns:
            name = col.get("name", "unknown")
            data_type = col.get("data_type", "VARCHAR2(255)")
            nullable = "" if col.get("nullable", True) else " NOT NULL"
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
        if isinstance(singer_type, list):
            singer_type = singer_type[0] if singer_type else "string"
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
        singer_schema: dict[str, t.JsonValue],
    ) -> r[dict[str, str]]:
        """Map Singer schema to Oracle types - simplified."""
        mapping = {}
        properties = singer_schema.get("properties", {})
        if isinstance(properties, dict):
            for field_name, field_def in properties.items():
                if isinstance(field_def, dict):
                    field_type = field_def.get("type", "string")
                    conversion = self.convert_singer_type(field_type)
                    if conversion.is_success:
                        mapping[field_name] = conversion.value
        return r.ok(mapping)

    # Placeholder methods for compatibility
    def generate_query_hash(
        self,
        sql: str = "",
        params: dict[str, t.JsonValue] | None = None,
    ) -> r[str]:
        """Generate query hash - simplified."""
        hash_input = f"{sql}_{params!s}"
        return r.ok(hashlib.sha256(hash_input.encode()).hexdigest()[:16])

    def get_connection_status(
        self,
    ) -> r[dict[str, t.JsonValue]]:
        """Get connection status - simplified."""
        return r.ok({
            "connected": self.is_connected(),
            "host": self._db_config.host,
            "port": self._db_config.port,
            "service_name": self._db_config.service_name,
        })

    def record_metric(
        _name: str,
        _value: float,
        _tags: dict[str, str] | None = None,
    ) -> r[None]:
        """Record metric - placeholder."""
        return r[None].ok(None)

    def get_metrics(self) -> r[dict[str, t.JsonValue]]:
        """Get metrics - placeholder."""
        return r.ok({})

    def health_check(self) -> r[dict[str, t.JsonValue]]:
        """Perform health check."""
        return r.ok({
            "status": "healthy" if self.is_connected() else "unhealthy",
            "timestamp": "2025-01-01T00:00:00Z",
        })

    def register_plugin(self, _name: str, _plugin: t.JsonValue) -> r[None]:
        """Register plugin - placeholder."""
        return r[None].ok(None)

    def unregister_plugin(self, _name: str) -> r[None]:
        """Unregister plugin - placeholder."""
        return r[None].ok(None)

    def list_plugins(self) -> r[dict[str, t.JsonValue]]:
        """List plugins - placeholder."""
        return r[dict[str, t.JsonValue]].ok({})

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
                lambda rows: (
                    int(rows[0]["count"])
                    if rows
                    and "count" in rows[0]
                    and isinstance(rows[0]["count"], (int, str))
                    else 0
                ),
            )
        except Exception as e:
            return r.fail(f"Failed to get row count: {e}")

    def track_operation(
        self,
        operation_type: str = "",
        duration: float = 0.0,
        *,
        success: bool = True,
        metadata: dict[str, t.JsonValue] | None = None,
    ) -> r[None]:
        """Track database operation for monitoring."""
        try:
            metadata_value: dict[str, t.JsonValue] = metadata if metadata else {}
            operation: dict[str, t.JsonValue] = {
                "operation_type": operation_type,
                "duration": duration,
                "success": success,
                "metadata": metadata_value,
                "timestamp": self._get_current_timestamp(),
            }
            self._operations.append(operation)
            return r[None].ok(None)
        except Exception as e:
            return r.fail(f"Failed to track operation: {e}")

    def get_operations(self) -> r[list[dict[str, t.JsonValue]]]:
        """Get tracked operations."""
        return r.ok(self._operations.copy())

    def _get_current_timestamp(self) -> str:
        """Get current timestamp for operation tracking."""
        return str(int(time.time()))


# Export the single refactored class following flext-core pattern
__all__ = ["FlextDbOracleServices"]
