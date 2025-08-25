"""FLEXT DB Oracle Operation Tracking following Flext[Area][Module] pattern.

This module provides the FlextDbOracleOperationTracking class with consolidated
operation tracking functionality following FLEXT architectural patterns with
DRY principles.

Single consolidated class containing ALL Oracle operation tracking components organized
internally, following SOLID principles and eliminating duplication.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from time import perf_counter
from typing import Self

from flext_core import FlextFactory

from .observability import FlextDbOracleObservabilityManager, FlextTrace


class FlextDbOracleOperationTracking(FlextFactory):
    """Oracle Database Operation Tracking following Flext[Area][Module] pattern.

    Single consolidated class containing ALL Oracle operation tracking functionality
    organized internally, following SOLID principles and DRY methodology.

    This class consolidates ALL Oracle operation tracking functionality into a single
    entry point eliminating duplication and multiple small classes.
    """

    # =============================================================================
    # INTERNAL OPERATION TRACKER CLASS - Consolidated operation tracking implementation
    # =============================================================================

    class _InternalOperationTracker:
        """Internal Oracle operation tracker consolidated into FlextDbOracleOperationTracking.

        DRY CONSOLIDATION: Moved from separate FlextDbOracleOperationTracker class to eliminate
        multiple small classes and follow DRY principles with large consolidated class.

        Context manager for tracking Oracle database operations.
        Automatically creates traces, records timing metrics, and handles errors.
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

    # =============================================================================
    # FACTORY METHODS - Consolidated operation tracker creation
    # =============================================================================

    @classmethod
    def create_operation_tracker(
        cls,
        observability_manager: FlextDbOracleObservabilityManager,
        operation: str,
        **attributes: object,
    ) -> _InternalOperationTracker:
        """Create Oracle operation tracker using consolidated internal class."""
        return cls._InternalOperationTracker(observability_manager, operation, **attributes)



# =============================================================================
# BACKWARD COMPATIBILITY ALIASES - DRY CONSOLIDATION
# =============================================================================

# Backward compatibility alias for FlextDbOracleOperationTracker
FlextDbOracleOperationTracker = FlextDbOracleOperationTracking._InternalOperationTracker

__all__: list[str] = [
    "FlextDbOracleOperationTracker",  # Backward compatibility
    "FlextDbOracleOperationTracking",
]
