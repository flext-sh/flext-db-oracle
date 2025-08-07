"""Oracle Database Exception Hierarchy.

Exception hierarchy following FLEXT patterns using factory pattern from flext-core.
Eliminates code duplication by using create_module_exception_classes() factory.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from flext_core import FlextError, create_module_exception_classes

# Create Oracle DB-specific exception classes using flext-core factory
# This eliminates the need for manual exception class creation and duplicated __init__ methods
_db_oracle_exceptions = create_module_exception_classes("flext_db_oracle")

# Extract factory-created exception classes with type annotations for MyPy
FlextDbOracleError: type[FlextError] = _db_oracle_exceptions["FlextDbOracleError"]
FlextDbOracleValidationError: type[FlextError] = _db_oracle_exceptions["FlextDbOracleValidationError"]
FlextDbOracleConfigurationError: type[FlextError] = _db_oracle_exceptions["FlextDbOracleConfigurationError"]
FlextDbOracleConnectionError: type[FlextError] = _db_oracle_exceptions["FlextDbOracleConnectionError"]
FlextDbOracleProcessingError: type[FlextError] = _db_oracle_exceptions["FlextDbOracleProcessingError"]
FlextDbOracleAuthenticationError: type[FlextError] = _db_oracle_exceptions["FlextDbOracleAuthenticationError"]
FlextDbOracleTimeoutError: type[FlextError] = _db_oracle_exceptions["FlextDbOracleTimeoutError"]


# Domain-specific exceptions for Oracle database business logic
class FlextDbOracleQueryError(FlextDbOracleError):  # type: ignore[valid-type,misc]
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

        super().__init__(message, operation=operation, **context)


class FlextDbOracleMetadataError(FlextDbOracleError):  # type: ignore[valid-type,misc]
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

        super().__init__(message, operation=operation, **context)


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
