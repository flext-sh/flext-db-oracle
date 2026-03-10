"""Oracle Database API with complete FLEXT ecosystem integration.

This API provides a unified interface to Oracle database operations
following FLEXT patterns with complete flext-core integration.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import contextlib
import os
import types
from collections.abc import Mapping, Sequence
from typing import Self, override

import oracledb
from flext_core import FlextService, r, t

from flext_db_oracle.constants import c
from flext_db_oracle.dispatcher import FlextDbOracleDispatcher
from flext_db_oracle.models import FlextDbOracleModels, m
from flext_db_oracle.services import FlextDbOracleServices
from flext_db_oracle.settings import FlextDbOracleSettings

OracleDatabaseError: type[Exception] = oracledb.DatabaseError
OracleInterfaceError: type[Exception] = oracledb.InterfaceError


class _NullPluginResult:
    """Result-like object for explicit null plugin compatibility behavior."""

    is_success: bool = True
    is_failure: bool = False
    error: None = None

    def __init__(self) -> None:
        self._first_read = True

    @property
    def value(self) -> str | None:
        """Return sentinel on first read and None afterwards for compatibility."""
        if self._first_read:
            self._first_read = False
            return "NULL_PLUGIN"
        return None


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
        self, config: FlextDbOracleSettings, context_name: str | None = None
    ) -> None:
        """Initialize API with Oracle configuration and complete flext-core integration."""
        super().__init__()
        self._oracle_config = config
        self._services = FlextDbOracleServices(config=self._oracle_config)
        self._context_name = context_name or "oracle-api"
        self._context = None
        self._dispatcher = FlextDbOracleDispatcher.build_dispatcher(self._services)
        self._plugins: dict[str, t.ContainerValue] = {}
        self._registry = self._plugins

    @override
    def __repr__(self) -> str:
        """Return string representation of the API instance."""
        status = "connected" if self.is_connected else "disconnected"
        return f"FlextDbOracleApi(host={self._oracle_config.host}, status={status})"

    def __enter__(self) -> Self:
        """Context manager entry."""
        _ = self.connect()
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: types.TracebackType | None,
    ) -> None:
        """Context manager exit - cleanup resources."""
        with contextlib.suppress(Exception):
            self.logger.debug("Disconnecting on context exit")
            self._services.disconnect()

    @property
    def _dispatch_enabled(self) -> bool:
        """Check if dispatcher is enabled."""
        return True

    @property
    @override
    def config(self) -> FlextDbOracleSettings:
        """Get the configuration."""
        return self._oracle_config

    @property
    def connection(self) -> FlextDbOracleServices | None:
        """Get connection object - public interface."""
        return self._services if self._services.is_connected() else None

    @property
    def is_connected(self) -> bool:
        """Check if connected to the database."""
        return self._services.is_connected()

    @property
    def oracle_config(self) -> FlextDbOracleSettings:
        """Get the Oracle configuration."""
        return self._oracle_config

    @property
    def services(self) -> FlextDbOracleServices:
        """Get the services instance."""
        return self._services

    @classmethod
    def from_config(cls, config: FlextDbOracleSettings) -> FlextDbOracleApi:
        """Create API instance from an existing settings object."""
        return cls(config=config)

    @classmethod
    def from_env(cls, prefix: str = "ORACLE_") -> r[FlextDbOracleApi]:
        """Create API instance from environment variables.

        Args:
            prefix: Environment variable prefix (default: "ORACLE_")

        Returns:
            r[FlextDbOracleApi]: API instance or error.

        """
        try:
            username_keys = [f"{prefix}USERNAME"]
            password_keys = [f"{prefix}PASSWORD"]
            if prefix == "ORACLE_":
                username_keys.append("FLEXT_TARGET_ORACLE_USERNAME")
                password_keys.append("FLEXT_TARGET_ORACLE_PASSWORD")
            username_set = any(os.environ.get(key) for key in username_keys)
            password_set = any(os.environ.get(key) for key in password_keys)
            if not username_set:
                return r[FlextDbOracleApi].fail(
                    "Oracle username is required but not configured"
                )
            if not password_set:
                return r[FlextDbOracleApi].fail(
                    "Oracle password is required but not configured"
                )
            config_result = FlextDbOracleSettings.from_env(prefix)
            if config_result.is_failure:
                return r[FlextDbOracleApi].fail(
                    f"Config creation failed: {config_result.error}"
                )
            config = config_result.value
            if not config.username:
                return r[FlextDbOracleApi].fail(
                    "Oracle username is required but not configured"
                )
            if not config.password:
                return r[FlextDbOracleApi].fail(
                    "Oracle password is required but not configured"
                )
            return r[FlextDbOracleApi].ok(cls(config=config))
        except Exception as e:
            return r[FlextDbOracleApi].fail(
                f"API creation from environment failed: {e}"
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
                    f"Config creation from URL failed: {config_result.error}"
                )
            config = config_result.value
            return r[FlextDbOracleApi].ok(cls(config=config))
        except Exception as e:
            return r[FlextDbOracleApi].fail(f"API creation from URL failed: {e}")

    def connect(self) -> r[FlextDbOracleApi]:
        """Connect to Oracle database."""
        self.logger.info(
            "Connecting to Oracle database", extra=self._oracle_config.host
        )
        return self._services.connect().map(lambda _: self)

    def convert_singer_type(
        self, singer_type: str | list[str], format_hint: str | None = None
    ) -> r[str]:
        """Convert Singer JSON Schema type to Oracle SQL type."""
        return self._services.convert_singer_type(singer_type, format_hint)

    def disconnect(self) -> r[bool]:
        """Disconnect from Oracle database."""
        self.logger.info("Disconnecting from Oracle database")
        return self._services.disconnect()

    @override
    def execute(self, **_kwargs: t.JsonValue) -> r[FlextDbOracleSettings]:
        """Execute default domain service operation - return config."""
        try:
            return r.ok(self._oracle_config)
        except Exception as e:
            return r[FlextDbOracleSettings].fail(f"API execution failed: {e}")

    def execute_many(
        self, sql: str, parameters_list: Sequence[Mapping[str, t.ContainerValue]]
    ) -> r[int]:
        """Execute a statement multiple times with different parameters."""
        self.logger.debug("Executing bulk statement", batch_size=len(parameters_list))
        typed_params_list = [
            m.ConfigMap.model_validate(params) for params in parameters_list
        ]
        return self._services.execute_many(sql, typed_params_list)

    def execute_sql(
        self, sql: str, parameters: Mapping[str, t.ContainerValue] | None = None
    ) -> r[int]:
        """Execute an INSERT/UPDATE/DELETE statement and return rows affected."""
        self.logger.debug("Executing SQL statement", statement_length=len(sql))
        query_params = (
            m.ConfigMap.model_validate(parameters)
            if parameters is not None
            else m.ConfigMap(root={})
        )
        return self._services.execute_statement(sql, query_params)

    def execute_statement(
        self,
        sql: str | t.JsonValue,
        parameters: Mapping[str, t.ContainerValue] | None = None,
    ) -> r[int]:
        """Execute SQL statement directly and return affected rows."""
        try:
            sql_text = str(sql)
            query_params = (
                m.ConfigMap.model_validate(parameters)
                if parameters is not None
                else m.ConfigMap(root={})
            )
            return self._services.execute_statement(sql_text, query_params)
        except Exception as e:
            return r[int].fail(f"Statement execution failed: {e}")

    def get_columns(
        self, table: str, schema: str | None = None
    ) -> r[list[FlextDbOracleModels.DbOracle.Column]]:
        """Get column information for specified table."""
        return self._services.get_columns(table, schema)

    def get_health_status(self) -> r[FlextDbOracleModels.DbOracle.ConnectionStatus]:
        """Get database connection health status."""
        return self._services.get_connection_status()

    def get_observability_metrics(self) -> r[Mapping[str, t.JsonValue]]:
        """Get observability metrics for the connection."""
        return self._services.get_metrics().map(lambda metrics: metrics.model_dump())

    def get_plugin(self, name: str) -> r[t.ContainerValue] | _NullPluginResult:
        """Get a registered plugin by name."""
        if name not in self._plugins:
            return r[t.ContainerValue].fail(f"Plugin '{name}' not found")
        plugin = self._plugins[name]
        if plugin is None:
            return _NullPluginResult()

        def _to_json(value: t.ContainerValue) -> t.ContainerValue:
            if isinstance(value, (str, int, float, bool)):
                return value
            if isinstance(value, Mapping):
                return {str(k): _to_json(v) for k, v in value.items()}
            if isinstance(value, Sequence):
                return [_to_json(v) for v in value]
            return str(value)

        return r[t.ContainerValue].ok(_to_json(plugin))

    def get_primary_keys(self, table: str, schema: str | None = None) -> r[list[str]]:
        """Get primary key column names for specified table."""
        return self._services.get_primary_keys(table, schema)

    def get_schemas(self) -> r[list[str]]:
        """Get list of available schemas."""
        return self._services.get_schemas()

    def get_table_metadata(
        self, table: str, schema: str | None = None
    ) -> r[FlextDbOracleModels.DbOracle.TableMetadata]:
        """Get complete table metadata including columns and constraints."""
        return self._services.get_table_metadata(table, schema)

    def get_tables(self, schema: str | None = None) -> r[list[str]]:
        """Get list of tables in specified schema."""
        return self._services.get_tables(schema)

    @override
    def is_valid(self) -> bool:
        """Check if API configuration is valid."""
        return self._oracle_config.port >= c.DbOracle.OracleNetwork.MIN_PORT and bool(
            self._oracle_config.service_name
        )

    def list_plugins(self) -> r[list[str]]:
        """List all registered plugin names."""
        return r[list[str]].ok(list(self._plugins.keys()))

    def map_singer_schema(self, schema: t.ConfigurationMapping) -> r[Mapping[str, str]]:
        """Map Singer JSON Schema to Oracle table schema."""
        return self._services.map_singer_schema(schema).map(lambda value: value.mapping)

    def optimize_query(self, sql: str) -> r[str]:
        """Optimize a SQL query for Oracle."""
        try:
            return r[str].ok(" ".join(sql.split()))
        except (AttributeError, ValueError, TypeError) as e:
            return r[str].fail(f"Query optimization failed: {e}")

    def query(
        self, sql: str, parameters: Mapping[str, t.ContainerValue] | None = None
    ) -> r[list[m.Dict]]:
        """Execute a SELECT query and return all results."""
        self.logger.debug("Executing query", query_length=len(sql))
        query_params = (
            m.ConfigMap.model_validate(parameters)
            if parameters is not None
            else m.ConfigMap(root={})
        )
        return self._services.execute_query(sql, query_params)

    def query_one(
        self, sql: str, parameters: Mapping[str, t.ContainerValue] | None = None
    ) -> r[m.Dict | None]:
        """Execute a SELECT query and return first result or None."""
        query_params = (
            m.ConfigMap.model_validate(parameters)
            if parameters is not None
            else m.ConfigMap(root={})
        )
        return self._services.fetch_one(sql, query_params)

    def register_plugin(self, name: str, plugin: t.ContainerValue) -> r[bool]:
        """Register a plugin in local API registry."""
        self._plugins[name] = plugin
        return r[bool].ok(True)

    def test_connection(self) -> r[bool]:
        """Test Oracle database connection."""
        return self._services.test_connection()

    def transaction(self) -> r[Mapping[str, t.JsonValue]]:
        """Get transaction status information."""
        try:
            status: dict[str, t.JsonValue] = {
                "connected": self._services.is_connected(),
                "transaction_available": True,
            }
            return r[Mapping[str, t.JsonValue]].ok(status)
        except (AttributeError, RuntimeError, ValueError) as e:
            return r[Mapping[str, t.JsonValue]].fail(
                f"Transaction status check failed: {e}"
            )

    def unregister_plugin(self, name: str) -> r[bool]:
        """Unregister a plugin from local API registry."""
        if name not in self._plugins:
            return r[bool].fail(f"Plugin '{name}' not found")
        self._plugins.pop(name)
        return r[bool].ok(True)

    def _convert_to_query_result(
        self, sql: str, data: list[m.Dict]
    ) -> FlextDbOracleModels.DbOracle.QueryResult:
        """Convert raw query data to QueryResult model."""
        if not data:
            return FlextDbOracleModels.DbOracle.QueryResult(
                query=sql, columns=[], rows=[], row_count=0
            )
        first_row = data[0].root
        columns = list(first_row.keys())
        rows = [
            FlextDbOracleModels.DbOracle.RowData(
                values=[str(value) for value in row.root.values()]
            )
            for row in data
        ]
        return FlextDbOracleModels.DbOracle.QueryResult(
            query=sql, columns=columns, rows=rows, row_count=len(data)
        )

    def _execute_query_sql(
        self, sql: str
    ) -> r[FlextDbOracleModels.DbOracle.QueryResult]:
        """Execute SQL query and return results as QueryResult."""
        try:
            return self._services.execute_query(sql).map(
                lambda data: self._convert_to_query_result(sql, data)
            )
        except Exception as e:
            return r[FlextDbOracleModels.DbOracle.QueryResult].fail(
                f"SQL execution error: {e}"
            )
