from dataclasses import dataclass
from typing import NoReturn, Protocol

import click
from _typeshed import Incomplete
from flext_core import FlextPlugin as FlextPlugin
from rich.console import Console

from flext_db_oracle.api import FlextDbOracleApi as FlextDbOracleApi
from flext_db_oracle.config import FlextDbOracleConfig as FlextDbOracleConfig
from flext_db_oracle.constants import ORACLE_DEFAULT_PORT as ORACLE_DEFAULT_PORT
from flext_db_oracle.plugins import (
    register_all_oracle_plugins as register_all_oracle_plugins,
)

def format_output(
    data: object, _format_type: str = "table", console: Console | None = None
) -> str: ...

console: Incomplete

class CliErrorHandler:
    def __init__(self, console: Console) -> None: ...
    def print_error(self, message: str) -> None: ...
    def print_error_exception(self, exception: Exception) -> None: ...
    def print_no_data_error(self, operation: str) -> None: ...
    def handle_no_data_error_with_exception(self, operation: str) -> NoReturn: ...
    def handle_operation_failure_with_exception(
        self, operation: str, error: str
    ) -> None: ...
    def raise_cli_error(self, message: str) -> NoReturn: ...
    def raise_cli_exception_from_exception(self, exception: Exception) -> NoReturn: ...

class CliDataValidator:
    @staticmethod
    def safe_get_test_data(
        test_data: dict[str, object] | None, key: str, default: object = None
    ) -> object: ...
    @staticmethod
    def safe_get_query_data_attr(
        query_data: object | None, attr: str, default: object = None
    ) -> object: ...
    @staticmethod
    def safe_iterate_list(data_list: list[str] | None) -> list[str]: ...
    @staticmethod
    def safe_iterate_dict(data_dict: dict[str, str] | None) -> dict[str, str]: ...
    @staticmethod
    def safe_get_list_length(obj: object) -> int: ...
    @staticmethod
    def extract_table_info(
        table_info: object, schema: str | None
    ) -> tuple[str, str]: ...

class ConfigProtocol(Protocol):
    output_format: str

class PluginProtocol(Protocol):
    name: str
    version: str

@dataclass
class ConnectionParams:
    host: str
    port: int
    service_name: str
    username: str
    password: str

@click.pass_context
def oracle(ctx: click.Context, profile: str, output: str, *, debug: bool) -> None: ...
@click.pass_context
def connect(ctx: click.Context, /, **connection_args: str | int) -> None: ...

class _ConnectionTestExecutor:
    ctx: Incomplete
    params: Incomplete
    config: Incomplete
    debug: Incomplete
    def __init__(self, ctx: click.Context, params: ConnectionParams) -> None: ...
    def execute(self) -> None: ...

@click.pass_context
def connect_env(ctx: click.Context, env_prefix: str) -> None: ...

class QueryResultProcessor:
    config: Incomplete
    console: Incomplete
    def __init__(self, config: ConfigProtocol, console: Console) -> None: ...
    def process_success(
        self, query_data: object, results: list[object], limit: int | None
    ) -> None: ...

@click.pass_context
def query(ctx: click.Context, sql: str, limit: int | None) -> None: ...
@click.pass_context
def schemas(ctx: click.Context) -> None: ...
@click.pass_context
def tables(ctx: click.Context, schema: str | None) -> None: ...

class PluginManagerProcessor:
    config: Incomplete
    console: Incomplete
    def __init__(self, config: ConfigProtocol, console: Console) -> None: ...
    def handle_registration_success(
        self, registration_results: dict[str, str]
    ) -> None: ...
    def handle_plugin_list_success(self, plugin_list: list[FlextPlugin]) -> None: ...

@click.pass_context
def plugins(ctx: click.Context) -> None: ...
@click.pass_context
def optimize(ctx: click.Context, sql: str) -> None: ...
@click.pass_context
def health(ctx: click.Context) -> None: ...
def main() -> None: ...
