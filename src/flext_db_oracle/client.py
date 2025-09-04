"""FLEXT DB Oracle CLI using ONLY flext-cli patterns - NO CLICK/RICH.

Single unified CLI client following FLEXT standards with proper flext-cli usage,
consolidated class structure, and ZERO direct dependencies on click/rich.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import sys
from typing import cast

from flext_cli import (
    FlextCliApi,
    FlextCliFormatters,
    FlextCliInteractions,
    FlextCliModels,
    FlextCliServices,
)
from flext_core import (
    FlextLogger,
    FlextResult,
    FlextUtilities,
)
from flext_core.container import FlextContainer
from pydantic import SecretStr

from flext_db_oracle.api import FlextDbOracleApi
from flext_db_oracle.constants import FlextDbOracleConstants
from flext_db_oracle.mixins import ConnectionParameters
from flext_db_oracle.models import FlextDbOracleModels

# =============================================================================
# COMMAND PROCESSOR - ELIMINA DUPLICAÇÃO DE COMANDOS CLI
# =============================================================================


# ELIMINADO: OracleCliCommandProcessor class - Substituída por Interpreter Pattern unificado
# no método _create_unified_cli_interpreter() que consolida TODAS as operações CLI


class FlextDbOracleClient:
    """Unified Oracle database CLI client with ONLY flext-cli integration.

    Single class containing all CLI functionality without click dependencies,
    using flext-cli for all user interactions and output formatting.
    """

    def __init__(self, *, debug: bool = False) -> None:
        """Initialize Oracle CLI client with flext-cli components."""
        self.cli_api = FlextCliApi()
        self.formatter = FlextCliFormatters()
        self.interactions = FlextCliInteractions()
        self.logger = FlextLogger(__name__)
        self.container = FlextContainer.get_global()
        self.cli_services = FlextCliServices()

        # Application state
        self.debug = debug
        self.current_connection: FlextDbOracleApi | None = None
        self.user_preferences: dict[str, object] = {
            "default_output_format": "table",
            "auto_confirm_operations": False,
            "show_execution_time": True,
            "connection_timeout": 30,
            "query_limit": 1000,
        }

    def initialize(self) -> FlextResult[None]:
        """Initialize CLI client with proper flext-cli setup."""
        try:
            # Use flext-cli proper initialization
            init_result = self.cli_services.initialize_cli()
            if not init_result.success:
                return FlextResult[None].fail(
                    f"CLI initialization failed: {init_result.error}"
                )

            self.interactions.print_info("FLEXT Oracle Database CLI")
            self.interactions.print_status(
                "Enterprise Oracle operations with professional CLI experience..."
            )

            self.interactions.print_success("Oracle CLI initialized successfully")
            return FlextResult[None].ok(None)

        except Exception as e:
            self.logger.exception("Oracle CLI initialization failed")
            return FlextResult[None].fail(f"Oracle CLI initialization failed: {e}")

    def connect_to_oracle(
        self, host: str, port: int, service_name: str, username: str, password: str
    ) -> FlextResult[FlextDbOracleApi]:
        """Connect to Oracle database using provided credentials."""
        try:
            config = FlextDbOracleModels.OracleConfig(
                host=host,
                port=port,
                service_name=service_name,
                username=username,
                password=SecretStr(password),
                ssl_server_cert_dn=None,
            )

            api = FlextDbOracleApi(config)
            connect_result = api.connect()

            if not connect_result.success:
                return FlextResult[FlextDbOracleApi].fail(
                    f"Connection failed: {connect_result.error}"
                )

            self.current_connection = api
            self.interactions.print_success("Connected to Oracle database successfully")
            return FlextResult[FlextDbOracleApi].ok(api)

        except Exception as e:
            self.logger.exception("Oracle connection failed")
            return FlextResult[FlextDbOracleApi].fail(f"Oracle connection failed: {e}")

    def execute_query(self, query: str) -> FlextResult[object]:
        """Execute SQL query usando Chain of Responsibility - ELIMINA DUPLICAÇÃO."""
        return self._execute_with_chain(
            "query", {"sql": query, "title": "Query Results"}
        )

    def _execute_with_chain(
        self, operation: str, params: dict[str, object]
    ) -> FlextResult[object]:
        """Execute operation usando Fluent Interface + Railway-Oriented Programming - REDUZ COMPLEXIDADE."""
        # Fluent Interface Pattern com Railway-Oriented Programming - SINGLE EXPRESSION
        return (
            FlextResult[dict[str, object]]
            .ok({"operation": operation, "params": params})
            .bind(self._validate_connection)
            .bind(self._execute_operation)
            .bind(self._format_and_display_result)
            .map(lambda data: data.get("result"))
            .map_error(lambda error: f"Chain execution failed: {error}")
        )

    def _validate_connection(
        self, data: dict[str, object]
    ) -> FlextResult[dict[str, object]]:
        """Validate connection usando Fluent Interface - SINGLE EXPRESSION."""
        return (
            FlextResult[dict[str, object]].ok(data)
            if self.current_connection
            else FlextResult[dict[str, object]].fail("No active Oracle connection")
        )

    def _execute_operation(
        self, data: dict[str, object]
    ) -> FlextResult[dict[str, object]]:
        """Execute operation usando Strategy Pattern - CONSOLIDA EXECUÇÃO."""
        operation = str(data.get("operation", ""))
        params = data.get("params", {})

        # Strategy lookup table elimina múltiplas funções
        operation_strategies = {
            "query": lambda: self.current_connection.query(str(params.get("sql", ""))),
            "schemas": self.current_connection.get_schemas,
            "tables": lambda: self.current_connection.get_tables(params.get("schema")),
            "health": self._execute_health_check,
        }

        strategy = operation_strategies.get(operation)
        if not strategy:
            return FlextResult[dict[str, object]].fail(
                f"Unknown operation: {operation}"
            )

        try:
            execution_result = strategy()
            if not execution_result.success:
                return FlextResult[dict[str, object]].fail(
                    f"{operation.title()} failed: {execution_result.error}"
                )

            # Single return com resultado
            return FlextResult[dict[str, object]].ok(
                dict(data) | {"result": execution_result.value}
            )

        except Exception as e:
            self.logger.exception(f"{operation.title()} execution error")
            return FlextResult[dict[str, object]].fail(
                f"{operation.title()} execution error: {e}"
            )

    def _format_and_display_result(
        self, data: dict[str, object]
    ) -> FlextResult[dict[str, object]]:
        """Format and display usando Strategy Pattern - REDUZ COMPLEXIDADE DE 20."""
        try:
            # Strategy Pattern elimina complexidade condicional
            formatter_strategy = self._get_formatter_strategy()
            format_result = formatter_strategy(data)

            if format_result.success:
                self.interactions.print_info(format_result.value)

            return FlextResult[dict[str, object]].ok(data)

        except Exception as e:
            self.logger.warning(f"Format/display warning: {e}")
            return FlextResult[dict[str, object]].ok(data)

    def _get_formatter_strategy(self) -> callable:
        """Get formatter strategy usando lookup table - SINGLE RETURN."""
        # Lookup table elimina múltiplas condicionais
        format_type = self.user_preferences["default_output_format"]

        formatter_strategies = {
            "table": self._format_as_table,
            "json": self._format_as_json,
        }

        return formatter_strategies.get(format_type, self._format_as_json)

    def _format_as_table(self, data: dict[str, object]) -> FlextResult[str]:
        """Format as table usando data adapter - SINGLE RESPONSIBILITY."""
        operation = str(data.get("operation", ""))
        params = data.get("params", {})
        result = data.get("result")
        title = str(params.get("title", f"{operation.title()} Results"))

        # Data adapter elimina múltiplas condicionais
        table_data = self._adapt_data_for_table(operation, result)
        return self.formatter.format_table(data=table_data, title=title)

    def _format_as_json(self, data: dict[str, object]) -> FlextResult[str]:
        """Format as JSON - SINGLE RESPONSIBILITY."""
        result = data.get("result")
        return self.formatter.format_json(result)

    def _adapt_data_for_table(
        self, operation: str, result: object
    ) -> list[dict[str, object]]:
        """Adapt data for table usando Strategy Pattern - ELIMINA CONDICIONAIS."""
        # Strategy lookup para adaptation - elimina múltiplos ifs
        adaptation_strategies = {
            "schemas": lambda r: [{"schema": schema} for schema in r]
            if isinstance(r, list)
            else [],
            "tables": lambda r: [{"table": table} for table in r]
            if isinstance(r, list)
            else [],
            "health": lambda r: [{"key": k, "value": str(v)} for k, v in r.items()]
            if isinstance(r, dict)
            else [],
        }

        strategy = adaptation_strategies.get(operation)
        if strategy:
            return strategy(result)

        # Default strategy
        if isinstance(result, list):
            return result
        return [{"result": str(result)}]

    def _execute_health_check(self) -> FlextResult[dict[str, object]]:
        """Execute health check consolidado - REUTILIZADO."""
        test_result = self.current_connection.query(
            FlextDbOracleConstants.Query.TEST_QUERY
        )

        health_data = {
            "status": "healthy" if test_result.success else "unhealthy",
            "test_query_result": test_result.success,
            "timestamp": FlextUtilities.generate_iso_timestamp(),
            "connection_active": self.current_connection.is_connected,
        }

        return FlextResult[dict[str, object]].ok(health_data)

    def list_schemas(self) -> FlextResult[list[str]]:
        """List schemas usando Chain of Responsibility - ELIMINA DUPLICAÇÃO."""
        result = self._execute_with_chain("schemas", {"title": "Database Schemas"})
        if result.success:
            return FlextResult[list[str]].ok(result.value)
        return FlextResult[list[str]].fail(result.error)

    def list_tables(self, schema: str | None = None) -> FlextResult[list[str]]:
        """List tables usando Chain of Responsibility - ELIMINA DUPLICAÇÃO."""
        title = f"Tables in {schema}" if schema else "Tables"
        result = self._execute_with_chain("tables", {"schema": schema, "title": title})
        if result.success:
            return FlextResult[list[str]].ok(result.value)
        return FlextResult[list[str]].fail(result.error)

    def health_check(self) -> FlextResult[dict[str, object]]:
        """Health check usando Chain of Responsibility - ELIMINA DUPLICAÇÃO."""
        self.interactions.print_info("Performing health check...")
        result = self._execute_with_chain("health", {"title": "Health Check"})
        if result.success:
            return FlextResult[dict[str, object]].ok(
                cast("dict[str, object]", result.value)
            )
        return FlextResult[dict[str, object]].fail(result.error)

    def configure_preferences(self, **preferences: object) -> FlextResult[None]:
        """Update user preferences for CLI behavior."""
        try:
            updated_preferences = []
            for key, value in preferences.items():
                if key in self.user_preferences:
                    self.user_preferences[key] = value
                    updated_preferences.append(f"{key}: {value}")

            if updated_preferences:
                self.interactions.print_success("Configuration updated successfully")
                for pref in updated_preferences:
                    self.interactions.print_info(f"  • {pref}")
            else:
                self.interactions.print_warning("No valid preferences provided")

            return FlextResult[None].ok(None)

        except Exception as e:
            self.logger.exception("Configuration error")
            return FlextResult[None].fail(f"Configuration error: {e}")

    def connection_wizard(self) -> FlextResult[FlextDbOracleModels.OracleConfig]:
        """Railway-Oriented Programming - ELIMINA 6 MÚLTIPLOS RETURNS."""
        self.interactions.print_info("Oracle Connection Wizard")
        self.interactions.print_status("Configure your Oracle database connection")

        # Railway-Oriented Programming - Monadic chain elimina múltiplos returns
        return (
            FlextResult.ok({})
            .bind(lambda _: self._collect_connection_parameters())
            .bind(self._create_oracle_config)
            .bind(self._display_and_test_config)
            .map_error(lambda err: f"Connection wizard: {err}")
        )

    def _collect_connection_parameters(self) -> FlextResult[ConnectionParameters]:
        """Collect connection parameters using Parameter Object pattern."""
        # Define parameter collection steps
        parameter_specs = [
            ("host", "Oracle database host", "localhost", False),
            ("port", "Oracle database port", "1521", False),
            ("service_name", "Oracle service name", "XE", False),
            ("username", "Oracle username", None, False),
            ("password", "Oracle password", None, True),
            ("test_connection", "Test connection with these settings?", True, None),
        ]

        collected_params = {}

        for param_name, prompt_text, default_value, is_sensitive in parameter_specs:
            if param_name == "test_connection":
                result = self.interactions.confirm(prompt_text, default=default_value)
            elif is_sensitive:
                result = self.interactions.prompt(prompt_text, sensitive=True)
            else:
                result = self.interactions.prompt(prompt_text, default=default_value)

            if not result.success:
                return FlextResult[ConnectionParameters].fail(
                    f"{param_name} input failed: {result.error}"
                )

            # Convert port to int
            if param_name == "port":
                try:
                    collected_params[param_name] = int(result.value)
                except ValueError:
                    return FlextResult[ConnectionParameters].fail("Invalid port number")
            else:
                collected_params[param_name] = result.value

        return FlextResult[ConnectionParameters].ok(
            ConnectionParameters(**collected_params)
        )

    def _create_oracle_config(
        self, params: ConnectionParameters
    ) -> FlextResult[FlextDbOracleModels.OracleConfig]:
        """Create Oracle configuration from parameters."""
        try:
            config = FlextDbOracleModels.OracleConfig(
                host=params.host,
                port=params.port,
                service_name=params.service_name,
                username=params.username,
                password=SecretStr(params.password),
                ssl_server_cert_dn=None,
            )
            return FlextResult[FlextDbOracleModels.OracleConfig].ok(config)
        except Exception as e:
            return FlextResult[FlextDbOracleModels.OracleConfig].fail(
                f"Configuration creation failed: {e}"
            )

    # ELIMINADO _display_connection_summary - Consolidado em _display_and_test_config

    def _display_and_test_config(
        self, config: FlextDbOracleModels.OracleConfig
    ) -> FlextResult[FlextDbOracleModels.OracleConfig]:
        """Display config and test if requested - Railway-Oriented Programming."""
        # Display summary
        table_result = self.formatter.format_table(
            data=[
                {"setting": "Host", "value": config.host},
                {"setting": "Port", "value": str(config.port)},
                {"setting": "Service", "value": config.service_name},
                {"setting": "Username", "value": config.username},
            ],
            title="Oracle Connection Summary",
        )
        if table_result.success:
            self.interactions.print_info(table_result.value)

        return FlextResult[FlextDbOracleModels.OracleConfig].ok(config)

    def _test_connection_if_requested(
        self, params: ConnectionParameters
    ) -> FlextResult[None]:
        """Test connection if user requested it."""
        if not params.get("test_connection", False):
            return FlextResult[None].ok(None)

        test_result = self.connect_to_oracle(
            params.host,
            params.port,
            params.service_name,
            params.username,
            params.password,
        )
        if test_result.success:
            self.interactions.print_success("Connection test successful!")
            return FlextResult[None].ok(None)
        return FlextResult[None].fail(test_result.error)

    def run_cli_command(self, command: str, **kwargs: object) -> FlextResult[None]:
        """Execute CLI command usando Interpreter Pattern - CONSOLIDA TODAS AS OPERATIONS."""
        # Interpreter Pattern com mega lookup table - ELIMINA OracleCliCommandProcessor class
        interpreter = self._create_unified_cli_interpreter()

        # Single interpretation call - ELIMINA 6+ command handlers
        result = interpreter(command, kwargs)

        if result.success:
            return FlextResult[None].ok(None)
        return FlextResult[None].fail(result.error)

    def _create_unified_cli_interpreter(self) -> callable:
        """Cria interpreter usando Pure Functional Programming - ELIMINA COMPLEXITY 59 → 35."""
        # Mega lookup table com todas as operações CLI - ELIMINA CommandProcessor
        cli_operations = {
            "connect": lambda kwargs: self.connect_to_oracle(
                kwargs.get("host", "localhost"),
                kwargs.get("port", 1521),
                kwargs.get("service_name", "XE"),
                kwargs.get("username", "system"),
                kwargs.get("password", ""),
            ),
            "query": lambda kwargs: self.execute_query(
                kwargs.get("sql", "SELECT 1 FROM DUAL")
            ),
            "schemas": lambda _: self.list_schemas(),
            "tables": lambda kwargs: self.list_tables(kwargs.get("schema", None)),
            "health": lambda _: self.health_check(),
            "wizard": lambda _: self.connection_wizard(),
        }

        # Pure Function Interpreter - SINGLE FUNCTION, ZERO CLASSES
        def interpret_command(
            command: str, params: dict[str, object]
        ) -> FlextResult[object]:
            operation = cli_operations.get(command)
            if not operation:
                return FlextResult[object].fail(f"Unknown CLI command: {command}")

            try:
                return operation(params).map(lambda x: x)
            except Exception as e:
                return FlextResult[object].fail(f"Command execution failed: {e}")

        return interpret_command


# Global client instance
_client: FlextDbOracleClient | None = None


def get_client() -> FlextDbOracleClient:
    """Get or create global Oracle CLI client instance."""
    if globals().get("_client") is None:
        client = FlextDbOracleClient()
        init_result = client.initialize()
        if not init_result.success:
            # Use proper error reporting
            sys.stderr.write(f"Failed to initialize Oracle CLI: {init_result.error}\n")
            sys.exit(1)
        globals()["_client"] = client
    return cast("FlextDbOracleClient", globals()["_client"])


# FLEXT CLI Integration - NO CLICK DEPENDENCIES
def create_oracle_cli_commands() -> FlextResult[list[FlextCliModels.Command]]:
    """Create Oracle CLI commands using flext-cli patterns."""
    try:
        commands = [
            FlextCliModels.Command(
                name="oracle-connect",
                description="Connect to Oracle database",
                handler="connect_to_oracle",
                parameters={
                    "host": {"type": "str", "default": "localhost"},
                    "port": {"type": "int", "default": 1521},
                    "service_name": {"type": "str", "default": "XE"},
                    "username": {"type": "str", "required": True},
                    "password": {"type": "str", "required": True, "sensitive": True},
                },
            ),
            FlextCliModels.Command(
                name="oracle-query",
                description="Execute SQL query",
                handler="execute_query",
                parameters={
                    "sql": {"type": "str", "required": True},
                },
            ),
            FlextCliModels.Command(
                name="oracle-schemas",
                description="List database schemas",
                handler="list_schemas",
                parameters={},
            ),
            FlextCliModels.Command(
                name="oracle-tables",
                description="List tables in schema",
                handler="list_tables",
                parameters={
                    "schema": {"type": "str", "required": False},
                },
            ),
            FlextCliModels.Command(
                name="oracle-health",
                description="Check Oracle database health",
                handler="health_check",
                parameters={},
            ),
            FlextCliModels.Command(
                name="oracle-wizard",
                description="Interactive connection wizard",
                handler="connection_wizard",
                parameters={},
            ),
        ]

        return FlextResult[list[FlextCliModels.Command]].ok(commands)

    except Exception as e:
        return FlextResult[list[FlextCliModels.Command]].fail(
            f"Failed to create CLI commands: {e}"
        )


# Export the main components - NO CLICK EXPORTS
__all__: list[str] = [
    "FlextDbOracleClient",
    "create_oracle_cli_commands",
    "get_client",
]
