"""Oracle Database API with complete FLEXT ecosystem integration.

This API provides a unified interface to Oracle database operations
following FLEXT patterns with complete flext-core integration.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import contextlib
from collections.abc import Sequence
from typing import Self, override

from flext_core import (
    FlextBus,
    FlextContainer,
    FlextContext,
    FlextResult,
    FlextService,
    FlextTypes,
)

from flext_db_oracle.config import FlextDbOracleConfig
from flext_db_oracle.constants import FlextDbOracleConstants
from flext_db_oracle.dispatcher import FlextDbOracleDispatcher
from flext_db_oracle.models import FlextDbOracleModels
from flext_db_oracle.services import FlextDbOracleServices


class FlextDbOracleApi(FlextService):
    """Oracle Database API with complete flext-core integration.

    This API provides a unified interface to Oracle database operations,
    integrating with flext-core components for proper error handling,
    logging, service orchestration, and enterprise patterns.

    Architecture:
    - Extends FlextService for domain service patterns
    - Uses FlextResult railway pattern for error handling
    - Integrates FlextContainer, FlextContext, FlextBus for enterprise features
    - Delegates to FlextDbOracleServices for Oracle operations
    - Optional FlextDispatcher integration for CQRS patterns
    """

    @override
    def __init__(
        self,
        config: FlextDbOracleConfig,
        context_name: str | None = None,
    ) -> None:
        """Initialize API with Oracle configuration and complete flext-core integration."""
        # Configuration management - use FlextDbOracleConfig directly
        self._oracle_config = config

        # Initialize FlextService with config
        super().__init__(config=self._oracle_config)

        # Core services initialization
        self._services = FlextDbOracleServices(config=self._oracle_config)

        # Context and naming
        self._context_name = context_name or "oracle-api"

        # Complete flext-core ecosystem integration
        self._container = FlextContainer.get_global()
        self._context = FlextContext()
        self._bus = FlextBus()
        # Logger will be initialized lazily via the parent class property

        # Optional dispatcher for CQRS patterns
        self._dispatcher = FlextDbOracleDispatcher.build_dispatcher(
            self._services, bus=self._bus
        )

        # Plugin system
        self._plugins: FlextTypes.Dict = {}

    @property
    def oracle_config(self) -> FlextDbOracleConfig:
        """Get the Oracle configuration."""
        return self._oracle_config

    @property
    def config(self) -> FlextDbOracleConfig:
        """Get the Oracle configuration (overrides base class)."""
        return self._oracle_config

    def is_valid(self) -> bool:
        """Check if API configuration is valid."""
        try:
            return (
                self._oracle_config.port
                >= FlextDbOracleConstants.OracleNetwork.MIN_PORT
                and self._oracle_config.service_name is not None
            )
        except AttributeError:
            return False

    @classmethod
    def from_config(cls, config: FlextDbOracleConfig) -> Self:
        """Create API instance from configuration."""
        return cls(config)

    @classmethod
    def from_env(cls, prefix: str = "ORACLE_") -> FlextResult[Self]:
        """Create API instance from environment variables.

        Args:
            prefix: Environment variable prefix (default: "ORACLE_")

        Returns:
            FlextResult[Self]: API instance or error.

        """
        try:
            config_result = FlextDbOracleConfig.from_env(prefix)
            if config_result.is_failure:
                return FlextResult[Self].fail(
                    f"Config creation failed: {config_result.error}"
                )

            config = config_result.unwrap()
            return FlextResult[Self].ok(cls(config))
        except Exception as e:
            return FlextResult[Self].fail(f"API creation from environment failed: {e}")

    def to_dict(self) -> FlextTypes.Dict:
        """Convert API instance to dictionary representation."""
        return {
            "config": {
                "host": self._oracle_config.host,
                "port": self._oracle_config.port,
                "service_name": self._oracle_config.service_name,
                "username": self._oracle_config.username,
            },
            "connected": self.is_connected,
            "plugin_count": len(self._plugins),
            "dispatcher_enabled": self._dispatcher is not None,
        }

    @property
    def services(self) -> FlextDbOracleServices:
        """Get the services instance."""
        return self._services

    @property
    def plugins(self) -> FlextTypes.Dict:
        """Get the plugins dictionary."""
        return self._plugins

    # Connection Management
    def connect(self) -> FlextResult[FlextDbOracleApi]:
        """Connect to Oracle database."""
        self.logger.info(
            "Connecting to Oracle database",
            extra={"host": self._oracle_config.host},
        )

        return self._services.connect().map(lambda _: self)

    def disconnect(self) -> FlextResult[None]:
        """Disconnect from Oracle database."""
        self.logger.info("Disconnecting from Oracle database")
        return self._services.disconnect()

    def test_connection(self) -> FlextResult[bool]:
        """Test Oracle database connection."""
        return self._services.test_connection()

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
        """Execute a SELECT query and return all results."""
        params = parameters or {}
        self.logger.debug("Executing query", query_length=len(sql))

        return self._services.execute_query(sql, params)

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
        return self._services.fetch_one(sql, params)

    def execute_sql(
        self,
        sql: str,
        parameters: FlextTypes.Dict | None = None,
    ) -> FlextResult[int]:
        """Execute an INSERT/UPDATE/DELETE statement and return rows affected."""
        params = parameters or {}
        self.logger.debug(
            "Executing SQL statement", extra={"statement_length": len(sql)}
        )

        return self._services.execute_statement(sql, params)

    def execute_many(
        self,
        sql: str,
        parameters_list: Sequence[FlextTypes.Dict],
    ) -> FlextResult[int]:
        """Execute a statement multiple times with different parameters."""
        params_list: list[FlextTypes.Dict] = list(parameters_list)
        self.logger.debug(
            "Executing bulk statement", extra={"batch_size": len(params_list)}
        )

        return self._services.execute_many(sql, params_list)

    def execute_statement(
        self,
        sql: str | object,
        parameters: FlextTypes.Dict | None = None,
    ) -> FlextResult[int]:
        """Execute SQL statement directly and return affected rows."""
        try:
            sql_text = str(sql) if not isinstance(sql, str) else sql
            params = parameters or {}

            return self._services.execute_statement(sql_text, params)
        except Exception as e:
            return FlextResult.fail(f"Statement execution failed: {e}")

    # Schema Introspection
    def get_schemas(self) -> FlextResult[FlextTypes.StringList]:
        """Get list of available schemas."""
        return self._services.get_schemas()

    def get_tables(
        self, schema: str | None = None
    ) -> FlextResult[FlextTypes.StringList]:
        """Get list of tables in specified schema."""
        return self._services.get_tables(schema)

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
            FlextResult[FlextTypes.StringList]: Success result with primary key column names.

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
            FlextResult[FlextTypes.StringList]: Success result with list of plugin names.

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
            result = self._services.execute_query(sql)
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
                    # Note: Only handling dict[str, object] format for now -
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
                "host": self._oracle_config.host,
                "port": self._oracle_config.port,
                "service_name": self._oracle_config.service_name,
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

    def _dispatch_enabled(self) -> bool:
        """Check if dispatcher is enabled."""
        return self._dispatcher is not None

    def __enter__(self) -> Self:
        """Context manager entry."""
        return self

    def __exit__(self, exc_type: object, exc_val: object, exc_tb: object) -> None:
        """Context manager exit - cleanup resources if needed."""
        if hasattr(self._services, "disconnect"):
            with contextlib.suppress(Exception):
                # Log cleanup attempt but suppress errors during context exit
                self.logger.debug("Attempting disconnect during context manager exit")
                self._services.disconnect()

    def execute(self) -> FlextResult[FlextDbOracleConfig]:
        """Execute default domain service operation - return config.

        Returns:
            FlextResult[FlextDbOracleConfig]: Configuration instance or error.

        """
        try:
            return FlextResult.ok(self._oracle_config)
        except Exception as e:
            return FlextResult.fail(f"API execution failed: {e}")

    @override
    def __repr__(self) -> str:
        """Return string representation of the API instance."""
        connection_status = "connected" if self.is_connected else "disconnected"
        return f"FlextDbOracleApi(host={self._oracle_config.host}, status={connection_status})"
