"""Oracle Database CLI integration with FLEXT ecosystem.

Provides CLI functionality for Oracle database operations using flext-cli
foundation exclusively, avoiding direct Click/Rich imports per FLEXT standards.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import sys
import time
from collections.abc import Mapping, MutableSequence, Sequence
from datetime import UTC, datetime
from typing import override

import oracledb
import yaml
from flext_cli import cli
from pydantic import TypeAdapter, ValidationError

from flext_core import r, s
from flext_db_oracle import FlextDbOracleApi, FlextDbOracleSettings, c, m, t

OracleDatabaseError: type[Exception] = oracledb.DatabaseError
OracleInterfaceError: type[Exception] = oracledb.InterfaceError


class FlextDbOracleCli(s[str]):
    """Unified Oracle CLI Service using flext-cli exclusively.

    Zero Tolerance COMPLIANCE:
    - NO direct click imports - uses flext-cli foundation only
    - Unified class pattern with nested helpers
    - Explicit r error handling
    - flext-cli for ALL output formatting and user interaction
    """

    @override
    def __init__(self) -> None:
        """Initialize Oracle CLI Service."""
        super().__init__()

    class _OracleConnectionHelper:
        """Nested helper class for Oracle connection operations."""

        @staticmethod
        def create_config_from_params(
            host: str = c.DbOracle.OracleDefaults.DEFAULT_HOST,
            port: int = c.DbOracle.Connection.DEFAULT_PORT,
            service_name: str = c.DbOracle.Connection.DEFAULT_SERVICE_NAME,
            username: str = c.DbOracle.OracleDefaults.DEFAULT_USERNAME,
            password: str | None = None,
        ) -> r[FlextDbOracleSettings]:
            """Create Oracle configuration from parameters.

            Returns:
            r[FlextDbOracleSettings]: Configuration or error.

            """
            if password is None or not password.strip():
                return r[FlextDbOracleSettings].fail(
                    "Password is required for Oracle connection",
                )
            try:
                config = FlextDbOracleSettings.model_validate({
                    "host": host,
                    "port": port,
                    "service_name": service_name,
                    "username": username,
                    "password": password,
                })
                return r[FlextDbOracleSettings].ok(config)
            except (
                OracleDatabaseError,
                OracleInterfaceError,
                ConnectionError,
                ValidationError,
                ValueError,
            ) as e:
                return r[FlextDbOracleSettings].fail(
                    f"Configuration creation failed: {e}",
                )

        @staticmethod
        def validate_connection(config: FlextDbOracleSettings) -> r[bool]:
            """Validate Oracle database connection.

            Returns:
            r[bool]: True if connection valid, False otherwise.

            """
            new_api = FlextDbOracleApi(config=config)
            connect_result = new_api.connect()
            if connect_result.is_failure:
                error_text = connect_result.error or "Unknown connection error"
                return r[bool].fail(f"Connection failed: {error_text}")
            success = True
            return r[bool].ok(success)

    class _OutputFormatter:
        """Nested helper class for formatting Oracle CLI output."""

        @staticmethod
        def display_message(message: str) -> None:
            """Display message to user via cli."""
            cli.print(message)

        @staticmethod
        def format_data(
            data: m.DbOracle.OutputPayload
            | m.DbOracle.HealthCheckReport
            | Mapping[str, t.DbOracle.CliScalar]
            | t.StrSequence
            | str,
            output_format: str,
        ) -> r[str]:
            """Format any data payload using simple formatters.

            Returns:
            r[str]: Formatted data.

            """
            if output_format == "json":
                match data:
                    case m.DbOracle.OutputPayload() | m.DbOracle.HealthCheckReport():
                        return r[str].ok(data.model_dump_json(indent=2))
                    case _:
                        adapter = TypeAdapter(type(data))
                        return r[str].ok(adapter.dump_json(data, indent=2).decode())
            if output_format == "yaml":
                yaml_payload: (
                    m.DbOracle.OutputPayload
                    | m.DbOracle.HealthCheckReport
                    | Mapping[str, t.DbOracle.CliScalar]
                    | t.StrSequence
                    | str
                )
                match data:
                    case m.DbOracle.OutputPayload() | m.DbOracle.HealthCheckReport():
                        yaml_payload = data.model_dump(mode="python")
                    case _:
                        yaml_payload = data
                return r[str].ok(yaml.dump(yaml_payload, default_flow_style=False))
            return r[str].ok(str(data))

        @staticmethod
        def format_error_message(error: str) -> r[str]:
            """Format error message using simple formatting.

            Returns:
            r[str]: Formatted error message.

            """
            formatted_msg = f"❌ {error}"
            return r[str].ok(formatted_msg)

        @staticmethod
        def format_list_output(
            items: t.StrSequence | Sequence[m.DbOracle.NamedItem],
            title: str,
            output_format: str = "table",
        ) -> r[str]:
            """Format list output using simple formatters.

            Returns:
            r[str]: Formatted list output.

            """
            string_items: MutableSequence[str] = []
            for item in items:
                match item:
                    case str() as item_text:
                        string_items.append(item_text)
                    case _:
                        try:
                            parsed_item = m.DbOracle.NamedItem.model_validate(item)
                            string_items.append(parsed_item.name)
                        except ValidationError:
                            string_items.append(str(item))
            if output_format == "table":
                output_lines = [title, "=" * len(title)]
                output_lines.extend(f"  - {item}" for item in string_items)
                return r[str].ok("\n".join(output_lines))
            if output_format == "json":
                data = m.DbOracle.OutputPayload(title=title, items=string_items)
                return r[str].ok(data.model_dump_json(indent=2))
            if output_format == "yaml":
                data = m.DbOracle.OutputPayload(title=title, items=string_items)
                return r[str].ok(
                    yaml.dump(data.model_dump(mode="python"), default_flow_style=False),
                )
            output_lines = [title, *string_items]
            return r[str].ok("\n".join(output_lines))

        @staticmethod
        def format_success_message(message: str) -> r[str]:
            """Format success message using simple formatting.

            Returns:
            r[str]: Formatted success message.

            """
            formatted_msg = f"✅ {message}"
            return r[str].ok(formatted_msg)

    @classmethod
    def main(cls) -> r[str]:
        """Execute main CLI entry point using flext-cli exclusively."""
        cli_service = cls()
        return cli_service.run_cli()

    @classmethod
    def run_main(cls) -> int:
        """Module-level main entry point."""
        return 0 if cls.main().is_success else 1

    @override
    def execute(self, **_kwargs: str | float | bool) -> r[str]:
        """Execute domain service - required by s.

        Returns:
        r[str]: Service status.

        """
        self.logger.info("Oracle CLI service initialized")
        return r[str].ok("Oracle CLI service ready")

    def execute_health_check(
        self,
        host: str = c.DbOracle.OracleDefaults.DEFAULT_HOST,
        port: int = c.DbOracle.Connection.DEFAULT_PORT,
        service_name: str = c.DbOracle.Connection.DEFAULT_SERVICE_NAME,
        username: str = c.DbOracle.Connection.DEFAULT_USERNAME,
        password: str | None = None,
        timeout: int = c.DbOracle.Connection.DEFAULT_TIMEOUT,
    ) -> r[m.DbOracle.HealthCheckReport]:
        """Execute complete health check for Oracle database connection.

        Args:
        host: Oracle database hostname
        port: Oracle database port
        service_name: Oracle service name
        username: Oracle username
        password: Oracle password (required)
        timeout: Connection timeout in seconds

        Returns:
        r[m.DbOracle.HealthCheckReport]: Health check results with status and timing

        """
        start_time = time.time()
        try:
            config = FlextDbOracleSettings.model_validate({
                "host": host,
                "port": port,
                "service_name": service_name,
                "username": username,
                "password": password,
                "timeout": timeout,
            })
            api = FlextDbOracleApi(config=config)
            health_result = api.get_health_status()
            if health_result.is_failure:
                return r[m.DbOracle.HealthCheckReport].fail(
                    f"Health check failed: {health_result.error}",
                )
            elapsed_time = time.time() - start_time
            health_data = health_result.value
            result = m.DbOracle.HealthCheckReport.model_validate({
                "status": "healthy",
                "host": host,
                "port": port,
                "service_name": service_name,
                "response_time_ms": round(elapsed_time * 1000, 2),
                "details": health_data.model_dump(mode="json"),
                "timestamp": datetime.now(UTC).isoformat(),
            })
            return r[m.DbOracle.HealthCheckReport].ok(result)
        except (OracleDatabaseError, OracleInterfaceError, ConnectionError) as e:
            elapsed_time = time.time() - start_time
            error_result = m.DbOracle.HealthCheckReport(
                status="unhealthy",
                host=host,
                port=port,
                service_name=service_name,
                response_time_ms=round(elapsed_time * 1000, 2),
                details={},
                error=str(e),
                timestamp=datetime.now(UTC).isoformat(),
            )
            return r[m.DbOracle.HealthCheckReport].ok(error_result)

    def execute_list_schemas(
        self,
        host: str = "localhost",
        port: int = c.DbOracle.Connection.DEFAULT_PORT,
        service_name: str = c.DbOracle.Connection.DEFAULT_SERVICE_NAME,
        username: str = c.DbOracle.Connection.DEFAULT_USERNAME,
        password: str | None = None,
        output_format: str = "table",
    ) -> r[str]:
        """Execute Oracle schemas listing.

        Returns:
        r[str]: Schemas list or error.

        """
        formatter = self._OutputFormatter
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
                formatter.display_message(error_msg.value)
            return r[str].fail(error_text)
        config = config_result.value
        validation_result = self._OracleConnectionHelper.validate_connection(config)
        if validation_result.is_failure:
            error_text = validation_result.error or "Unknown validation error"
            error_msg = formatter.format_error_message(error_text)
            if error_msg.is_success:
                formatter.display_message(error_msg.value)
            return r[str].fail(error_text)
        api = FlextDbOracleApi(config=config)
        schemas_result = api.get_schemas()
        if schemas_result.is_failure:
            error_text = schemas_result.error or "Unknown schemas error"
            error_msg = formatter.format_error_message(
                f"Failed to get schemas: {error_text}",
            )
            if error_msg.is_success:
                formatter.display_message(error_msg.value)
            return r[str].fail(error_text)
        schemas = schemas_result.value
        formatted_result = formatter.format_list_output(
            schemas,
            "Available Oracle Schemas",
            output_format,
        )
        if formatted_result.is_success:
            formatter.display_message(formatted_result.value)
        return r[str].ok(f"Listed {len(schemas)} schemas successfully")

    def execute_list_tables(
        self,
        schema: str = "SYSTEM",
        host: str = "localhost",
        port: int = c.DbOracle.Connection.DEFAULT_PORT,
        service_name: str = c.DbOracle.Connection.DEFAULT_SERVICE_NAME,
        username: str = c.DbOracle.Connection.DEFAULT_USERNAME,
        password: str | None = None,
        output_format: str = "table",
    ) -> r[str]:
        """Execute Oracle tables listing for a schema.

        Returns:
        r[str]: Tables list or error.

        """
        formatter = self._OutputFormatter
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
                formatter.display_message(error_msg.value)
            return r[str].fail(error_text)
        config = config_result.value
        validation_result = self._OracleConnectionHelper.validate_connection(config)
        if validation_result.is_failure:
            error_text = validation_result.error or "Unknown validation error"
            error_msg = formatter.format_error_message(error_text)
            if error_msg.is_success:
                formatter.display_message(error_msg.value)
            return r[str].fail(error_text)
        api = FlextDbOracleApi(config=config)
        tables_result = api.get_tables(schema)
        if tables_result.is_failure:
            error_text = tables_result.error or "Unknown tables error"
            error_msg = formatter.format_error_message(
                f"Failed to get tables: {error_text}",
            )
            if error_msg.is_success:
                formatter.display_message(error_msg.value)
            return r[str].fail(error_text)
        tables = tables_result.value
        formatted_result = formatter.format_list_output(
            tables,
            f"Tables in schema {schema}",
            output_format,
        )
        if formatted_result.is_success:
            formatter.display_message(formatted_result.value)
        return r[str].ok(f"Listed {len(tables)} tables in schema {schema} successfully")

    def execute_query(
        self,
        sql: str,
        host: str = "localhost",
        port: int = c.DbOracle.Connection.DEFAULT_PORT,
        service_name: str = c.DbOracle.Connection.DEFAULT_SERVICE_NAME,
        username: str = c.DbOracle.Connection.DEFAULT_USERNAME,
        password: str | None = None,
        output_format: str = "table",
    ) -> r[str]:
        """Execute SQL query against Oracle database.

        Returns:
        r[str]: Query results or error.

        """
        formatter = self._OutputFormatter
        if not sql.strip():
            return self._handle_error_and_fail(
                formatter,
                "SQL query cannot be empty",
                "SQL query cannot be empty",
            )
        config_result = self._OracleConnectionHelper.create_config_from_params(
            host,
            port,
            service_name,
            username,
            password,
        )
        if config_result.is_failure:
            error_text = config_result.error or "Unknown configuration error"
            return self._handle_error_and_fail(
                formatter,
                error_text,
                f"Configuration failed: {error_text}",
            )
        config = config_result.value
        validation_result = self._OracleConnectionHelper.validate_connection(config)
        if validation_result.is_failure:
            error_text = validation_result.error or "Unknown validation error"
            return self._handle_error_and_fail(formatter, error_text, error_text)
        api = FlextDbOracleApi(config=config)
        query_result = api.query(sql)
        if query_result.is_failure:
            error_text = query_result.error or "Unknown query error"
            return self._handle_error_and_fail(
                formatter,
                error_text,
                f"Query failed: {error_text}",
            )
        result = query_result.value
        row_count = len(result)
        success_msg = formatter.format_success_message(
            f"Query executed successfully. Rows: {row_count}",
        )
        if success_msg.is_success:
            formatter.display_message(success_msg.value)
        formatted_result = formatter.format_data(
            {"rows": "row_count", "result": "result"},
            output_format,
        )
        if formatted_result.is_success:
            return r[str].ok(formatted_result.value)
        return r[str].ok(f"Query executed successfully with {row_count} rows")

    def run_cli(self, args: t.StrSequence | None = None) -> r[str]:
        """Run CLI with command line arguments simulation.

        Returns:
        r[str]: CLI execution result.

        """
        if args is None:
            args = sys.argv[1:]
        if not args:
            help_msg = "Oracle Database CLI - Enterprise Oracle operations.\n\nAvailable commands:\n health Check Oracle database health\n schemas List Oracle schemas\n tables List Oracle tables in a schema\n query Execute SQL query\n\nUse --help with any command for detailed options.\n"
            self._OutputFormatter.display_message(help_msg)
            return r[str].ok("Help displayed")
        command = args[0].lower()
        if command == "health":
            health_result = self.execute_health_check()
            if health_result.is_success:
                return r[str].ok("Health check completed successfully")
            return r[str].fail(health_result.error or "Health check failed")
        if command == "schemas":
            return self.execute_list_schemas()
        if command == "tables":
            return self.execute_list_tables()
        if command == "query":
            min_query_args = 2
            if len(args) < min_query_args:
                error_msg = "SQL query is required for query command"
                self._OutputFormatter.display_message(f"{error_msg}")
                return r[str].fail(error_msg)
            return self.execute_query(args[1])
        error_msg = f"Unknown command: {command}"
        self._OutputFormatter.display_message(f"{error_msg}")
        return r[str].fail(error_msg)

    def _handle_error_and_fail(
        self,
        formatter: type[_OutputFormatter],
        error_message: str,
        display_message: str | None = None,
    ) -> r[str]:
        """Handle error by displaying message and returning failure result."""
        if display_message:
            error_msg = formatter.format_error_message(display_message)
            if error_msg.is_success:
                formatter.display_message(error_msg.value)
        return r[str].fail(error_message)


if __name__ == "__main__":
    raise SystemExit(FlextDbOracleCli.run_main())
