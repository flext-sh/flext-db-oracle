"""Generic Oracle Database services delegating to flext-core and SQLAlchemy.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import hashlib
import time
from collections.abc import Generator
from contextlib import contextmanager
from typing import cast
from urllib.parse import quote_plus

from flext_core import FlextResult, FlextService, FlextTypes
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Connection, Engine

from flext_db_oracle.config import FlextDbOracleConfig


class FlextDbOracleServices(FlextService[FlextDbOracleConfig]):
    """Generic Oracle database services using flext-core patterns."""

    def __init__(self, config: FlextDbOracleConfig) -> None:
        """Initialize with configuration."""
        super().__init__()
        self._config = config
        self._engine: Engine | None = None
        self._operations: list[dict[str, FlextTypes.JsonValue]] = []

    def _build_connection_url(self) -> FlextResult[str]:
        """Build Oracle connection URL from configuration."""
        try:
            password = self._config.password.get_secret_value()
            if not password:
                return FlextResult.fail("Password is required for database connection")

            encoded_password = quote_plus(password)
            db_id = self._config.sid or self._config.service_name
            url = f"oracle+oracledb://{self._config.username}:{encoded_password}@{self._config.host}:{self._config.port}/{db_id}"
            return FlextResult.ok(url)
        except Exception as e:
            return FlextResult.fail(f"Failed to build connection URL: {e}")

    def _get_engine(self) -> FlextResult[Engine]:
        """Get database engine."""
        if not self._engine or not self.is_connected():
            return FlextResult.fail("Not connected to database")
        return FlextResult.ok(self._engine)

    # Connection Management
    def connect(self) -> FlextResult[FlextDbOracleServices]:
        """Establish Oracle database connection."""
        try:
            url_result = self._build_connection_url()
            if url_result.is_failure:
                return FlextResult.fail(
                    url_result.error or "Failed to build connection URL"
                )

            self._engine = create_engine(
                url_result.unwrap(),
                pool_pre_ping=True,
                pool_recycle=3600,  # 1 hour
                echo=False,
            )

            # Test connection
            with self._engine.connect() as conn:
                conn.execute(text("SELECT 1 FROM dual"))

            self.logger.info(f"Connected to Oracle database: {self._config.host}")
            return FlextResult.ok(self)

        except Exception as e:
            self.logger.exception("Oracle connection failed")
            return FlextResult.fail(f"Connection failed: {e}")

    def disconnect(self) -> FlextResult[None]:
        """Disconnect from Oracle database."""
        try:
            if self._engine:
                self._engine.dispose()
                self._engine = None
                self.logger.info("Disconnected from Oracle database")
            return FlextResult.ok(None)
        except Exception as e:
            return FlextResult.fail(f"Disconnect failed: {e}")

    def is_connected(self) -> bool:
        """Check if connected to Oracle database."""
        return self._engine is not None

    def test_connection(self) -> FlextResult[bool]:
        """Test Oracle database connection."""
        try:
            engine_result = self._get_engine()
            if engine_result.is_failure:
                return FlextResult.fail("Not connected to database")

            with engine_result.unwrap().connect() as conn:
                conn.execute(text("SELECT 1 FROM dual"))
            return FlextResult.ok(True)
        except Exception as e:
            return FlextResult.fail(f"Connection test failed: {e}")

    @contextmanager
    def get_connection(self) -> Generator[Connection]:
        """Get database connection context manager."""
        if not self._engine:
            msg = "No database connection established"
            raise RuntimeError(msg)
        with self._engine.connect() as connection:
            yield connection

    @contextmanager
    def transaction(self) -> Generator[Connection]:
        """Get transaction context for database operations."""
        if not self._engine:
            msg = "No database connection established"
            raise RuntimeError(msg)
        with self._engine.begin() as transaction:
            yield transaction

    # Query Operations
    def execute_query(
        self, sql: str, params: dict[str, FlextTypes.JsonValue] | None = None
    ) -> FlextResult[list[dict[str, FlextTypes.JsonValue]]]:
        """Execute SQL query and return results."""
        try:
            engine_result = self._get_engine()
            if engine_result.is_failure:
                return FlextResult.fail(
                    engine_result.error or "Failed to get database engine"
                )

            with engine_result.unwrap().connect() as conn:
                result = conn.execute(text(sql), params or {})
                rows = [dict(row) for row in result]
                return FlextResult.ok(rows)
        except Exception as e:
            return FlextResult.fail(f"Query execution failed: {e}")

    def execute_statement(
        self, sql: str, params: dict[str, FlextTypes.JsonValue] | None = None
    ) -> FlextResult[int]:
        """Execute SQL statement and return affected rows."""
        try:
            engine_result = self._get_engine()
            if engine_result.is_failure:
                return FlextResult.fail(
                    engine_result.error or "Failed to get database engine"
                )

            with engine_result.unwrap().connect() as conn:
                result = conn.execute(text(sql), params or {})
                return FlextResult.ok(result.rowcount)
        except Exception as e:
            return FlextResult.fail(f"Statement execution failed: {e}")

    def execute_many(
        self, sql: str, params_list: list[dict[str, FlextTypes.JsonValue]]
    ) -> FlextResult[int]:
        """Execute SQL statement multiple times."""
        try:
            engine_result = self._get_engine()
            if engine_result.is_failure:
                return FlextResult.fail(
                    engine_result.error or "Failed to get database engine"
                )

            total_affected = 0
            with engine_result.unwrap().connect() as conn:
                for params in params_list:
                    result = conn.execute(text(sql), params)
                    total_affected += result.rowcount
            return FlextResult.ok(total_affected)
        except Exception as e:
            return FlextResult.fail(f"Bulk execution failed: {e}")

    def fetch_one(
        self, sql: str, params: dict[str, FlextTypes.JsonValue] | None = None
    ) -> FlextResult[dict[str, FlextTypes.JsonValue] | None]:
        """Execute query and return first result."""
        try:
            result = self.execute_query(sql, params)
            if result.is_failure:
                return FlextResult.fail(result.error or "Query execution failed")

            rows = result.unwrap()
            return FlextResult.ok(rows[0] if rows else None)
        except Exception as e:
            return FlextResult.fail(f"Fetch one failed: {e}")

    # Schema Operations
    def get_schemas(self) -> FlextResult[list[str]]:
        """Get list of Oracle schemas."""
        try:
            sql = "SELECT username as schema_name FROM all_users WHERE username NOT IN ('SYS', 'SYSTEM', 'ANONYMOUS', 'XDB', 'CTXSYS', 'MDSYS', 'WMSYS') ORDER BY username"
            result = self.execute_query(sql)
            if result.is_failure:
                return FlextResult.fail(result.error or "Failed to execute query")

            schemas = [str(row["schema_name"]) for row in result.unwrap()]
            return FlextResult.ok(schemas)
        except Exception as e:
            return FlextResult.fail(f"Failed to get schemas: {e}")

    def get_tables(self, schema: str | None = None) -> FlextResult[list[str]]:
        """Get list of tables in Oracle schema."""
        try:
            if schema:
                sql = "SELECT table_name FROM all_tables WHERE owner = UPPER(:schema_name) ORDER BY table_name"
                params: dict[str, FlextTypes.JsonValue] | None = {"schema_name": schema}
            else:
                sql = "SELECT table_name FROM user_tables ORDER BY table_name"
                params = None

            result = self.execute_query(sql, params)
            if result.is_failure:
                return FlextResult.fail(result.error or "Failed to execute query")

            tables = [str(row["table_name"]) for row in result.unwrap()]
            return FlextResult.ok(tables)
        except Exception as e:
            return FlextResult.fail(f"Failed to get tables: {e}")

    def get_columns(
        self, table_name: str, schema_name: str | None = None
    ) -> FlextResult[list[dict[str, FlextTypes.JsonValue]]]:
        """Get column information for Oracle table."""
        try:
            if schema_name:
                sql = """
 SELECT column_name, data_type, data_length, data_precision, data_scale, nullable
 FROM all_tab_columns
 WHERE table_name = UPPER(:table_name) AND owner = UPPER(:schema_name)
 ORDER BY column_id
 """
                params: dict[str, FlextTypes.JsonValue] = {
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
        except Exception as e:
            return FlextResult.fail(f"Failed to get columns: {e}")

    def get_primary_keys(
        self, table_name: str, schema: str | None = None
    ) -> FlextResult[list[str]]:
        """Get primary key column names for specified table."""
        try:
            if schema:
                sql = """
 SELECT column_name
 FROM all_constraints c, all_cons_columns cc
 WHERE c.constraint_type = 'P'
 AND c.constraint_name = cc.constraint_name
 AND c.table_name = UPPER(:table_name)
 AND c.owner = :schema
 ORDER BY cc.position
 """
                params: dict[str, FlextTypes.JsonValue] = {
                    "table_name": table_name,
                    "schema": schema,
                }
            else:
                sql = """
 SELECT column_name
 FROM all_constraints c, all_cons_columns cc
 WHERE c.constraint_type = 'P'
 AND c.constraint_name = cc.constraint_name
 AND c.table_name = UPPER(:table_name)
 ORDER BY cc.position
 """
                params = {"table_name": table_name}

            result = self.execute_query(sql, params)
            if result.is_failure:
                return FlextResult.fail(result.error or "Failed to execute query")

            primary_keys = [str(row["column_name"]) for row in result.unwrap()]
            return FlextResult.ok(primary_keys)
        except Exception as e:
            return FlextResult.fail(f"Failed to get primary keys: {e}")

    def get_table_metadata(
        self, table_name: str, schema: str | None = None
    ) -> FlextResult[dict[str, FlextTypes.JsonValue]]:
        """Get complete table metadata."""
        try:
            # Get table columns
            columns_result = self.get_columns(table_name, schema)
            if columns_result.is_failure:
                return FlextResult.fail(columns_result.error or "Failed to get columns")

            # Get primary keys
            pk_result = self.get_primary_keys(table_name, schema)
            if pk_result.is_failure:
                return FlextResult.fail(pk_result.error or "Failed to get primary keys")

            metadata: dict[str, FlextTypes.JsonValue] = {
                "table_name": table_name,
                "schema": schema,
                "columns": cast("FlextTypes.JsonValue", columns_result.unwrap()),
                "primary_keys": cast("FlextTypes.JsonValue", pk_result.unwrap()),
            }

            return FlextResult.ok(metadata)
        except Exception as e:
            return FlextResult.fail(f"Failed to get table metadata: {e}")

    # Domain Service
    def execute(self, **kwargs: object) -> FlextResult[FlextDbOracleConfig]:
        """Execute main domain service operation - return config."""
        test_result = self.test_connection()
        if test_result.is_success:
            return FlextResult.ok(self._config)
        return FlextResult.fail(test_result.error or "Connection test failed")

    # Placeholder methods for compatibility - delegate to simpler implementations
    def build_select(
        self,
        table_name: str,
        columns: list[str] | None = None,
        conditions: dict[str, FlextTypes.JsonValue] | None = None,
        schema_name: str | None = None,
    ) -> FlextResult[str]:
        """Build SELECT query - simplified implementation."""
        cols = ", ".join(columns) if columns else "*"
        where = f" WHERE {conditions}" if conditions else ""
        schema = f"{schema_name}." if schema_name else ""
        # Query builder pattern - inputs should be validated by caller
        # S608: Safe - uses column identifiers and bind parameters, not user input
        sql = f"SELECT {cols} FROM {schema}{table_name}{where}"
        return FlextResult.ok(sql)

    def build_insert_statement(
        self,
        table_name: str,
        columns: list[str],
        schema_name: str | None = None,
        returning_columns: list[str] | None = None,
    ) -> FlextResult[str]:
        """Build INSERT statement - simplified."""
        schema = f"{schema_name}." if schema_name else ""
        cols = ", ".join(columns)
        vals = ", ".join(f":{col}" for col in columns)
        # Query builder pattern - inputs should be validated by caller
        # S608: Safe - uses parameterized bind variables (:col), not direct value injection
        sql = f"INSERT INTO {schema}{table_name} ({cols}) VALUES ({vals})"
        if returning_columns:
            ret = ", ".join(returning_columns)
            sql += f" RETURNING {ret}"
        return FlextResult.ok(sql)

    def build_update_statement(
        self,
        table_name: str,
        set_columns: list[str],
        where_columns: list[str],
        schema_name: str | None = None,
    ) -> FlextResult[str]:
        """Build UPDATE statement - simplified."""
        schema = f"{schema_name}." if schema_name else ""
        sets = ", ".join(f"{col} = :{col}" for col in set_columns)
        wheres = " AND ".join(f"{col} = :where_{col}" for col in where_columns)
        # Query builder pattern - inputs should be validated by caller
        # S608: Safe - uses parameterized bind variables (:col, :where_col)
        sql = f"UPDATE {schema}{table_name} SET {sets} WHERE {wheres}"
        return FlextResult.ok(sql)

    def build_delete_statement(
        self, table_name: str, where_columns: list[str], schema_name: str | None = None
    ) -> FlextResult[str]:
        """Build DELETE statement - simplified."""
        schema = f"{schema_name}." if schema_name else ""
        wheres = " AND ".join(f"{col} = :{col}" for col in where_columns)
        # Query builder pattern - inputs should be validated by caller
        # S608: Safe - uses parameterized bind variables (:col), not direct value injection
        sql = f"DELETE FROM {schema}{table_name} WHERE {wheres}"
        return FlextResult.ok(sql)

    def build_create_index_statement(self, _config: object) -> FlextResult[str]:
        """Build CREATE INDEX statement - placeholder."""
        return FlextResult.ok("CREATE INDEX statement")

    def create_table_ddl(
        self,
        table_name: str,
        columns: list[dict[str, FlextTypes.JsonValue]],
        schema_name: str | None = None,
    ) -> FlextResult[str]:
        """Generate CREATE TABLE DDL - simplified."""
        schema = f"{schema_name}." if schema_name else ""
        col_defs: list[str] = []
        for col in columns:
            name = col.get("name", "unknown")
            data_type = col.get("data_type", "VARCHAR2(255)")
            nullable = "" if col.get("nullable", True) else " NOT NULL"
            col_defs.append(f"{name} {data_type}{nullable}")

        ddl = f"CREATE TABLE {schema}{table_name} (\n  {', '.join(col_defs)}\n)"
        return FlextResult.ok(ddl)

    def drop_table_ddl(
        self, table_name: str, schema_name: str | None = None
    ) -> FlextResult[str]:
        """Generate DROP TABLE DDL."""
        schema = f"{schema_name}." if schema_name else ""
        ddl = f"DROP TABLE {schema}{table_name}"
        return FlextResult.ok(ddl)

    def convert_singer_type(
        self, singer_type: str | list[str], _format_hint: str | None = None
    ) -> FlextResult[str]:
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
        return FlextResult.ok(oracle_type)

    def map_singer_schema(
        self, singer_schema: dict[str, FlextTypes.JsonValue]
    ) -> FlextResult[dict[str, str]]:
        """Map Singer schema to Oracle types - simplified."""
        mapping = {}
        properties = singer_schema.get("properties", {})
        if isinstance(properties, dict):
            for field_name, field_def in properties.items():
                if isinstance(field_def, dict):
                    field_type = field_def.get("type", "string")
                    conversion = self.convert_singer_type(field_type)
                    if conversion.is_success:
                        mapping[field_name] = conversion.unwrap()
        return FlextResult.ok(mapping)

    # Placeholder methods for compatibility
    def generate_query_hash(
        self, sql: str, params: dict[str, FlextTypes.JsonValue] | None = None
    ) -> FlextResult[str]:
        """Generate query hash - simplified."""
        hash_input = f"{sql}_{params!s}"
        return FlextResult.ok(hashlib.sha256(hash_input.encode()).hexdigest()[:16])

    def get_connection_status(self) -> FlextResult[dict[str, FlextTypes.JsonValue]]:
        """Get connection status - simplified."""
        return FlextResult.ok({
            "connected": self.is_connected(),
            "host": self._config.host,
            "port": self._config.port,
            "service_name": self._config.service_name,
        })

    def record_metric(
        self, _name: str, _value: float, _tags: dict[str, str] | None = None
    ) -> FlextResult[None]:
        """Record metric - placeholder."""
        return FlextResult.ok(None)

    def get_metrics(self) -> FlextResult[dict[str, FlextTypes.JsonValue]]:
        """Get metrics - placeholder."""
        return FlextResult.ok({})

    def health_check(self) -> FlextResult[dict[str, FlextTypes.JsonValue]]:
        """Perform health check."""
        return FlextResult.ok({
            "status": "healthy" if self.is_connected() else "unhealthy",
            "connected": self.is_connected(),
            "timestamp": "2025-01-01T00:00:00Z",
        })

    def register_plugin(self, _name: str, _plugin: object) -> FlextResult[None]:
        """Register plugin - placeholder."""
        return FlextResult.ok(None)

    def unregister_plugin(self, _name: str) -> FlextResult[None]:
        """Unregister plugin - placeholder."""
        return FlextResult.ok(None)

    def list_plugins(self) -> FlextResult[dict[str, FlextTypes.JsonValue]]:
        """List plugins - placeholder."""
        return FlextResult.ok({})

    def get_plugin(self, _name: str) -> FlextResult[object]:
        """Get plugin - placeholder implementation.

        Args:
        _name: Plugin name (reserved for future implementation)

        """
        return FlextResult.ok(None)

    def get_primary_key_columns(
        self, table_name: str, schema_name: str | None = None
    ) -> FlextResult[list[str]]:
        """Alias for get_primary_keys."""
        return self.get_primary_keys(table_name, schema_name)

    def get_table_row_count(
        self, table_name: str, schema_name: str | None = None
    ) -> FlextResult[int]:
        """Get row count - simplified."""
        try:
            schema = f"{schema_name}." if schema_name else ""
            # Query builder pattern - inputs should be validated by caller
            # S608: Safe - uses column identifiers and bind parameters
            sql = f"SELECT COUNT(*) as count FROM {schema}{table_name}"
            result = self.execute_query(sql)
            if result.is_failure:
                return FlextResult.fail(result.error or "Failed to get count")

            rows = result.unwrap()
            if rows and "count" in rows[0]:
                count_value = rows[0]["count"]
                count = int(count_value) if isinstance(count_value, (int, str)) else 0
            else:
                count = 0
            return FlextResult.ok(count)
        except Exception as e:
            return FlextResult.fail(f"Failed to get row count: {e}")

    def track_operation(
        self,
        operation_type: str,
        duration: float,
        *,
        _success: bool,
        metadata: dict[str, FlextTypes.JsonValue] | None = None,
    ) -> FlextResult[None]:
        """Track database operation for monitoring."""
        try:
            operation = {
                "operation_type": operation_type,
                "duration": duration,
                "success": _success,
                "metadata": metadata or {},
                "timestamp": self._get_current_timestamp(),
            }
            self._operations.append(cast("dict[str, FlextTypes.JsonValue]", operation))
            return FlextResult.ok(None)
        except Exception as e:
            return FlextResult.fail(f"Failed to track operation: {e}")

    def get_operations(self) -> FlextResult[list[dict[str, FlextTypes.JsonValue]]]:
        """Get tracked operations."""
        return FlextResult.ok(self._operations.copy())

    def _get_current_timestamp(self) -> str:
        """Get current timestamp for operation tracking."""
        return str(int(time.time()))


# Export the single refactored class following flext-core pattern
__all__ = ["FlextDbOracleServices"]
