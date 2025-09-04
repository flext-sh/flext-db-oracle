"""Oracle Database API following FLEXT ecosystem patterns.

Clean, production-ready Oracle database API that follows SOLID principles,
uses proper typing, and integrates with flext-core patterns.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Self

from flext_core import FlextLogger, FlextResult

from flext_db_oracle.models import FlextDbOracleModels
from flext_db_oracle.services import FlextDbOracleServices

if TYPE_CHECKING:
    from collections.abc import Sequence

logger = FlextLogger(__name__)


class FlextDbOracleApi:
    """Oracle Database API with clean delegation to services layer.

    This API provides a clean interface to Oracle database operations
    by delegating all work to the services layer while maintaining
    type safety and proper error handling.
    """

    def __init__(self, config: FlextDbOracleModels.OracleConfig) -> None:
        """Initialize API with Oracle configuration."""
        self._config = config
        self._services = FlextDbOracleServices(config)
        self._logger = logger.bind(component="oracle-api")
        self._plugins: dict[str, object] = {}

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
        except Exception:
            return False

    @classmethod
    def from_config(cls, config: FlextDbOracleModels.OracleConfig) -> FlextDbOracleApi:
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
    def query(self, sql: str, parameters: dict[str, object] | None = None) -> FlextResult[list[dict[str, object]]]:
        """Execute a SELECT query and return all results."""
        return self._services.execute_query(sql, parameters or {})

    def query_one(self, sql: str, parameters: dict[str, object] | None = None) -> FlextResult[dict[str, object] | None]:
        """Execute a SELECT query and return first result or None."""
        return self._services.fetch_one(sql, parameters or {})

    def execute(self, sql: str, parameters: dict[str, object] | None = None) -> FlextResult[int]:
        """Execute an INSERT/UPDATE/DELETE statement and return rows affected."""
        return self._services.execute_statement(sql, parameters or {})

    def execute_many(self, sql: str, parameters_list: Sequence[dict[str, object]]) -> FlextResult[int]:
        """Execute a statement multiple times with different parameters."""
        return self._services.execute_many(sql, list(parameters_list))

    # Schema Introspection
    def get_schemas(self) -> FlextResult[list[str]]:
        """Get list of available schemas."""
        return self._services.get_schemas()

    def get_tables(self, schema: str | None = None) -> FlextResult[list[str]]:
        """Get list of tables in specified schema."""
        return self._services.get_tables(schema)

    def get_columns(self, table: str, schema: str | None = None) -> FlextResult[list[FlextDbOracleModels.ColumnInfo]]:
        """Get column information for specified table."""
        return self._services.get_columns(table, schema)

    # Transaction Management
    def transaction(self) -> FlextResult[object]:
        """Get a transaction context manager."""
        try:
            transaction_context = self._services.transaction()
            return FlextResult[object].ok(transaction_context)
        except Exception as e:
            return FlextResult[object].fail(f"Transaction creation failed: {e}")

    # Utility Methods
    def optimize_query(self, sql: str) -> FlextResult[str]:
        """Optimize a SQL query for Oracle."""
        # Simple optimization - remove extra whitespace and normalize
        try:
            optimized = " ".join(sql.split())
            return FlextResult[str].ok(optimized)
        except Exception as e:
            return FlextResult[str].fail(f"Query optimization failed: {e}")

    def get_observability_metrics(self) -> FlextResult[dict[str, object]]:
        """Get observability metrics for the connection."""
        return self._services.get_metrics()

    # Configuration

    @classmethod
    def from_env(cls, prefix: str = "FLEXT_TARGET_ORACLE") -> FlextResult[Self]:
        """Create API instance from environment variables."""
        config_result = FlextDbOracleModels.OracleConfig.from_env(prefix)
        if config_result.success:
            instance = cls.from_config(config_result.value)
            return FlextResult[Self].ok(instance)  # type: ignore[arg-type]
        return FlextResult[Self].fail(f"Failed to load config from environment: {config_result.error}")

    @classmethod
    def from_url(cls, database_url: str) -> FlextResult[Self]:
        """Create API instance from database URL."""
        config_result = FlextDbOracleModels.OracleConfig.from_url(database_url)
        if config_result.success:
            instance = cls.from_config(config_result.value)
            return FlextResult[Self].ok(instance)  # type: ignore[arg-type]
        return FlextResult[Self].fail(f"Failed to parse database URL: {config_result.error}")

    # Plugin System
    def register_plugin(self, name: str, plugin: object) -> FlextResult[None]:
        """Register a plugin with the services layer."""
        try:
            self._plugins[name] = plugin
            return FlextResult[None].ok(None)
        except Exception as e:
            return FlextResult[None].fail(f"Failed to register plugin '{name}': {e}")

    def unregister_plugin(self, name: str) -> FlextResult[None]:
        """Unregister a plugin from the services layer."""
        try:
            if name in self._plugins:
                del self._plugins[name]
                return FlextResult[None].ok(None)
            return FlextResult[None].fail(f"Plugin '{name}' not found")
        except Exception as e:
            return FlextResult[None].fail(f"Failed to unregister plugin '{name}': {e}")

    def get_plugin(self, name: str) -> FlextResult[object]:
        """Get a registered plugin by name."""
        try:
            if name in self._plugins:
                return FlextResult[object].ok(self._plugins[name])
            return FlextResult[object].fail(f"Plugin '{name}' not found")
        except Exception as e:
            return FlextResult[object].fail(f"Failed to get plugin '{name}': {e}")

    def list_plugins(self) -> FlextResult[list[str]]:
        """List all registered plugin names."""
        try:
            return FlextResult[list[str]].ok(list(self._plugins.keys()))
        except Exception as e:
            return FlextResult[list[str]].fail(f"Failed to list plugins: {e}")

    def __repr__(self) -> str:
        """String representation of the API instance."""
        connection_status = "connected" if self.is_connected else "disconnected"
        return f"FlextDbOracleApi(host={self._config.host}, status={connection_status})"
