"""Oracle Database API with clean delegation to services layer.

This API provides a clean interface to Oracle database operations
by delegating all work to the services layer while maintaining
type safety and proper error handling.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import contextlib
from collections.abc import Callable, Sequence
from typing import Self, cast, override

from flext_core import (
    FlextContainer,
    FlextContext,
    FlextDispatcher,
    FlextLogger,
    FlextResult,
    FlextService,
    FlextTypes,
    T,
)

from flext_db_oracle.config import FlextDbOracleConfig
from flext_db_oracle.constants import FlextDbOracleConstants
from flext_db_oracle.models import FlextDbOracleModels, FlextDbOracleModels as Models
from flext_db_oracle.services import FlextDbOracleServices

from . import dispatcher as oracle_dispatcher

logger = FlextLogger(__name__)


class FlextDbOracleApi(FlextService[FlextDbOracleConfig]):
    """Oracle Database API with complete flext-core integration.

    This API provides a unified interface to Oracle database operations,
    integrating with flext-core components for proper error handling,
    logging, service orchestration, and enterprise patterns.
    """

    @override
    def __init__(
        self,
        config: Models.OracleConfig,
        context_name: str | None = None,
    ) -> None:
        """Initialize API with Oracle configuration."""
        super().__init__()  # Initialize FlextService
        # Convert OracleConfig model to FlextDbOracleConfig settings
        self._oracle_config: FlextDbOracleConfig = self._convert_to_config(config)
        self._services: FlextDbOracleServices = FlextDbOracleServices(
            config=config, domain_events=[]
        )
        self._context_name = context_name or "oracle-api"
        self._logger = logger

        # Complete flext-core ecosystem integration
        self._container = FlextContainer.get_global()
        self._context = FlextContext()
        self._plugins: FlextTypes.Dict = {}
        self._dispatcher: FlextDispatcher | None = None

    @property
    def config(self) -> FlextDbOracleConfig:
        """Get the Oracle configuration."""
        return self._oracle_config

    def _convert_to_config(
        self, oracle_config: Models.OracleConfig
    ) -> FlextDbOracleConfig:
        """Convert OracleConfig model to FlextDbOracleConfig settings."""
        # Create a FlextDbOracleConfig from the OracleConfig model
        config = FlextDbOracleConfig()
        # Set the Oracle-specific attributes
        config.oracle_host = oracle_config.host
        config.oracle_port = oracle_config.port
        config.oracle_service_name = getattr(
            oracle_config, "service_name", oracle_config.name
        )
        config.oracle_username = oracle_config.username
        config.oracle_password = oracle_config.password
        config.oracle_database_name = oracle_config.name
        config.oracle_sid = getattr(oracle_config, "sid", "")
        return config

    def is_valid(self) -> bool:
        """Check if API configuration is valid."""
        try:
            return (
                self._oracle_config.oracle_port
                >= FlextDbOracleConstants.OracleNetwork.MIN_PORT
                and self._oracle_config.oracle_service_name is not None
            )
        except AttributeError:
            # Config object may be None or missing attributes
            return False

    @classmethod
    def from_config(cls, config: Models.OracleConfig) -> Self:
        """Create API instance from configuration."""
        return cls(config)

    def to_dict(self) -> FlextTypes.Dict:
        """Convert API instance to dictionary representation.

        Returns:
            dict["str", "object"]: Dictionary containing API state information.

        """
        return {
            "config": {
                "host": self._oracle_config.oracle_host,
                "port": self._oracle_config.oracle_port,
                "service_name": self._oracle_config.oracle_service_name,
                "username": self._oracle_config.oracle_username,
                # Note: not exposing password for security
            },
            "connected": "False",  # Would require connection check
            "plugin_count": len(self.plugins),
        }

    def _dispatch_enabled(self) -> bool:
        """Return True when dispatcher feature flag is active."""
        return FlextDbOracleConstants.FeatureFlags.dispatcher_enabled()

    def _ensure_dispatcher(self) -> FlextDispatcher | None:
        """Create dispatcher on-demand when the feature flag is enabled."""
        if not self._dispatch_enabled():
            return None
        if self._dispatcher is None:
            self._dispatcher = (
                oracle_dispatcher.FlextDbOracleDispatcher.build_dispatcher(
                    self._services,
                )
            )
        return self._dispatcher

    @property
    def services(self) -> FlextDbOracleServices:
        """Get the services instance."""
        return self._services

    @property
    def plugins(self) -> FlextTypes.Dict:
        """Get the plugins dictionary."""
        return self._plugins

    def get_dispatcher(self) -> FlextDispatcher | None:
        """Get the dispatcher instance."""
        return self._ensure_dispatcher()

    def get_services(self) -> FlextDbOracleServices:
        """Get the services instance."""
        return self._services

    def get_plugins(self) -> FlextTypes.Dict:
        """Get the plugins dictionary."""
        return self.plugins

    def dispatch_command(self, command: object) -> FlextResult[object] | None:
        """Dispatch a command through the shared dispatcher when available."""
        dispatcher = self._ensure_dispatcher()
        if dispatcher is None:
            return None

        dispatch_result: FlextResult[object] = dispatcher.dispatch(command)
        if dispatch_result.is_failure:
            return FlextResult[object].fail(
                dispatch_result.error or "Dispatcher execution failed",
            )

        payload = dispatch_result.unwrap()
        if isinstance(payload, FlextResult):
            return payload
        return FlextResult[object].ok(payload)

    def dispatch_or(
        self,
        command: object,
        fallback: Callable[[], FlextResult[T]],
    ) -> FlextResult[T]:
        """Dispatch command or execute fallback when dispatcher disabled."""
        dispatched = self.dispatch_command(command)
        if dispatched is not None:
            return cast("FlextResult[T]", dispatched)
        return fallback()

    # Connection Management
    def connect(self) -> FlextResult[FlextDbOracleApi]:
        """Connect to Oracle database.

        Returns:
            FlextResult[FlextDbOracleApi]: Success result with connected API instance.

        """
        # Use dispatcher if available, otherwise delegate to services
        dispatcher = self.get_dispatcher()
        if dispatcher is not None:
            dispatch_result = dispatcher.dispatch(
                oracle_dispatcher.FlextDbOracleDispatcher.ConnectCommand(),
            )
            if dispatch_result is not None:
                return cast("FlextResult[FlextDbOracleApi]", dispatch_result)

        result = self._services.connect()
        if result.is_success:
            return FlextResult[FlextDbOracleApi].ok(self)
        return cast("FlextResult[FlextDbOracleApi]", result)

    def disconnect(self) -> FlextResult[None]:
        """Disconnect from Oracle database.

        Returns:
            FlextResult[None]: Success result when disconnected.

        """
        dispatch_result = self.dispatch_command(
            oracle_dispatcher.FlextDbOracleDispatcher.DisconnectCommand(),
        )
        if dispatch_result is not None:
            return cast("FlextResult[None]", dispatch_result)

        return self._services.disconnect()

    def test_connection(self) -> FlextResult[bool]:
        """Test Oracle database connection.

        Returns:
            FlextResult[bool]: Success result with connection test status.

        """
        return self.dispatch_or(
            oracle_dispatcher.FlextDbOracleDispatcher.TestConnectionCommand(),
            self._services.test_connection,
        )

    @property
    def is_connected(self) -> bool:
        """Check if connected to the database."""
        return self._services.is_connected()

    # Query Operations
    def query(
        self,
        sql: str,
        parameters: FlextTypes.Dict | None = None,
    ) -> FlextResult[list[FlextTypes.Dict]]:
        """Execute a SELECT query and return all results.

        Args:
            sql: The SQL query to execute.
            parameters: Optional parameters for the query.

        Returns:
            FlextResult[list[FlextTypes.Dict]]: Success result with query results.

        """
        params = parameters or {}
        return self.dispatch_or(
            oracle_dispatcher.FlextDbOracleDispatcher.ExecuteQueryCommand(sql, params),
            lambda: self._services.execute_query(sql, params),
        )

    def query_one(
        self,
        sql: str,
        parameters: FlextTypes.Dict | None = None,
    ) -> FlextResult[FlextTypes.Dict | None]:
        """Execute a SELECT query and return first result or None.

        Args:
            sql: The SQL query to execute.
            parameters: Optional parameters for the query.

        Returns:
            FlextResult[dict | None]: Success result with first row or None.

        """
        params = parameters or {}
        return self.dispatch_or(
            oracle_dispatcher.FlextDbOracleDispatcher.FetchOneCommand(sql, params),
            lambda: self._services.fetch_one(sql, params),
        )

    def execute_sql(
        self,
        sql: str,
        parameters: FlextTypes.Dict | None = None,
    ) -> FlextResult[int]:
        """Execute an INSERT/UPDATE/DELETE statement and return rows affected.

        Args:
            sql: The SQL statement to execute.
            parameters: Optional parameters for the statement.

        Returns:
            FlextResult[int]: Success result with number of affected rows.

        """
        params = parameters or {}
        return self.dispatch_or(
            oracle_dispatcher.FlextDbOracleDispatcher.ExecuteStatementCommand(
                sql, params
            ),
            lambda: self._services.execute_statement(sql, params),
        )

    def execute_many(
        self,
        sql: str,
        parameters_list: Sequence[FlextTypes.Dict],
    ) -> FlextResult[int]:
        """Execute a statement multiple times with different parameters.

        Args:
            sql: The SQL statement to execute.
            parameters_list: List of parameter dictionaries.

        Returns:
            FlextResult[int]: Success result with total number of affected rows.

        """
        params_list: list[FlextTypes.Dict] = list(parameters_list)
        return self.dispatch_or(
            oracle_dispatcher.FlextDbOracleDispatcher.ExecuteManyCommand(
                sql, params_list
            ),
            lambda: self._services.execute_many(sql, params_list),
        )

    def execute_statement(
        self,
        sql: str | object,  # Accept both string and SQLAlchemy objects
        parameters: FlextTypes.Dict | None = None,
    ) -> FlextResult[int]:
        """Execute SQL statement directly and return affected rows.

        Args:
            sql: The SQL statement (string or SQLAlchemy object).
            parameters: Optional parameters for the statement.

        Returns:
            FlextResult[int]: Success result with number of affected rows.

        """
        try:
            # Handle SQLAlchemy objects by converting to string
            if hasattr(sql, "__str__") and not isinstance(sql, str):
                sql_text = str(sql)
            else:
                sql_text = str(sql)

            params = parameters or {}
            return self.dispatch_or(
                oracle_dispatcher.FlextDbOracleDispatcher.ExecuteStatementCommand(
                    sql_text, params
                ),
                lambda: self._services.execute_statement(sql_text, params),
            )
        except (AttributeError, TypeError, ValueError) as e:
            return FlextResult.fail(f"Statement execution failed: {e}")

    # Schema Introspection
    def get_schemas(self) -> FlextResult[FlextTypes.StringList]:
        """Get list of available schemas.

        Returns:
            FlextResult[list[str]]: Success result with list of schema names.

        """
        return self._services.get_schemas()

    def get_tables(
        self,
        schema: str | None = None,
    ) -> FlextResult[FlextTypes.StringList]:
        """Get list of tables in specified schema.

        Args:
            schema: Optional schema name to filter tables.

        Returns:
            FlextResult[list[str]]: Success result with list of table names.

        """
        result = self._services.get_tables(schema)
        if result.is_success:
            return FlextResult[FlextTypes.StringList].ok(result.value)
        return FlextResult[FlextTypes.StringList].fail(result.error or "Unknown error")

    def get_columns(
        self,
        table: str,
        schema: str | None = None,
    ) -> FlextResult[list[FlextTypes.Dict]]:
        """Get column information for specified table.

        Args:
            table: The table name.
            schema: Optional schema name.

        Returns:
            FlextResult[list[FlextTypes.Dict]]: Success result with column information.

        """
        result = self._services.get_columns(table, schema)
        if result.is_success:
            columns_data: list[FlextTypes.Dict] = [
                {
                    "name": col.name,
                    "data_type": col.data_type,
                    "nullable": col.nullable,
                    "default_value": col.default_value,
                }
                for col in result.value
            ]
            return FlextResult[list[FlextTypes.Dict]].ok(columns_data)
        return FlextResult[list[FlextTypes.Dict]].fail(result.error or "Unknown error")

    def get_table_metadata(
        self,
        table: str,
        schema: str | None = None,
    ) -> FlextResult[FlextTypes.Dict]:
        """Get comprehensive table metadata including columns and constraints.

        Args:
            table: The table name.
            schema: Optional schema name.

        Returns:
            FlextResult[FlextTypes.Dict]: Success result with table metadata.

        """
        return self._services.get_table_metadata(table, schema)

    def get_primary_keys(
        self,
        table: str,
        schema: str | None = None,
    ) -> FlextResult[FlextTypes.StringList]:
        """Get primary key column names for specified table.

        Args:
            table: The table name.
            schema: Optional schema name.

        Returns:
            FlextResult[list[str]]: Success result with primary key column names.

        """
        return self._services.get_primary_keys(table, schema)

    def convert_singer_type(
        self,
        singer_type: str | FlextTypes.StringList,
        format_hint: str | None = None,
    ) -> FlextResult[str]:
        """Convert Singer JSON Schema type to Oracle SQL type.

        Args:
            singer_type: Singer JSON Schema type definition.
            format_hint: Optional format hint for type conversion.

        Returns:
            FlextResult[str]: Oracle SQL type or error.

        """
        return self._services.convert_singer_type(singer_type, format_hint)

    def map_singer_schema(
        self,
        schema: FlextTypes.Dict,
    ) -> FlextResult[FlextTypes.StringDict]:
        """Map Singer JSON Schema to Oracle table schema.

        Args:
            schema: Singer JSON Schema definition.

        Returns:
            FlextResult[dict["str", "str"]]: Oracle table schema mapping or error.

        """
        return self._services.map_singer_schema(schema)

    # Transaction Management
    def transaction(self) -> FlextResult[object]:
        """Get a transaction context manager.

        Returns:
            FlextResult[object]: Transaction context manager or error.

        """
        try:
            transaction_context = self._services.transaction()
            return FlextResult.ok(transaction_context)
        except (AttributeError, RuntimeError, ValueError) as e:
            return FlextResult.fail(f"Transaction creation failed: {e}")

    # Utility Methods
    def optimize_query(self, sql: str) -> FlextResult[str]:
        """Optimize a SQL query for Oracle.

        Args:
            sql (str): The SQL query to optimize.

        Returns:
            FlextResult[str]: Optimized query or error.

        """
        try:
            optimized = " ".join(sql.split())
            return FlextResult.ok(optimized)
        except (AttributeError, ValueError, TypeError) as e:
            return FlextResult.fail(f"Query optimization failed: {e}")

    def get_observability_metrics(self) -> FlextResult[FlextTypes.Dict]:
        """Get observability metrics for the connection.

        Returns:
            FlextResult[dict["str", "object"]]: Observability metrics or error.

        """
        return self._services.get_metrics()

    # Configuration

    @classmethod
    def from_env(
        cls, prefix: str = "FLEXT_TARGET_ORACLE"
    ) -> FlextResult[FlextDbOracleApi]:
        """Create API instance from environment variables."""
        config_result = FlextDbOracleModels.OracleConfig.from_env(
            prefix.replace("FLEXT_TARGET_", ""),
        )
        if config_result.is_success:
            instance = cls.from_config(config_result.value)
            return FlextResult.ok(instance)
        return FlextResult.fail(
            f"Failed to load config from environment: {config_result.error}",
        )

    @classmethod
    def from_url(cls, database_url: str) -> FlextResult[FlextDbOracleApi]:
        """Create API instance from database URL."""
        config_result = FlextDbOracleModels.OracleConfig.from_url(database_url)
        if config_result.is_success:
            instance = cls.from_config(config_result.value)
            return FlextResult.ok(instance)
        return FlextResult.fail(f"Failed to parse database URL: {config_result.error}")

    # Plugin System
    def register_plugin(self, name: str, plugin: object) -> FlextResult[None]:
        """Register a plugin with the services layer.

        Args:
            name: The plugin name.
            plugin: The plugin object.

        Returns:
            FlextResult[None]: Success result when plugin is registered.

        """
        try:
            self._plugins[name] = plugin
            return FlextResult.ok(None)
        except (KeyError, AttributeError, TypeError) as e:
            return FlextResult.fail(f"Failed to register plugin '{name}': {e}")

    def unregister_plugin(self, name: str) -> FlextResult[None]:
        """Unregister a plugin from the services layer.

        Args:
            name: The plugin name to unregister.

        Returns:
            FlextResult[None]: Success result when plugin is unregistered.

        """
        try:
            if name in self._plugins:
                del self._plugins[name]
                return FlextResult.ok(None)
            return FlextResult.fail(f"Plugin '{name}' not found")
        except (KeyError, AttributeError) as e:
            return FlextResult.fail(f"Failed to unregister plugin '{name}': {e}")

    def get_plugin(self, name: str) -> FlextResult[object]:
        """Get a registered plugin by name.

        Args:
            name: The plugin name.

        Returns:
            FlextResult[object]: Success result with the plugin object.

        """
        try:
            if name in self._plugins:
                return FlextResult.ok(self._plugins[name])
            return FlextResult.fail(f"Plugin '{name}' not found")
        except (KeyError, AttributeError) as e:
            return FlextResult.fail(f"Failed to get plugin '{name}': {e}")

    def list_plugins(self) -> FlextResult[FlextTypes.StringList]:
        """List all registered plugin names.

        Returns:
            FlextResult[list[str]]: Success result with list of plugin names.

        """
        try:
            return FlextResult.ok(list(self._plugins.keys()))
        except (AttributeError, TypeError) as e:
            return FlextResult.fail(f"Failed to list plugins: {e}")

    # Additional methods demanded by tests and real usage
    def _execute_query_sql(
        self,
        sql: str,
    ) -> FlextResult[FlextDbOracleModels.QueryResult]:
        """Execute SQL query and return results as QueryResult."""
        try:
            result = self.dispatch_or(
                oracle_dispatcher.FlextDbOracleDispatcher.ExecuteQueryCommand(sql, {}),
                lambda: self._services.execute_query(sql),
            )
            if result.is_success:
                # Convert result data to proper format for QueryResult
                # If it's raw data, wrap it in QueryResult
                # Initialize variables
                rows_data: list[FlextTypes.List] = []
                columns: FlextTypes.StringList = []

                if isinstance(result.value, list) and result.value:
                    # Check first element to determine format
                    first_element = result.value[0]
                    if isinstance(first_element, dict):
                        # Convert list of dicts to list of lists
                        rows_data = [list(row.values()) for row in result.value]
                        columns = list(first_element.keys())
                    # Note: Only handling dict format for now -
                    # other formats can be added when needed

                query_result = FlextDbOracleModels.QueryResult(
                    query=sql,
                    columns=columns,
                    rows=rows_data,
                    row_count=len(result.value)
                    if isinstance(result.value, list)
                    else 0,
                    query_hash=None,
                    explain_plan=None,
                )
                return FlextResult.ok(query_result)
            return FlextResult.fail(result.error or "SQL execution failed")
        except Exception as e:
            return FlextResult.fail(f"SQL execution error: {e}")

    def get_health_status(self) -> FlextResult[FlextTypes.Dict]:
        """Get database connection health status.

        Returns:
            FlextResult[dict["str", "object"]]: Health status information or error.

        """
        try:
            # Delegate to services layer for health check
            status = {
                "connected": hasattr(self._services, "_connected")
                and getattr(self._services, "_connected", False),
                "host": self._config.host,
                "port": self._config.port,
                "service_name": self._config.service_name,
            }
            return FlextResult.ok(status)
        except Exception as e:
            return FlextResult.fail(f"Health check failed: {e}")

    @property
    def _connection(self) -> object | None:
        """Get connection object (delegates to services)."""
        if self._services.is_connected():
            return self._services
        return None

    @property
    def connection(self) -> object | None:
        """Get connection object - public interface."""
        return self._connection

    def __enter__(self) -> Self:
        """Context manager entry."""
        return self

    def __exit__(self, exc_type: object, exc_val: object, exc_tb: object) -> None:
        """Context manager exit - cleanup resources if needed."""
        if hasattr(self._services, "disconnect"):
            with contextlib.suppress(Exception):
                # Log cleanup attempt but suppress errors during context exit
                logger.debug("Attempting disconnect during context manager exit")
                self._services.disconnect()

    def execute(self) -> FlextResult[FlextTypes.Dict]:
        """Execute default domain service operation - return API status.

        Returns:
            FlextResult[dict["str", "object"]]: API status information or error.

        """
        try:
            return FlextResult.ok(self.to_dict())
        except Exception as e:
            return FlextResult.fail(f"API execution failed: {e}")

    @override
    def __repr__(self) -> str:
        """Return string representation of the API instance."""
        connection_status = "connected" if self.is_connected else "disconnected"
        return f"FlextDbOracleApi(host={self._config.host}, status={connection_status})"
