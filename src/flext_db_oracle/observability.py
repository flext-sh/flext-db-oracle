"""Oracle Observability Manager - DRY observability patterns.

Copyright (c) 2025 FLEXT Contributors
SPDX-License-Identifier: MIT

Centralized observability management following DRY, KISS, and SOLID principles.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from time import perf_counter
from typing import TYPE_CHECKING, Any, Self

from flext_core import FlextResult, get_logger
from flext_observability import (
    FlextHealthCheck,
    FlextObservabilityMonitor,
    FlextTrace,
    flext_create_health_check,
    flext_create_metric,
    flext_create_trace,
)

if TYPE_CHECKING:
    from flext_core import FlextContainer


class FlextDbOracleObservabilityManager:
    """Centralized observability manager for Oracle database operations.

    Follows Single Responsibility and DRY principles by centralizing all
    observability concerns in one place.
    """

    def __init__(self, container: FlextContainer, context_name: str) -> None:
        """Initialize observability manager."""
        self._container = container
        self._context_name = context_name
        self._logger = get_logger(f"FlextDbOracleObservability.{context_name}")

        # Observability components using flext-observability patterns
        self._monitor = FlextObservabilityMonitor(container)

        self._initialized = False

    def initialize(self) -> FlextResult[None]:
        """Initialize observability system."""
        if self._initialized:
            return FlextResult.ok(None)

        try:
            # Use the proper initialization pattern from flext-observability
            init_result = self._monitor.flext_initialize_observability()
            if init_result.is_success:
                start_result = self._monitor.flext_start_monitoring()
                if start_result.is_success:
                    self._logger.info("Observability monitoring initialized successfully")
                else:
                    self._logger.warning("Failed to start monitoring: %s", start_result.error)
            else:
                self._logger.warning("Failed to initialize observability: %s", init_result.error)
        except (AttributeError, ValueError) as e:
            self._logger.warning("Failed to initialize observability: %s", e)

        self._initialized = True
        return FlextResult.ok(None)

    def create_trace(self, operation: str, **attributes: Any) -> FlextTrace:  # noqa: ANN401
        """Create trace for operation (DRY pattern)."""
        trace_id = str(uuid.uuid4())
        span_id = str(uuid.uuid4())

        # Use flext_create_trace with proper parameters
        trace_result = flext_create_trace(
            trace_id=trace_id,
            operation=f"{self._context_name}.{operation}",
            config=attributes,
        )

        if trace_result.is_success and trace_result.data:
            return trace_result.data

        # Fallback: create trace directly using FlextTrace constructor
        return FlextTrace(
            id=str(uuid.uuid4()),
            trace_id=trace_id,
            operation=f"{self._context_name}.{operation}",
            span_id=span_id,
            duration_ms=0,
            status="pending",
            timestamp=datetime.now(UTC),
        )

    def record_metric(
        self,
        name: str,
        value: float,
        unit: str = "",
        **tags: str,
    ) -> None:
        """Record metric (DRY pattern)."""
        # Use flext_create_metric with proper parameters
        metric_result = flext_create_metric(
            name=f"{self._context_name}.{name}",
            value=value,
            unit=unit,
            tags={"context": self._context_name, **tags},
        )

        if metric_result.is_success:
            self._logger.debug("Metric %s created successfully", name)
        else:
            self._logger.warning(
                "Failed to create metric %s: %s",
                name,
                metric_result.error,
            )

    def create_health_check(
        self,
        status: str,
        message: str,
        metrics: dict[str, Any] | None = None,  # noqa: ARG002
    ) -> FlextResult[FlextHealthCheck]:
        """Create health check (DRY pattern)."""
        # Use flext_create_health_check with proper parameters
        # Note: metrics parameter kept for API compatibility but not used by flext_create_health_check
        return flext_create_health_check(
            component=f"oracle.{self._context_name}",
            status=status,
            message=message,
        )

    def finish_trace(
        self,
        trace: FlextTrace,
        duration_ms: int,
        status: str = "success",
        error: str | None = None,
    ) -> FlextTrace:
        """Finish trace with timing and status (DRY pattern) - Creates new immutable trace."""
        # FlextTrace is frozen (immutable), so we need to create a new one
        updated_span_attributes = dict(trace.span_attributes)
        if error:
            updated_span_attributes["error"] = error

        # Create new trace with updated fields using flext_create_trace
        config = {
            "span_id": trace.span_id,
            "duration_ms": duration_ms,
            "status": status,
        }

        trace_result = flext_create_trace(
            trace_id=trace.trace_id,
            operation=trace.operation,
            config=config,
        )

        if trace_result.is_success and trace_result.data:
            # Copy span attributes to new trace
            new_trace = trace_result.data
            new_trace.span_attributes.update(updated_span_attributes)
            self._logger.debug("Trace finished: %s", new_trace.span_id)
            return new_trace

        # Fallback: return original trace (should not happen)
        self._logger.warning("Failed to create updated trace, returning original")
        return trace

    def get_current_timestamp(self) -> str:
        """Get current UTC timestamp in ISO format (DRY pattern)."""
        return datetime.now(UTC).isoformat()

    def is_monitoring_active(self) -> bool:
        """Check if monitoring is active."""
        return self._initialized and self._monitor.flext_is_monitoring_active()


class FlextDbOracleOperationTracker:
    """Operation tracking context manager for DRY timing patterns.

    Follows SOLID principles by having single responsibility for operation tracking.
    """

    def __init__(
        self,
        observability: FlextDbOracleObservabilityManager,
        operation: str,
        **attributes: Any,  # noqa: ANN401
    ) -> None:
        """Initialize operation tracker."""
        self._observability = observability
        self._operation = operation
        self._attributes = attributes
        self._trace: FlextTrace | None = None
        self._start_time: float = 0.0

    def __enter__(self) -> Self:
        """Start operation tracking."""
        self._trace = self._observability.create_trace(
            self._operation,
            **self._attributes,
        )
        self._start_time = perf_counter()
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: object,
    ) -> None:
        """Finish operation tracking."""
        if self._trace:
            duration_ms = int((perf_counter() - self._start_time) * 1000)
            status = "error" if exc_type else "success"
            error = str(exc_val) if exc_val else None
            self._observability.finish_trace(self._trace, duration_ms, status, error)

    def record_metric(
        self,
        name: str,
        value: float,
        unit: str = "",
        **tags: str,
    ) -> None:
        """Record metric during operation."""
        self._observability.record_metric(
            f"{self._operation}.{name}",
            value,
            unit,
            **tags,
        )

    def get_execution_time_ms(self) -> float:
        """Get current execution time in milliseconds."""
        return (perf_counter() - self._start_time) * 1000


class FlextDbOracleErrorHandler:
    """Centralized error handling following DRY and SOLID principles."""

    def __init__(self, observability: FlextDbOracleObservabilityManager) -> None:
        """Initialize error handler."""
        self._observability = observability
        self._logger = get_logger(
            f"FlextDbOracleErrorHandler.{observability._context_name}",  # noqa: SLF001
        )

    def handle_connection_error(self, error: str | None) -> None:
        """Handle connection errors with proper metrics and tracing."""
        self._observability.record_metric(
            "error.connection",
            1,
            "count",
            error_type="connection_failure",
        )
        self._logger.error("Connection error: %s", error)
        msg = f"Failed to connect: {error}"
        raise ConnectionError(msg)

    def handle_config_error(self) -> None:
        """Handle configuration errors."""
        self._observability.record_metric(
            "error.configuration",
            1,
            "count",
            error_type="missing_config",
        )
        self._logger.error("Configuration error: No configuration provided")
        msg = "No configuration provided"
        raise ValueError(msg)

    def handle_query_error(
        self,
        error: str,
        sql: str | None = None,
    ) -> FlextResult[None]:
        """Handle query errors with context."""
        self._observability.record_metric(
            "error.query",
            1,
            "count",
            error_type="query_failure",
        )
        if sql:
            self._logger.error("Query error for SQL '%s': %s", sql[:100], error)
        else:
            self._logger.error("Query error: %s", error)
        return FlextResult.fail(error)

    def handle_plugin_error(self, plugin_name: str, error: str) -> FlextResult[None]:
        """Handle plugin errors."""
        self._observability.record_metric(
            "error.plugin",
            1,
            "count",
            plugin_name=plugin_name,
        )
        self._logger.error("Plugin '%s' error: %s", plugin_name, error)
        return FlextResult.fail(f"{plugin_name} plugin failed: {error}")


__all__ = [
    "FlextDbOracleErrorHandler",
    "FlextDbOracleObservabilityManager",
    "FlextDbOracleOperationTracker",
]
