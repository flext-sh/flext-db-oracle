"""FLEXT DB Oracle Connection Management.

This module provides enterprise-grade Oracle database connection management using
SQLAlchemy 2 and FLEXT Core patterns. It implements Clean Architecture principles
with comprehensive connection pooling, transaction management, and error handling
for Oracle database operations.

Key Components:
    - FlextDbOracleConnection: Main connection manager with SQLAlchemy 2 integration
    - Connection pool management with configurable sizing and lifecycle
    - Transaction context managers for safe database operations
    - Schema introspection and metadata operations
    - Singer schema mapping for data pipeline integration
    - DDL generation and execution with Oracle optimizations

Architecture:
    This module implements the Infrastructure layer's database connectivity concern,
    providing the foundation for all Oracle database operations within the FLEXT
    ecosystem. It follows Clean Architecture dependency inversion principles by
    abstracting database operations behind type-safe FlextResult patterns.

Example:
    Basic connection and query execution:

    >>> from flext_db_oracle import FlextDbOracleConfig, FlextDbOracleConnection
    >>> config = FlextDbOracleConfig.from_env().value
    >>> connection = FlextDbOracleConnection(config)
    >>> connect_result = connection.connect()
    >>> if connect_result.success:
    ...     result = connection.execute(
    ...         "SELECT * FROM employees WHERE dept_id = :dept", {"dept": 10}
    ...     )
    ...     if result.success:
    ...         for row in result.value:
    ...             print(row)

Integration:
    - Built on SQLAlchemy 2.x for modern async/sync database operations
    - Integrates with flext-core FlextResult patterns for error handling
    - Supports flext-observability for performance monitoring
    - Compatible with Singer ecosystem for data pipeline operations
    - Provides foundation for flext-tap-oracle and flext-target-oracle

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from collections.abc import Generator
from contextlib import contextmanager
from typing import TYPE_CHECKING, TypeVar, cast
from urllib.parse import quote_plus

from flext_core import FlextResult, get_logger
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session, sessionmaker

from .config_types import CreateIndexStatementConfig, MergeStatementConfig

from .constants import (
    ORACLE_DATE_TYPE,
    ORACLE_DEFAULT_VARCHAR_TYPE,
    ORACLE_TEST_QUERY,
    ORACLE_TIMESTAMP_TYPE,
    SINGER_TO_ORACLE_TYPE_MAP,
)

# Oracle column information constants
ORACLE_COLUMN_INFO_FIELDS = 7  # Expected number of fields in Oracle column info query

if TYPE_CHECKING:
    from collections.abc import Generator, Sequence

    from sqlalchemy.engine import Engine

    from .config import FlextDbOracleConfig

T = TypeVar("T")

logger = get_logger(__name__)


class FlextDbOracleConnection:
    """Oracle database connection using SQLAlchemy 2 and flext-core patterns.

    Provides unified interface for Oracle database operations with proper
    connection management, transactions, and error handling.
    """

    def __init__(self, config: FlextDbOracleConfig) -> None:
        """Initialize connection with configuration."""
        self.config = config

        # SQLAlchemy components
        self._engine: Engine | None = None
        self._session_factory: sessionmaker[Session] | None = None

        self._logger = get_logger(f"{__name__}.{self.__class__.__name__}")

    def connect(self) -> FlextResult[bool]:
        """Connect to Oracle database using SQLAlchemy 2."""
        try:
            # Validate configuration
            config_validation = self.config.validate_domain_rules()
            if config_validation.is_failure:
                return FlextResult.fail(
                    f"Configuration invalid: {config_validation.error}",
                )

            # Build connection URL
            url_result = self._build_connection_url()
            if url_result.is_failure or not url_result.data:
                error_msg = url_result.error or "Connection URL is empty"
                return FlextResult.fail(error_msg)

            # Create SQLAlchemy engine with optimized settings
            self._engine = create_engine(
                url_result.data,
                echo=False,
                pool_pre_ping=True,
                pool_recycle=3600,
                pool_size=self.config.pool_min,
                max_overflow=self.config.pool_max - self.config.pool_min,
            )

            self._session_factory = sessionmaker(bind=self._engine)

            # Test connection
            with self._engine.connect() as conn:
                conn.execute(text(ORACLE_TEST_QUERY))

            self._logger.info("Connected using SQLAlchemy 2")
            return FlextResult.ok(data=True)

        except (SQLAlchemyError, OSError, ValueError, AttributeError) as e:
            return self._handle_database_error_with_logging("Failed to connect", e)

    def disconnect(self) -> FlextResult[bool]:
        """Disconnect from database."""
        try:
            if self._engine:
                self._engine.dispose()
                self._engine = None
                self._session_factory = None
                self._logger.info("Disconnected from Oracle database")
            return FlextResult.ok(data=True)
        except (SQLAlchemyError, OSError, ValueError, AttributeError) as e:
            return self._handle_database_error_simple("Disconnect failed", e)

    def is_connected(self) -> bool:
        """Check if connected to database."""
        return self._engine is not None

    def _ensure_connected(self) -> FlextResult[None]:
        """Ensure database is connected and engine is initialized.

        Enterprise-safe connection validation with detailed error reporting.
        """
        if not self.is_connected():
            return FlextResult.fail("Not connected to database")

        if not self._engine:
            return FlextResult.fail("Database engine not initialized")

        return FlextResult.ok(None)

    def _handle_database_error_with_logging(
        self,
        operation: str,
        exception: Exception,
    ) -> FlextResult[T]:
        """Handle database errors with logging - DRY pattern for error handling.

        Args:
            operation: Description of the operation that failed
            exception: The exception that occurred

        Returns:
            FlextResult with failure containing formatted error message

        """
        error_msg: str = f"{operation}: {exception}"
        self._logger.error(error_msg)
        return FlextResult.fail(error_msg)

    def _handle_database_error_simple(
        self,
        operation: str,
        exception: Exception,
    ) -> FlextResult[T]:
        """Handle database errors without logging - DRY pattern for simple error handling.

        Args:
            operation: Description of the operation that failed
            exception: The exception that occurred

        Returns:
            FlextResult with failure containing formatted error message

        """
        return FlextResult.fail(f"{operation}: {exception}")

    def execute(
        self,
        sql: str,
        parameters: dict[str, object] | None = None,
    ) -> FlextResult[list[object]]:
        """Execute SQL statement using SQLAlchemy 2."""
        connection_check = self._ensure_connected()
        if connection_check.is_failure:
            return FlextResult.fail(connection_check.error or "Connection failed")

        try:
            if self._engine is None:  # Additional safety check beyond _ensure_connected()
                return FlextResult.fail("Database engine is None after connection check")
            with self._engine.connect() as conn:
                result = conn.execute(text(sql), parameters or {})

                # Handle different statement types
                if sql.strip().upper().startswith(("SELECT", "WITH")):
                    rows = result.fetchall()
                    return FlextResult.ok(list(rows))
                conn.commit()
                return FlextResult.ok([result.rowcount])

        except (SQLAlchemyError, OSError, ValueError, AttributeError) as e:
            return self._handle_database_error_with_logging("SQL execution failed", e)

    def execute_many(
        self,
        sql: str,
        parameters_list: list[dict[str, object]],
    ) -> FlextResult[int]:
        """Execute SQL with multiple parameter sets."""
        connection_check = self._ensure_connected()
        if connection_check.is_failure:
            return FlextResult.fail(connection_check.error or "Connection failed")

        try:
            if self._engine is None:  # Additional safety check beyond _ensure_connected()
                return FlextResult.fail("Database engine is None after connection check")
            with self._engine.connect() as conn:
                result = conn.execute(text(sql), parameters_list)
                conn.commit()
                return FlextResult.ok(result.rowcount)

        except (SQLAlchemyError, OSError, ValueError, AttributeError) as e:
            return self._handle_database_error_with_logging("Batch execution failed", e)

    def fetch_one(
        self,
        sql: str,
        parameters: dict[str, object] | None = None,
    ) -> FlextResult[object]:
        """Fetch single row."""
        connection_check = self._ensure_connected()
        if connection_check.is_failure:
            return FlextResult.fail(connection_check.error or "Connection failed")

        try:
            if self._engine is None:  # Additional safety check beyond _ensure_connected()
                return FlextResult.fail("Database engine is None after connection check")
            with self._engine.connect() as conn:
                result = conn.execute(text(sql), parameters or {})
                return FlextResult.ok(result.fetchone())

        except (SQLAlchemyError, OSError, ValueError, AttributeError) as e:
            return self._handle_database_error_with_logging("Fetch one failed", e)

    @contextmanager
    def session(self) -> Generator[Session]:
        """Get SQLAlchemy session with automatic transaction management."""
        if not self._session_factory:
            msg = "Not connected to database"
            raise ValueError(msg)

        session = self._session_factory()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    @contextmanager
    def transaction(self) -> Generator[object]:
        """Context manager for database transactions."""
        connection_check = self._ensure_connected()
        if connection_check.is_failure:
            raise ValueError(connection_check.error or "Connection failed")

        if self._engine is None:  # Additional safety check beyond _ensure_connected()
            msg = "Database engine is None after connection check"
            raise ValueError(msg)
        with self._engine.connect() as conn:
            trans = conn.begin()
            try:
                yield conn
                trans.commit()
            except Exception:
                trans.rollback()
                raise

    def close(self) -> FlextResult[None]:
        """Close database connection."""
        try:
            if self._engine:
                self._engine.dispose()
                self._engine = None
                self._session_factory = None
                self._logger.info("Database connection closed")
            return FlextResult.ok(None)
        except Exception as e:
            # Clean up references even if disposal fails
            self._engine = None
            self._session_factory = None
            error_msg: str = f"Failed to close connection: {e}"
            self._logger.exception(error_msg)
            return FlextResult.fail(error_msg)

    def execute_query(
        self,
        sql: str,
        parameters: dict[str, object] | None = None,
    ) -> FlextResult[list[object]]:
        """Execute query and return result - alias for execute method."""
        return self.execute(sql, parameters)

    def test_connection(self) -> FlextResult[bool]:
        """Test database connection."""
        connection_check = self._ensure_connected()
        if connection_check.is_failure:
            return FlextResult.fail(connection_check.error or "Connection failed")

        try:
            result = self.execute(ORACLE_TEST_QUERY)
            return FlextResult.ok(result.success)
        except (SQLAlchemyError, OSError, ValueError, AttributeError, Exception) as e:
            return self._handle_database_error_simple("Connection test failed", e)

    def _build_table_names_query(
        self,
        schema_name: str | None = None,
    ) -> tuple[str, dict[str, object]]:
        """Build table names query with parameters - DRY pattern for table queries."""
        if schema_name:
            sql = "SELECT table_name FROM all_tables WHERE owner = UPPER(:schema_name) ORDER BY table_name"
            params: dict[str, object] = {"schema_name": schema_name}
        else:
            sql = "SELECT table_name FROM user_tables ORDER BY table_name"
            params = {}
        return sql, params

    def get_table_names(self, schema_name: str | None = None) -> FlextResult[list[str]]:
        """Get table names from schema."""
        try:
            sql, params = self._build_table_names_query(schema_name)

            result = self.execute(sql, params)
            if result.is_failure:
                return FlextResult.fail(result.error or "Failed to get table names")

            if not result.data:
                return FlextResult.ok([])

            # MYPY FIX: Safe type conversion for table names
            table_names: list[str] = [
                str(row[0])
                for row in result.data
                if hasattr(row, "__getitem__")
                and hasattr(row, "__len__")
                and len(row) > 0
            ]

            return FlextResult.ok(table_names)
        except (SQLAlchemyError, OSError, ValueError, AttributeError, Exception) as e:
            return self._handle_database_error_simple("Error retrieving table names", e)

    def get_schemas(self) -> FlextResult[list[str]]:
        """Get available schema names."""
        sql = "SELECT username FROM all_users ORDER BY username"

        result = self.execute(sql)
        if result.is_failure:
            return FlextResult.fail(result.error or "Failed to get schemas")

        if not result.data:
            return FlextResult.ok([])

        # MYPY FIX: Safe type conversion for schema names
        # SQLAlchemy 2 returns Row objects, not tuples, so check for indexable objects
        schema_names: list[str] = [
            str(row[0])
            for row in result.data
            if hasattr(row, "__getitem__") and hasattr(row, "__len__") and len(row) > 0
        ]

        return FlextResult.ok(schema_names)

    def get_current_schema(self) -> FlextResult[str]:
        """Get current schema name."""
        sql = "SELECT USER FROM DUAL"

        result = self.execute(sql)
        if result.is_failure:
            return FlextResult.fail(f"Failed to get current schema: {result.error}")

        if not result.data or len(result.data) == 0:
            return FlextResult.fail("No current schema returned")

        # Get first row, first column - SQLAlchemy Row objects are indexable
        current_schema = (
            str(result.data[0][0])
            if hasattr(result.data[0], "__getitem__")
            else str(result.data[0])
        )
        return FlextResult.ok(current_schema)

    def _build_column_info_query(
        self,
        table_name: str,
        schema_name: str | None = None,
    ) -> tuple[str, dict[str, object]]:
        """Build column info query with parameters - DRY pattern for schema queries."""
        base_sql = """
            SELECT column_name, data_type, nullable, data_length, data_precision, data_scale, column_id
            FROM {table_view}
            WHERE {where_clause}
            ORDER BY column_id
        """

        if schema_name:
            table_view = "all_tab_columns"
            where_clause = (
                "owner = UPPER(:schema_name) AND table_name = UPPER(:table_name)"
            )
            params: dict[str, object] = {
                "schema_name": schema_name,
                "table_name": table_name,
            }
        else:
            table_view = "user_tab_columns"
            where_clause = "table_name = UPPER(:table_name)"
            params = {"table_name": table_name}

        sql = base_sql.format(table_view=table_view, where_clause=where_clause)
        return sql, params

    def _convert_column_row_to_dict(self, row: Sequence[object]) -> dict[str, object]:
        """Convert Oracle column row to dictionary - Single Responsibility."""
        return {
            "column_name": str(row[0]),
            "data_type": str(row[1]),
            "nullable": str(row[2]) == "Y",
            "data_length": row[3],
            "data_precision": row[4],
            "data_scale": row[5],
            "column_id": row[6],
        }

    def get_column_info(
        self,
        table_name: str,
        schema_name: str | None = None,
    ) -> FlextResult[list[dict[str, object]]]:
        """Get column information for table."""
        sql, params = self._build_column_info_query(table_name, schema_name)

        result = self.execute(sql, params)
        if result.is_failure:
            return FlextResult.fail(result.error or "Failed to get column info")

        # MYPY FIX: Safe type conversion for column information
        columns: list[dict[str, object]] = [
            self._convert_column_row_to_dict(cast("Sequence[object]", row))
            for row in result.data or []
            if hasattr(row, "__getitem__")
            and hasattr(row, "__len__")
            and len(row) >= ORACLE_COLUMN_INFO_FIELDS
        ]

        return FlextResult.ok(columns)

    def _build_primary_key_query(
        self,
        table_name: str,
        schema_name: str | None = None,
    ) -> tuple[str, dict[str, object]]:
        """Build primary key query with parameters - DRY pattern for constraint queries."""
        base_sql = """
            SELECT column_name
            FROM {cons_columns_view} c
            JOIN {constraints_view} ct ON c.constraint_name = ct.constraint_name{owner_join}
            WHERE ct.constraint_type = 'P'
                AND {where_clause}
            ORDER BY c.position
        """

        if schema_name:
            cons_columns_view = "all_cons_columns"
            constraints_view = "all_constraints"
            owner_join = " AND c.owner = ct.owner"
            where_clause = (
                "ct.owner = UPPER(:schema_name) AND ct.table_name = UPPER(:table_name)"
            )
            params: dict[str, object] = {
                "schema_name": schema_name,
                "table_name": table_name,
            }
        else:
            cons_columns_view = "user_cons_columns"
            constraints_view = "user_constraints"
            owner_join = ""
            where_clause = "ct.table_name = UPPER(:table_name)"
            params = {"table_name": table_name}

        sql = base_sql.format(
            cons_columns_view=cons_columns_view,
            constraints_view=constraints_view,
            owner_join=owner_join,
            where_clause=where_clause,
        )
        return sql, params

    def get_primary_key_columns(
        self,
        table_name: str,
        schema_name: str | None = None,
    ) -> FlextResult[list[str]]:
        """Get primary key columns for table (consolidated from services)."""
        sql, params = self._build_primary_key_query(table_name, schema_name)

        result = self.execute(sql, params)
        if result.is_failure:
            return FlextResult.fail(result.error or "Failed to get primary key columns")

        if not result.data:
            return FlextResult.ok([])

        # MYPY FIX: Safe type conversion for primary key columns
        pk_columns: list[str] = [
            str(row[0])
            for row in result.data
            if hasattr(row, "__getitem__") and hasattr(row, "__len__") and len(row) > 0
        ]

        return FlextResult.ok(pk_columns)

    def get_table_metadata(
        self,
        table_name: str,
        schema_name: str | None = None,
    ) -> FlextResult[dict[str, object]]:
        """Get complete table metadata (consolidated from services)."""
        # Get columns
        columns_result = self.get_column_info(table_name, schema_name)
        if columns_result.is_failure:
            return FlextResult.fail(f"Failed to get columns: {columns_result.error}")

        # Get primary keys
        pk_result = self.get_primary_key_columns(table_name, schema_name)
        if pk_result.is_failure:
            return FlextResult.fail(f"Failed to get primary keys: {pk_result.error}")

        metadata: dict[str, object] = {
            "table_name": table_name,
            "schema_name": schema_name,
            "columns": columns_result.data,
            "primary_keys": pk_result.data,
        }

        return FlextResult.ok(metadata)

    def _build_select_base(
        self,
        table_name: str,
        columns: list[str] | None = None,
        schema_name: str | None = None,
    ) -> tuple[str, str]:
        """Build base SELECT query parts - DRY pattern for select methods."""
        # Build column list - safe since it's internal column names
        column_list = ", ".join(columns) if columns else "*"

        # Build table name using existing helper
        full_table_name = self._build_table_name(table_name, schema_name)

        return column_list, full_table_name

    def build_select(
        self,
        table_name: str,
        columns: list[str] | None = None,
        conditions: dict[str, object] | None = None,
        schema_name: str | None = None,
    ) -> FlextResult[str]:
        """Build SELECT query - BACKWARD COMPATIBILITY maintained.

        WARNING: For conditions with user input, use execute() with parameters instead.
        This method is kept for backward compatibility with existing tests.
        """
        try:
            column_list, full_table_name = self._build_select_base(
                table_name,
                columns,
                schema_name,
            )

            # Build WHERE clause - SECURITY: Only safe for trusted internal values
            where_clause = ""
            if conditions:
                where_conditions = []
                for key, value in conditions.items():
                    # NOTE: This is only safe for internal/trusted values
                    # For user input, use execute() with parameters instead
                    if isinstance(value, str):
                        # Basic escaping for strings - not full protection
                        escaped_value = value.replace("'", "''")
                        where_conditions.append(f"{key} = '{escaped_value}'")
                    elif isinstance(value, (int, float)):
                        where_conditions.append(f"{key} = {value}")
                    else:
                        where_conditions.append(f"{key} = '{value!s}'")
                where_clause = " WHERE " + " AND ".join(where_conditions)

            # Build SQL - safe for internal use only (basic escaping applied)
            sql = f"SELECT {column_list} FROM {full_table_name}{where_clause}"  # nosec # noqa: S608
            return FlextResult.ok(sql)

        except (ValueError, TypeError, AttributeError) as e:
            return FlextResult.fail(f"Query building failed: {e}")

    def build_select_safe(
        self,
        table_name: str,
        columns: list[str] | None = None,
        conditions: dict[str, object] | None = None,
        schema_name: str | None = None,
    ) -> FlextResult[tuple[str, dict[str, object]]]:
        """Build SELECT query with parameterized conditions (SECURE version)."""
        try:
            column_list, full_table_name = self._build_select_base(
                table_name,
                columns,
                schema_name,
            )

            # Build WHERE clause with parameters (SECURITY: No SQL injection)
            where_clause = ""
            params: dict[str, object] = {}
            if conditions:
                where_conditions = []
                for key, value in conditions.items():
                    # Use parameterized queries to prevent SQL injection
                    param_name = f"param_{key}"
                    where_conditions.append(f"{key} = :{param_name}")
                    params[param_name] = value
                where_clause = " WHERE " + " AND ".join(where_conditions)

            # Build safe SQL with parameterized conditions (fully secure)
            sql = f"SELECT {column_list} FROM {full_table_name}{where_clause}"  # nosec # noqa: S608
            return FlextResult.ok((sql, params))

        except (ValueError, TypeError, AttributeError) as e:
            return FlextResult.fail(f"Query building failed: {e}")

    def _build_table_name(self, table_name: str, schema_name: str | None = None) -> str:
        """Build full table name with optional schema - DRY pattern."""
        if schema_name:
            return f"{schema_name}.{table_name}"
        return table_name

    def _build_column_definition(self, col: dict[str, object]) -> FlextResult[str]:
        """Build single column definition - Single Responsibility pattern."""
        # Support both 'type' and 'data_type' keys for backward compatibility
        data_type = col.get("data_type") or col.get("type")
        if not data_type:
            return FlextResult.fail("Column must have 'type' or 'data_type' specified")

        col_def = f"{col['name']} {data_type}"
        if not col.get("nullable", True):
            col_def += " NOT NULL"
        if col.get("default_value"):
            col_def += f" DEFAULT {col['default_value']}"
        return FlextResult.ok(col_def)

    def _collect_primary_key_columns(
        self,
        columns: list[dict[str, object]],
    ) -> list[str]:
        """Collect primary key columns from column definitions - Single Responsibility."""
        return [str(col["name"]) for col in columns if col.get("primary_key", False)]

    def create_table_ddl(
        self,
        table_name: str,
        columns: list[dict[str, object]],
        schema_name: str | None = None,
    ) -> FlextResult[str]:
        """Generate CREATE TABLE DDL (consolidated from services)."""
        try:
            full_table_name = self._build_table_name(table_name, schema_name)
            column_defs: list[str] = []

            # Build column definitions
            for col in columns:
                col_def_result = self._build_column_definition(col)
                if col_def_result.is_failure:
                    return col_def_result
                # col_def_result.data is guaranteed to be str from FlextResult.ok(col_def)
                column_defs.append(col_def_result.data or "")

            # Add PRIMARY KEY constraint if any columns are marked as primary key
            primary_key_columns = self._collect_primary_key_columns(columns)
            if primary_key_columns:
                pk_constraint = f"CONSTRAINT PK_{table_name} PRIMARY KEY ({', '.join(primary_key_columns)})"
                column_defs.append(pk_constraint)

            ddl = f"CREATE TABLE {full_table_name} (\n  {',\n  '.join(column_defs)}\n)"
            return FlextResult.ok(ddl)

        except (
            SQLAlchemyError,
            OSError,
            ValueError,
            AttributeError,
            TypeError,
            KeyError,
        ) as e:
            return self._handle_database_error_simple("DDL generation failed", e)

    def drop_table_ddl(
        self,
        table_name: str,
        schema_name: str | None = None,
    ) -> FlextResult[str]:
        """Generate DROP TABLE DDL (consolidated from services)."""
        try:
            full_table_name = self._build_table_name(table_name, schema_name)
            ddl = f"DROP TABLE {full_table_name}"
            return FlextResult.ok(ddl)

        except (SQLAlchemyError, OSError, ValueError, AttributeError) as e:
            return self._handle_database_error_simple("DROP DDL generation failed", e)

    def execute_ddl(self, ddl: str) -> FlextResult[bool]:
        """Execute DDL statement (consolidated from services)."""
        try:
            result = self.execute(ddl)
            if result.success:
                return FlextResult.ok(data=True)
            return FlextResult.fail(result.error or "DDL execution failed")

        except (SQLAlchemyError, OSError, ValueError, AttributeError) as e:
            return self._handle_database_error_simple("DDL execution failed", e)

    def convert_singer_type(
        self,
        singer_type: str | list[str],
        format_hint: str | None = None,
    ) -> FlextResult[str]:
        """Convert Singer type to Oracle type (consolidated from services)."""
        try:
            # Handle array types
            if isinstance(singer_type, list):
                if "null" in singer_type:
                    # Remove null and get actual type
                    actual_types = [t for t in singer_type if t != "null"]
                    singer_type = actual_types[0] if actual_types else "string"
                else:
                    singer_type = singer_type[0]

            # Use centralized Singer to Oracle type mapping
            type_mapping = SINGER_TO_ORACLE_TYPE_MAP

            # Handle date/time formats
            if singer_type == "string" and format_hint:
                format_lower = format_hint.lower()
                if "date-time" in format_lower or "datetime" in format_lower:
                    return FlextResult.ok(ORACLE_TIMESTAMP_TYPE)
                if "time" in format_lower:
                    return FlextResult.ok(ORACLE_TIMESTAMP_TYPE)
                if "date" in format_lower:
                    return FlextResult.ok(ORACLE_DATE_TYPE)

            oracle_type = type_mapping.get(singer_type, ORACLE_DEFAULT_VARCHAR_TYPE)
            return FlextResult.ok(oracle_type)

        except (SQLAlchemyError, OSError, ValueError, AttributeError) as e:
            return self._handle_database_error_simple("Type conversion failed", e)

    def _validate_singer_properties(
        self,
        singer_schema: dict[str, object],
    ) -> FlextResult[dict[str, object]]:
        """Validate Singer schema properties - Single Responsibility."""
        properties = singer_schema.get("properties", {})
        if not isinstance(properties, dict):
            return FlextResult.fail("Schema properties must be a dictionary")
        return FlextResult.ok(properties)

    def _map_single_field(
        self,
        field_name: str,
        field_def: dict[str, object],
    ) -> FlextResult[tuple[str, str]]:
        """Map single Singer field to Oracle column - Single Responsibility."""
        field_type_obj = field_def.get("type", "string")
        format_hint_obj = field_def.get("format")

        # Safe casting for Singer field types
        if isinstance(field_type_obj, (str, list)):
            field_type = field_type_obj
        else:
            field_type = "string"  # Default fallback

        # Safe casting for format hint
        if isinstance(format_hint_obj, str) or format_hint_obj is None:
            format_hint = format_hint_obj
        else:
            format_hint = None  # Default fallback

        type_result = self.convert_singer_type(field_type, format_hint)
        if type_result.is_failure:
            return FlextResult.fail(type_result.error or "Type conversion failed")

        oracle_type = type_result.data or "VARCHAR2(4000)"
        return FlextResult.ok((field_name, oracle_type))

    def map_singer_schema(
        self,
        singer_schema: dict[str, object],
    ) -> FlextResult[dict[str, str]]:
        """Map Singer schema to Oracle column definitions (consolidated from services)."""
        try:
            # Validate properties
            properties_result = self._validate_singer_properties(singer_schema)
            if properties_result.is_failure:
                # Convert FlextResult[dict[str, object]] to FlextResult[dict[str, str]]
                return FlextResult.fail(
                    properties_result.error or "Schema validation failed",
                )

            properties = properties_result.data
            if not properties:
                return FlextResult.ok({})

            oracle_columns: dict[str, str] = {}

            # Process each field
            for field_name, field_def in properties.items():
                if not isinstance(field_def, dict):
                    continue  # Skip invalid field definitions

                field_result = self._map_single_field(field_name, field_def)
                if field_result.is_failure:
                    # Convert FlextResult[tuple[str, str]] to FlextResult[dict[str, str]]
                    return FlextResult.fail(
                        field_result.error or "Field mapping failed",
                    )

                field_data = field_result.data
                if field_data:  # field_data is tuple[str, str]
                    name, oracle_type = field_data
                    oracle_columns[name] = oracle_type

            return FlextResult.ok(oracle_columns)

        except (SQLAlchemyError, OSError, ValueError, AttributeError) as e:
            return self._handle_database_error_simple("Schema mapping failed", e)

    def _build_connection_url(self) -> FlextResult[str]:
        """Build Oracle connection URL for SQLAlchemy."""
        try:
            username = quote_plus(self.config.username)
            password = quote_plus(self.config.password.get_secret_value())
            host = self.config.host
            port = self.config.port

            if self.config.service_name:
                # Use service name
                url = f"oracle+oracledb://{username}:{password}@{host}:{port}/?service_name={self.config.service_name}"
            elif self.config.sid:
                # Use SID
                url = f"oracle+oracledb://{username}:{password}@{host}:{port}/{self.config.sid}"
            else:
                return FlextResult.fail("Must provide either service_name or sid")

            return FlextResult.ok(url)

        except (SQLAlchemyError, OSError, ValueError, AttributeError) as e:
            return self._handle_database_error_simple("URL building failed", e)

    # =============================================================================
    # DML Operations (INSERT, UPDATE, DELETE, MERGE)
    # =============================================================================

    def build_insert_statement(
        self,
        table_name: str,
        columns: list[str],
        schema_name: str | None = None,
        returning_columns: list[str] | None = None,
        hints: list[str] | None = None,
    ) -> FlextResult[str]:
        """Build INSERT statement with Oracle-specific features.

        Args:
            table_name: Target table name
            columns: Column names to insert
            schema_name: Optional schema name
            returning_columns: Columns to return after insert (Oracle RETURNING clause)
            hints: Oracle optimizer hints (e.g., ['APPEND', 'PARALLEL(4)'])

        Returns:
            FlextResult containing the INSERT statement

        """
        try:
            full_table_name = self._build_table_name(table_name, schema_name)

            # Build hints if provided
            hint_clause = ""
            if hints:
                hint_clause = f"/*+ {' '.join(hints)} */ "

            # Build column list and parameter placeholders
            col_list = ", ".join(columns)
            param_list = ", ".join([f":{col}" for col in columns])

            # Build basic INSERT
            sql = f"INSERT {hint_clause}INTO {full_table_name} ({col_list}) VALUES ({param_list})"

            # Add RETURNING clause if specified
            if returning_columns:
                returning_list = ", ".join(returning_columns)
                sql += f" RETURNING {returning_list} INTO {', '.join([f':out_{col}' for col in returning_columns])}"

            return FlextResult.ok(sql)

        except Exception as e:
            return self._handle_database_error_simple("INSERT statement build failed", e)

    def build_update_statement(
        self,
        table_name: str,
        set_columns: list[str],
        where_columns: list[str],
        schema_name: str | None = None,
        returning_columns: list[str] | None = None,
    ) -> FlextResult[str]:
        """Build UPDATE statement with Oracle-specific features.

        Args:
            table_name: Target table name
            set_columns: Columns to update
            where_columns: Columns for WHERE clause
            schema_name: Optional schema name
            returning_columns: Columns to return after update

        Returns:
            FlextResult containing the UPDATE statement

        """
        try:
            full_table_name = self._build_table_name(table_name, schema_name)

            # Build SET clause
            set_clause = ", ".join([f"{col} = :{col}" for col in set_columns])

            # Build WHERE clause
            where_clause = " AND ".join([f"{col} = :where_{col}" for col in where_columns])

            # Build UPDATE statement
            sql = f"UPDATE {full_table_name} SET {set_clause} WHERE {where_clause}"

            # Add RETURNING clause if specified
            if returning_columns:
                returning_list = ", ".join(returning_columns)
                sql += f" RETURNING {returning_list} INTO {', '.join([f':out_{col}' for col in returning_columns])}"

            return FlextResult.ok(sql)

        except Exception as e:
            return self._handle_database_error_simple("UPDATE statement build failed", e)

    def build_merge_statement(
        self,
        config: MergeStatementConfig,
    ) -> FlextResult[str]:
        """Build Oracle MERGE statement for upsert operations - SOLID refactoring.

        Args:
            config: Merge statement configuration with all required parameters

        Returns:
            FlextResult containing the MERGE statement

        """
        try:
            full_table_name = self._build_table_name(config.target_table, config.schema_name)

            # Default update columns to all non-key columns
            if config.update_columns is None:
                update_columns = [col for col in config.source_columns if col not in config.merge_keys]
            else:
                update_columns = config.update_columns

            # Default insert columns to all source columns
            if config.insert_columns is None:
                insert_columns = config.source_columns
            else:
                insert_columns = config.insert_columns

            # Build hints if provided
            hint_clause = ""
            if config.hints:
                hint_clause = f"/*+ {' '.join(config.hints)} */ "

            # Build source subquery with parameters
            source_select = ", ".join([f":src_{col} AS {col}" for col in config.source_columns])

            # Build ON clause
            on_conditions = " AND ".join([f"tgt.{key} = src.{key}" for key in config.merge_keys])

            # Build UPDATE SET clause
            update_set = ", ".join([f"tgt.{col} = src.{col}" for col in update_columns])

            # Build INSERT columns and values
            insert_cols = ", ".join(insert_columns)
            insert_vals = ", ".join([f"src.{col}" for col in insert_columns])

            # Build complete MERGE statement
            sql = f"""
                MERGE {hint_clause}INTO {full_table_name} tgt
                USING (SELECT {source_select} FROM DUAL) src
                ON ({on_conditions})
                WHEN MATCHED THEN
                    UPDATE SET {update_set}
                WHEN NOT MATCHED THEN
                    INSERT ({insert_cols})
                    VALUES ({insert_vals})
            """

            return FlextResult.ok(sql.strip())

        except Exception as e:
            return self._handle_database_error_simple("MERGE statement build failed", e)

    def build_delete_statement(
        self,
        table_name: str,
        where_columns: list[str],
        schema_name: str | None = None,
    ) -> FlextResult[str]:
        """Build DELETE statement.

        Args:
            table_name: Target table name
            where_columns: Columns for WHERE clause
            schema_name: Optional schema name

        Returns:
            FlextResult containing the DELETE statement

        """
        try:
            full_table_name = self._build_table_name(table_name, schema_name)

            # Build WHERE clause
            where_clause = " AND ".join([f"{col} = :{col}" for col in where_columns])

            # Build DELETE statement
            sql = f"DELETE FROM {full_table_name} WHERE {where_clause}"

            return FlextResult.ok(sql)

        except Exception as e:
            return self._handle_database_error_simple("DELETE statement build failed", e)

    def build_create_index_statement(
        self,
        index_name: str,
        table_name: str,
        columns: list[str],
        *,
        schema_name: str | None = None,
        unique: bool = False,
        tablespace: str | None = None,
        parallel: int | None = None,
    ) -> FlextResult[str]:
        """Build CREATE INDEX statement with Oracle-specific features.

        Args:
            index_name: Name of the index
            table_name: Table to index
            columns: Column names to index
            schema_name: Optional schema name
            unique: Whether to create unique index
            tablespace: Optional tablespace name
            parallel: Degree of parallelism for index creation

        Returns:
            FlextResult containing the CREATE INDEX statement

        """
        try:
            full_table_name = self._build_table_name(table_name, schema_name)

            # Build index type
            index_type = "UNIQUE INDEX" if unique else "INDEX"

            # Build column list
            col_list = ", ".join(columns)

            # Build basic CREATE INDEX
            sql = f"CREATE {index_type} {schema_name}.{index_name} ON {full_table_name} ({col_list})"

            # Add tablespace if specified
            if tablespace:
                sql += f" TABLESPACE {tablespace}"

            # Add parallel option if specified
            if parallel:
                sql += f" PARALLEL {parallel}"

            return FlextResult.ok(sql)

        except Exception as e:
            return self._handle_database_error_simple("CREATE INDEX statement build failed", e)


__all__: list[str] = ["FlextDbOracleConnection"]
