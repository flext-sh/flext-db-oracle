"""Oracle Database client providing CLI and programmatic access.

This module provides the Oracle database client with CLI functionality
using FLEXT ecosystem patterns for database operations.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import json
from collections.abc import Callable
from typing import ClassVar, TypeGuard

from flext_core import r
from flext_core.service import FlextService

from flext_db_oracle.api import FlextDbOracleApi
from flext_db_oracle.settings import FlextDbOracleSettings
from flext_db_oracle.typings import t


def _is_json_value(value: object) -> TypeGuard[t.JsonValue]:
    """Check whether value matches JSON-compatible typing contract."""
    if value is None or isinstance(value, (bool, int, float, str)):
        return True
    if isinstance(value, list):
        return all(_is_json_value(item) for item in value)
    if isinstance(value, dict):
        return all(isinstance(k, str) and _is_json_value(v) for k, v in value.items())
    return False


class FlextDbOracleClient(FlextService[FlextDbOracleSettings]):
    """Oracle Database CLI client with complete FLEXT ecosystem integration.

    This client provides command-line interface operations for Oracle Database
    management using the flext-db-oracle foundation API with full flext-core integration.
    """

    debug: bool = False
    current_connection: FlextDbOracleApi | None = None
    user_preferences: ClassVar[t.DbOracle.ConnectionPool] = t.ConfigMap(root={})

    def __init__(self, *, debug: bool = False, **kwargs: t.GeneralValueType) -> None:
        """Initialize Oracle CLI client with proper composition."""
        # Configuration - create locally (don't pass to parent to avoid extra_forbidden error)
        self._oracle_config = FlextDbOracleSettings()

        # Initialize FlextService with remaining kwargs
        super().__init__(**kwargs)
        # Logger will be initialized lazily via the parent class property

        # Application state - set debug value
        self.debug = debug

    @property
    def oracle_config(self) -> FlextDbOracleSettings:
        """Get the Oracle configuration."""
        return self._oracle_config

    def connect_to_oracle(
        self,
        host: str | None = None,
        port: int | None = None,
        service_name: str | None = None,
        username: str | None = None,
        password: str | None = None,
    ) -> r[FlextDbOracleApi]:
        """Connect to Oracle database with provided parameters or config defaults.

        Returns:
        r[FlextDbOracleApi]: API instance or error.

        """
        try:
            # Use provided parameters or fall back to config defaults
            actual_host = host or self.oracle_config.host
            actual_port = port or self.oracle_config.port
            actual_service_name = service_name or self.oracle_config.service_name
            actual_username = username or self.oracle_config.username
            actual_password = password or self.oracle_config.password.get_secret_value()

            # Validate required parameters
            if not actual_host:
                return r[FlextDbOracleApi].fail("Oracle host is required")
            if not actual_username:
                return r[FlextDbOracleApi].fail("Oracle username is required")
            if not actual_password:
                return r[FlextDbOracleApi].fail("Oracle password is required")

            self.logger.info(
                "Connecting to Oracle at %s:%s/%s",
                actual_host,
                actual_port,
                actual_service_name,
            )

            # Create Oracle configuration
            config: FlextDbOracleSettings = FlextDbOracleSettings(
                host=actual_host,
                port=actual_port,
                service_name=actual_service_name,
                username=actual_username,
                password=actual_password,
            )

            # Create and configure Oracle API
            api = FlextDbOracleApi(config=config)
            connect_result: r[FlextDbOracleApi] = api.connect()

            if connect_result.is_success:
                self.current_connection = api
                self.logger.info("Oracle connection established successfully")
                return r[FlextDbOracleApi].ok(api)
            return r[FlextDbOracleApi].fail(
                f"Oracle connection failed: {connect_result.error}",
            )

        except Exception as e:
            return r[FlextDbOracleApi].fail(f"Connection error: {e}")

    def _execute_with_chain(
        self,
        operation: str,
        **params: t.GeneralValueType,
    ) -> r[t.ConfigMap]:
        """Execute operation with validation chain.

        Returns:
        r[t.ConfigMap]: Operation result or error.

        """
        validation_result: r[None] = self._validate_connection()
        if validation_result.is_failure:
            return r[t.ConfigMap].fail(
                validation_result.error or "Validation failed",
            )

        return self._execute_operation(operation, **params)

    def _validate_connection(self) -> r[None]:
        """Validate current Oracle connection.

        Returns:
        r[None]: Success or error.

        """
        if not self.current_connection:
            return r[None].fail("No active Oracle connection")

        if not self.current_connection.is_connected:
            return r[None].fail("Oracle connection not active")

        return r[None].ok(None)

    def _execute_operation(
        self,
        operation: str,
        **params: t.GeneralValueType,
    ) -> r[t.ConfigMap]:
        """Execute Oracle operation with error handling.

        Returns:
        r[t.ConfigMap]: Operation result or error.

        """
        if not self.current_connection:
            return r[t.ConfigMap].fail("No active connection")

        try:
            if operation == "list_schemas":
                return self._handle_list_schemas_operation()
            if operation == "list_tables":
                return self._handle_list_tables_operation(**params)
            if operation == "query":
                return self._handle_query_operation(**params)
            if operation == "health_check":
                return self._handle_health_check_operation()

            return r[t.ConfigMap].fail(
                f"Unknown operation: {operation}",
            )

        except Exception as e:
            return r[t.ConfigMap].fail(f"Operation failed: {e}")

    def _handle_list_schemas_operation(self) -> r[t.ConfigMap]:
        """Handle list schemas operation."""
        if self.current_connection is None:
            return r[t.ConfigMap].fail("No active database connection")
        return self.current_connection.get_schemas().map(
            lambda schemas: t.ConfigMap(root={"schemas": list(schemas)}),
        )

    def _handle_list_tables_operation(
        self,
        **params: t.GeneralValueType,
    ) -> r[t.ConfigMap]:
        """Handle list tables operation."""
        if self.current_connection is None:
            return r[t.ConfigMap].fail("No active database connection")
        schema = str(params.get("schema", ""))
        return self.current_connection.get_tables(schema or None).map(
            lambda tables: t.ConfigMap(root={"tables": list(tables)}),
        )

    def _handle_query_operation(
        self,
        **params: t.GeneralValueType,
    ) -> r[t.ConfigMap]:
        """Handle query operation."""
        if self.current_connection is None:
            return r[t.ConfigMap].fail("No active database connection")
        sql = str(params.get("sql", ""))
        if not sql:
            return r[t.ConfigMap].fail("SQL query required")

        params_dict_raw = params.get("params", {})
        params_dict: dict[str, t.JsonValue] = {}
        if isinstance(params_dict_raw, dict):
            params_dict = {
                str(k): v
                for k, v in params_dict_raw.items()
                if isinstance(k, str) and _is_json_value(v)
            }
        return self.current_connection.query(sql, params_dict).map(
            lambda rows: t.ConfigMap(
                root={
                    "rows": [row.root for row in rows],
                    "row_count": len(rows),
                }
            ),
        )

    def _handle_health_check_operation(self) -> r[t.ConfigMap]:
        """Handle health check operation."""
        if self.current_connection is None:
            return r[t.ConfigMap].fail("No active database connection")
        return self.current_connection.get_health_status().map(
            lambda status: t.ConfigMap(root=status.model_dump()),
        )

    def _format_and_display_result(
        self,
        operation_result: r[t.ConfigMap],
        format_type: str = "table",
    ) -> r[str]:
        """Format and display operation result.

        Returns:
        r[str]: Formatted result or error.

        """
        return self._get_formatter_strategy(format_type).flat_map(
            lambda formatter: operation_result.flat_map(
                lambda data: (
                    formatter(data)
                    if callable(formatter)
                    else r[str].fail("Invalid formatter strategy")
                ),
            ),
        )

    def _get_formatter_strategy(
        self,
        format_type: str,
    ) -> r[Callable[[t.ConfigMap], r[str]]]:
        """Get formatter strategy for output format.

        Returns:
        r[t.JsonValue]: Formatter strategy or error.

        """
        try:
            formatter_strategies: dict[
                str,
                Callable[[t.ConfigMap], r[str]],
            ] = {
                "table": self._format_as_table,
                "json": self._format_as_json,
                "plain": lambda data: r[str].ok(str(data)),
            }

            if format_type in formatter_strategies:
                return r[Callable[[t.ConfigMap], r[str]]].ok(
                    formatter_strategies[format_type],
                )
            return r[Callable[[t.ConfigMap], r[str]]].fail(
                f"Unsupported format: {format_type}",
            )
        except Exception as e:
            return r[Callable[[t.ConfigMap], r[str]]].fail(
                f"Formatter strategy error: {e}",
            )

    def _format_as_table(
        self,
        data: t.ConfigMap,
    ) -> r[str]:
        """Format data as table output.

        Returns:
        r[str]: Table formatted data or error.

        """
        try:
            return self._adapt_data_for_table(data).map(
                lambda adapted_data: (
                    self._build_table_string(adapted_data)
                    if adapted_data
                    else str(adapted_data)
                ),
            )
        except Exception as e:
            return r[str].fail(f"Table formatting failed: {e}")

    def _build_table_string(self, adapted_data: list[dict[str, str]]) -> str:
        """Build table string from adapted data."""
        headers: list[str] = list(adapted_data[0].keys())
        rows: list[list[str]] = [[str(row[h]) for h in headers] for row in adapted_data]
        result_str = f"{'|'.join(headers)}\n{'|'.join(['---'] * len(headers))}\n"
        result_str += "\n".join(["|".join(row) for row in rows])
        return result_str

    def _format_as_json(
        self,
        data: t.ConfigMap,
    ) -> r[str]:
        """Format data as JSON output.

        Returns:
        r[str]: JSON formatted data or error.

        """
        try:
            return r[str].ok(json.dumps(data.root, indent=2, default=str))
        except Exception as e:
            return r[str].fail(f"JSON formatting failed: {e}")

    def _adapt_data_for_table(
        self,
        data: t.ConfigMap,
    ) -> r[list[dict[str, str]]]:
        """Adapt data for table display.

        Returns:
        r[list[dict[str, str]]]: Adapted data or error.

        """
        try:

            def adapt_schemas(r: t.GeneralValueType) -> list[dict[str, str]]:
                return [{"schema": str(s)} for s in r] if isinstance(r, list) else []

            def adapt_tables(r: t.GeneralValueType) -> list[dict[str, str]]:
                return [{"table": str(t)} for t in r] if isinstance(r, list) else []

            def adapt_health(r: t.GeneralValueType) -> list[dict[str, str]]:
                return (
                    [{"key": str(k), "value": str(v)} for k, v in r.items()]
                    if isinstance(r, dict)
                    else []
                )

            adaptation_strategies: dict[
                str,
                Callable[[t.GeneralValueType], list[dict[str, str]]],
            ] = {
                "schemas": adapt_schemas,
                "tables": adapt_tables,
                "health": adapt_health,
            }

            data_root = data.root
            for key, strategy in adaptation_strategies.items():
                if key in data_root:
                    adapted_data: list[dict[str, str]] = strategy(data_root[key])
                    return r[list[dict[str, str]]].ok(adapted_data)

            # Default: convert to list of key-value pairs
            result: list[dict[str, str]] = [
                {"key": str(k), "value": str(v)} for k, v in data_root.items()
            ]
            return r[list[dict[str, str]]].ok(result)
        except Exception as e:
            return r[list[dict[str, str]]].fail(
                f"Data adaptation failed: {e}",
            )

    def _execute_health_check(
        self,
    ) -> r[t.ConfigMap]:
        """Execute Oracle health check.

        Returns:
        r[t.ConfigMap]: Health check result or error.

        """
        try:
            validation_result: r[None] = self._validate_connection()
            if validation_result.is_failure:
                return r[t.ConfigMap].fail(
                    validation_result.error or "Connection validation failed",
                )

            if not self.current_connection:
                return r[t.ConfigMap].fail("No connection available")

            health_data: dict[str, t.GeneralValueType] = {
                "connection_status": "active"
                if self.current_connection.is_connected
                else "inactive",
                "host": self.current_connection.oracle_config.host,
                "port": self.current_connection.oracle_config.port,
                "service_name": self.current_connection.oracle_config.service_name,
                "timestamp": "now",  # Could use actual timestamp
            }

            return r[t.ConfigMap].ok(t.ConfigMap(root=health_data))
        except Exception as e:
            return r[t.ConfigMap].fail(f"Health check failed: {e}")

    def list_schemas(self) -> r[str]:
        """List Oracle schemas with formatted output.

        Returns:
        r[str]: Formatted schemas list or error.

        """
        operation_result: r[t.ConfigMap] = self._execute_with_chain(
            "list_schemas",
        )
        format_type = str(
            self.user_preferences.root.get("default_output_format", "table")
        )
        return self._format_and_display_result(operation_result, format_type)

    def list_tables(self, schema: str | None = None) -> r[str]:
        """List Oracle tables with formatted output.

        Returns:
        r[str]: Formatted tables list or error.

        """
        operation_result: r[t.ConfigMap] = self._execute_with_chain(
            "list_tables",
            schema=schema or "",
        )
        format_type = str(
            self.user_preferences.root.get("default_output_format", "table")
        )
        return self._format_and_display_result(operation_result, format_type)

    def execute(self) -> r[FlextDbOracleSettings]:
        """Execute the main domain operation for Oracle client.

        Returns:
        r[FlextDbOracleSettings]: Success with settings or failure with error

        """
        # Default implementation returns current configuration
        return r[FlextDbOracleSettings].ok(self._oracle_config)

    def execute_query(
        self,
        sql: str,
        params: t.Query.QueryParameters | None = None,
    ) -> r[str]:
        """Execute SQL query with formatted output.

        Returns:
        r[str]: Formatted query results or error.

        """
        query_params: dict[str, t.JsonValue] = {}
        if params is not None:
            query_params = {
                k: v
                for k, v in params.root.items()
                if isinstance(k, str) and _is_json_value(v)
            }
        operation_result = self._execute_with_chain(
            "query",
            sql=sql,
            params=query_params,
        )
        format_type = str(
            self.user_preferences.root.get("default_output_format", "table")
        )
        return self._format_and_display_result(operation_result, format_type)

    def health_check(self) -> r[t.ConfigMap]:
        """Perform Oracle health check.

        Returns:
        r[t.ConfigMap]: Health check result or error.

        """
        return self._execute_health_check()

    def disconnect(self) -> r[None]:
        """Disconnect from Oracle database.

        Returns:
        r[None]: Success or error.

        """
        if self.current_connection:
            result: r[None] = self.current_connection.disconnect()
            self.current_connection = None
            return result
        return r[None].ok(None)

    def configure_preferences(
        self,
        **preferences: str | int | bool,
    ) -> r[None]:
        """Configure client preferences.

        Returns:
        r[None]: Success or error.

        """
        try:
            self.user_preferences.root.update(preferences)
            self.logger.info(
                "Client preferences updated",
                extra={"preferences": "preferences"},
            )
            return r[None].ok(None)
        except Exception as e:
            return r[None].fail(f"Preference configuration failed: {e}")

    @classmethod
    def run_cli_command(
        cls,
        operation: str,
        **params: str | int | bool,
    ) -> r[str]:
        """Run Oracle CLI command with proper error handling.

        Returns:
        r[str]: Command result or error.

        """
        try:
            client = cls()

            if operation == "health":

                def health_cmd() -> r[t.ConfigMap]:
                    return client.health_check()

                health_result: r[t.ConfigMap] = health_cmd()
                if health_result.is_success:
                    return r[str].ok(f"Health check: {health_result.value}")
                return r[str].fail(
                    health_result.error or "Health check failed",
                )

            # Log unused params for debugging but don't remove them as they may be used for future operations
            if params:
                client.logger.debug(
                    "Unused CLI parameters for operation '%s': %s",
                    operation,
                    params,
                )

            return r[str].fail(f"Unknown CLI operation: {operation}")
        except Exception as e:
            return r[str].fail(f"CLI command failed: {e}")


# Zero Tolerance: No wrapper functions or global instances - use FlextDbOracleClient.get_client() directly

__all__: list[str] = [
    "FlextDbOracleClient",
]
