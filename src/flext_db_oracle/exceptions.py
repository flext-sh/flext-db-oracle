"""Oracle Database-specific exceptions extending flext-core patterns.

This module provides Oracle-specific exception classes that extend FlextExceptions
with database-specific error handling and metadata.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from flext_core import FlextExceptions


class FlextDbOracleExceptions(FlextExceptions):
    """Oracle database-specific exceptions extending FlextExceptions.

    Provides Oracle-specific exception types with database metadata
    and error categorization for Oracle database operations.
    """

    class Error(FlextExceptions.BaseError):
        """Base Oracle error extending FlextExceptions.BaseError."""

        def __init__(
            self,
            message: str,
            *,
            oracle_error_code: str | None = None,
            sql_state: str | None = None,
            **kwargs: object,
        ) -> None:
            """Initialize Oracle error with message and optional metadata."""
            super().__init__(message, **kwargs)
            self.oracle_error_code = oracle_error_code
            self.sql_state = sql_state

    class OracleConnectionError(FlextExceptions.ConnectionError):
        """Oracle connection error extending FlextExceptions.ConnectionError."""

        def __init__(
            self,
            message: str,
            *,
            tns_error: str | None = None,
            connection_string: str | None = None,
            **kwargs: object,
        ) -> None:
            """Initialize connection error with TNS and connection metadata."""
            super().__init__(message, **kwargs)
            self.tns_error = tns_error
            self.connection_string = connection_string

    class OracleMetadataError(FlextExceptions.OperationError):
        """Oracle metadata error extending FlextExceptions.OperationError."""

        def __init__(
            self,
            message: str,
            *,
            object_name: str | None = None,
            object_type: str | None = None,
            **kwargs: object,
        ) -> None:
            """Initialize metadata error with object name and type metadata."""
            super().__init__(message, **kwargs)
            self.object_name = object_name
            self.object_type = object_type

    class ProcessingError(FlextExceptions.OperationError):
        """Oracle processing error extending FlextExceptions.OperationError."""

        def __init__(
            self,
            message: str,
            *,
            operation_type: str | None = None,
            processing_stage: str | None = None,
            **kwargs: object,
        ) -> None:
            """Initialize processing error with operation type and stage metadata."""
            super().__init__(message, **kwargs)
            self.operation_type = operation_type
            self.processing_stage = processing_stage

    class OracleQueryError(FlextExceptions.OperationError):
        """Oracle query error extending FlextExceptions.OperationError."""

        def __init__(
            self,
            message: str,
            *,
            sql_text: str | None = None,
            bind_variables: dict[str, object] | None = None,
            **kwargs: object,
        ) -> None:
            """Initialize query error with SQL text and bind variables metadata."""
            super().__init__(message, **kwargs)
            self.sql_text = sql_text
            self.bind_variables = bind_variables or {}

    class OracleTimeoutError(FlextExceptions.TimeoutError):
        """Oracle timeout error extending FlextExceptions.TimeoutError."""

        def __init__(
            self,
            message: str,
            *,
            query_id: str | None = None,
            elapsed_time: float | None = None,
            **kwargs: object,
        ) -> None:
            """Initialize timeout error with query ID and elapsed time metadata."""
            super().__init__(message, **kwargs)
            self.query_id = query_id
            self.elapsed_time = elapsed_time


__all__ = [
    "FlextDbOracleExceptions",
]
