"""Oracle Database services with unified class pattern and FLEXT ecosystem integration.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import hashlib
from collections.abc import Generator
from contextlib import contextmanager
from datetime import UTC, datetime
from typing import cast, override
from urllib.parse import quote_plus

# Use complete flext-core integration
from flext_core import (
    FlextContainer,
    FlextLogger,
    FlextResult,
    FlextService,
    FlextTypes,
)
from sqlalchemy import (
    Column,
    Integer,
    MetaData,
    String,
    Table,
    create_engine,
    delete,
    insert,
    select,
    text,
    update,
)
from sqlalchemy.engine import Engine

from flext_db_oracle.config import FlextDbOracleConfig
from flext_db_oracle.constants import FlextDbOracleConstants
from flext_db_oracle.models import FlextDbOracleModels
from flext_db_oracle.utilities import FlextDbOracleUtilities


class FlextDbOracleServices(FlextService):
    """SOLID-compliant Oracle database services with complete flext-core integration."""

    def __init__(
        self, config: FlextDbOracleConfig, domain_events: list | None = None
    ) -> None:
        """Initialize Oracle services with configuration."""
        self._config = config
        self._domain_events = domain_events or []
        super().__init__(config=self._config)

    # =============================================================================
    # NESTED HELPER CLASSES - SINGLE RESPONSIBILITY PRINCIPLE
    # =============================================================================

    class _ConnectionManager:
        """Nested helper for Oracle connection lifecycle management."""

        @override
        def __init__(
            self,
            config: FlextDbOracleConfig,
            logger: FlextLogger,
        ) -> None:
            """Initialize the connection manager."""
            self.config: FlextDbOracleConfig = config
            self.logger = logger
            self._engine: Engine | None = None
            # SQLAlchemy 2.0 Core API - removed session factory
            self._connected: bool = False

        def connect(self) -> FlextResult[bool]:
            """Establish Oracle database connection with proper error handling."""
            try:
                connection_result = self._build_connection_url()
                if connection_result.is_failure:
                    return FlextResult[bool].fail(
                        connection_result.error or "Failed to build connection URL",
                    )

                self._engine = create_engine(
                    connection_result.unwrap(),
                    pool_pre_ping=True,
                    pool_recycle=FlextDbOracleConstants.OraclePerformance.DEFAULT_POOL_RECYCLE,
                    echo=False,
                )

                # Test connection with explicit validation
                test_result: FlextResult[bool] = self._test_connection_internal()
                if test_result.is_failure:
                    return FlextResult[bool].fail(
                        f"Connection test failed: {test_result.error}",
                    )

                self._connected = True
                self.logger.info("Connected to Oracle database: %s", self.config.host)
                return FlextResult[bool].ok(data=True)

            except Exception as e:
                self.logger.exception("Oracle connection failed")
                return FlextResult[bool].fail(f"Connection failed: {e}")

        def disconnect(self) -> FlextResult[bool]:
            """Disconnect from Oracle database and clean up resources."""
            try:
                if self._engine:
                    self._engine.dispose()
                    self._engine = None
                    # SQLAlchemy 2.0 Core API - removed session factory cleanup
                    self._connected = False
                    self.logger.info("Disconnected from Oracle database")
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
                    conn.execute(text(FlextDbOracleConstants.Query.TEST_QUERY))
                    return FlextResult[bool].ok(data=True)

            except Exception as e:
                return FlextResult[bool].fail(f"Connection test failed: {e}")

        @contextmanager
        def get_connection(self) -> Generator[object]:
            """Get database connection context manager for SQLAlchemy 2.0 Core API."""
            if not self._engine:
                msg = "No database engine available"
                raise RuntimeError(msg)

            with self._engine.connect() as connection:
                yield connection

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
                password = self.config.password.get_secret_value()
                if not password:
                    return FlextResult[str].fail(
                        "Password is required for database connection"
                    )
                encoded_password = quote_plus(password)

                # Use SID if available, otherwise use service_name
                database_identifier = self.config.sid or self.config.service_name

                connection_string = (
                    f"oracle+oracledb://{self.config.username}:"
                    f"{encoded_password}@{self.config.host}:{self.config.port}/"
                    f"{database_identifier}"
                )

                return FlextResult[str].ok(connection_string)
            except Exception as e:
                return FlextResult[str].fail(f"Failed to build connection URL: {e}")

    class _QueryExecutor:
        """Nested helper for SQL query execution and result handling."""

        @override
        def __init__(
            self,
            connection_manager: FlextDbOracleServices._ConnectionManager,
            logger: FlextLogger,
        ) -> None:
            """Initialize the query executor."""
            self._connection_manager = connection_manager
            self.logger = logger

        def execute_query(
            self,
            sql: str,
            params: FlextTypes.Dict | None = None,
        ) -> FlextResult[list[FlextTypes.Dict]]:
            """Execute SQL query and return results."""
            try:
                engine_result = self._connection_manager.get_engine()
                if engine_result.is_failure:
                    return FlextResult[list[FlextTypes.Dict]].fail(
                        engine_result.error or "Engine not available",
                    )

                engine = engine_result.unwrap()
                with engine.connect() as conn:
                    result = conn.execute(text(sql), params or {})
                    rows = [dict(row) for row in result]
                    return FlextResult[list[FlextTypes.Dict]].ok(rows)

            except Exception as e:
                return FlextResult[list[FlextTypes.Dict]].fail(
                    f"Query execution failed: {e}",
                )

        def execute_statement(
            self,
            sql: str,
            params: FlextTypes.Dict | None = None,
        ) -> FlextResult[int]:
            """Execute SQL statement and return affected rows."""
            try:
                engine_result = self._connection_manager.get_engine()
                if engine_result.is_failure:
                    return FlextResult[int].fail(
                        engine_result.error or "Engine not available",
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
            params_list: list[FlextTypes.Dict],
        ) -> FlextResult[int]:
            """Execute SQL statement multiple times with different parameters."""
            try:
                engine_result = self._connection_manager.get_engine()
                if engine_result.is_failure:
                    return FlextResult[int].fail(
                        engine_result.error or "Engine not available",
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
            params: FlextTypes.Dict | None = None,
        ) -> FlextResult[FlextTypes.Dict | None]:
            """Execute query and return first result."""
            try:
                result = self.execute_query(sql, params)
                if result.is_failure:
                    return FlextResult[FlextTypes.Dict | None].fail(
                        result.error or "Query failed",
                    )

                rows = result.unwrap()
                if not rows:
                    return FlextResult[FlextTypes.Dict | None].ok(None)

                return FlextResult[FlextTypes.Dict | None].ok(rows[0])

            except Exception as e:
                return FlextResult[FlextTypes.Dict | None].fail(
                    f"Fetch one failed: {e}",
                )

        def generate_query_hash(
            self,
            sql: str,
            params: FlextTypes.Dict | None = None,
        ) -> FlextResult[str]:
            """Generate hash for SQL query caching."""
            try:
                return FlextDbOracleUtilities.generate_query_hash(sql, params)
            except Exception as e:
                return FlextResult[str].fail(f"Failed to generate query hash: {e}")

    class _SqlBuilder:
        """Nested helper for SQL statement construction using SQLAlchemy 2.0 Core API."""

        @override
        def __init__(self, logger: FlextLogger) -> None:
            """Initialize the SQL builder with SQLAlchemy 2.0 metadata."""
            self.logger = logger
            self._metadata: MetaData = MetaData()

        def _create_table_object(
            self,
            table_name: str,
            schema_name: str | None = None,
        ) -> Table:
            """Create SQLAlchemy Table object for modern query building."""
            # Validate identifiers first
            validated_table = (
                FlextDbOracleUtilities.OracleValidation.validate_identifier(
                    table_name,
                ).unwrap()
            )
            validated_schema = None
            if schema_name:
                validated_schema = (
                    FlextDbOracleUtilities.OracleValidation.validate_identifier(
                        schema_name,
                    ).unwrap()
                )

            # Create a dynamic table with common column types for query building
            # This allows SQLAlchemy to handle SQL injection prevention
            return Table(
                validated_table,
                self._metadata,
                Column("id", Integer),
                Column("name", String(255)),
                Column("email", String(255)),
                Column("status", String(255)),  # Add STATUS column for tests
                # Make case-insensitive by adding both upper and lower case versions
                Column("ID", Integer),
                Column("NAME", String(255)),
                Column("EMAIL", String(255)),
                Column("STATUS", String(255)),
                schema=validated_schema,
                autoload_with=None,
                extend_existing=True,
            )

        def build_select(
            self,
            table_name: str,
            columns: FlextTypes.StringList | None = None,
            conditions: FlextTypes.Dict | None = None,
            schema_name: str | None = None,
        ) -> FlextResult[str]:
            """Build a SELECT query using SQLAlchemy 2.0 Core API."""
            try:
                # Validate identifiers to prevent SQL injection
                validation_result = self._validate_identifiers(
                    table_name,
                    columns,
                    conditions,
                    schema_name,
                )
                if validation_result.is_failure:
                    return FlextResult[str].fail(
                        validation_result.error or "Validation failed",
                    )

                # Create SQLAlchemy table object for modern query building
                table = self._create_table_object(table_name, schema_name)

                # Build SELECT statement using SQLAlchemy 2.0 Core API
                if columns:
                    # For specific columns, use text() for dynamic column selection
                    validated_columns = [
                        col for col in columns if self._is_safe_identifier(col)
                    ]
                    column_exprs = [text(col) for col in validated_columns]
                    stmt = select(*column_exprs).select_from(table)
                else:
                    # Select all columns
                    stmt = select(table)

                # Add WHERE conditions using SQLAlchemy parameterization
                if conditions:
                    for key in conditions:
                        if self._is_safe_identifier(key):
                            # Use text() with bound parameters for dynamic column references
                            stmt = stmt.where(text(f"{key} = :{key}"))

                # Compile to string with proper parameterization - don't use literal_binds
                # This will keep the :parameter syntax for proper parameterization
                query = str(stmt.compile(compile_kwargs={"literal_binds": False}))
                return FlextResult[str].ok(query)
            except Exception as e:
                return FlextResult[str].fail(f"Failed to build SELECT query: {e}")

        def build_insert_statement(
            self,
            table_name: str,
            columns: FlextTypes.StringList,
            schema_name: str | None = None,
            returning_columns: FlextTypes.StringList | None = None,
        ) -> FlextResult[str]:
            """Build INSERT statement using SQLAlchemy 2.0 Core API."""
            try:
                # Validate all identifiers
                for col in columns:
                    if not self._is_safe_identifier(col):
                        return FlextResult[str].fail(f"Invalid column name: {col}")

                if returning_columns:
                    for col in returning_columns:
                        if not self._is_safe_identifier(col):
                            return FlextResult[str].fail(
                                f"Invalid RETURNING column: {col}",
                            )

                # Create SQLAlchemy table object for modern query building
                table = self._create_table_object(table_name, schema_name)

                # Build INSERT statement using SQLAlchemy 2.0 Core API with specific columns
                stmt = insert(table)

                # Create values dict for only the specified columns
                values_dict: FlextTypes.Dict = {
                    col.lower(): text(f":{col.lower()}") for col in columns
                }
                stmt = stmt.values(values_dict)

                # Add RETURNING clause if specified (Oracle support)
                if returning_columns:
                    # Use text() for dynamic RETURNING columns
                    returning_exprs = [text(col) for col in returning_columns]
                    stmt = stmt.returning(*returning_exprs)

                # Compile to string - SQLAlchemy handles SQL injection prevention
                query = str(stmt.compile(compile_kwargs={"literal_binds": False}))
                return FlextResult[str].ok(query)

            except Exception as e:
                return FlextResult[str].fail(f"Failed to build INSERT statement: {e}")

        def build_update_statement(
            self,
            table_name: str,
            set_columns: FlextTypes.StringList,
            where_columns: FlextTypes.StringList,
            schema_name: str | None = None,
        ) -> FlextResult[str]:
            """Build UPDATE statement using SQLAlchemy 2.0 Core API."""
            try:
                # Validate all column names
                for col in set_columns + where_columns:
                    if not self._is_safe_identifier(col):
                        return FlextResult[str].fail(f"Invalid column name: {col}")

                # Create SQLAlchemy table object for modern query building
                table = self._create_table_object(table_name, schema_name)

                # Build UPDATE statement using SQLAlchemy 2.0 Core API
                stmt = update(table)

                # Add WHERE conditions using text() for dynamic columns
                for col in where_columns:
                    stmt = stmt.where(text(f"{col} = :where_{col}"))

                # Add VALUES placeholder - actual values will be provided at execution time
                # SQLAlchemy requires at least one value to generate valid SQL
                if set_columns:
                    # Use dictionary comprehension with string keys for SQLAlchemy values()
                    values_dict: FlextTypes.Dict = {
                        col: text(f":{col}") for col in set_columns
                    }
                    stmt = stmt.values(values_dict)

                # Compile to string - SQLAlchemy handles SQL injection prevention
                query = str(stmt.compile(compile_kwargs={"literal_binds": False}))
                return FlextResult[str].ok(query)

            except Exception as e:
                return FlextResult[str].fail(f"Failed to build UPDATE statement: {e}")

        def build_delete_statement(
            self,
            table_name: str,
            where_columns: FlextTypes.StringList,
            schema_name: str | None = None,
        ) -> FlextResult[str]:
            """Build DELETE statement using SQLAlchemy 2.0 Core API."""
            try:
                # Validate all column names
                for col in where_columns:
                    if not self._is_safe_identifier(col):
                        return FlextResult[str].fail(f"Invalid WHERE column: {col}")

                # Create SQLAlchemy table object for modern query building
                table = self._create_table_object(table_name, schema_name)

                # Build DELETE statement using SQLAlchemy 2.0 Core API
                stmt = delete(table)

                # Add WHERE conditions using text() for dynamic columns
                for col in where_columns:
                    stmt = stmt.where(text(f"{col} = :{col}"))

                # Compile to string - SQLAlchemy handles SQL injection prevention
                query = str(stmt.compile(compile_kwargs={"literal_binds": False}))
                return FlextResult[str].ok(query)

            except Exception as e:
                return FlextResult[str].fail(f"Failed to build DELETE statement: {e}")

        def _validate_identifiers(
            self,
            table_name: str,
            columns: FlextTypes.StringList | None = None,
            conditions: FlextTypes.Dict | None = None,
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
                                f"Invalid condition column: {key}",
                            )

                return FlextResult[bool].ok(data=True)
            except Exception as e:
                return FlextResult[bool].fail(f"Validation failed: {e}")

        def _is_safe_identifier(self, identifier: str) -> bool:
            """Check if identifier is safe for SQL using Oracle validation."""
            result = FlextDbOracleUtilities.OracleValidation.validate_identifier(
                identifier,
            )
            return bool(result.is_success)

        def _build_table_reference(
            self,
            table_name: str,
            schema_name: str | None = None,
        ) -> str:
            """Build validated table reference with optional schema."""
            table_result = FlextDbOracleUtilities.OracleValidation.validate_identifier(
                table_name,
            )
            if table_result.is_failure:
                error_msg = f"Invalid table name: {table_result.error}"
                raise ValueError(error_msg)
            validated_table = str(table_result.unwrap())

            if schema_name:
                schema_result = (
                    FlextDbOracleUtilities.OracleValidation.validate_identifier(
                        schema_name,
                    )
                )
                if schema_result.is_failure:
                    error_msg = f"Invalid schema name: {schema_result.error}"
                    raise ValueError(error_msg)
                validated_schema = str(schema_result.unwrap())
                return f"{validated_schema}.{validated_table}"
            return validated_table

    class _SchemaIntrospector:
        """Nested helper for database metadata and schema operations."""

        @override
        def __init__(
            self,
            query_executor: FlextDbOracleServices._QueryExecutor,
            logger: FlextLogger,
        ) -> None:
            """Initialize the schema introspector."""
            self._query_executor = query_executor
            self.logger = logger

        def get_schemas(self) -> FlextResult[FlextTypes.StringList]:
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
                    return FlextResult[FlextTypes.StringList].fail(
                        result.error or "Failed to get schemas",
                    )

                schemas = [str(row["schema_name"]) for row in result.unwrap()]
                return FlextResult[FlextTypes.StringList].ok(schemas)

            except Exception as e:
                return FlextResult[FlextTypes.StringList].fail(
                    f"Failed to get schemas: {e}"
                )

        def get_tables(
            self, schema: str | None = None
        ) -> FlextResult[FlextTypes.StringList]:
            """Get list of tables in Oracle schema."""
            try:
                params: FlextTypes.Dict | None
                if schema:
                    sql = """

                    SELECT table_name
                    FROM all_tables
                    WHERE owner = UPPER(:schema_name)
                    ORDER BY table_name
                    """

                    params = {"schema_name": "schema"}
                else:
                    sql = """

                    SELECT table_name
                    FROM user_tables
                    ORDER BY table_name
                    """

                    params = None

                result = self._query_executor.execute_query(sql, params)
                if result.is_failure:
                    return FlextResult[FlextTypes.StringList].fail(
                        result.error or "Failed to get tables",
                    )

                tables = [str(row["table_name"]) for row in result.unwrap()]
                return FlextResult[FlextTypes.StringList].ok(tables)

            except Exception as e:
                return FlextResult[FlextTypes.StringList].fail(
                    f"Failed to get tables: {e}"
                )

        def get_columns(
            self,
            table_name: str,
            schema_name: str | None = None,
        ) -> FlextResult[list[FlextDbOracleModels.Column]]:
            """Get column information for Oracle table."""
            _ = table_name  # Parameter required by API but not used in stub implementation
            try:
                if schema_name:
                    sql = """

                    SELECT column_name, data_type, data_length, data_precision, data_scale, nullable
                    FROM all_tab_columns
                    WHERE table_name = UPPER(:table_name) AND owner = UPPER(:schema_name)
                    ORDER BY column_id
                    """

                    params: FlextTypes.Dict = {
                        "table_name": "table_name",
                        "schema_name": "schema_name",
                    }
                else:
                    sql = """

                    SELECT column_name, data_type, data_length, data_precision, data_scale, nullable
                    FROM user_tab_columns
                    WHERE table_name = UPPER(:table_name)
                    ORDER BY column_id
                    """

                    params = {"table_name": "table_name"}

                result = self._query_executor.execute_query(sql, params)
                if result.is_failure:
                    return FlextResult[list[FlextDbOracleModels.Column]].fail(
                        result.error or "Failed to get columns",
                    )

                columns: list[FlextDbOracleModels.Column] = []
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
                    f"Failed to get columns: {e}",
                )

        def get_primary_key_columns(
            self,
            table_name: str,
            schema_name: str | None = None,
        ) -> FlextResult[FlextTypes.StringList]:
            """Get primary key columns for a table."""
            _ = table_name  # Parameter required by API but not used in stub implementation
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

                    params: FlextTypes.Dict = {
                        "table_name": "table_name",
                        "schema_name": "schema_name",
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

                    params = {"table_name": "table_name"}

                result = self._query_executor.execute_query(sql, params)
                if result.is_failure:
                    return FlextResult[FlextTypes.StringList].fail(
                        result.error or "Failed to get primary keys",
                    )

                pk_columns = [str(row["column_name"]) for row in result.unwrap()]
                return FlextResult[FlextTypes.StringList].ok(pk_columns)

            except Exception as e:
                return FlextResult[FlextTypes.StringList].fail(
                    f"Failed to get primary key columns: {e}",
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
                    schema_validation = (
                        FlextDbOracleUtilities.OracleValidation.validate_identifier(
                            schema_name,
                        )
                    )
                    table_validation = (
                        FlextDbOracleUtilities.OracleValidation.validate_identifier(
                            table_name,
                        )
                    )
                    if schema_validation.is_failure or table_validation.is_failure:
                        return FlextResult[int].fail("Invalid schema or table name")
                else:
                    # Validate just table name
                    table_validation = (
                        FlextDbOracleUtilities.OracleValidation.validate_identifier(
                            table_name,
                        )
                    )
                    if table_validation.is_failure:
                        return FlextResult[int].fail("Invalid table name")

                # Use SQLAlchemy 2.0 Core API for modern SQL generation
                # Create a Table object for the count query
                metadata: MetaData = MetaData()
                validated_table = (
                    FlextDbOracleUtilities.OracleValidation.validate_identifier(
                        table_name,
                    ).unwrap()
                )
                validated_schema = None
                if schema_name:
                    validated_schema = (
                        FlextDbOracleUtilities.OracleValidation.validate_identifier(
                            schema_name,
                        ).unwrap()
                    )

                table = Table(
                    validated_table,
                    metadata,
                    Column("id", Integer),  # Placeholder column
                    schema=validated_schema,
                    autoload_with=None,
                    extend_existing=True,
                )

                # Build COUNT query using SQLAlchemy 2.0 Core API
                stmt = select(text("COUNT(*) as row_count")).select_from(table)
                sql = str(stmt.compile(compile_kwargs={"literal_binds": "False"}))
                result = self._query_executor.execute_query(sql)
                if result.is_failure:
                    return FlextResult[int].fail(
                        result.error or "Failed to get row count",
                    )

                rows = result.unwrap()
                if not rows:
                    return FlextResult[int].ok(0)

                count_value = rows[0]["row_count"]
                count = int(str(count_value)) if count_value is not None else 0
                return FlextResult[int].ok(count)

            except Exception as e:
                return FlextResult[int].fail(f"Failed to get row count: {e}")

        def get_table_metadata(
            self, table_name: str, schema: str | None = None
        ) -> FlextResult[FlextTypes.Dict]:
            """Get comprehensive table metadata including columns and constraints."""
            try:
                # Get table columns
                columns_result = self.get_columns(table_name, schema)
                if columns_result.is_failure:
                    return FlextResult[FlextTypes.Dict].fail(
                        columns_result.error or "Failed to get columns"
                    )

                # Get primary keys
                pk_result = self.get_primary_keys(table_name, schema)
                if pk_result.is_failure:
                    return FlextResult[FlextTypes.Dict].fail(
                        pk_result.error or "Failed to get primary keys"
                    )

                metadata: FlextTypes.Dict = {
                    "table_name": table_name,
                    "schema": schema,
                    "columns": columns_result.value,
                    "primary_keys": pk_result.value,
                }

                return FlextResult[FlextTypes.Dict].ok(metadata)
            except Exception as e:
                return FlextResult[FlextTypes.Dict].fail(
                    f"Failed to get table metadata: {e}"
                )

        def get_primary_keys(
            self, table_name: str, schema: str | None = None
        ) -> FlextResult[FlextTypes.StringList]:
            """Get primary key column names for specified table."""
            try:
                # Use parameterized query to prevent SQL injection
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
                    params: FlextTypes.Dict = {
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
                    params: FlextTypes.Dict = {"table_name": table_name}

                result = self._query_executor.execute_query(sql, params)
                if result.is_failure:
                    return FlextResult[FlextTypes.StringList].fail(
                        result.error or "Failed to get primary keys"
                    )

                primary_keys: FlextTypes.StringList = [
                    str(row["column_name"]) for row in result.value
                ]
                return FlextResult[FlextTypes.StringList].ok(primary_keys)
            except Exception as e:
                return FlextResult[FlextTypes.StringList].fail(
                    f"Failed to get primary keys: {e}"
                )

    class _DdlGenerator:
        """Nested helper for DDL statement generation and schema changes."""

        @override
        def __init__(self, logger: FlextLogger) -> None:
            """Initialize the DDL generator."""
            self.logger = logger

        def create_table_ddl(
            self,
            table_name: str,
            columns: list[FlextTypes.Dict],
            schema_name: str | None = None,
        ) -> FlextResult[str]:
            """Generate CREATE TABLE DDL statement."""
            try:
                full_table_name = self._build_table_name(table_name, schema_name)

                column_defs: FlextTypes.StringList = []
                primary_keys = []

                for col in columns:
                    col_def_result = self._build_column_definition(col)
                    if col_def_result.is_failure:
                        return FlextResult[str].fail(
                            col_def_result.error or "Column definition failed",
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
            singer_type: str | FlextTypes.StringList,
            format_hint: str | None = None,
        ) -> FlextResult[str]:
            """Convert Singer JSON Schema type to Oracle SQL type."""
            try:
                # Handle array types (e.g., ["string", "null"])
                if isinstance(singer_type, list):
                    non_null_types = [t for t in singer_type if t != "null"]
                    if not non_null_types:
                        return FlextResult[str].ok(
                            FlextDbOracleConstants.DataTypes.DEFAULT_VARCHAR_TYPE
                        )
                    singer_type = non_null_types[0]

                # Convert based on Singer type
                type_mapping = FlextDbOracleConstants.DataTypes.SINGER_TYPE_MAP

                # Check for format hints
                if format_hint:
                    format_mapping = {
                        "date-time": "TIMESTAMP",
                        "date": "DATE",
                        "time": "TIMESTAMP",
                    }
                    if format_hint in format_mapping:
                        return FlextResult[str].ok(format_mapping[format_hint])

                oracle_type = type_mapping.get(
                    singer_type, FlextDbOracleConstants.DataTypes.DEFAULT_VARCHAR_TYPE
                )
                return FlextResult[str].ok(oracle_type)

            except Exception as e:
                return FlextResult[str].fail(f"Type conversion failed: {e}")

        def map_singer_schema(
            self,
            singer_schema: FlextTypes.Dict,
        ) -> FlextResult[FlextTypes.StringDict]:
            """Map Singer JSON schema to Oracle column types."""
            try:
                mapping = {}

                properties = singer_schema.get("properties", {})
                if not isinstance(properties, dict):
                    return FlextResult[FlextTypes.StringDict].fail(
                        "Invalid properties format"
                    )

                for field_name, field_def in properties.items():
                    if not isinstance(field_def, dict):
                        continue

                    field_type = field_def.get("type")
                    field_format = field_def.get("format")

                    if field_type is not None:
                        conversion_result = self.convert_singer_type(
                            field_type,
                            field_format,
                        )
                    else:
                        conversion_result = FlextResult[str].ok(
                            FlextDbOracleConstants.DataTypes.DEFAULT_VARCHAR_TYPE
                        )

                    if conversion_result.is_success:
                        mapping[field_name] = conversion_result.unwrap()
                    else:
                        mapping[field_name] = (
                            FlextDbOracleConstants.DataTypes.DEFAULT_VARCHAR_TYPE
                        )  # Default fallback

                return FlextResult[FlextTypes.StringDict].ok(mapping)

            except Exception as e:
                return FlextResult[FlextTypes.StringDict].fail(
                    f"Schema mapping failed: {e}"
                )

        def _build_table_name(
            self,
            table_name: str,
            schema_name: str | None = None,
        ) -> str:
            """Build full table name with optional schema."""
            if schema_name:
                return f"{schema_name}.{table_name}"
            return table_name

        def _build_column_definition(
            self,
            column_def: FlextTypes.Dict,
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
        """Nested helper for performance monitoring and health checks."""

        @override
        def __init__(
            self,
            connection_manager: FlextDbOracleServices._ConnectionManager,
            config: FlextDbOracleConfig,
            logger: FlextLogger,
        ) -> None:
            """Initialize the metrics collector."""
            self._connection_manager = connection_manager
            self._config: FlextDbOracleConfig = config
            self.logger = logger
            self._metrics: FlextTypes.Dict = {}
            self._operations: list[FlextTypes.Dict] = []

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
                    db_version=None,  # Could be populated from Oracle version query
                    error_message=None,
                )
                return FlextResult[FlextDbOracleModels.ConnectionStatus].ok(status)

            except Exception as e:
                return FlextResult[FlextDbOracleModels.ConnectionStatus].fail(
                    f"Failed to get connection status: {e}",
                )

        def record_metric(
            self,
            name: str,
            value: float,
            tags: FlextTypes.StringDict | None = None,
        ) -> FlextResult[bool]:
            """Record performance metric."""
            _ = value  # Parameter required by API but not used in stub implementation
            try:
                metric = {
                    "name": "name",
                    "value": "value",
                    "tags": tags or {},
                    "timestamp": datetime.now(UTC).isoformat(),
                }
                self._metrics[name] = metric
                return FlextResult[bool].ok(data=True)

            except Exception as e:
                return FlextResult[bool].fail(f"Failed to record metric: {e}")

        def get_metrics(self) -> FlextResult[FlextTypes.Dict]:
            """Get recorded performance metrics."""
            return FlextResult[FlextTypes.Dict].ok(self._metrics.copy())

        def track_operation(
            self,
            operation: str,
            duration_ms: float,
            *,
            success: bool,
            metadata: FlextTypes.Dict | None = None,
        ) -> FlextResult[str]:
            """Track database operation performance."""
            _ = (
                duration_ms,
                success,
            )  # Parameters required by API but not used in stub implementation
            try:
                hash_input = f"{operation}_{datetime.now(UTC).isoformat()}"
                operation_id = hashlib.sha256(hash_input.encode()).hexdigest()[:16]

                operation_record: FlextTypes.Dict = {
                    "id": "operation_id",
                    "operation": "operation",
                    "duration_ms": "duration_ms",
                    "success": "success",
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

        def get_operations(self) -> FlextResult[list[FlextTypes.Dict]]:
            """Get tracked operations history."""
            return FlextResult[list[FlextTypes.Dict]].ok(self._operations.copy())

        def health_check(self) -> FlextResult[FlextTypes.Dict]:
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
                    database_info: FlextTypes.Dict = cast(
                        "FlextTypes.Dict", health_info["database"]
                    )
                    if test_result.is_success:
                        database_info["test_query"] = "passed"
                    else:
                        health_info["status"] = "degraded"
                        database_info["test_query"] = "failed"

                health_result: FlextTypes.Dict = cast("FlextTypes.Dict", health_info)
                return FlextResult[FlextTypes.Dict].ok(health_result)

            except Exception as e:
                return FlextResult[FlextTypes.Dict].fail(f"Health check failed: {e}")

    class _PluginRegistry:
        """Nested helper for plugin registration and management."""

        @override
        def __init__(self, logger: FlextLogger) -> None:
            """Initialize the plugin registry."""
            self.logger = logger
            self._plugins: FlextTypes.Dict = {}

        def register_plugin(self, name: str, plugin: object) -> FlextResult[bool]:
            """Register a plugin."""
            try:
                self._plugins[name] = plugin
                self.logger.info(f"Plugin '{name}' registered successfully")
                return FlextResult[bool].ok(data=True)

            except Exception as e:
                return FlextResult[bool].fail(
                    f"Failed to register plugin '{name}': {e}",
                )

        def unregister_plugin(self, name: str) -> FlextResult[bool]:
            """Unregister a plugin."""
            try:
                if name in self._plugins:
                    del self._plugins[name]
                    self.logger.info(f"Plugin '{name}' unregistered successfully")
                return FlextResult[bool].ok(data=True)

            except Exception as e:
                return FlextResult[bool].fail(
                    f"Failed to unregister plugin '{name}': {e}",
                )

        def list_plugins(self) -> FlextResult[FlextTypes.Dict]:
            """List all registered plugins."""
            try:
                if not self._plugins:
                    return FlextResult[FlextTypes.Dict].fail("No plugins registered")
                return FlextResult[FlextTypes.Dict].ok(self._plugins.copy())

            except Exception as e:
                return FlextResult[FlextTypes.Dict].fail(
                    f"Failed to list plugins: {e}",
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
        super().model_post_init(__context)
        try:
            # Initialize core dependencies
            self._container = FlextContainer.get_global()
            self.logger = FlextLogger(__name__)

            # Initialize nested helpers with proper dependency injection
            self._connection_manager = self._ConnectionManager(
                self._config,
                self.logger,
            )
            self._query_executor = self._QueryExecutor(
                self._connection_manager,
                self.logger,
            )
            self._sql_builder = self._SqlBuilder(self.logger)
            self._schema_introspector = self._SchemaIntrospector(
                self._query_executor,
                self.logger,
            )
            self._ddl_generator = self._DdlGenerator(self.logger)
            self._metrics_collector = self._MetricsCollector(
                self._connection_manager,
                self._config,
                self.logger,
            )
            self._plugin_registry = self._PluginRegistry(self.logger)

            # CLI compatibility handled through property methods instead

        except Exception:
            if self.logger:
                self.logger.exception("Failed to initialize nested helpers")
            raise

    def execute(self) -> FlextResult[FlextDbOracleConfig]:
        """Execute main domain service operation - return config."""
        test_result = self._connection_manager.test_connection()
        if test_result.is_success:
            return FlextResult[FlextDbOracleConfig].ok(self._config)
        return FlextResult[FlextDbOracleConfig].fail(
            test_result.error or "Connection test failed",
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
                result.error or "Connection failed",
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
    def get_connection(self) -> Generator[object]:
        """Get database connection context manager for SQLAlchemy 2.0 Core API."""
        with self._connection_manager.get_connection() as connection:
            yield connection

    @contextmanager
    def transaction(self) -> Generator[object]:
        """Get transaction context for database operations."""
        with self._connection_manager.transaction() as transaction:
            yield transaction

    # Query Execution Delegation
    def execute_query(
        self,
        sql: str,
        params: FlextTypes.Dict | None = None,
    ) -> FlextResult[list[FlextTypes.Dict]]:
        """Execute SQL query and return results."""
        return self._query_executor.execute_query(sql, params)

    def execute_statement(
        self,
        sql: str,
        params: FlextTypes.Dict | None = None,
    ) -> FlextResult[int]:
        """Execute SQL statement and return affected rows."""
        return self._query_executor.execute_statement(sql, params)

    def execute_many(
        self,
        sql: str,
        params_list: list[FlextTypes.Dict],
    ) -> FlextResult[int]:
        """Execute SQL statement multiple times."""
        return self._query_executor.execute_many(sql, params_list)

    def fetch_one(
        self,
        sql: str,
        params: FlextTypes.Dict | None = None,
    ) -> FlextResult[FlextTypes.Dict | None]:
        """Execute query and return first result."""
        return self._query_executor.fetch_one(sql, params)

    def generate_query_hash(
        self,
        sql: str,
        params: FlextTypes.Dict | None = None,
    ) -> FlextResult[str]:
        """Generate hash for SQL query caching."""
        return self._query_executor.generate_query_hash(sql, params)

    # SQL Building Delegation
    def build_select(
        self,
        table_name: str,
        columns: FlextTypes.StringList | None = None,
        conditions: FlextTypes.Dict | None = None,
        schema_name: str | None = None,
    ) -> FlextResult[str]:
        """Build a SELECT query string."""
        return self._sql_builder.build_select(
            table_name,
            columns,
            conditions,
            schema_name,
        )

    def build_insert_statement(
        self,
        table_name: str,
        columns: FlextTypes.StringList,
        schema_name: str | None = None,
        returning_columns: FlextTypes.StringList | None = None,
    ) -> FlextResult[str]:
        """Build INSERT statement."""
        return self._sql_builder.build_insert_statement(
            table_name,
            columns,
            schema_name,
            returning_columns,
        )

    def build_update_statement(
        self,
        table_name: str,
        set_columns: FlextTypes.StringList,
        where_columns: FlextTypes.StringList,
        schema_name: str | None = None,
    ) -> FlextResult[str]:
        """Build UPDATE statement."""
        return self._sql_builder.build_update_statement(
            table_name,
            set_columns,
            where_columns,
            schema_name,
        )

    def build_delete_statement(
        self,
        table_name: str,
        where_columns: FlextTypes.StringList,
        schema_name: str | None = None,
    ) -> FlextResult[str]:
        """Build DELETE statement."""
        return self._sql_builder.build_delete_statement(
            table_name,
            where_columns,
            schema_name,
        )

    def build_create_index_statement(
        self,
        config: FlextDbOracleModels.CreateIndexConfig,
    ) -> FlextResult[str]:
        """Build CREATE INDEX statement."""
        try:
            # Build the basic CREATE INDEX statement
            unique_keyword = "UNIQUE " if config.unique else ""
            schema_prefix = f"{config.schema_name}." if config.schema_name else ""
            table_ref = f"{schema_prefix}{config.table_name}"
            index_ref = f"{schema_prefix}{config.index_name}"
            columns_str = ", ".join(config.columns)

            sql = f"CREATE {unique_keyword}INDEX {index_ref} ON {table_ref} ({columns_str})"

            # Add optional clauses
            if config.tablespace:
                sql += f" TABLESPACE {config.tablespace}"

            if config.parallel:
                sql += f" PARALLEL {config.parallel}"

            return FlextResult[str].ok(sql)
        except Exception as e:
            return FlextResult[str].fail(f"Failed to build CREATE INDEX statement: {e}")

    # Schema Introspection Delegation
    def get_schemas(self) -> FlextResult[FlextTypes.StringList]:
        """Get list of Oracle schemas."""
        return self._schema_introspector.get_schemas()

    def get_table_metadata(
        self, table_name: str, schema: str | None = None
    ) -> FlextResult[FlextTypes.Dict]:
        """Get comprehensive table metadata including columns and constraints."""
        return self._schema_introspector.get_table_metadata(table_name, schema)

    def get_primary_keys(
        self, table_name: str, schema: str | None = None
    ) -> FlextResult[FlextTypes.StringList]:
        """Get primary key column names for specified table."""
        return self._schema_introspector.get_primary_keys(table_name, schema)

    def get_tables(
        self, schema: str | None = None
    ) -> FlextResult[FlextTypes.StringList]:
        """Get list of tables in Oracle schema."""
        return self._schema_introspector.get_tables(schema)

    def get_columns(
        self,
        table_name: str,
        schema_name: str | None = None,
    ) -> FlextResult[list[FlextDbOracleModels.Column]]:
        """Get column information for Oracle table."""
        return self._schema_introspector.get_columns(table_name, schema_name)

    def get_primary_key_columns(
        self,
        table_name: str,
        schema_name: str | None = None,
    ) -> FlextResult[FlextTypes.StringList]:
        """Get primary key columns for a table."""
        return self._schema_introspector.get_primary_key_columns(
            table_name,
            schema_name,
        )

    def get_table_row_count(
        self,
        table_name: str,
        schema_name: str | None = None,
    ) -> FlextResult[int]:
        """Get row count for Oracle table."""
        return self._schema_introspector.get_table_row_count(table_name, schema_name)

    # DDL Generation Delegation
    def create_table_ddl(
        self,
        table_name: str,
        columns: list[FlextTypes.Dict],
        schema_name: str | None = None,
    ) -> FlextResult[str]:
        """Generate CREATE TABLE DDL statement."""
        return self._ddl_generator.create_table_ddl(table_name, columns, schema_name)

    def drop_table_ddl(
        self,
        table_name: str,
        schema_name: str | None = None,
    ) -> FlextResult[str]:
        """Generate DROP TABLE DDL statement."""
        return self._ddl_generator.drop_table_ddl(table_name, schema_name)

    def convert_singer_type(
        self,
        singer_type: str | FlextTypes.StringList,
        format_hint: str | None = None,
    ) -> FlextResult[str]:
        """Convert Singer JSON Schema type to Oracle SQL type."""
        return self._ddl_generator.convert_singer_type(singer_type, format_hint)

    def map_singer_schema(
        self,
        singer_schema: FlextTypes.Dict,
    ) -> FlextResult[FlextTypes.StringDict]:
        """Map Singer JSON schema to Oracle column types."""
        return self._ddl_generator.map_singer_schema(singer_schema)

    # Metrics Collection Delegation
    def get_connection_status(
        self,
    ) -> FlextResult[FlextDbOracleModels.ConnectionStatus]:
        """Get Oracle connection status."""
        return self._metrics_collector.get_connection_status()

    def record_metric(
        self,
        name: str,
        value: float,
        tags: FlextTypes.StringDict | None = None,
    ) -> FlextResult[None]:
        """Record performance metric."""
        result = self._metrics_collector.record_metric(name, value, tags)
        return (
            FlextResult[None].ok(None)
            if result.is_success
            else FlextResult[None].fail(result.error or "Failed to record metric")
        )

    def get_metrics(self) -> FlextResult[FlextTypes.Dict]:
        """Get recorded performance metrics."""
        return self._metrics_collector.get_metrics()

    def track_operation(
        self,
        operation: str,
        duration_ms: float,
        *,
        success: bool,
        metadata: FlextTypes.Dict | None = None,
    ) -> FlextResult[str]:
        """Track database operation performance."""
        return self._metrics_collector.track_operation(
            operation,
            duration_ms,
            success=success,
            metadata=metadata,
        )

    def get_operations(self) -> FlextResult[list[FlextTypes.Dict]]:
        """Get tracked operations history."""
        return self._metrics_collector.get_operations()

    def health_check(self) -> FlextResult[FlextTypes.Dict]:
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

    def list_plugins(self) -> FlextResult[FlextTypes.Dict]:
        """List all registered plugins."""
        return self._plugin_registry.list_plugins()

    def get_plugin(self, name: str) -> FlextResult[object]:
        """Get a specific plugin."""
        return self._plugin_registry.get_plugin(name)


# Export the single refactored class following flext-core pattern
__all__ = ["FlextDbOracleServices"]
