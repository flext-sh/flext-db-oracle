"""Oracle Database exception hierarchy using flext-core patterns.

Copyright (c) 2025 FLEXT Contributors
SPDX-License-Identifier: MIT

Domain-specific exceptions for Oracle database operations inheriting from flext-core.
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


class FlextDbOracleError(FlextError):
    """Base exception for Oracle database operations."""

    def __init__(
        self,
        message: str = "Oracle database error",
        database_name: str | None = None,
        **kwargs: object,
    ) -> None:
        """Initialize Oracle database error with context."""
        context = kwargs.copy()
        if database_name is not None:
            context["database_name"] = database_name

        super().__init__(message, error_code="ORACLE_DB_ERROR", context=context)


class FlextDbOracleConnectionError(FlextConnectionError):
    """Oracle database connection errors."""

    def __init__(
        self,
        message: str = "Oracle database connection failed",
        host: str | None = None,
        port: int | None = None,
        service_name: str | None = None,
        **kwargs: object,
    ) -> None:
        """Initialize Oracle database connection error with context."""
        context = kwargs.copy()
        if host is not None:
            context["host"] = host
        if port is not None:
            context["port"] = port
        if service_name is not None:
            context["service_name"] = service_name

        super().__init__(f"Oracle DB connection: {message}", **context)


class FlextDbOracleAuthenticationError(FlextAuthenticationError):
    """Oracle database authentication errors."""

    def __init__(
        self,
        message: str = "Oracle database authentication failed",
        username: str | None = None,
        database_name: str | None = None,
        **kwargs: object,
    ) -> None:
        """Initialize Oracle database authentication error with context."""
        context = kwargs.copy()
        if username is not None:
            context["username"] = username
        if database_name is not None:
            context["database_name"] = database_name

        super().__init__(f"Oracle DB auth: {message}", **context)


class FlextDbOracleValidationError(FlextValidationError):
    """Oracle database validation errors."""

    def __init__(
        self,
        message: str = "Oracle database validation failed",
        field: str | None = None,
        value: object = None,
        table_name: str | None = None,
        **kwargs: object,
    ) -> None:
        """Initialize Oracle database validation error with context."""
        validation_details: dict[str, object] = {}
        if field is not None:
            validation_details["field"] = field
        if value is not None:
            validation_details["value"] = str(value)[:100]  # Truncate long values

        context = kwargs.copy()
        if table_name is not None:
            context["table_name"] = table_name

        super().__init__(
            f"Oracle DB validation: {message}",
            validation_details=validation_details,
            context=context,
        )


class FlextDbOracleConfigurationError(FlextConfigurationError):
    """Oracle database configuration errors."""

    def __init__(
        self,
        message: str = "Oracle database configuration error",
        config_key: str | None = None,
        **kwargs: object,
    ) -> None:
        """Initialize Oracle database configuration error with context."""
        context = kwargs.copy()
        if config_key is not None:
            context["config_key"] = config_key

        super().__init__(f"Oracle DB config: {message}", **context)


class FlextDbOracleProcessingError(FlextProcessingError):
    """Oracle database processing errors."""

    def __init__(
        self,
        message: str = "Oracle database processing failed",
        operation: str | None = None,
        table_name: str | None = None,
        **kwargs: object,
    ) -> None:
        """Initialize Oracle database processing error with context."""
        context = kwargs.copy()
        if operation is not None:
            context["operation"] = operation
        if table_name is not None:
            context["table_name"] = table_name

        super().__init__(f"Oracle DB processing: {message}", **context)


class FlextDbOracleTimeoutError(FlextTimeoutError):
    """Oracle database timeout errors."""

    def __init__(
        self,
        message: str = "Oracle database operation timed out",
        operation: str | None = None,
        timeout_seconds: float | None = None,
        **kwargs: object,
    ) -> None:
        """Initialize Oracle database timeout error with context."""
        context = kwargs.copy()
        if operation is not None:
            context["operation"] = operation
        if timeout_seconds is not None:
            context["timeout_seconds"] = timeout_seconds

        super().__init__(f"Oracle DB timeout: {message}", **context)


class FlextDbOracleQueryError(FlextDbOracleError):
    """Oracle database query errors."""

    def __init__(
        self,
        message: str = "Oracle database query error",
        query: str | None = None,
        error_code: str | None = None,
        **kwargs: object,
    ) -> None:
        """Initialize Oracle database query error with context."""
        context = kwargs.copy()
        if query is not None:
            context["query"] = query[:200]  # Truncate long queries
        if error_code is not None:
            context["oracle_error_code"] = error_code

        super().__init__(f"Oracle DB query: {message}", context=context)


class FlextDbOracleMetadataError(FlextDbOracleError):
    """Oracle database metadata errors."""

    def __init__(
        self,
        message: str = "Oracle database metadata error",
        schema_name: str | None = None,
        object_name: str | None = None,
        **kwargs: object,
    ) -> None:
        """Initialize Oracle database metadata error with context."""
        context = kwargs.copy()
        if schema_name is not None:
            context["schema_name"] = schema_name
        if object_name is not None:
            context["object_name"] = object_name

        super().__init__(f"Oracle DB metadata: {message}", context=context)


__all__ = [
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
