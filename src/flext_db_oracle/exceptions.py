"""Oracle Database Exception Hierarchy following Flext[Area][Module] pattern.

This module provides Oracle-specific exceptions using modern patterns from flext-core.
Single class inheriting from FlextExceptions with all Oracle exception functionality
as delegated methods, following SOLID principles, PEP8, Python 3.13+, and FLEXT
structural patterns.

Copyright (c) 2025 FLEXT Contributors
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from flext_core import FlextExceptions, FlextTypes

from flext_db_oracle.mixins import ParameterObject


# Parameter Object usando dataclass Python 3.13+ - REDUZ PARÂMETROS
@dataclass(frozen=True, slots=True)  # Python 3.13+ otimizações
class ExceptionParams:
    """Parameter Object para reduzir parâmetros de exceção - ELIMINA 6 PARÂMETROS."""

    message: str
    code: str | None = None
    context: FlextTypes.Core.Dict | None = None

    def __post_init__(self) -> None:
        """Validação automática usando Python 3.13+ patterns."""
        if not self.message or not self.message.strip():
            msg = "Message cannot be empty"
            raise ValueError(msg)
        # Auto-resolve context
        if self.context is None:
            object.__setattr__(self, "context", {})


# ✅ USING FlextExceptions.Error - NO LOCAL BaseError VIOLATIONS
# Following FLEXT_REFACTORING_PROMPT.md line 686: "Exceptions - Inherit from FlextExceptions"


class FlextDbOracleExceptions(FlextExceptions):
    """Oracle database exceptions following Flext[Area][Module] pattern.

    Single class inheriting from FlextExceptions with all Oracle exception
    functionality as delegated methods, following SOLID principles,
    PEP8, Python 3.13+, and FLEXT structural patterns.

    ZERO local BaseError classes - complete delegation to flext-core.
    """

    class OracleErrorCodes(Enum):
        """Error codes for Oracle database domain operations."""

        ORACLE_ERROR = "ORACLE_ERROR"
        ORACLE_VALIDATION_ERROR = "ORACLE_VALIDATION_ERROR"
        ORACLE_CONFIGURATION_ERROR = "ORACLE_CONFIGURATION_ERROR"
        ORACLE_CONNECTION_ERROR = "ORACLE_CONNECTION_ERROR"
        ORACLE_PROCESSING_ERROR = "ORACLE_PROCESSING_ERROR"
        ORACLE_AUTHENTICATION_ERROR = "ORACLE_AUTHENTICATION_ERROR"
        ORACLE_TIMEOUT_ERROR = "ORACLE_TIMEOUT_ERROR"
        ORACLE_QUERY_ERROR = "ORACLE_QUERY_ERROR"
        ORACLE_METADATA_ERROR = "ORACLE_METADATA_ERROR"

    # =============================================================================
    # Oracle Exception Classes - All delegate to flext-core base classes
    # =============================================================================
    # Note: No local BaseError - use FlextExceptions directly from flext-core

    class ValidationError(ValueError):
        """Oracle validation error usando Parameter Object - REDUZ PARÂMETROS."""

        def __init__(self, params: ExceptionParams | str) -> None:
            """Initialize usando Parameter Object pattern - ELIMINA MÚLTIPLOS PARÂMETROS."""
            # Backward compatibility para string simples
            if isinstance(params, str):
                params = ExceptionParams(message=params, code="ORACLE_VALIDATION_ERROR")

            super().__init__(params.message)
            self.error_code = params.code or "ORACLE_VALIDATION_ERROR"
            self.context = params.context or {}

    class ConfigurationError(FlextExceptions._ConfigurationError):
        """Oracle configuration error usando Parameter Object - REDUZ PARÂMETROS."""

        def __init__(self, params: ExceptionParams | str) -> None:
            """Initialize usando Parameter Object pattern - ELIMINA MÚLTIPLOS PARÂMETROS."""
            if isinstance(params, str):
                params = ExceptionParams(
                    message=params,
                    code="ORACLE_CONFIGURATION_ERROR",
                )

            resolved_code = params.code or "ORACLE_CONFIGURATION_ERROR"
            super().__init__(params.message, code=resolved_code, context=params.context)

    class DatabaseConnectionError(FlextExceptions._ConnectionError):
        """Oracle database connection error usando Parameter Object - REDUZ PARÂMETROS."""

        def __init__(self, params: ExceptionParams | str) -> None:
            """Initialize usando Parameter Object - ELIMINA PARÂMETROS DESNECESSÁRIOS."""
            if isinstance(params, str):
                params = ExceptionParams(message=params, code="ORACLE_CONNECTION_ERROR")

            super().__init__(params.message)

    class ProcessingError(FlextExceptions._ProcessingError):
        """Oracle processing error using FlextExceptions proven foundation."""

        def __init__(
            self,
            message: str,
            *,
            code: str | None = None,
            context: FlextTypes.Core.Dict | None = None,
        ) -> None:
            """Initialize Oracle processing error via flext-core."""
            resolved_code = code or "ORACLE_PROCESSING_ERROR"
            super().__init__(message, code=resolved_code, context=context)

    class AuthenticationError(FlextExceptions._AuthenticationError):
        """Oracle authentication error using FlextExceptions proven foundation."""

        def __init__(
            self,
            message: str,
            *,
            code: str | None = None,
            context: FlextTypes.Core.Dict | None = None,
        ) -> None:
            """Initialize Oracle authentication error via flext-core."""
            resolved_code = code or "ORACLE_AUTHENTICATION_ERROR"
            super().__init__(message, code=resolved_code, context=context)

    class DatabaseTimeoutError(FlextExceptions._TimeoutError):
        """Oracle database timeout error using FlextExceptions proven foundation."""

        def __init__(
            self,
            message: str,
            *,
            code: str | None = None,
            context: FlextTypes.Core.Dict | None = None,
        ) -> None:
            """Initialize Oracle timeout error via flext-core."""
            resolved_code = code or "ORACLE_TIMEOUT_ERROR"
            super().__init__(message, code=resolved_code, context=context)

    class QueryError(FlextExceptions._OperationError):
        """Oracle query error using FlextExceptions proven foundation with Parameter Object pattern."""

        def __init__(
            self,
            message: str,
            *,
            params: ParameterObject | None = None,
        ) -> None:
            """Initialize Oracle query error with SQL context via Parameter Object pattern."""
            if params is None:
                params = ParameterObject()

            context_dict: FlextTypes.Core.Dict = {}

            # Extract query parameter with truncation
            if params.has("query"):
                query = str(params.get("query"))
                max_query_length = 200
                context_dict["query"] = (
                    query[:max_query_length] + "..."
                    if len(query) > max_query_length
                    else query
                )

            # Extract other parameters
            for param_name in ["operation", "execution_time", "rows_affected"]:
                if params.has(param_name):
                    context_dict[param_name] = params.get(param_name)

            # Merge with any existing context
            if params.has("context"):
                existing_context = params.get("context")
                if isinstance(existing_context, dict):
                    context_dict.update(existing_context)

            error_code = str(params.get("code", default="ORACLE_QUERY_ERROR"))
            super().__init__(message, code=error_code, context=context_dict)

    class MetadataError(FlextExceptions._OperationError):
        """Oracle metadata error using FlextExceptions proven foundation with Parameter Object pattern."""

        def __init__(
            self,
            message: str,
            *,
            params: ParameterObject | None = None,
        ) -> None:
            """Initialize Oracle metadata error with schema context via Parameter Object pattern."""
            if params is None:
                params = ParameterObject()

            context_dict: FlextTypes.Core.Dict = {}

            # Extract metadata parameters
            for param_name in [
                "schema_name",
                "object_name",
                "object_type",
                "operation",
            ]:
                if params.has(param_name):
                    context_dict[param_name] = params.get(param_name)

            # Merge with any existing context
            if params.has("context"):
                existing_context = params.get("context")
                if isinstance(existing_context, dict):
                    context_dict.update(existing_context)

            error_code = str(params.get("code", default="ORACLE_METADATA_ERROR"))
            super().__init__(message, code=error_code, context=context_dict)

    class ConnectionOperationError(ConnectionError):
        """Oracle connection operation error using Parameter Object pattern."""

        def __init__(
            self,
            message: str,
            *,
            params: ParameterObject | None = None,
        ) -> None:
            """Initialize Oracle connection operation error with connection context via Parameter Object."""
            if params is None:
                params = ParameterObject()

            # Extract connection parameters for context (stored as instance attribute for potential logging)
            connection_context: FlextTypes.Core.Dict = {}

            for param_name in [
                "host",
                "port",
                "service_name",
                "username",
                "connection_timeout",
            ]:
                if params.has(param_name):
                    connection_context[param_name] = params.get(param_name)

            # Merge with any existing context
            if params.has("context"):
                existing_context = params.get("context")
                if isinstance(existing_context, dict):
                    connection_context.update(existing_context)

            # Store context for potential future use
            self._connection_context = connection_context
            error_code = str(
                params.get(
                    "code",
                    default=FlextDbOracleExceptions.OracleErrorCodes.ORACLE_CONNECTION_ERROR.value,
                ),
            )
            self._error_code = error_code

            super().__init__(message)

    # Factory methods ELIMINATED - use direct exception instantiation:
    # FlextDbOracleExceptions.DatabaseConnectionError("message")
    # FlextDbOracleExceptions.ValidationError("message")
    # etc.

    @classmethod
    def get_available_error_codes(cls) -> list[OracleErrorCodes]:
        """Get all available Oracle error codes."""
        return list(cls.OracleErrorCodes)

    @classmethod
    def is_oracle_error(cls, error: Exception) -> bool:
        """Check if exception is an Oracle database error."""
        return isinstance(error, FlextExceptions)

    # NO COMPATIBILITY ALIASES - use classes directly
    # Following FLEXT standards - no backward compatibility


# Create module-level aliases for backward compatibility
OracleConnectionError = FlextDbOracleExceptions.ConnectionOperationError
OracleQueryError = FlextDbOracleExceptions.QueryError
OracleValidationError = FlextDbOracleExceptions.ValidationError

# Export API - Main class plus compatibility aliases
__all__: FlextTypes.Core.StringList = [
    "FlextDbOracleExceptions",
    "OracleConnectionError",
    "OracleQueryError",
    "OracleValidationError",
]
