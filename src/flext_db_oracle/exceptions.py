"""Oracle Database Exception Hierarchy.

Exception hierarchy following FLEXT patterns using factory pattern from flext-core.
Eliminates code duplication by using create_module_exception_classes() factory.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from flext_core import FlextError

# Oracle DB-specific exception classes following FLEXT patterns
# Manual implementation instead of factory pattern to fix MyPy issues


class FlextDbOracleError(FlextError):
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


# Domain-specific exceptions for Oracle database business logic
class FlextDbOracleQueryError(FlextDbOracleError):
    """Oracle database query errors with SQL query context."""

    def __init__(
        self,
        message: str = "Oracle database query error",
        *,
        query: str | None = None,
        operation: str = "query_execution",
        **kwargs: object,
    ) -> None:
        """Initialize Oracle query error with SQL context."""
        context = dict(kwargs)
        if query is not None:
            context["query"] = query[:200]  # Truncate long queries for safety

        context["operation"] = operation
        super().__init__(message, context=context)


class FlextDbOracleMetadataError(FlextDbOracleError):
    """Oracle database metadata errors with schema context."""

    def __init__(
        self,
        message: str = "Oracle database metadata error",
        *,
        schema_name: str | None = None,
        object_name: str | None = None,
        operation: str = "metadata_processing",
        **kwargs: object,
    ) -> None:
        """Initialize Oracle metadata error with schema context."""
        context = dict(kwargs)
        if schema_name is not None:
            context["schema_name"] = schema_name
        if object_name is not None:
            context["object_name"] = object_name

        context["operation"] = operation
        super().__init__(message, context=context)


# Export all exceptions - factory-created + domain-specific
__all__ = [
    # Alphabetically sorted for RUF022 compliance
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
