"""Oracle Database Exception Hierarchy - Modern Pydantic v2 Patterns.

This module provides Oracle-specific exceptions using modern patterns from flext-core.
All exceptions follow the FlextErrorMixin pattern with keyword-only arguments and
modern Python 3.13 type aliases for comprehensive error handling in Oracle operations.

Copyright (c) 2025 FLEXT Contributors
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from collections.abc import Mapping
from enum import Enum

from flext_core import FlextError
from flext_core.exceptions import FlextErrorMixin


class FlextDbOracleErrorCodes(Enum):
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


# Base Oracle database exception hierarchy using FlextErrorMixin pattern
class FlextDbOracleError(FlextError, FlextErrorMixin):
    """Base Oracle database error."""


class FlextDbOracleValidationError(FlextDbOracleError):
    """Oracle database validation error."""


class FlextDbOracleConfigurationError(FlextDbOracleError):
    """Oracle database configuration error."""


class FlextDbOracleConnectionError(FlextDbOracleError):
    """Oracle database connection error."""


class FlextDbOracleProcessingError(FlextDbOracleError):
    """Oracle database processing error."""


class FlextDbOracleAuthenticationError(FlextDbOracleError):
    """Oracle database authentication error."""


class FlextDbOracleTimeoutError(FlextDbOracleError):
    """Oracle database timeout error."""


# Domain-specific exceptions for Oracle business logic
# Using modern FlextErrorMixin pattern with context support


class FlextDbOracleQueryError(FlextDbOracleError):
    """Oracle database query errors with SQL query context."""

    def __init__(
        self,
        message: str,
        *,
        query: str | None = None,
        operation: str | None = None,
        execution_time: float | None = None,
        rows_affected: int | None = None,
        code: FlextDbOracleErrorCodes
        | None = FlextDbOracleErrorCodes.ORACLE_QUERY_ERROR,
        context: Mapping[str, object] | None = None,
    ) -> None:
        """Initialize Oracle query error with SQL query context."""
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

        super().__init__(
            message,
            code=code,
            context=context_dict,
        )


class FlextDbOracleMetadataError(FlextDbOracleError):
    """Oracle database metadata errors with schema context."""

    def __init__(
        self,
        message: str,
        *,
        schema_name: str | None = None,
        object_name: str | None = None,
        object_type: str | None = None,
        operation: str | None = None,
        code: FlextDbOracleErrorCodes
        | None = FlextDbOracleErrorCodes.ORACLE_METADATA_ERROR,
        context: Mapping[str, object] | None = None,
    ) -> None:
        """Initialize Oracle metadata error with schema context."""
        context_dict: dict[str, object] = dict(context) if context else {}
        if schema_name is not None:
            context_dict["schema_name"] = schema_name
        if object_name is not None:
            context_dict["object_name"] = object_name
        if object_type is not None:
            context_dict["object_type"] = object_type
        if operation is not None:
            context_dict["operation"] = operation

        super().__init__(
            message,
            code=code,
            context=context_dict,
        )


class FlextDbOracleConnectionOperationError(FlextDbOracleConnectionError):
    """Oracle connection operation errors with connection context."""

    def __init__(
        self,
        message: str,
        *,
        host: str | None = None,
        port: int | None = None,
        service_name: str | None = None,
        username: str | None = None,
        connection_timeout: float | None = None,
        code: FlextDbOracleErrorCodes
        | None = FlextDbOracleErrorCodes.ORACLE_CONNECTION_ERROR,
        context: Mapping[str, object] | None = None,
    ) -> None:
        """Initialize Oracle connection error with connection context."""
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

        super().__init__(
            message,
            code=code,
            context=context_dict,
        )


__all__: list[str] = [
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
