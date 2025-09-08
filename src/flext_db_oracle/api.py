"""Oracle Database API following FLEXT ecosystem patterns.

Clean, production-ready Oracle database API that follows SOLID principles,
uses proper typing, and integrates with flext-core patterns.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import contextlib
from collections.abc import Sequence
from typing import Self, cast

from flext_core import FlextLogger, FlextResult, FlextTypes

from flext_db_oracle.models import FlextDbOracleModels
from flext_db_oracle.services import FlextDbOracleServices

logger = FlextLogger(__name__)


class FlextDbOracleApi:
    """Oracle Database API with clean delegation to services layer.

    This API provides a clean interface to Oracle database operations
    by delegating all work to the services layer while maintaining
    type safety and proper error handling.
    """

    def __init__(
        self, config: FlextDbOracleModels.OracleConfig, context_name: str | None = None
    ) -> None:
        """Initialize API with Oracle configuration."""
        self._config = config
        self._services = FlextDbOracleServices(config)
        self._context_name = context_name or "oracle-api"
        self._logger = logger.bind(component=self._context_name)
        self._plugins: FlextTypes.Core.Dict = {}

    @property
    def config(self) -> FlextDbOracleModels.OracleConfig:
        """Get the Oracle configuration."""
        return self._config

    def is_valid(self) -> bool:
        """Check if API configuration is valid."""
        try:
            return (
                self._config.host is not None
                and self._config.port > 0
                and self._config.service_name is not None
                and self._config.username is not None
            )
        except AttributeError:
            # Config object may be None or missing attributes
            return False

    @classmethod
    def from_config(cls, config: FlextDbOracleModels.OracleConfig) -> FlextDbOracleApi:
        """Create API instance from configuration."""
        return cls(config)

    @classmethod
    def with_config(cls, config: FlextDbOracleModels.OracleConfig) -> FlextDbOracleApi:
        """Create API instance with configuration (alias for from_config).

        Args:
            config: Oracle configuration

        Returns:
            FlextDbOracleApi instance

        """
        return cls(config)

    def to_dict(self) -> FlextTypes.Core.Dict:
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

    # Connection Management
    def connect(self) -> FlextResult[Self]:
        """Connect to Oracle database."""
        result = self._services.connect()
        if result.success:
            return FlextResult[Self].ok(self)
        return FlextResult[Self].fail(f"Connection failed: {result.error}")

    def disconnect(self) -> FlextResult[None]:
        """Disconnect from Oracle database."""
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
        parameters: FlextTypes.Core.Dict | None = None,
    ) -> FlextResult[list[FlextTypes.Core.Dict]]:
        """Execute a SELECT query and return all results."""
        return self._services.execute_query(sql, parameters or {})

    def query_one(
        self,
        sql: str,
        parameters: FlextTypes.Core.Dict | None = None,
    ) -> FlextResult[FlextTypes.Core.Dict | None]:
        """Execute a SELECT query and return first result or None."""
        return self._services.fetch_one(sql, parameters or {})

    def execute(
        self,
        sql: str,
        parameters: FlextTypes.Core.Dict | None = None,
    ) -> FlextResult[int]:
        """Execute an INSERT/UPDATE/DELETE statement and return rows affected."""
        return self._services.execute_statement(sql, parameters or {})

    def execute_many(
        self,
        sql: str,
        parameters_list: Sequence[FlextTypes.Core.Dict],
    ) -> FlextResult[int]:
        """Execute a statement multiple times with different parameters."""
        return self._services.execute_many(sql, list(parameters_list))

    # Schema Introspection
    def get_schemas(self) -> FlextResult[FlextTypes.Core.StringList]:
        """Get list of available schemas."""
        return self._services.get_schemas()

    def get_tables(
        self, schema: str | None = None
    ) -> FlextResult[list[FlextTypes.Core.Dict]]:
        """Get list of tables in specified schema."""
        try:
            result = self._services.get_tables(schema)
            if result.success:
                # Convert list of strings to list of dict for consistency with tests
                table_dicts: list[FlextTypes.Core.Dict] = [
                    {"name": name} for name in result.value
                ]
                return FlextResult[list[FlextTypes.Core.Dict]].ok(table_dicts)
            return FlextResult[list[FlextTypes.Core.Dict]].fail(
                result.error or "Failed to get tables"
            )
        except Exception as e:
            return FlextResult[list[FlextTypes.Core.Dict]].fail(
                f"Error getting tables: {e}"
            )

    def get_columns(
        self,
        table: str,
        schema: str | None = None,
    ) -> FlextResult[list[FlextTypes.Core.Dict]]:
        """Get column information for specified table."""
        try:
            result = self._services.get_columns(table, schema)
            if result.success:
                # Convert ColumnInfo objects to dict for consistency
                column_dicts = []
                for col in result.value:
                    if hasattr(col, "model_dump"):
                        column_dicts.append(col.model_dump())
                    elif hasattr(col, "__dict__"):
                        column_dicts.append(col.__dict__)
                    else:
                        column_dicts.append({"name": str(col)})
                return FlextResult[list[FlextTypes.Core.Dict]].ok(column_dicts)
            return FlextResult[list[FlextTypes.Core.Dict]].fail(
                result.error or "Failed to get columns"
            )
        except Exception as e:
            return FlextResult[list[FlextTypes.Core.Dict]].fail(
                f"Error getting columns: {e}"
            )

    def get_table_metadata(
        self, table: str, schema: str | None = None
    ) -> FlextResult[FlextTypes.Core.Dict]:
        """Get comprehensive table metadata including columns and constraints."""
        try:
            # Get table information
            tables_result = self.get_tables(schema)
            if not tables_result.success:
                return FlextResult[FlextTypes.Core.Dict].fail(
                    f"Failed to get tables: {tables_result.error}"
                )

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
                return FlextResult[FlextTypes.Core.Dict].fail(
                    f"Table '{table}' not found"
                )

            # Get columns for this table
            columns_result = self.get_columns(table, schema)
            if not columns_result.success:
                return FlextResult[FlextTypes.Core.Dict].fail(
                    f"Failed to get columns: {columns_result.error}"
                )

            metadata: FlextTypes.Core.Dict = {
                "table_name": table,
                "schema_name": schema,
                "columns": columns_result.value,
                "column_count": len(columns_result.value),
            }

            return FlextResult[FlextTypes.Core.Dict].ok(metadata)
        except Exception as e:
            return FlextResult[FlextTypes.Core.Dict].fail(
                f"Error getting table metadata: {e}"
            )

    def get_primary_keys(
        self, table: str, schema: str | None = None
    ) -> FlextResult[FlextTypes.Core.StringList]:
        """Get primary key column names for specified table."""
        try:
            columns_result = self.get_columns(table, schema)
            if not columns_result.success:
                return FlextResult[FlextTypes.Core.StringList].fail(
                    f"Failed to get columns: {columns_result.error}"
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

            return FlextResult[FlextTypes.Core.StringList].ok(primary_keys)
        except Exception as e:
            return FlextResult[FlextTypes.Core.StringList].fail(
                f"Error getting primary keys: {e}"
            )

    def convert_singer_type(
        self,
        singer_type: str | FlextTypes.Core.StringList,
        format_hint: str | None = None,
    ) -> FlextResult[str]:
        """Convert Singer JSON Schema type to Oracle SQL type."""
        return self._services.convert_singer_type(singer_type, format_hint)

    def map_singer_schema(
        self, schema: FlextTypes.Core.Dict
    ) -> FlextResult[FlextTypes.Core.Headers]:
        """Map Singer JSON Schema to Oracle table schema."""
        return self._services.map_singer_schema(schema)

    # Transaction Management
    def transaction(self) -> FlextResult[object]:
        """Get a transaction context manager."""
        try:
            transaction_context = self._services.transaction()
            return FlextResult[object].ok(transaction_context)
        except (AttributeError, RuntimeError, ValueError) as e:
            return FlextResult[object].fail(f"Transaction creation failed: {e}")

    # Utility Methods
    def optimize_query(self, sql: str) -> FlextResult[str]:
        """Optimize a SQL query for Oracle."""
        # Simple optimization - remove extra whitespace and normalize
        try:
            optimized = " ".join(sql.split())
            return FlextResult[str].ok(optimized)
        except (AttributeError, ValueError, TypeError) as e:
            return FlextResult[str].fail(f"Query optimization failed: {e}")

    def get_observability_metrics(self) -> FlextResult[FlextTypes.Core.Dict]:
        """Get observability metrics for the connection."""
        return self._services.get_metrics()

    # Configuration

    @classmethod
    def from_env(
        cls,
        prefix: str = "FLEXT_TARGET_ORACLE",
    ) -> FlextResult[Self]:
        """Create API instance from environment variables."""
        config_result = FlextDbOracleModels.OracleConfig.from_env(prefix)
        if config_result.success:
            instance = cls.from_config(config_result.value)
            return FlextResult[Self].ok(cast("Self", instance))
        return FlextResult[Self].fail(
            f"Failed to load config from environment: {config_result.error}",
        )

    @classmethod
    def from_url(cls, database_url: str) -> FlextResult[Self]:
        """Create API instance from database URL."""
        config_result = FlextDbOracleModels.OracleConfig.from_url(database_url)
        if config_result.success:
            instance = cls.from_config(config_result.value)
            return FlextResult[Self].ok(cast("Self", instance))
        return FlextResult[Self].fail(
            f"Failed to parse database URL: {config_result.error}"
        )

    # Plugin System
    def register_plugin(self, name: str, plugin: object) -> FlextResult[None]:
        """Register a plugin with the services layer."""
        try:
            self._plugins[name] = plugin
            return FlextResult[None].ok(None)
        except (KeyError, AttributeError, TypeError) as e:
            return FlextResult[None].fail(f"Failed to register plugin '{name}': {e}")

    def unregister_plugin(self, name: str) -> FlextResult[None]:
        """Unregister a plugin from the services layer."""
        try:
            if name in self._plugins:
                del self._plugins[name]
                return FlextResult[None].ok(None)
            return FlextResult[None].fail(f"Plugin '{name}' not found")
        except (KeyError, AttributeError) as e:
            return FlextResult[None].fail(f"Failed to unregister plugin '{name}': {e}")

    def get_plugin(self, name: str) -> FlextResult[object]:
        """Get a registered plugin by name."""
        try:
            if name in self._plugins:
                return FlextResult[object].ok(self._plugins[name])
            return FlextResult[object].fail(f"Plugin '{name}' not found")
        except (KeyError, AttributeError) as e:
            return FlextResult[object].fail(f"Failed to get plugin '{name}': {e}")

    def list_plugins(self) -> FlextResult[FlextTypes.Core.StringList]:
        """List all registered plugin names."""
        try:
            return FlextResult[FlextTypes.Core.StringList].ok(
                list(self._plugins.keys())
            )
        except (AttributeError, TypeError) as e:
            return FlextResult[FlextTypes.Core.StringList].fail(
                f"Failed to list plugins: {e}"
            )

    # Additional methods demanded by tests and real usage
    def execute_sql(self, sql: str) -> FlextResult[FlextDbOracleModels.QueryResult]:
        """Execute SQL query and return results."""
        try:
            # Delegate to services layer
            result = self._services.execute_query(sql)
            if result.success:
                # Convert result data to proper format for QueryResult
                # If it's raw data, wrap it in QueryResult
                # Initialize variables
                rows_data: list[FlextTypes.Core.List] = []
                columns: FlextTypes.Core.StringList = []

                if isinstance(result.value, list) and result.value:
                    # Check first element to determine format
                    first_element = result.value[0]
                    if isinstance(first_element, dict):
                        # Convert list of dicts to list of lists
                        rows_data = [list(row.values()) for row in result.value]
                        columns = list(first_element.keys())
                    # Note: Only handling dict format for now - other formats can be added when needed

                query_result = FlextDbOracleModels.QueryResult(
                    columns=columns,
                    rows=rows_data,
                    row_count=len(result.value)
                    if isinstance(result.value, list)
                    else 0,
                    query_hash=None,
                    explain_plan=None,
                )
                return FlextResult[FlextDbOracleModels.QueryResult].ok(query_result)
            return FlextResult[FlextDbOracleModels.QueryResult].fail(
                result.error or "SQL execution failed"
            )
        except Exception as e:
            return FlextResult[FlextDbOracleModels.QueryResult].fail(
                f"SQL execution error: {e}"
            )

    def get_health_status(self) -> FlextResult[FlextTypes.Core.Dict]:
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
            return FlextResult[FlextTypes.Core.Dict].ok(status)
        except Exception as e:
            return FlextResult[FlextTypes.Core.Dict].fail(f"Health check failed: {e}")

    @property
    def connection(self) -> object:
        """Get connection object (delegates to services)."""
        return getattr(self._services, "connection", None)

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

    def __repr__(self) -> str:
        """Return string representation of the API instance."""
        connection_status = "connected" if self.is_connected else "disconnected"
        return f"FlextDbOracleApi(host={self._config.host}, status={connection_status})"
