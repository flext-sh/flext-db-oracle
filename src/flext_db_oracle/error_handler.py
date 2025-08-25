"""FLEXT DB Oracle Error Handling following Flext[Area][Module] pattern.

This module provides the FlextDbOracleErrorHandling class with consolidated
error handling functionality following FLEXT architectural patterns with
DRY principles.

Single consolidated class containing ALL Oracle error handling components organized
internally, following SOLID principles and eliminating duplication.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_core import FlextFactory, get_logger

from .observability import FlextDbOracleObservabilityManager

# Constants for observability configuration
MAX_SQL_LOG_LENGTH = 100  # Maximum SQL length to display in logs


class FlextDbOracleErrorHandling(FlextFactory):
    """Oracle Database Error Handling following Flext[Area][Module] pattern.

    Single consolidated class containing ALL Oracle error handling functionality
    organized internally, following SOLID principles and DRY methodology.

    This class consolidates ALL Oracle error handling functionality into a single
    entry point eliminating duplication and multiple small classes.
    """

    # =============================================================================
    # INTERNAL ERROR HANDLER CLASS - Consolidated error handling implementation
    # =============================================================================

    class _InternalErrorHandler:
        """Internal Oracle error handler consolidated into FlextDbOracleErrorHandling.

        DRY CONSOLIDATION: Moved from separate FlextDbOracleErrorHandler class to eliminate
        multiple small classes and follow DRY principles with large consolidated class.
        """

        def __init__(
            self, observability_manager: FlextDbOracleObservabilityManager
        ) -> None:
            """Initialize error handler."""
            self._observability = observability_manager
            self._logger = get_logger(f"{__name__}.ErrorHandler")

        def handle_connection_error(self, error: Exception, context: str = "") -> None:
            """Handle connection errors with observability."""
            error_msg = f"Connection error{f' in {context}' if context else ''}: {error}"
            self._logger.error(error_msg)
            self._observability.record_metric("oracle.connection.errors", 1.0)

        def handle_query_error(
            self, error: Exception, sql: str = "", context: str = ""
        ) -> None:
            """Handle query errors with observability."""
            truncated_sql = (
                sql[:MAX_SQL_LOG_LENGTH] + "..." if len(sql) > MAX_SQL_LOG_LENGTH else sql
            )
            error_msg = f"Query error{f' in {context}' if context else ''}: {error}"
            if truncated_sql:
                error_msg += f" (SQL: {truncated_sql})"

            self._logger.error(error_msg)
            self._observability.record_metric("oracle.query.errors", 1.0)

        def handle_metadata_error(self, error: Exception, context: str = "") -> None:
            """Handle metadata operation errors with observability."""
            error_msg = f"Metadata error{f' in {context}' if context else ''}: {error}"
            self._logger.error(error_msg)
            self._observability.record_metric("oracle.metadata.errors", 1.0)

    # =============================================================================
    # FACTORY METHODS - Consolidated error handler creation
    # =============================================================================

    @classmethod
    def create_error_handler(
        cls, observability_manager: FlextDbOracleObservabilityManager
    ) -> _InternalErrorHandler:
        """Create Oracle error handler using consolidated internal class."""
        return cls._InternalErrorHandler(observability_manager)



# =============================================================================
# BACKWARD COMPATIBILITY ALIASES - DRY CONSOLIDATION
# =============================================================================

# Backward compatibility alias for FlextDbOracleErrorHandler
FlextDbOracleErrorHandler = FlextDbOracleErrorHandling._InternalErrorHandler

__all__: list[str] = [
    "FlextDbOracleErrorHandler",  # Backward compatibility
    "FlextDbOracleErrorHandling",
]
