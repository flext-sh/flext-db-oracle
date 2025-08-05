"""FLEXT DB Oracle Command Line Interface.

This module provides a comprehensive command-line interface for Oracle database
operations using FLEXT CLI patterns and Clean Architecture principles. It implements
enterprise-grade CLI commands with rich formatting, comprehensive error handling,
and seamless integration with the FLEXT ecosystem.

Key Components:
    - Oracle CLI Group: Main command group with connection, query, and management commands
    - Connection Commands: connect, connect-env for database connectivity testing
    - Query Commands: query, optimize for SQL execution and optimization
    - Schema Commands: schemas, tables for database structure exploration
    - Plugin Commands: plugins for extensibility management
    - Health Commands: health for database status monitoring

Architecture:
    This module implements the Presentation layer's CLI concern following Clean
    Architecture principles. It uses the Strategy pattern for output formatting,
    Template Method pattern for command execution, and Single Responsibility
    principle for command processors and result handlers.

Example:
    Basic Oracle CLI usage:

    >>> # Connect to Oracle database
    >>> oracle connect --host oracle-server --port 1521 --service-name PROD --username app_user
    >>>
    >>> # Execute query with environment configuration
    >>> oracle connect-env && oracle query --sql "SELECT COUNT(*) FROM employees"
    >>>
    >>> # List schemas and tables
    >>> oracle schemas && oracle tables --schema HR
    >>>
    >>> # Register and manage plugins
    >>> oracle plugins

Integration:
    - Built on flext-cli foundation for consistent CLI patterns
    - Integrates with Rich library for enhanced terminal formatting
    - Supports multiple output formats (table, json, yaml, csv)
    - Compatible with FLEXT ecosystem configuration and observability
    - Provides comprehensive error handling and user feedback

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import TYPE_CHECKING, Literal, Protocol, cast

import click
from flext_cli import get_config
from flext_cli.core.formatters import format_output
from pydantic import SecretStr
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

if TYPE_CHECKING:
    from flext_plugin import FlextPlugin

# Direct imports to avoid circular dependency - DRY refactoring
from flext_db_oracle.api import FlextDbOracleApi
from flext_db_oracle.config import FlextDbOracleConfig
from flext_db_oracle.plugins import register_all_oracle_plugins

from .constants import ORACLE_DEFAULT_PORT

console = Console()


def _print_error(message: str) -> None:
    """Print error message with red formatting - DRY pattern for CLI errors."""
    console.print(f"[red]{message}[/red]")


def _print_error_exception(exception: Exception) -> None:
    """Print exception as error - DRY pattern for exception handling."""
    console.print(f"[red]Error: {exception}[/red]")


def _print_no_data_error(operation: str) -> None:
    """Print no data error - DRY pattern for data validation."""
    console.print(f"[red]{operation} returned no data[/red]")


def _handle_no_data_error_with_cli_exception(operation: str) -> None:
    """Handle no data error with print and CLI exception - DRY pattern for no data scenarios."""
    _print_no_data_error(operation)
    _raise_cli_error(f"{operation} returned no data")


def _handle_operation_failure_with_cli_exception(operation: str, error: str) -> None:
    """Handle operation failure with print and CLI exception - DRY pattern for operation failures."""
    _print_error(f"{operation} failed: {error}")
    _raise_cli_error(f"{operation} failed: {error}")


class ConfigProtocol(Protocol):
    """Protocol for CLI config objects."""

    output_format: str


class PluginProtocol(Protocol):
    """Protocol for plugin objects."""

    name: str
    version: str


@dataclass
class ConnectionParams:
    """Oracle connection parameters - DRY pattern for connection data."""

    host: str
    port: int
    service_name: str
    username: str
    password: str


def _raise_cli_error(message: str) -> None:
    """Raise ClickException with message - DRY error handling pattern."""
    raise click.ClickException(message)


def _raise_cli_exception_from_exception(exception: Exception) -> None:
    """Raise ClickException from exception - DRY pattern for exception chaining."""
    raise click.ClickException(str(exception)) from exception


def _safe_get_test_data(
    test_data: dict[str, object] | None,
    key: str,
    default: object = None,
) -> object:
    """Safely get value from test_data dict - DRY null safety pattern."""
    return test_data.get(key, default) if test_data is not None else default


def _safe_get_query_data_attr(
    query_data: object | None,
    attr: str,
    default: object = None,
) -> object:
    """Safely get attribute from query_data - DRY null safety pattern."""
    return getattr(query_data, attr, default) if query_data is not None else default


def _safe_iterate_list(data_list: list[str] | None) -> list[str]:
    """Safely iterate over list - DRY null safety pattern."""
    return data_list if data_list is not None else []


def _safe_iterate_dict(data_dict: dict[str, str] | None) -> dict[str, str]:
    """Safely iterate over dict - DRY null safety pattern."""
    return data_dict if data_dict is not None else {}


def _safe_get_list_length(obj: object) -> int:
    """Safely get length of list-like object - DRY pattern for type-safe length checking."""
    if obj is None:
        return 0
    if isinstance(obj, list):
        return len(obj)
    if hasattr(obj, "__len__"):
        try:
            return len(obj)
        except (TypeError, AttributeError):
            return 0
    return 0


def _extract_table_info(table_info: object, schema: str | None) -> tuple[str, str]:
    """Extract table name and schema from table_info object - eliminates deeply nested control flow."""
    # Guard clause pattern - early return for dict-like objects
    if hasattr(table_info, "get"):
        name = table_info.get("name", "") or str(table_info)
        schema_name = table_info.get("schema", schema or "")
        return name, schema_name

    # Simple object case
    return str(table_info), schema or ""


@click.group()
@click.option(
    "--profile",
    default="default",
    help="Configuration profile to use",
)
@click.option(
    "--output",
    type=click.Choice(["table", "json", "yaml", "csv"]),
    default="table",
    help="Output format",
)
@click.option(
    "--debug/--no-debug",
    default=False,
    help="Enable debug mode",
)
@click.pass_context
def oracle(
    ctx: click.Context,
    profile: str,
    output: str,
    *,
    debug: bool,
) -> None:
    """Oracle Database CLI commands."""
    # Setup CLI context
    config = get_config()
    config.profile = profile
    config.output_format = cast("Literal['table', 'json', 'yaml', 'csv', 'plain']", output)
    config.debug = debug

    ctx.ensure_object(dict)
    ctx.obj["config"] = config
    ctx.obj["console"] = console
    ctx.obj["debug"] = debug


@oracle.command()
@click.option(
    "--host",
    required=True,
    help="Oracle database host",
)
@click.option(
    "--port",
    type=int,
    default=ORACLE_DEFAULT_PORT,
    help="Oracle database port",
)
@click.option(
    "--service-name",
    required=True,
    help="Oracle service name",
)
@click.option(
    "--username",
    required=True,
    help="Database username",
)
@click.option(
    "--password",
    prompt=True,
    hide_input=True,
    help="Database password",
)
@click.pass_context
def connect(
    ctx: click.Context,
    /,
    **connection_args: str | int,
) -> None:  # necessary CLI args - / makes ctx positional-only
    """Connect to Oracle database and test connection."""
    # Extract and validate connection args - refatoração DRY real
    params = ConnectionParams(
        host=str(connection_args["host"]),
        port=int(connection_args["port"]),
        service_name=str(connection_args["service_name"]),
        username=str(connection_args["username"]),
        password=str(connection_args["password"]),
    )
    _execute_connection_test(ctx, params)


def _execute_connection_test(ctx: click.Context, params: ConnectionParams) -> None:
    """Execute connection test with parameters - DRY pattern."""
    # Strategy Pattern: Create connection test execution strategy
    executor = _ConnectionTestExecutor(ctx, params)
    executor.execute()


class _ConnectionTestExecutor:
    """Connection test executor using Strategy + Template Method patterns - Single Responsibility."""

    def __init__(self, ctx: click.Context, params: ConnectionParams) -> None:
        """Initialize connection test executor."""
        self.ctx = ctx
        self.params = params
        self.config = ctx.obj["config"]
        self.debug = ctx.obj["debug"]

    def execute(self) -> None:
        """Template Method: Execute connection test with structured phases."""
        try:
            # Phase 1: Setup
            api = self._setup_connection()

            # Phase 2: Connect
            self._establish_connection(api)

            # Phase 3: Test
            test_result = self._perform_connection_test(api)

            # Phase 4: Handle Result
            self._handle_test_result(test_result)

        except (
            click.ClickException,
            ValueError,
            TypeError,
            AttributeError,
            ConnectionError,
            OSError,
        ) as e:
            self._handle_exception(e)

    def _setup_connection(self) -> FlextDbOracleApi:
        """Set up connection configuration - Single Responsibility."""
        oracle_config = self._create_oracle_config()
        return FlextDbOracleApi(oracle_config, context_name="cli")

    def _create_oracle_config(self) -> FlextDbOracleConfig:
        """Create Oracle configuration with defaults - Single Responsibility."""
        return FlextDbOracleConfig(
            host=self.params.host,
            port=self.params.port,
            service_name=self.params.service_name,
            username=self.params.username,
            password=SecretStr(self.params.password),
            sid=None,  # Usando service_name
            pool_min=1,
            pool_max=10,
            pool_increment=1,
            timeout=30,
            encoding="UTF-8",
            ssl_enabled=False,
            ssl_cert_path=None,
            ssl_key_path=None,
            protocol="tcp",
            ssl_server_dn_match=True,
            ssl_server_cert_dn=None,
            autocommit=False,
        )

    def _establish_connection(self, api: FlextDbOracleApi) -> None:
        """Establish database connection - Single Responsibility."""
        if self.debug:
            console.print(
                f"[blue]Connecting to {self.params.host}:{self.params.port}/{self.params.service_name}...[/blue]",
            )
        api.connect()

    def _perform_connection_test(self, api: FlextDbOracleApi) -> object:
        """Perform connection test with observability - Single Responsibility."""
        return api.test_connection_with_observability()

    def _handle_test_result(self, test_result: object) -> None:
        """Handle test result based on success/failure - Single Responsibility."""
        if hasattr(test_result, "success") and test_result.success:
            self._handle_successful_test(test_result)
        else:
            self._handle_failed_test(test_result)

    def _handle_successful_test(self, test_result: object) -> None:
        """Handle successful connection test - Single Responsibility."""
        test_data = getattr(test_result, "data", None)

        if test_data is None:
            _handle_no_data_error_with_cli_exception("Connection test")

        self._display_success_panel(test_data)
        self._display_health_data(test_data)

    def _display_success_panel(self, test_data: object) -> None:
        """Display connection success panel - Single Responsibility."""
        # Type-safe conversion for _safe_get_test_data
        test_data_dict = test_data if isinstance(test_data, dict) else None

        info_panel = Panel(
            f"""✅ **Connection Successful**

Host: {self.params.host}
Port: {self.params.port}
Service: {self.params.service_name}
Status: {_safe_get_test_data(test_data_dict, "status", "unknown")}
Test Duration: {_safe_get_test_data(test_data_dict, "test_duration_ms", 0)}ms""",
            title="Oracle Connection",
            border_style="green",
        )
        console.print(info_panel)

    def _display_health_data(self, test_data: object) -> None:
        """Display health data if available - Single Responsibility."""
        # Type-safe conversion for _safe_get_test_data
        test_data_dict = test_data if isinstance(test_data, dict) else None

        health_data = _safe_get_test_data(test_data_dict, "health", {})
        if not (health_data and isinstance(health_data, dict)):
            return

        output_data = self._prepare_health_output_data(test_data_dict, health_data)

        if self.config.output_format == "table":
            self._display_health_table(output_data)
        else:
            format_output(output_data, self.config.output_format, console)

    def _prepare_health_output_data(
        self,
        test_data: dict[str, object] | None,
        health_data: dict[str, object],
    ) -> dict[str, object]:
        """Prepare health data for output - Single Responsibility."""
        return {
            "connection_status": _safe_get_test_data(test_data, "status"),
            "test_duration_ms": _safe_get_test_data(test_data, "test_duration_ms"),
            "health_status": health_data.get("status"),
            "health_message": health_data.get("message"),
            "metrics": health_data.get("metrics", {}),
        }

    def _display_health_table(self, output_data: dict[str, object]) -> None:
        """Display health data as table - Single Responsibility."""
        table = Table(title="Connection Details")
        table.add_column("Property", style="cyan")
        table.add_column("Value", style="green")

        for key, value in output_data.items():
            formatted_value = (
                json.dumps(value, indent=2) if isinstance(value, dict) else str(value)
            )
            table.add_row(key.replace("_", " ").title(), formatted_value)

        console.print(table)

    def _handle_failed_test(self, test_result: object) -> None:
        """Handle failed connection test - Single Responsibility."""
        error = getattr(test_result, "error", "Unknown error")
        _handle_operation_failure_with_cli_exception("Connection", error)

    def _handle_exception(self, exception: Exception) -> None:
        """Handle exceptions during connection test - Single Responsibility."""
        _print_error_exception(exception)
        _raise_cli_exception_from_exception(exception)


@oracle.command()
@click.option(
    "--env-prefix",
    default="FLEXT_TARGET_ORACLE_",
    help="Environment variable prefix",
)
@click.pass_context
def connect_env(ctx: click.Context, env_prefix: str) -> None:
    """Connect to Oracle using environment variables."""
    config = ctx.obj["config"]
    debug = ctx.obj["debug"]

    try:
        if debug:
            console.print(
                f"[blue]Loading configuration from environment (prefix: {env_prefix})...[/blue]",
            )

        # Create API from environment
        api = FlextDbOracleApi.from_env(env_prefix=env_prefix, context_name="cli")

        # Test connection
        test_result = api.test_connection_with_observability()

        if test_result.success:
            test_data = test_result.data

            # Null check para test_data - refatoração DRY real
            if test_data is None:
                _handle_no_data_error_with_cli_exception("Connection test")

            console.print(
                Panel(
                    f"""✅ **Connection Successful (from environment)**

Status: {_safe_get_test_data(test_data, "status", "unknown")}
Test Duration: {_safe_get_test_data(test_data, "test_duration_ms", 0)}ms""",
                    title="Oracle Connection",
                    border_style="green",
                ),
            )

            # Output health data
            health_data = _safe_get_test_data(test_data, "health", {})
            if health_data and config.output_format != "table":
                format_output(health_data, config.output_format, console)
        else:
            _handle_operation_failure_with_cli_exception(
                "Connection",
                test_result.error or "Unknown connection error",
            )

    except (
        OSError,
        ValueError,
        AttributeError,
        RuntimeError,
        TypeError,
        KeyError,
    ) as e:
        _print_error_exception(e)
        _raise_cli_exception_from_exception(e)


class QueryResultProcessor:
    """refactoring: Single Responsibility for query result processing."""

    def __init__(self, config: ConfigProtocol, console: Console) -> None:
        """Initialize result processor."""
        self.config = config
        self.console = console

    def process_success(
        self,
        query_data: object,
        results: list[object],
        limit: int | None,
    ) -> None:
        """Process successful query results."""
        # Apply limit if specified
        limited_results = self._apply_limit(results, limit)

        # Display summary panel
        self._display_summary_panel(query_data)

        # Display results based on format
        if self.config.output_format == "table" and limited_results:
            self._display_as_table(query_data, limited_results)
        else:
            self._display_as_structured_output(query_data, limited_results)

    def _apply_limit(self, results: list[object], limit: int | None) -> list[object]:
        """Apply row limit to results."""
        if limit and isinstance(results, list) and len(results) > limit:
            self.console.print(f"[yellow]Results limited to {limit} rows[/yellow]")
            return results[:limit]
        return results

    def _display_summary_panel(self, query_data: object) -> None:
        """Display query execution summary."""
        execution_time = _safe_get_query_data_attr(query_data, "execution_time_ms", 0)
        row_count = _safe_get_query_data_attr(query_data, "row_count", 0)
        columns = _safe_get_query_data_attr(query_data, "columns", [])

        self.console.print(
            Panel(
                f"""✅ **Query Executed Successfully**

Execution Time: {execution_time:.2f}ms
Rows Returned: {row_count}
Columns: {_safe_get_list_length(columns)}""",
                title="Query Results",
                border_style="green",
            ),
        )

    def _display_as_table(
        self,
        query_data: object,
        results: list[object],
    ) -> None:
        """Display results as rich table."""
        table: Table = Table(title=f"Query Results ({len(results)} rows)")

        # Add columns
        columns = _safe_get_query_data_attr(query_data, "columns", [])
        if columns and isinstance(columns, list):
            for col in columns:
                table.add_column(str(col), style="cyan")

        # Add rows
        for row in results:
            # Ensure row is iterable (tuple, list, etc.)
            if hasattr(row, "__iter__") and not isinstance(row, (str, bytes)):
                table.add_row(
                    *[str(cell) if cell is not None else "NULL" for cell in row],
                )
            else:
                # Single value row
                table.add_row(str(row) if row is not None else "NULL")

        self.console.print(table)

    def _display_as_structured_output(
        self,
        query_data: object,
        results: list[object],
    ) -> None:
        """Display results as structured output."""
        output_data = {
            "execution_time_ms": _safe_get_query_data_attr(
                query_data,
                "execution_time_ms",
                0,
            ),
            "row_count": _safe_get_query_data_attr(query_data, "row_count", 0),
            "columns": _safe_get_query_data_attr(query_data, "columns", []),
            "rows": results,
        }
        format_output(output_data, self.config.output_format, self.console)


@oracle.command()
@click.option(
    "--sql",
    required=True,
    help="SQL query to execute",
)
@click.option(
    "--limit",
    type=int,
    help="Limit number of results",
)
@click.pass_context
def query(ctx: click.Context, sql: str, limit: int | None) -> None:
    """Execute SQL query against Oracle database - SOLID refactored."""
    config = ctx.obj["config"]
    debug = ctx.obj["debug"]

    try:
        # Create API from environment
        api = FlextDbOracleApi.from_env(context_name="cli")

        if debug:
            console.print(f"[blue]Executing query: {sql[:100]}...[/blue]")

        with api:
            # Execute query with timing
            query_result = api.query_with_timing(sql)

            if query_result.success:
                query_data = query_result.data

                # Null check for query_data
                if query_data is None:
                    _handle_no_data_error_with_cli_exception("Query execution")

                results: list[object] = cast(
                    "list[object]",
                    _safe_get_query_data_attr(query_data, "rows", []),
                )

                # Use SOLID processor for result handling
                processor = QueryResultProcessor(config, console)
                processor.process_success(query_data, results, limit)

            else:
                _handle_operation_failure_with_cli_exception(
                    "Query",
                    query_result.error or "Unknown query error",
                )

    except (
        OSError,
        ValueError,
        AttributeError,
        RuntimeError,
        TypeError,
        KeyError,
    ) as e:
        _print_error_exception(e)
        _raise_cli_exception_from_exception(e)


@oracle.command()
@click.pass_context
def schemas(ctx: click.Context) -> None:
    """List Oracle database schemas."""
    config = ctx.obj["config"]

    try:
        api = FlextDbOracleApi.from_env(context_name="cli")

        with api:
            schemas_result = api.get_schemas()

            if schemas_result.success:
                schema_list = schemas_result.data

                # Null check para schema_list - refatoração DRY real
                if schema_list is None:
                    _handle_no_data_error_with_cli_exception("Schema retrieval")

                console.print(
                    Panel(
                        f"""✅ **Schemas Retrieved**

Total Schemas: {len(_safe_iterate_list(schema_list))}""",
                        title="Oracle Schemas",
                        border_style="green",
                    ),
                )

                if config.output_format == "table":
                    table = Table(title="Oracle Schemas")
                    table.add_column("Schema Name", style="cyan")

                    for schema in _safe_iterate_list(schema_list):
                        table.add_row(str(schema))

                    console.print(table)
                else:
                    format_output(
                        {"schemas": schema_list},
                        config.output_format,
                        console,
                    )
            else:
                console.print(
                    f"[red]Failed to retrieve schemas: {schemas_result.error}[/red]",
                )
                _raise_cli_error(f"Failed to retrieve schemas: {schemas_result.error}")

    except (
        OSError,
        ValueError,
        AttributeError,
        RuntimeError,
        TypeError,
        KeyError,
    ) as e:
        _print_error_exception(e)
        _raise_cli_exception_from_exception(e)


@oracle.command()
@click.option(
    "--schema",
    help="Schema name to filter tables",
)
@click.pass_context
def tables(ctx: click.Context, schema: str | None) -> None:
    """List Oracle database tables."""
    config = ctx.obj["config"]

    try:
        api = FlextDbOracleApi.from_env(context_name="cli")

        with api:
            tables_result = api.get_tables(schema)

            if tables_result.success:
                table_list = tables_result.data

                # Null check para table_list - refatoração DRY real
                if table_list is None:
                    _handle_no_data_error_with_cli_exception("Table retrieval")

                title = f"Oracle Tables{f' in {schema}' if schema else ''}"
                console.print(
                    Panel(
                        f"""✅ **Tables Retrieved**

Total Tables: {len(_safe_iterate_list(table_list))}
Schema: {schema or "All"}""",
                        title=title,
                        border_style="green",
                    ),
                )

                if config.output_format == "table":
                    table = Table(title=title)
                    table.add_column("Table Name", style="cyan")
                    table.add_column("Schema", style="yellow")

                    for table_info in _safe_iterate_list(table_list):
                        # Extract table info using helper function - eliminates deep nesting
                        name, schema_name = _extract_table_info(table_info, schema)
                        table.add_row(name, schema_name)

                    console.print(table)
                else:
                    format_output({"tables": table_list}, config.output_format, console)
            else:
                console.print(
                    f"[red]Failed to retrieve tables: {tables_result.error}[/red]",
                )
                _raise_cli_error(f"Failed to retrieve tables: {tables_result.error}")

    except (
        OSError,
        ValueError,
        AttributeError,
        RuntimeError,
        TypeError,
        KeyError,
    ) as e:
        _print_error_exception(e)
        _raise_cli_exception_from_exception(e)


class PluginManagerProcessor:
    """refactoring: Single Responsibility for plugin management operations."""

    def __init__(self, config: ConfigProtocol, console: Console) -> None:
        """Initialize plugin manager processor."""
        self.config = config
        self.console = console

    def handle_registration_success(self, registration_results: dict[str, str]) -> None:
        """Handle successful plugin registration - Single Responsibility."""
        self._display_registration_success_panel()
        self._display_registration_results(registration_results)

    def handle_plugin_list_success(self, plugin_list: list[FlextPlugin]) -> None:
        """Handle successful plugin listing - Single Responsibility."""
        self.console.print(f"\n[blue]Available Plugins: {len(plugin_list)}[/blue]")

        if self.config.output_format == "table":
            self._display_plugins_table(plugin_list)
        else:
            self._display_plugins_structured(plugin_list)

    def _display_registration_success_panel(self) -> None:
        """Display registration success panel."""
        self.console.print(
            Panel(
                """✅ **Plugin Registration Complete**""",
                title="Oracle Plugins",
                border_style="green",
            ),
        )

    def _display_registration_results(
        self,
        registration_results: dict[str, str],
    ) -> None:
        """Display registration results based on output format."""
        if self.config.output_format == "table":
            self._display_registration_table(registration_results)
        else:
            format_output(registration_results, self.config.output_format, self.console)

    def _display_registration_table(self, registration_results: dict[str, str]) -> None:
        """Display registration results as table."""
        table = Table(title="Plugin Registration Results")
        table.add_column("Plugin Name", style="cyan")
        table.add_column("Status", style="green")

        for plugin_name, status in _safe_iterate_dict(registration_results).items():
            table.add_row(plugin_name, status)

        self.console.print(table)

    def _display_plugins_table(self, plugin_list: list[FlextPlugin]) -> None:
        """Display plugins as rich table."""
        plugin_table = Table(title="Available Plugins")
        plugin_table.add_column("Name", style="cyan")
        plugin_table.add_column("Version", style="yellow")
        plugin_table.add_column("Type", style="magenta")
        plugin_table.add_column("Description", style="white")

        for plugin in plugin_list:
            plugin_table.add_row(
                str(plugin.name),
                str(plugin.version),
                str(getattr(plugin, "plugin_type", "unknown") or "unknown"),
                str(getattr(plugin, "description", "") or ""),
            )

        self.console.print(plugin_table)

    def _display_plugins_structured(self, plugin_list: list[FlextPlugin]) -> None:
        """Display plugins as structured output."""
        plugin_data: list[dict[str, object]] = [
            {
                "name": p.name,
                "version": p.version,
                "type": getattr(p, "plugin_type", "unknown"),
                "description": getattr(p, "description", ""),
            }
            for p in plugin_list
        ]
        format_output({"plugins": plugin_data}, self.config.output_format, self.console)


@oracle.command()
@click.pass_context
def plugins(ctx: click.Context) -> None:
    """Manage Oracle database plugins - SOLID refactored."""
    config = ctx.obj["config"]

    try:
        api = FlextDbOracleApi.from_env(context_name="cli")

        with api:
            # Use SOLID processor for plugin management
            processor = PluginManagerProcessor(config, console)

            # Register all Oracle plugins
            register_result = register_all_oracle_plugins(api)

            if register_result.success:
                registration_results = register_result.data

                # Null check for registration_results
                if registration_results is None:
                    _handle_no_data_error_with_cli_exception("Plugin registration")

                # Validation for production safety - no assert needed after explicit checks
                if registration_results is None:
                    console.print(
                        "[red]❌ Plugin registration succeeded but returned None[/red]",
                    )
                    _raise_cli_error("Plugin registration succeeded but returned None")

                # registration_results is guaranteed non-None after validation above
                processor.handle_registration_success(
                    cast("dict[str, str]", registration_results),
                )

                # List all plugins
                plugins_result = api.list_plugins()
                if plugins_result.success and plugins_result.data:
                    processor.handle_plugin_list_success(plugins_result.data)
            else:
                console.print(
                    f"[red]Plugin registration failed: {register_result.error}[/red]",
                )
                _raise_cli_error(f"Plugin registration failed: {register_result.error}")

    except (
        OSError,
        ValueError,
        AttributeError,
        RuntimeError,
        TypeError,
        KeyError,
    ) as e:
        _print_error_exception(e)
        _raise_cli_exception_from_exception(e)


@oracle.command()
@click.option(
    "--sql",
    required=True,
    help="SQL query to optimize",
)
@click.pass_context
def optimize(ctx: click.Context, sql: str) -> None:
    """Optimize SQL query using built-in plugin."""
    config = ctx.obj["config"]

    try:
        api = FlextDbOracleApi.from_env(context_name="cli")

        with api:
            optimize_result = api.optimize_query(sql)

            if optimize_result.success:
                optimization_data = optimize_result.data

                # Null check para optimization_data - refatoração DRY real
                if optimization_data is None:
                    _handle_no_data_error_with_cli_exception("Query optimization")

                suggestions = _safe_get_test_data(optimization_data, "suggestions", [])

                console.print(
                    Panel(
                        f"""✅ **Query Analysis Complete**

SQL Length: {_safe_get_test_data(optimization_data, "sql_length", 0)} characters
Has JOINs: {_safe_get_test_data(optimization_data, "has_joins", default=False)}
Has Subqueries: {_safe_get_test_data(optimization_data, "has_subqueries", default=False)}
Suggestions: {_safe_get_list_length(suggestions)}""",
                        title="Query Optimization",
                        border_style="green",
                    ),
                )

                if suggestions and isinstance(suggestions, list):
                    console.print("\n[yellow]Optimization Suggestions:[/yellow]")
                    for i, suggestion in enumerate(suggestions, 1):
                        console.print(f"  {i}. {suggestion}")
                else:
                    console.print(
                        "\n[green]No optimization suggestions - query looks good![/green]",
                    )

                if config.output_format != "table":
                    format_output(optimization_data, config.output_format, console)
            else:
                console.print(
                    f"[red]Query optimization failed: {optimize_result.error}[/red]",
                )
                _raise_cli_error(f"Query optimization failed: {optimize_result.error}")

    except (
        OSError,
        ValueError,
        AttributeError,
        RuntimeError,
        TypeError,
        KeyError,
    ) as e:
        _print_error_exception(e)
        _raise_cli_exception_from_exception(e)


@oracle.command()
@click.pass_context
def health(ctx: click.Context) -> None:
    """Check Oracle database health status."""
    config = ctx.obj["config"]

    try:
        api = FlextDbOracleApi.from_env(context_name="cli")

        with api:
            health_result = api.get_health_status()

            if health_result.success:
                health_data = health_result.data

                # Null check para health data - refatoração DRY real
                if health_data is None:
                    _handle_no_data_error_with_cli_exception("Health check")

                status = getattr(health_data, "status", "unknown")
                status_color = {
                    "healthy": "green",
                    "degraded": "yellow",
                    "unhealthy": "red",
                }.get(status, "white")

                component = getattr(health_data, "component", "unknown")
                message = getattr(health_data, "message", "No message")
                timestamp = getattr(health_data, "timestamp", None)
                timestamp_str = timestamp.isoformat() if timestamp else "N/A"

                console.print(
                    Panel(
                        f"""**Health Status: [{status_color}]{status.upper()}[/{status_color}]**

Component: {component}
Message: {message}
Timestamp: {timestamp_str}""",
                        title="Oracle Health Check",
                        border_style=status_color,
                    ),
                )

                # Show metrics com null check - refatoração DRY real
                metrics = getattr(health_data, "metrics", {})
                if metrics:
                    if config.output_format == "table":
                        metrics_table = Table(title="Health Metrics")
                        metrics_table.add_column("Metric", style="cyan")
                        metrics_table.add_column("Value", style="green")

                        for key, value in metrics.items():
                            metrics_table.add_row(
                                key.replace("_", " ").title(),
                                str(value),
                            )

                        console.print(metrics_table)
                    else:
                        health_dict = {
                            "status": status,
                            "component": component,
                            "message": message,
                            "metrics": metrics,
                            "timestamp": timestamp_str,
                        }
                        # format_output precisa de console como primeiro argumento
                        format_output(health_dict, config.output_format, console)
            else:
                _print_error(f"Health check failed: {health_result.error}")
                _raise_cli_error(f"Health check failed: {health_result.error}")

    except (
        OSError,
        ValueError,
        AttributeError,
        RuntimeError,
        TypeError,
        KeyError,
    ) as e:
        _print_error_exception(e)
        _raise_cli_exception_from_exception(e)


def main() -> None:
    """Execute main CLI entry point."""
    oracle()


if __name__ == "__main__":
    main()
