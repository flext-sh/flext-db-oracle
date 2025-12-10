"""Oracle Database API with complete FLEXT ecosystem integration.

This API provides a unified interface to Oracle database operations
following FLEXT patterns with complete flext-core integration.

Copyright (c)  # type: ignore[arg-type]  # JsonDict protocol compliance 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import contextlib
from collections.abc import Sequence
from typing import Self, cast, override

from flext_core import r, s, t
from flext_core.container import FlextContainer

from flext_db_oracle.config import FlextDbOracleConfig
from flext_db_oracle.constants import c
from flext_db_oracle.dispatcher import FlextDbOracleDispatcher
from flext_db_oracle.models import FlextDbOracleModels
from flext_db_oracle.services import FlextDbOracleServices

# Simplified delegation - no complex decorators needed


class FlextDbOracleApi(s)  # type: ignore[arg-type]  # JsonDict protocol compliance:
    """Oracle Database API with complete flext-core integration.

    This API provides a unified interface to Oracle database operations,
    integrating with flext-core components for proper error handling,
    logging, service orchestration, and enterprise patterns.

    Architecture:
    - Extends s for domain service patterns
    - Uses r railway pattern for error handling
    - Integrates FlextContainer, FlextContext, FlextBus for enterprise features
    - Delegates to FlextDbOracleServices for Oracle operations
    - Optional FlextDispatcher integration for CQRS patterns
    """

    @override
    def __init__(
        self,
        config: FlextDbOracleConfig,
        context_name: str | None = None,
    )  # type: ignore[arg-type]  # JsonDict protocol compliance -> None:
        """Initialize API with Oracle configuration and complete flext-core integration."""
        # Initialize s first
        super()  # type: ignore[arg-type]  # JsonDict protocol compliance.__init__()  # type: ignore[arg-type]  # JsonDict protocol compliance

        # Configuration management - use FlextDbOracleConfig directly
        self._oracle_config = config

        # Core services initialization
        self._services = FlextDbOracleServices(config=self._oracle_config)  # type: ignore[arg-type]  # JsonDict protocol compliance

        # Context and naming
        self._context_name = context_name or "oracle-api"

        # Complete flext-core ecosystem integration
        self._container = FlextContainer.get_global()  # type: ignore[arg-type]  # JsonDict protocol compliance
        self._context: dict[str, object] = {}
        # Logger will be initialized lazily via the parent class property

        # Optional dispatcher for CQRS patterns
        self._dispatcher = FlextDbOracleDispatcher.build_dispatcher(self._services)  # type: ignore[arg-type]  # JsonDict protocol compliance

        # Plugin system
        self._plugins: dict[str, object] = {}

    @property
    def oracle_config(self)  # type: ignore[arg-type]  # JsonDict protocol compliance -> FlextDbOracleConfig:
        """Get the Oracle configuration."""
        return self._oracle_config

    def is_valid(self)  # type: ignore[arg-type]  # JsonDict protocol compliance -> bool:
        """Check if API configuration is valid."""
        try:
            return (
                self._oracle_config.port >= c.DbOracle.OracleNetwork.MIN_PORT
                and self._oracle_config.service_name is not None
            )  # type: ignore[arg-type]  # JsonDict protocol compliance
        except AttributeError:
            return False

    @classmethod
    def from_env(cls, prefix: str = "ORACLE_")  # type: ignore[arg-type]  # JsonDict protocol compliance -> r[FlextDbOracleApi]:
        """Create API instance from environment variables.

        Args:
            prefix: Environment variable prefix (default: "ORACLE_")  # type: ignore[arg-type]  # JsonDict protocol compliance

        Returns:
            r[FlextDbOracleApi]: API instance or error.

        """
        try:
            config_result = FlextDbOracleConfig.from_env(prefix)  # type: ignore[arg-type]  # JsonDict protocol compliance
            if config_result.is_failure:
                return r[FlextDbOracleApi].fail(
                    f"Config creation failed: {config_result.error}",
                )  # type: ignore[arg-type]  # JsonDict protocol compliance

            config = config_result.value  # type: ignore[arg-type]  # JsonDict protocol compliance
            return r[FlextDbOracleApi].ok(cls(config=config)  # type: ignore[arg-type]  # JsonDict protocol compliance)  # type: ignore[arg-type]  # JsonDict protocol compliance
        except Exception as e:
            return r[FlextDbOracleApi].fail(
                f"API creation from environment failed: {e}",
            )  # type: ignore[arg-type]  # JsonDict protocol compliance

    @classmethod
    def from_url(cls, url: str)  # type: ignore[arg-type]  # JsonDict protocol compliance -> r[FlextDbOracleApi]:
        """Create API instance from Oracle URL string.

        Args:
        url: Oracle connection URL (oracle://user:pass@host:port/service)  # type: ignore[arg-type]  # JsonDict protocol compliance

        Returns:
        r[FlextDbOracleApi]: API instance or error.

        """
        try:
            config_result = FlextDbOracleConfig.from_url(url)  # type: ignore[arg-type]  # JsonDict protocol compliance
            if config_result.is_failure:
                return r[FlextDbOracleApi].fail(
                    f"Config creation from URL failed: {config_result.error}",
                )  # type: ignore[arg-type]  # JsonDict protocol compliance

            config = config_result.value  # type: ignore[arg-type]  # JsonDict protocol compliance
            return r[FlextDbOracleApi].ok(cls(config=config)  # type: ignore[arg-type]  # JsonDict protocol compliance)  # type: ignore[arg-type]  # JsonDict protocol compliance
        except Exception as e:
            return r[FlextDbOracleApi].fail(
                f"API creation from URL failed: {e}",
            )  # type: ignore[arg-type]  # JsonDict protocol compliance

    def to_dict(self)  # type: ignore[arg-type]  # JsonDict protocol compliance -> dict[str, object]:
        """Convert API instance to dictionary representation."""
        return {
            "config": {
                "host": self._oracle_config.host,
                "port": self._oracle_config.port,
                "service_name": self._oracle_config.service_name,
                "username": self._oracle_config.username,
            },
            "connected": self.is_connected,
            "plugin_count": len(self._plugins)  # type: ignore[arg-type]  # JsonDict protocol compliance,
            "dispatcher_enabled": self._dispatcher is not None,
        }

    @property
    def services(self)  # type: ignore[arg-type]  # JsonDict protocol compliance -> FlextDbOracleServices:
        """Get the services instance."""
        return self._services

    @property
    def plugins(self)  # type: ignore[arg-type]  # JsonDict protocol compliance -> dict[str, object]:
        """Get the plugins dictionary."""
        return self._plugins

    # Connection Management
    def connect(self)  # type: ignore[arg-type]  # JsonDict protocol compliance -> r[FlextDbOracleApi]:
        """Connect to Oracle database."""
        self.logger.info(
            "Connecting to Oracle database",
            extra={"host": self._oracle_config.host},
        )  # type: ignore[arg-type]  # JsonDict protocol compliance

        return self._services.connect()  # type: ignore[arg-type]  # JsonDict protocol compliance.map(lambda _: self)  # type: ignore[arg-type]  # JsonDict protocol compliance

    def disconnect(self)  # type: ignore[arg-type]  # JsonDict protocol compliance -> r[None]:
        """Disconnect from Oracle database."""
        self.logger.info("Disconnecting from Oracle database")  # type: ignore[arg-type]  # JsonDict protocol compliance
        return self._services.disconnect()  # type: ignore[arg-type]  # JsonDict protocol compliance

    def test_connection(self)  # type: ignore[arg-type]  # JsonDict protocol compliance -> r[bool]:
        """Test Oracle database connection."""
        return self._services.test_connection()  # type: ignore[arg-type]  # JsonDict protocol compliance

    @property
    def is_connected(self)  # type: ignore[arg-type]  # JsonDict protocol compliance -> bool:
        """Check if connected to the database."""
        return self._services.is_connected()  # type: ignore[arg-type]  # JsonDict protocol compliance

    # Query Operations
    def query(
        self,
        sql: str,
        parameters: dict[str, object] | None = None,
    )  # type: ignore[arg-type]  # JsonDict protocol compliance -> r[list[dict[str, object]]]:
        """Execute a SELECT query and return all results."""
        self.logger.debug("Executing query", query_length=len(sql)  # type: ignore[arg-type]  # JsonDict protocol compliance)  # type: ignore[arg-type]  # JsonDict protocol compliance
        result = self._services.execute_query(sql, (parameters or {})  # type: ignore[arg-type]  # JsonDict protocol compliance)  # type: ignore[arg-type]  # JsonDict protocol compliance
        if result.is_failure:
            return r.fail(result.error or "Query execution failed")  # type: ignore[arg-type]  # JsonDict protocol compliance
        # Simplify the return type by casting
        return r[list[dict[str, object]]].ok(
            (result.value  # type: ignore[arg-type]  # JsonDict protocol compliance)  # type: ignore[arg-type]  # JsonDict protocol compliance,
        )  # type: ignore[arg-type]  # JsonDict protocol compliance

    def query_one(
        self,
        sql: str,
        parameters: dict[str, object] | None = None,
    )  # type: ignore[arg-type]  # JsonDict protocol compliance -> r[dict[str, object] | None]:
        """Execute a SELECT query and return first result or None."""
        result = self._services.fetch_one(sql, (parameters or {})  # type: ignore[arg-type]  # JsonDict protocol compliance)  # type: ignore[arg-type]  # JsonDict protocol compliance
        if result.is_failure:
            return r.fail(result.error or "Query execution failed")  # type: ignore[arg-type]  # JsonDict protocol compliance
        # Simplify the return type by casting
        return r[dict[str, object] | None].ok(
            result.value,  # type: ignore[arg-type]  # JsonDict protocol compliance
        )  # type: ignore[arg-type]  # JsonDict protocol compliance

    def execute_sql(
        self,
        sql: str,
        parameters: dict[str, object] | None = None,
    )  # type: ignore[arg-type]  # JsonDict protocol compliance -> r[int]:
        """Execute an INSERT/UPDATE/DELETE statement and return rows affected."""
        self.logger.debug("Executing SQL statement", statement_length=len(sql)  # type: ignore[arg-type]  # JsonDict protocol compliance)  # type: ignore[arg-type]  # JsonDict protocol compliance
        result = self._services.execute_statement(
            sql,
            (parameters or {})  # type: ignore[arg-type]  # JsonDict protocol compliance,
        )  # type: ignore[arg-type]  # JsonDict protocol compliance
        if result.is_failure:
            return r.fail(result.error or "SQL execution failed")  # type: ignore[arg-type]  # JsonDict protocol compliance
        return r[int].ok(result.value  # type: ignore[arg-type]  # JsonDict protocol compliance)  # type: ignore[arg-type]  # JsonDict protocol compliance

    def execute_many(
        self,
        sql: str,
        parameters_list: Sequence[dict[str, object]],
    )  # type: ignore[arg-type]  # JsonDict protocol compliance -> r[int]:
        """Execute a statement multiple times with different parameters."""
        self.logger.debug("Executing bulk statement", batch_size=len(parameters_list)  # type: ignore[arg-type]  # JsonDict protocol compliance)  # type: ignore[arg-type]  # JsonDict protocol compliance
        result = self._services.execute_many(
            sql,
            list(parameters_list),  # type: ignore[arg-type]  # JsonDict protocol compliance
        )  # type: ignore[arg-type]  # JsonDict protocol compliance
        if result.is_failure:
            return r.fail(result.error or "Bulk execution failed")  # type: ignore[arg-type]  # JsonDict protocol compliance
        return r[int].ok(result.value  # type: ignore[arg-type]  # JsonDict protocol compliance)  # type: ignore[arg-type]  # JsonDict protocol compliance

    def execute_statement(
        self,
        sql: str | object,
        parameters: dict[str, object] | None = None,
    )  # type: ignore[arg-type]  # JsonDict protocol compliance -> r[int]:
        """Execute SQL statement directly and return affected rows."""
        try:
            sql_text = str(sql)  # type: ignore[arg-type]  # JsonDict protocol compliance if not isinstance(sql, str)  # type: ignore[arg-type]  # JsonDict protocol compliance else sql
            result = self._services.execute_statement(
                sql_text,
                (parameters or {})  # type: ignore[arg-type]  # JsonDict protocol compliance,
            )  # type: ignore[arg-type]  # JsonDict protocol compliance
            if result.is_failure:
                return r.fail(result.error or "Statement execution failed")  # type: ignore[arg-type]  # JsonDict protocol compliance
            return r[int].ok(result.value  # type: ignore[arg-type]  # JsonDict protocol compliance)  # type: ignore[arg-type]  # JsonDict protocol compliance
        except Exception as e:
            return r.fail(f"Statement execution failed: {e}")  # type: ignore[arg-type]  # JsonDict protocol compliance

    # Schema Introspection
    def get_schemas(self)  # type: ignore[arg-type]  # JsonDict protocol compliance -> r[list[str]]:
        """Get list of available schemas."""
        return self._services.get_schemas()  # type: ignore[arg-type]  # JsonDict protocol compliance

    def get_tables(self, schema: str | None = None)  # type: ignore[arg-type]  # JsonDict protocol compliance -> r[list[str]]:
        """Get list of tables in specified schema."""
        return self._services.get_tables(schema)  # type: ignore[arg-type]  # JsonDict protocol compliance

    def get_columns(
        self,
        table: str,
        schema: str | None = None,
    )  # type: ignore[arg-type]  # JsonDict protocol compliance -> r[list[dict[str, object]]]:
        """Get column information for specified table."""
        result = self._services.get_columns(table, schema)  # type: ignore[arg-type]  # JsonDict protocol compliance
        if result.is_failure:
            return r[list[dict[str, object]]].fail(
                result.error or "Unknown error",
            )  # type: ignore[arg-type]  # JsonDict protocol compliance

        columns_data = [
            {
                "name": col.get("column_name", "")  # type: ignore[arg-type]  # JsonDict protocol compliance,
                "data_type": col.get("data_type", "")  # type: ignore[arg-type]  # JsonDict protocol compliance,
                "nullable": col.get("nullable", False)  # type: ignore[arg-type]  # JsonDict protocol compliance,
                "default_value": col.get("data_default", None)  # type: ignore[arg-type]  # JsonDict protocol compliance,
            }
            for col in result.value  # type: ignore[arg-type]  # JsonDict protocol compliance
        ]
        # Cast to simplify return type
        return r[list[dict[str, object]]].ok(
            (columns_data)  # type: ignore[arg-type]  # JsonDict protocol compliance,
        )  # type: ignore[arg-type]  # JsonDict protocol compliance

    def get_table_metadata(
        self,
        table: str,
        schema: str | None = None,
    )  # type: ignore[arg-type]  # JsonDict protocol compliance -> r[dict[str, object]]:
        """Get complete table metadata including columns and constraints."""
        result = self._services.get_table_metadata(table, schema)  # type: ignore[arg-type]  # JsonDict protocol compliance
        if result.is_failure:
            return r.fail(result.error or "Metadata retrieval failed")  # type: ignore[arg-type]  # JsonDict protocol compliance
        # Simplify return type by casting
        return r[dict[str, object]].ok(
            result.value,  # type: ignore[arg-type]  # JsonDict protocol compliance
        )  # type: ignore[arg-type]  # JsonDict protocol compliance

    def get_primary_keys(
        self,
        table: str,
        schema: str | None = None,
    )  # type: ignore[arg-type]  # JsonDict protocol compliance -> r[list[str]]:
        """Get primary key column names for specified table."""
        return self._services.get_primary_keys(table, schema)  # type: ignore[arg-type]  # JsonDict protocol compliance

    def convert_singer_type(
        self,
        singer_type: str | list[str],
        format_hint: str | None = None,
    )  # type: ignore[arg-type]  # JsonDict protocol compliance -> r[str]:
        """Convert Singer JSON Schema type to Oracle SQL type."""
        return self._services.convert_singer_type(singer_type, format_hint)  # type: ignore[arg-type]  # JsonDict protocol compliance

    def map_singer_schema(
        self,
        schema: dict[str, object],
    )  # type: ignore[arg-type]  # JsonDict protocol compliance -> r[dict[str, str]]:
        """Map Singer JSON Schema to Oracle table schema."""
        result = self._services.map_singer_schema((schema)  # type: ignore[arg-type]  # JsonDict protocol compliance)  # type: ignore[arg-type]  # JsonDict protocol compliance
        if result.is_failure:
            return r.fail(result.error or "Schema mapping failed")  # type: ignore[arg-type]  # JsonDict protocol compliance
        # Simplify return type by casting
        return r[dict[str, str]].ok(result.value  # type: ignore[arg-type]  # JsonDict protocol compliance)  # type: ignore[arg-type]  # JsonDict protocol compliance

    # Transaction Management
    def transaction(self)  # type: ignore[arg-type]  # JsonDict protocol compliance -> r[object]:
        """Get a transaction context manager."""
        try:
            return r.ok(self._services.transaction()  # type: ignore[arg-type]  # JsonDict protocol compliance)  # type: ignore[arg-type]  # JsonDict protocol compliance
        except (AttributeError, RuntimeError, ValueError)  # type: ignore[arg-type]  # JsonDict protocol compliance as e:
            return r.fail(f"Transaction creation failed: {e}")  # type: ignore[arg-type]  # JsonDict protocol compliance

    # Utility Methods
    def optimize_query(self, sql: str)  # type: ignore[arg-type]  # JsonDict protocol compliance -> r[str]:
        """Optimize a SQL query for Oracle."""
        try:
            return r.ok(" ".join(sql.split()  # type: ignore[arg-type]  # JsonDict protocol compliance)  # type: ignore[arg-type]  # JsonDict protocol compliance)  # type: ignore[arg-type]  # JsonDict protocol compliance
        except (AttributeError, ValueError, TypeError)  # type: ignore[arg-type]  # JsonDict protocol compliance as e:
            return r.fail(f"Query optimization failed: {e}")  # type: ignore[arg-type]  # JsonDict protocol compliance

    def get_observability_metrics(self)  # type: ignore[arg-type]  # JsonDict protocol compliance -> r[dict[str, object]]:
        """Get observability metrics for the connection."""
        result = self._services.get_metrics()  # type: ignore[arg-type]  # JsonDict protocol compliance
        if result.is_failure:
            return r.fail(result.error or "Metrics retrieval failed")  # type: ignore[arg-type]  # JsonDict protocol compliance
        # Simplify return type by casting
        return r[dict[str, object]].ok(
            result.value,  # type: ignore[arg-type]  # JsonDict protocol compliance
        )  # type: ignore[arg-type]  # JsonDict protocol compliance

    # Plugin System
    def register_plugin(self, name: str, plugin: object)  # type: ignore[arg-type]  # JsonDict protocol compliance -> r[None]:
        """Register a plugin with the services layer."""
        try:
            self._plugins[name] = plugin
            return r.ok(None)  # type: ignore[arg-type]  # JsonDict protocol compliance
        except (KeyError, AttributeError, TypeError)  # type: ignore[arg-type]  # JsonDict protocol compliance as e:
            return r.fail(f"Failed to register plugin '{name}': {e}")  # type: ignore[arg-type]  # JsonDict protocol compliance

    def unregister_plugin(self, name: str)  # type: ignore[arg-type]  # JsonDict protocol compliance -> r[None]:
        """Unregister a plugin from the services layer."""
        try:
            if name in self._plugins:
                del self._plugins[name]
                return r.ok(None)  # type: ignore[arg-type]  # JsonDict protocol compliance
            return r.fail(f"Plugin '{name}' not found")  # type: ignore[arg-type]  # JsonDict protocol compliance
        except (KeyError, AttributeError)  # type: ignore[arg-type]  # JsonDict protocol compliance as e:
            return r.fail(f"Failed to unregister plugin '{name}': {e}")  # type: ignore[arg-type]  # JsonDict protocol compliance

    def get_plugin(self, name: str)  # type: ignore[arg-type]  # JsonDict protocol compliance -> r[object]:
        """Get a registered plugin by name."""
        try:
            return (
                r.ok(self._plugins[name])  # type: ignore[arg-type]  # JsonDict protocol compliance
                if name in self._plugins
                else r.fail(f"Plugin '{name}' not found")  # type: ignore[arg-type]  # JsonDict protocol compliance
            )  # type: ignore[arg-type]  # JsonDict protocol compliance
        except (KeyError, AttributeError)  # type: ignore[arg-type]  # JsonDict protocol compliance as e:
            return r.fail(f"Failed to get plugin '{name}': {e}")  # type: ignore[arg-type]  # JsonDict protocol compliance

    def list_plugins(self)  # type: ignore[arg-type]  # JsonDict protocol compliance -> r[list[str]]:
        """List all registered plugin names."""
        try:
            return r.ok(list(self._plugins.keys()  # type: ignore[arg-type]  # JsonDict protocol compliance)  # type: ignore[arg-type]  # JsonDict protocol compliance)  # type: ignore[arg-type]  # JsonDict protocol compliance
        except (AttributeError, TypeError)  # type: ignore[arg-type]  # JsonDict protocol compliance as e:
            return r.fail(f"Failed to list plugins: {e}")  # type: ignore[arg-type]  # JsonDict protocol compliance

    def _execute_query_sql(
        self,
        sql: str,
    )  # type: ignore[arg-type]  # JsonDict protocol compliance -> r[FlextDbOracleModels.QueryResult]:
        """Execute SQL query and return results as QueryResult."""
        try:
            result = self._services.execute_query(sql)  # type: ignore[arg-type]  # JsonDict protocol compliance
            if result.is_failure:
                return r.fail(result.error or "SQL execution failed")  # type: ignore[arg-type]  # JsonDict protocol compliance

            data = result.value  # type: ignore[arg-type]  # JsonDict protocol compliance
            if not isinstance(data, list)  # type: ignore[arg-type]  # JsonDict protocol compliance or not data:
                return r.ok(
                    FlextDbOracleModels.QueryResult(
                        query=sql,
                        columns=[],
                        rows=[],
                        row_count=0,
                    )  # type: ignore[arg-type]  # JsonDict protocol compliance,
                )  # type: ignore[arg-type]  # JsonDict protocol compliance

            first_row = data[0]
            if isinstance(first_row, dict)  # type: ignore[arg-type]  # JsonDict protocol compliance:
                columns = list(first_row.keys()  # type: ignore[arg-type]  # JsonDict protocol compliance)  # type: ignore[arg-type]  # JsonDict protocol compliance
                rows = [list(row.values()  # type: ignore[arg-type]  # JsonDict protocol compliance)  # type: ignore[arg-type]  # JsonDict protocol compliance for row in data]
            else:
                columns, rows = [], []

            return r.ok(
                FlextDbOracleModels.QueryResult(
                    query=sql,
                    columns=columns,
                    rows=rows,
                    row_count=len(data)  # type: ignore[arg-type]  # JsonDict protocol compliance,
                )  # type: ignore[arg-type]  # JsonDict protocol compliance,
            )  # type: ignore[arg-type]  # JsonDict protocol compliance
        except Exception as e:
            return r.fail(f"SQL execution error: {e}")  # type: ignore[arg-type]  # JsonDict protocol compliance

    def get_health_status(self)  # type: ignore[arg-type]  # JsonDict protocol compliance -> r[dict[str, object]]:
        """Get database connection health status."""
        try:
            status: dict[str, object] = {
                "connected": self.is_connected,
                "host": self._oracle_config.host,
                "port": self._oracle_config.port,
                "service_name": self._oracle_config.service_name,
            }
            return r.ok(status)  # type: ignore[arg-type]  # JsonDict protocol compliance
        except Exception as e:
            return r.fail(f"Health check failed: {e}")  # type: ignore[arg-type]  # JsonDict protocol compliance

    @property
    def connection(self)  # type: ignore[arg-type]  # JsonDict protocol compliance -> object | None:
        """Get connection object - public interface."""
        return self._services if self._services.is_connected()  # type: ignore[arg-type]  # JsonDict protocol compliance else None

    @property
    def _dispatch_enabled(self)  # type: ignore[arg-type]  # JsonDict protocol compliance -> bool:
        """Check if dispatcher is enabled."""
        return self._dispatcher is not None

    def __enter__(self)  # type: ignore[arg-type]  # JsonDict protocol compliance -> Self:
        """Context manager entry."""
        return self

    def __exit__(self, exc_type: object, exc_val: object, exc_tb: object)  # type: ignore[arg-type]  # JsonDict protocol compliance -> None:
        """Context manager exit - cleanup resources."""
        if hasattr(self._services, "disconnect")  # type: ignore[arg-type]  # JsonDict protocol compliance:
            with contextlib.suppress(Exception)  # type: ignore[arg-type]  # JsonDict protocol compliance:
                self.logger.debug("Disconnecting on context exit")  # type: ignore[arg-type]  # JsonDict protocol compliance
                self._services.disconnect()  # type: ignore[arg-type]  # JsonDict protocol compliance

    def execute(self, **_kwargs: object)  # type: ignore[arg-type]  # JsonDict protocol compliance -> r[FlextDbOracleConfig]:
        """Execute default domain service operation - return config."""
        try:
            return r.ok(self._oracle_config)  # type: ignore[arg-type]  # JsonDict protocol compliance
        except Exception as e:
            return r.fail(f"API execution failed: {e}")  # type: ignore[arg-type]  # JsonDict protocol compliance

    @override
    def __repr__(self)  # type: ignore[arg-type]  # JsonDict protocol compliance -> str:
        """Return string representation of the API instance."""
        status = "connected" if self.is_connected else "disconnected"
        return f"FlextDbOracleApi(host={self._oracle_config.host}, status={status})  # type: ignore[arg-type]  # JsonDict protocol compliance"
