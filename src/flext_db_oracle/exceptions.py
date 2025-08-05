"""Oracle Database exception hierarchy using flext-core DRY patterns.

Domain-specific exceptions using factory pattern to eliminate 150+ lines of duplication.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from flext_core.exceptions import (
    FlextAuthenticationError,
    FlextConfigurationError,
    FlextConnectionError,
    FlextError,
    FlextProcessingError,
    FlextTimeoutError,
    FlextValidationError,
)


# SOLID Implementation: Explicit exception classes with proper inheritance
class FlextDbOracleError(FlextError):
    """Base exception for Oracle database operations."""

    def __init__(
        self,
        message: str = "Oracle database error",
        *,
        error_code: str | None = None,
        **kwargs: object,
    ) -> None:
        """Initialize Oracle database error with context."""
        formatted_message = f"Oracle DB: {message}"
        context = dict(kwargs)
        super().__init__(formatted_message, error_code=error_code, context=context)


class FlextDbOracleValidationError(FlextValidationError):
    """Oracle database validation errors."""

    def __init__(
        self,
        message: str = "Oracle database validation failed",
        *,
        field: str | None = None,
        value: object = None,
        **kwargs: object,
    ) -> None:
        """Initialize Oracle validation error with context."""
        validation_details: dict[str, object] = {}
        if field is not None:
            validation_details["field"] = field
        if value is not None:
            validation_details["value"] = str(value)[:100]

        context = dict(kwargs)
        super().__init__(
            f"Oracle DB: {message}",
            validation_details=validation_details,
            context=context,
        )


class FlextDbOracleConfigurationError(FlextConfigurationError):
    """Oracle database configuration errors."""

    def __init__(
        self,
        message: str = "Oracle database configuration error",
        *,
        config_key: str | None = None,
        **kwargs: object,
    ) -> None:
        """Initialize Oracle configuration error with context."""
        context = dict(kwargs)
        if config_key is not None:
            context["config_key"] = config_key
        super().__init__(f"Oracle DB config: {message}", **context)


class FlextDbOracleConnectionError(FlextConnectionError):
    """Oracle database connection errors."""

    def __init__(
        self,
        message: str = "Oracle database connection failed",
        *,
        service_name: str | None = None,
        endpoint: str | None = None,
        **kwargs: object,
    ) -> None:
        """Initialize Oracle connection error with context."""
        context = dict(kwargs)
        if service_name is not None:
            context["service_name"] = service_name
        if endpoint is not None:
            context["endpoint"] = endpoint
        super().__init__(f"Oracle DB connection: {message}", **context)


class FlextDbOracleProcessingError(FlextProcessingError):
    """Oracle database processing errors."""

    def __init__(
        self,
        message: str = "Oracle database processing failed",
        *,
        operation: str | None = None,
        file_path: str | None = None,
        **kwargs: object,
    ) -> None:
        """Initialize Oracle processing error with context."""
        context = dict(kwargs)
        if operation is not None:
            context["operation"] = operation
        if file_path is not None:
            context["file_path"] = file_path
        super().__init__(f"Oracle DB processing: {message}", **context)


class FlextDbOracleAuthenticationError(FlextAuthenticationError):
    """Oracle database authentication errors."""

    def __init__(
        self,
        message: str = "Oracle database authentication failed",
        *,
        username: str | None = None,
        auth_method: str | None = None,
        **kwargs: object,
    ) -> None:
        """Initialize Oracle authentication error with context."""
        context = dict(kwargs)
        if username is not None:
            context["username"] = username
        if auth_method is not None:
            context["auth_method"] = auth_method
        super().__init__(f"Oracle DB: {message}", **context)


class FlextDbOracleTimeoutError(FlextTimeoutError):
    """Oracle database timeout errors."""

    def __init__(
        self,
        message: str = "Oracle database operation timed out",
        *,
        timeout_duration: float | None = None,
        operation: str | None = None,
        **kwargs: object,
    ) -> None:
        """Initialize Oracle timeout error with context."""
        context = dict(kwargs)
        if timeout_duration is not None:
            context["timeout_duration"] = timeout_duration
        if operation is not None:
            context["operation"] = operation
        super().__init__(f"Oracle DB: {message}", **context)


class FlextDbOracleQueryError(FlextDbOracleError):
    """Oracle database query errors with query-specific context."""

    def __init__(
        self,
        message: str = "Oracle database query error",
        *,
        query: str | None = None,
        error_code: str | None = None,
        **kwargs: object,
    ) -> None:
        """Initialize query error with context."""
        formatted_message = f"Oracle DB query: {message}"
        context = dict(kwargs)
        if query is not None:
            context["query"] = query[:200]  # Truncate long queries
        super().__init__(formatted_message, error_code=error_code, **context)


class FlextDbOracleMetadataError(FlextDbOracleError):
    """Oracle database metadata errors with metadata-specific context."""

    def __init__(
        self,
        message: str = "Oracle database metadata error",
        *,
        schema_name: str | None = None,
        object_name: str | None = None,
        error_code: str | None = None,
        **kwargs: object,
    ) -> None:
        """Initialize metadata error with context."""
        formatted_message = f"Oracle DB metadata: {message}"
        context = dict(kwargs)
        if schema_name is not None:
            context["schema_name"] = schema_name
        if object_name is not None:
            context["object_name"] = object_name
        super().__init__(formatted_message, error_code=error_code, **context)


# Domain-specific exceptions now implemented as explicit classes above


__all__: list[str] = [
    "FlextDbOracleAuthenticationError",
    "FlextDbOracleConfigurationError",
    "FlextDbOracleConnectionError",
    "FlextDbOracleError",
    "FlextDbOracleMetadataError",
    "FlextDbOracleProcessingError",
    "FlextDbOracleQueryError",
    "FlextDbOracleTimeoutError",
    "FlextDbOracleValidationError",
]
