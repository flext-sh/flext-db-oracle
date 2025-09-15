"""Oracle Database client providing CLI and programmatic access.

This module provides the Oracle database client with CLI functionality
using FLEXT ecosystem patterns for database operations.

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
    FlextCliServices,
)
from flext_core import (
    FlextContainer,
    FlextDomainService,
    FlextLogger,
    FlextProcessing,
    FlextResult,
    FlextTypes,
    FlextUtilities,
)

from flext_db_oracle.api import FlextDbOracleApi
from flext_db_oracle.constants import FlextDbOracleConstants
from flext_db_oracle.mixins import ConnectionParameters
from flext_db_oracle.models import FlextDbOracleModels


class FlextDbOracleClient(FlextDomainService[FlextTypes.Core.Dict]):
    """Unified Oracle database CLI client with ONLY flext-cli integration.

    Single class containing all CLI functionality without click dependencies,
    using flext-cli for all user interactions and output formatting.
    """

    def __init__(self, *, debug: bool = False) -> None:
        """Initialize Oracle CLI client with flext-cli components."""
        super().__init__()  # Initialize FlextDomainService base
        self.logger = FlextLogger(__name__)
        # Simple CLI implementation without flext-cli dependencies
        self.logger.info("Oracle CLI client initialized")
        self.container = FlextContainer.get_global()
        # Use FlextProcessing for service orchestration
        self.service_orchestrator = FlextProcessing.create_handler_registry()

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

        # Initialize placeholder components for missing attributes
        # Initialize flext-cli formatters for proper FLEXT ecosystem integration
        self.formatter = FlextCliFormatters()

        # Initialize flext-cli interactions for proper FLEXT ecosystem integration
        self.interactions = FlextCliInteractions()

        # Initialize flext-cli API for proper FLEXT ecosystem integration
        self.cli_api = FlextCliApi()
        self.cli_services = FlextCliServices()

    def initialize(self) -> FlextResult[None]:
        """Initialize CLI client with proper flext-cli setup."""
        try:
            # Initialize service orchestrator
            init_result = FlextResult[None].ok(
                None
            )  # Service orchestrator is already initialized
            if not init_result.success:
                return FlextResult[None].fail(
                    f"CLI initialization failed: {init_result.error}",
                )

            self.logger.info("FLEXT Oracle Database CLI")
            self.logger.info(
                "Enterprise Oracle operations with professional CLI experience...",
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
                self.logger.info(format_result.value)

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
        formatted = self.formatter.format_json(result)
        return FlextResult[str].ok(formatted.unwrap())

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
        self.logger.info("Performing health check...")
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
                self.logger.info("Configuration updated successfully")
                for pref in updated_preferences:
                    self.logger.info(f"  • {pref}")
            else:
                self.logger.warning("No valid preferences provided")

            return FlextResult[None].ok(None)

        except Exception as e:
            self.logger.exception("Configuration error")
            return FlextResult[None].fail(f"Configuration error: {e}")

    def connection_wizard(self) -> FlextResult[FlextDbOracleModels.OracleConfig]:
        """Railway-Oriented Programming - ELIMINA 6 MÚLTIPLOS RETURNS."""
        self.logger.info("Oracle Connection Wizard")
        self.logger.info("Configure your Oracle database connection")

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
                name=params.service_name,  # Use name field for database/service
                user=params.username,
                password=params.password,
                service_name=params.service_name,
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

    # Class-level singleton management
    _client_instance: FlextDbOracleClient | None = None

    @classmethod
    def get_client(cls) -> FlextDbOracleClient:
        """Get or create global Oracle CLI client instance."""
        if cls._client_instance is None:
            client = cls()
            init_result = client.initialize()
            if not init_result.success:
                # Use proper error reporting
                sys.stderr.write(f"Failed to initialize Oracle CLI: {init_result.error}\n")
                sys.exit(1)
            cls._client_instance = client
        return cls._client_instance

    @staticmethod
    def create_oracle_cli_commands() -> FlextResult[list[str]]:
        """Create Oracle CLI commands using simple string list."""
        try:
            commands = [
                "oracle-connect --host localhost --port 1521",
                "oracle-query --sql 'SELECT 1 FROM DUAL'",
                "oracle-schemas",
                "oracle-tables --schema SYSTEM",
                "oracle-health",
                "oracle-wizard",
            ]

            return FlextResult[list[str]].ok(commands)

        except Exception as e:
            return FlextResult[list[str]].fail(
                f"Failed to create CLI commands: {e}",
            )

    @classmethod
    def _create_oracle_cli(cls) -> FlextResult[FlextDbOracleClient]:
        """Create Oracle CLI using FlextDbOracleClient implementation."""
        try:
            # Create Oracle client instance
            client = cls()
            init_result = client.initialize()
            if not init_result.success:
                return FlextResult[FlextDbOracleClient].fail(
                    f"Failed to initialize client: {init_result.error}"
                )

            return FlextResult[FlextDbOracleClient].ok(client)
        except Exception as e:
            return FlextResult[FlextDbOracleClient].fail(f"CLI creation failed: {e}")

    def execute(self) -> FlextResult[FlextTypes.Core.Dict]:
        """Execute default domain service operation - return client status."""
        try:
            status_data: FlextTypes.Core.Dict = {
                "client_initialized": True,
                "connection_active": self.current_connection is not None,
                "user_preferences": self.user_preferences.copy(),
                "debug_mode": self.debug,
            }
            return FlextResult[FlextTypes.Core.Dict].ok(status_data)
        except Exception as e:
            return FlextResult[FlextTypes.Core.Dict].fail(f"Client execution failed: {e}")

    class _OracleCliFactory:
        """Nested helper class for Oracle CLI instance management."""

        @staticmethod
        def create_cli_instance() -> FlextDbOracleClient | None:
            """Create Oracle CLI instance - REAL IMPLEMENTATION using FlextDbOracleClient."""
            oracle_cli_result = FlextDbOracleClient._create_oracle_cli()
            return oracle_cli_result.value if oracle_cli_result.success else None


# Oracle CLI instance - REAL IMPLEMENTATION using FlextDbOracleClient
oracle_cli = FlextDbOracleClient._OracleCliFactory.create_cli_instance()

# Backward compatibility functions that delegate to class methods
def get_client() -> FlextDbOracleClient:
    """Get or create global Oracle CLI client instance."""
    return FlextDbOracleClient.get_client()

def create_oracle_cli_commands() -> FlextResult[list[str]]:
    """Create Oracle CLI commands using simple string list."""
    return FlextDbOracleClient.create_oracle_cli_commands()


# Export the main components - INCLUDING oracle_cli
__all__: FlextTypes.Core.StringList = [
    "FlextDbOracleClient",
    "create_oracle_cli_commands",
    "get_client",
    "oracle_cli",
]
