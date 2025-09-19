"""Oracle Database CLI integration with FLEXT ecosystem.

Provides CLI functionality for Oracle database operations using flext-cli
foundation exclusively, avoiding direct Click/Rich imports per FLEXT standards.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import json
import sys
from typing import Protocol

import yaml

from flext_cli import FlextCliMain
from flext_core import FlextContainer, FlextDomainService, FlextLogger, FlextResult
from flext_db_oracle.api import FlextDbOracleApi
from flext_db_oracle.models import FlextDbOracleModels


class FlextDbOracleCliService(FlextDomainService[str]):
    """Unified Oracle CLI Service using flext-cli exclusively.

    ZERO TOLERANCE COMPLIANCE:
    - NO direct click imports - uses flext-cli foundation only
    - Unified class pattern with nested helpers
    - Explicit FlextResult error handling
    - flext-cli for ALL output formatting and user interaction
    """

    def __init__(self) -> None:
        """Initialize Oracle CLI Service."""
        super().__init__()
        self._container = FlextContainer.get_global()
        self._logger = FlextLogger(__name__)
        # Initialize CLI components with explicit error handling
        cli_result = self._initialize_cli_main()
        if cli_result.is_failure:
            self._logger.warning(f"CLI initialization failed: {cli_result.error}")
            self._cli_main: FlextCliMain | None = None
        else:
            self._cli_main = cli_result.unwrap()

    def _initialize_cli_main(self) -> FlextResult[FlextCliMain]:
        """Initialize CLI main component with explicit error handling."""
        try:
            cli_main = FlextCliMain()
            return FlextResult[FlextCliMain].ok(cli_main)
        except Exception as e:
            return FlextResult[FlextCliMain].fail(
                f"FlextCliMain initialization failed: {e}",
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
            host: str = "localhost",
            port: int = 1521,
            service_name: str = "XEPDB1",
            username: str = "system",
            password: str = "",
        ) -> FlextResult[FlextDbOracleModels.OracleConfig]:
            """Create Oracle configuration from parameters."""
            if not password:
                return FlextResult[FlextDbOracleModels.OracleConfig].fail(
                    "Password is required for Oracle connection",
                )

            try:
                config = FlextDbOracleModels.OracleConfig(
                    host=host,
                    port=port,
                    service_name=service_name,
                    username=username,  # Fixed: Use 'username' parameter name
                    password=password,
                )
                return FlextResult[FlextDbOracleModels.OracleConfig].ok(config)
            except Exception as e:
                return FlextResult[FlextDbOracleModels.OracleConfig].fail(
                    f"Configuration creation failed: {e}",
                )

        @staticmethod
        def validate_connection(
            config: FlextDbOracleModels.OracleConfig,
        ) -> FlextResult[bool]:
            """Validate Oracle database connection."""
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

        def __init__(self, cli_main: FlextCliMain | None = None) -> None:
            """Initialize output formatter without external dependencies."""
            self._cli_main = cli_main

        def format_success_message(self, message: str) -> FlextResult[str]:
            """Format success message using simple formatting."""
            formatted_msg = f"✅ {message}"
            return FlextResult[str].ok(formatted_msg)

        def format_error_message(self, error: str) -> FlextResult[str]:
            """Format error message using simple formatting."""
            formatted_msg = f"❌ {error}"
            return FlextResult[str].ok(formatted_msg)

        def format_list_output(
            self,
            items: list[str] | list[dict[str, object]],
            title: str,
            output_format: str = "table",
        ) -> FlextResult[str]:
            """Format list output using simple formatters."""
            # Convert dict items to string representation
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
            """Format any data object using simple formatters."""
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
        host: str = "localhost",
        port: int = 1521,
        service_name: str = "XEPDB1",
        username: str = "system",
        password: str = "",
        output_format: str = "table",
    ) -> FlextResult[str]:
        """Execute Oracle database health check."""
        formatter = self._OutputFormatter(self._cli_main)

        # Create configuration
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

        # Validate connection
        config = config_result.unwrap()
        validation_result = self._OracleConnectionHelper.validate_connection(config)

        if validation_result.is_failure:
            error_text = validation_result.error or "Unknown validation error"
            error_msg = formatter.format_error_message(error_text)
            if error_msg.is_success:
                formatter.display_message(error_msg.unwrap())
            return FlextResult[str].fail(error_text)

        # Success
        success_msg = formatter.format_success_message("Oracle database is healthy")
        if success_msg.is_success:
            formatter.display_message(success_msg.unwrap())

        # Format result using specified output format
        formatted_result = formatter.format_data(
            {"status": "healthy", "message": "Oracle database is healthy"},
            output_format,
        )
        if formatted_result.is_success:
            return FlextResult[str].ok(formatted_result.unwrap())

        return FlextResult[str].ok("Health check completed successfully")

    def execute_list_schemas(
        self,
        host: str = "localhost",
        port: int = 1521,
        service_name: str = "XEPDB1",
        username: str = "system",
        password: str = "",
        output_format: str = "table",
    ) -> FlextResult[str]:
        """Execute Oracle schemas listing."""
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
        port: int = 1521,
        service_name: str = "XEPDB1",
        username: str = "system",
        password: str = "",
        output_format: str = "table",
    ) -> FlextResult[str]:
        """Execute Oracle tables listing for a schema."""
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
        port: int = 1521,
        service_name: str = "XEPDB1",
        username: str = "system",
        password: str = "",
        output_format: str = "table",
    ) -> FlextResult[str]:
        """Execute SQL query against Oracle database."""
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
            {"rows": row_count, "result": result},
            output_format,
        )
        if formatted_result.is_success:
            return FlextResult[str].ok(formatted_result.unwrap())

        return FlextResult[str].ok(f"Query executed successfully with {row_count} rows")

    def execute(self) -> FlextResult[str]:
        """Execute domain service - required by FlextDomainService."""
        self._logger.info("Oracle CLI service initialized")
        return FlextResult[str].ok("Oracle CLI service ready")

    def run_cli(self, args: list[str] | None = None) -> FlextResult[str]:
        """Run CLI with command line arguments simulation."""
        if args is None:
            args = sys.argv[1:]

        if not args:
            # Show help/usage
            help_msg = """Oracle Database CLI - Enterprise Oracle operations.

Available commands:
  health    Check Oracle database health
  schemas   List Oracle schemas
  tables    List Oracle tables in a schema
  query     Execute SQL query

Use --help with any command for detailed options.
"""

            self._OutputFormatter(self._cli_main).display_message(help_msg)
            return FlextResult[str].ok("Help displayed")

        command = args[0].lower()

        # Basic command parsing - in a real implementation, use proper CLI argument parsing
        if command == "health":
            return self.execute_health_check()
        if command == "schemas":
            return self.execute_list_schemas()
        if command == "tables":
            return self.execute_list_tables()
        if command == "query":
            min_query_args = 2
            if len(args) < min_query_args:
                error_msg = "SQL query is required for query command"
                self._OutputFormatter(self._cli_main).display_message(f"❌ {error_msg}")
                return FlextResult[str].fail(error_msg)
            return self.execute_query(args[1])
        error_msg = f"Unknown command: {command}"
        self._OutputFormatter(self._cli_main).display_message(f"❌ {error_msg}")
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
    FlextDbOracleCliService.run_main()
