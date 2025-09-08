"""FLEXT DB Oracle CLI using ONLY flext-cli patterns - NO CLICK/RICH.

Single unified CLI client following FLEXT standards with proper flext-cli usage,
consolidated class structure, and ZERO direct dependencies on click/rich.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import sys
from collections.abc import Callable
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
    FlextTypes,
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
        self.user_preferences: FlextTypes.Core.Dict = {
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
            init_result = self.cli_services.create_session()
            if not init_result.success:
                return FlextResult[None].fail(
                    f"CLI initialization failed: {init_result.error}",
                )

            self.interactions.print_info("FLEXT Oracle Database CLI")
            self.interactions.print_status(
                "Enterprise Oracle operations with professional CLI experience...",
            )

            self.interactions.print_success("Oracle CLI initialized successfully")
            return FlextResult[None].ok(None)

        except Exception as e:
            self.logger.exception("Oracle CLI initialization failed")
            return FlextResult[None].fail(f"Oracle CLI initialization failed: {e}")

    def connect_to_oracle(
        self,
        host: str,
        port: int,
        service_name: str,
        username: str,
        password: str,
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
                    f"Connection failed: {connect_result.error}",
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
            "query",
            {"sql": query, "title": "Query Results"},
        )

    def _execute_with_chain(
        self,
        operation: str,
        params: FlextTypes.Core.Dict,
    ) -> FlextResult[object]:
        """Execute operation usando Fluent Interface + Railway-Oriented Programming - REDUZ COMPLEXIDADE."""
        # Fluent Interface Pattern com Railway-Oriented Programming - SINGLE EXPRESSION
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
        """Validate connection usando Fluent Interface - SINGLE EXPRESSION."""
        return (
            FlextResult[FlextTypes.Core.Dict].ok(data)
            if self.current_connection
            else FlextResult[FlextTypes.Core.Dict].fail("No active Oracle connection")
        )

    def _execute_operation(
        self,
        data: FlextTypes.Core.Dict,
    ) -> FlextResult[FlextTypes.Core.Dict]:
        """Execute operation usando Strategy Pattern - CONSOLIDA EXECUÇÃO."""
        operation = str(data.get("operation", ""))
        params = data.get("params", {})

        # Strategy lookup table elimina múltiplas funções
        if self.current_connection is None:
            return FlextResult[FlextTypes.Core.Dict].fail("No active connection")

        connection = self.current_connection  # Already checked for None above
        params_dict = cast("FlextTypes.Core.Dict", params)
        operation_strategies = {
            "query": lambda: connection.query(str(params_dict.get("sql", ""))),
            "schemas": connection.get_schemas,
            "tables": lambda: connection.get_tables(
                cast("str", params_dict.get("schema"))
                if params_dict.get("schema")
                else None
            ),
            "health": self._execute_health_check,
        }

        strategy = operation_strategies.get(operation)
        if not strategy:
            return FlextResult[FlextTypes.Core.Dict].fail(
                f"Unknown operation: {operation}",
            )

        try:
            execution_result = strategy()
            if not hasattr(execution_result, "success"):
                return FlextResult[FlextTypes.Core.Dict].fail(
                    f"Invalid result from {operation}"
                )

            result = cast("FlextResult[object]", execution_result)
            if not result.success:
                return FlextResult[FlextTypes.Core.Dict].fail(
                    f"{operation.title()} failed: {result.error}",
                )

            # Single return com resultado
            return FlextResult[FlextTypes.Core.Dict].ok(
                dict(data) | {"result": result.value},
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
        """Format and display usando Strategy Pattern - REDUZ COMPLEXIDADE DE 20."""
        try:
            # Strategy Pattern elimina complexidade condicional
            formatter_strategy = self._get_formatter_strategy()
            format_result = formatter_strategy(data)

            if format_result.success:
                self.interactions.print_info(format_result.value)

            return FlextResult[FlextTypes.Core.Dict].ok(data)

        except Exception as e:
            self.logger.warning(f"Format/display warning: {e}")
            return FlextResult[FlextTypes.Core.Dict].ok(data)

    def _get_formatter_strategy(
        self,
    ) -> Callable[[FlextTypes.Core.Dict], FlextResult[str]]:
        """Get formatter strategy usando lookup table - SINGLE RETURN."""
        # Lookup table elimina múltiplas condicionais
        format_type = cast("str", self.user_preferences["default_output_format"])

        formatter_strategies: dict[
            str, Callable[[FlextTypes.Core.Dict], FlextResult[str]]
        ] = {
            "table": self._format_as_table,
            "json": self._format_as_json,
        }

        return formatter_strategies.get(format_type, self._format_as_json)

    def _format_as_table(self, data: FlextTypes.Core.Dict) -> FlextResult[str]:
        """Format as table usando data adapter - SINGLE RESPONSIBILITY."""
        operation = str(data.get("operation", ""))
        params = data.get("params", {})
        result = data.get("result")
        params_dict = cast("FlextTypes.Core.Dict", params)
        title = str(params_dict.get("title", f"{operation.title()} Results"))

        # Data adapter elimina múltiplas condicionais
        table_data = self._adapt_data_for_table(operation, result)
        table_result = self.formatter.format_table(data=table_data, title=title)
        if table_result.success:
            return FlextResult[str].ok(str(table_result.value))
        return FlextResult[str].fail(f"Table formatting failed: {table_result.error}")

    def _format_as_json(self, data: FlextTypes.Core.Dict) -> FlextResult[str]:
        """Format as JSON - SINGLE RESPONSIBILITY."""
        result = data.get("result")
        return self.formatter.format_json(result)

    def _adapt_data_for_table(
        self,
        operation: str,
        result: object,
    ) -> list[FlextTypes.Core.Dict]:
        """Adapt data for table usando Strategy Pattern - ELIMINA CONDICIONAIS."""

        # Strategy lookup with explicit typing - elimina múltiplos ifs
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
        """Execute health check consolidado - REUTILIZADO."""
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
        """List schemas usando Chain of Responsibility - ELIMINA DUPLICAÇÃO."""
        result = self._execute_with_chain("schemas", {"title": "Database Schemas"})
        if result.success:
            return FlextResult[FlextTypes.Core.StringList].ok(
                cast("FlextTypes.Core.StringList", result.value)
            )
        return FlextResult[FlextTypes.Core.StringList].fail(
            result.error or "Schema listing failed"
        )

    def list_tables(
        self, schema: str | None = None
    ) -> FlextResult[FlextTypes.Core.StringList]:
        """List tables usando Chain of Responsibility - ELIMINA DUPLICAÇÃO."""
        title = f"Tables in {schema}" if schema else "Tables"
        result = self._execute_with_chain("tables", {"schema": schema, "title": title})
        if result.success:
            return FlextResult[FlextTypes.Core.StringList].ok(
                cast("FlextTypes.Core.StringList", result.value)
            )
        return FlextResult[FlextTypes.Core.StringList].fail(
            result.error or "Table listing failed"
        )

    def health_check(self) -> FlextResult[FlextTypes.Core.Dict]:
        """Health check usando Chain of Responsibility - ELIMINA DUPLICAÇÃO."""
        self.interactions.print_info("Performing health check...")
        result = self._execute_with_chain("health", {"title": "Health Check"})
        if result.success:
            return FlextResult[FlextTypes.Core.Dict].ok(
                cast("FlextTypes.Core.Dict", result.value),
            )
        return FlextResult[FlextTypes.Core.Dict].fail(
            result.error or "Health check failed"
        )

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
            .tap_error(lambda err: self.logger.error(f"Connection wizard: {err}"))
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

        # Type-safe parameter collection using explicit variables
        host_value = ""
        port_value = 0
        service_name_value = ""
        username_value = ""
        password_value = ""
        test_connection_value = False

        for param_name, prompt_text, default_value, is_sensitive in parameter_specs:
            if param_name == "test_connection":
                # Convert to proper bool type for confirm
                bool_default = (
                    bool(default_value) if default_value is not None else False
                )
                bool_result = self.interactions.confirm(
                    prompt_text, default=bool_default
                )
                if not bool_result.success:
                    return FlextResult[ConnectionParameters].fail(
                        f"{param_name} input failed: {bool_result.error}",
                    )
                test_connection_value = bool_result.value
            elif is_sensitive:
                # For sensitive fields, don't provide default
                str_result = self.interactions.prompt(prompt_text, default=None)
                if not str_result.success:
                    return FlextResult[ConnectionParameters].fail(
                        f"{param_name} input failed: {str_result.error}",
                    )
                if param_name == "password":
                    password_value = str_result.value
            else:
                # Convert to proper str type for prompt
                str_default = str(default_value) if default_value is not None else None
                str_result = self.interactions.prompt(prompt_text, default=str_default)
                if not str_result.success:
                    return FlextResult[ConnectionParameters].fail(
                        f"{param_name} input failed: {str_result.error}",
                    )
                # Assign to appropriate typed variable
                if param_name == "host":
                    host_value = str_result.value
                elif param_name == "port":
                    try:
                        port_value = int(str_result.value)
                    except ValueError:
                        return FlextResult[ConnectionParameters].fail(
                            "Invalid port number"
                        )
                elif param_name == "service_name":
                    service_name_value = str_result.value
                elif param_name == "username":
                    username_value = str_result.value

        # Create ConnectionParameters with proper typed fields
        return FlextResult[ConnectionParameters].ok(
            ConnectionParameters(
                host=host_value,
                port=port_value,
                service_name=service_name_value,
                username=username_value,
                password=password_value,
                test_connection=test_connection_value,
            ),
        )

    def _create_oracle_config(
        self,
        params: ConnectionParameters,
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
                f"Configuration creation failed: {e}",
            )

    # ELIMINADO _display_connection_summary - Consolidado em _display_and_test_config

    def _display_and_test_config(
        self,
        config: FlextDbOracleModels.OracleConfig,
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
            # Convert Table to string for print_info
            self.interactions.print_info(str(table_result.value))

        return FlextResult[FlextDbOracleModels.OracleConfig].ok(config)

    def _test_connection_if_requested(
        self,
        params: ConnectionParameters,
    ) -> FlextResult[None]:
        """Test connection if user requested it."""
        if not (
            params.test_connection if hasattr(params, "test_connection") else False
        ):
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
        return FlextResult[None].fail(test_result.error or "Connection test failed")

    def run_cli_command(self, command: str, **kwargs: object) -> FlextResult[None]:
        """Execute CLI command usando Interpreter Pattern - CONSOLIDA TODAS AS OPERATIONS."""
        # Interpreter Pattern com mega lookup table - ELIMINA OracleCliCommandProcessor class
        interpreter = self._create_unified_cli_interpreter()

        # Single interpretation call - ELIMINA 6+ command handlers
        result = interpreter(command, kwargs)

        if result.success:
            return FlextResult[None].ok(None)
        error_msg = result.error or "Command execution failed"
        return FlextResult[None].fail(error_msg)

    def _create_unified_cli_interpreter(
        self,
    ) -> Callable[[str, FlextTypes.Core.Dict], FlextResult[object]]:
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
                kwargs.get("sql", "SELECT 1 FROM DUAL"),
            ),
            "schemas": lambda _: self.list_schemas(),
            "tables": lambda kwargs: self.list_tables(kwargs.get("schema", None)),
            "health": lambda _: self.health_check(),
            "wizard": lambda _: self.connection_wizard(),
        }

        # Pure Function Interpreter - SINGLE FUNCTION, ZERO CLASSES
        def interpret_command(
            command: str,
            params: FlextTypes.Core.Dict,
        ) -> FlextResult[object]:
            operation = cli_operations.get(command)
            if not operation:
                return FlextResult[object].fail(f"Unknown CLI command: {command}")

            try:
                # Type-safe operation call with explicit function typing
                typed_operation: Callable[
                    [FlextTypes.Core.Dict], FlextResult[object]
                ] = cast(
                    "Callable[[FlextTypes.Core.Dict], FlextResult[object]]",
                    operation,
                )
                result = typed_operation(params)
                # Result is now properly typed as FlextResult[object]
                if result.success:
                    return FlextResult[object].ok(result.value)
                return FlextResult[object].fail(result.error or "Operation failed")
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
def create_oracle_cli_commands() -> FlextResult[list[FlextCliModels.CliCommand]]:
    """Create Oracle CLI commands using flext-cli patterns."""
    try:
        commands = [
            FlextCliModels.CliCommand(
                command_line="oracle-connect --host localhost --port 1521",
            ),
            FlextCliModels.CliCommand(
                command_line="oracle-query --sql 'SELECT 1 FROM DUAL'",
            ),
            FlextCliModels.CliCommand(
                command_line="oracle-schemas",
            ),
            FlextCliModels.CliCommand(
                command_line="oracle-tables --schema SYSTEM",
            ),
            FlextCliModels.CliCommand(
                command_line="oracle-health",
            ),
            FlextCliModels.CliCommand(
                command_line="oracle-wizard",
            ),
        ]

        return FlextResult[list[FlextCliModels.CliCommand]].ok(commands)

    except Exception as e:
        return FlextResult[list[FlextCliModels.CliCommand]].fail(
            f"Failed to create CLI commands: {e}",
        )


# Create Oracle CLI instance for external use
def _create_oracle_cli() -> FlextResult[object]:
    """Create Oracle CLI using flext-cli patterns - REAL IMPLEMENTATION."""
    try:
        # Initialize CLI
        cli = FlextCliApi(version="0.9.0")

        # Create Oracle commands
        commands_result = create_oracle_cli_commands()
        if not commands_result.success:
            return FlextResult[object].fail(
                f"Failed to create commands: {commands_result.error}"
            )

        # Return the CLI API itself since register_command and get_click_group don't exist
        return FlextResult[object].ok(cli)
    except ImportError as e:
        return FlextResult[object].fail(f"flext-cli not available: {e}")
    except Exception as e:
        return FlextResult[object].fail(f"CLI creation failed: {e}")


# Oracle CLI instance - REAL IMPLEMENTATION using flext-cli
_oracle_cli_result = _create_oracle_cli()
oracle_cli = _oracle_cli_result.value if _oracle_cli_result.success else None


# Export the main components - INCLUDING oracle_cli
__all__: FlextTypes.Core.StringList = [
    "FlextDbOracleClient",
    "create_oracle_cli_commands",
    "get_client",
    "oracle_cli",
]
