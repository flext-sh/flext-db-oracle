"""Oracle Database Exception Hierarchy.

Exception hierarchy following FLEXT patterns using factory pattern from flext-core.
Eliminates code duplication by using create_module_exception_classes() factory.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from dataclasses import dataclass

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


# =============================================================================
# PARAMETER CLASSES - Reduces parameter count for complex constructors
# =============================================================================


@dataclass
class OracleMetadataErrorParams:
    """Parameters for Oracle metadata errors - REDUCES PARAMETER COUNT."""

    schema_name: str | None = None
    object_name: str | None = None
    operation: str = "metadata_processing"

    def to_context(self, **kwargs: object) -> dict[str, object]:
        """Convert parameters to error context dictionary."""
        context = dict(kwargs)
        if self.schema_name is not None:
            context["schema_name"] = self.schema_name
        if self.object_name is not None:
            context["object_name"] = self.object_name
        context["operation"] = self.operation
        return context


@dataclass
class OracleQueryErrorParams:
    """Parameters for Oracle query errors - REDUCES PARAMETER COUNT."""

    query: str | None = None
    operation: str = "query_execution"

    def to_context(self, **kwargs: object) -> dict[str, object]:
        """Convert parameters to error context dictionary."""
        context = dict(kwargs)
        if self.query is not None:
            context["query"] = self.query[:200]  # Truncate long queries for safety
        context["operation"] = self.operation
        return context


# =============================================================================
# DOMAIN-SPECIFIC EXCEPTIONS
# =============================================================================


class FlextDbOracleQueryError(FlextDbOracleError):
    """Oracle database query errors with SQL query context."""

    def __init__(
        self,
        message: str = "Oracle database query error",
        *,
        params: OracleQueryErrorParams | None = None,
        # Backward compatibility parameters
        query: str | None = None,
        operation: str = "query_execution",
        **kwargs: object,
    ) -> None:
        """Initialize Oracle query error with SQL query context."""
        if params is None:
            params = OracleQueryErrorParams(query=query, operation=operation)

        context = params.to_context(**kwargs)
        super().__init__(message, context=context)


class FlextDbOracleMetadataError(FlextDbOracleError):
    """Oracle database metadata errors with schema context."""

    def __init__(
        self,
        message: str = "Oracle database metadata error",
        *,
        params: OracleMetadataErrorParams | None = None,
        # Backward compatibility parameters
        schema_name: str | None = None,
        object_name: str | None = None,
        operation: str = "metadata_processing",
        **kwargs: object,
    ) -> None:
        """Initialize Oracle metadata error with schema context."""
        if params is None:
            params = OracleMetadataErrorParams(
                schema_name=schema_name,
                object_name=object_name,
                operation=operation,
            )

        context = params.to_context(**kwargs)
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
