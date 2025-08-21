"""FLEXT DB Oracle Observability Management - Simplified Implementation.

This module provides basic observability for Oracle database operations
using only flext-core dependencies. It implements a simplified Clean Architecture
approach with centralized monitoring and error handling.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from time import perf_counter
from typing import Self

from flext_core import FlextContainer, FlextResult, get_logger

# Constants for observability configuration
MAX_SQL_LOG_LENGTH = 100  # Maximum SQL length to display in logs


class FlextTrace:
    """Simple trace implementation for Oracle operations."""

    def __init__(self, trace_id: str, operation_name: str, timestamp: datetime) -> None:
        """Initialize trace."""
        self.trace_id = trace_id
        self.operation_name = operation_name
        self.timestamp = timestamp
        self.attributes: dict[str, object] = {}


class FlextHealthCheck:
    """Simple health check implementation."""

    def __init__(self, component: str, status: str, message: str = "") -> None:
        """Initialize health check."""
        self.component = component
        self.status = status
        self.message = message
        self.timestamp = datetime.now(UTC)


class FlextDbOracleObservabilityManager:
    """Centralized observability manager for Oracle database operations.

    Follows Single Responsibility and DRY principles by centralizing all
    observability concerns in one place.
    """

    def __init__(self, container: FlextContainer, context_name: str) -> None:
        """Initialize observability manager."""
        self._container = container
        self._context_name = context_name
        self._logger = get_logger(f"{__name__}.{context_name}")
        self._initialized = False

    def initialize(self) -> FlextResult[None]:
        """Initialize observability components."""
        try:
            self._logger.info("Initializing observability for %s", self._context_name)
            self._initialized = True
            return FlextResult[None].ok(None)
        except Exception as e:
            return FlextResult[None].fail(f"Failed to initialize observability: {e}")

    def create_trace(
        self,
        operation: str,
        **attributes: object,
    ) -> FlextTrace:
        """Create trace for operation."""
        trace_id = str(uuid.uuid4())
        timestamp = datetime.now(UTC)
        trace = FlextTrace(trace_id, f"{self._context_name}.{operation}", timestamp)
        trace.attributes.update(attributes)

        self._logger.debug("Created trace %s for %s", trace_id, operation)
        return trace

    def record_metric(
        self,
        metric_name: str,
        value: float,
        unit: str = "",
        **tags: object,
    ) -> None:
        """Record metric (simplified logging-based implementation)."""
        self._logger.info(
            "METRIC: %s=%s%s %s",
            metric_name,
            value,
            f" {unit}" if unit else "",
            f"tags={tags}" if tags else "",
        )

    def create_health_check(
        self,
        component: str,
        status: str,
        message: str = "",
    ) -> FlextResult[FlextHealthCheck]:
        """Create health check."""
        try:
            health_check = FlextHealthCheck(component, status, message)
            self._logger.debug("Health check: %s = %s", component, status)
            return FlextResult[FlextHealthCheck].ok(health_check)
        except Exception as e:
            return FlextResult[FlextHealthCheck].fail(
                f"Failed to create health check: {e}"
            )

    def finish_trace(self, trace: FlextTrace, **final_attributes: object) -> FlextTrace:
        """Finish trace with final attributes."""
        trace.attributes.update(final_attributes)
        duration = (datetime.now(UTC) - trace.timestamp).total_seconds()
        trace.attributes["duration_seconds"] = duration

        self._logger.debug(
            "Finished trace %s for %s (duration: %.3fs)",
            trace.trace_id,
            trace.operation_name,
            duration,
        )
        return trace

    def is_monitoring_active(self) -> bool:
        """Check if monitoring is active."""
        return self._initialized


class FlextDbOracleOperationTracker:
    """Context manager for tracking Oracle database operations.

    Automatically creates traces, records timing metrics, and handles errors.
    Follows the Context Manager pattern for clean resource management.
    """

    def __init__(
        self,
        observability_manager: FlextDbOracleObservabilityManager,
        operation: str,
        **attributes: object,
    ) -> None:
        """Initialize operation tracker."""
        self._observability = observability_manager
        self._operation = operation
        self._attributes = attributes
        self._trace: FlextTrace | None = None
        self._start_time = 0.0

    def __enter__(self) -> Self:
        """Start tracking operation."""
        self._start_time = perf_counter()
        self._trace = self._observability.create_trace(
            self._operation, **self._attributes
        )
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: object,
    ) -> None:
        """Finish tracking operation."""
        if self._trace:
            duration = perf_counter() - self._start_time
            final_attributes: dict[str, object] = {
                "duration_seconds": duration,
                "success": exc_type is None,
            }
            if exc_type:
                final_attributes["error_type"] = exc_type.__name__
                final_attributes["error_message"] = str(exc_val)

            self._observability.finish_trace(self._trace, **final_attributes)
            self._observability.record_metric(
                f"oracle.{self._operation}.duration", duration, "seconds"
            )

    def add_attribute(self, key: str, value: object) -> None:
        """Add attribute to current trace."""
        if self._trace:
            self._trace.attributes[key] = value


class FlextDbOracleErrorHandler:
    """Centralized error handling with observability integration."""

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
