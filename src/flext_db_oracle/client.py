"""Oracle Database client providing CLI and programmatic access.

This module provides the Oracle database client with CLI functionality
using FLEXT ecosystem patterns for database operations.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import json
from collections.abc import Callable
from typing import cast

from flext_core import (
    FlextContainer,
    FlextLogger,
    FlextResult,
)
from flext_db_oracle.api import FlextDbOracleApi
from flext_db_oracle.config import FlextDbOracleConfig
from flext_db_oracle.models import FlextDbOracleModels
from flext_db_oracle.typings import FlextDbOracleTypes

from .constants import FlextDbOracleConstants


class FlextDbOracleClient:
    """Oracle Database CLI client with proper FLEXT ecosystem integration.

    This client provides command-line interface operations for Oracle Database
    management using the flext-db-oracle foundation API.
    """

    def __init__(
        self, *, debug: bool = False, config: FlextDbOracleConfig | None = None
    ) -> None:
        """Initialize Oracle CLI client with proper composition."""
        # Core dependencies injected via composition
        self.container = FlextContainer.get_global()
        self.logger = FlextLogger(__name__)

        # Configuration - use provided or get from container/global instance
        self.config = config or FlextDbOracleConfig.get_global_instance()

        # Application state
        self.debug = debug
        self.current_connection: FlextDbOracleApi | None = None
        self.user_preferences: FlextDbOracleTypes.Connection.ConnectionConfiguration = {
            "default_output_format": "table",
            "auto_confirm_operations": "False",
            "show_execution_time": "True",
            "connection_timeout": FlextDbOracleConstants.Connection.DEFAULT_CONNECTION_TIMEOUT,
            "query_limit": FlextDbOracleConstants.Query.DEFAULT_QUERY_LIMIT,
        }

        self.logger.info("Oracle CLI client initialized")

    def connect_to_oracle(
        self,
        host: str | None = None,
        port: int | None = None,
        service_name: str | None = None,
        username: str | None = None,
        password: str | None = None,
    ) -> FlextResult[FlextDbOracleApi]:
        """Connect to Oracle database with provided parameters or config defaults.

        Returns:
            FlextResult[FlextDbOracleApi]: API instance or error.

        """
        try:
            # Use provided parameters or fall back to config defaults
            actual_host = host or self.config.oracle_host
            actual_port = port or self.config.oracle_port
            actual_service_name = service_name or self.config.oracle_service_name
            actual_username = username or self.config.oracle_username
            actual_password = password or self.config.oracle_password.get_secret_value()

            # Validate required parameters
            if not actual_host:
                return FlextResult[FlextDbOracleApi].fail("Oracle host is required")
            if not actual_username:
                return FlextResult[FlextDbOracleApi].fail("Oracle username is required")
            if not actual_password:
                return FlextResult[FlextDbOracleApi].fail("Oracle password is required")

            self.logger.info(
                f"Connecting to Oracle at {actual_host}:{actual_port}/{actual_service_name}"
            )

            # Create Oracle configuration
            config: FlextDbOracleModels.OracleConfig = FlextDbOracleModels.OracleConfig(
                host=actual_host,
                port=actual_port,
                service_name=actual_service_name,
                username=actual_username,
                password=actual_password,
            )

            # Create and configure Oracle API
            api = FlextDbOracleApi(config=config)
            connect_result: FlextResult[FlextDbOracleApi] = api.connect()

            if connect_result.is_success:
                self.current_connection = api
                self.logger.info("Oracle connection established successfully")
                return FlextResult[FlextDbOracleApi].ok(api)
            return FlextResult[FlextDbOracleApi].fail(
                f"Oracle connection failed: {connect_result.error}",
            )

        except Exception as e:
            return FlextResult[FlextDbOracleApi].fail(f"Connection error: {e}")

    def _execute_with_chain(
        self,
        operation: str,
        **params: object,
    ) -> FlextResult[dict[str, object]]:
        """Execute operation with validation chain.

        Returns:
            FlextResult[dict[str, object]]: Operation result or error.

        """
        validation_result: FlextResult[None] = self._validate_connection()
        if validation_result.is_failure:
            return FlextResult[dict[str, object]].fail(
                validation_result.error or "Validation failed",
            )

        return self._execute_operation(operation, **params)

    def _validate_connection(self) -> FlextResult[None]:
        """Validate current Oracle connection.

        Returns:
            FlextResult[None]: Success or error.

        """
        if not self.current_connection:
            return FlextResult[None].fail("No active Oracle connection")

        if not self.current_connection.is_connected:
            return FlextResult[None].fail("Oracle connection not active")

        return FlextResult[None].ok(None)

    def _execute_operation(
        self,
        operation: str,
        **params: object,
    ) -> FlextResult[dict[str, object]]:
        """Execute Oracle operation with error handling.

        Returns:
            FlextResult[dict[str, object]]: Operation result or error.

        """
        if not self.current_connection:
            return FlextResult[dict[str, object]].fail("No active connection")

        try:
            if operation == "list_schemas":
                schemas_result: FlextResult[list[str]] = (
                    self.current_connection.get_schemas()
                )
                if schemas_result.is_success:
                    return FlextResult[dict[str, object]].ok(
                        {"schemas": list(schemas_result.value)},
                    )
                return FlextResult[dict[str, object]].fail(
                    schemas_result.error or "Schema listing failed",
                )

            if operation == "list_tables":
                schema = str(params.get("schema", ""))
                tables_result: FlextResult[list[str]] = (
                    self.current_connection.get_tables(schema or None)
                )
                if tables_result.is_success:
                    return FlextResult[dict[str, object]].ok(
                        {"tables": list(tables_result.value)},
                    )
                return FlextResult[dict[str, object]].fail(
                    tables_result.error or "Table listing failed",
                )

            if operation == "query":
                sql = str(params.get("sql", ""))
                if not sql:
                    return FlextResult[dict[str, object]].fail("SQL query required")

                params_dict_raw = params.get("params", {})
                params_dict: dict[str, object] = (
                    params_dict_raw if isinstance(params_dict_raw, dict) else {}
                )
                query_result: FlextResult[list[dict[str, object]]] = (
                    self.current_connection.query(sql, params_dict)
                )
                if query_result.is_success:
                    return FlextResult[dict[str, object]].ok({
                        "rows": list(query_result.value),
                        "row_count": len(query_result.value)
                        if query_result.value
                        else 0,
                    })
                return FlextResult[dict[str, object]].fail(
                    query_result.error or "Query execution failed",
                )

            if operation == "health_check":
                health_result: FlextResult[dict[str, object]] = (
                    self.current_connection.get_health_status()
                )
                if health_result.is_success:
                    return FlextResult[dict[str, object]].ok(health_result.value)
                return FlextResult[dict[str, object]].fail(
                    health_result.error or "Health check failed",
                )

            return FlextResult[dict[str, object]].fail(
                f"Unknown operation: {operation}",
            )

        except Exception as e:
            return FlextResult[dict[str, object]].fail(f"Operation failed: {e}")

    def _format_and_display_result(
        self,
        operation_result: FlextResult[dict[str, object]],
        format_type: str = "table",
    ) -> FlextResult[str]:
        """Format and display operation result.

        Returns:
            FlextResult[str]: Formatted result or error.

        """
        if operation_result.is_failure:
            return FlextResult[str].fail(operation_result.error or "Operation failed")

        data = operation_result.value
        formatter_result: FlextResult[
            Callable[[FlextDbOracleTypes.Query.QueryResult], FlextResult[str]]
        ] = self._get_formatter_strategy(format_type)
        if formatter_result.is_failure:
            return FlextResult[str].fail(
                formatter_result.error or "Formatter strategy failed",
            )

        formatter = formatter_result.value
        if callable(formatter):
            format_result: FlextResult[str] = formatter(
                cast("FlextDbOracleTypes.Query.QueryResult", data)
            )
            return format_result
        return FlextResult[str].fail("Invalid formatter strategy")

    def _get_formatter_strategy(
        self, format_type: str
    ) -> FlextResult[
        Callable[[FlextDbOracleTypes.Query.QueryResult], FlextResult[str]]
    ]:
        """Get formatter strategy for output format.

        Returns:
            FlextResult[object]: Formatter strategy or error.

        """
        try:
            formatter_strategies: dict[
                str, Callable[[FlextDbOracleTypes.Query.QueryResult], FlextResult[str]]
            ] = {
                "table": self._format_as_table,
                "json": self._format_as_json,
                "plain": lambda data: FlextResult[str].ok(str(data)),
            }

            if format_type in formatter_strategies:
                return FlextResult[
                    Callable[[FlextDbOracleTypes.Query.QueryResult], FlextResult[str]]
                ].ok(formatter_strategies[format_type])
            return FlextResult[
                Callable[[FlextDbOracleTypes.Query.QueryResult], FlextResult[str]]
            ].fail(f"Unsupported format: {format_type}")
        except Exception as e:
            return FlextResult[
                Callable[[FlextDbOracleTypes.Query.QueryResult], FlextResult[str]]
            ].fail(f"Formatter strategy error: {e}")

    def _format_as_table(
        self, data: FlextDbOracleTypes.Query.QueryResult
    ) -> FlextResult[str]:
        """Format data as table output.

        Returns:
            FlextResult[str]: Table formatted data or error.

        """
        try:
            # Adapt data for table display
            adapted_result: FlextResult[list[dict[str, str]]] = (
                self._adapt_data_for_table(data)
            )
            if adapted_result.is_failure:
                return FlextResult[str].fail(
                    adapted_result.error or "Data adaptation failed",
                )

            adapted_data = adapted_result.value

            # Simple table formatting
            if adapted_data:
                headers: list[str] = list(adapted_data[0].keys())
                rows: list[list[str]] = [
                    [str(row[h]) for h in headers] for row in adapted_data
                ]
                result_str = (
                    f"{'|'.join(headers)}\n{'|'.join(['---'] * len(headers))}\n"
                )
                result_str += "\n".join(["|".join(row) for row in rows])
                return FlextResult[str].ok(result_str)

            return FlextResult[str].ok(str(adapted_data))
        except Exception as e:
            return FlextResult[str].fail(f"Table formatting failed: {e}")

    def _format_as_json(
        self, data: FlextDbOracleTypes.Query.QueryResult
    ) -> FlextResult[str]:
        """Format data as JSON output.

        Returns:
            FlextResult[str]: JSON formatted data or error.

        """
        try:
            return FlextResult[str].ok(json.dumps(data, indent=2, default=str))
        except Exception as e:
            return FlextResult[str].fail(f"JSON formatting failed: {e}")

    def _adapt_data_for_table(
        self,
        data: FlextDbOracleTypes.Query.QueryResult,
    ) -> FlextResult[list[dict[str, str]]]:
        """Adapt data for table display.

        Returns:
            FlextResult[list[dict[str, str]]]: Adapted data or error.

        """
        try:

            def adapt_schemas(r: object) -> list[dict[str, str]]:
                return [{"schema": str(s)} for s in r if isinstance(r, list)] if isinstance(r, list) else []

            def adapt_tables(r: object) -> list[dict[str, str]]:
                return [{"table": str(t)} for t in r if isinstance(r, list)] if isinstance(r, list) else []

            def adapt_health(r: object) -> list[dict[str, str]]:
                return (
                    [{"key": str(k), "value": str(v)} for k, v in r.items()]
                    if isinstance(r, dict)
                    else []
                )

            adaptation_strategies: dict[
                str,
                Callable[[object], list[dict[str, str]]],
            ] = {
                "schemas": adapt_schemas,
                "tables": adapt_tables,
                "health": adapt_health,
            }

            for key, strategy in adaptation_strategies.items():
                if key in data:
                    adapted_data: list[dict[str, str]] = strategy(data[key])
                    return FlextResult[list[dict[str, str]]].ok(adapted_data)

            # Default: convert to list of key-value pairs
            result: list[dict[str, str]] = [
                {"key": str(k), "value": str(v)} for k, v in data.items()
            ]
            return FlextResult[list[dict[str, str]]].ok(result)
        except Exception as e:
            return FlextResult[list[dict[str, str]]].fail(
                f"Data adaptation failed: {e}",
            )

    def _execute_health_check(
        self,
    ) -> FlextResult[dict[str, object]]:
        """Execute Oracle health check.

        Returns:
            FlextResult[dict[str, object]]: Health check result or error.

        """
        try:
            validation_result: FlextResult[None] = self._validate_connection()
            if validation_result.is_failure:
                return FlextResult[dict[str, object]].fail(
                    validation_result.error or "Connection validation failed",
                )

            if not self.current_connection:
                return FlextResult[dict[str, object]].fail("No connection available")

            health_data: dict[str, object] = {
                "connection_status": "active"
                if self.current_connection.is_connected
                else "inactive",
                "host": self.current_connection.config.host,
                "port": self.current_connection.config.port,
                "service_name": self.current_connection.config.service_name,
                "timestamp": "now",  # Could use actual timestamp
            }

            return FlextResult[dict[str, object]].ok(health_data)
        except Exception as e:
            return FlextResult[dict[str, object]].fail(f"Health check failed: {e}")

    def list_schemas(self) -> FlextResult[str]:
        """List Oracle schemas with formatted output.

        Returns:
            FlextResult[str]: Formatted schemas list or error.

        """
        operation_result: FlextResult[dict[str, object]] = self._execute_with_chain(
            "list_schemas"
        )
        format_type = str(self.user_preferences.get("default_output_format", "table"))
        return self._format_and_display_result(operation_result, format_type)

    def list_tables(self, schema: str | None = None) -> FlextResult[str]:
        """List Oracle tables with formatted output.

        Returns:
            FlextResult[str]: Formatted tables list or error.

        """
        operation_result: FlextResult[dict[str, object]] = self._execute_with_chain(
            "list_tables", schema=schema or ""
        )
        format_type = str(self.user_preferences.get("default_output_format", "table"))
        return self._format_and_display_result(operation_result, format_type)

    def execute_query(
        self,
        sql: str,
        params: FlextDbOracleTypes.Query.QueryParameters | None = None,
    ) -> FlextResult[str]:
        """Execute SQL query with formatted output.

        Returns:
            FlextResult[str]: Formatted query results or error.

        """
        operation_result = self._execute_with_chain(
            "query",
            sql=sql,
            params=params or {},
        )
        format_type = str(self.user_preferences.get("default_output_format", "table"))
        return self._format_and_display_result(operation_result, format_type)

    def health_check(self) -> FlextResult[dict[str, object]]:
        """Perform Oracle health check.

        Returns:
            FlextResult[dict[str, object]]: Health check result or error.

        """
        return self._execute_health_check()

    def disconnect(self) -> FlextResult[None]:
        """Disconnect from Oracle database.

        Returns:
            FlextResult[None]: Success or error.

        """
        if self.current_connection:
            result: FlextResult[None] = self.current_connection.disconnect()
            self.current_connection = None
            return result
        return FlextResult[None].ok(None)

    def configure_preferences(
        self, **preferences: str | int | bool
    ) -> FlextResult[None]:
        """Configure client preferences.

        Returns:
            FlextResult[None]: Success or error.

        """
        try:
            self.user_preferences.update(preferences)
            self.logger.info(
                "Client preferences updated",
                extra={"preferences": "preferences"},
            )
            return FlextResult[None].ok(None)
        except Exception as e:
            return FlextResult[None].fail(f"Preference configuration failed: {e}")

    @classmethod
    def run_cli_command(
        cls, operation: str, **params: str | int | bool
    ) -> FlextResult[str]:
        """Run Oracle CLI command with proper error handling.

        Returns:
            FlextResult[str]: Command result or error.

        """
        try:
            client = cls()

            if operation == "health":

                def health_cmd() -> FlextResult[dict[str, object]]:
                    return client.health_check()

                health_result: FlextResult[dict[str, object]] = health_cmd()
                if health_result.is_success:
                    return FlextResult[str].ok(f"Health check: {health_result.value}")
                return FlextResult[str].fail(
                    health_result.error or "Health check failed",
                )

            # Log unused params for debugging but don't remove them as they may be used for future operations
            if params:
                FlextLogger(__name__).debug(
                    f"Unused CLI parameters for operation '{operation}': {params}",
                )

            return FlextResult[str].fail(f"Unknown CLI operation: {operation}")
        except Exception as e:
            return FlextResult[str].fail(f"CLI command failed: {e}")


# ZERO TOLERANCE: No wrapper functions or global instances - use FlextDbOracleClient.get_client() directly

__all__: list[str] = [
    "FlextDbOracleClient",
]
