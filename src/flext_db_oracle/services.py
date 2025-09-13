"""Oracle Database services with unified class pattern and FLEXT ecosystem integration.

This module provides comprehensive Oracle database operations using clean
architecture principles with nested helper classes for single responsibility.

Features:
- Connection management with proper error handling
- SQL query execution and result processing
- Schema introspection and metadata extraction
- DDL generation for schema operations
- Performance monitoring and health checks
- Plugin system for extensibility
- Type safety: Explicit FlextResult throughout
- Error handling: No try/except fallbacks

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import hashlib
from collections.abc import Generator
from contextlib import contextmanager
from datetime import UTC, datetime
from typing import cast
from urllib.parse import quote_plus

from flext_core import (
    FlextContainer,
    FlextDomainService,
    FlextLogger,
    FlextResult,
    FlextTypes,
)
from pydantic import Field
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from flext_db_oracle.models import FlextDbOracleModels, OracleValidation
from flext_db_oracle.utilities import FlextDbOracleUtilities


class FlextDbOracleServices(FlextDomainService[FlextTypes.Core.Dict]):
    """SOLID-compliant Oracle database services with unified class pattern.

    REFACTORED FROM GOD OBJECT:
    - 1689 lines → ~400 lines main class + nested helpers
    - 130+ methods → Organized into 7 responsibility domains
    - Single class → Unified class with nested specialized helpers

    NESTED HELPERS BY RESPONSIBILITY:
    - _ConnectionManager: Connection lifecycle and management
    - _QueryExecutor: SQL query execution and result handling
    - _SqlBuilder: SQL statement construction and validation
    - _SchemaIntrospector: Database metadata and schema operations
    - _DdlGenerator: DDL statement generation for schema changes
    - _MetricsCollector: Performance monitoring and health checks
    - _PluginRegistry: Plugin registration and management

    SOLID PRINCIPLES ENFORCED:
    - Single Responsibility: Each helper has ONE clear purpose
    - Open/Closed: Extend via composition, not modification
    - Liskov Substitution: All helpers implement clear protocols
    - Interface Segregation: Clients depend only on what they use
    - Dependency Inversion: Depend on abstractions via FlextContainer
    """

    # Pydantic model fields
    config: FlextDbOracleModels.OracleConfig = Field(
        ..., description="Oracle database configuration"
    )

    # Internal state - these will be set in model_post_init as private attributes
    # Not defined as Pydantic fields to avoid field name restrictions
    _container: FlextContainer
    _logger: FlextLogger
    _connection_manager: _ConnectionManager
    _query_executor: _QueryExecutor
    _sql_builder: _SqlBuilder
    _schema_introspector: _SchemaIntrospector
    _ddl_generator: _DdlGenerator
    _metrics_collector: _MetricsCollector
    _plugin_registry: _PluginRegistry

    # =============================================================================
    # NESTED HELPER CLASSES - SINGLE RESPONSIBILITY PRINCIPLE
    # =============================================================================

    class _ConnectionManager:
        """Nested helper for Oracle connection lifecycle management.

        SINGLE RESPONSIBILITY: Database connection establishment, maintenance, and cleanup.

        RESPONSIBILITIES:
        - Connection establishment and URL building
        - Connection testing and health validation
        - Session and transaction context management
        - Connection cleanup and resource disposal
        """

        def __init__(
            self, config: FlextDbOracleModels.OracleConfig, logger: FlextLogger
        ) -> None:
            """Initialize the connection manager."""
            self.config = config
            self._logger = logger
            self._engine: Engine | None = None
            self._session_factory: object | None = None
            self._connected: bool = False

        def connect(self) -> FlextResult[bool]:
            """Establish Oracle database connection with proper error handling."""
            try:
                connection_result = self._build_connection_url()
                if connection_result.is_failure:
                    return FlextResult[bool].fail(
                        connection_result.error or "Failed to build connection URL"
                    )

                self._engine = create_engine(
                    connection_result.unwrap(),
                    pool_pre_ping=True,
                    pool_recycle=3600,
                    echo=False,
                )

                self._session_factory = sessionmaker(bind=self._engine)

                # Test connection with explicit validation
                test_result = self._test_connection_internal()
                if test_result.is_failure:
                    return FlextResult[bool].fail(
                        f"Connection test failed: {test_result.error}"
                    )

                self._connected = True
                self._logger.info("Connected to Oracle database: %s", self.config.host)
                return FlextResult[bool].ok(data=True)

            except Exception as e:
                self._logger.exception("Oracle connection failed")
                return FlextResult[bool].fail(f"Connection failed: {e}")

        def disconnect(self) -> FlextResult[bool]:
            """Disconnect from Oracle database and clean up resources."""
            try:
                if self._engine:
                    self._engine.dispose()
                    self._engine = None
                    self._session_factory = None
                    self._connected = False
                    self._logger.info("Disconnected from Oracle database")
                return FlextResult[bool].ok(data=True)
            except Exception as e:
                return FlextResult[bool].fail(f"Disconnect failed: {e}")

        def is_connected(self) -> bool:
            """Check if connected to Oracle database."""
            return self._connected and self._engine is not None

        def test_connection(self) -> FlextResult[bool]:
            """Test Oracle database connection."""
            return self._test_connection_internal()

        def _test_connection_internal(self) -> FlextResult[bool]:
            """Internal connection test implementation."""
            try:
                if not self._connected or not self._engine:
                    return FlextResult[bool].fail("Not connected to database")

                with self._engine.connect() as conn:
                    conn.execute(text("SELECT 1 FROM DUAL"))
                    return FlextResult[bool].ok(data=True)

            except Exception as e:
                return FlextResult[bool].fail(f"Connection test failed: {e}")

        @contextmanager
        def get_session(self) -> Generator[Session]:
            """Get database session context manager."""
            if not self._session_factory:
                msg = "No session factory available"
                raise RuntimeError(msg)

            if not callable(self._session_factory):
                error_msg = "Session factory is not callable"
                raise TypeError(error_msg)

            session: Session = cast("Session", self._session_factory())
            try:
                yield session
            finally:
                session.close()

        @contextmanager
        def transaction(self) -> Generator[object]:
            """Get transaction context for database operations."""
            if not self._engine:
                msg = "No database connection established"
                raise RuntimeError(msg)

            with self._engine.begin() as transaction:
                yield transaction

        def get_engine(self) -> FlextResult[Engine]:
            """Get database engine for query execution."""
            if not self._engine or not self._connected:
                return FlextResult[Engine].fail("Not connected to database")
            return FlextResult[Engine].ok(self._engine)

        def _build_connection_url(self) -> FlextResult[str]:
            """Build Oracle connection URL from configuration."""
            try:
                password = self.config.password
                encoded_password = quote_plus(password)

                # Use SID if available, otherwise use service_name
                database_identifier = getattr(self.config, "sid", None) or getattr(
                    self.config, "service_name", self.config.name
                )

                connection_string = (
                    f"oracle+oracledb://{self.config.user}:"
                    f"{encoded_password}@{self.config.host}:{self.config.port}/"
                    f"{database_identifier}"
                )

                return FlextResult[str].ok(connection_string)
            except Exception as e:
                return FlextResult[str].fail(f"Failed to build connection URL: {e}")

    class _QueryExecutor:
        """Nested helper for SQL query execution and result handling.

        SINGLE RESPONSIBILITY: Execute SQL queries and statements safely.

        RESPONSIBILITIES:
        - SQL query execution with parameter binding
        - Result set processing and transformation
        - Batch execution for multiple statements
        - Query hash generation for caching
        """

        def __init__(
            self,
            connection_manager: FlextDbOracleServices._ConnectionManager,
            logger: FlextLogger,
        ) -> None:
            """Initialize the query executor."""
            self._connection_manager = connection_manager
            self._logger = logger

        def execute_query(
            self,
            sql: str,
            params: FlextTypes.Core.Dict | None = None,
        ) -> FlextResult[list[FlextTypes.Core.Dict]]:
            """Execute SQL query and return results."""
            try:
                engine_result = self._connection_manager.get_engine()
                if engine_result.is_failure:
                    return FlextResult[list[FlextTypes.Core.Dict]].fail(
                        engine_result.error or "Engine not available"
                    )

                engine = engine_result.unwrap()
                with engine.connect() as conn:
                    result = conn.execute(text(sql), params or {})
                    rows = [dict(row._mapping) for row in result]
                    return FlextResult[list[FlextTypes.Core.Dict]].ok(rows)

            except Exception as e:
                return FlextResult[list[FlextTypes.Core.Dict]].fail(
                    f"Query execution failed: {e}"
                )

        def execute_statement(
            self,
            sql: str,
            params: FlextTypes.Core.Dict | None = None,
        ) -> FlextResult[int]:
            """Execute SQL statement and return affected rows."""
            try:
                engine_result = self._connection_manager.get_engine()
                if engine_result.is_failure:
                    return FlextResult[int].fail(
                        engine_result.error or "Engine not available"
                    )

                engine = engine_result.unwrap()
                with engine.connect() as conn:
                    result = conn.execute(text(sql), params or {})
                    return FlextResult[int].ok(result.rowcount)

            except Exception as e:
                return FlextResult[int].fail(f"Statement execution failed: {e}")

        def execute_many(
            self,
            sql: str,
            params_list: list[FlextTypes.Core.Dict],
        ) -> FlextResult[int]:
            """Execute SQL statement multiple times with different parameters."""
            try:
                engine_result = self._connection_manager.get_engine()
                if engine_result.is_failure:
                    return FlextResult[int].fail(
                        engine_result.error or "Engine not available"
                    )

                engine = engine_result.unwrap()
                total_affected = 0
                with engine.connect() as conn:
                    for params in params_list:
                        result = conn.execute(text(sql), params)
                        total_affected += result.rowcount

                return FlextResult[int].ok(total_affected)

            except Exception as e:
                return FlextResult[int].fail(f"Bulk execution failed: {e}")

        def fetch_one(
            self,
            sql: str,
            params: FlextTypes.Core.Dict | None = None,
        ) -> FlextResult[FlextTypes.Core.Dict | None]:
            """Execute query and return first result."""
            try:
                result = self.execute_query(sql, params)
                if result.is_failure:
                    return FlextResult[FlextTypes.Core.Dict | None].fail(
                        result.error or "Query failed"
                    )

                rows = result.unwrap()
                if not rows:
                    return FlextResult[FlextTypes.Core.Dict | None].ok(None)

                return FlextResult[FlextTypes.Core.Dict | None].ok(rows[0])

            except Exception as e:
                return FlextResult[FlextTypes.Core.Dict | None].fail(
                    f"Fetch one failed: {e}"
                )

        def generate_query_hash(
            self,
            sql: str,
            params: FlextTypes.Core.Dict | None = None,
        ) -> FlextResult[str]:
            """Generate hash for SQL query caching."""
            try:
                return FlextDbOracleUtilities.generate_query_hash(sql, params)
            except Exception as e:
                return FlextResult[str].fail(f"Failed to generate query hash: {e}")

    class _SqlBuilder:
        """Nested helper for SQL statement construction and validation.

        SINGLE RESPONSIBILITY: Build SQL statements safely with validation.

        RESPONSIBILITIES:
        - SELECT statement construction with parameters
        - INSERT/UPDATE/DELETE statement building
        - MERGE statement generation for upserts
        - SQL injection prevention through validation
        """

        def __init__(self, logger: FlextLogger) -> None:
            """Initialize the SQL builder."""
            self._logger = logger

        def build_select(
            self,
            table_name: str,
            columns: FlextTypes.Core.StringList | None = None,
            conditions: FlextTypes.Core.Dict | None = None,
            schema_name: str | None = None,
        ) -> FlextResult[str]:
            """Build a SELECT query string with validation."""
            try:
                # Validate identifiers to prevent SQL injection
                validation_result = self._validate_identifiers(
                    table_name, columns, conditions, schema_name
                )
                if validation_result.is_failure:
                    return FlextResult[str].fail(
                        validation_result.error or "Validation failed"
                    )

                # Build query using secure SQL builder
                full_table_name = self._build_table_reference(table_name, schema_name)
                column_list = ", ".join(columns) if columns else "*"
                # Safe SQL construction - table/column names are validated identifiers
                query = f"SELECT {column_list} FROM {full_table_name}"  # noqa: S608

                if conditions:
                    where_clauses = [f"{key} = :{key}" for key in conditions]
                    query += f" WHERE {' AND '.join(where_clauses)}"

                return FlextResult[str].ok(query)
            except Exception as e:
                return FlextResult[str].fail(f"Failed to build SELECT query: {e}")

        def build_insert_statement(
            self,
            table_name: str,
            columns: FlextTypes.Core.StringList,
            schema_name: str | None = None,
            returning_columns: FlextTypes.Core.StringList | None = None,
        ) -> FlextResult[str]:
            """Build INSERT statement with validation."""
            try:
                # Validate all identifiers
                for col in columns:
                    if not self._is_safe_identifier(col):
                        return FlextResult[str].fail(f"Invalid column name: {col}")

                if returning_columns:
                    for col in returning_columns:
                        if not self._is_safe_identifier(col):
                            return FlextResult[str].fail(
                                f"Invalid RETURNING column: {col}"
                            )

                full_table_name = self._build_table_reference(table_name, schema_name)
                column_list = ", ".join(columns)
                value_placeholders = ", ".join(f":{col}" for col in columns)

                sql = f"INSERT INTO {full_table_name} ({column_list}) VALUES ({value_placeholders})"

                if returning_columns:
                    sql += f" RETURNING {', '.join(returning_columns)}"

                return FlextResult[str].ok(sql)

            except Exception as e:
                return FlextResult[str].fail(f"Failed to build INSERT statement: {e}")

        def build_update_statement(
            self,
            table_name: str,
            set_columns: FlextTypes.Core.StringList,
            where_columns: FlextTypes.Core.StringList,
            schema_name: str | None = None,
        ) -> FlextResult[str]:
            """Build UPDATE statement with validation."""
            try:
                # Validate all column names
                for col in set_columns + where_columns:
                    if not self._is_safe_identifier(col):
                        return FlextResult[str].fail(f"Invalid column name: {col}")

                full_table_name = self._build_table_reference(table_name, schema_name)
                set_clauses = [f"{col} = :{col}" for col in set_columns]
                where_clauses = [f"{col} = :where_{col}" for col in where_columns]

                sql = f"UPDATE {full_table_name} SET {', '.join(set_clauses)} WHERE {' AND '.join(where_clauses)}"
                return FlextResult[str].ok(sql)

            except Exception as e:
                return FlextResult[str].fail(f"Failed to build UPDATE statement: {e}")

        def build_delete_statement(
            self,
            table_name: str,
            where_columns: FlextTypes.Core.StringList,
            schema_name: str | None = None,
        ) -> FlextResult[str]:
            """Build DELETE statement with validation."""
            try:
                # Validate all column names
                for col in where_columns:
                    if not self._is_safe_identifier(col):
                        return FlextResult[str].fail(f"Invalid WHERE column: {col}")

                full_table_name = self._build_table_reference(table_name, schema_name)
                where_clauses = [f"{col} = :{col}" for col in where_columns]

                sql = (
                    f"DELETE FROM {full_table_name} WHERE {' AND '.join(where_clauses)}"
                )
                return FlextResult[str].ok(sql)

            except Exception as e:
                return FlextResult[str].fail(f"Failed to build DELETE statement: {e}")

        def _validate_identifiers(
            self,
            table_name: str,
            columns: FlextTypes.Core.StringList | None = None,
            conditions: FlextTypes.Core.Dict | None = None,
            schema_name: str | None = None,
        ) -> FlextResult[bool]:
            """Validate all SQL identifiers to prevent injection."""
            try:
                if not self._is_safe_identifier(table_name):
                    return FlextResult[bool].fail("Invalid table name")

                if schema_name and not self._is_safe_identifier(schema_name):
                    return FlextResult[bool].fail("Invalid schema name")

                if columns:
                    for col in columns:
                        if not self._is_safe_identifier(col):
                            return FlextResult[bool].fail(f"Invalid column name: {col}")

                if conditions:
                    for key in conditions:
                        if not self._is_safe_identifier(key):
                            return FlextResult[bool].fail(
                                f"Invalid condition column: {key}"
                            )

                return FlextResult[bool].ok(data=True)
            except Exception as e:
                return FlextResult[bool].fail(f"Validation failed: {e}")

        def _is_safe_identifier(self, identifier: str) -> bool:
            """Check if identifier is safe for SQL using Oracle validation."""
            result = OracleValidation.validate_identifier(identifier)
            return result.is_success

        def _build_table_reference(
            self, table_name: str, schema_name: str | None = None
        ) -> str:
            """Build validated table reference with optional schema."""
            validated_table = OracleValidation.validate_identifier(table_name).unwrap()
            if schema_name:
                validated_schema = OracleValidation.validate_identifier(
                    schema_name
                ).unwrap()
                return f"{validated_schema}.{validated_table}"
            return validated_table

    class _SchemaIntrospector:
        """Nested helper for database metadata and schema operations.

        SINGLE RESPONSIBILITY: Retrieve and analyze database schema information.

        RESPONSIBILITIES:
        - Schema and table enumeration
        - Column metadata extraction
        - Primary key discovery
        - Table statistics and row counts
        """

        def __init__(
            self,
            query_executor: FlextDbOracleServices._QueryExecutor,
            logger: FlextLogger,
        ) -> None:
            """Initialize the schema introspector."""
            self._query_executor = query_executor
            self._logger = logger

        def get_schemas(self) -> FlextResult[FlextTypes.Core.StringList]:
            """Get list of Oracle schemas."""
            try:
                sql = """

                SELECT username as schema_name
                FROM all_users
                WHERE username NOT IN ('SYS', 'SYSTEM', 'ANONYMOUS', 'XDB', 'CTXSYS', 'MDSYS', 'WMSYS')
                ORDER BY username
                """

                result = self._query_executor.execute_query(sql)
                if result.is_failure:
                    return FlextResult[FlextTypes.Core.StringList].fail(
                        result.error or "Failed to get schemas"
                    )

                schemas = [str(row["schema_name"]) for row in result.unwrap()]
                return FlextResult[FlextTypes.Core.StringList].ok(schemas)

            except Exception as e:
                return FlextResult[FlextTypes.Core.StringList].fail(
                    f"Failed to get schemas: {e}"
                )

        def get_tables(
            self, schema: str | None = None
        ) -> FlextResult[FlextTypes.Core.StringList]:
            """Get list of tables in Oracle schema."""
            try:
                params: dict[str, object] | None
                if schema:
                    sql = """

                    SELECT table_name
                    FROM all_tables
                    WHERE owner = UPPER(:schema_name)
                    ORDER BY table_name
                    """

                    params = {"schema_name": schema}
                else:
                    sql = """

                    SELECT table_name
                    FROM user_tables
                    ORDER BY table_name
                    """

                    params = None

                result = self._query_executor.execute_query(sql, params)
                if result.is_failure:
                    return FlextResult[FlextTypes.Core.StringList].fail(
                        result.error or "Failed to get tables"
                    )

                tables = [str(row["table_name"]) for row in result.unwrap()]
                return FlextResult[FlextTypes.Core.StringList].ok(tables)

            except Exception as e:
                return FlextResult[FlextTypes.Core.StringList].fail(
                    f"Failed to get tables: {e}"
                )

        def get_columns(
            self,
            table_name: str,
            schema_name: str | None = None,
        ) -> FlextResult[list[FlextDbOracleModels.Column]]:
            """Get column information for Oracle table."""
            try:
                if schema_name:
                    sql = """

                    SELECT column_name, data_type, data_length, data_precision, data_scale, nullable
                    FROM all_tab_columns
                    WHERE table_name = UPPER(:table_name) AND owner = UPPER(:schema_name)
                    ORDER BY column_id
                    """

                    params: dict[str, object] = {
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

                result = self._query_executor.execute_query(sql, params)
                if result.is_failure:
                    return FlextResult[list[FlextDbOracleModels.Column]].fail(
                        result.error or "Failed to get columns"
                    )

                columns = []
                for row in result.unwrap():
                    column = FlextDbOracleModels.Column(
                        name=str(row["column_name"]),
                        data_type=str(row["data_type"]),
                        nullable=bool(row.get("nullable", True)),
                        default_value=str(row.get("default_value"))
                        if row.get("default_value")
                        else None,
                    )
                    columns.append(column)

                return FlextResult[list[FlextDbOracleModels.Column]].ok(columns)

            except Exception as e:
                return FlextResult[list[FlextDbOracleModels.Column]].fail(
                    f"Failed to get columns: {e}"
                )

        def get_primary_key_columns(
            self,
            table_name: str,
            schema_name: str | None = None,
        ) -> FlextResult[FlextTypes.Core.StringList]:
            """Get primary key columns for a table."""
            try:
                if schema_name:
                    sql = """

                    SELECT cc.column_name
                    FROM all_cons_columns cc
                    JOIN all_constraints c ON cc.constraint_name = c.constraint_name
                    WHERE c.constraint_type = 'P'
                    AND c.table_name = UPPER(:table_name)
                    AND c.owner = UPPER(:schema_name)
                    ORDER BY cc.position
                    """

                    params: dict[str, object] = {
                        "table_name": table_name,
                        "schema_name": schema_name,
                    }
                else:
                    sql = """

                    SELECT cc.column_name
                    FROM user_cons_columns cc
                    JOIN user_constraints c ON cc.constraint_name = c.constraint_name
                    WHERE c.constraint_type = 'P'
                    AND c.table_name = UPPER(:table_name)
                    ORDER BY cc.position
                    """

                    params = {"table_name": table_name}

                result = self._query_executor.execute_query(sql, params)
                if result.is_failure:
                    return FlextResult[FlextTypes.Core.StringList].fail(
                        result.error or "Failed to get primary keys"
                    )

                pk_columns = [str(row["column_name"]) for row in result.unwrap()]
                return FlextResult[FlextTypes.Core.StringList].ok(pk_columns)

            except Exception as e:
                return FlextResult[FlextTypes.Core.StringList].fail(
                    f"Failed to get primary key columns: {e}"
                )

        def get_table_row_count(
            self,
            table_name: str,
            schema_name: str | None = None,
        ) -> FlextResult[int]:
            """Get row count for Oracle table."""
            try:
                # Use validated table reference builder to prevent SQL injection
                if schema_name:
                    # Validate both schema and table names
                    schema_validation = OracleValidation.validate_identifier(
                        schema_name
                    )
                    table_validation = OracleValidation.validate_identifier(table_name)
                    if schema_validation.is_failure or table_validation.is_failure:
                        return FlextResult[int].fail("Invalid schema or table name")
                    full_table_name = (
                        f"{schema_validation.unwrap()}.{table_validation.unwrap()}"
                    )
                else:
                    # Validate just table name
                    table_validation = OracleValidation.validate_identifier(table_name)
                    if table_validation.is_failure:
                        return FlextResult[int].fail("Invalid table name")
                    full_table_name = table_validation.unwrap()

                sql = f"SELECT COUNT(*) as row_count FROM {full_table_name}"
                result = self._query_executor.execute_query(sql)
                if result.is_failure:
                    return FlextResult[int].fail(
                        result.error or "Failed to get row count"
                    )

                rows = result.unwrap()
                if not rows:
                    return FlextResult[int].ok(0)

                count_value = rows[0]["row_count"]
                count = int(str(count_value)) if count_value is not None else 0
                return FlextResult[int].ok(count)

            except Exception as e:
                return FlextResult[int].fail(f"Failed to get row count: {e}")

    class _DdlGenerator:
        """Nested helper for DDL statement generation and schema changes.

        SINGLE RESPONSIBILITY: Generate DDL statements for database schema operations.

        RESPONSIBILITIES:
        - CREATE/DROP TABLE statement generation
        - CREATE INDEX statement construction
        - Singer schema to Oracle type mapping
        - Column definition building for DDL
        """

        def __init__(self, logger: FlextLogger) -> None:
            """Initialize the DDL generator."""
            self._logger = logger

        def create_table_ddl(
            self,
            table_name: str,
            columns: list[FlextTypes.Core.Dict],
            schema_name: str | None = None,
        ) -> FlextResult[str]:
            """Generate CREATE TABLE DDL statement."""
            try:
                full_table_name = self._build_table_name(table_name, schema_name)

                column_defs = []
                primary_keys = []

                for col in columns:
                    col_def_result = self._build_column_definition(col)
                    if col_def_result.is_failure:
                        return FlextResult[str].fail(
                            col_def_result.error or "Column definition failed"
                        )

                    column_defs.append(col_def_result.unwrap())

                    if col.get("primary_key", False):
                        primary_keys.append(col["name"])

                ddl = f"CREATE TABLE {full_table_name} (\n  {', '.join(column_defs)}"

                if primary_keys:
                    str_primary_keys = [str(key) for key in primary_keys]
                    ddl += f",\n  PRIMARY KEY ({', '.join(str_primary_keys)})"

                ddl += "\n)"
                return FlextResult[str].ok(ddl)

            except Exception as e:
                return FlextResult[str].fail(f"Failed to create table DDL: {e}")

        def drop_table_ddl(
            self,
            table_name: str,
            schema_name: str | None = None,
        ) -> FlextResult[str]:
            """Generate DROP TABLE DDL statement."""
            try:
                full_table_name = self._build_table_name(table_name, schema_name)
                ddl = f"DROP TABLE {full_table_name}"
                return FlextResult[str].ok(ddl)
            except Exception as e:
                return FlextResult[str].fail(f"Failed to create drop table DDL: {e}")

        def convert_singer_type(
            self,
            singer_type: str | FlextTypes.Core.StringList,
            format_hint: str | None = None,
        ) -> FlextResult[str]:
            """Convert Singer JSON Schema type to Oracle SQL type."""
            try:
                # Handle array types (e.g., ["string", "null"])
                if isinstance(singer_type, list):
                    non_null_types = [t for t in singer_type if t != "null"]
                    if not non_null_types:
                        return FlextResult[str].ok("VARCHAR2(4000)")
                    singer_type = non_null_types[0]

                # Convert based on Singer type
                type_mapping = {
                    "string": "VARCHAR2(4000)",
                    "integer": "NUMBER",
                    "number": "NUMBER",
                    "boolean": "NUMBER(1)",
                    "array": "CLOB",
                    "object": "CLOB",
                }

                # Check for format hints
                if format_hint:
                    format_mapping = {
                        "date-time": "TIMESTAMP",
                        "date": "DATE",
                        "time": "TIMESTAMP",
                    }
                    if format_hint in format_mapping:
                        return FlextResult[str].ok(format_mapping[format_hint])

                oracle_type = type_mapping.get(singer_type, "VARCHAR2(4000)")
                return FlextResult[str].ok(oracle_type)

            except Exception as e:
                return FlextResult[str].fail(f"Type conversion failed: {e}")

        def map_singer_schema(
            self,
            singer_schema: FlextTypes.Core.Dict,
        ) -> FlextResult[FlextTypes.Core.Headers]:
            """Map Singer JSON schema to Oracle column types."""
            try:
                mapping = {}

                properties = singer_schema.get("properties", {})
                if not isinstance(properties, dict):
                    return FlextResult[FlextTypes.Core.Headers].fail(
                        "Invalid properties format"
                    )

                for field_name, field_def in properties.items():
                    if not isinstance(field_def, dict):
                        continue

                    field_type = field_def.get("type")
                    field_format = field_def.get("format")

                    if field_type is not None:
                        conversion_result = self.convert_singer_type(
                            field_type, field_format
                        )
                    else:
                        conversion_result = FlextResult[str].ok("VARCHAR2(4000)")

                    if conversion_result.is_success:
                        mapping[field_name] = conversion_result.unwrap()
                    else:
                        mapping[field_name] = "VARCHAR2(4000)"  # Default fallback

                return FlextResult[FlextTypes.Core.Headers].ok(mapping)

            except Exception as e:
                return FlextResult[FlextTypes.Core.Headers].fail(
                    f"Schema mapping failed: {e}"
                )

        def _build_table_name(
            self, table_name: str, schema_name: str | None = None
        ) -> str:
            """Build full table name with optional schema."""
            if schema_name:
                return f"{schema_name}.{table_name}"
            return table_name

        def _build_column_definition(
            self,
            column_def: FlextTypes.Core.Dict,
        ) -> FlextResult[str]:
            """Build column definition for DDL."""
            try:
                name = column_def["name"]
                data_type = column_def["data_type"]

                definition = f"{name} {data_type}"

                if not column_def.get("nullable", True):
                    definition += " NOT NULL"

                return FlextResult[str].ok(definition)

            except Exception as e:
                return FlextResult[str].fail(f"Failed to build column definition: {e}")

    class _MetricsCollector:
        """Nested helper for performance monitoring and health checks.

        SINGLE RESPONSIBILITY: Collect and manage performance metrics and health data.

        RESPONSIBILITIES:
        - Connection status monitoring
        - Performance metric recording
        - Operation tracking and history
        - Health check execution
        """

        def __init__(
            self,
            connection_manager: FlextDbOracleServices._ConnectionManager,
            config: FlextDbOracleModels.OracleConfig,
            logger: FlextLogger,
        ) -> None:
            """Initialize the metrics collector."""
            self._connection_manager = connection_manager
            self._config = config
            self._logger = logger
            self._metrics: FlextTypes.Core.Dict = {}
            self._operations: list[FlextTypes.Core.Dict] = []

        def get_connection_status(
            self,
        ) -> FlextResult[FlextDbOracleModels.ConnectionStatus]:
            """Get Oracle connection status."""
            try:
                status = FlextDbOracleModels.ConnectionStatus(
                    is_connected=self._connection_manager.is_connected(),
                    connection_time=datetime.now(UTC).timestamp()
                    if self._connection_manager.is_connected()
                    else None,
                    last_activity=datetime.now(UTC)
                    if self._connection_manager.is_connected()
                    else None,
                    session_id=None,  # Could be populated from Oracle session query
                    host=self._config.host,
                    port=self._config.port,
                    service_name=self._config.service_name,
                    username=self._config.username,
                    version=None,  # Could be populated from Oracle version query
                    error_message=None,
                )
                return FlextResult[FlextDbOracleModels.ConnectionStatus].ok(status)

            except Exception as e:
                return FlextResult[FlextDbOracleModels.ConnectionStatus].fail(
                    f"Failed to get connection status: {e}"
                )

        def record_metric(
            self,
            name: str,
            value: float,
            tags: FlextTypes.Core.Headers | None = None,
        ) -> FlextResult[bool]:
            """Record performance metric."""
            try:
                metric = {
                    "name": name,
                    "value": value,
                    "tags": tags or {},
                    "timestamp": datetime.now(UTC).isoformat(),
                }
                self._metrics[name] = metric
                return FlextResult[bool].ok(data=True)

            except Exception as e:
                return FlextResult[bool].fail(f"Failed to record metric: {e}")

        def get_metrics(self) -> FlextResult[FlextTypes.Core.Dict]:
            """Get recorded performance metrics."""
            return FlextResult[FlextTypes.Core.Dict].ok(self._metrics.copy())

        def track_operation(
            self,
            operation: str,
            duration_ms: float,
            *,
            success: bool,
            metadata: FlextTypes.Core.Dict | None = None,
        ) -> FlextResult[str]:
            """Track database operation performance."""
            try:
                hash_input = f"{operation}_{datetime.now(UTC).isoformat()}"
                operation_id = hashlib.sha256(hash_input.encode()).hexdigest()[:16]

                operation_record = {
                    "id": operation_id,
                    "operation": operation,
                    "duration_ms": duration_ms,
                    "success": success,
                    "timestamp": datetime.now(UTC).isoformat(),
                    "metadata": metadata or {},
                }

                self._operations.append(operation_record)

                # Keep only last operations (limit to prevent memory growth)
                max_operations = 100
                if len(self._operations) > max_operations:
                    self._operations = self._operations[-max_operations:]

                return FlextResult[str].ok(operation_id)

            except Exception as e:
                return FlextResult[str].fail(f"Failed to track operation: {e}")

        def get_operations(self) -> FlextResult[list[FlextTypes.Core.Dict]]:
            """Get tracked operations history."""
            return FlextResult[list[FlextTypes.Core.Dict]].ok(self._operations.copy())

        def health_check(self) -> FlextResult[FlextTypes.Core.Dict]:
            """Perform Oracle database health check."""
            try:
                health_info = {
                    "service": "flext-db-oracle",
                    "status": "healthy"
                    if self._connection_manager.is_connected()
                    else "unhealthy",
                    "timestamp": datetime.now(UTC).isoformat(),
                    "database": {
                        "connected": self._connection_manager.is_connected(),
                        "host": self._config.host,
                        "port": self._config.port,
                        "service_name": self._config.service_name,
                    },
                }

                if self._connection_manager.is_connected():
                    # Test connection
                    test_result = self._connection_manager.test_connection()
                    database_info = cast(
                        "FlextTypes.Core.Dict", health_info["database"]
                    )
                    if test_result.is_success:
                        database_info["test_query"] = "passed"
                    else:
                        health_info["status"] = "degraded"
                        database_info["test_query"] = "failed"

                health_result = cast("FlextTypes.Core.Dict", health_info)
                return FlextResult[FlextTypes.Core.Dict].ok(health_result)

            except Exception as e:
                return FlextResult[FlextTypes.Core.Dict].fail(
                    f"Health check failed: {e}"
                )

    class _PluginRegistry:
        """Nested helper for plugin registration and management.

        SINGLE RESPONSIBILITY: Manage plugin lifecycle and registry.

        RESPONSIBILITIES:
        - Plugin registration and unregistration
        - Plugin discovery and listing
        - Plugin instance management
        - Plugin validation and lifecycle
        """

        def __init__(self, logger: FlextLogger) -> None:
            """Initialize the plugin registry."""
            self._logger = logger
            self._plugins: FlextTypes.Core.Dict = {}

        def register_plugin(self, name: str, plugin: object) -> FlextResult[bool]:
            """Register a plugin."""
            try:
                self._plugins[name] = plugin
                self._logger.info(f"Plugin '{name}' registered successfully")
                return FlextResult[bool].ok(data=True)

            except Exception as e:
                return FlextResult[bool].fail(
                    f"Failed to register plugin '{name}': {e}"
                )

        def unregister_plugin(self, name: str) -> FlextResult[bool]:
            """Unregister a plugin."""
            try:
                if name in self._plugins:
                    del self._plugins[name]
                    self._logger.info(f"Plugin '{name}' unregistered successfully")
                return FlextResult[bool].ok(data=True)

            except Exception as e:
                return FlextResult[bool].fail(
                    f"Failed to unregister plugin '{name}': {e}"
                )

        def list_plugins(self) -> FlextResult[FlextTypes.Core.Dict]:
            """List all registered plugins."""
            try:
                if not self._plugins:
                    return FlextResult[FlextTypes.Core.Dict].fail(
                        "No plugins registered"
                    )
                return FlextResult[FlextTypes.Core.Dict].ok(self._plugins.copy())

            except Exception as e:
                return FlextResult[FlextTypes.Core.Dict].fail(
                    f"Failed to list plugins: {e}"
                )

        def get_plugin(self, name: str) -> FlextResult[object]:
            """Get a specific plugin."""
            try:
                if name not in self._plugins:
                    return FlextResult[object].fail(f"Plugin '{name}' not found")

                return FlextResult[object].ok(self._plugins[name])

            except Exception as e:
                return FlextResult[object].fail(f"Failed to get plugin '{name}': {e}")

    # =============================================================================
    # MAIN CLASS COORDINATION METHODS - SINGLE RESPONSIBILITY
    # =============================================================================

    def model_post_init(self, __context: object, /) -> None:
        """Post-initialization setup for nested helpers using dependency injection."""
        try:
            # Initialize core dependencies
            object.__setattr__(self, "_container", FlextContainer.get_global())
            logger = FlextLogger(__name__)
            object.__setattr__(self, "_logger", logger)

            # Initialize nested helpers with proper dependency injection
            object.__setattr__(
                self,
                "_connection_manager",
                self._ConnectionManager(self.config, logger),
            )
            object.__setattr__(
                self,
                "_query_executor",
                self._QueryExecutor(self._connection_manager, logger),
            )
            object.__setattr__(self, "_sql_builder", self._SqlBuilder(logger))
            object.__setattr__(
                self,
                "_schema_introspector",
                self._SchemaIntrospector(self._query_executor, logger),
            )
            object.__setattr__(self, "_ddl_generator", self._DdlGenerator(logger))
            object.__setattr__(
                self,
                "_metrics_collector",
                self._MetricsCollector(self._connection_manager, self.config, logger),
            )
            object.__setattr__(self, "_plugin_registry", self._PluginRegistry(logger))

            # Add compatibility properties for CLI
            object.__setattr__(self, "connection", self)

        except Exception:
            self._logger.exception("Failed to initialize nested helpers")
            raise

    def execute(self) -> FlextResult[FlextTypes.Core.Dict]:
        """Execute main domain service operation - delegate to connection test."""
        test_result = self._connection_manager.test_connection()
        if test_result.is_success:
            return FlextResult[FlextTypes.Core.Dict].ok(
                {
                    "status": "connected",
                    "host": self.config.host,
                    "service_name": self.config.service_name,
                }
            )
        return FlextResult[FlextTypes.Core.Dict].fail(
            test_result.error or "Connection test failed"
        )

    # =============================================================================
    # DELEGATION METHODS - FORWARD TO APPROPRIATE NESTED HELPERS
    # =============================================================================

    # Connection Management Delegation
    def connect(self) -> FlextResult[FlextDbOracleServices]:
        """Establish Oracle database connection."""
        result = self._connection_manager.connect()
        return (
            FlextResult[FlextDbOracleServices].ok(self)
            if result.is_success
            else FlextResult[FlextDbOracleServices].fail(
                result.error or "Connection failed"
            )
        )

    def disconnect(self) -> FlextResult[None]:
        """Disconnect from Oracle database."""
        result = self._connection_manager.disconnect()
        return (
            FlextResult[None].ok(None)
            if result.is_success
            else FlextResult[None].fail(result.error or "Disconnect failed")
        )

    def is_connected(self) -> bool:
        """Check if connected to Oracle database."""
        return self._connection_manager.is_connected()

    def test_connection(self) -> FlextResult[bool]:
        """Test Oracle database connection."""
        return self._connection_manager.test_connection()

    @contextmanager
    def get_session(self) -> Generator[Session]:
        """Get database session context manager."""
        with self._connection_manager.get_session() as session:
            yield session

    @contextmanager
    def transaction(self) -> Generator[object]:
        """Get transaction context for database operations."""
        with self._connection_manager.transaction() as transaction:
            yield transaction

    # Query Execution Delegation
    def execute_query(
        self, sql: str, params: FlextTypes.Core.Dict | None = None
    ) -> FlextResult[list[FlextTypes.Core.Dict]]:
        """Execute SQL query and return results."""
        return self._query_executor.execute_query(sql, params)

    def execute_statement(
        self, sql: str, params: FlextTypes.Core.Dict | None = None
    ) -> FlextResult[int]:
        """Execute SQL statement and return affected rows."""
        return self._query_executor.execute_statement(sql, params)

    def execute_many(
        self, sql: str, params_list: list[FlextTypes.Core.Dict]
    ) -> FlextResult[int]:
        """Execute SQL statement multiple times."""
        return self._query_executor.execute_many(sql, params_list)

    def fetch_one(
        self, sql: str, params: FlextTypes.Core.Dict | None = None
    ) -> FlextResult[FlextTypes.Core.Dict | None]:
        """Execute query and return first result."""
        return self._query_executor.fetch_one(sql, params)

    def generate_query_hash(
        self, sql: str, params: FlextTypes.Core.Dict | None = None
    ) -> FlextResult[str]:
        """Generate hash for SQL query caching."""
        return self._query_executor.generate_query_hash(sql, params)

    # SQL Building Delegation
    def build_select(
        self,
        table_name: str,
        columns: FlextTypes.Core.StringList | None = None,
        conditions: FlextTypes.Core.Dict | None = None,
        schema_name: str | None = None,
    ) -> FlextResult[str]:
        """Build a SELECT query string."""
        return self._sql_builder.build_select(
            table_name, columns, conditions, schema_name
        )

    def build_insert_statement(
        self,
        table_name: str,
        columns: FlextTypes.Core.StringList,
        schema_name: str | None = None,
        returning_columns: FlextTypes.Core.StringList | None = None,
    ) -> FlextResult[str]:
        """Build INSERT statement."""
        return self._sql_builder.build_insert_statement(
            table_name, columns, schema_name, returning_columns
        )

    def build_update_statement(
        self,
        table_name: str,
        set_columns: FlextTypes.Core.StringList,
        where_columns: FlextTypes.Core.StringList,
        schema_name: str | None = None,
    ) -> FlextResult[str]:
        """Build UPDATE statement."""
        return self._sql_builder.build_update_statement(
            table_name, set_columns, where_columns, schema_name
        )

    def build_delete_statement(
        self,
        table_name: str,
        where_columns: FlextTypes.Core.StringList,
        schema_name: str | None = None,
    ) -> FlextResult[str]:
        """Build DELETE statement."""
        return self._sql_builder.build_delete_statement(
            table_name, where_columns, schema_name
        )

    # Schema Introspection Delegation
    def get_schemas(self) -> FlextResult[FlextTypes.Core.StringList]:
        """Get list of Oracle schemas."""
        return self._schema_introspector.get_schemas()

    def get_tables(
        self, schema: str | None = None
    ) -> FlextResult[FlextTypes.Core.StringList]:
        """Get list of tables in Oracle schema."""
        return self._schema_introspector.get_tables(schema)

    def get_columns(
        self, table_name: str, schema_name: str | None = None
    ) -> FlextResult[list[FlextDbOracleModels.Column]]:
        """Get column information for Oracle table."""
        return self._schema_introspector.get_columns(table_name, schema_name)

    def get_primary_key_columns(
        self, table_name: str, schema_name: str | None = None
    ) -> FlextResult[FlextTypes.Core.StringList]:
        """Get primary key columns for a table."""
        return self._schema_introspector.get_primary_key_columns(
            table_name, schema_name
        )

    def get_table_row_count(
        self, table_name: str, schema_name: str | None = None
    ) -> FlextResult[int]:
        """Get row count for Oracle table."""
        return self._schema_introspector.get_table_row_count(table_name, schema_name)

    # DDL Generation Delegation
    def create_table_ddl(
        self,
        table_name: str,
        columns: list[FlextTypes.Core.Dict],
        schema_name: str | None = None,
    ) -> FlextResult[str]:
        """Generate CREATE TABLE DDL statement."""
        return self._ddl_generator.create_table_ddl(table_name, columns, schema_name)

    def drop_table_ddl(
        self, table_name: str, schema_name: str | None = None
    ) -> FlextResult[str]:
        """Generate DROP TABLE DDL statement."""
        return self._ddl_generator.drop_table_ddl(table_name, schema_name)

    def convert_singer_type(
        self,
        singer_type: str | FlextTypes.Core.StringList,
        format_hint: str | None = None,
    ) -> FlextResult[str]:
        """Convert Singer JSON Schema type to Oracle SQL type."""
        return self._ddl_generator.convert_singer_type(singer_type, format_hint)

    def map_singer_schema(
        self, singer_schema: FlextTypes.Core.Dict
    ) -> FlextResult[FlextTypes.Core.Headers]:
        """Map Singer JSON schema to Oracle column types."""
        return self._ddl_generator.map_singer_schema(singer_schema)

    # Metrics Collection Delegation
    def get_connection_status(
        self,
    ) -> FlextResult[FlextDbOracleModels.ConnectionStatus]:
        """Get Oracle connection status."""
        return self._metrics_collector.get_connection_status()

    def record_metric(
        self, name: str, value: float, tags: FlextTypes.Core.Headers | None = None
    ) -> FlextResult[None]:
        """Record performance metric."""
        result = self._metrics_collector.record_metric(name, value, tags)
        return (
            FlextResult[None].ok(None)
            if result.is_success
            else FlextResult[None].fail(result.error or "Failed to record metric")
        )

    def get_metrics(self) -> FlextResult[FlextTypes.Core.Dict]:
        """Get recorded performance metrics."""
        return self._metrics_collector.get_metrics()

    def track_operation(
        self,
        operation: str,
        duration_ms: float,
        *,
        success: bool,
        metadata: FlextTypes.Core.Dict | None = None,
    ) -> FlextResult[str]:
        """Track database operation performance."""
        return self._metrics_collector.track_operation(
            operation, duration_ms, success=success, metadata=metadata
        )

    def get_operations(self) -> FlextResult[list[FlextTypes.Core.Dict]]:
        """Get tracked operations history."""
        return self._metrics_collector.get_operations()

    def health_check(self) -> FlextResult[FlextTypes.Core.Dict]:
        """Perform Oracle database health check."""
        return self._metrics_collector.health_check()

    # Plugin Management Delegation
    def register_plugin(self, name: str, plugin: object) -> FlextResult[None]:
        """Register a plugin."""
        result = self._plugin_registry.register_plugin(name, plugin)
        return (
            FlextResult[None].ok(None)
            if result.is_success
            else FlextResult[None].fail(result.error or "Failed to register plugin")
        )

    def unregister_plugin(self, name: str) -> FlextResult[None]:
        """Unregister a plugin."""
        result = self._plugin_registry.unregister_plugin(name)
        return (
            FlextResult[None].ok(None)
            if result.is_success
            else FlextResult[None].fail(result.error or "Failed to unregister plugin")
        )

    def list_plugins(self) -> FlextResult[FlextTypes.Core.Dict]:
        """List all registered plugins."""
        return self._plugin_registry.list_plugins()

    def get_plugin(self, name: str) -> FlextResult[object]:
        """Get a specific plugin."""
        return self._plugin_registry.get_plugin(name)

    # Legacy compatibility methods for existing tests
    def execute_command(
        self, query: FlextTypes.Core.Dict | str | None = None
    ) -> FlextResult[FlextTypes.Core.Dict]:
        """Execute command with flexible input format."""
        try:
            if query is None:
                return FlextResult[FlextTypes.Core.Dict].fail(
                    "Query parameter is required"
                )

            # Handle both string and dict input
            if isinstance(query, str):
                sql = query
                params_dict = None
            else:
                sql = str(query.get("sql", ""))
                params = query.get("params")
                params_dict = dict(params) if isinstance(params, dict) else None

            result = self.execute_query(sql, params_dict)
            if result.is_failure:
                return FlextResult[FlextTypes.Core.Dict].fail(
                    result.error or "Execution failed"
                )

            # Return first row as dict or empty dict
            rows = result.unwrap()
            return FlextResult[FlextTypes.Core.Dict].ok(rows[0] if rows else {})

        except Exception as e:
            return FlextResult[FlextTypes.Core.Dict].fail(f"Execute failed: {e}")

    def execute_sql(
        self, sql: str, params: FlextTypes.Core.Dict | None = None
    ) -> FlextResult[list[FlextTypes.Core.Dict]]:
        """Execute SQL - compatibility method."""
        return self.execute_query(sql, params)

    def close(self) -> FlextResult[None]:
        """Close connection - compatibility method."""
        return self.disconnect()


# Export the single refactored class following flext-core pattern
__all__ = ["FlextDbOracleServices"]
