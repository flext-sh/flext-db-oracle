"""FLEXT DB Oracle Observability following Flext[Area][Module] pattern.

This module provides the FlextDbOracleObservability class with consolidated
observability functionality following FLEXT architectural patterns with
DRY principles.

Single consolidated class containing ALL observability components organized
internally, following SOLID principles and eliminating duplication.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

from flext_core import FlextContainer, FlextFactory, FlextResult, get_logger


class FlextDbOracleObservability(FlextFactory):
    """Oracle Database Observability following Flext[Area][Module] pattern.

    Single consolidated class containing ALL observability functionality
    organized internally, following SOLID principles and DRY methodology.

    This class consolidates ALL Oracle observability functionality into a single
    entry point eliminating duplication and multiple small classes.
    """

    # =============================================================================
    # INTERNAL CLASSES - Consolidated observability components
    # =============================================================================

    class FlextTrace:
        """Consolidated trace implementation for Oracle operations."""

        def __init__(self, trace_id: str, operation_name: str, timestamp: datetime) -> None:
            """Initialize trace."""
            self.trace_id = trace_id
            self.operation_name = operation_name
            self.timestamp = timestamp
            self.attributes: dict[str, object] = {}

        def add_attribute(self, key: str, value: object) -> None:
            """Add attribute to trace."""
            self.attributes[key] = value

        def to_dict(self) -> dict[str, object]:
            """Convert trace to dictionary."""
            return {
                "trace_id": self.trace_id,
                "operation_name": self.operation_name,
                "timestamp": self.timestamp.isoformat(),
                "attributes": self.attributes,
            }

    class FlextHealthCheck:
        """Consolidated health check implementation."""

        def __init__(self, component: str, status: str, message: str = "") -> None:
            """Initialize health check."""
            self.component = component
            self.status = status
            self.message = message
            self.timestamp = datetime.now(UTC)

        def is_healthy(self) -> bool:
            """Check if component is healthy."""
            return self.status.lower() in ("healthy", "ok", "up")

        def to_dict(self) -> dict[str, object]:
            """Convert health check to dictionary."""
            return {
                "component": self.component,
                "status": self.status,
                "message": self.message,
                "timestamp": self.timestamp.isoformat(),
                "is_healthy": self.is_healthy(),
            }

    # =============================================================================
    # MAIN OBSERVABILITY MANAGER - Legacy FlextDbOracleObservabilityManager
    # =============================================================================

    class ObservabilityManager:
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
        ) -> FlextDbOracleObservability.FlextTrace:
            """Create trace for operation."""
            trace_id = str(uuid.uuid4())
            timestamp = datetime.now(UTC)
            trace = FlextDbOracleObservability.FlextTrace(trace_id, f"{self._context_name}.{operation}", timestamp)
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
        ) -> FlextResult[FlextDbOracleObservability.FlextHealthCheck]:
            """Create health check."""
            try:
                health_check = FlextDbOracleObservability.FlextHealthCheck(component, status, message)
                self._logger.debug("Health check: %s = %s", component, status)
                return FlextResult["FlextDbOracleObservability.FlextHealthCheck"].ok(health_check)
            except Exception as e:
                return FlextResult["FlextDbOracleObservability.FlextHealthCheck"].fail(
                    f"Failed to create health check: {e}"
                )

        def finish_trace(self, trace: FlextDbOracleObservability.FlextTrace, **final_attributes: object) -> FlextDbOracleObservability.FlextTrace:
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

    # =============================================================================
    # BACKWARD COMPATIBILITY ALIASES - Consolidated
    # =============================================================================

    # Create compatibility classes as internal references
    class ObservabilityComponents:
        """Backward compatibility - use FlextDbOracleObservability directly."""

        def __getattr__(self, name: str) -> object:
            """Get attribute from FlextDbOracleObservability for backward compatibility."""
            return getattr(FlextDbOracleObservability, name)


# =============================================================================
# MODULE-LEVEL BACKWARD COMPATIBILITY
# =============================================================================

# Backward compatibility for direct imports
FlextTrace = FlextDbOracleObservability.FlextTrace
FlextHealthCheck = FlextDbOracleObservability.FlextHealthCheck
FlextDbOracleObservabilityManager = FlextDbOracleObservability.ObservabilityManager

__all__ = [
    "FlextDbOracleObservability",
    "FlextDbOracleObservabilityManager",
    "FlextHealthCheck",
    "FlextTrace",
]
