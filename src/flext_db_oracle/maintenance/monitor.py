"""Oracle database performance monitoring utilities."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from ..connection.connection import OracleConnection

logger = logging.getLogger(__name__)


class PerformanceMonitor:
    """Monitors Oracle database performance metrics."""

    def __init__(self, connection: OracleConnection) -> None:
        """Initialize performance monitor.

        Args:
            connection: Database connection.
        """
        self.connection = connection

    def get_performance_metrics(self) -> dict[str, Any]:
        """Get basic performance metrics.

        Returns:
            Performance metrics.
        """
        metrics = {}

        # Get SGA information
        metrics["sga"] = self._get_sga_info()

        # Get wait events
        metrics["wait_events"] = self._get_wait_events()

        # Get session statistics
        metrics["sessions"] = self._get_session_stats()

        return metrics

    def _get_sga_info(self) -> dict[str, Any]:
        """Get System Global Area information."""
        try:
            sql = """
            SELECT
                name,
                value,
                unit
            FROM v$sga_dynamic_components
            WHERE current_size > 0
            ORDER BY current_size DESC
            """

            results = self.connection.fetch_all(sql)

            components = []
            for row in results:
                components.append(
                    {
                        "name": row[0],
                        "value": row[1],
                        "unit": row[2],
                    }
                )

            return {
                "status": "success",
                "components": components,
            }

        except Exception as e:
            logger.error("Failed to get SGA info: %s", e)
            return {"status": "failed", "error": str(e)}

    def _get_wait_events(self) -> dict[str, Any]:
        """Get top wait events."""
        try:
            sql = """
            SELECT
                event,
                total_waits,
                total_timeouts,
                time_waited,
                average_wait
            FROM v$system_event
            WHERE total_waits > 0
            ORDER BY time_waited DESC
            FETCH FIRST 10 ROWS ONLY
            """

            results = self.connection.fetch_all(sql)

            events = []
            for row in results:
                events.append(
                    {
                        "event": row[0],
                        "total_waits": row[1],
                        "total_timeouts": row[2],
                        "time_waited": row[3],
                        "average_wait": row[4],
                    }
                )

            return {
                "status": "success",
                "events": events,
            }

        except Exception as e:
            logger.error("Failed to get wait events: %s", e)
            return {"status": "failed", "error": str(e)}

    def _get_session_stats(self) -> dict[str, Any]:
        """Get session statistics."""
        try:
            sql = """
            SELECT
                COUNT(*) as total_sessions,
                COUNT(CASE WHEN status = 'ACTIVE' THEN 1 END) as active_sessions,
                COUNT(CASE WHEN status = 'INACTIVE' THEN 1 END) as inactive_sessions
            FROM v$session
            WHERE username IS NOT NULL
            """

            result = self.connection.fetch_one(sql)

            if result:
                return {
                    "status": "success",
                    "total_sessions": result[0],
                    "active_sessions": result[1],
                    "inactive_sessions": result[2],
                }

            return {"status": "no_data"}

        except Exception as e:
            logger.error("Failed to get session stats: %s", e)
            return {"status": "failed", "error": str(e)}
