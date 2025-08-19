"""FLEXT DB Oracle API - Enterprise Oracle Database Integration Service.

This module provides the main application service for Oracle database operations,
implementing Clean Architecture patterns with SOLID principles. The API serves as
the primary entry point for Oracle database interactions within the FLEXT ecosystem.

Architecture:
    The module implements a layered architecture with clear separation of concerns:
    - FlextDbOracleApi: Main application service coordinating Oracle operations
    - OracleConnectionManager: Dedicated connection lifecycle management
    - OracleQueryExecutor: Specialized query execution with performance optimization

Key Components:
    - Enterprise-grade connection pooling with automatic retry logic
    - Type-safe query execution returning FlextResult[T] patterns
    - Comprehensive observability and performance monitoring integration
    - Plugin system for extensible Oracle-specific functionality
    - Singer ecosystem foundation for data pipeline integration

Example:
    Basic Oracle database operations:

    >>> from flext_db_oracle import FlextDbOracleApi, FlextDbOracleConfig
    >>> config = FlextDbOracleConfig.from_env().data  # FlextResult
    >>> api = FlextDbOracleApi(config)
    >>>
    >>> # Connect and execute query
    >>> with api.connect() as connected_api:
    ...     result = connected_api.query(
    ...         "SELECT * FROM employees WHERE dept_id = :dept", {"dept": 10}
    ...     )
    ...     if result.success:
    ...         print(f"Retrieved {result.value.row_count} employees")

Integration:
    - Built on flext-core foundation patterns (FlextResult, FlextContainer)
    - Integrates with flext-observability for monitoring and metrics
    - Provides base patterns for flext-tap-oracle and flext-target-oracle
    - Compatible with Meltano orchestration and Singer data pipelines

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import types
from time import perf_counter
from typing import Self, TypeVar, cast

from flext_core import (
    FlextContainer,
    FlextPlugin,
    FlextResult,
    get_logger,
)
from flext_observability import FlextHealthCheck

from flext_db_oracle.config import FlextDbOracleConfig
from flext_db_oracle.config_types import MergeStatementConfig
from flext_db_oracle.connection import CreateIndexConfig, FlextDbOracleConnection
from flext_db_oracle.observability import (
    FlextDbOracleObservabilityManager,
)
from flext_db_oracle.typings import TDbOracleQueryResult

T = TypeVar("T")
# =============================================================================
# REFACTORING: Extract Class - Connection Manager
# =============================================================================


class OracleConnectionManager:
    """Manages Oracle database connections using SOLID principles.

    SOLID REFACTORING: Single Responsibility - handles only connection lifecycle.
    Extracted from FlextDbOracleApi to reduce complexity.
    """

    def __init__(
        self,
        config: FlextDbOracleConfig,
        observability: FlextDbOracleObservabilityManager | None,
        context_name: str,
        retry_attempts: int = 3,
    ) -> None:
        """Initialize connection manager."""
        self._config = config
        self._observability = observability
        self._context_name = context_name
        self._retry_attempts = retry_attempts
        self._logger = get_logger(f"OracleConnectionManager.{context_name}")

        self._connection: FlextDbOracleConnection | None = None
        self._is_connected = False

    def _handle_error_with_logging(
        self,
        operation: str,
        exception: Exception,
    ) -> FlextResult[T]:
        """Handle errors with logging - DRY pattern for error handling."""
        error_msg: str = f"{operation}: {exception}"
        self._logger.error(error_msg)
        return FlextResult[object].fail(error_msg)

    def _handle_error_simple(
        self,
        operation: str,
        exception: Exception,
    ) -> FlextResult[T]:
        """Handle errors without logging - DRY pattern for simple error handling."""
        return FlextResult[object].fail(f"{operation}: {exception}")

    @property
    def is_connected(self) -> bool:
        """Check if connected to database."""
        return self._is_connected and self._connection is not None

    @property
    def connection(self) -> FlextDbOracleConnection | None:
        """Get active connection."""
        return self._connection

    def connect(self) -> FlextResult[None]:
        """Connect to Oracle database with retry logic."""
        if self.is_connected:
            self._logger.debug("Already connected to Oracle database")
            return FlextResult[object].ok(None)

        start_time = perf_counter()
        self._init_connection_attempt()

        # Execute retry loop using Template Method pattern
        error_result = self._execute_connection_with_retries(start_time)

        if error_result:
            return self._handle_connection_failure(error_result, start_time)

        self._logger.info("Successfully connected to Oracle database")
        return FlextResult[object].ok(None)

    def disconnect(self) -> FlextResult[None]:
        """Disconnect from Oracle database."""
        if not self.is_connected:
            return FlextResult[object].ok(None)

        try:
            if self._connection:
                disconnect_result = self._connection.close()
                if disconnect_result.is_failure:
                    self._logger.warning(
                        "Disconnect warning: %s",
                        disconnect_result.error,
                    )

            self._connection = None
            self._is_connected = False
            self._logger.info("Disconnected from Oracle database")
            return FlextResult[object].ok(None)

        except (OSError, ValueError, AttributeError, RuntimeError) as e:
            return self._handle_error_with_logging("Error during disconnect", e)

    def test_connection(self) -> FlextResult[bool]:
        """Test Oracle database connection."""
        if not self.is_connected:
            return FlextResult[object].fail("Not connected to database")

        try:
            # Simple query to test connection
            if self._connection:
                test_result = self._connection.execute_query("SELECT 1 FROM DUAL")
                return FlextResult[object].ok(test_result.success)
            return FlextResult[object].fail("No active connection")

        except (OSError, ValueError) as e:
            return self._handle_error_simple("Connection test failed", e)

    def _init_connection_attempt(self) -> None:
        """Initialize connection attempt metrics."""
        self._logger.info("Connecting to Oracle database")
        if self._observability:
            self._observability.record_metric("connection.attempts", 1, "count")

    def _execute_connection_with_retries(self, start_time: float) -> str | None:
        """Execute connection with retry logic using Template Method."""
        last_error = None

        for attempt in range(self._retry_attempts + 1):
            try:
                connection_result = self._attempt_single_connection(attempt)

                if connection_result.success and connection_result.data:
                    self._handle_successful_connection(
                        connection_result.data,
                        start_time,
                    )
                    return None  # Success

                last_error = connection_result.error or "Unknown connection error"
                self._record_connection_failure(attempt, last_error)

            except (OSError, ValueError, ConnectionError) as e:
                last_error = f"Connection attempt {attempt + 1} failed: {e}"
                self._record_connection_failure(attempt, last_error)

        return last_error

    def _attempt_single_connection(
        self,
        _attempt: int,
    ) -> FlextResult[FlextDbOracleConnection]:
        """Attempt single database connection."""
        connection = FlextDbOracleConnection(self._config)
        return connection.connect().map(lambda _: connection)

    def _handle_successful_connection(
        self,
        connection: FlextDbOracleConnection,
        start_time: float,
    ) -> None:
        """Handle successful connection establishment."""
        self._connection = connection
        self._is_connected = True

        duration_ms = (perf_counter() - start_time) * 1000
        if self._observability:
            self._observability.record_metric(
                "connection.duration_ms",
                duration_ms,
                "histogram",
            )
            self._observability.record_metric("connection.success", 1, "count")

    def _record_connection_failure(self, attempt: int, error: str) -> None:
        """Record connection failure metrics."""
        if self._observability:
            self._observability.record_metric("connection.failures", 1, "count")
        self._logger.warning("Connection attempt %d failed: %s", attempt + 1, error)

    def _handle_connection_failure(
        self,
        error: str,
        start_time: float,
    ) -> FlextResult[None]:
        """Handle final connection failure."""
        duration_ms = (perf_counter() - start_time) * 1000
        if self._observability:
            self._observability.record_metric(
                "connection.total_failure_duration_ms",
                duration_ms,
                "histogram",
            )

        error_msg = (
            f"Failed to connect after {self._retry_attempts + 1} attempts: {error}"
        )
        self._logger.error(error_msg)
        return FlextResult[object].fail(error_msg)


# =============================================================================
# REFACTORING: Helper Classes to Reduce Complexity
# =============================================================================


class ApiResponseFormatter:
    """Helper class for formatting API responses - REDUCES COMPLEXITY in API methods."""

    def __init__(self, logger: object) -> None:
        """Initialize response formatter."""
        self._logger = logger

    def format_health_status(self, health_check: object) -> dict[str, object]:
        """Format health check object to dict for API compatibility."""
        if not hasattr(health_check, "status"):
            return {"status": "unknown", "message": "Invalid health check object"}

        # Safe access to timestamp with proper typing
        timestamp_obj = getattr(health_check, "timestamp", None)
        timestamp_str = ""
        if timestamp_obj is not None:
            if hasattr(timestamp_obj, "isoformat"):
                timestamp_str = timestamp_obj.isoformat()
            else:
                timestamp_str = str(timestamp_obj)

        health_dict: dict[str, object] = {
            "status": getattr(health_check, "status", "unknown"),
            "timestamp": timestamp_str,
            "message": getattr(health_check, "message", "") or "",
            "metrics": getattr(health_check, "metrics", {}),
            "component": getattr(health_check, "component", "oracle"),
        }
        return health_dict

    def create_connection_status(
        self,
        *,
        connected: bool,
        query_success: bool,
        observability_active: bool,
        error: str | None = None,
    ) -> dict[str, object]:
        """Create standardized connection status response."""
        base_status: dict[str, object] = {
            "connected": connected,
            "query_success": query_success,
            "observability_active": observability_active,
            "metrics_collected": connected and query_success,
        }

        if connected and query_success:
            base_status["status"] = "healthy"
        elif connected:
            base_status["status"] = "degraded"
        else:
            base_status["status"] = "disconnected"

        if error:
            base_status["error"] = error

        return base_status


class ApiPluginManager:
    """Helper class for plugin management operations - ELIMINATES DUPLICATION."""

    def __init__(self, plugins: dict[str, object], plugin_platform: object) -> None:
        """Initialize plugin manager."""
        self._plugins = plugins
        self._plugin_platform = plugin_platform

    def try_get_complex_plugin(self, plugin_name: str) -> FlextResult[object] | None:
        """Try to get plugin from complex plugin platform."""
        if not hasattr(self._plugin_platform, "plugin_service"):
            return None

        service = self._plugin_platform.plugin_service
        if not hasattr(service, "registry"):
            return None

        registry = service.registry
        if not hasattr(registry, "get_plugin"):
            return None

        plugin = registry.get_plugin(plugin_name)
        if plugin is not None:
            return FlextResult[object].ok(plugin)
        return FlextResult[object].fail(f"Plugin {plugin_name} not found")

    def get_simple_plugin(self, plugin_name: str) -> FlextResult[object]:
        """Get plugin from simple plugin dictionary."""
        if plugin_name not in self._plugins:
            return FlextResult[object].fail(f"Plugin {plugin_name} not found")
        return FlextResult[object].ok(self._plugins[plugin_name])

    def try_list_complex_plugins(self) -> FlextResult[list[object]] | None:
        """Try to list plugins from complex plugin platform."""
        if not hasattr(self._plugin_platform, "plugin_service"):
            return None

        service = self._plugin_platform.plugin_service
        if not hasattr(service, "registry"):
            return None

        registry = service.registry
        if not hasattr(registry, "list_plugins"):
            return None

        try:
            plugins = registry.list_plugins()
            return FlextResult[object].ok(plugins)
        except Exception as e:
            return FlextResult[object].fail(f"Failed to list plugins: {e}")

    def register_plugin_simple(self, plugin: object) -> str:
        """Register plugin in simple dictionary using plugin info."""
        plugin_info = (
            plugin.get_info() if hasattr(plugin, "get_info") else {"name": "unknown"}
        )
        plugin_name = plugin_info.get("name", "unknown")
        self._plugins[str(plugin_name)] = plugin
        return str(plugin_name)

    def try_register_complex_plugin(self, plugin: object) -> FlextResult[None] | None:
        """Try to register plugin in complex platform."""
        if not hasattr(self._plugin_platform, "load_plugin"):
            return None
        load_result = self._plugin_platform.load_plugin(plugin)
        if load_result.is_failure:
            return FlextResult[object].fail(f"Failed to register plugin: {load_result.error}")
        return FlextResult[object].ok(None)

    def list_simple_plugins(self) -> FlextResult[list[object]]:
        """List plugins from simple dictionary."""
        return FlextResult[object].ok(list(self._plugins.values()))


class ApiConnectionValidator:
    """Helper class for connection validation - REDUCES COMPLEXITY in connection methods."""

    def __init__(self, logger: object) -> None:
        """Initialize connection validator."""
        self._logger = logger

    def validate_connection_manager(
        self,
        connection_manager: object | None,
        operation: str,
    ) -> FlextResult[None]:
        """Validate connection manager is available for operation."""
        if not connection_manager:
            return FlextResult[object].fail(f"No connection manager available for {operation}")
        return FlextResult[object].ok(None)

    def validate_connection_active(
        self,
        connection_manager: object,
        operation: str,
    ) -> FlextResult[None]:
        """Validate connection is active for operation."""
        if (
            not hasattr(connection_manager, "connection")
            or not connection_manager.connection
        ):
            return FlextResult[object].fail(f"No database connection available for {operation}")
        return FlextResult[object].ok(None)

    def validate_query_executor(
        self,
        query_executor: object | None,
        operation: str,
    ) -> FlextResult[None]:
        """Validate query executor is available for operation."""
        if not query_executor:
            return FlextResult[object].fail(f"No query executor available for {operation}")
        return FlextResult[object].ok(None)


# =============================================================================
# REFACTORING: Extract Class - Query Executor
# =============================================================================


class OracleQueryExecutor:
    """Executes Oracle database queries using SOLID principles.

    SOLID REFACTORING: Single Responsibility - handles only query execution.
    Extracted from FlextDbOracleApi to reduce complexity.
    """

    def __init__(
        self,
        connection_manager: OracleConnectionManager,
        observability: FlextDbOracleObservabilityManager | None,
        context_name: str,
    ) -> None:
        """Initialize query executor."""
        self._connection_manager = connection_manager
        self._observability = observability
        self._logger = get_logger(f"OracleQueryExecutor.{context_name}")

    def _handle_error_with_logging(
        self,
        operation: str,
        exception: Exception,
    ) -> FlextResult[T]:
        """Handle errors with logging - DRY pattern for error handling."""
        error_msg: str = f"{operation}: {exception}"
        self._logger.error(error_msg)
        return FlextResult[object].fail(error_msg)

    def execute_query(
        self,
        sql: str,
        params: dict[str, object] | None = None,
    ) -> FlextResult[TDbOracleQueryResult]:
        """Execute SQL query with parameters."""
        if not self._connection_manager.is_connected:
            return FlextResult[object].fail("Database not connected")

        connection = self._connection_manager.connection
        if not connection:
            return FlextResult[object].fail("No active database connection")

        try:
            start_time = perf_counter()

            # Execute query using connection
            raw_result = connection.execute_query(sql, params or {})

            # Record metrics
            duration_ms = (perf_counter() - start_time) * 1000
            if self._observability:
                self._observability.record_metric(
                    "query.duration_ms",
                    duration_ms,
                    "histogram",
                )

            if raw_result.is_failure:
                if self._observability:
                    self._observability.record_metric("query.failures", 1, "count")
                self._logger.warning("Query failed: %s", raw_result.error)
                return FlextResult[object].fail(raw_result.error or "Query execution failed")

            # Convert raw result to TDbOracleQueryResult
            raw_data = raw_result.data or []

            # Convert list to TDbOracleQueryResult (raw_data is always a list from connection layer)
            rows_list = [
                tuple(row) if isinstance(row, (list, tuple)) else (row,)
                for row in raw_data
            ]
            query_result = TDbOracleQueryResult.model_validate({
                "rows": rows_list,
                "columns": [],  # Column names would need to be extracted from cursor/metadata
                "row_count": len(rows_list),
                "execution_time_ms": duration_ms,
            })

            if self._observability:
                self._observability.record_metric("query.success", 1, "count")
            self._logger.debug("Query executed successfully in %.2fms", duration_ms)
            return FlextResult[object].ok(query_result)

        except (OSError, ValueError, AttributeError, RuntimeError, TypeError) as e:
            if self._observability:
                self._observability.record_metric("query.exceptions", 1, "count")
            return self._handle_error_with_logging("Query execution error", e)

    def execute_query_single(
        self,
        sql: str,
        params: dict[str, object] | None = None,
    ) -> FlextResult[dict[str, object] | None]:
        """Execute query expecting single result."""
        result = self.execute_query(sql, params)

        if not result.success:
            return FlextResult[object].fail(result.error or "Query failed")

        query_result = result.data
        if not query_result or not query_result.rows:
            return FlextResult[object].ok(None)

        # Convert first row from tuple to dict
        if query_result.rows and query_result.columns:
            first_row = query_result.rows[0]
            row_dict = dict(zip(query_result.columns, first_row, strict=False))
            return FlextResult[object].ok(row_dict)

        return FlextResult[object].ok(None)

    def execute_batch(
        self,
        operations: list[tuple[str, dict[str, object] | None]]
        | list[tuple[str, object]],
    ) -> FlextResult[list[TDbOracleQueryResult]]:
        """Execute batch of SQL operations."""
        results: list[TDbOracleQueryResult] = []
        # Normalize operations that might have generic object as params
        normalized_ops: list[tuple[str, dict[str, object] | None]] = []
        for sql, params in operations:
            if params is None or isinstance(params, dict):
                normalized_ops.append((sql, params))
            else:
                # Best-effort to coerce unexpected param types
                normalized_ops.append((sql, None))

        for step_num, (sql, params) in enumerate(normalized_ops, 1):
            result = self.execute_query(sql, params)

            # Stop on first failure for transaction consistency
            if not result.success:
                self._logger.error(
                    "Batch operation %d failed: %s",
                    step_num,
                    result.error,
                )
                return FlextResult[object].fail(
                    f"Batch operation {step_num} failed: {result.error}",
                )

            # Only append successful result data
            if result.data:
                results.append(result.data)

        return FlextResult[object].ok(results)


# =============================================================================
# REFACTORING: Simplified Main API Class
# =============================================================================


class FlextDbOracleApi:
    """Simplified Oracle API using SOLID composition patterns.

    SOLID REFACTORING: Reduced complexity by extracting specialized managers.
    Now focuses on API coordination and high-level operations.
    """

    def __init__(
        self,
        config: FlextDbOracleConfig | None = None,
        context_name: str = "oracle",
    ) -> None:
        """Initialize Oracle API with composition pattern."""
        self._context_name = context_name
        # Store container lazily to satisfy import position rules
        self._container = None
        self._logger = get_logger(f"FlextDbOracleApi.{context_name}")

        # Configuration
        self._config = config

        # Composed managers using Dependency Injection
        # Create observability manager with a container on demand

        self._container = FlextContainer()
        self._observability = FlextDbOracleObservabilityManager(
            self._container,
            self._context_name,
        )

        if config:
            self._connection_manager: OracleConnectionManager | None = (
                OracleConnectionManager(
                    config,
                    self._observability,
                    context_name,
                )
            )
            self._query_executor: OracleQueryExecutor | None = OracleQueryExecutor(
                self._connection_manager,
                self._observability,
                context_name,
            )
        else:
            self._connection_manager = None
            self._query_executor = None

        # Plugin system - using mock implementation for now
        self._plugins: dict[str, object] = {}
        self._plugin_platform = self._plugins  # Simple compatibility layer

        # Error handler for observability integration
        self._error_handler = self._observability

        # Helper classes to reduce complexity
        self._response_formatter = ApiResponseFormatter(self._logger)
        self._plugin_manager = ApiPluginManager(self._plugins, self._plugin_platform)
        self._connection_validator = ApiConnectionValidator(self._logger)

        # Initialize observability
        self._observability.initialize()

    # =============================================================================
    # Error Handling Methods (DRY Pattern)
    # =============================================================================

    def _handle_error_simple(
        self,
        operation: str,
        exception: Exception,
    ) -> FlextResult[T]:
        """Handle errors without logging - DRY pattern for simple error handling."""
        return FlextResult[object].fail(f"{operation}: {exception}")

    def _handle_error_with_logging(
        self,
        operation: str,
        exception: Exception,
    ) -> FlextResult[T]:
        """Handle errors with logging - DRY pattern for error handling."""
        error_msg: str = f"{operation}: {exception}"
        self._logger.error(error_msg)
        return FlextResult[object].fail(error_msg)

    # =============================================================================
    # Factory Methods (Dependency Injection Pattern)
    # =============================================================================

    @classmethod
    def _create_api_from_config_result(
        cls,
        config_result: FlextResult[FlextDbOracleConfig],
        context_name: str,
        logger: object,
        operation_name: str,
    ) -> Self:
        """SOLID REFACTORING: Extract Method to eliminate code duplication.

        DRY Pattern - Single source of truth for API creation from config result.
        """
        if config_result.is_failure:
            logger.error("Failed to load configuration: %s", config_result.error)
            config_error = f"Configuration error: {config_result.error}"
            raise ValueError(config_error)

        # data is non-None by API contract

        # SOLID FIX: Use operation_name to create more specific context
        full_context_name = f"{context_name}.{operation_name}"
        return cls(config_result.data, full_context_name)

    @classmethod
    def from_env(
        cls,
        env_prefix: str = "FLEXT_TARGET_ORACLE",
        context_name: str = "oracle",
    ) -> Self:
        """Create Oracle API from environment variables."""
        logger = get_logger(f"FlextDbOracleApi.{context_name}")
        logger.info("Loading Oracle configuration from environment")

        # Ensure single underscore separator regardless of provided prefix
        normalized_prefix = env_prefix.rstrip("_")
        config_result = FlextDbOracleConfig.from_env_with_result(
            f"{normalized_prefix}_",
        )
        return cls._create_api_from_config_result(
            config_result,
            context_name,
            logger,
            "environment",
        )

    # Backward-compatibility helpers expected by some tests
    @classmethod
    def from_config(cls, config: object) -> Self:
        """Create API directly from a configuration-like object.

        Accepts either FlextDbOracleConfig or a compatible object with
        Oracle connection attributes and constructs a proper config.
        """
        if isinstance(config, FlextDbOracleConfig):
            return cls(config, "oracle")

        # Try to coerce from a foreign config object (e.g., client-b config)
        try:
            cfg_dict = {
                "host": getattr(config, "host", "localhost"),
                "port": int(getattr(config, "port", 1521)),
                "username": getattr(config, "username", ""),
                "password": getattr(config, "password", ""),
                "service_name": getattr(config, "service_name", None)
                or getattr(config, "sid", None)
                or "ORCLPDB1",
            }
            coerced = FlextDbOracleConfig.model_validate(cfg_dict)
            return cls(coerced, "oracle")
        except Exception as e:
            msg = f"Invalid configuration provided: {e}"
            raise ValueError(msg) from e

    @classmethod
    def with_config(
        cls,
        config_dict: dict[str, object] | FlextDbOracleConfig | None = None,
        context_name: str = "oracle",
        **kwargs: object,
    ) -> Self:
        """Create Oracle API with configuration dictionary or keyword arguments."""
        if isinstance(config_dict, FlextDbOracleConfig):
            config = config_dict
        elif config_dict is not None:
            # REAL REFACTORING: Use model_validate for proper type handling
            config = FlextDbOracleConfig.model_validate(config_dict)
        else:
            # REAL REFACTORING: Use model_validate for proper type handling
            config = FlextDbOracleConfig.model_validate(kwargs)
        return cls(config, context_name)

    @classmethod
    def from_url(
        cls,
        url: str,
        context_name: str = "oracle",
    ) -> Self:
        """Create Oracle API from database URL."""
        logger = get_logger(f"FlextDbOracleApi.{context_name}")
        logger.info("Loading Oracle configuration from URL")

        config_result = FlextDbOracleConfig.from_url(url)
        return cls._create_api_from_config_result(
            config_result,
            context_name,
            logger,
            "URL",
        )

    # =============================================================================
    # Connection Management (Delegation Pattern)
    # =============================================================================

    def connect(self) -> Self:
        """Connect to Oracle database."""
        if not self._connection_manager:
            no_config_error = "No configuration provided for connection"
            raise ValueError(no_config_error)

        result = self._connection_manager.connect()
        if result.is_failure:
            raise ConnectionError(result.error or "Connection failed")

        return self

    def disconnect(self) -> Self:
        """Disconnect from Oracle database."""
        if self._connection_manager:
            self._connection_manager.disconnect()
        return self

    def test_connection(self) -> FlextResult[bool]:
        """Test Oracle database connection."""
        # Ensure connection is established for test environments without DB
        if not self._connection_manager:
            return FlextResult[object].fail("No connection manager available")
        if not self._connection_manager.is_connected:
            connect_result = self._connection_manager.connect()
            if connect_result.is_failure:
                return FlextResult[object].fail(connect_result.error or "Connection failed")
        return self._connection_manager.test_connection()

    def test_connection_with_observability(self) -> FlextResult[dict[str, object]]:
        """Test connection with observability metrics for CLI compatibility."""
        try:
            observability_active = self._observability.is_monitoring_active()

            # If not connected, return disconnected status using helper
            if not self.is_connected:
                status = self._response_formatter.create_connection_status(
                    connected=False,
                    query_success=False,
                    observability_active=observability_active,
                )
                return FlextResult[object].ok(status)

            test_result = self.test_connection()

            if test_result.success:
                status = self._response_formatter.create_connection_status(
                    connected=bool(test_result.data),
                    query_success=bool(test_result.data),
                    observability_active=observability_active,
                )
            else:
                status = self._response_formatter.create_connection_status(
                    connected=False,
                    query_success=False,
                    observability_active=observability_active,
                    error=test_result.error or "Connection test failed",
                )

            return FlextResult[object].ok(status)

        except (OSError, ValueError, TypeError, ConnectionError) as e:
            return self._handle_error_simple("Connection test failed", e)
        except Exception as e:
            return self._handle_error_simple("Connection test failed", e)

    @property
    def config(self) -> FlextDbOracleConfig | None:
        """Get Oracle configuration."""
        return self._config

    @property
    def connection(self) -> FlextDbOracleConnection | None:
        """Get active database connection."""
        if self._connection_manager:
            return self._connection_manager.connection
        return None

    @property
    def is_connected(self) -> bool:
        """Check if connected to database."""
        # Check test flag first for backward compatibility
        if hasattr(self, "_test_is_connected"):
            return bool(self._test_is_connected) and self._connection is not None

        # Check connection manager flag for backward compatibility - only if connection exists
        if (
            self._connection_manager
            and hasattr(self._connection_manager, "_is_connected")
            and self._connection_manager._is_connected
            and self._connection_manager.connection is not None
        ):
            return True

        return bool(
            self._connection_manager and self._connection_manager.is_connected,
        )

    @property
    def _is_connected(self) -> bool:
        """BACKWARD COMPATIBILITY: Use is_connected instead."""
        return self.is_connected

    @_is_connected.setter
    def _is_connected(self, value: bool) -> None:
        """BACKWARD COMPATIBILITY: Set connection status."""
        if self._connection_manager:
            # Access private member for backward compatibility
            self._connection_manager._is_connected = value
        else:
            # For tests - create a simple flag
            self.__dict__["_test_is_connected"] = value

    @property
    def _connection(self) -> FlextDbOracleConnection | None:
        """BACKWARD COMPATIBILITY: Use connection instead."""
        return self.connection

    @_connection.setter
    def _connection(self, value: FlextDbOracleConnection | None) -> None:
        """BACKWARD COMPATIBILITY: Set connection."""
        if self._connection_manager:
            # Access private member for backward compatibility
            self._connection_manager._connection = value

    @property
    def _retry_attempts(self) -> int:
        """BACKWARD COMPATIBILITY: Get retry attempts from connection manager."""
        if self._connection_manager:
            return getattr(self._connection_manager, "_retry_attempts", 3)
        return 3  # Default value

    # =============================================================================
    # Query Execution (Delegation Pattern)
    # =============================================================================

    def query(
        self,
        sql: str,
        params: dict[str, object] | None = None,
    ) -> FlextResult[TDbOracleQueryResult]:
        """Execute SQL query."""
        if not self._query_executor:
            return FlextResult[object].fail("No query executor available")

        return self._query_executor.execute_query(sql, params)

    def query_one(
        self,
        sql: str,
        params: dict[str, object] | None = None,
    ) -> FlextResult[tuple[object, ...] | None]:
        """Execute query expecting single result - delegates to connection."""
        if not self._connection_manager or not self._connection_manager.connection:
            return FlextResult[object].fail("No database connection available")

        # MYPY FIX: Convert object to proper tuple type
        result = self._connection_manager.connection.fetch_one(sql, params or {})
        if result.is_failure:
            return FlextResult[object].fail(result.error or "Query failed")

        # Safe conversion to tuple type
        if result.data is None:
            return FlextResult[object].ok(None)

        if isinstance(result.data, (tuple, list)):
            return FlextResult[object].ok(tuple(result.data))
        return FlextResult[object].ok((result.data,))

    def execute_batch(
        self,
        operations: list[tuple[str, dict[str, object] | None]],
    ) -> FlextResult[list[TDbOracleQueryResult]]:
        """Execute batch of SQL operations."""
        if not self._query_executor:
            return FlextResult[object].fail("No query executor available")

        return self._query_executor.execute_batch(operations)

    # =============================================================================
    # Context Manager (Template Method Pattern)
    # =============================================================================

    def __enter__(self) -> Self:
        """Enter context manager - auto connect if not already connected."""
        if not self.is_connected:
            return self.connect()
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: types.TracebackType | None,
    ) -> None:
        """Exit context manager - auto disconnect."""
        self.disconnect()

    def transaction(self) -> _TransactionContextManager:
        """Start transaction context manager - delegates to connection."""
        if not self._connection_manager or not self._connection_manager.connection:
            msg = "No database connection available for transaction"
            raise ValueError(msg)

        return _TransactionContextManager(self, self._connection_manager.connection)

    # =============================================================================
    # Health Check (Delegation Pattern)
    # =============================================================================

    def get_health_check(self) -> FlextResult[FlextHealthCheck]:
        """Get health check status."""
        if not self.is_connected:
            return self._observability.create_health_check(
                status="unhealthy",
                message="Database not connected",
                metrics={"connected": False, "config_valid": self._config is not None},
            )

        # Test connection using API query method (for better testability)
        try:
            health_test = self.query("SELECT 1 FROM DUAL")
            if health_test.success:
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
                message=f"Database connection issues: {health_test.error}",
                metrics={
                    "connected": True,
                    "config_valid": True,
                    "last_query_success": False,
                },
            )
        except (OSError, ValueError, TypeError, ConnectionError) as e:
            return self._observability.create_health_check(
                status="degraded",
                message=f"Database connection issues: {e}",
                metrics={
                    "connected": True,
                    "config_valid": True,
                    "last_query_success": False,
                },
            )
        except Exception as e:
            return self._observability.create_health_check(
                status="degraded",
                message=f"Database connection issues: {e}",
                metrics={
                    "connected": True,
                    "config_valid": True,
                    "last_query_success": False,
                },
            )

    # =============================================================================
    # Plugin Management (Delegation Pattern)
    # =============================================================================

    def register_plugin(self, plugin: FlextPlugin) -> FlextResult[None]:
        """Register a plugin with the platform using ApiPluginManager helper."""
        try:
            # Use helper class to reduce complexity - delegates to ApiPluginManager
            complex_result = self._plugin_manager.try_register_complex_plugin(plugin)
            if complex_result is not None:
                return complex_result

            # Fall back to simple registration via helper
            self._plugin_manager.register_plugin_simple(plugin)
            return FlextResult[object].ok(None)
        except (TypeError, ValueError, AttributeError, RuntimeError) as e:
            return self._handle_error_simple("Plugin registration error", e)
        except Exception as e:
            return self._handle_error_simple("Plugin registration error", e)

    def unregister_plugin(self, plugin_name: str) -> FlextResult[None]:
        """Unregister a plugin from the platform."""
        if plugin_name in self._plugins:
            del self._plugins[plugin_name]
            return FlextResult[object].ok(None)
        return FlextResult[object].fail(f"Plugin {plugin_name} not found")

    def get_plugin(self, plugin_name: str) -> FlextResult[FlextPlugin]:
        """Get a registered plugin using ApiPluginManager helper.

        SOLID REFACTORING: Delegated to ApiPluginManager to reduce complexity.
        """
        try:
            # Delegate to helper class - reduces complexity in main API class
            complex_result = self._plugin_manager.try_get_complex_plugin(plugin_name)
            if complex_result is not None:
                if complex_result.success and complex_result.data:
                    return FlextResult[object].ok(cast("FlextPlugin", complex_result.data))
                return cast("FlextResult[FlextPlugin]", complex_result)

            # Fall back to simple plugin retrieval via helper
            simple_result = self._plugin_manager.get_simple_plugin(plugin_name)
            if simple_result.success and simple_result.data:
                return FlextResult[object].ok(cast("FlextPlugin", simple_result.data))
            return cast("FlextResult[FlextPlugin]", simple_result)

        except (TypeError, ValueError, AttributeError, RuntimeError, Exception) as e:
            return self._handle_error_simple("Failed to get plugin", e)

    def execute_plugin(
        self,
        plugin_name: str,
        **kwargs: dict[str, object],
    ) -> FlextResult[dict[str, object]]:
        """Execute a registered plugin.

        SOLID REFACTORING: Reduced from 6 returns to 3 using Guard Clauses
        and Extract Method patterns.
        """
        plugin_result = self.get_plugin(plugin_name)
        if plugin_result.is_failure:
            return FlextResult[object].fail(plugin_result.error or "Plugin not found")

        return self._execute_plugin_with_validation(
            plugin_result.data,
            plugin_name,
            **kwargs,
        )

    def list_plugins(self) -> FlextResult[list[FlextPlugin]]:
        """List all registered plugins using ApiPluginManager helper.

        SOLID REFACTORING: Delegated to ApiPluginManager to reduce complexity.
        """
        try:
            # Delegate to helper class - reduces complexity in main API class
            complex_result = self._plugin_manager.try_list_complex_plugins()
            if complex_result is not None:
                if complex_result.success and complex_result.data:
                    return FlextResult[object].ok(
                        [cast("FlextPlugin", p) for p in complex_result.data],
                    )
                return cast("FlextResult[list[FlextPlugin]]", complex_result)

            # Fall back to simple plugin list via helper
            simple_result = self._plugin_manager.list_simple_plugins()
            if simple_result.success and simple_result.data:
                return FlextResult[object].ok(
                    [cast("FlextPlugin", p) for p in simple_result.data],
                )
            return cast("FlextResult[list[FlextPlugin]]", simple_result)

        except (TypeError, ValueError, AttributeError, RuntimeError, Exception) as e:
            return self._handle_error_simple("Failed to list plugins", e)

    def _execute_plugin_with_validation(
        self,
        plugin: FlextPlugin | None,
        plugin_name: str,
        **kwargs: dict[str, object],
    ) -> FlextResult[dict[str, object]]:
        """SOLID REFACTORING: Extract Method for plugin execution with validation."""
        if plugin is None:
            return FlextResult[object].fail(f"Plugin {plugin_name} data is None")

        # Check if plugin has a callable config
        callable_obj = (
            getattr(plugin.config, "callable_obj", None)
            if hasattr(plugin, "config")
            else None
        )
        if callable_obj is None:
            return FlextResult[object].fail(f"Plugin {plugin_name} is not callable")

        # Execute the plugin
        try:
            result = callable_obj(**kwargs)
            return FlextResult[object].ok(result)
        except (TypeError, ValueError, AttributeError, RuntimeError, Exception) as e:
            return self._handle_error_simple("Plugin execution failed", e)

    def _try_list_complex_plugins(self) -> FlextResult[list[FlextPlugin]] | None:
        """SOLID REFACTORING: Extract Method for complex plugin platform listing."""
        if hasattr(self._plugin_platform, "plugin_service"):
            if self._plugin_platform.plugin_service is None:
                return FlextResult[object].fail("Plugin service is not available")

            if hasattr(self._plugin_platform.plugin_service, "registry"):
                registry = self._plugin_platform.plugin_service.registry
                if hasattr(registry, "list_plugins"):
                    return FlextResult[object].ok(registry.list_plugins())
            else:
                # No registry attribute - return empty list
                return FlextResult[object].ok([])
        return None

    # =============================================================================
    # Extended API Methods (Required by CLI)
    # =============================================================================

    def query_with_timing(
        self,
        sql: str,
        params: dict[str, object] | None = None,
    ) -> FlextResult[TDbOracleQueryResult]:
        """Execute query with timing information.

        SOLID REFACTORING: Reduced complexity from 19 to <5 using Extract Method pattern.
        """
        if not self._query_executor:
            return FlextResult[object].fail("No query executor available")

        start_time = perf_counter()
        result = self._query_executor.execute_query(sql, params)
        duration_ms = (perf_counter() - start_time) * 1000

        if result.success:
            timing_result = self._create_timing_result(result.data, duration_ms)
            return FlextResult[object].ok(timing_result)

        return FlextResult[object].fail(result.error or "Query execution failed")

    def _create_timing_result(
        self,
        data: object,
        duration_ms: float,
    ) -> TDbOracleQueryResult:
        """SOLID REFACTORING: Extract Method for TDbOracleQueryResult creation."""
        # Handle None data case
        if data is None:
            return TDbOracleQueryResult.model_validate({
                "rows": [],
                "columns": [],
                "row_count": 0,
                "execution_time_ms": duration_ms,
            })

        return TDbOracleQueryResult.model_validate({
            "rows": data.rows if hasattr(data, "rows") else [],
            "columns": data.columns if hasattr(data, "columns") else [],
            "row_count": data.row_count
            if hasattr(data, "row_count")
            else len(data.rows)
            if hasattr(data, "rows")
            else 0,
            "execution_time_ms": duration_ms,
        })

    def get_schemas(self) -> FlextResult[list[str]]:
        """Get list of database schemas."""
        if not self._connection_manager or not self._connection_manager.connection:
            return FlextResult[object].fail("No database connection available")

        result = self._connection_manager.connection.get_schemas()
        if result.is_failure:
            return result
        return FlextResult[object].ok(result.data or [])

    def get_tables(self, schema: str | None = None) -> FlextResult[list[str]]:
        """Get list of tables in schema."""
        if not self._connection_manager or not self._connection_manager.connection:
            return FlextResult[object].fail("No database connection available")

        result = self._connection_manager.connection.get_table_names(schema)
        if result.is_failure:
            return result
        return FlextResult[object].ok(result.data or [])

    def get_columns(
        self,
        table_name: str,
        schema: str | None = None,
    ) -> FlextResult[list[dict[str, object]]]:
        """Get column information for specified table."""
        if not self._connection_manager or not self._connection_manager.connection:
            return FlextResult[object].fail("No database connection available")

        result = self._connection_manager.connection.get_column_info(table_name, schema)
        if result.is_failure:
            return result
        return FlextResult[object].ok(result.data or [])

    def optimize_query(self, sql: str) -> FlextResult[dict[str, object]]:
        """Analyze and provide optimization suggestions for SQL query."""
        # Basic SQL analysis - in real implementation would use Oracle's EXPLAIN PLAN
        suggestions: list[str] = []
        analysis = {
            "sql_length": len(sql),
            "has_joins": "JOIN" in sql.upper(),
            "has_subqueries": "(" in sql and "SELECT" in sql.upper(),
            "suggestions": suggestions,
        }

        # Simple heuristic suggestions
        sql_upper = sql.upper()
        if "SELECT *" in sql_upper:
            suggestions.append("Avoid SELECT * - specify only needed columns")
        if "WHERE" not in sql_upper and "SELECT" in sql_upper:
            suggestions.append("Consider adding WHERE clause to limit results")
        max_query_length = 1000
        if len(sql) > max_query_length:
            suggestions.append(
                "Consider breaking down complex query into smaller parts",
            )

        return FlextResult[object].ok(analysis)

    def get_health_status(self) -> FlextResult[dict[str, object]]:
        """Get database health status."""
        # Delegate to existing health check method
        health_check_result = self.get_health_check()
        if health_check_result.success and health_check_result.data:
            # Convert FlextHealthCheck to dict for compatibility
            health_data = health_check_result.data
            health_dict: dict[str, object] = {
                "status": health_data.status,
                "timestamp": health_data.timestamp.isoformat(),
                "message": health_data.message or "",
                "metrics": health_data.metrics,
                "component": health_data.component,
            }
            return FlextResult[object].ok(health_dict)
        return FlextResult[object].fail(health_check_result.error or "Health check failed")

    def build_select(
        self,
        table_name: str,
        columns: list[str] | None = None,
        conditions: dict[str, object] | None = None,
        schema: str | None = None,
    ) -> FlextResult[str]:
        """Build SELECT SQL query - delegates to connection."""
        if not self._connection_manager or not self._connection_manager.connection:
            return FlextResult[object].fail("No database connection available")

        return self._connection_manager.connection.build_select(
            table_name,
            columns,
            conditions,
            schema,
        )

    def map_singer_schema(
        self,
        singer_schema: dict[str, object],
    ) -> FlextResult[dict[str, object]]:
        """Map Singer schema to Oracle schema - delegates to connection."""
        if not self._connection_manager or not self._connection_manager.connection:
            return FlextResult[object].fail("No database connection available")

        result = self._connection_manager.connection.map_singer_schema(singer_schema)
        # REAL REFACTORING: Properly convert dict[str, str] to dict[str, object]
        if result.success and result.data:
            converted_data: dict[str, object] = dict(result.data)
            return FlextResult[object].ok(converted_data)
        # If failure, create properly typed failure result
        return FlextResult[object].fail(result.error or "Schema mapping failed")

    def get_primary_keys(
        self,
        table_name: str,
        schema: str | None = None,
    ) -> FlextResult[list[str]]:
        """Get primary key columns for specified table - delegates to connection."""
        if not self._connection_manager or not self._connection_manager.connection:
            return FlextResult[object].fail("No database connection available")

        result = self._connection_manager.connection.get_primary_key_columns(
            table_name,
            schema,
        )
        if result.is_failure:
            return result
        return FlextResult[object].ok(result.data or [])

    def get_observability_metrics(self) -> FlextResult[dict[str, object]]:
        """Get observability metrics from the API."""
        try:
            metrics = {
                "context": self._context_name,
                "is_connected": self.is_connected,
                "config_valid": self._config is not None,
                "monitoring_active": self._observability.is_monitoring_active(),
            }
            return FlextResult[object].ok(metrics)
        except (TypeError, ValueError, AttributeError, RuntimeError) as e:
            return self._handle_error_simple("Failed to get metrics", e)
        except Exception as e:
            return self._handle_error_simple("Failed to get metrics", e)

    def execute_connection_monitor(
        self,
        **kwargs: dict[str, object],
    ) -> FlextResult[dict[str, object]]:
        """Execute connection monitor plugin - convenience method."""
        return self.execute_plugin("oracle_connection_monitor", **kwargs)

    def create_table_ddl(
        self,
        table_name: str,
        columns: list[dict[str, object]],
        schema: str | None = None,
    ) -> FlextResult[str]:
        """Create table DDL statement - delegates to connection."""
        if not self._connection_manager or not self._connection_manager.connection:
            return FlextResult[object].fail("No database connection available")

        return self._connection_manager.connection.create_table_ddl(
            table_name,
            columns,
            schema,
        )

    def drop_table_ddl(
        self,
        table_name: str,
        schema: str | None = None,
    ) -> FlextResult[str]:
        """Create drop table DDL statement - delegates to connection."""
        if not self._connection_manager or not self._connection_manager.connection:
            return FlextResult[object].fail("No database connection available")

        return self._connection_manager.connection.drop_table_ddl(table_name, schema)

    def get_table_metadata(
        self,
        table_name: str,
        schema: str | None = None,
    ) -> FlextResult[dict[str, object]]:
        """Get table metadata - delegates to connection."""
        if not self._connection_manager or not self._connection_manager.connection:
            return FlextResult[object].fail("No database connection available")

        return self._connection_manager.connection.get_table_metadata(
            table_name,
            schema,
        )

    def convert_singer_type(
        self,
        singer_type: str | list[str],
        format_hint: str | None = None,
    ) -> FlextResult[str]:
        """Convert Singer type to Oracle type - delegates to connection."""
        if not self._connection_manager or not self._connection_manager.connection:
            return FlextResult[object].fail("No database connection available")

        return self._connection_manager.connection.convert_singer_type(
            singer_type,
            format_hint,
        )

    def execute_ddl(self, sql: str) -> FlextResult[None]:
        """Execute DDL statement - BACKWARD COMPATIBILITY for flext-target-oracle.

        This method is required by flext-target-oracle and other dependent projects.
        Uses query method internally for DDL execution.
        """
        if not self._query_executor:
            return FlextResult[object].fail("No query executor available")

        # Execute DDL using query method (DDL statements don't return data)
        result = self._query_executor.execute_query(sql, None)

        if result.success:
            return FlextResult[object].ok(None)
        return FlextResult[object].fail(result.error or "DDL execution failed")

    # =============================================================================
    # DML Statement Builders (Delegated to Connection)
    # =============================================================================

    def build_insert_statement(
        self,
        table_name: str,
        columns: list[str],
        schema_name: str | None = None,
        returning_columns: list[str] | None = None,
        hints: list[str] | None = None,
    ) -> FlextResult[str]:
        """Build INSERT statement with Oracle-specific features."""
        if not self._connection_manager or not self._connection_manager.connection:
            return FlextResult[object].fail("No database connection available")

        return self._connection_manager.connection.build_insert_statement(
            table_name,
            columns,
            schema_name,
            returning_columns,
            hints,
        )

    def build_update_statement(
        self,
        table_name: str,
        set_columns: list[str],
        where_columns: list[str],
        schema_name: str | None = None,
        returning_columns: list[str] | None = None,
    ) -> FlextResult[str]:
        """Build UPDATE statement with Oracle-specific features."""
        if not self._connection_manager or not self._connection_manager.connection:
            return FlextResult[object].fail("No database connection available")

        return self._connection_manager.connection.build_update_statement(
            table_name,
            set_columns,
            where_columns,
            schema_name,
            returning_columns,
        )

    def build_merge_statement(
        self,
        config: MergeStatementConfig,
    ) -> FlextResult[str]:
        """Build Oracle MERGE statement for upsert operations - SOLID refactoring."""
        if not self._connection_manager or not self._connection_manager.connection:
            return FlextResult[object].fail("No database connection available")

        return self._connection_manager.connection.build_merge_statement(config)

    def build_delete_statement(
        self,
        table_name: str,
        where_columns: list[str],
        schema_name: str | None = None,
    ) -> FlextResult[str]:
        """Build DELETE statement."""
        if not self._connection_manager or not self._connection_manager.connection:
            return FlextResult[object].fail("No database connection available")

        return self._connection_manager.connection.build_delete_statement(
            table_name,
            where_columns,
            schema_name,
        )

    def build_create_index_statement(
        self,
        config: CreateIndexConfig,
    ) -> FlextResult[str]:
        """Build CREATE INDEX statement with Oracle-specific features - SOLID refactoring."""
        if not self._connection_manager or not self._connection_manager.connection:
            return FlextResult[object].fail("No database connection available")

        return self._connection_manager.connection.build_create_index_statement(config)


# =============================================================================
# Transaction Context Manager (Support Class)
# =============================================================================


class _TransactionContextManager:
    """Internal transaction context manager."""

    def __init__(
        self,
        api: FlextDbOracleApi,
        connection: FlextDbOracleConnection,
    ) -> None:
        self.api = api
        self.connection = connection
        self._transaction_context: object | None = None

    def __enter__(self) -> FlextDbOracleApi:
        self._transaction_context = self.connection.transaction()
        if hasattr(self._transaction_context, "__enter__"):
            self._transaction_context.__enter__()
        return self.api

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: types.TracebackType | None,
    ) -> None:
        if self._transaction_context and hasattr(self._transaction_context, "__exit__"):
            self._transaction_context.__exit__(exc_type, exc_val, exc_tb)


# =============================================================================
# Factory Functions (Dependency Injection)
# =============================================================================


def create_oracle_api(
    config: FlextDbOracleConfig | None = None,
    context_name: str = "oracle",
) -> FlextDbOracleApi:
    """Create Oracle API instance."""
    return FlextDbOracleApi(config, context_name)


def create_oracle_api_from_env(
    env_prefix: str = "FLEXT_TARGET_ORACLE_",
    context_name: str = "oracle",
) -> FlextDbOracleApi:
    """Create Oracle API from environment."""
    return FlextDbOracleApi.from_env(env_prefix, context_name)


__all__: list[str] = [
    "FlextDbOracleApi",
    "OracleConnectionManager",
    "OracleQueryExecutor",
    "create_oracle_api",
    "create_oracle_api_from_env",
]
