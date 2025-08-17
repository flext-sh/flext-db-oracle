from collections.abc import Mapping
from enum import Enum

from flext_core import FlextError
from flext_core.exceptions import FlextErrorMixin

__all__ = [
    "FlextDbOracleAuthenticationError",
    "FlextDbOracleConfigurationError",
    "FlextDbOracleConnectionError",
    "FlextDbOracleConnectionOperationError",
    "FlextDbOracleError",
    "FlextDbOracleErrorCodes",
    "FlextDbOracleMetadataError",
    "FlextDbOracleProcessingError",
    "FlextDbOracleQueryError",
    "FlextDbOracleTimeoutError",
    "FlextDbOracleValidationError",
]

class FlextDbOracleErrorCodes(Enum):
    ORACLE_ERROR = "ORACLE_ERROR"
    ORACLE_VALIDATION_ERROR = "ORACLE_VALIDATION_ERROR"
    ORACLE_CONFIGURATION_ERROR = "ORACLE_CONFIGURATION_ERROR"
    ORACLE_CONNECTION_ERROR = "ORACLE_CONNECTION_ERROR"
    ORACLE_PROCESSING_ERROR = "ORACLE_PROCESSING_ERROR"
    ORACLE_AUTHENTICATION_ERROR = "ORACLE_AUTHENTICATION_ERROR"
    ORACLE_TIMEOUT_ERROR = "ORACLE_TIMEOUT_ERROR"
    ORACLE_QUERY_ERROR = "ORACLE_QUERY_ERROR"
    ORACLE_METADATA_ERROR = "ORACLE_METADATA_ERROR"

class FlextDbOracleError(FlextError, FlextErrorMixin): ...
class FlextDbOracleValidationError(FlextDbOracleError): ...
class FlextDbOracleConfigurationError(FlextDbOracleError): ...
class FlextDbOracleConnectionError(FlextDbOracleError): ...
class FlextDbOracleProcessingError(FlextDbOracleError): ...
class FlextDbOracleAuthenticationError(FlextDbOracleError): ...
class FlextDbOracleTimeoutError(FlextDbOracleError): ...

class FlextDbOracleQueryError(FlextDbOracleError):
    def __init__(
        self,
        message: str,
        *,
        query: str | None = None,
        operation: str | None = None,
        execution_time: float | None = None,
        rows_affected: int | None = None,
        code: FlextDbOracleErrorCodes | None = ...,
        context: Mapping[str, object] | None = None,
    ) -> None: ...

class FlextDbOracleMetadataError(FlextDbOracleError):
    def __init__(
        self,
        message: str,
        *,
        schema_name: str | None = None,
        object_name: str | None = None,
        object_type: str | None = None,
        operation: str | None = None,
        code: FlextDbOracleErrorCodes | None = ...,
        context: Mapping[str, object] | None = None,
    ) -> None: ...

class FlextDbOracleConnectionOperationError(FlextDbOracleConnectionError):
    def __init__(
        self,
        message: str,
        *,
        host: str | None = None,
        port: int | None = None,
        service_name: str | None = None,
        username: str | None = None,
        connection_timeout: float | None = None,
        code: FlextDbOracleErrorCodes | None = ...,
        context: Mapping[str, object] | None = None,
    ) -> None: ...
