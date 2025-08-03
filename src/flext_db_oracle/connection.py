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
    >>> if connect_result.is_success:
    ...     result = connection.execute("SELECT * FROM employees WHERE dept_id = :dept", {"dept": 10})
    ...     if result.is_success:
    ...         for row in result.value:
    ...             print(row)

Integration:
    - Built on SQLAlchemy 2.x for modern async/sync database operations
    - Integrates with flext-core FlextResult patterns for error handling
    - Supports flext-observability for performance monitoring
    - Compatible with Singer ecosystem for data pipeline operations
    - Provides foundation for flext-tap-oracle and flext-target-oracle

Author: FLEXT Development Team
Version: 2.0.0
License: MIT

"""

from __future__ import annotations

from collections.abc import Generator
from contextlib import contextmanager
from typing import TYPE_CHECKING
from urllib.parse import quote_plus

from flext_core import FlextResult, get_logger
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session, sessionmaker

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
    from collections.abc import Generator

    from sqlalchemy.engine import Engine

    from .config import FlextDbOracleConfig

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
            error_msg = f"Failed to connect: {e}"
            self._logger.exception(error_msg)
            return FlextResult.fail(error_msg)

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
            return FlextResult.fail(f"Disconnect failed: {e}")

    def is_connected(self) -> bool:
        """Check if connected to database."""
        return self._engine is not None

    def execute(
        self,
        sql: str,
        parameters: dict[str, object] | None = None,
    ) -> FlextResult[list[object]]:
        """Execute SQL statement using SQLAlchemy 2."""
        if not self.is_connected():
            return FlextResult.fail("Not connected to database")

        if not self._engine:
            return FlextResult.fail("Database engine not initialized")

        try:
            with self._engine.connect() as conn:
                result = conn.execute(text(sql), parameters or {})

                # Handle different statement types
                if sql.strip().upper().startswith(("SELECT", "WITH")):
                    rows = result.fetchall()
                    return FlextResult.ok(list(rows))
                conn.commit()
                return FlextResult.ok([result.rowcount])

        except (SQLAlchemyError, OSError, ValueError, AttributeError) as e:
            error_msg = f"SQL execution failed: {e}"
            self._logger.exception(error_msg)
            return FlextResult.fail(error_msg)

    def execute_many(
        self,
        sql: str,
        parameters_list: list[dict[str, object]],
    ) -> FlextResult[int]:
        """Execute SQL with multiple parameter sets."""
        if not self.is_connected():
            return FlextResult.fail("Not connected to database")

        if not self._engine:
            return FlextResult.fail("Database engine not initialized")

        try:
            with self._engine.connect() as conn:
                result = conn.execute(text(sql), parameters_list)
                conn.commit()
                return FlextResult.ok(result.rowcount)

        except (SQLAlchemyError, OSError, ValueError, AttributeError) as e:
            error_msg = f"Batch execution failed: {e}"
            self._logger.exception(error_msg)
            return FlextResult.fail(error_msg)

    def fetch_one(
        self,
        sql: str,
        parameters: dict[str, object] | None = None,
    ) -> FlextResult[object]:
        """Fetch single row."""
        if not self.is_connected():
            return FlextResult.fail("Not connected to database")

        if not self._engine:
            return FlextResult.fail("Database engine not initialized")

        try:
            with self._engine.connect() as conn:
                result = conn.execute(text(sql), parameters or {})
                return FlextResult.ok(result.fetchone())

        except (SQLAlchemyError, OSError, ValueError, AttributeError) as e:
            error_msg = f"Fetch one failed: {e}"
            self._logger.exception(error_msg)
            return FlextResult.fail(error_msg)

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
        if not self.is_connected():
            msg = "Not connected to database"
            raise ValueError(msg)

        if not self._engine:
            msg = "Database engine not initialized"
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
            error_msg = f"Failed to close connection: {e}"
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
        if not self.is_connected():
            return FlextResult.fail("Not connected")

        try:
            result = self.execute(ORACLE_TEST_QUERY)
            return FlextResult.ok(result.is_success)
        except (SQLAlchemyError, OSError, ValueError, AttributeError, Exception) as e:
            return FlextResult.fail(f"Connection test failed: {e}")

    def get_table_names(self, schema_name: str | None = None) -> FlextResult[list[str]]:
        """Get table names from schema."""
        try:
            if schema_name:
                sql = "SELECT table_name FROM all_tables WHERE owner = UPPER(:schema_name) ORDER BY table_name"
                params: dict[str, object] = {"schema_name": schema_name}
            else:
                sql = "SELECT table_name FROM user_tables ORDER BY table_name"
                params = {}

            result = self.execute(sql, params)
            if result.is_failure:
                return FlextResult.fail(result.error or "Failed to get table names")

            if not result.data:
                return FlextResult.ok([])

            # MYPY FIX: Safe type conversion for table names
            table_names: list[str] = [
                str(row[0])
                for row in result.data
                if hasattr(row, "__getitem__") and hasattr(row, "__len__") and len(row) > 0
            ]

            return FlextResult.ok(table_names)
        except (SQLAlchemyError, OSError, ValueError, AttributeError, Exception) as e:
            return FlextResult.fail(f"Error retrieving table names: {e}")

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
        current_schema = str(result.data[0][0]) if hasattr(result.data[0], "__getitem__") else str(result.data[0])
        return FlextResult.ok(current_schema)

    def get_column_info(
        self,
        table_name: str,
        schema_name: str | None = None,
    ) -> FlextResult[list[dict[str, object]]]:
        """Get column information for table."""
        if schema_name:
            sql = """
                SELECT column_name, data_type, nullable, data_length, data_precision, data_scale, column_id
                FROM all_tab_columns
                WHERE owner = UPPER(:schema_name) AND table_name = UPPER(:table_name)
                ORDER BY column_id
            """
            params: dict[str, object] = {
                "schema_name": schema_name,
                "table_name": table_name,
            }
        else:
            sql = """
                SELECT column_name, data_type, nullable, data_length, data_precision, data_scale, column_id
                FROM user_tab_columns
                WHERE table_name = UPPER(:table_name)
                ORDER BY column_id
            """
            params = {"table_name": table_name}

        result = self.execute(sql, params)
        if result.is_failure:
            return FlextResult.fail(result.error or "Failed to get column info")

        # MYPY FIX: Safe type conversion for column information
        columns: list[dict[str, object]] = [
            {
                "column_name": str(row[0]),
                "data_type": str(row[1]),
                "nullable": str(row[2]) == "Y",
                "data_length": row[3],
                "data_precision": row[4],
                "data_scale": row[5],
                "column_id": row[6],
            }
            for row in result.data or []
            if hasattr(row, "__getitem__") and hasattr(row, "__len__") and len(row) >= ORACLE_COLUMN_INFO_FIELDS
        ]

        return FlextResult.ok(columns)

    def get_primary_key_columns(
        self,
        table_name: str,
        schema_name: str | None = None,
    ) -> FlextResult[list[str]]:
        """Get primary key columns for table (consolidated from services)."""
        if schema_name:
            sql = """
                SELECT column_name
                FROM all_cons_columns c
                JOIN all_constraints ct ON c.constraint_name = ct.constraint_name
                    AND c.owner = ct.owner
                WHERE ct.constraint_type = 'P'
                    AND ct.owner = UPPER(:schema_name)
                    AND ct.table_name = UPPER(:table_name)
                ORDER BY c.position
            """
            params: dict[str, object] = {
                "schema_name": schema_name,
                "table_name": table_name,
            }
        else:
            sql = """
                SELECT column_name
                FROM user_cons_columns c
                JOIN user_constraints ct ON c.constraint_name = ct.constraint_name
                WHERE ct.constraint_type = 'P'
                    AND ct.table_name = UPPER(:table_name)
                ORDER BY c.position
            """
            params = {"table_name": table_name}

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
            # Build column list - safe since it's internal column names
            column_list = ", ".join(columns) if columns else "*"

            # Build table name - safe since it's internal table/schema names
            if schema_name:
                full_table_name = f"{schema_name}.{table_name}"
            else:
                full_table_name = table_name

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
            # Build column list - safe since it's internal column names
            column_list = ", ".join(columns) if columns else "*"

            # Build table name - safe since it's internal table/schema names
            if schema_name:
                full_table_name = f"{schema_name}.{table_name}"
            else:
                full_table_name = table_name

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

    def create_table_ddl(
        self,
        table_name: str,
        columns: list[dict[str, object]],
        schema_name: str | None = None,
    ) -> FlextResult[str]:
        """Generate CREATE TABLE DDL (consolidated from services)."""
        try:
            # Build table name
            if schema_name:
                full_table_name = f"{schema_name}.{table_name}"
            else:
                full_table_name = table_name

            # Build column definitions and collect primary key columns
            column_defs = []
            primary_key_columns = []

            for col in columns:
                # Support both 'type' and 'data_type' keys for backward compatibility
                data_type = col.get("data_type") or col.get("type")
                if not data_type:
                    return FlextResult.fail("Column must have 'type' or 'data_type' specified")

                col_def = f"{col['name']} {data_type}"
                if not col.get("nullable", True):
                    col_def += " NOT NULL"
                if col.get("default_value"):
                    col_def += f" DEFAULT {col['default_value']}"
                column_defs.append(col_def)

                # Collect primary key columns
                if col.get("primary_key", False):
                    primary_key_columns.append(col["name"])

            # Add PRIMARY KEY constraint if any columns are marked as primary key
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
            return FlextResult.fail(f"DDL generation failed: {e}")

    def drop_table_ddl(
        self,
        table_name: str,
        schema_name: str | None = None,
    ) -> FlextResult[str]:
        """Generate DROP TABLE DDL (consolidated from services)."""
        try:
            if schema_name:
                full_table_name = f"{schema_name}.{table_name}"
            else:
                full_table_name = table_name

            ddl = f"DROP TABLE {full_table_name}"
            return FlextResult.ok(ddl)

        except (SQLAlchemyError, OSError, ValueError, AttributeError) as e:
            return FlextResult.fail(f"DROP DDL generation failed: {e}")

    def execute_ddl(self, ddl: str) -> FlextResult[bool]:
        """Execute DDL statement (consolidated from services)."""
        try:
            result = self.execute(ddl)
            if result.is_success:
                return FlextResult.ok(data=True)
            return FlextResult.fail(result.error or "DDL execution failed")

        except (SQLAlchemyError, OSError, ValueError, AttributeError) as e:
            return FlextResult.fail(f"DDL execution failed: {e}")

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
            return FlextResult.fail(f"Type conversion failed: {e}")

    def map_singer_schema(
        self,
        singer_schema: dict[str, object],
    ) -> FlextResult[dict[str, str]]:
        """Map Singer schema to Oracle column definitions (consolidated from services)."""
        try:
            oracle_columns: dict[str, str] = {}

            properties = singer_schema.get("properties", {})
            # MYPY FIX: Cast to proper type for iteration
            if not isinstance(properties, dict):
                return FlextResult.fail("Schema properties must be a dictionary")
            for field_name, field_def in properties.items():
                if not isinstance(field_def, dict):
                    continue  # Skip invalid field definitions
                field_type = field_def.get("type", "string")
                format_hint = field_def.get("format")

                type_result = self.convert_singer_type(field_type, format_hint)
                if type_result.is_failure:
                    return FlextResult.fail(
                        type_result.error or "Type conversion failed",
                    )

                oracle_columns[field_name] = type_result.data or "VARCHAR2(4000)"

            return FlextResult.ok(oracle_columns)

        except (SQLAlchemyError, OSError, ValueError, AttributeError) as e:
            return FlextResult.fail(f"Schema mapping failed: {e}")

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
            return FlextResult.fail(f"URL building failed: {e}")


__all__ = ["FlextDbOracleConnection"]
