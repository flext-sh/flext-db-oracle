from collections.abc import Generator
from contextlib import contextmanager

from _typeshed import Incomplete
from flext_core import FlextResult, FlextValueObject
from sqlalchemy.orm import Session

from flext_db_oracle.config import FlextDbOracleConfig
from flext_db_oracle.config_types import MergeStatementConfig

__all__ = ["FlextDbOracleConnection"]

class CreateIndexConfig(FlextValueObject):
    index_name: str
    table_name: str
    columns: list[str]
    schema_name: str | None
    unique: bool
    tablespace: str | None
    parallel: int | None
    @classmethod
    def validate_index_name(cls, v: str) -> str: ...
    @classmethod
    def validate_table_name(cls, v: str) -> str: ...
    @classmethod
    def validate_columns(cls, v: list[str]) -> list[str]: ...
    @classmethod
    def validate_parallel(cls, v: int | None) -> int | None: ...
    def validate_business_rules(self) -> FlextResult[None]: ...

class FlextDbOracleConnection:
    config: Incomplete
    def __init__(self, config: FlextDbOracleConfig) -> None: ...
    def connect(self) -> FlextResult[bool]: ...
    def disconnect(self) -> FlextResult[bool]: ...
    def is_connected(self) -> bool: ...
    def execute(
        self, sql: str, parameters: dict[str, object] | None = None
    ) -> FlextResult[list[object]]: ...
    def execute_many(
        self, sql: str, parameters_list: list[dict[str, object]]
    ) -> FlextResult[int]: ...
    def fetch_one(
        self, sql: str, parameters: dict[str, object] | None = None
    ) -> FlextResult[object]: ...
    @contextmanager
    def session(self) -> Generator[Session]: ...
    @contextmanager
    def transaction(self) -> Generator[object]: ...
    def close(self) -> FlextResult[None]: ...
    def execute_query(
        self, sql: str, parameters: dict[str, object] | None = None
    ) -> FlextResult[list[object]]: ...
    def test_connection(self) -> FlextResult[bool]: ...
    def get_table_names(
        self, schema_name: str | None = None
    ) -> FlextResult[list[str]]: ...
    def get_schemas(self) -> FlextResult[list[str]]: ...
    def get_current_schema(self) -> FlextResult[str]: ...
    def get_column_info(
        self, table_name: str, schema_name: str | None = None
    ) -> FlextResult[list[dict[str, object]]]: ...
    def get_primary_key_columns(
        self, table_name: str, schema_name: str | None = None
    ) -> FlextResult[list[str]]: ...
    def get_table_metadata(
        self, table_name: str, schema_name: str | None = None
    ) -> FlextResult[dict[str, object]]: ...
    def build_select(
        self,
        table_name: str,
        columns: list[str] | None = None,
        conditions: dict[str, object] | None = None,
        schema_name: str | None = None,
    ) -> FlextResult[str]: ...
    def build_select_safe(
        self,
        table_name: str,
        columns: list[str] | None = None,
        conditions: dict[str, object] | None = None,
        schema_name: str | None = None,
    ) -> FlextResult[tuple[str, dict[str, object]]]: ...
    def create_table_ddl(
        self,
        table_name: str,
        columns: list[dict[str, object]],
        schema_name: str | None = None,
    ) -> FlextResult[str]: ...
    def drop_table_ddl(
        self, table_name: str, schema_name: str | None = None
    ) -> FlextResult[str]: ...
    def execute_ddl(self, ddl: str) -> FlextResult[bool]: ...
    def convert_singer_type(
        self, singer_type: str | list[str], format_hint: str | None = None
    ) -> FlextResult[str]: ...
    def map_singer_schema(
        self, singer_schema: dict[str, object]
    ) -> FlextResult[dict[str, str]]: ...
    def build_insert_statement(
        self,
        table_name: str,
        columns: list[str],
        schema_name: str | None = None,
        returning_columns: list[str] | None = None,
        hints: list[str] | None = None,
    ) -> FlextResult[str]: ...
    def build_update_statement(
        self,
        table_name: str,
        set_columns: list[str],
        where_columns: list[str],
        schema_name: str | None = None,
        returning_columns: list[str] | None = None,
    ) -> FlextResult[str]: ...
    def build_merge_statement(
        self, config: MergeStatementConfig
    ) -> FlextResult[str]: ...
    def build_delete_statement(
        self, table_name: str, where_columns: list[str], schema_name: str | None = None
    ) -> FlextResult[str]: ...
    def build_create_index_statement(
        self, config: CreateIndexConfig
    ) -> FlextResult[str]: ...
