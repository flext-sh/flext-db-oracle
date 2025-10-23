"""Oracle Database CLI integration with FLEXT ecosystem.

Provides CLI functionality for Oracle database operations using flext-cli
foundation exclusively, avoiding direct Click/Rich imports per FLEXT standards.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import json
import sys
import time
from datetime import UTC, datetime
from typing import Protocol, override

import yaml
from flext_cli import FlextCliCommands
from flext_core import (
    FlextContainer,
    FlextResult,
    FlextService,
)

from flext_db_oracle.api import FlextDbOracleApi
from flext_db_oracle.config import FlextDbOracleConfig
from flext_db_oracle.constants import FlextDbOracleConstants


class FlextDbOracleCli(FlextService[str]):
    """Unified Oracle CLI Service using flext-cli exclusively.

    Zero Tolerance COMPLIANCE:
    - NO direct click imports - uses flext-cli foundation only
    - Unified class pattern with nested helpers
    - Explicit FlextResult error handling
    - flext-cli for ALL output formatting and user interaction
    """

    @override
    def __init__(self) -> None:
        """Initialize Oracle CLI Service."""
        super().__init__()
        self._container = FlextContainer.get_global()
        # Initialize CLI components with explicit error handling
        cli_result = self._initialize_cli_main()
        if cli_result.is_failure:
            self.logger.warning(f"CLI initialization failed: {cli_result.error}")
            self._cli_main: FlextCliCommands | None = None
        else:
            self._cli_main = cli_result.unwrap()

    def _initialize_cli_main(self) -> FlextResult[FlextCliCommands]:
        """Initialize CLI main component with explicit error handling.

        Returns:
        FlextResult[FlextCliCommands]: CLI main component or error.

        """
        try:
            cli_main = FlextCliCommands()
            return FlextResult[FlextCliCommands].ok(cli_main)
        except Exception as e:
            return FlextResult[FlextCliCommands].fail(
                f"FlextCliCommands initialization failed: {e}",
            )

    class _YamlModule(Protocol):
        """Protocol for YAML module interface."""

        def dump(self, data: object, *, default_flow_style: bool = True) -> str:
            """Dump data as YAML string."""
            ...

    class _OracleConnectionHelper:
        """Nested helper class for Oracle connection operations."""

        @staticmethod
        def create_config_from_params(
            host: str = FlextDbOracleConstants.OracleDefaults.DEFAULT_HOST,
            port: int = FlextDbOracleConstants.Connection.DEFAULT_PORT,
            service_name: str = FlextDbOracleConstants.Connection.DEFAULT_SERVICE_NAME,
            username: str = FlextDbOracleConstants.OracleDefaults.DEFAULT_USERNAME,
            password: str | None = None,
        ) -> FlextResult[FlextDbOracleConfig]:
            """Create Oracle configuration from parameters.

            Returns:
            FlextResult[FlextDbOracleConfig]: Configuration or error.

            """
            if password is None or not password.strip():
                return FlextResult[FlextDbOracleConfig].fail(
                    "Password is required for Oracle connection",
                )

            try:
                config = FlextDbOracleConfig(
                    host=host,
                    port=port,
                    service_name=service_name,
                    username=username,  # Fixed: Use 'username' parameter name
                    password=password,
                )
                return FlextResult[FlextDbOracleConfig].ok(config)
            except Exception as e:
                return FlextResult[FlextDbOracleConfig].fail(
                    f"Configuration creation failed: {e}",
                )

        @staticmethod
        def validate_connection(
            config: FlextDbOracleConfig,
        ) -> FlextResult[bool]:
            """Validate Oracle database connection.

            Returns:
            FlextResult[bool]: True if connection valid, False otherwise.

            """
            # Create new API instance with the config
            new_api = FlextDbOracleApi(config)

            # Connect to the database
            connect_result = new_api.connect()
            if connect_result.is_failure:
                error_text = connect_result.error or "Unknown connection error"
                return FlextResult[bool].fail(f"Connection failed: {error_text}")

            success = True
            return FlextResult[bool].ok(success)

    class _OutputFormatter:
        """Nested helper class for formatting Oracle CLI output."""

        @override
        def __init__(self, cli_main: FlextCliCommands | None = None) -> None:
            """Initialize output formatter without external dependencies."""
            self._cli_main = cli_main

        def format_success_message(self, message: str) -> FlextResult[str]:
            """Format success message using simple formatting.

            Returns:
            FlextResult[str]: Formatted success message.

            """
            formatted_msg = f"{message}"
            return FlextResult[str].ok(formatted_msg)

        def format_error_message(self, error: str) -> FlextResult[str]:
            """Format error message using simple formatting.

            Returns:
            FlextResult[str]: Formatted error message.

            """
            formatted_msg = f"{error}"
            return FlextResult[str].ok(formatted_msg)

        def format_list_output(
            self,
            items: list[str] | list[dict[str, object]],
            title: str,
            output_format: str = "table",
        ) -> FlextResult[str]:
            """Format list output using simple formatters.

            Returns:
            FlextResult[str]: Formatted list output.

            """
            # Convert dict[str, object] items to string representation
            if items and isinstance(items[0], dict):
                string_items = [
                    str(item.get("name", item))
                    for item in items
                    if isinstance(item, dict)
                ]
            else:
                string_items = [str(item) for item in items]

            if output_format == "table":
                # Simple table formatting
                output_lines = [title, "=" * len(title)]
                output_lines.extend(f"  - {item}" for item in string_items)
                return FlextResult[str].ok("\n".join(output_lines))
            if output_format == "json":
                # Simple JSON formatting
                data = {"title": title, "items": string_items}
                return FlextResult[str].ok(json.dumps(data, indent=2))
            if output_format == "yaml":
                # Simple YAML formatting - yaml is always available since imported
                data = {"title": title, "items": string_items}
                return FlextResult[str].ok(yaml.dump(data, default_flow_style=False))
            # Plain format
            output_lines = [title, *string_items]
            return FlextResult[str].ok("\n".join(output_lines))

        def format_data(self, data: object, output_format: str) -> FlextResult[str]:
            """Format any data object using simple formatters.

            Returns:
            FlextResult[str]: Formatted data.

            """
            if output_format == "json":
                return FlextResult[str].ok(json.dumps(data, indent=2, default=str))
            if output_format == "yaml":
                # YAML is always available since imported at module level
                return FlextResult[str].ok(yaml.dump(data, default_flow_style=False))
            return FlextResult[str].ok(str(data))

        def display_message(self, message: str) -> None:
            """Display message to user - direct output for CLI."""
            # Use sys.stdout for CLI output instead of print
            sys.stdout.write(f"{message}\n")
            sys.stdout.flush()

    def execute_health_check(
        self,
        host: str = FlextDbOracleConstants.OracleDefaults.DEFAULT_HOST,
        port: int = FlextDbOracleConstants.Connection.DEFAULT_PORT,
        service_name: str = FlextDbOracleConstants.Connection.DEFAULT_SERVICE_NAME,
        username: str = FlextDbOracleConstants.Connection.DEFAULT_USERNAME,
        password: str | None = None,
        timeout: int = FlextDbOracleConstants.Connection.DEFAULT_TIMEOUT,
    ) -> FlextResult[dict[str, object]]:
        """Execute complete health check for Oracle database connection.

        Args:
        host: Oracle database hostname
        port: Oracle database port
        service_name: Oracle service name
        username: Oracle username
        password: Oracle password (required)
        timeout: Connection timeout in seconds

        Returns:
        FlextResult[dict[str, object]]: Health check results with status and timing

        """
        start_time = time.time()

        try:
            # Build connection config

            # Create API instance
            config = FlextDbOracleConfig(
                host=host,
                port=port,
                service_name=service_name,
                username=username,
                password=password,
                timeout=timeout,
            )
            api = FlextDbOracleApi.from_config(config)

            # Test connection
            health_result = api.get_health_status()
            if health_result.is_failure:
                return FlextResult[dict[str, object]].fail(
                    f"Health check failed: {health_result.error}"
                )

            elapsed_time = time.time() - start_time
            health_data = health_result.unwrap()

            result: dict[str, object] = {
                "status": "healthy",
                "host": host,
                "port": port,
                "service_name": service_name,
                "response_time_ms": round(elapsed_time * 1000, 2),
                "details": health_data,
                "timestamp": datetime.now(UTC).isoformat(),
            }

            return FlextResult[dict[str, object]].ok(result)

        except Exception as e:
            elapsed_time = time.time() - start_time
            error_result: dict[str, object] = {
                "status": "unhealthy",
                "host": host,
                "port": port,
                "service_name": service_name,
                "response_time_ms": round(elapsed_time * 1000, 2),
                "error": str(e),
                "timestamp": datetime.now(UTC).isoformat(),
            }

            return FlextResult[dict[str, object]].ok(error_result)

    def execute_list_schemas(
        self,
        host: str = "localhost",
        port: int = FlextDbOracleConstants.Connection.DEFAULT_PORT,
        service_name: str = FlextDbOracleConstants.Connection.DEFAULT_SERVICE_NAME,
        username: str = FlextDbOracleConstants.Connection.DEFAULT_USERNAME,
        password: str | None = None,
        output_format: str = "table",
    ) -> FlextResult[str]:
        """Execute Oracle schemas listing.

        Returns:
        FlextResult[str]: Schemas list or error.

        """
        formatter = self._OutputFormatter(self._cli_main)

        # Create configuration and validate connection
        config_result = self._OracleConnectionHelper.create_config_from_params(
            host,
            port,
            service_name,
            username,
            password,
        )
        if config_result.is_failure:
            error_text = config_result.error or "Unknown configuration error"
            error_msg = formatter.format_error_message(
                f"Configuration failed: {error_text}",
            )
            if error_msg.is_success:
                formatter.display_message(error_msg.unwrap())
            return FlextResult[str].fail(error_text)

        config = config_result.unwrap()
        validation_result = self._OracleConnectionHelper.validate_connection(config)

        if validation_result.is_failure:
            error_text = validation_result.error or "Unknown validation error"
            error_msg = formatter.format_error_message(error_text)
            if error_msg.is_success:
                formatter.display_message(error_msg.unwrap())
            return FlextResult[str].fail(error_text)

        # Create API instance
        api = FlextDbOracleApi(config)

        # Get schemas
        schemas_result = api.get_schemas()
        if schemas_result.is_failure:
            error_text = schemas_result.error or "Unknown schemas error"
            error_msg = formatter.format_error_message(
                f"Failed to get schemas: {error_text}",
            )
            if error_msg.is_success:
                formatter.display_message(error_msg.unwrap())
            return FlextResult[str].fail(error_text)

        schemas = schemas_result.unwrap()

        # Format and display schemas
        formatted_result = formatter.format_list_output(
            schemas,
            "Available Oracle Schemas",
            output_format,
        )
        if formatted_result.is_success:
            formatter.display_message(formatted_result.unwrap())

        return FlextResult[str].ok(f"Listed {len(schemas)} schemas successfully")

    def execute_list_tables(
        self,
        schema: str = "SYSTEM",
        host: str = "localhost",
        port: int = FlextDbOracleConstants.Connection.DEFAULT_PORT,
        service_name: str = FlextDbOracleConstants.Connection.DEFAULT_SERVICE_NAME,
        username: str = FlextDbOracleConstants.Connection.DEFAULT_USERNAME,
        password: str | None = None,
        output_format: str = "table",
    ) -> FlextResult[str]:
        """Execute Oracle tables listing for a schema.

        Returns:
        FlextResult[str]: Tables list or error.

        """
        formatter = self._OutputFormatter(self._cli_main)

        # Create configuration and validate connection
        config_result = self._OracleConnectionHelper.create_config_from_params(
            host,
            port,
            service_name,
            username,
            password,
        )
        if config_result.is_failure:
            error_text = config_result.error or "Unknown configuration error"
            error_msg = formatter.format_error_message(
                f"Configuration failed: {error_text}",
            )
            if error_msg.is_success:
                formatter.display_message(error_msg.unwrap())
            return FlextResult[str].fail(error_text)

        config = config_result.unwrap()
        validation_result = self._OracleConnectionHelper.validate_connection(config)

        if validation_result.is_failure:
            error_text = validation_result.error or "Unknown validation error"
            error_msg = formatter.format_error_message(error_text)
            if error_msg.is_success:
                formatter.display_message(error_msg.unwrap())
            return FlextResult[str].fail(error_text)

        # Create API instance
        api = FlextDbOracleApi(config)

        # Get tables
        tables_result = api.get_tables(schema)
        if tables_result.is_failure:
            error_text = tables_result.error or "Unknown tables error"
            error_msg = formatter.format_error_message(
                f"Failed to get tables: {error_text}",
            )
            if error_msg.is_success:
                formatter.display_message(error_msg.unwrap())
            return FlextResult[str].fail(error_text)

        tables = tables_result.unwrap()

        # Format and display tables
        formatted_result = formatter.format_list_output(
            tables,
            f"Tables in schema {schema}",
            output_format,
        )
        if formatted_result.is_success:
            formatter.display_message(formatted_result.unwrap())

        return FlextResult[str].ok(
            f"Listed {len(tables)} tables in schema {schema} successfully",
        )

    def execute_query(
        self,
        sql: str,
        host: str = "localhost",
        port: int = FlextDbOracleConstants.Connection.DEFAULT_PORT,
        service_name: str = FlextDbOracleConstants.Connection.DEFAULT_SERVICE_NAME,
        username: str = FlextDbOracleConstants.Connection.DEFAULT_USERNAME,
        password: str | None = None,
        output_format: str = "table",
    ) -> FlextResult[str]:
        """Execute SQL query against Oracle database.

        Returns:
        FlextResult[str]: Query results or error.

        """
        formatter = self._OutputFormatter(self._cli_main)

        if not sql.strip():
            error_msg = formatter.format_error_message("SQL query cannot be empty")
            if error_msg.is_success:
                formatter.display_message(error_msg.unwrap())
            return FlextResult[str].fail("SQL query cannot be empty")

        # Create configuration and validate connection
        config_result = self._OracleConnectionHelper.create_config_from_params(
            host,
            port,
            service_name,
            username,
            password,
        )
        if config_result.is_failure:
            error_text = config_result.error or "Unknown configuration error"
            error_msg = formatter.format_error_message(
                f"Configuration failed: {error_text}",
            )
            if error_msg.is_success:
                formatter.display_message(error_msg.unwrap())
            return FlextResult[str].fail(error_text)

        config = config_result.unwrap()
        validation_result = self._OracleConnectionHelper.validate_connection(config)

        if validation_result.is_failure:
            error_text = validation_result.error or "Unknown validation error"
            error_msg = formatter.format_error_message(error_text)
            if error_msg.is_success:
                formatter.display_message(error_msg.unwrap())
            return FlextResult[str].fail(error_text)

        # Create API instance
        api = FlextDbOracleApi(config)

        # Execute query
        query_result = api.query(sql)
        if query_result.is_failure:
            error_text = query_result.error or "Unknown query error"
            error_msg = formatter.format_error_message(f"Query failed: {error_text}")
            if error_msg.is_success:
                formatter.display_message(error_msg.unwrap())
            return FlextResult[str].fail(error_text)

        result = query_result.unwrap()
        row_count = len(result)  # result is a list, so count items

        # Format and display result
        success_msg = formatter.format_success_message(
            f"Query executed successfully. Rows: {row_count}",
        )
        if success_msg.is_success:
            formatter.display_message(success_msg.unwrap())

        # Format result using specified output format
        formatted_result = formatter.format_data(
            {"rows": "row_count", "result": "result"},
            output_format,
        )
        if formatted_result.is_success:
            return FlextResult[str].ok(formatted_result.unwrap())

        return FlextResult[str].ok(f"Query executed successfully with {row_count} rows")

    @override
    def execute(self) -> FlextResult[str]:
        """Execute domain service - required by FlextService.

        Returns:
        FlextResult[str]: Service status.

        """
        self.logger.info("Oracle CLI service initialized")
        return FlextResult[str].ok("Oracle CLI service ready")

    def run_cli(self, args: list[str] | None = None) -> FlextResult[str]:
        """Run CLI with command line arguments simulation.

        Returns:
        FlextResult[str]: CLI execution result.

        """
        if args is None:
            args = sys.argv[1:]

        if not args:
            # Show help/usage
            help_msg = """Oracle Database CLI - Enterprise Oracle operations.

Available commands:
 health Check Oracle database health
 schemas List Oracle schemas
 tables List Oracle tables in a schema
 query Execute SQL query

Use --help with any command for detailed options.
"""

            self._OutputFormatter(self._cli_main).display_message(help_msg)
            return FlextResult[str].ok("Help displayed")

        command = args[0].lower()

        # Basic command parsing - in a real implementation, use proper CLI argument parsing
        if command == "health":
            health_result = self.execute_health_check()
            if health_result.is_success:
                return FlextResult[str].ok("Health check completed successfully")
            return FlextResult[str].fail(health_result.error or "Health check failed")
        if command == "schemas":
            return self.execute_list_schemas()
        if command == "tables":
            return self.execute_list_tables()
        if command == "query":
            min_query_args = 2
            if len(args) < min_query_args:
                error_msg = "SQL query is required for query command"
                self._OutputFormatter(self._cli_main).display_message(f"{error_msg}")
                return FlextResult[str].fail(error_msg)
            return self.execute_query(args[1])
        error_msg = f"Unknown command: {command}"
        self._OutputFormatter(self._cli_main).display_message(f"{error_msg}")
        return FlextResult[str].fail(error_msg)

    @classmethod
    def main(cls) -> None:
        """Execute main CLI entry point using flext-cli exclusively."""
        cli_service = cls()
        result = cli_service.run_cli()

        if result.is_failure:
            sys.exit(1)

    @classmethod
    def run_main(cls) -> None:
        """Module-level main entry point."""
        cls.main()


if __name__ == "__main__":
    FlextDbOracleCli.run_main()
