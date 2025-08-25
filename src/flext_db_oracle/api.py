"""FLEXT DB Oracle API - Enterprise Oracle Database Integration Service.

This module provides the main application service for Oracle database operations,
implementing Clean Architecture patterns with SOLID principles. The API serves as
the primary entry point for Oracle database interactions within the FLEXT ecosystem.

Architecture:
    The module implements the Flext[Area][Module] pattern with a single consolidated
    FlextDbOracleApi class containing all Oracle database functionality as internal
    methods, following SOLID principles and Clean Architecture patterns.

Key Components:
    - Enterprise-grade connection pooling with automatic retry logic
    - Type-safe query execution returning FlextResult[T] patterns
    - Comprehensive observability and performance monitoring integration
    - Plugin system for extensible Oracle-specific functionality
    - Singer ecosystem foundation for data pipeline integration

Example:
    Basic Oracle database operations:

    >>> from flext_db_oracle import FlextDbOracleApi, FlextDbOracleConfig
    >>> config = FlextDbOracleConfig.from_env().value  # FlextResult
    >>> api = FlextDbOracleApi(config)
    >>>
    >>> # Connect and execute query
    >>> with api.connect() as connected_api:
    ...     result = connected_api.query(
    ...         "SELECT * FROM employees WHERE dept_id = :dept", {"dept": 10}
    ...     )
    ...     if result.success:
    ...         query_result = result.value
    ...         print(f"Retrieved {query_result.row_count} employees")
    ...     else:
    ...         print(f"Query failed: {result.error}")

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
from typing import Self

from flext_core import (
    FlextContainer,
    FlextDomainService,
    FlextResult,
    get_logger,
)

from flext_db_oracle.config import FlextDbOracleConfig
from flext_db_oracle.connection import FlextDbOracleConnection
from flext_db_oracle.models import FlextDbOracleQueryResult
from flext_db_oracle.observability import (
    FlextDbOracleObservabilityManager,
)
from flext_db_oracle.typings import (
    has_get_info_method,
    is_dict_like,
    is_plugin_like,
)

# Constants for Oracle column metadata parsing
MIN_COLUMN_FIELDS = 4  # Required fields: name, type, length, nullable


def _is_valid_plugin(obj: object) -> bool:
    """Type guard to check if object has plugin-like attributes."""
    return is_plugin_like(obj)


def _get_plugin_info(plugin: object) -> dict[str, object]:
    """Type-safe way to get plugin info."""
    if has_get_info_method(plugin):
        try:
            get_info_method = getattr(plugin, "get_info", None)
            if get_info_method and callable(get_info_method):
                info = get_info_method()
                if is_dict_like(info):
                    return {str(k): str(v) for k, v in info.items()}
        except (TypeError, AttributeError):
            pass

    # Fallback: extract basic info from attributes if plugin-like
    if is_plugin_like(plugin):
        return {
            "name": getattr(plugin, "name", "unknown"),
            "version": getattr(plugin, "version", "unknown"),
            "type": type(plugin).__name__,
        }

    return {"name": "unknown", "version": "unknown", "type": type(plugin).__name__}


# =============================================================================
# FLEXT[AREA][MODULE] PATTERN - Oracle Database API
# =============================================================================


class FlextDbOracleApi(FlextDomainService[FlextDbOracleQueryResult]):
    """Oracle Database API following Flext[Area][Module] pattern.

    Single class inheriting from FlextDomainService with all Oracle database
    functionality as internal methods, following SOLID principles,
    PEP8, Python 3.13+, and FLEXT structural patterns.

    This class consolidates all Oracle database API functionality
    into a single entry point with internal organization.
    """

    def __init__(
        self,
        config: FlextDbOracleConfig | None = None,
        context_name: str = "oracle",
    ) -> None:
        """Initialize Oracle API with consolidated functionality."""
        self._context_name = context_name
        self._container = FlextContainer()
        self._logger = get_logger(f"FlextDbOracleApi.{context_name}")

        # Configuration
        self._config = config

        # Internal state for consolidated functionality
        self._connection: FlextDbOracleConnection | None = None
        self._is_connected = False
        self._retry_attempts = 3

        # Plugin system (consolidated from ApiPluginManager)
        self._plugins: dict[str, object] = {}

        # Observability manager
        self._observability = FlextDbOracleObservabilityManager(
            self._container,
            self._context_name,
        )

    # =============================================================================
    # Connection Management (consolidated from OracleConnectionManager)
    # =============================================================================

    def _handle_error_with_logging(
        self,
        operation: str,
        exception: Exception,
    ) -> FlextResult[None]:
        """Handle errors with logging - DRY pattern for error handling."""
        error_msg: str = f"{operation}: {exception}"
        self._logger.error(error_msg)
        return FlextResult[None].fail(error_msg)

    def _handle_error_simple(
        self,
        operation: str,
        exception: Exception,
    ) -> FlextResult[None]:
        """Handle errors without logging - DRY pattern for simple error handling."""
        return FlextResult[None].fail(f"{operation}: {exception}")

    @property
    def is_connected(self) -> bool:
        """Check if connected to database."""
        return self._is_connected and self._connection is not None

    @property
    def connection(self) -> FlextDbOracleConnection | None:
        """Get active connection."""
        return self._connection

    @property
    def config(self) -> FlextDbOracleConfig | None:
        """Get configuration."""
        return self._config

    def _init_connection_attempt(self) -> None:
        """Initialize connection attempt."""
        if self._config is None:
            msg = "Configuration is required for connection"
            raise ValueError(msg)

        self._connection = FlextDbOracleConnection(self._config)

    def _execute_connection_with_retries(
        self, _start_time: float
    ) -> FlextResult[None] | None:
        """Execute connection with retry logic."""
        for attempt in range(self._retry_attempts):
            try:
                if self._connection:
                    connect_result = self._connection.connect()
                    if connect_result.is_success:
                        self._is_connected = True
                        return None  # Success
                    self._logger.warning(
                        f"Connection attempt {attempt + 1} failed: {connect_result.error}"
                    )
                    if attempt == self._retry_attempts - 1:
                        return FlextResult[None].fail(f"Connection failed: {connect_result.error}")
            except Exception as e:
                self._logger.warning(f"Connection attempt {attempt + 1} failed: {e}")
                if attempt == self._retry_attempts - 1:
                    return FlextResult[None].fail(
                        f"Connection failed after {self._retry_attempts} attempts: {e}"
                    )

        return FlextResult[None].fail("Connection failed after all retry attempts")

    def _handle_connection_failure(
        self, error_result: FlextResult[None], start_time: float
    ) -> FlextResult[None]:
        """Handle connection failure."""
        self._connection = None
        self._is_connected = False
        elapsed_ms = (perf_counter() - start_time) * 1000
        error_msg = f"Connection failed after {elapsed_ms:.2f}ms: {error_result.error}"
        self._logger.error(error_msg)
        return FlextResult[None].fail(error_msg)

    def connect(self) -> FlextResult[Self]:
        """Connect to Oracle database with retry logic."""
        if self.is_connected:
            self._logger.debug("Already connected to Oracle database")
            return FlextResult[Self].ok(self)

        start_time = perf_counter()
        self._init_connection_attempt()

        # Execute retry loop using Template Method pattern
        error_result = self._execute_connection_with_retries(start_time)

        if error_result:
            self._handle_connection_failure(error_result, start_time)
            return FlextResult[Self].fail(error_result.error or "Connection failed")

        self._logger.info("Successfully connected to Oracle database")
        return FlextResult[Self].ok(self)

    def disconnect(self) -> FlextResult[None]:
        """Disconnect from Oracle database."""
        if not self.is_connected:
            return FlextResult[None].ok(None)

        try:
            if self._connection:
                disconnect_result = self._connection.close()
                # Modern FlextResult pattern: Check failure status directly
                if disconnect_result.is_failure:
                    self._logger.warning(
                        "Disconnect warning: %s",
                        disconnect_result.error or "Unknown disconnect error",
                    )

            self._connection = None
            self._is_connected = False
            self._logger.info("Disconnected from Oracle database")
            return FlextResult[None].ok(None)

        except (OSError, ValueError, AttributeError, RuntimeError) as e:
            return self._handle_error_with_logging("Error during disconnect", e)

    def test_connection(self) -> FlextResult[bool]:
        """Test Oracle database connection."""
        if not self.is_connected:
            return FlextResult[bool].fail("Not connected to database")

        try:
            # Simple query to test connection
            if self._connection:
                test_result = self._connection.execute_query("SELECT 1 FROM DUAL")
                if test_result.is_success:
                    return FlextResult[bool].ok(data=True)
                return FlextResult[bool].fail(
                    f"Connection test failed: {test_result.error}"
                )
            return FlextResult[bool].fail("No connection available")

        except Exception as e:
            return FlextResult[bool].fail(f"Connection test error: {e}")

    # =============================================================================
    # Query Execution (consolidated from OracleQueryExecutor)
    # =============================================================================

    def _validate_query_params(
        self, sql: str
    ) -> FlextResult[None]:
        """Validate query parameters."""
        if not sql or not sql.strip():
            return FlextResult[None].fail("SQL query cannot be empty")

        return FlextResult[None].ok(None)

    def _execute_query_with_metrics(
        self,
        sql: str,
        params: dict[str, object] | None = None,
        _method_name: str = "query",
    ) -> FlextResult[FlextDbOracleQueryResult]:
        """Execute query with performance metrics."""
        if not self.is_connected or not self._connection:
            return FlextResult[FlextDbOracleQueryResult].fail(
                "Not connected to database"
            )

        # Validate parameters
        validation_result = self._validate_query_params(sql)
        if validation_result.is_failure:
            return FlextResult[FlextDbOracleQueryResult].fail(
                validation_result.error or "Validation failed"
            )

        try:
            start_time = perf_counter()

            # Execute query
            query_result = self._connection.execute_query(sql, params)

            execution_time_ms = (perf_counter() - start_time) * 1000

            if query_result.is_success:
                # Create FlextDbOracleQueryResult
                result_data = query_result.value
                if hasattr(result_data, "fetchall"):
                    rows = result_data.fetchall()
                    columns = (
                        list(result_data.keys()) if hasattr(result_data, "keys") else []
                    )
                else:
                    rows = result_data if isinstance(result_data, list) else []
                    columns = []

                oracle_result = FlextDbOracleQueryResult(
                    columns=columns,
                    rows=rows,
                    row_count=len(rows) if isinstance(rows, list) else 0,
                    execution_time_ms=execution_time_ms,
                )

                self._logger.debug(f"Query executed in {execution_time_ms:.2f}ms")
                return FlextResult[FlextDbOracleQueryResult].ok(oracle_result)
            return FlextResult[FlextDbOracleQueryResult].fail(
                query_result.error or "Query execution failed"
            )

        except Exception as e:
            return FlextResult[FlextDbOracleQueryResult].fail(
                f"Query execution error: {e}"
            )

    def query(
        self,
        sql: str,
        params: dict[str, object] | None = None,
    ) -> FlextResult[FlextDbOracleQueryResult]:
        """Execute SQL query and return results."""
        return self._execute_query_with_metrics(sql, params, "query")

    def query_one(
        self,
        sql: str,
        params: dict[str, object] | None = None,
    ) -> FlextResult[dict[str, object] | None]:
        """Execute SQL query and return first row."""
        query_result = self.query(sql, params)

        if query_result.is_failure:
            return FlextResult[dict[str, object] | None].fail(
                query_result.error or "Query failed"
            )

        oracle_result = query_result.value
        if oracle_result.row_count > 0 and oracle_result.rows:
            # Convert first row tuple to dictionary using column names
            first_row = oracle_result.rows[0]
            if oracle_result.columns:
                row_dict = dict(zip(oracle_result.columns, first_row, strict=False))
                return FlextResult[dict[str, object] | None].ok(row_dict)

        return FlextResult[dict[str, object] | None].ok(None)

    def execute_sql(
        self,
        sql: str,
        params: dict[str, object] | None = None,
    ) -> FlextResult[int]:
        """Execute SQL statement and return affected rows count."""
        if not self.is_connected or not self._connection:
            return FlextResult[int].fail("Not connected to database")

        # Validate parameters
        validation_result = self._validate_query_params(sql)
        if validation_result.is_failure:
            return FlextResult[int].fail(validation_result.error or "Validation failed")

        try:
            execute_result = self._connection.execute(sql, params)

            if execute_result.is_success:
                # Extract affected rows count from list[int] result
                if isinstance(execute_result.value, list) and execute_result.value:
                    # For DML operations, connection returns list[int] with row counts
                    affected_rows = execute_result.value[0] if isinstance(execute_result.value[0], int) else 0
                else:
                    affected_rows = 0
                return FlextResult[int].ok(affected_rows)
            return FlextResult[int].fail(execute_result.error or "Execution failed")

        except Exception as e:
            return FlextResult[int].fail(f"Execution error: {e}")

    def execute_many(
        self,
        sql: str,
        params_list: list[dict[str, object]],
    ) -> FlextResult[int]:
        """Execute SQL statement multiple times with different parameters."""
        if not self.is_connected or not self._connection:
            return FlextResult[int].fail("Not connected to database")

        if not sql or not sql.strip():
            return FlextResult[int].fail("SQL query cannot be empty")

        try:
            total_affected = 0

            for params in params_list:
                execute_result = self.execute_sql(sql, params)
                if execute_result.is_failure:
                    return FlextResult[int].fail(
                        f"Batch execution failed: {execute_result.error}"
                    )

                total_affected += execute_result.value

            return FlextResult[int].ok(total_affected)

        except Exception as e:
            return FlextResult[int].fail(f"Batch execution error: {e}")

    # =============================================================================
    # Schema Operations
    # =============================================================================

    def get_schemas(self) -> FlextResult[list[str]]:
        """Get list of database schemas."""
        sql = """
        SELECT DISTINCT username
        FROM all_users
        ORDER BY username
        """

        query_result = self.query(sql)
        if query_result.is_failure:
            return FlextResult[list[str]].fail(
                query_result.error or "Failed to get schemas"
            )

        oracle_result = query_result.value
        schemas = [str(row[0]) for row in oracle_result.rows if row]
        return FlextResult[list[str]].ok(schemas)

    def get_tables(self, schema: str | None = None) -> FlextResult[list[str]]:
        """Get list of tables in schema."""
        if schema:
            sql = """
            SELECT table_name
            FROM all_tables
            WHERE owner = :schema
            ORDER BY table_name
            """
            params: dict[str, object] | None = {"schema": schema.upper()}
        else:
            sql = """
            SELECT table_name
            FROM user_tables
            ORDER BY table_name
            """
            params = None

        query_result = self.query(sql, params)
        if query_result.is_failure:
            return FlextResult[list[str]].fail(
                query_result.error or "Failed to get tables"
            )

        oracle_result = query_result.value
        tables = [str(row[0]) for row in oracle_result.rows if row]
        return FlextResult[list[str]].ok(tables)

    def get_columns(
        self, table_name: str, schema: str | None = None
    ) -> FlextResult[list[dict[str, object]]]:
        """Get column information for a table."""
        params: dict[str, object]
        if schema:
            sql = """
            SELECT column_name, data_type, data_length, nullable
            FROM all_tab_columns
            WHERE table_name = :table_name AND owner = :schema
            ORDER BY column_id
            """
            params = {"table_name": table_name.upper(), "schema": schema.upper()}
        else:
            sql = """
            SELECT column_name, data_type, data_length, nullable
            FROM user_tab_columns
            WHERE table_name = :table_name
            ORDER BY column_id
            """
            params = {"table_name": table_name.upper()}

        query_result = self.query(sql, params)
        if query_result.is_failure:
            return FlextResult[list[dict[str, object]]].fail(
                query_result.error or "Failed to get columns"
            )

        oracle_result = query_result.value
        columns = []

        for row in oracle_result.rows:
            if len(row) >= MIN_COLUMN_FIELDS:
                column_info = {
                    "column_name": str(row[0]),
                    "data_type": str(row[1]),
                    "data_length": row[2],
                    "nullable": str(row[3]) == "Y",
                }
                columns.append(column_info)

        return FlextResult[list[dict[str, object]]].ok(columns)

    # =============================================================================
    # Plugin Management (consolidated from ApiPluginManager)
    # =============================================================================

    def register_plugin(self, name: str, plugin: object) -> FlextResult[None]:
        """Register a plugin."""
        if not name or not name.strip():
            return FlextResult[None].fail("Plugin name cannot be empty")

        if not _is_valid_plugin(plugin):
            return FlextResult[None].fail("Invalid plugin object")

        self._plugins[name] = plugin
        self._logger.info(f"Registered plugin: {name}")
        return FlextResult[None].ok(None)

    def unregister_plugin(self, name: str) -> FlextResult[None]:
        """Unregister a plugin."""
        if name in self._plugins:
            del self._plugins[name]
            self._logger.info(f"Unregistered plugin: {name}")
            return FlextResult[None].ok(None)

        return FlextResult[None].fail(f"Plugin not found: {name}")

    def list_plugins(self) -> FlextResult[list[dict[str, object]]]:
        """List all registered plugins."""
        if not self._plugins:
            return FlextResult[list[dict[str, object]]].fail(
                "Plugin listing returned empty"
            )

        plugin_list = []
        for name, plugin in self._plugins.items():
            plugin_info = _get_plugin_info(plugin)
            plugin_info["registered_name"] = name
            plugin_list.append(plugin_info)

        return FlextResult[list[dict[str, object]]].ok(plugin_list)

    def get_plugin(self, name: str) -> FlextResult[object]:
        """Get a specific plugin by name."""
        if name in self._plugins:
            return FlextResult[object].ok(self._plugins[name])

        return FlextResult[object].fail(f"Plugin not found: {name}")

    # =============================================================================
    # Utility Methods (consolidated from ApiResponseFormatter and others)
    # =============================================================================

    def optimize_query(self, sql: str) -> FlextResult[dict[str, object]]:
        """Provide query optimization suggestions."""
        if not sql or not sql.strip():
            return FlextResult[dict[str, object]].fail("SQL query cannot be empty")

        suggestions = {
            "original_query": sql,
            "suggestions": [
                "Consider using bind variables for better performance",
                "Add appropriate indexes for frequently queried columns",
                "Use EXPLAIN PLAN to analyze query execution",
            ],
            "optimized": False,
        }

        return FlextResult[dict[str, object]].ok(suggestions)

    def get_observability_metrics(self) -> FlextResult[dict[str, object]]:
        """Get observability metrics."""
        metrics: dict[str, object] = {
            "connection_status": "connected" if self.is_connected else "disconnected",
            "context_name": self._context_name,
            "plugin_count": len(self._plugins),
            "config_loaded": self._config is not None,
        }

        return FlextResult[dict[str, object]].ok(metrics)

    # =============================================================================
    # Class Methods (Factory Pattern)
    # =============================================================================

    @classmethod
    def from_env(cls, context_name: str = "oracle") -> FlextResult[Self]:
        """Create API instance from environment variables."""
        try:
            config_result = FlextDbOracleConfig.from_env_with_result()
            if config_result.is_failure:
                return FlextResult[Self].fail(
                    f"Failed to load config from environment: {config_result.error}"
                )

            if config_result.is_success:
                api = cls(config_result.value, context_name)
                return FlextResult[Self].ok(api)
            return FlextResult[Self].fail(f"Config result failed: {config_result.error}")

        except Exception as e:
            return FlextResult[Self].fail(f"Failed to create API from environment: {e}")

    @classmethod
    def from_config(
        cls, config: FlextDbOracleConfig, context_name: str = "oracle"
    ) -> Self:
        """Create API instance from configuration."""
        return cls(config, context_name)

    @classmethod
    def with_config(cls, config: FlextDbOracleConfig) -> Self:
        """Create API instance with specific configuration."""
        return cls(config)

    @classmethod
    def from_url(cls, url: str, context_name: str = "oracle") -> FlextResult[Self]:
        """Create API instance from database URL."""
        try:
            config_result = FlextDbOracleConfig.from_url(url)
            if config_result.is_failure:
                return FlextResult[Self].fail(
                    f"Failed to parse URL: {config_result.error}"
                )

            if config_result.is_success:
                api = cls(config_result.value, context_name)
                return FlextResult[Self].ok(api)
            return FlextResult[Self].fail(f"Config URL parsing failed: {config_result.error}")

        except Exception as e:
            return FlextResult[Self].fail(f"Failed to create API from URL: {e}")

    # =============================================================================
    # Context Managers
    # =============================================================================

    def __enter__(self) -> Self:
        """Context manager entry."""
        connect_result = self.connect()
        if connect_result.is_failure:
            msg = f"Failed to connect: {connect_result.error}"
            raise RuntimeError(msg)
        return connect_result.value

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: types.TracebackType | None,
    ) -> None:
        """Context manager exit."""
        disconnect_result = self.disconnect()
        if disconnect_result.is_failure:
            self._logger.warning(f"Disconnect warning: {disconnect_result.error}")

    def transaction(self) -> _TransactionContextManager:
        """Start a transaction context."""
        if not self.is_connected or not self._connection:
            msg = "Not connected to database"
            raise RuntimeError(msg)

        return _TransactionContextManager(self, self._connection)

    # =============================================================================
    # Domain Service Implementation
    # =============================================================================

    def execute(self) -> FlextResult[FlextDbOracleQueryResult]:
        """Execute domain service operation (FlextDomainService requirement)."""
        # Execute Oracle-specific health check query (SELECT 1 FROM DUAL)
        health_check_result = self.test_connection()

        if health_check_result.is_failure:
            return FlextResult[FlextDbOracleQueryResult].fail(
                f"Domain operation failed: {health_check_result.error}"
            )

        # Execute domain-specific Oracle query to validate full functionality
        oracle_health_query = (
            "SELECT 'Oracle Database Service Operational' as status FROM DUAL"
        )
        return self.query(oracle_health_query)

    def __repr__(self) -> str:
        """Return string representation of FlextDbOracleApi."""
        if self.config is None:
            return "FlextDbOracleApi(config=None)"
        return f"FlextDbOracleApi(host={self.config.host}, port={self.config.port}, service_name={self.config.service_name})"


# =============================================================================
# Transaction Context Manager (Internal Support)
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
            exit_method = getattr(self._transaction_context, "__exit__", None)
            if exit_method and callable(exit_method):
                exit_method(exc_type, exc_val, exc_tb)


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
    context_name: str = "oracle",
) -> FlextDbOracleApi:
    """Create Oracle API from environment."""
    result = FlextDbOracleApi.from_env(context_name)
    if result.is_failure:
        msg = f"Failed to create API from environment: {result.error}"
        raise ValueError(msg)
    return result.value


# Export API - ONLY single class and factory functions
__all__: list[str] = [
    "FlextDbOracleApi",
    "create_oracle_api",
    "create_oracle_api_from_env",
]
