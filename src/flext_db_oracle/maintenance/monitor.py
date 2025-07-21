"""Oracle database performance monitoring utilities.

Built on flext-core foundation for comprehensive performance monitoring.
Uses ServiceResult pattern and async operations for robust monitoring.
"""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Any

from flext_core import DomainValueObject, Field, ServiceResult
from flext_observability.logging import get_logger

if TYPE_CHECKING:
    from flext_db_oracle.application.services import OracleConnectionService

logger = get_logger(__name__)


class SGAComponent(DomainValueObject):
    """Oracle SGA component information."""

    name: str = Field(..., description="Component name")
    current_size: int = Field(..., description="Current size in bytes", ge=0)
    min_size: int = Field(0, description="Minimum size in bytes", ge=0)
    max_size: int = Field(0, description="Maximum size in bytes", ge=0)
    unit: str = Field("bytes", description="Size unit")

    @property
    def size_mb(self) -> float:
        """Get size in MB."""
        return self.current_size / (1024 * 1024)


class WaitEvent(DomainValueObject):
    """Oracle wait event information."""

    event: str = Field(..., description="Wait event name")
    total_waits: int = Field(0, description="Total number of waits", ge=0)
    total_timeouts: int = Field(0, description="Total number of timeouts", ge=0)
    time_waited: float = Field(
        0.0,
        description="Total time waited in centiseconds",
        ge=0.0,
    )
    average_wait: float = Field(
        0.0,
        description="Average wait time in centiseconds",
        ge=0.0,
    )

    @property
    def time_waited_seconds(self) -> float:
        """Get time waited in seconds."""
        return self.time_waited / 100.0

    @property
    def average_wait_ms(self) -> float:
        """Get average wait time in milliseconds."""
        return self.average_wait * 10.0


class SessionStatistics(DomainValueObject):
    """Oracle session statistics."""

    total_sessions: int = Field(..., description="Total sessions", ge=0)
    active_sessions: int = Field(..., description="Active sessions", ge=0)
    inactive_sessions: int = Field(..., description="Inactive sessions", ge=0)
    blocked_sessions: int = Field(0, description="Blocked sessions", ge=0)
    system_sessions: int = Field(0, description="System sessions", ge=0)

    @property
    def active_percentage(self) -> float:
        """Get percentage of active sessions."""
        if self.total_sessions == 0:
            return 0.0
        return (self.active_sessions / self.total_sessions) * 100.0


class DatabaseMetrics(DomainValueObject):
    """Complete database performance metrics."""

    timestamp: datetime = Field(
        default_factory=datetime.now,
        description="Metrics timestamp",
    )
    sga_components: list[SGAComponent] = Field(
        default_factory=list,
        description="SGA components",
    )
    wait_events: list[WaitEvent] = Field(
        default_factory=list,
        description="Wait events",
    )
    session_stats: SessionStatistics | None = Field(
        None,
        description="Session statistics",
    )
    buffer_cache_hit_ratio: float | None = Field(
        None,
        description="Buffer cache hit ratio",
        ge=0.0,
        le=100.0,
    )
    library_cache_hit_ratio: float | None = Field(
        None,
        description="Library cache hit ratio",
        ge=0.0,
        le=100.0,
    )

    @property
    def total_sga_size_mb(self) -> float:
        """Get total SGA size in MB."""
        return sum(comp.size_mb for comp in self.sga_components)

    @property
    def top_wait_events(self) -> list[WaitEvent]:
        """Get top 5 wait events by time waited."""
        return sorted(self.wait_events, key=lambda x: x.time_waited, reverse=True)[:5]


class PerformanceMonitor:
    """Monitors Oracle database performance metrics using flext-core patterns."""

    def __init__(self, connection_service: OracleConnectionService) -> None:
        """Initialize the performance monitor.

        Args:
            connection_service: Oracle connection service for database operations

        """
        self.connection_service = connection_service

    async def get_performance_metrics(self) -> ServiceResult[DatabaseMetrics]:
        """Get comprehensive performance metrics."""
        try:
            logger.info("Collecting performance metrics")

            # Collect all metrics
            sga_result = await self.get_sga_info()
            wait_events_result = await self.get_wait_events()
            session_stats_result = await self.get_session_stats()
            cache_hit_ratios_result = await self.get_cache_hit_ratios()

            # Get cache hit ratios if available
            buffer_cache_hit_ratio = None
            library_cache_hit_ratio = None
            if cache_hit_ratios_result.is_success and cache_hit_ratios_result.value:
                cache_ratios = cache_hit_ratios_result.value
                buffer_cache_hit_ratio = cache_ratios.get("buffer_cache")
                library_cache_hit_ratio = cache_ratios.get("library_cache")

            # Build metrics object with all values
            metrics = DatabaseMetrics(
                sga_components=(sga_result.value or [])
                if sga_result.is_success
                else [],
                wait_events=(
                    (wait_events_result.value or [])
                    if wait_events_result.is_success
                    else []
                ),
                session_stats=(
                    session_stats_result.value
                    if session_stats_result.is_success
                    else None
                ),
                buffer_cache_hit_ratio=buffer_cache_hit_ratio,
                library_cache_hit_ratio=library_cache_hit_ratio,
            )

            logger.info("Performance metrics collected successfully")
            return ServiceResult.ok(metrics)

        except Exception as e:
            logger.exception("Failed to get performance metrics")
            return ServiceResult.fail(f"Failed to get performance metrics: {e}")

    async def get_sga_info(self) -> ServiceResult[list[SGAComponent]]:
        """Get SGA component information."""
        try:
            query = """
                SELECT
                    component,
                    current_size,
                    min_size,
                    max_size
                FROM v$sga_dynamic_components
                WHERE current_size > 0
                ORDER BY current_size DESC
            """

            result = await self.connection_service.execute_query(query)

            if not result.is_success:
                return ServiceResult.fail(result.error or "Failed to get SGA info")

            if not result.value or not result.value.rows:
                return ServiceResult.ok([])

            components = []
            for row in result.value.rows:
                component = SGAComponent(
                    name=row[0],
                    current_size=row[1],
                    min_size=row[2],
                    max_size=row[3],
                    unit="bytes",
                )
                components.append(component)

            logger.info("Retrieved %d SGA components", len(components))
            return ServiceResult.ok(components)

        except Exception as e:
            logger.exception("Failed to get SGA info")
            return ServiceResult.fail(f"Failed to get SGA info: {e}")

    async def get_wait_events(self, limit: int = 10) -> ServiceResult[list[WaitEvent]]:
        """Get top wait events by time waited."""
        try:
            query = """
                SELECT
                    event,
                    total_waits,
                    total_timeouts,
                    time_waited,
                    average_wait
                FROM v$system_event
                WHERE total_waits > 0
                AND event NOT LIKE 'SQL*Net%'
                ORDER BY time_waited DESC
                FETCH FIRST :limit ROWS ONLY
            """

            result = await self.connection_service.execute_query(
                query,
                {"limit": limit},
            )

            if not result.is_success:
                return ServiceResult.fail(result.error or "Failed to get wait events")

            if not result.value or not result.value.rows:
                return ServiceResult.ok([])

            events = []
            for row in result.value.rows:
                event = WaitEvent(
                    event=row[0],
                    total_waits=row[1],
                    total_timeouts=row[2],
                    time_waited=row[3],
                    average_wait=row[4],
                )
                events.append(event)

            logger.info("Retrieved %d wait events", len(events))
            return ServiceResult.ok(events)

        except Exception as e:
            logger.exception("Failed to get wait events")
            return ServiceResult.fail(f"Failed to get wait events: {e}")

    async def get_session_stats(self) -> ServiceResult[SessionStatistics]:
        """Get session statistics."""
        try:
            query = """
                SELECT
                    COUNT(*) as total_sessions,
                    COUNT(CASE WHEN status = 'ACTIVE' THEN 1 END) as active_sessions,
                    COUNT(CASE WHEN status = 'INACTIVE' THEN 1 END)
                    as inactive_sessions,
                    COUNT(CASE WHEN blocking_session IS NOT NULL THEN 1 END)
                    as blocked_sessions,
                    COUNT(CASE WHEN username IS NULL THEN 1 END) as system_sessions
                FROM v$session
            """

            result = await self.connection_service.execute_query(query)

            if not result.is_success:
                return ServiceResult.fail(result.error or "Failed to get session stats")

            if not result.value or not result.value.rows:
                return ServiceResult.fail("No session data found")

            row = result.value.rows[0]
            stats = SessionStatistics(
                total_sessions=row[0],
                active_sessions=row[1],
                inactive_sessions=row[2],
                blocked_sessions=row[3],
                system_sessions=row[4],
            )

            logger.info(
                "Retrieved session statistics: %d total, %d active",
                stats.total_sessions,
                stats.active_sessions,
            )
            return ServiceResult.ok(stats)

        except Exception as e:
            logger.exception("Failed to get session stats")
            return ServiceResult.fail(f"Failed to get session stats: {e}")

    async def get_cache_hit_ratios(self) -> ServiceResult[dict[str, float]]:
        """Get cache hit ratios."""
        try:
            # Buffer cache hit ratio
            buffer_cache_query = """
                SELECT
                    ROUND((1 - (phy.value / (db.value + cons.value))) * 100, 2)
                    as hit_ratio
                FROM
                    v$sysstat phy,
                    v$sysstat db,
                    v$sysstat cons
                WHERE
                    phy.name = 'physical reads'
                    AND db.name = 'db block gets'
                    AND cons.name = 'consistent gets'
            """

            # Library cache hit ratio
            library_cache_query = """
                SELECT
                    ROUND((1 - (misses / gets)) * 100, 2) as hit_ratio
                FROM v$librarycache
                WHERE namespace = 'SQL AREA'
                AND gets > 0
            """

            buffer_result = await self.connection_service.execute_query(
                buffer_cache_query,
            )
            library_result = await self.connection_service.execute_query(
                library_cache_query,
            )

            ratios = {}

            if (
                buffer_result.is_success
                and buffer_result.value
                and buffer_result.value.rows
            ):
                ratios["buffer_cache"] = buffer_result.value.rows[0][0]

            if (
                library_result.is_success
                and library_result.value
                and library_result.value.rows
            ):
                ratios["library_cache"] = library_result.value.rows[0][0]

            logger.info("Retrieved cache hit ratios: %s", ratios)
            return ServiceResult.ok(ratios)

        except Exception as e:
            logger.exception("Failed to get cache hit ratios")
            return ServiceResult.fail(f"Failed to get cache hit ratios: {e}")

    async def get_tablespace_usage(self) -> ServiceResult[list[dict[str, Any]]]:
        """Get tablespace usage information."""
        try:
            query = """
                SELECT
                    ts.tablespace_name,
                    NVL(df.total_size, 0) as total_size,
                    NVL(df.total_size - fs.free_space, 0) as used_size,
                    NVL(fs.free_space, 0) as free_space,
                    ROUND(NVL((df.total_size - fs.free_space)
                          / df.total_size * 100, 0), 2) as used_percent
                FROM
                    dba_tablespaces ts
                LEFT JOIN (
                    SELECT
                        tablespace_name,
                        SUM(bytes) as total_size
                    FROM dba_data_files
                    GROUP BY tablespace_name
                ) df ON ts.tablespace_name = df.tablespace_name
                LEFT JOIN (
                    SELECT
                        tablespace_name,
                        SUM(bytes) as free_space
                    FROM dba_free_space
                    GROUP BY tablespace_name
                ) fs ON ts.tablespace_name = fs.tablespace_name
                WHERE ts.contents != 'TEMPORARY'
                ORDER BY used_percent DESC
            """

            result = await self.connection_service.execute_query(query)

            if not result.is_success:
                return ServiceResult.fail(
                    result.error or "Failed to get tablespace usage",
                )

            if not result.value or not result.value.rows:
                return ServiceResult.ok([])

            tablespaces = []
            for row in result.value.rows:
                tablespace = {
                    "name": row[0],
                    "total_size_bytes": row[1],
                    "used_size_bytes": row[2],
                    "free_space_bytes": row[3],
                    "used_percent": row[4],
                    "total_size_mb": (row[1] / (1024 * 1024)) if row[1] else 0,
                    "used_size_mb": (row[2] / (1024 * 1024)) if row[2] else 0,
                    "free_space_mb": (row[3] / (1024 * 1024)) if row[3] else 0,
                }
                tablespaces.append(tablespace)

            logger.info("Retrieved usage for %d tablespaces", len(tablespaces))
            return ServiceResult.ok(tablespaces)

        except Exception as e:
            logger.exception("Failed to get tablespace usage")
            return ServiceResult.fail(f"Failed to get tablespace usage: {e}")

    async def get_active_sessions(
        self,
        limit: int = 20,
    ) -> ServiceResult[list[dict[str, Any]]]:
        """Get information about active sessions."""
        try:
            query = """
                SELECT
                    sid,
                    serial#,
                    username,
                    program,
                    machine,
                    osuser,
                    status,
                    TO_CHAR(logon_time, 'YYYY-MM-DD HH24:MI:SS') as logon_time,
                    sql_id,
                    blocking_session,
                    wait_class,
                    event
                FROM v$session
                WHERE status = 'ACTIVE'
                AND username IS NOT NULL
                ORDER BY logon_time DESC
                FETCH FIRST :limit ROWS ONLY
            """

            result = await self.connection_service.execute_query(
                query,
                {"limit": limit},
            )

            if not result.is_success:
                return ServiceResult.fail(
                    result.error or "Failed to get active sessions",
                )

            if not result.value or not result.value.rows:
                return ServiceResult.ok([])

            sessions = []
            for row in result.value.rows:
                session = {
                    "sid": row[0],
                    "serial": row[1],
                    "username": row[2],
                    "program": row[3],
                    "machine": row[4],
                    "osuser": row[5],
                    "status": row[6],
                    "logon_time": row[7],
                    "sql_id": row[8],
                    "blocking_session": row[9],
                    "wait_class": row[10],
                    "event": row[11],
                }
                sessions.append(session)

            logger.info("Retrieved %d active sessions", len(sessions))
            return ServiceResult.ok(sessions)

        except Exception as e:
            logger.exception("Failed to get active sessions")
            return ServiceResult.fail(f"Failed to get active sessions: {e}")

    async def generate_performance_report(self) -> ServiceResult[dict[str, Any]]:
        """Generate comprehensive performance report."""
        try:
            # Get all performance data
            metrics_result = await self.get_performance_metrics()
            tablespace_result = await self.get_tablespace_usage()
            active_sessions_result = await self.get_active_sessions()

            if not metrics_result.is_success:
                return ServiceResult.fail(
                    metrics_result.error or "Failed to get performance metrics",
                )

            metrics = metrics_result.value
            if not metrics:
                return ServiceResult.fail("Performance metrics data is empty")

            report = {
                "timestamp": metrics.timestamp.isoformat(),
                "sga": {
                    "total_size_mb": metrics.total_sga_size_mb,
                    "components": [
                        comp.model_dump() for comp in metrics.sga_components[:10]
                    ],
                },
                "sessions": (
                    metrics.session_stats.model_dump() if metrics.session_stats else {}
                ),
                "cache_hit_ratios": {
                    "buffer_cache": metrics.buffer_cache_hit_ratio,
                    "library_cache": metrics.library_cache_hit_ratio,
                },
                "top_wait_events": [
                    event.model_dump() for event in metrics.top_wait_events
                ],
                "tablespaces": (
                    tablespace_result.value if tablespace_result.is_success else []
                ),
                "active_sessions_count": (
                    len(active_sessions_result.value or [])
                    if active_sessions_result.is_success
                    else 0
                ),
            }

            logger.info("Generated performance report")
            return ServiceResult.ok(report)

        except Exception as e:
            logger.exception("Failed to generate performance report")
            return ServiceResult.fail(f"Failed to generate performance report: {e}")
