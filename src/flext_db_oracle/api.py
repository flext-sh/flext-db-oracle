"""Oracle API with enhanced flext-core patterns.

Refactored Oracle database interface that consolidates functionality using
composition patterns and flext-core resources to reduce complexity.
"""

from __future__ import annotations

from contextlib import contextmanager
from datetime import UTC, datetime
from typing import TYPE_CHECKING, Any, Self

from flext_core import (
    FlextResult,
    get_flext_container,
    get_logger,
)
from pydantic import SecretStr

from .config import FlextDbOracleConfig
from .connection import FlextDbOracleConnection
from .types import TDbOracleQueryResult

if TYPE_CHECKING:
    import types
    from collections.abc import Generator


class FlextDbOracleApi:
    """Oracle API using composition and flext-core patterns.

    High-level interface that consolidates configuration, connection,
    and database operations into a single API using composition.
    """

    def __init__(
        self,
        config: FlextDbOracleConfig | None = None,
        context_name: str = "oracle",
    ) -> None:
        """Initialize Oracle API with optional configuration.

        Args:
            config: Optional Oracle configuration.
            context_name: Context name for logging and container management.

        """
        self._context_name = context_name
        self._container = get_flext_container()
        self._logger = get_logger(f"FlextDbOracleApi.{context_name}")

        # Configuration and connection management
        self._config = config
        self._connection: FlextDbOracleConnection | None = None
        self._is_connected = False

        # Default settings
        self._retry_attempts = 3

    # =============================================================================
    # FACTORY METHODS
    # =============================================================================

    @classmethod
    def from_env(
        cls,
        env_prefix: str = "FLEXT_TARGET_ORACLE_",
        context_name: str = "oracle",
    ) -> FlextDbOracleApi:
        """Create Oracle API from environment variables."""
        logger = get_logger(f"FlextDbOracleApi.{context_name}")
        logger.info("Loading Oracle configuration from environment")

        config_result = FlextDbOracleConfig.from_env(env_prefix)
        if config_result.is_failure:
            logger.error("Failed to load config from environment: %s", config_result.error)
            msg = f"Configuration loading failed: {config_result.error}"
            raise ValueError(msg)

        if config_result.data is None:
            msg = "Configuration data is None - this should not happen"
            raise ValueError(msg)

        config = config_result.data

        logger.info("Oracle configuration loaded successfully")
        return cls(config, context_name)

    @classmethod
    def with_config(
        cls,
        context_name: str = "oracle",
        **config_params: Any,  # noqa: ANN401  # Required for flexible config parameter passing
    ) -> FlextDbOracleApi:
        """Create Oracle API with direct configuration parameters."""
        logger = get_logger(f"FlextDbOracleApi.{context_name}")
        logger.info("Creating Oracle configuration with parameters")

        # Create configuration with defaults using flext-core patterns
        try:
            # Handle password conversion to SecretStr if provided
            params = dict(config_params)
            if "password" in params:
                password_val = params["password"]
                params["password"] = SecretStr(str(password_val))
            config = FlextDbOracleConfig(**params)
        except (ValueError, TypeError, AttributeError) as e:
            logger.exception("Configuration creation failed")
            msg = f"Invalid configuration: {e}"
            raise ValueError(msg) from e

        config_result = config.validate_domain_rules()
        if config_result.is_failure:
            logger.error("Configuration creation failed: %s", config_result.error)
            msg = f"Invalid configuration: {config_result.error}"
            raise ValueError(msg)

        logger.info("Oracle configuration created successfully")
        return cls(config, context_name)

    @classmethod
    def from_url(
        cls,
        url: str,
        context_name: str = "oracle",
    ) -> FlextDbOracleApi:
        """Create Oracle API from connection URL."""
        logger = get_logger(f"FlextDbOracleApi.{context_name}")
        logger.info("Creating Oracle configuration from URL")

        config_result = FlextDbOracleConfig.from_url(url)
        if config_result.is_failure:
            logger.error("URL parsing failed: %s", config_result.error)
            msg = f"Invalid URL format: {config_result.error}"
            raise ValueError(msg)

        config = config_result.data
        logger.info("Oracle configuration created from URL successfully")
        return cls(config, context_name)

    # =============================================================================
    # CONNECTION MANAGEMENT
    # =============================================================================

    def connect(self) -> FlextDbOracleApi:
        """Establish database connection with retry logic."""
        if self._is_connected:
            self._logger.info("Already connected to Oracle database")
            return self

        if not self._config:
            msg = "No configuration provided"
            raise ValueError(msg)

        self._logger.info("Connecting to Oracle database")

        # Simple retry logic
        last_error = None
        for attempt in range(self._retry_attempts + 1):
            try:
                connection = FlextDbOracleConnection(self._config)
                connect_result = connection.connect()
                if connect_result.is_success:
                    self._connection = connection
                    self._is_connected = True

                    # Store in container
                    self._container.register(f"oracle_connection_{self._context_name}", self._connection)

                    self._logger.info("Oracle database connection established successfully")
                    return self
                last_error = connect_result.error
                if attempt < self._retry_attempts:
                    self._logger.warning("Connection attempt %d failed, retrying: %s", attempt + 1, last_error)

            except (ConnectionError, OSError, ValueError, AttributeError) as e:
                last_error = str(e)
                if attempt < self._retry_attempts:
                    self._logger.warning("Connection attempt %d failed, retrying: %s", attempt + 1, last_error)

        self._logger.error("Connection failed after %d attempts: %s", self._retry_attempts + 1, last_error)
        msg = f"Failed to connect: {last_error}"
        raise ConnectionError(msg)

    def disconnect(self) -> FlextDbOracleApi:
        """Disconnect from database."""
        if not self._is_connected or not self._connection:
            return self

        self._logger.info("Disconnecting from Oracle database")
        self._connection.disconnect()
        self._connection = None
        self._is_connected = False
        self._logger.info("Oracle database disconnected successfully")
        return self

    def test_connection(self) -> FlextResult[bool]:
        """Test database connection."""
        if not self._connection:
            return FlextResult.fail("No connection established")

        self._logger.info("Testing Oracle database connection")
        return self._connection.test_connection()

    # =============================================================================
    # QUERY OPERATIONS
    # =============================================================================

    def query(
        self,
        sql: str,
        params: dict[str, Any] | None = None,
    ) -> FlextResult[list[tuple[Any, ...]]]:
        """Execute SQL query."""
        if not self._is_connected or not self._connection:
            return FlextResult.fail("Database not connected")

        self._logger.debug("Executing SQL query")
        result = self._connection.execute(sql, params)
        if result.is_success:
            row_count = len(result.data) if result.data else 0
            self._logger.info("Query executed successfully, returned %d rows", row_count)
        else:
            self._logger.error("Query execution failed: %s", result.error)

        return result

    def query_with_timing(self, sql: str, params: dict[str, Any] | None = None) -> FlextResult[TDbOracleQueryResult]:
        """Execute query with timing metrics (consolidated from QueryService)."""
        if not self._is_connected or not self._connection:
            return FlextResult.fail("Database not connected")

        start_time = datetime.now(UTC)

        try:
            # Execute query
            result = self._connection.execute(sql, params)
            if result.is_failure:
                return FlextResult.fail(result.error or "Query execution failed")

            # Calculate execution time
            execution_time = (datetime.now(UTC) - start_time).total_seconds() * 1000

            # Handle None data result
            rows_data = result.data or []

            # Create structured result (consolidated functionality)
            query_result = TDbOracleQueryResult(
                rows=rows_data,
                columns=[],  # Would need cursor.description to get column names
                row_count=len(rows_data),
                execution_time_ms=execution_time,
            )

            self._logger.info("Query executed: %d rows, %.2fms", len(rows_data), execution_time)
            return FlextResult.ok(query_result)

        except (ConnectionError, OSError, ValueError, AttributeError) as e:
            execution_time = (datetime.now(UTC) - start_time).total_seconds() * 1000
            self._logger.exception("Query failed after %.2fms", execution_time)
            return FlextResult.fail(f"Query execution failed: {e}")

    def query_one(
        self,
        sql: str,
        params: dict[str, Any] | None = None,
    ) -> FlextResult[tuple[Any, ...] | None]:
        """Execute SQL query expecting single result."""
        if not self._is_connected or not self._connection:
            return FlextResult.fail("Database not connected")

        return self._connection.fetch_one(sql, params)

    def execute_batch(self, operations: list[tuple[str, dict[str, Any] | None]]) -> FlextResult[list[Any]]:
        """Execute batch operations using flext-core patterns."""
        if not self._connection:
            return FlextResult.fail("No database connection")

        results = []
        for i, (sql, params) in enumerate(operations):
            self._logger.debug("Executing batch operation %d", i + 1)
            result = self._connection.execute(sql, params)
            if result.is_failure:
                self._logger.error("Batch operation %d failed: %s", i + 1, result.error)
                return FlextResult.fail(f"Batch operation {i + 1} failed: {result.error}")
            results.append(result.data)

        self._logger.info("Batch operations completed successfully: %d operations", len(operations))
        return FlextResult.ok(results)

    # =============================================================================
    # CONTEXT MANAGEMENT
    # =============================================================================

    @contextmanager
    def transaction(self) -> Generator[FlextDbOracleApi]:
        """Context manager for database transactions."""
        if not self._connection:
            msg = "No database connection"
            raise ValueError(msg)

        self._logger.info("Starting database transaction")
        try:
            with self._connection.transaction():
                yield self
            self._logger.info("Transaction completed successfully")
        except Exception:
            self._logger.exception("Transaction failed")
            raise

    # =============================================================================
    # METADATA OPERATIONS - Consolidated interface
    # =============================================================================

    def get_tables(self, schema: str | None = None) -> FlextResult[list[str]]:
        """Get table names."""
        if not self._connection:
            return FlextResult.fail("No database connection")

        return self._connection.get_table_names(schema)

    def get_schemas(self) -> FlextResult[list[str]]:
        """Get available schema names (consolidated from connection)."""
        if not self._connection:
            return FlextResult.fail("No database connection")

        return self._connection.get_schemas()

    def get_columns(
        self,
        table_name: str,
        schema: str | None = None,
    ) -> FlextResult[list[dict[str, Any]]]:
        """Get column information for table."""
        if not self._connection:
            return FlextResult.fail("No database connection")

        return self._connection.get_column_info(table_name, schema)

    def get_primary_keys(
        self,
        table_name: str,
        schema: str | None = None,
    ) -> FlextResult[list[str]]:
        """Get primary key columns for table."""
        if not self._connection:
            return FlextResult.fail("No database connection")

        return self._connection.get_primary_key_columns(table_name, schema)

    def get_table_metadata(
        self,
        table_name: str,
        schema: str | None = None,
    ) -> FlextResult[dict[str, Any]]:
        """Get complete table metadata."""
        if not self._connection:
            return FlextResult.fail("No database connection")

        return self._connection.get_table_metadata(table_name, schema)

    def build_select(
        self,
        table_name: str,
        columns: list[str] | None = None,
        conditions: dict[str, Any] | None = None,
        schema: str | None = None,
    ) -> FlextResult[str]:
        """Build SELECT query using SQLAlchemy patterns."""
        if not self._connection:
            return FlextResult.fail("No database connection")

        return self._connection.build_select(table_name, columns, conditions, schema)

    # =============================================================================
    # DDL OPERATIONS - Consolidated interface
    # =============================================================================

    def create_table_ddl(
        self,
        table_name: str,
        columns: list[dict[str, Any]],
        schema: str | None = None,
    ) -> FlextResult[str]:
        """Generate CREATE TABLE DDL."""
        if not self._connection:
            return FlextResult.fail("No database connection")

        return self._connection.create_table_ddl(table_name, columns, schema)

    def drop_table_ddl(
        self,
        table_name: str,
        schema: str | None = None,
    ) -> FlextResult[str]:
        """Generate DROP TABLE DDL."""
        if not self._connection:
            return FlextResult.fail("No database connection")

        return self._connection.drop_table_ddl(table_name, schema)

    def execute_ddl(self, ddl: str) -> FlextResult[bool]:
        """Execute DDL statement."""
        if not self._connection:
            return FlextResult.fail("No database connection")

        return self._connection.execute_ddl(ddl)

    # =============================================================================
    # TYPE CONVERSION - Singer/Oracle schema mapping
    # =============================================================================

    def convert_singer_type(
        self,
        singer_type: str | list[str],
        format_hint: str | None = None,
    ) -> FlextResult[str]:
        """Convert Singer type to Oracle type."""
        if not self._connection:
            return FlextResult.fail("No database connection")

        return self._connection.convert_singer_type(singer_type, format_hint)

    def map_singer_schema(
        self,
        singer_schema: dict[str, Any],
    ) -> FlextResult[dict[str, str]]:
        """Map Singer schema to Oracle column definitions."""
        if not self._connection:
            return FlextResult.fail("No database connection")

        return self._connection.map_singer_schema(singer_schema)

    # =============================================================================
    # PROPERTIES
    # =============================================================================

    @property
    def is_connected(self) -> bool:
        """Check if database is connected."""
        return self._is_connected and self._connection is not None

    @property
    def config(self) -> FlextDbOracleConfig | None:
        """Get current configuration."""
        return self._config

    @property
    def connection(self) -> FlextDbOracleConnection | None:
        """Get underlying connection."""
        return self._connection

    def __enter__(self) -> Self:
        """Context manager entry."""
        if not self._is_connected:
            self.connect()
        return self

    def __exit__(self, exc_type: type[BaseException] | None, exc_val: BaseException | None, exc_tb: types.TracebackType | None) -> None:
        """Context manager exit."""
        self.disconnect()


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    "FlextDbOracleApi",
]
