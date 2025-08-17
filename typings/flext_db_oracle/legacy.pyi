from collections.abc import Mapping

from flext_db_oracle.api import FlextDbOracleApi
from flext_db_oracle.config import FlextDbOracleConfig
from flext_db_oracle.connection import FlextDbOracleConnection
from flext_db_oracle.exceptions import (
    FlextDbOracleAuthenticationError,
    FlextDbOracleConfigurationError,
    FlextDbOracleConnectionError,
    FlextDbOracleError,
    FlextDbOracleMetadataError,
    FlextDbOracleProcessingError,
    FlextDbOracleQueryError,
    FlextDbOracleTimeoutError,
    FlextDbOracleValidationError,
)
from flext_db_oracle.metadata import FlextDbOracleMetadataManager
from flext_db_oracle.types import FlextDbOracleConnectionStatus

__all__ = [
    "FlextOracleApi",
    "OracleApi",
    "OracleAuthenticationError",
    "OracleConfig",
    "OracleConfigurationError",
    "OracleConnection",
    "OracleConnectionError",
    "OracleDatabase",
    "OracleError",
    "OracleMetadata",
    "OracleMetadataError",
    "OracleMetadataErrorParams",
    "OracleProcessingError",
    "OracleQueryError",
    "OracleQueryErrorParams",
    "OracleTimeoutError",
    "OracleValidationError",
    "SimpleOracleConnection",
    "create_oracle_api",
    "create_oracle_connection",
    "setup_oracle_database",
]

FlextDbOracleMetadata = FlextDbOracleMetadataManager
FlextDbOracleConnectionInfo = FlextDbOracleConnectionStatus

def OracleApi(
    config: FlextDbOracleConfig | None = None, context_name: str = "oracle"
) -> FlextDbOracleApi: ...
def OracleDatabase(
    config: FlextDbOracleConfig | None = None, context_name: str = "oracle"
) -> FlextDbOracleApi: ...
def OracleConnection(
    config: FlextDbOracleConfig | None = None,
) -> FlextDbOracleConnection: ...
def OracleConfig(**kwargs: object) -> FlextDbOracleConfig: ...
def OracleMetadata(
    connection: FlextDbOracleConnection | None = None,
) -> FlextDbOracleMetadataManager: ...
def OracleError(
    message: str,
    *,
    code: object | None = None,
    context: Mapping[str, object] | None = None,
    **kwargs: object,
) -> FlextDbOracleError: ...
def OracleConnectionError(
    message: str,
    *,
    code: object | None = None,
    context: Mapping[str, object] | None = None,
    **kwargs: object,
) -> FlextDbOracleConnectionError: ...
def OracleQueryError(
    message: str,
    *,
    query: str | None = None,
    operation: str | None = None,
    execution_time: float | None = None,
    rows_affected: int | None = None,
    code: object | None = None,
    context: Mapping[str, object] | None = None,
    **kwargs: object,
) -> FlextDbOracleQueryError: ...
def OracleConfigurationError(
    message: str,
    *,
    code: object | None = None,
    context: Mapping[str, object] | None = None,
    **kwargs: object,
) -> FlextDbOracleConfigurationError: ...
def OracleValidationError(
    message: str,
    *,
    code: object | None = None,
    context: Mapping[str, object] | None = None,
    **kwargs: object,
) -> FlextDbOracleValidationError: ...
def OracleTimeoutError(
    message: str,
    *,
    code: object | None = None,
    context: Mapping[str, object] | None = None,
    **kwargs: object,
) -> FlextDbOracleTimeoutError: ...
def OracleAuthenticationError(
    message: str,
    *,
    code: object | None = None,
    context: Mapping[str, object] | None = None,
    **kwargs: object,
) -> FlextDbOracleAuthenticationError: ...
def OracleProcessingError(
    message: str,
    *,
    code: object | None = None,
    context: Mapping[str, object] | None = None,
    **kwargs: object,
) -> FlextDbOracleProcessingError: ...
def OracleMetadataError(
    message: str,
    *,
    schema_name: str | None = None,
    object_name: str | None = None,
    object_type: str | None = None,
    operation: str | None = None,
    code: object | None = None,
    context: Mapping[str, object] | None = None,
    **kwargs: object,
) -> FlextDbOracleMetadataError: ...
def FlextOracleApi(
    config: FlextDbOracleConfig | None = None, context_name: str = "oracle"
) -> FlextDbOracleApi: ...
def SimpleOracleConnection(
    config: FlextDbOracleConfig | None = None,
) -> FlextDbOracleConnection: ...
def create_oracle_connection(
    config: FlextDbOracleConfig | None = None,
) -> FlextDbOracleConnection: ...
def create_oracle_api(
    config: FlextDbOracleConfig | None = None, context_name: str = "oracle"
) -> FlextDbOracleApi: ...
def setup_oracle_database(
    config: FlextDbOracleConfig | None = None, context_name: str = "oracle"
) -> FlextDbOracleApi: ...
def OracleMetadataErrorParams(**kwargs: object) -> dict[str, object]: ...
def OracleQueryErrorParams(**kwargs: object) -> dict[str, object]: ...
