"""Oracle Database API with complete FLEXT ecosystem integration.

This API provides a unified interface to Oracle database operations
following FLEXT patterns with complete flext-core integration.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import contextlib
import types
from collections.abc import Sequence
from typing import Self, override

from flext_core import r, t
from flext_core.service import FlextService

from flext_db_oracle.constants import c
from flext_db_oracle.dispatcher import FlextDbOracleDispatcher
from flext_db_oracle.models import FlextDbOracleModels
from flext_db_oracle.services import FlextDbOracleServices
from flext_db_oracle.settings import FlextDbOracleSettings

# Simplified delegation - no complex decorators needed


class FlextDbOracleApi(FlextService[FlextDbOracleSettings]):
    """Oracle Database API with complete flext-core integration.

    This API provides a unified interface to Oracle database operations,
    integrating with flext-core components for proper error handling,
    logging, service orchestration, and enterprise patterns.

    Architecture:
    - Extends s for domain service patterns
    - Uses r railway pattern for error handling
    - Integrates FlextContext, FlextBus for enterprise features
    - Delegates to FlextDbOracleServices for Oracle operations
    - Optional FlextDispatcher integration for CQRS patterns
    """

    @override
    def __init__(
        self,
        config: FlextDbOracleSettings,
        context_name: str | None = None,
    ) -> None:
        """Initialize API with Oracle configuration and complete flext-core integration."""
        # Initialize s first
        super().__init__()

        # Configuration management - use FlextDbOracleSettings directly
        self._oracle_config = config

        # Core services initialization
        self._services = FlextDbOracleServices(config=self._oracle_config)

        # Context and naming
        self._context_name = context_name or "oracle-api"

        # Complete flext-core ecosystem integration
        # Container is accessible via FlextContainer.get_global() when needed
        self._context = None
        # Logger will be initialized lazily via the parent class property

        # Optional dispatcher for CQRS patterns
        self._dispatcher = FlextDbOracleDispatcher.build_dispatcher(self._services)

        # Plugin system
        self._plugins: dict[str, t.JsonValue] = {}

    @property
    def oracle_config(self) -> FlextDbOracleSettings:
        """Get the Oracle configuration."""
        return self._oracle_config

    def is_valid(self) -> bool:
        """Check if API configuration is valid."""
        try:
            return (
                self._oracle_config.port >= c.DbOracle.OracleNetwork.MIN_PORT
                and self._oracle_config.service_name is not None
            )
        except AttributeError:
            return False

    @classmethod
    def from_env(cls, prefix: str = "ORACLE_") -> r[FlextDbOracleApi]:
        """Create API instance from environment variables.

        Args:
            prefix: Environment variable prefix (default: "ORACLE_")

        Returns:
            r[FlextDbOracleApi]: API instance or error.

        """
        try:
            config_result = FlextDbOracleSettings.from_env(prefix)
            if config_result.is_failure:
                return r[FlextDbOracleApi].fail(
                    f"Config creation failed: {config_result.error}",
                )

            config = config_result.value
            return r[FlextDbOracleApi].ok(cls(config=config))
        except Exception as e:
            return r[FlextDbOracleApi].fail(
                f"API creation from environment failed: {e}",
            )

    @classmethod
    def from_url(cls, url: str) -> r[FlextDbOracleApi]:
        """Create API instance from Oracle URL string.

        Args:
        url: Oracle connection URL (oracle://user:pass@host:port/service)

        Returns:
        r[FlextDbOracleApi]: API instance or error.

        """
        try:
            config_result = FlextDbOracleSettings.from_url(url)
            if config_result.is_failure:
                return r[FlextDbOracleApi].fail(
                    f"Config creation from URL failed: {config_result.error}",
                )

            config = config_result.value
            return r[FlextDbOracleApi].ok(cls(config=config))
        except Exception as e:
            return r[FlextDbOracleApi].fail(
                f"API creation from URL failed: {e}",
            )

    def to_dict(self) -> dict[str, t.JsonValue]:
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
    def plugins(self) -> dict[str, t.JsonValue]:
        """Get the plugins dictionary."""
        return self._plugins

    # Connection Management
    def connect(self) -> r[FlextDbOracleApi]:
        """Connect to Oracle database."""
        self.logger.info(
            "Connecting to Oracle database",
            extra={"host": self._oracle_config.host},
        )

        return self._services.connect().map(lambda _: self)

    def disconnect(self) -> r[None]:
        """Disconnect from Oracle database."""
        self.logger.info("Disconnecting from Oracle database")
        return self._services.disconnect()

    def test_connection(self) -> r[bool]:
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
        parameters: dict[str, t.JsonValue] | None = None,
    ) -> r[list[dict[str, t.JsonValue]]]:
        """Execute a SELECT query and return all results."""
        self.logger.debug("Executing query", query_length=len(sql))
        return self._services.execute_query(sql, parameters or {})

    def query_one(
        self,
        sql: str,
        parameters: dict[str, t.JsonValue] | None = None,
    ) -> r[dict[str, t.JsonValue] | None]:
        """Execute a SELECT query and return first result or None."""
        return self._services.fetch_one(sql, parameters or {})

    def execute_sql(
        self,
        sql: str,
        parameters: dict[str, t.JsonValue] | None = None,
    ) -> r[int]:
        """Execute an INSERT/UPDATE/DELETE statement and return rows affected."""
        self.logger.debug("Executing SQL statement", statement_length=len(sql))
        return self._services.execute_statement(sql, parameters or {})

    def execute_many(
        self,
        sql: str,
        parameters_list: Sequence[dict[str, t.JsonValue]],
    ) -> r[int]:
        """Execute a statement multiple times with different parameters."""
        self.logger.debug("Executing bulk statement", batch_size=len(parameters_list))
        return self._services.execute_many(sql, list(parameters_list))

    def execute_statement(
        self,
        sql: str | t.JsonValue,
        parameters: dict[str, t.JsonValue] | None = None,
    ) -> r[int]:
        """Execute SQL statement directly and return affected rows."""
        try:
            sql_text = str(sql) if not isinstance(sql, str) else sql
            return self._services.execute_statement(sql_text, parameters or {})
        except Exception as e:
            return r.fail(f"Statement execution failed: {e}")

    # Schema Introspection
    def get_schemas(self) -> r[list[str]]:
        """Get list of available schemas."""
        return self._services.get_schemas()

    def get_tables(self, schema: str | None = None) -> r[list[str]]:
        """Get list of tables in specified schema."""
        return self._services.get_tables(schema)

    def get_columns(
        self,
        table: str,
        schema: str | None = None,
    ) -> r[list[dict[str, t.JsonValue]]]:
        """Get column information for specified table."""
        return self._services.get_columns(table, schema).map(
            lambda cols: [
                {
                    "name": col.get("column_name", ""),
                    "data_type": col.get("data_type", ""),
                    "nullable": col.get("nullable", False),
                    "default_value": col.get("data_default", None),
                }
                for col in cols
            ],
        )

    def get_table_metadata(
        self,
        table: str,
        schema: str | None = None,
    ) -> r[dict[str, t.JsonValue]]:
        """Get complete table metadata including columns and constraints."""
        return self._services.get_table_metadata(table, schema)

    def get_primary_keys(
        self,
        table: str,
        schema: str | None = None,
    ) -> r[list[str]]:
        """Get primary key column names for specified table."""
        return self._services.get_primary_keys(table, schema)

    def convert_singer_type(
        self,
        singer_type: str | list[str],
        format_hint: str | None = None,
    ) -> r[str]:
        """Convert Singer JSON Schema type to Oracle SQL type."""
        return self._services.convert_singer_type(singer_type, format_hint)

    def map_singer_schema(
        self,
        schema: dict[str, t.JsonValue],
    ) -> r[dict[str, str]]:
        """Map Singer JSON Schema to Oracle table schema."""
        return self._services.map_singer_schema(schema)

    # Transaction Management
    def transaction(self) -> r[dict[str, t.JsonValue]]:
        """Get transaction status information."""
        try:
            # Return transaction status rather than context manager
            status: dict[str, t.JsonValue] = {
                "connected": self._services.is_connected(),
                "transaction_available": hasattr(self._services, "transaction"),
            }
            return r[dict[str, t.JsonValue]].ok(status)
        except (AttributeError, RuntimeError, ValueError) as e:
            return r[dict[str, t.JsonValue]].fail(
                f"Transaction status check failed: {e}"
            )

    # Utility Methods
    def optimize_query(self, sql: str) -> r[str]:
        """Optimize a SQL query for Oracle."""
        try:
            return r.ok(" ".join(sql.split()))
        except (AttributeError, ValueError, TypeError) as e:
            return r.fail(f"Query optimization failed: {e}")

    def get_observability_metrics(self) -> r[dict[str, t.JsonValue]]:
        """Get observability metrics for the connection."""
        return self._services.get_metrics()

    # Plugin System
    def register_plugin(self, name: str, plugin: t.JsonValue) -> r[None]:
        """Register a plugin with the services layer."""
        try:
            self._plugins[name] = plugin
            return r.ok(None)
        except (KeyError, AttributeError, TypeError) as e:
            return r.fail(f"Failed to register plugin '{name}': {e}")

    def unregister_plugin(self, name: str) -> r[None]:
        """Unregister a plugin from the services layer."""
        try:
            if name in self._plugins:
                del self._plugins[name]
                return r.ok(None)
            return r.fail(f"Plugin '{name}' not found")
        except (KeyError, AttributeError) as e:
            return r.fail(f"Failed to unregister plugin '{name}': {e}")

    def get_plugin(self, name: str) -> r[t.JsonValue]:
        """Get a registered plugin by name."""
        try:
            return (
                r.ok(self._plugins[name])
                if name in self._plugins
                else r.fail(f"Plugin '{name}' not found")
            )
        except (KeyError, AttributeError) as e:
            return r.fail(f"Failed to get plugin '{name}': {e}")

    def list_plugins(self) -> r[list[str]]:
        """List all registered plugin names."""
        try:
            return r.ok(list(self._plugins.keys()))
        except (AttributeError, TypeError) as e:
            return r.fail(f"Failed to list plugins: {e}")

    def _execute_query_sql(
        self,
        sql: str,
    ) -> r[FlextDbOracleModels.DbOracle.QueryResult]:
        """Execute SQL query and return results as QueryResult."""
        try:
            return self._services.execute_query(sql).map(
                lambda data: self._convert_to_query_result(sql, data),
            )
        except Exception as e:
            return r.fail(f"SQL execution error: {e}")

    def _convert_to_query_result(
        self,
        sql: str,
        data: list[dict[str, t.JsonValue]],
    ) -> FlextDbOracleModels.DbOracle.QueryResult:
        """Convert raw query data to QueryResult model."""
        if not isinstance(data, list) or not data:
            return FlextDbOracleModels.DbOracle.QueryResult(
                query=sql,
                columns=[],
                rows=[],
                row_count=0,
            )

        first_row = data[0]
        if isinstance(first_row, dict):
            columns = list(first_row.keys())
            rows = [list(row.values()) for row in data]
        else:
            columns, rows = [], []

        return FlextDbOracleModels.DbOracle.QueryResult(
            query=sql,
            columns=columns,
            rows=rows,
            row_count=len(data),
        )

    def get_health_status(self) -> r[dict[str, t.JsonValue]]:
        """Get database connection health status."""
        try:
            status: dict[str, t.JsonValue] = {
                "connected": self.is_connected,
                "host": self._oracle_config.host,
                "port": self._oracle_config.port,
                "service_name": self._oracle_config.service_name,
            }
            return r.ok(status)
        except Exception as e:
            return r.fail(f"Health check failed: {e}")

    @property
    def connection(self) -> FlextDbOracleServices | None:
        """Get connection object - public interface."""
        return self._services if self._services.is_connected() else None

    @property
    def _dispatch_enabled(self) -> bool:
        """Check if dispatcher is enabled."""
        return self._dispatcher is not None

    def __enter__(self) -> Self:
        """Context manager entry."""
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: types.TracebackType | None,
    ) -> None:
        """Context manager exit - cleanup resources."""
        if hasattr(self._services, "disconnect"):
            with contextlib.suppress(Exception):
                self.logger.debug("Disconnecting on context exit")
                self._services.disconnect()

    def execute(self, **_kwargs: t.JsonValue) -> r[FlextDbOracleSettings]:
        """Execute default domain service operation - return config."""
        try:
            return r.ok(self._oracle_config)
        except Exception as e:
            return r.fail(f"API execution failed: {e}")

    @override
    def __repr__(self) -> str:
        """Return string representation of the API instance."""
        status = "connected" if self.is_connected else "disconnected"
        return f"FlextDbOracleApi(host={self._oracle_config.host}, status={status})"
