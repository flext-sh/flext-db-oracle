from collections.abc import Iterator
from datetime import datetime
from typing import TypedDict

from _typeshed import Incomplete
from flext_core import FlextResult, FlextValueObject

from flext_db_oracle.metadata import (
    FlextDbOracleColumn as _FlextDbOracleColumn,
    FlextDbOracleSchema as _FlextDbOracleSchema,
    FlextDbOracleTable as _FlextDbOracleTable,
)

__all__ = [
    "FlextDbOracleColumn",
    "FlextDbOracleConnectionStatus",
    "FlextDbOracleQueryResult",
    "FlextDbOracleSchema",
    "FlextDbOracleTable",
    "TDbOracleColumn",
    "TDbOracleConnectionStatus",
    "TDbOracleQueryResult",
    "TDbOracleSchema",
    "TDbOracleTable",
]

FlextDbOracleColumn: Incomplete
FlextDbOracleTable: Incomplete
FlextDbOracleSchema: Incomplete
FlextDbOracleQueryResult: Incomplete
FlextDbOracleConnectionStatus: Incomplete

class TDbOracleQueryResult(FlextValueObject):
    columns: list[str]
    rows: list[tuple[object, ...]]
    row_count: int
    execution_time_ms: float
    query_hash: str | None
    @classmethod
    def validate_row_count(cls, v: int) -> int: ...
    @classmethod
    def validate_execution_time(cls, v: float) -> float: ...
    def validate_business_rules(self) -> FlextResult[None]: ...
    def validate_domain_rules(self) -> FlextResult[None]: ...
    def to_dict_list(self) -> list[dict[str, object]]: ...
    def __iter__(self) -> Iterator[tuple[object, ...]]: ...
    @property
    def is_empty(self) -> bool: ...
    def __len__(self) -> int: ...
    def get_column_values(self, column_name: str) -> FlextResult[list[object]]: ...

class TDbOracleConnectionStatus(FlextValueObject):
    is_connected: bool
    host: str
    port: int
    service_name: str
    username: str
    connection_time_ms: float | None
    last_error: str | None
    last_check: datetime | None
    database: str | None
    active_sessions: int
    max_sessions: int
    @classmethod
    def validate_host(cls, v: str) -> str: ...
    @classmethod
    def validate_port(cls, v: int) -> int: ...
    @classmethod
    def validate_service_name(cls, v: str) -> str: ...
    @classmethod
    def validate_username(cls, v: str) -> str: ...
    @classmethod
    def validate_active_sessions(cls, v: int) -> int: ...
    @classmethod
    def validate_max_sessions(cls, v: int) -> int: ...
    def validate_business_rules(self) -> FlextResult[None]: ...
    def validate_domain_rules(self) -> FlextResult[None]: ...
    def to_dict(
        self, *, by_alias: bool = True, exclude_none: bool = True
    ) -> dict[str, object]: ...
    @property
    def connection_string(self) -> str: ...
    @property
    def session_utilization_percent(self) -> float: ...
    def is_healthy(self) -> bool: ...

class TDbOracleColumn(_FlextDbOracleColumn):
    def __init__(self, **kwargs: object) -> None: ...

class TDbOracleTable(_FlextDbOracleTable):
    def __init__(self, **kwargs: object) -> None: ...

class TDbOracleSchema(_FlextDbOracleSchema):
    def __init__(self, **kwargs: object) -> None: ...

FlextDbOracleQueryResult = TDbOracleQueryResult
FlextDbOracleConnectionStatus = TDbOracleConnectionStatus

class OracleColumnInfo(TypedDict, total=False):
    column_name: str
    data_type: str
    nullable: bool
    data_length: int | None
    data_precision: int | None
    data_scale: int | None
    column_id: int
    default_value: str | None
    comments: str | None
