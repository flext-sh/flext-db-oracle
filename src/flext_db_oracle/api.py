"""Oracle Database API with clean delegation to services layer.

This API provides a clean interface to Oracle database operations
by delegating all work to the services layer while maintaining
type safety and proper error handling.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import contextlib
import logging
from collections.abc import Callable, Sequence
from typing import Self, TypeVar, cast

from flext_core import FlextConstants, FlextDispatcher, FlextModels, FlextResult
from flext_db_oracle.constants import FlextDbOracleConstants
from flext_db_oracle.models import FlextDbOracleModels
from flext_db_oracle.services import FlextDbOracleServices

from . import dispatcher as oracle_dispatcher

logger = logging.getLogger(__name__)
T = TypeVar("T")


class _ConnectionHelper:
    """Helper class for connection management operations."""

    def __init__(self, api: FlextDbOracleApi) -> None:
        self._api = api

    def _connect(self) -> FlextResult[FlextDbOracleApi]:
        """Connect to Oracle database.

        Returns:
            FlextResult[FlextDbOracleApi]: Success result with connected API instance.

        """
        dispatch_result = self._api._dispatch_command(
            oracle_dispatcher.FlextDbOracleDispatcher.ConnectCommand(),
        )
        if dispatch_result is not None:
            if dispatch_result.is_success:
                return FlextResult.ok(self._api)
            return FlextResult.fail(
                dispatch_result.error or "Connection failed",
            )

        result = self._api._services.connect()
        if result.is_success:
            return FlextResult.ok(self._api)
        return FlextResult.fail(f"Connection failed: {result.error}")

    def _disconnect(self) -> FlextResult[None]:
        """Disconnect from Oracle database.

        Returns:
            FlextResult[None]: Success result when disconnected.

        """
        dispatch_result = self._api._dispatch_command(
            oracle_dispatcher.FlextDbOracleDispatcher.DisconnectCommand(),
        )
        if dispatch_result is not None:
            return cast("FlextResult[None]", dispatch_result)

        return self._api._services.disconnect()

    def _test_connection(self) -> FlextResult[bool]:
        """Test Oracle database connection.

        Returns:
            FlextResult[bool]: Success result with connection test status.

        """
        return self._api._dispatch_or(
            oracle_dispatcher.FlextDbOracleDispatcher.TestConnectionCommand(),
            self._api._services.test_connection,
        )

    @property
    def _is_connected(self) -> bool:
        """Check if connected to the database."""
        return self._api._services.is_connected()


class _QueryHelper:
    """Helper class for query operations."""

    def __init__(self, api: FlextDbOracleApi) -> None:
        self._api = api

    def _query(
        self,
        sql: str,
        parameters: dict[str, object] | None = None,
    ) -> FlextResult[list[dict[str, object]]]:
        """Execute a SELECT query and return all results.

        Returns:
            FlextResult[list[dict[str, object]]]: Success result with query results.

        """
        params = parameters or {}
        return self._api._dispatch_or(
            oracle_dispatcher.FlextDbOracleDispatcher.ExecuteQueryCommand(sql, params),
            lambda: self._api._services.execute_query(sql, params),
        )

    def _query_one(
        self,
        sql: str,
        parameters: dict[str, object] | None = None,
    ) -> FlextResult[dict[str, object] | None]:
        """Execute a SELECT query and return first result or None.

        Returns:
            FlextResult[dict[str, object] | None]: Success result with first row or None.

        """
        params = parameters or {}
        return self._api._dispatch_or(
            oracle_dispatcher.FlextDbOracleDispatcher.FetchOneCommand(sql, params),
            lambda: self._api._services.fetch_one(sql, params),
        )

    def _execute_sql(
        self,
        sql: str,
        parameters: dict[str, object] | None = None,
    ) -> FlextResult[int]:
        """Execute an INSERT/UPDATE/DELETE statement and return rows affected.

        Returns:
            FlextResult[int]: Success result with number of affected rows.

        """
        params = parameters or {}
        return self._api._dispatch_or(
            oracle_dispatcher.FlextDbOracleDispatcher.ExecuteStatementCommand(
                sql,
                params,
            ),
            lambda: self._api._services.execute_statement(sql, params),
        )

    def _execute_many(
        self,
        sql: str,
        parameters_list: Sequence[dict[str, object]],
    ) -> FlextResult[int]:
        """Execute a statement multiple times with different parameters.

        Returns:
            FlextResult[int]: Success result with total number of affected rows.

        """
        params_list = list(parameters_list)
        return self._api._dispatch_or(
            oracle_dispatcher.FlextDbOracleDispatcher.ExecuteManyCommand(
                sql,
                params_list,
            ),
            lambda: self._api._services.execute_many(sql, params_list),
        )

    def _execute_statement(
        self,
        sql: str | object,  # Accept both string and SQLAlchemy objects
        parameters: dict[str, object] | None = None,
    ) -> FlextResult[int]:
        """Execute SQL statement directly and return affected rows.

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
            return self._api._dispatch_or(
                oracle_dispatcher.FlextDbOracleDispatcher.ExecuteStatementCommand(
                    sql_text,
                    params,
                ),
                lambda: self._api._services.execute_statement(sql_text, params),
            )
        except (AttributeError, TypeError, ValueError) as e:
            return FlextResult.fail(f"Statement execution failed: {e}")


class _MetadataHelper:
    """Helper class for metadata operations."""

    def __init__(self, api: FlextDbOracleApi) -> None:
        self._api = api

    def _get_schemas(self) -> FlextResult[list[str]]:
        """Get list of available schemas.

        Returns:
            FlextResult[list[str]]: Success result with list of schema names.

        """
        return self._api._services.get_schemas()

    def _get_tables(
        self,
        schema: str | None = None,
    ) -> FlextResult[list[dict[str, object]]]:
        """Get list of tables in schema."""
        return self._api._services.get_tables(schema)

    def _get_columns(
        self,
        table_name: str,
        schema: str | None = None,
    ) -> FlextResult[list[dict[str, object]]]:
        """Get column information for a table."""
        return self._api._services.get_columns(table_name, schema)

    def _get_table_metadata(
        self,
        table_name: str,
        schema: str | None = None,
    ) -> FlextResult[dict[str, object]]:
        """Get comprehensive metadata for a table."""
        return self._api._services.get_table_metadata(table_name, schema)

    def _get_primary_keys(
        self,
        table_name: str,
        schema: str | None = None,
    ) -> FlextResult[list[str]]:
        """Get primary key columns for a table."""
        return self._api._services.get_primary_keys(table_name, schema)


class _PluginHelper:
    """Helper class for plugin management."""

    def __init__(self, api: FlextDbOracleApi) -> None:
        self._api = api

    def _register_plugin(self, name: str, plugin: object) -> FlextResult[None]:
        """Register a plugin with the services layer."""
        try:
            self._api._plugins[name] = plugin
            return FlextResult.ok(None)
        except (KeyError, AttributeError, TypeError) as e:
            return FlextResult.fail(f"Failed to register plugin '{name}': {e}")

    def _unregister_plugin(self, name: str) -> FlextResult[None]:
        """Unregister a plugin from the services layer."""
        try:
            if name in self._api._plugins:
                del self._api._plugins[name]
                return FlextResult.ok(None)
            return FlextResult.fail(f"Plugin '{name}' not found")
        except (KeyError, AttributeError) as e:
            return FlextResult.fail(f"Failed to unregister plugin '{name}': {e}")

    def _get_plugin(self, name: str) -> FlextResult[object]:
        """Get a registered plugin by name."""
        try:
            if name in self._api._plugins:
                return FlextResult.ok(self._api._plugins[name])
            return FlextResult.fail(f"Plugin '{name}' not found")
        except (KeyError, AttributeError) as e:
            return FlextResult.fail(f"Failed to get plugin '{name}': {e}")

    def _list_plugins(self) -> FlextResult[list[str]]:
        """List all registered plugin names."""
        try:
            return FlextResult.ok(list(self._api._plugins.keys()))
        except (AttributeError, TypeError) as e:
            return FlextResult.fail(f"Failed to list plugins: {e}")


class FlextDbOracleApi(FlextModels.Entity):
    """Oracle Database API with clean delegation to services layer."""

    def __init__(
        self,
        config: FlextDbOracleModels.OracleConfig,
        context_name: str | None = None,
    ) -> None:
        """Initialize API with Oracle configuration."""
        super().__init__()  # Initialize FlextDomainService base
        self._config = config
        self._services = FlextDbOracleServices(config=config)
        self._context_name = context_name or "oracle-api"
        self._logger = logger
        self._plugins: dict[str, object] = {}
        self._dispatcher: FlextDispatcher | None = None

        # Initialize helper instances
        self._connection_helper = _ConnectionHelper(self)
        self._query_helper = _QueryHelper(self)
        self._metadata_helper = _MetadataHelper(self)
        self._plugin_helper = _PluginHelper(self)

    @property
    def config(self) -> FlextDbOracleModels.OracleConfig:
        """Get the Oracle configuration."""
        return self._config

    def _is_valid(self) -> bool:
        """Check if API configuration is valid."""
        try:
            return (
                self._config.port > FlextConstants.Performance.MIN_CURRENT_STEP
                and self._config.service_name is not None
            )
        except AttributeError:
            # Config object may be None or missing attributes
            return False

    @classmethod
    def from_config(cls, config: FlextDbOracleModels.OracleConfig) -> Self:
        """Create API instance from configuration."""
        return cls(config)

    def _to_dict(self) -> dict[str, object]:
        """Convert API instance to dictionary representation."""
        return {
            "config": {
                "host": self._config.host,
                "port": self._config.port,
                "service_name": self._config.service_name,
                "username": self._config.username,
                # Note: not exposing password for security
            },
            "connected": False,  # Would require connection check
            "plugin_count": len(self._plugins),
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

    def _dispatch_command(self, command: object) -> FlextResult[object] | None:
        """Dispatch a command through the shared dispatcher when available."""
        dispatcher = self._ensure_dispatcher()
        if dispatcher is None:
            return None

        dispatch_result = dispatcher.dispatch(command)
        if dispatch_result.is_failure:
            return FlextResult[object].fail(
                dispatch_result.error or "Dispatcher execution failed",
            )

        payload = dispatch_result.unwrap()
        if isinstance(payload, FlextResult):
            return payload
        return FlextResult[object].ok(payload)

    def _dispatch_or(
        self,
        command: object,
        fallback: Callable[[], FlextResult[T]],
    ) -> FlextResult[T]:
        """Dispatch command or execute fallback when dispatcher disabled."""
        dispatched = self._dispatch_command(command)
        if dispatched is not None:
            return cast("FlextResult[T]", dispatched)
        return fallback()

    # Connection Management - delegate to helper
    def connect(self) -> FlextResult[Self]:
        """Connect to Oracle database.

        Returns:
            FlextResult[Self]: Success result with connected API instance.

        """
        return self._connection_helper._connect()

    def disconnect(self) -> FlextResult[None]:
        """Disconnect from Oracle database.

        Returns:
            FlextResult[None]: Success result when disconnected.

        """
        return self._connection_helper._disconnect()

    def test_connection(self) -> FlextResult[bool]:
        """Test Oracle database connection.

        Returns:
            FlextResult[bool]: Success result with connection test status.

        """
        return self._connection_helper._test_connection()

    @property
    def is_connected(self) -> bool:
        """Check if connected to the database."""
        return self._connection_helper._is_connected

    # Query Operations - delegate to helper
    def query(
        self,
        sql: str,
        parameters: dict[str, object] | None = None,
    ) -> FlextResult[list[dict[str, object]]]:
        """Execute a SELECT query and return all results."""
        return self._query_helper._query(sql, parameters)

    def query_one(
        self,
        sql: str,
        parameters: dict[str, object] | None = None,
    ) -> FlextResult[dict[str, object] | None]:
        """Execute a SELECT query and return first result or None."""
        return self._query_helper._query_one(sql, parameters)

    def execute_sql(
        self,
        sql: str,
        parameters: dict[str, object] | None = None,
    ) -> FlextResult[int]:
        """Execute an INSERT/UPDATE/DELETE statement and return rows affected."""
        return self._query_helper._execute_sql(sql, parameters)

    def execute_many(
        self,
        sql: str,
        parameters_list: Sequence[dict[str, object]],
    ) -> FlextResult[int]:
        """Execute a statement multiple times with different parameters."""
        return self._query_helper._execute_many(sql, parameters_list)

    def execute_statement(
        self,
        sql: str | object,  # Accept both string and SQLAlchemy objects
        parameters: dict[str, object] | None = None,
    ) -> FlextResult[int]:
        """Execute SQL statement directly and return affected rows."""
        return self._query_helper._execute_statement(sql, parameters)

    # Schema Introspection - delegate to helper
    def _get_schemas(self) -> FlextResult[list[str]]:
        """Get list of available schemas."""
        return self._metadata_helper._get_schemas()

    def _get_tables(
        self,
        schema: str | None = None,
    ) -> FlextResult[list[dict[str, object]]]:
        """Get list of tables in specified schema."""
        return self._metadata_helper._get_tables(schema)

    def _get_columns(
        self,
        table: str,
        schema: str | None = None,
    ) -> FlextResult[list[dict[str, object]]]:
        """Get column information for specified table."""
        return self._metadata_helper._get_columns(table, schema)

    def _get_table_metadata(
        self,
        table: str,
        schema: str | None = None,
    ) -> FlextResult[dict[str, object]]:
        """Get comprehensive table metadata including columns and constraints."""
        return self._metadata_helper._get_table_metadata(table, schema)

    def _get_primary_keys(
        self,
        table: str,
        schema: str | None = None,
    ) -> FlextResult[list[str]]:
        """Get primary key column names for specified table."""
        return self._metadata_helper._get_primary_keys(table, schema)

    def _convert_singer_type(
        self,
        singer_type: str | list[str],
        format_hint: str | None = None,
    ) -> FlextResult[str]:
        """Convert Singer JSON Schema type to Oracle SQL type."""
        return self._services.convert_singer_type(singer_type, format_hint)

    def _map_singer_schema(
        self,
        schema: dict[str, object],
    ) -> FlextResult[dict[str, str]]:
        """Map Singer JSON Schema to Oracle table schema."""
        return self._services.map_singer_schema(schema)

    # Transaction Management
    def _transaction(self) -> FlextResult[object]:
        """Get a transaction context manager."""
        try:
            transaction_context = self._services.transaction()
            return FlextResult.ok(transaction_context)
        except (AttributeError, RuntimeError, ValueError) as e:
            return FlextResult.fail(f"Transaction creation failed: {e}")

    # Utility Methods
    def _optimize_query(self, sql: str) -> FlextResult[str]:
        """Optimize a SQL query for Oracle."""
        try:
            optimized = " ".join(sql.split())
            return FlextResult.ok(optimized)
        except (AttributeError, ValueError, TypeError) as e:
            return FlextResult.fail(f"Query optimization failed: {e}")

    def _get_observability_metrics(self) -> FlextResult[dict[str, object]]:
        """Get observability metrics for the connection."""
        return self._services.get_metrics()

    # Configuration

    @classmethod
    def from_env(cls, prefix: str = "FLEXT_TARGET_ORACLE") -> FlextResult[Self]:
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
    def from_url(cls, database_url: str) -> FlextResult[Self]:
        """Create API instance from database URL."""
        config_result = FlextDbOracleModels.OracleConfig.from_url(database_url)
        if config_result.is_success:
            instance = cls.from_config(config_result.value)
            return FlextResult.ok(instance)
        return FlextResult.fail(f"Failed to parse database URL: {config_result.error}")

    # Plugin System - delegate to helper
    def _register_plugin(self, name: str, plugin: object) -> FlextResult[None]:
        """Register a plugin with the services layer."""
        return self._plugin_helper._register_plugin(name, plugin)

    def _unregister_plugin(self, name: str) -> FlextResult[None]:
        """Unregister a plugin from the services layer."""
        return self._plugin_helper._unregister_plugin(name)

    def _get_plugin(self, name: str) -> FlextResult[object]:
        """Get a registered plugin by name."""
        return self._plugin_helper._get_plugin(name)

    def _list_plugins(self) -> FlextResult[list[str]]:
        """List all registered plugin names."""
        return self._plugin_helper._list_plugins()

    # Additional methods demanded by tests and real usage
    def _execute_query_sql(
        self,
        sql: str,
    ) -> FlextResult[FlextDbOracleModels.QueryResult]:
        """Execute SQL query and return results as QueryResult."""
        try:
            result = self._dispatch_or(
                oracle_dispatcher.FlextDbOracleDispatcher.ExecuteQueryCommand(sql, {}),
                lambda: self._services.execute_query(sql),
            )
            if result.is_success:
                # Convert result data to proper format for QueryResult
                # If it's raw data, wrap it in QueryResult
                # Initialize variables
                rows_data: list[list[object]] = []
                columns: list[str] = []

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

    def _get_health_status(self) -> FlextResult[dict[str, object]]:
        """Get database connection health status."""
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

    def _execute(self) -> FlextResult[dict[str, object]]:
        """Execute default domain service operation - return API status."""
        try:
            return FlextResult.ok(self.to_dict())
        except Exception as e:
            return FlextResult.fail(f"API execution failed: {e}")

    def __repr__(self) -> str:
        """Return string representation of the API instance."""
        connection_status = "connected" if self.is_connected else "disconnected"
        return f"FlextDbOracleApi(host={self._config.host}, status={connection_status})"
