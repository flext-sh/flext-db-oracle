"""FLEXT DB Oracle CLI using flext-cli comprehensive patterns.

Single unified CLI client following FLEXT standards with proper flext-cli usage,
no direct rich/click imports, and consolidated class structure.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import cast

import click
from flext_cli import (
    FlextCliFormatters,
    FlextCliInteractions,
    setup_cli,
)
from flext_core import (
    FlextContainer,
    FlextLogger,
    FlextResult,
)
from pydantic import SecretStr

from flext_db_oracle.api import FlextDbOracleApi
from flext_db_oracle.constants import FlextDbOracleConstants
from flext_db_oracle.models import FlextDbOracleModels


class FlextDbOracleClient:
    """Unified Oracle database CLI client with proper flext-cli integration.

    Single class containing all CLI functionality without facade patterns,
    direct rich imports, or compatibility layers.
    """

    def __init__(self, *, debug: bool = False) -> None:
        """Initialize Oracle CLI client with flext-cli components."""
        # Use proper flext-cli components instead of direct rich
        self.formatter = FlextCliFormatters()
        self.interactions = FlextCliInteractions()
        self.logger = FlextLogger(__name__)
        self.container = FlextContainer.get_global()

        # Application state
        self.debug = debug
        self.current_connection: FlextDbOracleApi | None = None
        self.user_preferences: dict[str, object] = {
            "default_output_format": "table",
            "auto_confirm_operations": False,
            "show_execution_time": True,
            "connection_timeout": 30,  # Default connection timeout
            "query_limit": 1000,  # Default query fetch size
        }

    def initialize(self) -> FlextResult[None]:
        """Initialize CLI client with setup and validation."""
        try:
            # Print welcome message using flext-cli
            self.interactions.print_info("FLEXT Oracle Database CLI")
            self.interactions.print_status(
                "Enterprise Oracle operations with professional CLI experience..."
            )

            setup_result = setup_cli()
            if not setup_result.success:
                return FlextResult[None].fail(f"CLI setup failed: {setup_result.error}")

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
                ssl_server_cert_dn=None,  # Explicitly set optional field
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
        """Execute SQL query on connected Oracle database."""
        if not self.current_connection:
            return FlextResult[object].fail("No active Oracle connection")

        try:
            result = self.current_connection.query(query)
            if not result.success:
                return FlextResult[object].fail(
                    f"Query execution failed: {result.error}"
                )

            # Format output based on user preferences
            if self.user_preferences["default_output_format"] == "table":
                table_result = self.formatter.format_table(
                    data=result.value, title="Query Results"
                )
                if table_result.success:
                    self.interactions.print_info(str(table_result.value))
            else:
                json_result = self.formatter.format_json(result.value)
                if json_result.success:
                    self.interactions.print_info(str(json_result.value))

            return FlextResult[object].ok(result.value)

        except Exception as e:
            self.logger.exception("Query execution error")
            return FlextResult[object].fail(f"Query execution error: {e}")

    def list_schemas(self) -> FlextResult[list[str]]:
        """List available schemas in connected Oracle database."""
        if not self.current_connection:
            return FlextResult[list[str]].fail("No active Oracle connection")

        try:
            schemas_result = self.current_connection.get_schemas()
            if not schemas_result.success:
                return FlextResult[list[str]].fail(
                    f"Failed to retrieve schemas: {schemas_result.error}"
                )

            schemas = schemas_result.value
            table_result = self.formatter.format_table(
                data=[{"schema": schema} for schema in schemas],
                title=f"Database Schemas ({len(schemas)} found)",
            )
            if table_result.success:
                self.interactions.print_info(str(table_result.value))

            return FlextResult[list[str]].ok(schemas)

        except Exception as e:
            self.logger.exception("Schema listing error")
            return FlextResult[list[str]].fail(f"Schema listing error: {e}")

    def list_tables(self, schema: str | None = None) -> FlextResult[list[str]]:
        """List tables in specified schema or current schema."""
        if not self.current_connection:
            return FlextResult[list[str]].fail("No active Oracle connection")

        try:
            tables_result = self.current_connection.get_tables(schema)
            if not tables_result.success:
                return FlextResult[list[str]].fail(
                    f"Failed to retrieve tables: {tables_result.error}"
                )

            tables = tables_result.value
            title = f"Tables in {schema}" if schema else "Tables"
            table_result = self.formatter.format_table(
                data=[{"table": table} for table in tables],
                title=f"{title} ({len(tables)} found)",
            )
            if table_result.success:
                self.interactions.print_info(str(table_result.value))

            return FlextResult[list[str]].ok(tables)

        except Exception as e:
            self.logger.exception("Table listing error")
            return FlextResult[list[str]].fail(f"Table listing error: {e}")

    def health_check(self) -> FlextResult[dict[str, object]]:
        """Perform Oracle database health check."""
        if not self.current_connection:
            return FlextResult[dict[str, object]].fail("No active Oracle connection")

        try:
            self.interactions.print_info("Performing health check...")

            # Execute test query
            test_result = self.current_connection.query(
                FlextDbOracleConstants.Query.TEST_QUERY
            )

            health_data = {
                "status": "healthy" if test_result.success else "unhealthy",
                "test_query_result": test_result.success,
                "timestamp": datetime.now(UTC).isoformat(),
                "connection_active": self.current_connection.is_connected,
            }

            json_result = self.formatter.format_json(health_data)
            if json_result.success:
                self.interactions.print_info(json_result.value)
            # Cast to ensure type compatibility
            typed_health_data = cast("dict[str, object]", health_data)
            return FlextResult[dict[str, object]].ok(typed_health_data)

        except Exception as e:
            self.logger.exception("Health check error")
            return FlextResult[dict[str, object]].fail(f"Health check error: {e}")

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
        """Interactive connection configuration wizard using flext-cli."""
        try:
            self.interactions.print_info("Oracle Connection Wizard")
            self.interactions.print_status("Configure your Oracle database connection")

            # Use flext-cli interactions instead of direct rich Prompt
            host_result = self.interactions.prompt(
                "Oracle database host", default="localhost"
            )
            if not host_result.success:
                return FlextResult[FlextDbOracleModels.OracleConfig].fail(
                    f"Host input failed: {host_result.error}"
                )
            host = host_result.value

            port_result = self.interactions.prompt(
                "Oracle database port", default="1521"
            )
            if not port_result.success:
                return FlextResult[FlextDbOracleModels.OracleConfig].fail(
                    f"Port input failed: {port_result.error}"
                )
            port = int(port_result.value)

            service_result = self.interactions.prompt(
                "Oracle service name", default="XE"
            )
            if not service_result.success:
                return FlextResult[FlextDbOracleModels.OracleConfig].fail(
                    f"Service input failed: {service_result.error}"
                )
            service_name = service_result.value

            username_result = self.interactions.prompt("Oracle username")
            if not username_result.success:
                return FlextResult[FlextDbOracleModels.OracleConfig].fail(
                    f"Username input failed: {username_result.error}"
                )
            username = username_result.value

            password_result = self.interactions.prompt("Oracle password")
            if not password_result.success:
                return FlextResult[FlextDbOracleModels.OracleConfig].fail(
                    f"Password input failed: {password_result.error}"
                )
            password = password_result.value

            # Use flext-cli confirmation instead of direct rich Confirm
            confirm_result = self.interactions.confirm(
                "Test connection with these settings?", default=True
            )
            if not confirm_result.success:
                return FlextResult[FlextDbOracleModels.OracleConfig].fail(
                    f"Confirmation failed: {confirm_result.error}"
                )
            test_connection = confirm_result.value

            config = FlextDbOracleModels.OracleConfig(
                host=host,
                port=port,
                service_name=service_name,
                username=username,
                password=SecretStr(password),
                ssl_server_cert_dn=None,  # Explicitly set optional field
            )

            # Display connection summary
            table_result = self.formatter.format_table(
                data=[
                    {"setting": "Host", "value": host},
                    {"setting": "Port", "value": str(port)},
                    {"setting": "Service", "value": service_name},
                    {"setting": "Username", "value": username},
                ],
                title="Oracle Connection Summary",
            )
            if table_result.success:
                self.interactions.print_info(str(table_result.value))

            if test_connection:
                test_result = self.connect_to_oracle(
                    host, port, service_name, username, password
                )
                if test_result.success:
                    self.interactions.print_success("Connection test successful!")
                else:
                    self.interactions.print_error(
                        f"Connection test failed: {test_result.error}"
                    )

            return FlextResult[FlextDbOracleModels.OracleConfig].ok(config)

        except Exception as e:
            self.logger.exception("Connection wizard error")
            return FlextResult[FlextDbOracleModels.OracleConfig].fail(
                f"Connection wizard error: {e}"
            )


# Global client instance
_client: FlextDbOracleClient | None = None


def get_client() -> FlextDbOracleClient:
    """Get or create global Oracle CLI client instance."""
    # Use module-level variable without global statement
    if globals().get("_client") is None:
        client = FlextDbOracleClient()
        client.initialize()
        globals()["_client"] = client
    return cast("FlextDbOracleClient", globals()["_client"])


# CLI Command Group
@click.group(name="oracle")
@click.option("--debug", is_flag=True, help="Enable debug mode")
@click.pass_context
def oracle_cli(ctx: click.Context, *, debug: bool) -> None:
    """FLEXT Oracle Database CLI - Enterprise Oracle operations."""
    ctx.ensure_object(dict)
    ctx.obj["debug"] = debug
    client = get_client()
    if debug:
        client.debug = True


@oracle_cli.command("connect")
@click.option("--host", default="localhost", help="Oracle database host")
@click.option("--port", default=1521, help="Oracle database port")
@click.option("--service-name", default="XE", help="Oracle service name")
@click.option("--username", prompt=True, help="Oracle username")
@click.option("--password", prompt=True, hide_input=True, help="Oracle password")
def connect_command(
    host: str, port: int, service_name: str, username: str, password: str
) -> None:
    """Connect to Oracle database."""
    client = get_client()
    result = client.connect_to_oracle(host, port, service_name, username, password)
    if not result.success:
        client.interactions.print_error(f"Connection failed: {result.error}")
        raise click.ClickException(result.error or "Connection failed")


@oracle_cli.command("query")
@click.argument("sql")
def query_command(sql: str) -> None:
    """Execute SQL query."""
    client = get_client()
    result = client.execute_query(sql)
    if not result.success:
        client.interactions.print_error(f"Query failed: {result.error}")
        raise click.ClickException(result.error or "Query failed")


@oracle_cli.command("schemas")
def schemas_command() -> None:
    """List database schemas."""
    client = get_client()
    result = client.list_schemas()
    if not result.success:
        client.interactions.print_error(f"Failed to list schemas: {result.error}")
        raise click.ClickException(result.error or "Failed to list schemas")


@oracle_cli.command("tables")
@click.option("--schema", help="Schema name")
def tables_command(schema: str | None) -> None:
    """List tables in schema."""
    client = get_client()
    result = client.list_tables(schema)
    if not result.success:
        client.interactions.print_error(f"Failed to list tables: {result.error}")
        raise click.ClickException(result.error or "Failed to list tables")


@oracle_cli.command("health")
def health_command() -> None:
    """Check Oracle database health."""
    client = get_client()
    result = client.health_check()
    if not result.success:
        client.interactions.print_error(f"Health check failed: {result.error}")
        raise click.ClickException(result.error or "Health check failed")


@oracle_cli.command("wizard")
def wizard_command() -> None:
    """Interactive connection wizard."""
    client = get_client()
    result = client.connection_wizard()
    if not result.success:
        client.interactions.print_error(f"Wizard failed: {result.error}")
        raise click.ClickException(result.error or "Wizard failed")


# Export the main CLI command
__all__: list[str] = [
    "FlextDbOracleClient",
    "get_client",
    "oracle_cli",
]
