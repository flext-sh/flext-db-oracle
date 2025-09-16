"""Oracle Database client providing CLI and programmatic access.

This module provides the Oracle database client with CLI functionality
using FLEXT ecosystem patterns for database operations.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import sys
from collections.abc import Callable

from flext_cli import (
    FlextCliApi,
    FlextCliFormatters,
    FlextCliInteractions,
    FlextCliServices,
)
from flext_core import (
    FlextContainer,
    FlextLogger,
    FlextResult,
    FlextTypes,
    FlextUtilities,
)

from flext_db_oracle.api import FlextDbOracleApi
from flext_db_oracle.constants import FlextDbOracleConstants
from flext_db_oracle.models import FlextDbOracleModels


class FlextDbOracleClient:
    """Unified Oracle database CLI client using composition and SOLID principles.

    REFACTORED: No longer inherits from FlextDomainService (wrong abstraction).
    Uses composition with proper single responsibility.
    """

    def __init__(self, *, debug: bool = False) -> None:
        """Initialize Oracle CLI client with proper composition."""
        # Core dependencies injected via composition
        self.logger = FlextLogger(__name__)
        self.container = FlextContainer.get_global()

        # CLI components using flext-cli
        self.formatter = FlextCliFormatters()
        self.interactions = FlextCliInteractions()
        self.cli_api = FlextCliApi()
        self.cli_services = FlextCliServices()

        # Application state
        self.debug = debug
        self.current_connection: FlextDbOracleApi | None = None
        self.user_preferences: FlextTypes.Core.Dict = {
            "default_output_format": "table",
            "auto_confirm_operations": False,
            "show_execution_time": True,
            "connection_timeout": 30,
            "query_limit": 1000,
        }

        self.logger.info("Oracle CLI client initialized")

    def initialize(self) -> FlextResult[None]:
        """Initialize CLI client with proper flext-cli setup."""
        try:
            self.logger.info("FLEXT Oracle Database CLI")
            self.logger.info(
                "Enterprise Oracle operations with professional CLI experience..."
            )
            self.logger.info("Oracle CLI initialized successfully")
            return FlextResult[None].ok(None)

        except Exception as e:
            self.logger.exception("Oracle CLI initialization failed")
            return FlextResult[None].fail(f"Oracle CLI initialization failed: {e}")

    def connect_to_oracle(
        self,
        host: str,
        port: int,
        service_name: str,
        user: str,
        password: str,
    ) -> FlextResult[FlextDbOracleApi]:
        """Connect to Oracle database using provided credentials."""
        try:
            config = FlextDbOracleModels.OracleConfig(
                host=host,
                port=port,
                name=service_name,  # Required field - use service_name as database
                user=user,
                password=password,
                service_name=service_name,
                ssl_server_cert_dn=None,
            )

            api = FlextDbOracleApi(config)
            connect_result = api.connect()

            if not connect_result.success:
                return FlextResult[FlextDbOracleApi].fail(
                    f"Connection failed: {connect_result.error}",
                )

            self.current_connection = api
            self.logger.info("Connected to Oracle database successfully")
            return FlextResult[FlextDbOracleApi].ok(api)

        except Exception as e:
            self.logger.exception("Oracle connection failed")
            return FlextResult[FlextDbOracleApi].fail(f"Oracle connection failed: {e}")

    def execute_query(self, query: str) -> FlextResult[object]:
        """Execute SQL query using Chain of Responsibility."""
        return self._execute_with_chain(
            "query",
            {"sql": query, "title": "Query Results"},
        )

    def _execute_with_chain(
        self,
        operation: str,
        params: FlextTypes.Core.Dict,
    ) -> FlextResult[object]:
        """Execute operation using Railway-Oriented Programming."""
        return (
            FlextResult[FlextTypes.Core.Dict]
            .ok({"operation": operation, "params": params})
            .bind(self._validate_connection)
            .bind(self._execute_operation)
            .bind(self._format_and_display_result)
            .map(lambda data: data.get("result"))
            .tap_error(
                lambda error: self.logger.error(f"Chain execution failed: {error}")
            )
        )

    def _validate_connection(
        self,
        data: FlextTypes.Core.Dict,
    ) -> FlextResult[FlextTypes.Core.Dict]:
        """Validate connection."""
        return (
            FlextResult[FlextTypes.Core.Dict].ok(data)
            if self.current_connection
            else FlextResult[FlextTypes.Core.Dict].fail("No active Oracle connection")
        )

    def _execute_operation(
        self,
        data: FlextTypes.Core.Dict,
    ) -> FlextResult[FlextTypes.Core.Dict]:
        """Execute operation using Strategy Pattern."""
        operation = str(data.get("operation", ""))
        params = data.get("params", {})

        if self.current_connection is None:
            return FlextResult[FlextTypes.Core.Dict].fail("No active connection")

        connection = self.current_connection

        # Type-safe parameter handling without cast
        if not isinstance(params, dict):
            return FlextResult[FlextTypes.Core.Dict].fail("Invalid parameters format")

        params_dict: FlextTypes.Core.Dict = params

        # Type-safe schema parameter extraction
        schema_param = params_dict.get("schema")
        schema_str: str | None = str(schema_param) if schema_param else None

        operation_strategies = {
            "query": lambda: connection.query(str(params_dict.get("sql", ""))),
            "schemas": connection.get_schemas,
            "tables": lambda: connection.get_tables(schema_str),
            "health": self._execute_health_check,
        }

        strategy = operation_strategies.get(operation)
        if not strategy:
            return FlextResult[FlextTypes.Core.Dict].fail(
                f"Unknown operation: {operation}",
            )

        try:
            execution_result = strategy()

            # Validate that we got a FlextResult-like object
            if not hasattr(execution_result, "success"):
                return FlextResult[FlextTypes.Core.Dict].fail(
                    f"Invalid result from {operation}"
                )

            # Type-safe access to result attributes using getattr with defaults
            is_success = getattr(execution_result, "success", False)
            if not is_success:
                error_msg = getattr(execution_result, "error", "Unknown error")
                return FlextResult[FlextTypes.Core.Dict].fail(
                    f"{operation.title()} failed: {error_msg}",
                )

            # Get the value safely
            result_value = getattr(execution_result, "value", None)
            return FlextResult[FlextTypes.Core.Dict].ok(
                dict(data) | {"result": result_value},
            )

        except Exception as e:
            self.logger.exception(f"{operation.title()} execution error")
            return FlextResult[FlextTypes.Core.Dict].fail(
                f"{operation.title()} execution error: {e}",
            )

    def _format_and_display_result(
        self,
        data: FlextTypes.Core.Dict,
    ) -> FlextResult[FlextTypes.Core.Dict]:
        """Format and display using Strategy Pattern."""
        try:
            formatter_strategy = self._get_formatter_strategy()
            format_result = formatter_strategy(data)

            if format_result.success:
                self.logger.info(format_result.value)

            return FlextResult[FlextTypes.Core.Dict].ok(data)

        except Exception as e:
            self.logger.warning(f"Format/display warning: {e}")
            return FlextResult[FlextTypes.Core.Dict].ok(data)

    def _get_formatter_strategy(
        self,
    ) -> Callable[[FlextTypes.Core.Dict], FlextResult[str]]:
        """Get formatter strategy using lookup table."""
        # Type-safe preference access without cast
        format_preference = self.user_preferences["default_output_format"]
        format_type = str(format_preference) if format_preference else "json"

        formatter_strategies: dict[
            str, Callable[[FlextTypes.Core.Dict], FlextResult[str]]
        ] = {
            "table": self._format_as_table,
            "json": self._format_as_json,
        }

        return formatter_strategies.get(format_type, self._format_as_json)

    def _format_as_table(self, data: FlextTypes.Core.Dict) -> FlextResult[str]:
        """Format as table using data adapter."""
        operation = str(data.get("operation", ""))
        params = data.get("params", {})
        result = data.get("result")

        # Type-safe parameter handling without cast
        if not isinstance(params, dict):
            params_dict: FlextTypes.Core.Dict = {}
        else:
            params_dict = params

        title_param = params_dict.get("title", f"{operation.title()} Results")
        title = str(title_param)

        table_data = self._adapt_data_for_table(operation, result)
        table_result = self.formatter.format_table(data=table_data, title=title)
        if table_result.success:
            return FlextResult[str].ok(str(table_result.value))
        return FlextResult[str].fail(f"Table formatting failed: {table_result.error}")

    def _format_as_json(self, data: FlextTypes.Core.Dict) -> FlextResult[str]:
        """Format as JSON."""
        result = data.get("result")
        formatted = self.formatter.format_json(result)
        return FlextResult[str].ok(formatted.unwrap())

    def _adapt_data_for_table(
        self,
        operation: str,
        result: object,
    ) -> list[FlextTypes.Core.Dict]:
        """Adapt data for table using Strategy Pattern."""

        def adapt_schemas(r: object) -> list[FlextTypes.Core.Dict]:
            return [{"schema": schema} for schema in r] if isinstance(r, list) else []

        def adapt_tables(r: object) -> list[FlextTypes.Core.Dict]:
            return [{"table": table} for table in r] if isinstance(r, list) else []

        def adapt_health(r: object) -> list[FlextTypes.Core.Dict]:
            return (
                [{"key": k, "value": str(v)} for k, v in r.items()]
                if isinstance(r, dict)
                else []
            )

        adaptation_strategies: dict[
            str, Callable[[object], list[FlextTypes.Core.Dict]]
        ] = {
            "schemas": adapt_schemas,
            "tables": adapt_tables,
            "health": adapt_health,
        }

        strategy = adaptation_strategies.get(operation)
        if strategy:
            return strategy(result)

        # Default strategy
        if isinstance(result, list):
            return result
        return [{"result": str(result)}]

    def _execute_health_check(self) -> FlextResult[FlextTypes.Core.Dict]:
        """Execute health check."""
        if self.current_connection is None:
            return FlextResult[FlextTypes.Core.Dict].fail(
                "No active connection for health check"
            )

        test_result = self.current_connection.query(
            FlextDbOracleConstants.Query.TEST_QUERY,
        )

        health_data: FlextTypes.Core.Dict = {
            "status": "healthy" if test_result.success else "unhealthy",
            "test_query_result": test_result.success,
            "timestamp": FlextUtilities.generate_iso_timestamp(),
            "connection_active": self.current_connection.is_connected,
        }

        return FlextResult[FlextTypes.Core.Dict].ok(health_data)

    def list_schemas(self) -> FlextResult[FlextTypes.Core.StringList]:
        """List schemas using Chain of Responsibility."""
        result = self._execute_with_chain("schemas", {"title": "Database Schemas"})
        if result.success:
            # Type-safe value extraction without cast
            value = result.value
            if isinstance(value, list):
                string_list: FlextTypes.Core.StringList = [str(item) for item in value]
                return FlextResult[FlextTypes.Core.StringList].ok(string_list)
            return FlextResult[FlextTypes.Core.StringList].fail(
                "Invalid schema list format"
            )
        return FlextResult[FlextTypes.Core.StringList].fail(
            result.error or "Schema listing failed"
        )

    def list_tables(
        self, schema: str | None = None
    ) -> FlextResult[FlextTypes.Core.StringList]:
        """List tables using Chain of Responsibility."""
        title = f"Tables in {schema}" if schema else "Tables"
        result = self._execute_with_chain("tables", {"schema": schema, "title": title})
        if result.success:
            # Type-safe value extraction without cast
            value = result.value
            if isinstance(value, list):
                string_list: FlextTypes.Core.StringList = [str(item) for item in value]
                return FlextResult[FlextTypes.Core.StringList].ok(string_list)
            return FlextResult[FlextTypes.Core.StringList].fail(
                "Invalid table list format"
            )
        return FlextResult[FlextTypes.Core.StringList].fail(
            result.error or "Table listing failed"
        )

    def health_check(self) -> FlextResult[FlextTypes.Core.Dict]:
        """Health check using Chain of Responsibility."""
        self.logger.info("Performing health check...")
        result = self._execute_with_chain("health", {"title": "Health Check"})
        if result.success:
            # Type-safe value extraction without cast
            value = result.value
            if isinstance(value, dict):
                return FlextResult[FlextTypes.Core.Dict].ok(value)
            return FlextResult[FlextTypes.Core.Dict].fail(
                "Invalid health check result format"
            )
        return FlextResult[FlextTypes.Core.Dict].fail(
            result.error or "Health check failed"
        )

    # Class-level singleton management
    def configure_preferences(
        self, **preferences: object
    ) -> FlextResult[FlextTypes.Core.Dict]:
        """Configure user preferences for the Oracle CLI client."""
        try:
            for key, value in preferences.items():
                if key in self.user_preferences:
                    self.user_preferences[key] = value
                else:
                    return FlextResult[FlextTypes.Core.Dict].fail(
                        f"Invalid preference key: {key}"
                    )

            return FlextResult[FlextTypes.Core.Dict].ok(self.user_preferences.copy())
        except Exception as e:
            return FlextResult[FlextTypes.Core.Dict].fail(
                f"Failed to configure preferences: {e}"
            )

    def run_cli_command(self, command: str, **kwargs: object) -> FlextResult[object]:
        """Execute CLI command with parameters."""
        try:
            # Type-safe parameter extraction
            schema_param = kwargs.get("schema")
            schema_str: str | None = (
                str(schema_param) if schema_param is not None else None
            )

            sql_param = kwargs.get("sql")
            sql_str: str = str(sql_param) if sql_param is not None else ""

            def health_cmd() -> FlextResult[FlextTypes.Core.Dict]:
                return self.health_check()

            def schemas_cmd() -> FlextResult[FlextTypes.Core.StringList]:
                return self.list_schemas()

            def tables_cmd() -> FlextResult[FlextTypes.Core.StringList]:
                return self.list_tables(schema_str)

            def query_cmd() -> FlextResult[object]:
                return self.execute_query(sql_str)

            # Define command result type union to avoid explicit Any
            command_result = (
                FlextResult[FlextTypes.Core.Dict] |
                FlextResult[FlextTypes.Core.StringList] |
                FlextResult[object]
            )
            command_strategies: dict[str, Callable[[], command_result]] = {
                "health": health_cmd,
                "schemas": schemas_cmd,
                "tables": tables_cmd,
                "query": query_cmd,
            }

            strategy = command_strategies.get(command)
            if not strategy:
                return FlextResult[object].fail(f"Unknown command: {command}")

            # Cast to object to match return type
            result = strategy()
            return FlextResult[object].ok(result.unwrap()) if result.success else FlextResult[object].fail(result.error or "Command failed")
        except Exception as e:
            return FlextResult[object].fail(f"Command execution failed: {e}")

    _client_instance: FlextDbOracleClient | None = None

    @classmethod
    def get_client(cls) -> FlextDbOracleClient:
        """Get or create global Oracle CLI client instance."""
        if cls._client_instance is None:
            client = cls()
            init_result = client.initialize()
            if not init_result.success:
                sys.stderr.write(
                    f"Failed to initialize Oracle CLI: {init_result.error}\n"
                )
                sys.exit(1)
            cls._client_instance = client
        return cls._client_instance


# ZERO TOLERANCE: No wrapper functions or global instances - use FlextDbOracleClient.get_client() directly

__all__: FlextTypes.Core.StringList = [
    "FlextDbOracleClient",
]
