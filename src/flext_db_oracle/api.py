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

from flext_core import FlextDispatcher, FlextModels, FlextResult
from flext_db_oracle.constants import FlextDbOracleConstants
from flext_db_oracle.models import FlextDbOracleModels
from flext_db_oracle.services import FlextDbOracleServices

from . import dispatcher as oracle_dispatcher

logger = logging.getLogger(__name__)
T = TypeVar("T")


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

    @property
    def config(self) -> FlextDbOracleModels.OracleConfig:
        """Get the Oracle configuration."""
        return self._config

    def is_valid(self) -> bool:
        """Check if API configuration is valid."""
        try:
            return (
                self._config.port > 0
                and self._config.service_name is not None
            )
        except AttributeError:
            # Config object may be None or missing attributes
            return False

    @classmethod
    def from_config(cls, config: FlextDbOracleModels.OracleConfig) -> Self:
        """Create API instance from configuration."""
        return cls(config)

    def to_dict(self) -> dict[str, object]:
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

    # Connection Management
    def connect(self) -> FlextResult[Self]:
        """Connect to Oracle database."""
        dispatch_result = self._dispatch_command(
            oracle_dispatcher.FlextDbOracleDispatcher.ConnectCommand(),
        )
        if dispatch_result is not None:
            if dispatch_result.is_success:
                return FlextResult.ok(self)
            return FlextResult.fail(
                dispatch_result.error or "Connection failed",
            )

        result = self._services.connect()
        if result.is_success:
            return FlextResult.ok(self)
        return FlextResult.fail(f"Connection failed: {result.error}")

    def disconnect(self) -> FlextResult[None]:
        """Disconnect from Oracle database."""
        dispatch_result = self._dispatch_command(
            oracle_dispatcher.FlextDbOracleDispatcher.DisconnectCommand(),
        )
        if dispatch_result is not None:
            return cast("FlextResult[None]", dispatch_result)

        return self._services.disconnect()

    def test_connection(self) -> FlextResult[bool]:
        """Test Oracle database connection."""
        return self._dispatch_or(
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
        parameters: dict[str, object] | None = None,
    ) -> FlextResult[list[dict[str, object]]]:
        """Execute a SELECT query and return all results."""
        params = parameters or {}
        return self._dispatch_or(
            oracle_dispatcher.FlextDbOracleDispatcher.ExecuteQueryCommand(sql, params),
            lambda: self._services.execute_query(sql, params),
        )

    def query_one(
        self,
        sql: str,
        parameters: dict[str, object] | None = None,
    ) -> FlextResult[dict[str, object] | None]:
        """Execute a SELECT query and return first result or None."""
        params = parameters or {}
        return self._dispatch_or(
            oracle_dispatcher.FlextDbOracleDispatcher.FetchOneCommand(sql, params),
            lambda: self._services.fetch_one(sql, params),
        )

    def execute_sql(
        self,
        sql: str,
        parameters: dict[str, object] | None = None,
    ) -> FlextResult[int]:
        """Execute an INSERT/UPDATE/DELETE statement and return rows affected."""
        params = parameters or {}
        return self._dispatch_or(
            oracle_dispatcher.FlextDbOracleDispatcher.ExecuteStatementCommand(
                sql,
                params,
            ),
            lambda: self._services.execute_statement(sql, params),
        )

    def execute_many(
        self,
        sql: str,
        parameters_list: Sequence[dict[str, object]],
    ) -> FlextResult[int]:
        """Execute a statement multiple times with different parameters."""
        params_list = list(parameters_list)
        return self._dispatch_or(
            oracle_dispatcher.FlextDbOracleDispatcher.ExecuteManyCommand(
                sql,
                params_list,
            ),
            lambda: self._services.execute_many(sql, params_list),
        )

    def execute_statement(
        self,
        sql: str | object,  # Accept both string and SQLAlchemy objects
        parameters: dict[str, object] | None = None,
    ) -> FlextResult[int]:
        """Execute SQL statement directly and return affected rows."""
        try:
            # Handle SQLAlchemy objects by converting to string
            if hasattr(sql, "__str__") and not isinstance(sql, str):
                sql_text = str(sql)
            else:
                sql_text = str(sql)

            params = parameters or {}
            return self._dispatch_or(
                oracle_dispatcher.FlextDbOracleDispatcher.ExecuteStatementCommand(
                    sql_text,
                    params,
                ),
                lambda: self._services.execute_statement(sql_text, params),
            )
        except Exception as e:
            return FlextResult.fail(f"Statement execution failed: {e}")

    # Schema Introspection
    def get_schemas(self) -> FlextResult[list[str]]:
        """Get list of available schemas."""
        return self._dispatch_or(
            oracle_dispatcher.FlextDbOracleDispatcher.GetSchemasCommand(),
            self._services.get_schemas,
        )

    def get_tables(
        self,
        schema: str | None = None,
    ) -> FlextResult[list[dict[str, object]]]:
        """Get list of tables in specified schema."""
        try:
            result = self._dispatch_or(
                oracle_dispatcher.FlextDbOracleDispatcher.GetTablesCommand(schema),
                lambda: self._services.get_tables(schema),
            )
            if result.is_success:
                # Convert list of strings to list of dict for consistency with tests
                table_dicts: list[dict[str, object]] = [
                    {"name": name} for name in result.value
                ]
                return FlextResult.ok(table_dicts)
            return FlextResult.fail(result.error or "Failed to get tables")
        except Exception as e:
            return FlextResult.fail(f"Error getting tables: {e}")

    def get_columns(
        self,
        table: str,
        schema: str | None = None,
    ) -> FlextResult[list[dict[str, object]]]:
        """Get column information for specified table."""
        try:
            result = self._dispatch_or(
                oracle_dispatcher.FlextDbOracleDispatcher.GetColumnsCommand(
                    table,
                    schema,
                ),
                lambda: self._services.get_columns(table, schema),
            )
            if result.is_success:
                # Convert ColumnInfo objects to dict for consistency
                column_dicts = []
                for col in result.value:
                    if hasattr(col, "model_dump"):
                        column_dicts.append(col.model_dump())
                    elif hasattr(col, "__dict__"):
                        column_dicts.append(col.__dict__)
                    else:
                        column_dicts.append({"name": str(col)})
                return FlextResult.ok(column_dicts)
            return FlextResult.fail(result.error or "Failed to get columns")
        except Exception as e:
            return FlextResult.fail(f"Error getting columns: {e}")

    def get_table_metadata(
        self,
        table: str,
        schema: str | None = None,
    ) -> FlextResult[dict[str, object]]:
        """Get comprehensive table metadata including columns and constraints."""
        try:
            # Get table information
            tables_result = self.get_tables(schema)
            if not tables_result.is_success:
                return FlextResult.fail(f"Failed to get tables: {tables_result.error}")

            # Find the specific table
            table_info = None
            for tbl in tables_result.value:
                tbl_name = tbl.get("name", "")
                if (
                    isinstance(tbl, dict)
                    and isinstance(tbl_name, str)
                    and tbl_name.upper() == table.upper()
                ):
                    table_info = tbl
                    break

            if not table_info:
                return FlextResult.fail(f"Table '{table}' not found")

            # Get columns for this table
            columns_result = self.get_columns(table, schema)
            if not columns_result.is_success:
                return FlextResult.fail(
                    f"Failed to get columns: {columns_result.error}",
                )

            metadata: dict[str, object] = {
                "table_name": table,
                "schema_name": schema,
                "columns": columns_result.value,
                "column_count": len(columns_result.value),
            }

            return FlextResult.ok(metadata)
        except Exception as e:
            return FlextResult.fail(f"Error getting table metadata: {e}")

    def get_primary_keys(
        self,
        table: str,
        schema: str | None = None,
    ) -> FlextResult[list[str]]:
        """Get primary key column names for specified table."""
        try:
            columns_result = self.get_columns(table, schema)
            if not columns_result.is_success:
                return FlextResult.fail(
                    f"Failed to get columns: {columns_result.error}",
                )

            primary_keys = []
            for col in columns_result.value:
                if isinstance(col, dict):
                    # Check various indicators of primary key
                    column_name = col.get("column_name", "")
                    nullable = col.get("nullable", True)
                    column_id = col.get("column_id", 0)

                    # Heuristic for primary key detection
                    if isinstance(column_name, str):
                        name_lower = column_name.lower()
                    else:
                        continue  # Skip if not string
                    is_likely_pk = (
                        name_lower in {"id", "pk"}
                        or name_lower.endswith(("_id", "_pk"))
                        or (column_id == 1 and not nullable)
                    )

                    if is_likely_pk and isinstance(column_name, str):
                        primary_keys.append(column_name)

            return FlextResult.ok(primary_keys)
        except Exception as e:
            return FlextResult.fail(f"Error getting primary keys: {e}")

    def convert_singer_type(
        self,
        singer_type: str | list[str],
        format_hint: str | None = None,
    ) -> FlextResult[str]:
        """Convert Singer JSON Schema type to Oracle SQL type."""
        return self._services.convert_singer_type(singer_type, format_hint)

    def map_singer_schema(
        self,
        schema: dict[str, object],
    ) -> FlextResult[dict[str, str]]:
        """Map Singer JSON Schema to Oracle table schema."""
        return self._services.map_singer_schema(schema)

    # Transaction Management
    def transaction(self) -> FlextResult[object]:
        """Get a transaction context manager."""
        try:
            transaction_context = self._services.transaction()
            return FlextResult.ok(transaction_context)
        except (AttributeError, RuntimeError, ValueError) as e:
            return FlextResult.fail(f"Transaction creation failed: {e}")

    # Utility Methods
    def optimize_query(self, sql: str) -> FlextResult[str]:
        """Optimize a SQL query for Oracle."""
        try:
            optimized = " ".join(sql.split())
            return FlextResult.ok(optimized)
        except (AttributeError, ValueError, TypeError) as e:
            return FlextResult.fail(f"Query optimization failed: {e}")

    def get_observability_metrics(self) -> FlextResult[dict[str, object]]:
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

    # Plugin System
    def register_plugin(self, name: str, plugin: object) -> FlextResult[None]:
        """Register a plugin with the services layer."""
        try:
            self._plugins[name] = plugin
            return FlextResult.ok(None)
        except (KeyError, AttributeError, TypeError) as e:
            return FlextResult.fail(f"Failed to register plugin '{name}': {e}")

    def unregister_plugin(self, name: str) -> FlextResult[None]:
        """Unregister a plugin from the services layer."""
        try:
            if name in self._plugins:
                del self._plugins[name]
                return FlextResult.ok(None)
            return FlextResult.fail(f"Plugin '{name}' not found")
        except (KeyError, AttributeError) as e:
            return FlextResult.fail(f"Failed to unregister plugin '{name}': {e}")

    def get_plugin(self, name: str) -> FlextResult[object]:
        """Get a registered plugin by name."""
        try:
            if name in self._plugins:
                return FlextResult.ok(self._plugins[name])
            return FlextResult.fail(f"Plugin '{name}' not found")
        except (KeyError, AttributeError) as e:
            return FlextResult.fail(f"Failed to get plugin '{name}': {e}")

    def list_plugins(self) -> FlextResult[list[str]]:
        """List all registered plugin names."""
        try:
            return FlextResult.ok(list(self._plugins.keys()))
        except (AttributeError, TypeError) as e:
            return FlextResult.fail(f"Failed to list plugins: {e}")

    # Additional methods demanded by tests and real usage
    def execute_query_sql(
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

    def get_health_status(self) -> FlextResult[dict[str, object]]:
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
    def connection(self) -> object | None:
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

    def execute(self) -> FlextResult[dict[str, object]]:
        """Execute default domain service operation - return API status."""
        try:
            return FlextResult.ok(self.to_dict())
        except Exception as e:
            return FlextResult.fail(f"API execution failed: {e}")

    def __repr__(self) -> str:
        """Return string representation of the API instance."""
        connection_status = "connected" if self.is_connected else "disconnected"
        return f"FlextDbOracleApi(host={self._config.host}, status={connection_status})"
