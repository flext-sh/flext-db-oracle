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
    "create_oracle_api",
    "create_oracle_connection",
    "flext_oracle_api",
    "oracle_api",
    "oracle_authentication_error",
    "oracle_config",
    "oracle_configuration_error",
    "oracle_connection",
    "oracle_connection_error",
    "oracle_database",
    "oracle_error",
    "oracle_metadata",
    "oracle_metadata_error",
    "oracle_metadata_error_params",
    "oracle_processing_error",
    "oracle_query_error",
    "oracle_query_error_params",
    "oracle_timeout_error",
    "oracle_validation_error",
    "setup_oracle_database",
    "simple_oracle_connection",
]

FlextDbOracleMetadata = FlextDbOracleMetadataManager
FlextDbOracleConnectionInfo = FlextDbOracleConnectionStatus

def oracle_api(
    config: FlextDbOracleConfig | None = None, context_name: str = "oracle"
) -> FlextDbOracleApi: ...
def oracle_database(
    config: FlextDbOracleConfig | None = None, context_name: str = "oracle"
) -> FlextDbOracleApi: ...
def oracle_connection(
    config: FlextDbOracleConfig | None = None,
) -> FlextDbOracleConnection: ...
def oracle_config(**kwargs: object) -> FlextDbOracleConfig: ...
def oracle_metadata(
    connection: FlextDbOracleConnection | None = None,
) -> FlextDbOracleMetadataManager: ...
def oracle_error(
    message: str,
    *,
    code: object | None = None,
    context: Mapping[str, object] | None = None,
    **kwargs: object,
) -> FlextDbOracleError: ...
def oracle_connection_error(
    message: str,
    *,
    code: object | None = None,
    context: Mapping[str, object] | None = None,
    **kwargs: object,
) -> FlextDbOracleConnectionError: ...
def oracle_query_error(
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
def oracle_configuration_error(
    message: str,
    *,
    code: object | None = None,
    context: Mapping[str, object] | None = None,
    **kwargs: object,
) -> FlextDbOracleConfigurationError: ...
def oracle_validation_error(
    message: str,
    *,
    code: object | None = None,
    context: Mapping[str, object] | None = None,
    **kwargs: object,
) -> FlextDbOracleValidationError: ...
def oracle_timeout_error(
    message: str,
    *,
    code: object | None = None,
    context: Mapping[str, object] | None = None,
    **kwargs: object,
) -> FlextDbOracleTimeoutError: ...
def oracle_authentication_error(
    message: str,
    *,
    code: object | None = None,
    context: Mapping[str, object] | None = None,
    **kwargs: object,
) -> FlextDbOracleAuthenticationError: ...
def oracle_processing_error(
    message: str,
    *,
    code: object | None = None,
    context: Mapping[str, object] | None = None,
    **kwargs: object,
) -> FlextDbOracleProcessingError: ...
def oracle_metadata_error(
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
def flext_oracle_api(
    config: FlextDbOracleConfig | None = None, context_name: str = "oracle"
) -> FlextDbOracleApi: ...
def simple_oracle_connection(
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
def oracle_metadata_error_params(**kwargs: object) -> dict[str, object]: ...
def oracle_query_error_params(**kwargs: object) -> dict[str, object]: ...
