"""Oracle API with enhanced flext-core patterns.

Refactored Oracle database interface that consolidates functionality using
composition patterns and flext-core resources to reduce complexity.
"""

from __future__ import annotations

from contextlib import contextmanager
from time import perf_counter
from typing import TYPE_CHECKING, Any, Self

from flext_core import (
    FlextResult,
    get_flext_container,
    get_logger,
)
from flext_plugin import (
    FlextPlugin,
    create_flext_plugin,
    create_flext_plugin_platform,
)
from pydantic import SecretStr

from .config import FlextDbOracleConfig
from .connection import FlextDbOracleConnection
from .observability import (
    FlextDbOracleErrorHandler,
    FlextDbOracleObservabilityManager,
)
from .types import TDbOracleQueryResult

if TYPE_CHECKING:
    import types
    from collections.abc import Generator

    from flext_observability import FlextHealthCheck, FlextTrace


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

        # Centralized observability manager (DRY principle)
        self._observability = FlextDbOracleObservabilityManager(
            self._container, self._context_name,
        )
        self._error_handler = FlextDbOracleErrorHandler(self._observability)

        # Plugin system
        self._plugin_platform = create_flext_plugin_platform(
            {
                "context_name": self._context_name,
                "oracle_api": self,
            },
        )

        # Initialize systems
        self._observability.initialize()
        self._init_plugins()

    # =============================================================================
    # OBSERVABILITY METHODS (Centralized in FlextDbOracleObservabilityManager)
    # =============================================================================

    def _get_health_check(self) -> FlextResult[FlextHealthCheck]:
        """Get health check status for Oracle connection."""
        if not self._is_connected or not self._connection:
            return self._observability.create_health_check(
                status="unhealthy",
                message="Database not connected",
                metrics={"connected": False, "config_valid": self._config is not None},
            )

        # Test connection with simple query
        health_query_result = self.query("SELECT 1 FROM DUAL")

        if health_query_result.is_success:
            return self._observability.create_health_check(
                status="healthy",
                message="Database connection operational",
                metrics={
                    "connected": True,
                    "config_valid": True,
                    "last_query_success": True,
                },
            )

        return self._observability.create_health_check(
            status="degraded",
            message=f"Database connection issues: {health_query_result.error}",
            metrics={
                "connected": True,
                "config_valid": True,
                "last_query_success": False,
            },
        )

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
            logger.error(
                "Failed to load config from environment: %s",
                config_result.error,
            )
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
    # CONNECTION MANAGEMENT - DRY helper methods
    # =============================================================================

    def _create_connection_trace(self) -> FlextTrace:
        """Create connection trace - DRY pattern."""
        return self._observability.create_trace(
            "connect",
            host=self._config.host if self._config else "unknown",
            service_name=self._config.service_name if self._config else "unknown",
        )

    def _handle_connection_success(
        self, trace: FlextTrace, execution_time: float,
    ) -> FlextDbOracleApi:
        """Handle successful connection - DRY pattern."""
        self._is_connected = True
        self._observability.record_metric("connection.success", 1, "count")
        self._observability.record_metric(
            "connection.duration_ms", execution_time * 1000, "ms",
        )
        self._observability.finish_trace(
            trace, int(execution_time * 1000), "success",
        )
        self._logger.info(
            "Connected to Oracle database in %.2fms", execution_time * 1000,
        )
        return self

    def _handle_already_connected(self) -> FlextDbOracleApi:
        """Handle already connected state - DRY pattern."""
        self._logger.info("Already connected to Oracle database")
        self._observability.record_metric("connection.already_connected", 1, "count")
        return self

    def _init_connection_attempt(self) -> None:
        """Initialize connection attempt - DRY pattern."""
        self._logger.info("Connecting to Oracle database")
        self._observability.record_metric("connection.attempts", 1, "count")

    def _execute_connection_retry_loop(self, start_time: float) -> str | None:
        """Execute connection retry loop - DRY pattern."""
        last_error = None
        for attempt in range(self._retry_attempts + 1):
            result = self._attempt_single_connection(attempt, start_time)
            if result["success"]:
                return None  # Success, no error
            last_error = result["error"]
        return last_error

    def _attempt_single_connection(
        self, attempt: int, start_time: float,
    ) -> dict[str, Any]:
        """Attempt single connection - DRY pattern."""
        attempt_start = perf_counter()

        try:
            # Type guard: _config já foi verificado acima
            assert self._config is not None  # noqa: S101
            connection = FlextDbOracleConnection(self._config)
            connect_result = connection.connect()

            if connect_result.is_success:
                return self._handle_connection_attempt_success(
                    connection, attempt, start_time,
                )

            # Handle connection failure - DRY pattern
            error_msg = connect_result.error or "Unknown connection error"
            self._record_attempt_failure(
                attempt, attempt_start, error_msg, "connection_result_failure",
            )
        except (ConnectionError, OSError, ValueError, AttributeError) as e:
            error_str = str(e)
            self._record_attempt_failure(attempt, attempt_start, error_str, type(e).__name__)
            return {"success": False, "error": error_str}

        return {"success": False, "error": error_msg}

    def _handle_connection_attempt_success(
        self, connection: FlextDbOracleConnection, attempt: int, start_time: float,
    ) -> dict[str, Any]:
        """Handle successful connection attempt - DRY pattern."""
        self._connection = connection
        self._container.register(
            f"oracle_connection_{self._context_name}", self._connection,
        )

        connection_time = perf_counter() - start_time
        self._observability.record_metric("connection.attempts_made", attempt + 1, "count")

        # Execute connection monitor plugin
        monitor_result = self.execute_connection_monitor()
        if monitor_result.is_success and monitor_result.data:
            self._logger.debug(
                "Connection monitor executed: %s",
                monitor_result.data.get("connection_status", "unknown"),
            )

        trace = self._create_connection_trace()
        self._handle_connection_success(trace, connection_time)
        return {"success": True, "error": None}

    def _record_attempt_failure(
        self, attempt: int, attempt_start: float, error: str, error_type: str,
    ) -> None:
        """Record attempt failure metrics - DRY pattern."""
        attempt_time = perf_counter() - attempt_start
        self._observability.record_metric(
            "connection.attempt_failed", 1, "count",
            attempt=str(attempt + 1), error_type=error_type,
        )
        self._observability.record_metric(
            "connection.attempt_duration_ms", attempt_time * 1000, "ms",
        )

        if attempt < self._retry_attempts:
            self._logger.warning(
                "Connection attempt %d failed in %.2fms, retrying: %s",
                attempt + 1, attempt_time * 1000, error,
            )

    def _handle_connection_failure_final(
        self, trace: FlextTrace, start_time: float, last_error: str,
    ) -> None:
        """Handle final connection failure - DRY pattern."""
        total_time = perf_counter() - start_time
        self._observability.record_metric("connection.failure", 1, "count")
        self._observability.record_metric(
            "connection.total_duration_ms", total_time * 1000, "ms",
        )
        self._observability.record_metric(
            "connection.total_attempts", self._retry_attempts + 1, "count",
        )

        trace.span_attributes["attempts"] = self._retry_attempts + 1
        self._observability.finish_trace(
            trace, int(total_time * 1000), "error", str(last_error),
        )

        self._logger.error(
            "Connection failed after %d attempts in %.2fms: %s",
            self._retry_attempts + 1, total_time * 1000, last_error,
        )
        self._error_handler.handle_connection_error(last_error)

    def _handle_connection_exception(
        self, trace: FlextTrace, start_time: float, e: Exception,
    ) -> None:
        """Handle connection exception - DRY pattern."""
        total_time = perf_counter() - start_time
        self._observability.record_metric(
            "connection.unexpected_error", 1, "count", error_type=type(e).__name__,
        )

        trace.span_attributes["error_type"] = type(e).__name__
        self._observability.finish_trace(
            trace, int(total_time * 1000), "error", str(e),
        )

    def _handle_connection_failure(
        self, trace: FlextTrace, execution_time: float, error: str,
    ) -> None:
        """Handle connection failure - DRY pattern."""
        self._observability.record_metric("connection.failure", 1, "count")
        self._observability.record_metric(
            "connection.duration_ms", execution_time * 1000, "ms",
        )
        self._observability.finish_trace(
            trace, int(execution_time * 1000), "error", error,
        )
        self._logger.error(
            "Failed to connect to Oracle database in %.2fms: %s",
            execution_time * 1000,
            error,
        )
        self._error_handler.handle_connection_error(error)

    # =============================================================================
    # CONNECTION MANAGEMENT
    # =============================================================================

    def connect(self) -> FlextDbOracleApi:
        """Establish database connection with retry logic and observability."""
        trace = self._create_connection_trace()
        start_time = perf_counter()

        try:
            # Check early exit conditions - DRY pattern
            if self._is_connected:
                return self._handle_already_connected()

            if not self._config:
                self._error_handler.handle_config_error()
                return self  # Não deve chegar aqui, mas para type checking

            # Initialize connection attempt - DRY pattern
            self._init_connection_attempt()

            # Execute retry loop - DRY pattern
            last_error = self._execute_connection_retry_loop(start_time)

            # Handle connection failure - DRY pattern
            if last_error is not None:
                self._handle_connection_failure_final(trace, start_time, last_error)

        except Exception as e:
            self._handle_connection_exception(trace, start_time, e)
            raise

        # Fallback return (should not reach here in normal flow)
        return self

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
        """Execute SQL query with full observability."""
        # Create trace for query operation
        # Create SQL preview for logging (constant limit for clarity)
        sql_preview_limit = 100
        sql_preview = (
            sql[:sql_preview_limit] + "..." if len(sql) > sql_preview_limit else sql
        )
        trace = self._observability.create_trace(
            "query",
            sql_preview=sql_preview,
            has_params=params is not None,
            param_count=len(params) if params else 0,
        )
        start_time = perf_counter()

        try:
            if not self._is_connected or not self._connection:
                self._observability.record_metric("query.not_connected", 1, "count")
                self._observability.finish_trace(
                    trace,
                    0,
                    "error",
                    "Database not connected",
                )
                return FlextResult.fail("Database not connected")

            # Execute query optimization plugin if available
            optimization_result = self.optimize_query(sql)
            if optimization_result.is_success and optimization_result.data:
                opt_data = optimization_result.data
                if opt_data.get("suggestions"):
                    self._logger.debug(
                        "Query optimization suggestions: %s",
                        opt_data["suggestions"],
                    )

            self._logger.debug("Executing SQL query")
            self._observability.record_metric("query.attempts", 1, "count")

            result = self._connection.execute(sql, params)
            execution_time = perf_counter() - start_time

            if result.is_success:
                row_count = len(result.data) if result.data else 0

                # Record success metrics
                self._observability.record_metric("query.success", 1, "count")
                self._observability.record_metric(
                    "query.duration_ms", execution_time * 1000, "ms",
                )
                self._observability.record_metric(
                    "query.rows_returned", row_count, "count",
                )

                # Update trace
                trace.span_attributes["rows_returned"] = row_count
                self._observability.finish_trace(
                    trace,
                    int(execution_time * 1000),
                    "success",
                )

                self._logger.info(
                    "Query executed successfully in %.2fms, returned %d rows",
                    execution_time * 1000,
                    row_count,
                )

                return result

            # Handle query failure - DRY pattern
            self._observability.record_metric("query.failure", 1, "count")
            self._observability.record_metric(
                "query.duration_ms", execution_time * 1000, "ms",
            )

            # Update trace
            self._observability.finish_trace(
                trace,
                int(execution_time * 1000),
                "error",
                result.error or "Unknown error",
            )

            self._logger.error(
                "Query execution failed in %.2fms: %s",
                execution_time * 1000,
                result.error,
            )

        except (ValueError, TypeError, AttributeError, ConnectionError, OSError) as e:
            # Record unexpected errors
            execution_time = perf_counter() - start_time
            self._observability.record_metric(
                "query.unexpected_error", 1, "count", error_type=type(e).__name__,
            )

            trace.span_attributes["error_type"] = type(e).__name__
            self._observability.finish_trace(
                trace,
                int(execution_time * 1000),
                "error",
                str(e),
            )

            raise

        return result

    def query_with_timing(
        self,
        sql: str,
        params: dict[str, Any] | None = None,
    ) -> FlextResult[TDbOracleQueryResult]:
        """Execute query with timing metrics (consolidated from QueryService)."""
        if not self._is_connected or not self._connection:
            return FlextResult.fail("Database not connected")

        start_time = perf_counter()

        try:
            # Execute query
            result = self._connection.execute(sql, params)
            if result.is_failure:
                return FlextResult.fail(result.error or "Query execution failed")

            # Calculate execution time
            execution_time = (perf_counter() - start_time) * 1000

            # Handle None data result
            rows_data = result.data or []

            # Create structured result (consolidated functionality)
            query_result = TDbOracleQueryResult(
                rows=rows_data,
                columns=[],  # Would need cursor.description to get column names
                row_count=len(rows_data),
                execution_time_ms=execution_time,
            )

            self._logger.info(
                "Query executed: %d rows, %.2fms",
                len(rows_data),
                execution_time,
            )
            return FlextResult.ok(query_result)

        except (ConnectionError, OSError, ValueError, AttributeError) as e:
            execution_time = (perf_counter() - start_time) * 1000
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

    def execute_batch(
        self,
        operations: list[tuple[str, dict[str, Any] | None]],
    ) -> FlextResult[list[Any]]:
        """Execute batch operations using flext-core patterns."""
        if not self._connection:
            return FlextResult.fail("No database connection")

        results = []
        for i, (sql, params) in enumerate(operations):
            self._logger.debug("Executing batch operation %d", i + 1)
            result = self._connection.execute(sql, params)
            if result.is_failure:
                self._logger.error("Batch operation %d failed: %s", i + 1, result.error)
                return FlextResult.fail(
                    f"Batch operation {i + 1} failed: {result.error}",
                )
            results.append(result.data)

        self._logger.info(
            "Batch operations completed successfully: %d operations",
            len(operations),
        )
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
        except (ValueError, TypeError, AttributeError, ConnectionError, OSError):
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
    # OBSERVABILITY PUBLIC API
    # =============================================================================

    def get_health_status(self) -> FlextResult[FlextHealthCheck]:
        """Get current health status of Oracle connection."""
        return self._get_health_check()

    def get_observability_metrics(self) -> FlextResult[dict[str, Any]]:
        """Get observability metrics summary."""
        try:
            return FlextResult.ok(
                {
                    "context": self._context_name,
                    "is_connected": self._is_connected,
                    "has_config": self._config is not None,
                    "monitoring_active": self._observability.is_monitoring_active(),
                    "retry_attempts": self._retry_attempts,
                },
            )
        except (ValueError, TypeError, AttributeError) as e:
            return FlextResult.fail(f"Failed to get metrics: {e}")

    def test_connection_with_observability(self) -> FlextResult[dict[str, Any]]:
        """Test connection with detailed observability data."""
        trace = self._observability.create_trace("test_connection")
        start_time = perf_counter()

        try:
            if not self._is_connected or not self._connection:
                health_result = self._get_health_check()
                if health_result.is_failure:
                    return FlextResult.fail(
                        health_result.error or "Health check failed",
                    )

                health_data = {}
                if health_result.is_success and health_result.data:
                    health_data = health_result.data.model_dump()

                return FlextResult.ok(
                    {
                        "status": "disconnected",
                        "health": health_data,
                        "test_duration_ms": int((perf_counter() - start_time) * 1000),
                    },
                )

            # Execute health check query
            query_result = self.query("SELECT 1 as health_check FROM DUAL")
            test_duration = perf_counter() - start_time

            # Update trace
            status = "success" if query_result.is_success else "error"
            error = (
                query_result.error or "Unknown error"
                if query_result.is_failure
                else None
            )
            self._observability.finish_trace(
                trace,
                int(test_duration * 1000),
                status,
                error,
            )

            # Record test metrics
            self._observability.record_metric("connection.test", 1, "count")
            self._observability.record_metric(
                "connection.test_duration_ms", test_duration * 1000, "ms",
            )

            health_result = self._get_health_check()
            health_data = {}
            if health_result.is_success and health_result.data:
                health_data = health_result.data.model_dump()

            return FlextResult.ok(
                {
                    "status": "healthy" if query_result.is_success else "unhealthy",
                    "query_success": query_result.is_success,
                    "query_error": query_result.error
                    if query_result.is_failure
                    else None,
                    "test_duration_ms": int(test_duration * 1000),
                    "health": health_data,
                },
            )

        except (ValueError, TypeError, AttributeError, ConnectionError) as e:
            test_duration = perf_counter() - start_time
            self._observability.finish_trace(
                trace,
                int(test_duration * 1000),
                "error",
                str(e),
            )

            return FlextResult.fail(f"Connection test failed: {e}")

    # =============================================================================
    # PLUGIN SYSTEM PUBLIC API
    # =============================================================================

    def register_plugin(self, plugin: FlextPlugin) -> FlextResult[None]:
        """Register a plugin with the Oracle API."""
        # Use plugin platform API directly - refatoração DRY real
        try:
            result = self._plugin_platform.load_plugin(plugin)
            if result.is_success:
                return FlextResult.ok(data=None)
            return FlextResult.fail(f"Failed to register plugin: {result.error}")
        except (RuntimeError, ValueError, AttributeError) as e:
            return FlextResult.fail(f"Plugin registration error: {e}")

    def unregister_plugin(self, plugin_name: str) -> FlextResult[None]:
        """Unregister a plugin by name."""
        # Use plugin platform API directly - refatoração DRY real
        try:
            result = self._plugin_platform.unload_plugin(plugin_name)
            if result.is_success:
                return FlextResult.ok(data=None)
            return FlextResult.fail(f"Failed to unregister plugin: {result.error}")
        except (RuntimeError, ValueError, AttributeError) as e:
            return FlextResult.fail(f"Plugin unregistration error: {e}")

    def execute_plugin(
        self,
        plugin_name: str,
        **kwargs: Any,  # noqa: ANN401
    ) -> FlextResult[Any]:
        """Execute a plugin by name."""
        # Simplificado: buscar plugin e executar - refatoração DRY
        try:
            plugin_result = self.get_plugin(plugin_name)
            if plugin_result.is_failure:
                return FlextResult.fail(plugin_result.error or "Plugin not found")

            plugin = plugin_result.data
            if plugin and hasattr(plugin, "callable_obj") and plugin.callable_obj:
                return FlextResult.ok(plugin.callable_obj(**kwargs))
            return FlextResult.fail("Plugin is not callable")
        except (ValueError, TypeError, AttributeError) as e:
            return FlextResult.fail(f"Plugin execution failed: {e}")

    def list_plugins(self) -> FlextResult[list[FlextPlugin]]:
        """List all registered plugins."""
        # Usar registry diretamente - refatoração DRY
        try:
            service = self._plugin_platform.plugin_service
            if hasattr(service, "registry") and hasattr(
                service.registry, "list_plugins",
            ):
                plugins = service.registry.list_plugins()
                return FlextResult.ok(plugins)
            return FlextResult.ok([])  # Lista vazia se não há registry
        except (AttributeError, ValueError, TypeError) as e:
            return FlextResult.fail(f"Failed to list plugins: {e}")

    def get_plugin(self, plugin_name: str) -> FlextResult[FlextPlugin]:
        """Get a plugin by name."""
        # Usar registry diretamente - refatoração DRY
        try:
            service = self._plugin_platform.plugin_service
            if hasattr(service, "registry") and hasattr(service.registry, "get_plugin"):
                plugin = service.registry.get_plugin(plugin_name)
                if plugin:
                    return FlextResult.ok(plugin)
            return FlextResult.fail(f"Plugin '{plugin_name}' not found")
        except (AttributeError, ValueError, TypeError) as e:
            return FlextResult.fail(f"Failed to get plugin: {e}")

    def execute_connection_monitor(self, **kwargs: Any) -> FlextResult[dict[str, Any]]:  # noqa: ANN401
        """Execute the built-in connection monitor plugin."""
        return self.execute_plugin("oracle_connection_monitor", **kwargs)

    def optimize_query(self, sql: str, **kwargs: Any) -> FlextResult[dict[str, Any]]:  # noqa: ANN401
        """Execute the built-in query optimizer plugin."""
        return self.execute_plugin("oracle_query_optimizer", sql=sql, **kwargs)

    # =============================================================================
    # PLUGIN SYSTEM PRIVATE METHODS
    # =============================================================================

    def _init_plugins(self) -> None:
        """Initialize plugin system."""
        try:
            # Register built-in Oracle plugins
            self._register_built_in_plugins()
            self._logger.info("Plugin system initialized successfully")
        except (ValueError, TypeError, AttributeError) as e:
            self._logger.warning("Failed to initialize plugin system: %s", e)

    def _register_built_in_plugins(self) -> None:
        """Register built-in Oracle plugins."""
        # Connection monitoring plugin - usar assinaturas corretas da API real
        connection_plugin = create_flext_plugin(
            name="oracle_connection_monitor",
            version="0.9.0",
            config={
                "description": "Monitor Oracle database connections",
                "author": "FLEXT Team",
                "plugin_type": "monitor",
                "monitor_interval": 30,
                "alert_on_disconnect": True,
                "metrics_enabled": True,
                "callable_obj": self._connection_monitor_plugin,
            },
        )

        register_result = self._plugin_platform.load_plugin(connection_plugin)
        if register_result.is_failure:
            self._logger.warning(
                "Failed to register connection monitor plugin: %s",
                register_result.error,
            )

        # Query optimization plugin - usar assinaturas corretas da API real
        query_plugin = create_flext_plugin(
            name="oracle_query_optimizer",
            version="0.9.0",
            config={
                "description": "Optimize Oracle SQL queries",
                "author": "FLEXT Team",
                "plugin_type": "optimizer",
                "analyze_queries": True,
                "suggest_hints": True,
                "cache_plans": True,
                "callable_obj": self._query_optimizer_plugin,
            },
        )

        register_result = self._plugin_platform.load_plugin(query_plugin)
        if register_result.is_failure:
            self._logger.warning(
                "Failed to register query optimizer plugin: %s",
                register_result.error,
            )

    def _connection_monitor_plugin(self, **kwargs: Any) -> FlextResult[dict[str, Any]]:  # noqa: ANN401
        """Built-in connection monitoring plugin."""
        try:
            health_result = self._get_health_check()
            if health_result.is_failure:
                error_msg = health_result.error or "Unknown health check error"
                return FlextResult.fail(error_msg)

            health_data = health_result.data

            # Null check para health data - refatoração DRY real
            if health_data is None:
                return FlextResult.fail("Health check returned no data")

            status = getattr(health_data, "status", "unknown")
            metrics = getattr(health_data, "metrics", {})

            monitor_data = {
                "plugin_name": "oracle_connection_monitor",
                "timestamp": self._observability.get_current_timestamp(),
                "connection_status": status,
                "is_connected": self._is_connected,
                "health_metrics": metrics,
                **kwargs,
            }

            # Record monitoring metric
            self._observability.record_metric(
                "plugin.connection_monitor.execution",
                1,
                "count",
                status=status,
            )

            return FlextResult.ok(monitor_data)

        except (ValueError, TypeError, AttributeError) as e:
            return FlextResult.fail(f"Connection monitor plugin failed: {e}")

    def _query_optimizer_plugin(
        self,
        sql: str | None = None,
        **kwargs: Any,  # noqa: ANN401
    ) -> FlextResult[dict[str, Any]]:
        """Built-in query optimization plugin."""
        try:
            if not sql:
                return FlextResult.fail("SQL query required for optimization")

            # Simple query analysis com type safety - refatoração DRY real
            suggestions: list[str] = []
            sql_upper = sql.upper()

            analysis = {
                "plugin_name": "oracle_query_optimizer",
                "timestamp": self._observability.get_current_timestamp(),
                "sql_length": len(sql),
                "has_joins": "JOIN" in sql_upper,
                "has_subqueries": sql_upper.count("SELECT") > 1,
                "suggestions": suggestions,
            }

            # Basic optimization suggestions
            if "SELECT *" in sql_upper:
                suggestions.append("Consider specifying columns instead of SELECT *")

            if "ORDER BY" in sql_upper and "LIMIT" not in sql_upper:
                suggestions.append("Consider adding ROWNUM limit for large result sets")

            if analysis["has_joins"] and "WHERE" not in sql_upper:
                suggestions.append(
                    "Consider adding WHERE clause to filter JOIN results",
                )

            # Record optimization metric
            self._observability.record_metric(
                "plugin.query_optimizer.execution",
                1,
                "count",
                suggestions_count=str(len(suggestions)),
            )

            return FlextResult.ok({**analysis, **kwargs})

        except (ValueError, TypeError, AttributeError) as e:
            return FlextResult.fail(f"Query optimizer plugin failed: {e}")

    # =============================================================================
    # ERROR HANDLING (Refactored to FlextDbOracleErrorHandler)
    # =============================================================================
    # Error handling moved to observability.FlextDbOracleErrorHandler for DRY

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

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: types.TracebackType | None,
    ) -> None:
        """Context manager exit."""
        self.disconnect()


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    "FlextDbOracleApi",
]
