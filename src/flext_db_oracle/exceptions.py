"""Oracle Database-specific exceptions extending flext-core patterns.

This module provides Oracle-specific exception classes that extend e
with database-specific error handling and metadata.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from flext_core import e

from flext_db_oracle import t


class FlextDbOracleExceptions(e):
    """Oracle database-specific exceptions extending e.

    Provides Oracle-specific exception types with database metadata
    and error categorization for Oracle database operations.
    """

    class Error(e.BaseError):
        """Base Oracle error extending e.BaseError."""

        def __init__(
            self,
            message: str,
            *,
            oracle_error_code: str | None = None,
            sql_state: str | None = None,
        ) -> None:
            """Initialize Oracle error with message and optional metadata."""
            super().__init__(message)
            self.oracle_error_code = oracle_error_code
            self.sql_state = sql_state

    class OracleConnectionError(e.ConnectionError):
        """Oracle connection error extending e.ConnectionError."""

        def __init__(
            self,
            message: str,
            *,
            tns_error: str | None = None,
            connection_string: str | None = None,
        ) -> None:
            """Initialize connection error with TNS and connection metadata."""
            super().__init__(message)
            self.tns_error = tns_error
            self.connection_string = connection_string

    class OracleMetadataError(e.OperationError):
        """Oracle metadata error extending e.OperationError."""

        def __init__(
            self,
            message: str,
            *,
            object_name: str | None = None,
            object_type: str | None = None,
        ) -> None:
            """Initialize metadata error with t.JsonValue name and type metadata."""
            super().__init__(message)
            self.object_name = object_name
            self.object_type = object_type

    class ProcessingError(e.OperationError):
        """Oracle processing error extending e.OperationError."""

        def __init__(
            self,
            message: str,
            *,
            operation_type: str | None = None,
            processing_stage: str | None = None,
        ) -> None:
            """Initialize processing error with operation type and stage metadata."""
            super().__init__(message)
            self.operation_type = operation_type
            self.processing_stage = processing_stage

    class OracleQueryError(e.OperationError):
        """Oracle query error extending e.OperationError."""

        def __init__(
            self,
            message: str,
            *,
            sql_text: str | None = None,
            bind_variables: t.JsonMapping | None = None,
        ) -> None:
            """Initialize query error with SQL text and bind variables metadata."""
            super().__init__(message)
            self.sql_text = sql_text
            self.bind_variables = bind_variables or {}

    class OracleTimeoutError(e.TimeoutError):
        """Oracle timeout error extending e.TimeoutError."""

        def __init__(
            self,
            message: str,
            *,
            query_id: str | None = None,
            elapsed_time: float | None = None,
        ) -> None:
            """Initialize timeout error with query ID and elapsed time metadata."""
            super().__init__(message)
            self.query_id = query_id
            self.elapsed_time = elapsed_time


e = FlextDbOracleExceptions

__all__: list[str] = ["FlextDbOracleExceptions", "e"]
