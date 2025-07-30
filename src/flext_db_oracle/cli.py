"""Oracle Database CLI Commands - Production-ready command line interface.

Copyright (c) 2025 FLEXT Contributors
SPDX-License-Identifier: MIT

CLI commands for Oracle database operations using flext-cli patterns.
"""

from __future__ import annotations

import json
from dataclasses import dataclass

import click
from flext_cli import (
    format_output,
    get_config,
)
from pydantic import SecretStr
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

# Direct imports to avoid circular dependency - DRY refactoring
from flext_db_oracle.api import FlextDbOracleApi
from flext_db_oracle.config import FlextDbOracleConfig
from flext_db_oracle.plugins import register_all_oracle_plugins

from .constants import ORACLE_DEFAULT_PORT

console = Console()


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
    config.output_format = output
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
    config = ctx.obj["config"]
    debug = ctx.obj["debug"]

    try:
        # Create Oracle configuration com valores padrão completos - refatoração DRY real
        oracle_config = FlextDbOracleConfig(
            host=params.host,
            port=params.port,
            service_name=params.service_name,
            username=params.username,
            password=SecretStr(params.password),
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

        # Create API and connect
        api = FlextDbOracleApi(oracle_config, context_name="cli")

        if debug:
            console.print(
                f"[blue]Connecting to {params.host}:{params.port}/{params.service_name}...[/blue]",
            )

        api.connect()

        # Test connection with observability
        test_result = api.test_connection_with_observability()

        if test_result.is_success:
            test_data = test_result.data

            # Null check para test_data - refatoração DRY real
            if test_data is None:
                console.print("[red]Connection test returned no data[/red]")
                _raise_cli_error("Connection test returned no data")

            # Create connection info panel
            info_panel = Panel(
                f"""✅ **Connection Successful**

Host: {params.host}
Port: {params.port}
Service: {params.service_name}
Status: {_safe_get_test_data(test_data, "status", "unknown")}
Test Duration: {_safe_get_test_data(test_data, "test_duration_ms", 0)}ms""",
                title="Oracle Connection",
                border_style="green",
            )
            console.print(info_panel)

            # Show health data if available
            health_data = _safe_get_test_data(test_data, "health", {})
            if health_data and isinstance(health_data, dict):
                output_data = {
                    "connection_status": _safe_get_test_data(test_data, "status"),
                    "test_duration_ms": _safe_get_test_data(
                        test_data,
                        "test_duration_ms",
                    ),
                    "health_status": health_data.get("status"),
                    "health_message": health_data.get("message"),
                    "metrics": health_data.get("metrics", {}),
                }

                if config.output_format == "table":
                    table = Table(title="Connection Details")
                    table.add_column("Property", style="cyan")
                    table.add_column("Value", style="green")

                    for key, value in output_data.items():
                        if isinstance(value, dict):
                            formatted_value = json.dumps(value, indent=2)
                        else:
                            formatted_value = str(value)
                        table.add_row(key.replace("_", " ").title(), formatted_value)

                    console.print(table)
                else:
                    format_output(output_data, config.output_format, console)
        else:
            console.print(f"[red]Connection failed: {test_result.error}[/red]")
            _raise_cli_error(f"Connection failed: {test_result.error}")

    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise click.ClickException(str(e)) from e


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

        if test_result.is_success:
            test_data = test_result.data

            # Null check para test_data - refatoração DRY real
            if test_data is None:
                console.print("[red]Connection test returned no data[/red]")
                _raise_cli_error("Connection test returned no data")

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
            console.print(f"[red]Connection failed: {test_result.error}[/red]")
            _raise_cli_error(f"Connection failed: {test_result.error}")

    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise click.ClickException(str(e)) from e


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
    """Execute SQL query against Oracle database."""
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

            if query_result.is_success:
                query_data = query_result.data

                # Null check para query_data - refatoração DRY real
                if query_data is None:
                    console.print("[red]Query execution returned no data[/red]")
                    _raise_cli_error("Query execution returned no data")

                results = _safe_get_query_data_attr(query_data, "rows", [])

                # Apply limit if specified
                if limit and isinstance(results, list) and len(results) > limit:
                    results = results[:limit]
                    console.print(f"[yellow]Results limited to {limit} rows[/yellow]")

                # Display results
                console.print(
                    Panel(
                        f"""✅ **Query Executed Successfully**

Execution Time: {_safe_get_query_data_attr(query_data, "execution_time_ms", 0):.2f}ms
Rows Returned: {_safe_get_query_data_attr(query_data, "row_count", 0)}
Columns: {_safe_get_list_length(_safe_get_query_data_attr(query_data, "columns", []))}""",
                        title="Query Results",
                        border_style="green",
                    ),
                )

                if (
                    config.output_format == "table"
                    and results
                    and isinstance(results, list)
                ):
                    # Create rich table
                    table = Table(title=f"Query Results ({len(results)} rows)")

                    # Add columns
                    columns = _safe_get_query_data_attr(query_data, "columns", [])
                    if columns and isinstance(columns, list):
                        for col in columns:
                            table.add_column(str(col), style="cyan")

                    # Add rows
                    for row in results:
                        table.add_row(
                            *[
                                str(cell) if cell is not None else "NULL"
                                for cell in row
                            ],
                        )

                    console.print(table)
                else:
                    # Format as requested output
                    output_data = {
                        "execution_time_ms": _safe_get_query_data_attr(
                            query_data,
                            "execution_time_ms",
                            0,
                        ),
                        "row_count": _safe_get_query_data_attr(
                            query_data,
                            "row_count",
                            0,
                        ),
                        "columns": _safe_get_query_data_attr(query_data, "columns", []),
                        "rows": results,
                    }
                    format_output(output_data, config.output_format, console)

            else:
                console.print(f"[red]Query failed: {query_result.error}[/red]")
                _raise_cli_error(f"Query failed: {query_result.error}")

    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise click.ClickException(str(e)) from e


@oracle.command()
@click.pass_context
def schemas(ctx: click.Context) -> None:
    """List Oracle database schemas."""
    config = ctx.obj["config"]

    try:
        api = FlextDbOracleApi.from_env(context_name="cli")

        with api:
            schemas_result = api.get_schemas()

            if schemas_result.is_success:
                schema_list = schemas_result.data

                # Null check para schema_list - refatoração DRY real
                if schema_list is None:
                    console.print("[red]Schema retrieval returned no data[/red]")
                    _raise_cli_error("Schema retrieval returned no data")

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

    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise click.ClickException(str(e)) from e


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

            if tables_result.is_success:
                table_list = tables_result.data

                # Null check para table_list - refatoração DRY real
                if table_list is None:
                    console.print("[red]Table retrieval returned no data[/red]")
                    _raise_cli_error("Table retrieval returned no data")

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
                        # Simplificar type checking - refatoração DRY real
                        if hasattr(table_info, "get"):
                            # É um dict-like object
                            name = (
                                table_info.get("name", "")
                                if hasattr(table_info, "get")
                                else str(table_info)
                            )
                            schema_name = (
                                table_info.get("schema", schema or "")
                                if hasattr(table_info, "get")
                                else (schema or "")
                            )
                            table.add_row(name, schema_name)
                        else:
                            # É um objeto simples
                            table.add_row(str(table_info), schema or "")

                    console.print(table)
                else:
                    format_output({"tables": table_list}, config.output_format, console)
            else:
                console.print(
                    f"[red]Failed to retrieve tables: {tables_result.error}[/red]",
                )
                _raise_cli_error(f"Failed to retrieve tables: {tables_result.error}")

    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise click.ClickException(str(e)) from e


@oracle.command()
@click.pass_context
def plugins(ctx: click.Context) -> None:
    """Manage Oracle database plugins."""
    config = ctx.obj["config"]

    try:
        api = FlextDbOracleApi.from_env(context_name="cli")

        with api:
            # Register all Oracle plugins
            register_result = register_all_oracle_plugins(api)

            if register_result.is_success:
                registration_results = register_result.data

                # Null check para registration_results - refatoração DRY real
                if registration_results is None:
                    console.print("[red]Plugin registration returned no data[/red]")
                    _raise_cli_error("Plugin registration returned no data")

                console.print(
                    Panel(
                        """✅ **Plugin Registration Complete**""",
                        title="Oracle Plugins",
                        border_style="green",
                    ),
                )

                if config.output_format == "table":
                    table = Table(title="Plugin Registration Results")
                    table.add_column("Plugin Name", style="cyan")
                    table.add_column("Status", style="green")

                    for plugin_name, status in _safe_iterate_dict(
                        registration_results,
                    ).items():
                        # table.add_row não aceita style como argumento - refatoração DRY real
                        table.add_row(plugin_name, status)

                    console.print(table)
                else:
                    format_output(registration_results, config.output_format, console)

                # List all plugins
                plugins_result = api.list_plugins()
                if plugins_result.is_success and plugins_result.data:
                    plugin_list = plugins_result.data

                    console.print(
                        f"\n[blue]Available Plugins: {len(plugin_list)}[/blue]",
                    )

                    if config.output_format == "table":
                        plugin_table = Table(title="Available Plugins")
                        plugin_table.add_column("Name", style="cyan")
                        plugin_table.add_column("Version", style="yellow")
                        plugin_table.add_column("Type", style="magenta")
                        plugin_table.add_column("Description", style="white")

                        for plugin in plugin_list:
                            plugin_table.add_row(
                                str(plugin.name),
                                str(plugin.version),
                                str(
                                    getattr(plugin, "plugin_type", "unknown")
                                    or "unknown",
                                ),
                                str(getattr(plugin, "description", "") or ""),
                            )

                        console.print(plugin_table)
                    else:
                        plugin_data = [
                            {
                                "name": p.name,
                                "version": p.version,
                                "type": getattr(p, "plugin_type", "unknown"),
                                "description": getattr(p, "description", ""),
                            }
                            for p in plugin_list
                        ]
                        format_output(
                            {"plugins": plugin_data},
                            config.output_format,
                            console,
                        )
            else:
                console.print(
                    f"[red]Plugin registration failed: {register_result.error}[/red]",
                )
                _raise_cli_error(f"Plugin registration failed: {register_result.error}")

    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise click.ClickException(str(e)) from e


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

            if optimize_result.is_success:
                optimization_data = optimize_result.data

                # Null check para optimization_data - refatoração DRY real
                if optimization_data is None:
                    console.print("[red]Query optimization returned no data[/red]")
                    _raise_cli_error("Query optimization returned no data")

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

    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise click.ClickException(str(e)) from e


@oracle.command()
@click.pass_context
def health(ctx: click.Context) -> None:
    """Check Oracle database health status."""
    config = ctx.obj["config"]

    try:
        api = FlextDbOracleApi.from_env(context_name="cli")

        with api:
            health_result = api.get_health_status()

            if health_result.is_success:
                health_data = health_result.data

                # Null check para health data - refatoração DRY real
                if health_data is None:
                    console.print("[red]Health check returned no data[/red]")
                    _raise_cli_error("Health check returned no data")

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
                console.print(f"[red]Health check failed: {health_result.error}[/red]")
                _raise_cli_error(f"Health check failed: {health_result.error}")

    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise click.ClickException(str(e)) from e


def main() -> None:
    """Execute main CLI entry point."""
    oracle()


if __name__ == "__main__":
    main()
