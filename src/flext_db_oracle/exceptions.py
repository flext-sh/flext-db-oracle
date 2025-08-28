"""Oracle Database Exception Hierarchy following Flext[Area][Module] pattern.

This module provides Oracle-specific exceptions using modern patterns from flext-core.
Single class inheriting from FlextExceptions with all Oracle exception functionality
as delegated methods, following SOLID principles, PEP8, Python 3.13+, and FLEXT
structural patterns.

All exception functionality is delegated to flext-core base classes.
ZERO local BaseError classes - complete elimination of duplication.

Copyright (c) 2025 FLEXT Contributors
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from collections.abc import Mapping
from enum import Enum

from flext_core import (
    FlextExceptions,
    # FlextExceptions,  # Not available in flext-core
    FlextProcessingError,
)

# =============================================================================
# FLEXT[AREA][MODULE] PATTERN - Oracle Database Exceptions
# =============================================================================


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
        """Oracle validation error - uses standard ValueError."""

        def __init__(
            self,
            message: str,
            *,
            code: str | None = None,
            context: dict[str, object] | None = None,
        ) -> None:
            """Initialize Oracle validation error via flext-core."""
            # ValueError only accepts message - store additional info as instance attributes
            super().__init__(message)
            self.error_code = code or "ORACLE_VALIDATION_ERROR"
            self.context = context or {}

    class ConfigurationError(FlextExceptions):
        """Oracle configuration error - delegates to FlextExceptions."""

        def __init__(
            self,
            message: str,
            *,
            code: str | None = None,
            context: dict[str, object] | None = None,
        ) -> None:
            """Initialize Oracle configuration error via flext-core."""
            resolved_code = code or "ORACLE_CONFIGURATION_ERROR"
            super().__init__(message, error_code=resolved_code, context=context)

    class DatabaseConnectionError(FlextExceptions):
        """Oracle database connection error - delegates to FlextExceptions."""

        def __init__(
            self,
            message: str,
            *,
            code: str | None = None,
            context: dict[str, object] | None = None,
        ) -> None:
            """Initialize Oracle connection error via flext-core."""
            resolved_code = code or "ORACLE_CONNECTION_ERROR"
            super().__init__(message, error_code=resolved_code, context=context)

    class ProcessingError(FlextProcessingError):
        """Oracle processing error - delegates to FlextProcessingError."""

        def __init__(
            self,
            message: str,
            *,
            code: str | None = None,
            context: dict[str, object] | None = None,
        ) -> None:
            """Initialize Oracle processing error via flext-core."""
            resolved_code = code or "ORACLE_PROCESSING_ERROR"
            super().__init__(message, error_code=resolved_code, context=context)

    class AuthenticationError(FlextExceptions):
        """Oracle authentication error - delegates to FlextExceptions."""

        def __init__(
            self,
            message: str,
            *,
            code: str | None = None,
            context: dict[str, object] | None = None,
        ) -> None:
            """Initialize Oracle authentication error via flext-core."""
            resolved_code = code or "ORACLE_AUTHENTICATION_ERROR"
            super().__init__(message, error_code=resolved_code, context=context)

    class DatabaseTimeoutError(FlextExceptions):
        """Oracle database timeout error - delegates to FlextExceptions."""

        def __init__(
            self,
            message: str,
            *,
            code: str | None = None,
            context: dict[str, object] | None = None,
        ) -> None:
            """Initialize Oracle timeout error via flext-core."""
            resolved_code = code or "ORACLE_TIMEOUT_ERROR"
            super().__init__(message, error_code=resolved_code, context=context)

    class QueryError(FlextExceptions):
        """Oracle query error - delegates to FlextExceptions with SQL context."""

        def __init__(
            self,
            message: str,
            *,
            query: str | None = None,
            operation: str | None = None,
            execution_time: float | None = None,
            rows_affected: int | None = None,
            code: object | None = None,
            context: Mapping[str, object] | None = None,
        ) -> None:
            """Initialize Oracle query error with SQL context via flext-core."""
            context_dict: dict[str, object] = dict(context) if context else {}

            if query is not None:
                # Truncate long queries for safety and readability
                max_query_length = 200
                context_dict["query"] = (
                    query[:max_query_length] + "..."
                    if len(query) > max_query_length
                    else query
                )
            if operation is not None:
                context_dict["operation"] = operation
            if execution_time is not None:
                context_dict["execution_time"] = execution_time
            if rows_affected is not None:
                context_dict["rows_affected"] = rows_affected

            error_code = "ORACLE_QUERY_ERROR" if code is None else str(code)
            super().__init__(message, error_code=error_code, context=context_dict)

    class MetadataError(FlextExceptions):
        """Oracle metadata error - delegates to FlextExceptions with schema context."""

        def __init__(
            self,
            message: str,
            *,
            schema_name: str | None = None,
            object_name: str | None = None,
            object_type: str | None = None,
            operation: str | None = None,
            code: object | None = None,
            context: Mapping[str, object] | None = None,
        ) -> None:
            """Initialize Oracle metadata error with schema context via flext-core."""
            context_dict: dict[str, object] = dict(context) if context else {}

            if schema_name is not None:
                context_dict["schema_name"] = schema_name
            if object_name is not None:
                context_dict["object_name"] = object_name
            if object_type is not None:
                context_dict["object_type"] = object_type
            if operation is not None:
                context_dict["operation"] = operation

            error_code = "ORACLE_METADATA_ERROR" if code is None else str(code)
            super().__init__(message, error_code=error_code, context=context_dict)

    class ConnectionOperationError(ConnectionError):
        """Oracle connection operation error - inherits from Oracle ConnectionError."""

        def __init__(
            self,
            message: str,
            *,
            host: str | None = None,
            port: int | None = None,
            service_name: str | None = None,
            username: str | None = None,
            connection_timeout: float | None = None,
            code: str | None = None,
            context: Mapping[str, object] | None = None,
        ) -> None:
            """Initialize Oracle connection operation error with connection context."""
            context_dict: dict[str, object] = dict(context) if context else {}

            if host is not None:
                context_dict["host"] = host
            if port is not None:
                context_dict["port"] = port
            if service_name is not None:
                context_dict["service_name"] = service_name
            if username is not None:
                context_dict["username"] = username
            if connection_timeout is not None:
                context_dict["connection_timeout"] = connection_timeout

            # Store error code for potential future use
            _ = (
                code
                or FlextDbOracleExceptions.OracleErrorCodes.ORACLE_CONNECTION_ERROR.value
            )
            super().__init__(message)

    # =============================================================================
    # Factory Methods for Exception Creation
    # =============================================================================

    @classmethod
    def create_oracle_error(
        cls,
        message: str,
        *,
        code: str | None = None,
        context: dict[str, object] | None = None,
    ) -> FlextExceptions:
        """Create Oracle database error using factory pattern."""
        from flext_core import FlextExceptions

        return FlextExceptions(
            message, error_code=code or "ORACLE_ERROR", context=context
        )

    @classmethod
    def create_connection_error(
        cls,
        message: str,
        *,
        context: dict[str, object] | None = None,
    ) -> DatabaseConnectionError:
        """Create Oracle connection error using factory pattern."""
        return cls.DatabaseConnectionError(
            message,
            code=cls.OracleErrorCodes.ORACLE_CONNECTION_ERROR.value,
            context=context,
        )

    @classmethod
    def create_validation_error(
        cls,
        message: str,
        *,
        context: dict[str, object] | None = None,
    ) -> ValidationError:
        """Create Oracle validation error using factory pattern."""
        return cls.ValidationError(
            message,
            code=cls.OracleErrorCodes.ORACLE_VALIDATION_ERROR.value,
            context=context,
        )

    @classmethod
    def create_configuration_error(
        cls,
        message: str,
        *,
        context: dict[str, object] | None = None,
    ) -> ConfigurationError:
        """Create Oracle configuration error using factory pattern."""
        return cls.ConfigurationError(
            message,
            code=cls.OracleErrorCodes.ORACLE_CONFIGURATION_ERROR.value,
            context=context,
        )

    @classmethod
    def create_query_error(
        cls,
        message: str,
        *,
        context: dict[str, object] | None = None,
    ) -> QueryError:
        """Create Oracle query error using factory pattern."""
        return cls.QueryError(
            message,
            code=cls.OracleErrorCodes.ORACLE_QUERY_ERROR,
            context=context,
        )

    @classmethod
    def create_metadata_error(
        cls,
        message: str,
        *,
        context: dict[str, object] | None = None,
    ) -> MetadataError:
        """Create Oracle metadata error using factory pattern."""
        return cls.MetadataError(
            message,
            code=cls.OracleErrorCodes.ORACLE_METADATA_ERROR,
            context=context,
        )

    @classmethod
    def create_authentication_error(
        cls,
        message: str,
        *,
        context: dict[str, object] | None = None,
    ) -> AuthenticationError:
        """Create Oracle authentication error using factory pattern."""
        return cls.AuthenticationError(
            message,
            code=cls.OracleErrorCodes.ORACLE_AUTHENTICATION_ERROR.value,
            context=context,
        )

    @classmethod
    def create_timeout_error(
        cls,
        message: str,
        *,
        context: dict[str, object] | None = None,
    ) -> DatabaseTimeoutError:
        """Create Oracle timeout error using factory pattern."""
        return cls.DatabaseTimeoutError(
            message,
            code=cls.OracleErrorCodes.ORACLE_TIMEOUT_ERROR.value,
            context=context,
        )

    @classmethod
    def create_processing_error(
        cls,
        message: str,
        *,
        context: dict[str, object] | None = None,
    ) -> ProcessingError:
        """Create Oracle processing error using factory pattern."""
        return cls.ProcessingError(
            message,
            code=cls.OracleErrorCodes.ORACLE_PROCESSING_ERROR.value,
            context=context,
        )

    @classmethod
    def get_available_error_codes(cls) -> list[OracleErrorCodes]:
        """Get all available Oracle error codes."""
        return list(cls.OracleErrorCodes)

    @classmethod
    def is_oracle_error(cls, error: Exception) -> bool:
        """Check if exception is an Oracle database error."""
        return isinstance(error, FlextExceptions)

    # =============================================================================
    # Backward Compatibility Aliases
    # =============================================================================

    # Maintain existing functionality as aliases
    # BaseError was removed - use FlextExceptions from flext-core directly
    from flext_core import FlextExceptions

    FlextDbOracleError = FlextExceptions
    FlextDbOracleValidationError = ValidationError
    FlextDbOracleConfigurationError = ConfigurationError
    FlextDbOracleConnectionError = DatabaseConnectionError
    FlextDbOracleProcessingError = ProcessingError
    FlextDbOracleAuthenticationError = AuthenticationError
    FlextDbOracleTimeoutError = DatabaseTimeoutError
    FlextDbOracleQueryError = QueryError
    FlextDbOracleMetadataError = MetadataError
    FlextDbOracleConnectionOperationError = ConnectionOperationError
    FlextDbOracleOracleErrorCodes = OracleErrorCodes


# Export API - ONLY single class with backward compatibility
__all__: list[str] = [
    "FlextDbOracleAuthenticationError",
    "FlextDbOracleConfigurationError",
    "FlextDbOracleConnectionError",
    "FlextDbOracleConnectionOperationError",
    "FlextDbOracleError",
    "FlextDbOracleExceptions",
    "FlextDbOracleMetadataError",
    "FlextDbOracleOracleErrorCodes",
    "FlextDbOracleProcessingError",
    "FlextDbOracleQueryError",
    "FlextDbOracleTimeoutError",
    "FlextDbOracleValidationError",
]

# Create backward compatibility module-level aliases
# BaseError was removed - use FlextExceptions from flext-core directly
FlextDbOracleError = FlextExceptions
FlextDbOracleValidationError = FlextDbOracleExceptions.ValidationError
FlextDbOracleConfigurationError = FlextDbOracleExceptions.ConfigurationError
FlextDbOracleConnectionError = FlextDbOracleExceptions.DatabaseConnectionError
FlextDbOracleProcessingError = FlextDbOracleExceptions.ProcessingError
FlextDbOracleAuthenticationError = FlextDbOracleExceptions.AuthenticationError
FlextDbOracleTimeoutError = FlextDbOracleExceptions.DatabaseTimeoutError
FlextDbOracleQueryError = FlextDbOracleExceptions.QueryError
FlextDbOracleMetadataError = FlextDbOracleExceptions.MetadataError
FlextDbOracleConnectionOperationError = FlextDbOracleExceptions.ConnectionOperationError
FlextDbOracleOracleErrorCodes = FlextDbOracleExceptions.OracleErrorCodes
