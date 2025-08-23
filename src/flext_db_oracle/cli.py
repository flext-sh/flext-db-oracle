"""FLEXT DB Oracle CLI using flext-cli comprehensive patterns.

Enterprise-grade CLI application demonstrating all flext-cli patterns and capabilities
for Oracle database operations with professional user experience.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

import click
from flext_cli import (
    ExistingDir,
    FlextApiClient,
    FlextCliContext,
    FlextCliEntityFactory,
    FlextCliOutputFormat,
    PositiveInt,
    cli_enhanced,
    cli_handle_keyboard_interrupt,
    cli_measure_time,
    create_cli_container,
    setup_cli,
)
from flext_cli.simple_api import (
    create_development_cli_config,
    create_production_cli_config,
)
from flext_core import (
    FlextDecorators,
    FlextLoggingDecorators,
    FlextPerformanceDecorators,
    FlextResult,
    get_logger,
)
from pydantic import SecretStr
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm, Prompt
from rich.table import Table

from flext_db_oracle.config import FlextDbOracleConfig
from flext_db_oracle.plugins import register_all_oracle_plugins
from flext_db_oracle.utilities import FlextDbOracleUtilities


class FlextDbOracleCliApplication:
    """Enterprise Oracle CLI application with comprehensive flext-cli integration.

    Follows flext-cli hierarchical configuration patterns and modern architecture.
    """

    def __init__(self, *, debug: bool = False) -> None:
        """Initialize Oracle CLI application with hierarchical configuration."""
        # Modern flext-cli pattern: Use hierarchical configuration
        self.cli_config = (
            create_development_cli_config(debug=True, log_level="DEBUG")
            if debug
            else create_production_cli_config(debug=False, log_level="INFO")
        )

        # Core CLI components using modern patterns
        self.console = Console()
        self.logger = get_logger(__name__)
        self.container: object = create_cli_container()
        self.api_client = FlextApiClient()
        self.entity_factory = FlextCliEntityFactory()

        # Application state with modern patterns
        self.current_connection: object | None = None
        self.active_operations: list[str] = []

        # Modern flext-cli pattern: Type-safe user preferences
        self.user_preferences: dict[str, object] = {
            "default_output_format": "table",
            "auto_confirm_operations": False,
            "show_execution_time": True,
            "color_output": True,
            "verbose_errors": True,
            "connection_timeout": 30,
            "query_limit": 1000,
            "enable_plugins": True,
        }

    def initialize_application(self) -> FlextResult[None]:
        """Initialize the Oracle CLI application with setup and validation."""
        try:
            self.console.print(
                Panel(
                    "[bold cyan]FLEXT Oracle Database CLI[/bold cyan]\n\n"
                    "[yellow]Enterprise Oracle operations with professional CLI experience...[/yellow]",
                    expand=False,
                )
            )

            # Setup CLI foundation
            setup_result = setup_cli()
            if not setup_result.success:
                return FlextResult[None].fail(f"CLI setup failed: {setup_result.error}")

            # Register services in container
            self._register_core_services()

            self.console.print("✅ Oracle CLI initialized successfully")
            return FlextResult[None].ok(None)

        except Exception as e:
            return FlextResult[None].fail(f"Oracle CLI initialization failed: {e}")

    def _register_core_services(self) -> None:
        """Register core services in the DI container."""
        services = [
            ("console", self.console),
            ("logger", self.logger),
            ("config", self.cli_config),
            ("api_client", self.api_client),
            ("entity_factory", self.entity_factory),
        ]

        for service_name, service_instance in services:
            # Register services if container has register method
            if hasattr(self.container, "register"):
                self.container.register(service_name, service_instance)


# Global application instance - initialized with debug detection
app: FlextDbOracleCliApplication | None = None


def get_app(*, debug: bool = False) -> FlextDbOracleCliApplication:
    """Get or create the global application instance with proper configuration."""
    global app  # noqa: PLW0603
    if app is None:
        app = FlextDbOracleCliApplication(debug=debug)
    return app


# Main CLI group with modern flext-cli patterns
@click.group(
    context_settings={"help_option_names": ["-h", "--help"]},
    invoke_without_command=True,
)
@click.version_option(version="0.9.0", prog_name="flext-db-oracle")
@click.option(
    "--profile",
    default="default",
    envvar="FLEXT_DB_ORACLE_PROFILE",
    help="Configuration profile (default/dev/staging/prod)",
)
@click.option(
    "--output",
    "-o",
    type=click.Choice(["table", "json", "yaml", "csv", "plain"]),
    default="table",
    help="Output format",
)
@click.option(
    "--debug/--no-debug",
    default=False,
    envvar="FLEXT_DB_ORACLE_DEBUG",
    help="Enable debug mode",
)
@click.option("--verbose/--quiet", default=False, help="Verbose output")
@click.pass_context
@cli_enhanced(
    validate_inputs=True,
    handle_keyboard_interrupt=True,
    measure_time=True,
)
def oracle_cli(
    ctx: click.Context,
    profile: str,
    output: str,
    *,
    debug: bool,
    verbose: bool,
) -> None:
    """FLEXT Oracle Database CLI - Enterprise Oracle Operations.

    Professional Oracle database management with comprehensive CLI capabilities
    including connection management, query execution, schema operations, and more.
    """
    # Modern flext-cli pattern: Get application with debug configuration
    application = get_app(debug=debug)

    # Initialize application using modern setup_cli patterns
    init_result = application.initialize_application()
    if not init_result.success:
        application.console.print(
            f"[red]Initialization failed: {init_result.error}[/red]"
        )
        ctx.exit(1)

    # Modern flext-cli pattern: Setup Click context with CLI components
    ctx.ensure_object(dict)
    ctx.obj["app"] = application
    ctx.obj["profile"] = profile
    ctx.obj["output_format"] = output
    ctx.obj["debug"] = debug
    ctx.obj["verbose"] = verbose

    # Modern flext-cli pattern: Hierarchical configuration context
    cli_context = FlextCliContext(
        console=application.console,
        debug=debug,
        quiet=not verbose,
        verbose=verbose,
    )
    ctx.obj["cli_context"] = cli_context
    ctx.obj["config"] = application.cli_config

    # Show help if no command (modern flext-cli pattern)
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())

    if debug:
        application.console.print(
            f"[dim]Profile: {profile} | Format: {output} | Debug: {debug} | Verbose: {verbose}[/dim]"
        )


# Connection Management Commands Group
@oracle_cli.group()
@click.pass_context
def connection(ctx: click.Context) -> None:
    """Oracle database connection management commands."""


@connection.command()
@click.option("--host", required=True, help="Oracle database host")
@click.option("--port", type=int, default=1521, help="Oracle database port")
@click.option("--service-name", required=True, help="Oracle service name")
@click.option("--username", required=True, help="Oracle username")
@click.option("--password", prompt=True, hide_input=True, help="Oracle password")
@click.pass_context
@cli_enhanced
@FlextPerformanceDecorators.time_execution
def test(
    ctx: click.Context,
    host: str,
    port: int,
    service_name: str,
    username: str,
    password: str,
) -> None:
    """Test Oracle database connection with specified parameters."""
    app: FlextDbOracleCliApplication = ctx.obj["app"]
    cli_context: FlextCliContext = ctx.obj["cli_context"]

    app.console.print(
        f"[green]Testing Oracle connection: {host}:{port}/{service_name}[/green]"
    )

    try:
        # Create configuration
        config = FlextDbOracleConfig(
            host=host,
            port=port,
            service_name=service_name,
            username=username,
            password=SecretStr(password),
        )

        # Create API and use context manager pattern for connection
        api = FlextDbOracleUtilities.create_api_from_config(config)

        try:
            with api as connected_api:
                # Test connection
                test_result = connected_api.test_connection()
                if not test_result.success:
                    app.console.print(
                        f"[red]Connection test failed: {test_result.error}[/red]"
                    )
                    ctx.exit(1)

                # Display success
                if cli_context.debug:
                    app.console.print(
                        f"[green]✅ Successfully connected to {host}:{port}/{service_name}[/green]"
                    )

                success_data = {
                    "status": "connected",
                    "host": host,
                    "port": port,
                    "service_name": service_name,
                    "username": username,
                }

                if cli_context.output == FlextCliOutputFormat.TABLE:
                    success_panel = Panel(
                        "✅ **Connection Successful**\n\n"
                        f"Host: {host}\n"
                        f"Port: {port}\n"
                        f"Service: {service_name}\n"
                        f"Username: {username}",
                        title="Oracle Connection",
                        border_style="green",
                    )
                    app.console.print(success_panel)
                elif cli_context.output == FlextCliOutputFormat.JSON:
                    app.console.print(json.dumps(success_data, indent=2))
                else:
                    app.console.print(str(success_data))

        except (ConnectionError, ValueError, OSError, RuntimeError) as e:
            app.console.print(f"[red]Connection failed: {e}[/red]")
            ctx.exit(1)

    except Exception as e:
        app.console.print(f"[red]Error: {e}[/red]")
        ctx.exit(1)


@oracle_cli.command()
@click.pass_context
@cli_enhanced(
    validate_inputs=True,
    handle_keyboard_interrupt=True,
    measure_time=True,
)
@FlextLoggingDecorators.log_execution
@FlextPerformanceDecorators.time_execution
def connect_env(ctx: click.Context) -> None:
    """Connect to Oracle database using environment variables."""
    debug = ctx.obj["debug"]
    output_format = ctx.obj["output_format"]

    try:
        # Create configuration from environment
        config_result = FlextDbOracleUtilities.create_config_from_env()
        if not config_result.success:
            app.console.print(f"[red]Configuration error: {config_result.error}[/red]")
            ctx.exit(1)

        config = config_result.value
        api = FlextDbOracleUtilities.create_api_from_config(config)

        # Use context manager pattern for connection
        try:
            with api as connected_api:
                # Test connection
                test_result = connected_api.test_connection()
                if not test_result.success:
                    app.console.print(
                        f"[red]Connection test failed: {test_result.error}[/red]"
                    )
                    ctx.exit(1)

                if debug:
                    app.console.print(
                        "[green]✅ Successfully connected using environment variables[/green]"
                    )

                success_data = {
                    "status": "connected",
                    "host": config.host,
                    "port": config.port,
                    "service_name": config.service_name,
                    "username": config.username,
                }

                if output_format == "table":
                    success_panel = Panel(
                        "✅ **Connection Successful (Environment)**\n\n"
                        f"Host: {config.host}\n"
                        f"Port: {config.port}\n"
                        f"Service: {config.service_name}\n"
                        f"Username: {config.username}",
                        title="Oracle Connection",
                        border_style="green",
                    )
                    app.console.print(success_panel)
                elif output_format == "json":
                    app.console.print(json.dumps(success_data, indent=2))
                else:
                    app.console.print(str(success_data))

        except (ConnectionError, ValueError, OSError, RuntimeError) as e:
            app.console.print(f"[red]Connection failed: {e}[/red]")
            ctx.exit(1)

    except Exception as e:
        app.console.print(f"[red]Error: {e}[/red]")
        ctx.exit(1)


@oracle_cli.command()
@click.option("--sql", required=True, help="SQL query to execute")
@click.option("--limit", type=int, default=100, help="Limit number of rows returned")
@click.pass_context
@cli_enhanced(
    validate_inputs=True,
    handle_keyboard_interrupt=True,
    measure_time=True,
)
@FlextLoggingDecorators.log_execution
@FlextPerformanceDecorators.time_execution
@FlextDecorators.safe_result
def query(ctx: click.Context, sql: str, limit: int) -> None:
    """Execute SQL query against Oracle database."""
    debug = ctx.obj["debug"]
    output_format = ctx.obj["output_format"]

    try:
        # Create configuration from environment
        config_result = FlextDbOracleUtilities.create_config_from_env()
        if not config_result.success:
            app.console.print(f"[red]Configuration error: {config_result.error}[/red]")
            ctx.exit(1)

        config = config_result.value
        api = FlextDbOracleUtilities.create_api_from_config(config)

        # Use context manager pattern for connection
        try:
            with api as connected_api:
                if debug:
                    app.console.print(
                        f"[blue]Executing query (limit={limit}): {sql[:100]}...[/blue]"
                    )

                # Execute query with limit
                query_result = connected_api.query(sql)
                if not query_result.success:
                    app.console.print(f"[red]Query failed: {query_result.error}[/red]")
                    ctx.exit(1)

                # Apply limit to result data
                result_data = query_result.value
                if isinstance(result_data, list) and len(result_data) > limit:
                    result_data = result_data[:limit]
                    app.console.print(
                        f"[yellow]Result limited to {limit} rows[/yellow]"
                    )
                FlextDbOracleUtilities.format_query_result(
                    result_data, output_format, app.console
                )

        except (ConnectionError, ValueError, OSError, RuntimeError) as e:
            app.console.print(f"[red]Connection failed: {e}[/red]")
            ctx.exit(1)

    except Exception as e:
        app.console.print(f"[red]Error: {e}[/red]")
        ctx.exit(1)


@oracle_cli.command()
@click.pass_context
@cli_enhanced(
    validate_inputs=True,
    handle_keyboard_interrupt=True,
    measure_time=True,
)
@FlextLoggingDecorators.log_execution
@FlextPerformanceDecorators.time_execution
def schemas(ctx: click.Context) -> None:
    """List all database schemas."""
    debug = ctx.obj["debug"]
    output_format = ctx.obj["output_format"]

    try:
        # Create configuration and API
        config_result = FlextDbOracleUtilities.create_config_from_env()
        if not config_result.success:
            app.console.print(f"[red]Configuration error: {config_result.error}[/red]")
            ctx.exit(1)

        config = config_result.value
        api = FlextDbOracleUtilities.create_api_from_config(config)

        # Use context manager pattern for connection
        try:
            with api as connected_api:
                # Get schemas
                schemas_result = connected_api.get_schemas()
                if not schemas_result.success:
                    app.console.print(
                        f"[red]Failed to get schemas: {schemas_result.error}[/red]"
                    )
                    ctx.exit(1)

                schema_list = schemas_result.value

                if debug:
                    app.console.print(f"[blue]Found {len(schema_list)} schemas[/blue]")

                # Display results
                if output_format == "table":
                    table = Table(title=f"Database Schemas ({len(schema_list)} found)")
                    table.add_column("Schema Name", style="cyan")

                    for schema in schema_list:
                        table.add_row(schema)

                    app.console.print(table)
                else:
                    data = {"schemas": schema_list, "count": len(schema_list)}
                    if output_format == "json":
                        app.console.print(json.dumps(data, indent=2))
                    else:
                        app.console.print(str(data))

        except (ConnectionError, ValueError, OSError, RuntimeError) as e:
            app.console.print(f"[red]Connection failed: {e}[/red]")
            ctx.exit(1)

    except Exception as e:
        app.console.print(f"[red]Error: {e}[/red]")
        ctx.exit(1)


@oracle_cli.command()
@click.option("--schema", help="Schema name to list tables for")
@cli_enhanced
@FlextPerformanceDecorators.time_execution
@FlextLoggingDecorators.log_calls
@FlextDecorators.safe_call((KeyboardInterrupt,))
@click.pass_context
def tables(ctx: click.Context, schema: str | None) -> None:
    """List tables in schema."""
    debug = ctx.obj["debug"]
    output_format = ctx.obj["output_format"]

    try:
        # Create configuration and API
        config_result = FlextDbOracleUtilities.create_config_from_env()
        if not config_result.success:
            app.console.print(f"[red]Configuration error: {config_result.error}[/red]")
            ctx.exit(1)

        config = config_result.value
        api = FlextDbOracleUtilities.create_api_from_config(config)

        # Use context manager pattern for connection
        try:
            with api as connected_api:
                # Get tables
                tables_result = connected_api.get_tables(schema)
                if not tables_result.success:
                    app.console.print(
                        f"[red]Failed to get tables: {tables_result.error}[/red]"
                    )
                    ctx.exit(1)

                table_list = tables_result.value
                schema_display = schema or "current"

                if debug:
                    app.console.print(
                        f"[blue]Found {len(table_list)} tables in schema '{schema_display}'[/blue]"
                    )

                # Display results
                if output_format == "table":
                    table = Table(
                        title=f"Tables in Schema '{schema_display}' ({len(table_list)} found)"
                    )
                    table.add_column("Table Name", style="cyan")

                    for table_name in table_list:
                        table.add_row(table_name)

                    app.console.print(table)
                else:
                    data = {
                        "schema": schema_display,
                        "tables": table_list,
                        "count": len(table_list),
                    }
                    if output_format == "json":
                        app.console.print(json.dumps(data, indent=2))
                    else:
                        app.console.print(str(data))

        except (ConnectionError, ValueError, OSError, RuntimeError) as e:
            app.console.print(f"[red]Connection failed: {e}[/red]")
            ctx.exit(1)

    except Exception as e:
        app.console.print(f"[red]Error: {e}[/red]")
        ctx.exit(1)


@oracle_cli.command()
@click.pass_context
def health(ctx: click.Context) -> None:
    """Check Oracle database health status."""
    debug = ctx.obj["debug"]
    output_format = ctx.obj["output_format"]

    try:
        # Create configuration and API
        config_result = FlextDbOracleUtilities.create_config_from_env()
        if not config_result.success:
            app.console.print(f"[red]Configuration error: {config_result.error}[/red]")
            ctx.exit(1)

        config = config_result.value
        api = FlextDbOracleUtilities.create_api_from_config(config)

        # Use context manager pattern for connection
        try:
            with api as connected_api:
                if debug:
                    app.console.print("[blue]Performing health check...[/blue]")

                # Get health status
                health_result = connected_api.get_health_check()
                if not health_result.success:
                    app.console.print(
                        f"[red]Health check failed: {health_result.error}[/red]"
                    )
                    ctx.exit(1)

                health_data = health_result.value

                # Display health status
                FlextDbOracleUtilities._display_health_data(
                    health_data, output_format, app.console
                )

        except (ConnectionError, ValueError, OSError, RuntimeError) as e:
            app.console.print(f"[red]Connection failed: {e}[/red]")
            ctx.exit(1)

    except Exception as e:
        app.console.print(f"[red]Error: {e}[/red]")
        ctx.exit(1)


@oracle_cli.command()
@click.pass_context
def plugins(ctx: click.Context) -> None:
    """Manage Oracle database plugins."""
    debug = ctx.obj["debug"]
    output_format = ctx.obj["output_format"]

    try:
        # Create configuration and API
        config_result = FlextDbOracleUtilities.create_config_from_env()
        if not config_result.success:
            app.console.print(f"[red]Configuration error: {config_result.error}[/red]")
            ctx.exit(1)

        config = config_result.value
        api = FlextDbOracleUtilities.create_api_from_config(config)

        # Use context manager pattern for connection
        try:
            with api as connected_api:
                if debug:
                    app.console.print("[blue]Registering Oracle plugins...[/blue]")

                # Register plugins
                register_all_oracle_plugins(connected_api)

                # List available plugins
                plugin_list = [
                    "data_validation_plugin",
                    "performance_monitor_plugin",
                    "security_audit_plugin",
                ]

                if output_format == "table":
                    table = Table(title="Oracle Database Plugins")
                    table.add_column("Plugin Name", style="cyan")
                    table.add_column("Status", style="green")

                    for plugin in plugin_list:
                        table.add_row(plugin, "✅ Registered")

                    app.console.print(table)
                else:
                    data = {
                        "plugins": plugin_list,
                        "count": len(plugin_list),
                        "status": "registered",
                    }
                    if output_format == "json":
                        app.console.print(json.dumps(data, indent=2))
                    else:
                        app.console.print(str(data))

        except (ConnectionError, ValueError, OSError, RuntimeError) as e:
            app.console.print(f"[red]Connection failed: {e}[/red]")
            ctx.exit(1)

    except Exception as e:
        app.console.print(f"[red]Error: {e}[/red]")
        ctx.exit(1)


# Configuration Management Commands Group
@oracle_cli.group()
@click.pass_context
def config(ctx: click.Context) -> None:
    """Oracle CLI configuration management commands."""


@config.command()
@click.pass_context
@cli_enhanced
def show(ctx: click.Context) -> None:
    """Show current Oracle CLI configuration."""
    app: FlextDbOracleCliApplication = ctx.obj["app"]

    app.console.print("[green]Oracle CLI Configuration[/green]")

    # Display configuration
    config_table = Table(title="Oracle CLI Configuration")
    config_table.add_column("Setting", style="cyan")
    config_table.add_column("Value", style="green")

    config_table.add_row("Profile", ctx.obj["profile"])
    config_table.add_row("Output Format", ctx.obj["output_format"])
    config_table.add_row("Debug Mode", str(ctx.obj["debug"]))
    config_table.add_row("Verbose Mode", str(ctx.obj["verbose"]))

    app.console.print(config_table)

    # Show user preferences
    app.console.print("\n[yellow]User Preferences:[/yellow]")
    prefs_table = Table()
    prefs_table.add_column("Preference", style="cyan")
    prefs_table.add_column("Value", style="green")

    for pref_name, pref_value in app.user_preferences.items():
        prefs_table.add_row(pref_name, str(pref_value))

    app.console.print(prefs_table)


@config.command()
@click.option("--profile", help="Set default profile")
@click.option(
    "--output",
    type=click.Choice(["table", "json", "yaml", "csv", "plain"]),
    help="Set default output format",
)
@click.option("--timeout", type=PositiveInt, help="Set connection timeout")
@click.option("--query-limit", type=PositiveInt, help="Set query result limit")
@click.pass_context
@cli_enhanced
def set_config(
    ctx: click.Context,
    profile: str | None,
    output: str | None,
    timeout: int | None,
    query_limit: int | None,
) -> None:
    """Set Oracle CLI configuration values."""
    app: FlextDbOracleCliApplication = ctx.obj["app"]

    if not any([profile, output, timeout, query_limit]):
        app.console.print("[yellow]No configuration changes specified[/yellow]")
        return

    app.console.print("[green]Updating Oracle CLI configuration...[/green]")

    changes = []

    if profile:
        app.user_preferences["default_profile"] = profile
        changes.append(f"Profile: {profile}")

    if output:
        app.user_preferences["default_output_format"] = output
        changes.append(f"Output format: {output}")

    if timeout:
        app.user_preferences["connection_timeout"] = timeout
        changes.append(f"Connection timeout: {timeout}s")

    if query_limit:
        app.user_preferences["query_limit"] = query_limit
        changes.append(f"Query limit: {query_limit} rows")

    # Display changes
    app.console.print("✅ Oracle CLI configuration updated:")
    for change in changes:
        app.console.print(f"   • {change}")


# Interactive Commands Group
@oracle_cli.group()
@click.pass_context
def interactive(ctx: click.Context) -> None:
    """Interactive Oracle CLI commands and wizards."""


@interactive.command()
@click.pass_context
@cli_handle_keyboard_interrupt
@cli_enhanced
def wizard(ctx: click.Context) -> None:
    """Interactive Oracle connection setup wizard."""
    app: FlextDbOracleCliApplication = ctx.obj["app"]

    app.console.print(
        Panel(
            "[bold magenta]Oracle Database Connection Wizard[/bold magenta]\n\n"
            "[yellow]This wizard will guide you through Oracle database configuration...[/yellow]",
            expand=False,
        )
    )

    try:
        # Collect connection parameters
        host = Prompt.ask("Oracle database host", default="localhost")
        port = int(Prompt.ask("Oracle database port", default="1521"))
        service_name = Prompt.ask("Oracle service name", default="XE")
        username = Prompt.ask("Oracle username")
        password = Prompt.ask("Oracle password", password=True)

        # Optional advanced settings
        use_advanced = Confirm.ask("Configure advanced settings?", default=False)

        pool_size = 5
        connection_timeout = 30
        if use_advanced:
            pool_size = int(Prompt.ask("Connection pool size", default="5"))
            connection_timeout = int(
                Prompt.ask("Connection timeout (seconds)", default="30")
            )

        # Display summary
        wizard_table = Table(title="Oracle Connection Summary")
        wizard_table.add_column("Setting", style="cyan")
        wizard_table.add_column("Value", style="green")

        wizard_table.add_row("Host", host)
        wizard_table.add_row("Port", str(port))
        wizard_table.add_row("Service Name", service_name)
        wizard_table.add_row("Username", username)
        wizard_table.add_row("Password", "***" * len(password))
        wizard_table.add_row("Pool Size", str(pool_size))
        wizard_table.add_row("Timeout", f"{connection_timeout}s")

        app.console.print(wizard_table)

        # Test connection
        if Confirm.ask("Test connection with these settings?", default=True):
            with app.console.status("[bold green]Testing Oracle connection..."):
                try:
                    config = FlextDbOracleConfig(
                        host=host,
                        port=port,
                        service_name=service_name,
                        username=username,
                        password=SecretStr(password),
                        pool_size=pool_size,
                        connection_timeout=connection_timeout,
                    )

                    api = FlextDbOracleUtilities.create_api_from_config(config)
                    with api as connected_api:
                        test_result = connected_api.test_connection()
                        if test_result.success:
                            app.console.print("✅ Connection test successful!")

                            # Store configuration
                            wizard_config = {
                                "host": host,
                                "port": port,
                                "service_name": service_name,
                                "username": username,
                                "pool_size": pool_size,
                                "connection_timeout": connection_timeout,
                                "configured_at": datetime.now(UTC).isoformat(),
                            }

                            app.user_preferences.update(wizard_config)
                        else:
                            app.console.print(
                                f"[red]Connection test failed: {test_result.error}[/red]"
                            )

                except Exception as e:
                    app.console.print(f"[red]Connection error: {e}[/red]")
        else:
            app.console.print("[yellow]Connection test skipped[/yellow]")

    except KeyboardInterrupt:
        app.console.print("\n[yellow]Wizard cancelled by user[/yellow]")


# Database Analysis Commands Group
@oracle_cli.group()
@click.pass_context
def analyze(ctx: click.Context) -> None:
    """Oracle database analysis and statistics commands."""


@analyze.command()
@click.option(
    "--directory", type=ExistingDir, default=".", help="Output directory for report"
)
@click.pass_context
@cli_enhanced
@cli_measure_time
def database(ctx: click.Context, directory: Path) -> None:
    """Analyze Oracle database and generate comprehensive report."""
    app: FlextDbOracleCliApplication = ctx.obj["app"]

    app.console.print("[green]Analyzing Oracle database...[/green]")

    try:
        # Create configuration and API
        config_result = FlextDbOracleUtilities.create_config_from_env()
        if not config_result.success:
            app.console.print(f"[red]Configuration error: {config_result.error}[/red]")
            ctx.exit(1)

        config = config_result.value
        api = FlextDbOracleUtilities.create_api_from_config(config)

        with (
            api as connected_api,
            app.console.status("[bold green]Gathering database statistics..."),
        ):
            # Get comprehensive database information
            schemas_result = connected_api.get_schemas()
            total_schemas = len(schemas_result.unwrap_or([]))

            # Get tables from current schema
            tables_result = connected_api.get_tables()
            total_tables = len(tables_result.unwrap_or([]))

            # Generate analysis report
            analysis_table = Table(title="Oracle Database Analysis")
            analysis_table.add_column("Metric", style="cyan")
            analysis_table.add_column("Value", style="green")

            analysis_table.add_row("Database Host", config.host)
            analysis_table.add_row("Service Name", config.service_name)
            analysis_table.add_row("Total Schemas", str(total_schemas))
            analysis_table.add_row("Total Tables", str(total_tables))
            analysis_table.add_row(
                "Analysis Time", datetime.now(UTC).strftime("%Y-%m-%d %H:%M:%S UTC")
            )

            app.console.print(analysis_table)

            # Save report to file if requested
            report_file = (
                directory
                / f"oracle_analysis_{datetime.now(UTC).strftime('%Y%m%d_%H%M%S')}.json"
            )
            report_data = {
                "database_host": config.host,
                "service_name": config.service_name,
                "total_schemas": total_schemas,
                "total_tables": total_tables,
                "analysis_timestamp": datetime.now(UTC).isoformat(),
            }

            report_file.write_text(json.dumps(report_data, indent=2))
            app.console.print(f"📄 Analysis report saved to: {report_file}")

    except Exception as e:
        app.console.print(f"[red]Analysis error: {e}[/red]")
        ctx.exit(1)


# Main CLI entry point with comprehensive error handling
def main() -> None:
    """Main CLI entry point with comprehensive error handling."""
    try:
        # Click CLI with proper argument handling
        # oracle_cli is decorated with @click.group() so it will parse sys.argv automatically
        oracle_cli()  # Click handles sys.argv automatically
    except KeyboardInterrupt:
        # Use simple print for keyboard interrupt without depending on app instance
        print("\n[yellow]Oracle CLI operation cancelled by user[/yellow]")
        raise SystemExit(130) from None
    except Exception as e:
        # Use simple print for general errors without depending on app instance
        print(f"[bold red]Oracle CLI error: {e}[/bold red]")
        raise SystemExit(1) from e


if __name__ == "__main__":
    main()
