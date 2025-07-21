"""Oracle database health checking utilities.

Built on flext-core foundation for comprehensive health monitoring.
Uses ServiceResult pattern and async operations for robust health checks.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from flext_core import DomainValueObject, Field, ServiceResult
from flext_observability.logging import get_logger

if TYPE_CHECKING:
    from flext_db_oracle.application.services import OracleConnectionService

logger = get_logger(__name__)

# Performance assessment thresholds
EXCELLENT_BUFFER_HIT = 95.0
EXCELLENT_LIBRARY_HIT = 95.0
EXCELLENT_SHARED_POOL_USAGE = 80.0

GOOD_BUFFER_HIT = 90.0
GOOD_LIBRARY_HIT = 90.0
GOOD_SHARED_POOL_USAGE = 90.0

ACCEPTABLE_BUFFER_HIT = 80.0
ACCEPTABLE_LIBRARY_HIT = 80.0
ACCEPTABLE_SHARED_POOL_USAGE = 95.0

# Health assessment thresholds
HIGH_REDO_ACTIVITY_THRESHOLD = 4
MAX_ACCEPTABLE_FAILURES = 1
MAX_CONCERNING_FAILURES = 2


class DatabaseHealth(DomainValueObject):
    """Overall database health status."""

    connection_status: str = Field(..., description="Connection status")
    tablespace_status: str = Field(..., description="Tablespace status")
    session_status: str = Field(..., description="Session status")
    overall_status: str = Field(..., description="Overall health status")
    details: dict[str, Any] = Field(
        default_factory=dict,
        description="Health check details",
    )

    @property
    def is_healthy(self) -> bool:
        """Check if database is overall healthy."""
        return self.overall_status == "healthy"


class TablespaceInfo(DomainValueObject):
    """Tablespace information."""

    name: str = Field(..., description="Tablespace name")
    status: str = Field(..., description="Tablespace status")
    contents: str = Field(..., description="Tablespace contents type")
    logging: str = Field(..., description="Logging status")
    size_mb: float | None = Field(None, description="Size in MB", ge=0.0)
    used_mb: float | None = Field(None, description="Used space in MB", ge=0.0)
    free_mb: float | None = Field(None, description="Free space in MB", ge=0.0)

    @property
    def usage_percent(self) -> float:
        """Calculate usage percentage."""
        if self.size_mb and self.used_mb:
            return (self.used_mb / self.size_mb) * 100
        return 0.0


class SessionInfo(DomainValueObject):
    """Database session information."""

    username: str | None = Field(None, description="Session username")
    status: str = Field(..., description="Session status")
    machine: str | None = Field(None, description="Client machine")
    program: str | None = Field(None, description="Client program")
    logon_time: str | None = Field(None, description="Logon timestamp")
    sql_id: str | None = Field(None, description="Current SQL ID")


class HealthChecker:
    """Monitors Oracle database health and performance using flext-core patterns."""

    def __init__(self, connection_service: OracleConnectionService) -> None:
        """Initialize the health checker.

        Args:
            connection_service: Oracle connection service for database operations

        """
        self.connection_service = connection_service

    async def check_overall_health(self) -> ServiceResult[DatabaseHealth]:
        """Perform comprehensive health check."""
        try:
            logger.info("Starting comprehensive health check")

            # Perform individual checks
            connection_result = await self.check_connection()
            tablespace_result = await self.check_tablespaces()
            session_result = await self.check_sessions()

            # Determine overall status
            overall_status = "healthy"
            if (
                not connection_result.is_success
                or not tablespace_result.is_success
                or not session_result.is_success
            ):
                overall_status = "unhealthy"

            health = DatabaseHealth(
                connection_status=(
                    "healthy" if connection_result.is_success else "unhealthy"
                ),
                tablespace_status=(
                    "healthy" if tablespace_result.is_success else "unhealthy"
                ),
                session_status="healthy" if session_result.is_success else "unhealthy",
                overall_status=overall_status,
                details={
                    "connection": (
                        connection_result.data
                        if connection_result.is_success
                        else connection_result.error
                    ),
                    "tablespaces": (
                        tablespace_result.data if tablespace_result.is_success else []
                    ),
                    "sessions": (
                        session_result.data if session_result.is_success else []
                    ),
                },
            )

            logger.info("Health check completed: %s", overall_status)
            return ServiceResult.ok(health)

        except Exception as e:
            logger.exception("Health check failed")
            return ServiceResult.fail(f"Health check failed: {e}")

    async def check_connection(self) -> ServiceResult[dict[str, Any]]:
        """Check database connection health."""
        try:
            result = await self.connection_service.execute_query("SELECT 1 FROM DUAL")

            if not result.is_success:
                return ServiceResult.fail(
                    result.error or "Connection health check failed",
                )

            if not result.data or not result.data.rows:
                return ServiceResult.fail("Connection test query returned no data")

            connection_info = {
                "status": "active",
                "test_query": "passed",
                "result": result.data.rows[0][0] if result.data.rows else None,
            }

            logger.info("Connection health check passed")
            return ServiceResult.ok(connection_info)

        except Exception as e:
            logger.exception("Connection health check failed")
            return ServiceResult.fail(f"Connection check failed: {e}")

    async def check_tablespaces(self) -> ServiceResult[list[TablespaceInfo]]:
        """Check tablespace health and usage."""
        try:
            query = """
                SELECT
                    ts.tablespace_name,
                    ts.status,
                    ts.contents,
                    ts.logging,
                    NVL(df.total_size, 0) / 1024 / 1024 as size_mb,
                    NVL(df.total_size - fs.free_space, 0) / 1024 / 1024 as used_mb,
                    NVL(fs.free_space, 0) / 1024 / 1024 as free_mb
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
                ORDER BY ts.tablespace_name
            """

            result = await self.connection_service.execute_query(query)

            if not result.is_success:
                return ServiceResult.fail(result.error or "Failed to check tablespaces")

            if not result.data or not result.data.rows:
                return ServiceResult.ok([])

            tablespaces = []
            for row in result.data.rows:
                tablespace = TablespaceInfo(
                    name=row[0],
                    status=row[1],
                    contents=row[2],
                    logging=row[3],
                    size_mb=row[4],
                    used_mb=row[5],
                    free_mb=row[6],
                )
                tablespaces.append(tablespace)

            logger.info("Retrieved health info for %d tablespaces", len(tablespaces))
            return ServiceResult.ok(tablespaces)

        except Exception as e:
            logger.exception("Tablespace health check failed")
            return ServiceResult.fail(f"Tablespace check failed: {e}")

    async def check_sessions(self, limit: int = 50) -> ServiceResult[list[SessionInfo]]:
        """Check active database sessions."""
        try:
            query = """
                SELECT
                    username,
                    status,
                    machine,
                    program,
                    TO_CHAR(logon_time, 'YYYY-MM-DD HH24:MI:SS') as logon_time,
                    sql_id
                FROM v$session
                WHERE username IS NOT NULL
                ORDER BY logon_time DESC
                FETCH FIRST :limit ROWS ONLY
            """

            result = await self.connection_service.execute_query(
                query,
                {"limit": limit},
            )

            if not result.is_success:
                return ServiceResult.fail(result.error or "Failed to check sessions")

            if not result.data or not result.data.rows:
                return ServiceResult.ok([])

            sessions = []
            for row in result.data.rows:
                session = SessionInfo(
                    username=row[0],
                    status=row[1],
                    machine=row[2],
                    program=row[3],
                    logon_time=row[4],
                    sql_id=row[5],
                )
                sessions.append(session)

            logger.info("Retrieved info for %d active sessions", len(sessions))
            return ServiceResult.ok(sessions)

        except Exception as e:
            logger.exception("Session health check failed")
            return ServiceResult.fail(f"Session check failed: {e}")

    async def generate_health_report(self) -> ServiceResult[dict[str, Any]]:
        """Generate comprehensive health report."""
        try:
            health_result = await self.check_overall_health()

            if not health_result.is_success:
                return ServiceResult.fail(
                    health_result.error or "Failed to check overall health",
                )

            health = health_result.data
            if not health:
                return ServiceResult.fail("Health check data is empty")

            report = {
                "timestamp": health.details.get("timestamp", "N/A"),
                "overall_status": health.overall_status,
                "is_healthy": health.is_healthy,
                "components": {
                    "connection": health.connection_status,
                    "tablespaces": health.tablespace_status,
                    "sessions": health.session_status,
                },
                "details": health.details,
                "summary": f"Database is {health.overall_status}",
            }

            logger.info("Generated health report: %s", health.overall_status)
            return ServiceResult.ok(report)

        except Exception as e:
            logger.exception("Failed to generate health report")
            return ServiceResult.fail(f"Health report generation failed: {e}")

    async def check_database_performance_metrics(self) -> ServiceResult[dict[str, Any]]:
        """Check key Oracle database performance metrics."""
        try:
            # Get buffer cache hit ratio
            buffer_cache_query = """
                SELECT
                    (1 - (phy.data / (cur.data + con.data))) * 100
                    as buffer_hit_ratio
                FROM
                    v$sysstat phy,
                    v$sysstat cur,
                    v$sysstat con
                WHERE
                    phy.name = 'physical reads'
                    AND cur.name = 'db block gets'
                    AND con.name = 'consistent gets'
            """

            buffer_result = await self.connection_service.execute_query(
                buffer_cache_query,
            )
            buffer_hit_ratio = (
                buffer_result.data.rows[0][0]
                if buffer_result.is_success
                and buffer_result.data
                and buffer_result.data.rows
                else 0
            )

            # Get library cache hit ratio
            library_cache_query = """
                SELECT
                    SUM(pinhits) / SUM(pins) * 100 as library_cache_hit_ratio
                FROM v$librarycache
                WHERE pins > 0
            """

            library_result = await self.connection_service.execute_query(
                library_cache_query,
            )
            library_hit_ratio = (
                library_result.data.rows[0][0]
                if library_result.is_success
                and library_result.data
                and library_result.data.rows
                else 0
            )

            # Get shared pool usage
            shared_pool_query = """
                SELECT
                    ROUND((1 - (bytes / max_size)) * 100, 2) as shared_pool_used_pct
                FROM (
                    SELECT
                        SUM(bytes) as bytes,
                        MAX(max_size) as max_size
                    FROM v$sgastat
                    WHERE pool = 'shared pool'
                )
            """

            shared_pool_result = await self.connection_service.execute_query(
                shared_pool_query,
            )
            shared_pool_used = (
                shared_pool_result.data.rows[0][0]
                if shared_pool_result.is_success
                and shared_pool_result.data
                and shared_pool_result.data.rows
                else 0
            )

            # Get PGA usage
            pga_query = """
                SELECT
                    ROUND(value / 1024 / 1024, 2) as pga_used_mb
                FROM v$pgastat
                WHERE name = 'total PGA allocated'
            """

            pga_result = await self.connection_service.execute_query(pga_query)
            pga_used_mb = (
                pga_result.data.rows[0][0]
                if pga_result.is_success and pga_result.data and pga_result.data.rows
                else 0
            )

            # Get active sessions count
            sessions_query = """
                SELECT
                    COUNT(*) as active_sessions
                FROM v$session
                WHERE status = 'ACTIVE'
                AND username IS NOT NULL
            """

            sessions_result = await self.connection_service.execute_query(
                sessions_query,
            )
            active_sessions = (
                sessions_result.data.rows[0][0]
                if sessions_result.is_success
                and sessions_result.data
                and sessions_result.data.rows
                else 0
            )

            # Get wait events summary
            wait_events_query = """
                SELECT
                    event,
                    total_waits,
                    time_waited
                FROM v$system_event
                WHERE wait_class != 'Idle'
                AND total_waits > 0
                ORDER BY time_waited DESC
                FETCH FIRST 5 ROWS ONLY
            """

            wait_result = await self.connection_service.execute_query(wait_events_query)
            top_wait_events = (
                [
                    {
                        "event": row[0],
                        "total_waits": row[1],
                        "time_waited": row[2],
                    }
                    for row in wait_result.data.rows
                ]
                if wait_result.is_success and wait_result.data and wait_result.data.rows
                else []
            )

            metrics = {
                "buffer_cache_hit_ratio": round(buffer_hit_ratio, 2),
                "library_cache_hit_ratio": round(library_hit_ratio, 2),
                "shared_pool_used_percent": round(shared_pool_used, 2),
                "pga_used_mb": pga_used_mb,
                "active_sessions": active_sessions,
                "top_wait_events": top_wait_events,
                "performance_assessment": self._assess_performance_metrics(
                    buffer_hit_ratio,
                    library_hit_ratio,
                    shared_pool_used,
                ),
            }

            logger.info("Retrieved database performance metrics")
            return ServiceResult.ok(metrics)

        except Exception as e:
            logger.exception("Failed to check performance metrics")
            return ServiceResult.fail(f"Failed to check performance metrics: {e}")

    def _assess_performance_metrics(
        self,
        buffer_hit: float,
        library_hit: float,
        shared_pool_used: float,
    ) -> str:
        """Assess overall performance based on key metrics."""
        if (
            buffer_hit > EXCELLENT_BUFFER_HIT
            and library_hit > EXCELLENT_LIBRARY_HIT
            and shared_pool_used < EXCELLENT_SHARED_POOL_USAGE
        ):
            return "excellent"
        if (
            buffer_hit > GOOD_BUFFER_HIT
            and library_hit > GOOD_LIBRARY_HIT
            and shared_pool_used < GOOD_SHARED_POOL_USAGE
        ):
            return "good"
        if (
            buffer_hit > ACCEPTABLE_BUFFER_HIT
            and library_hit > ACCEPTABLE_LIBRARY_HIT
            and shared_pool_used < ACCEPTABLE_SHARED_POOL_USAGE
        ):
            return "acceptable"
        return "poor"

    async def check_database_locks(self) -> ServiceResult[dict[str, Any]]:
        """Check for database locks and blocking sessions."""
        try:
            # Get blocking sessions
            blocking_query = """
                SELECT
                    s1.username as blocking_user,
                    s1.sid as blocking_sid,
                    s1.serial# as blocking_serial,
                    s2.username as blocked_user,
                    s2.sid as blocked_sid,
                    s2.serial# as blocked_serial,
                    l1.type as lock_type,
                    l1.mode_held,
                    l1.mode_requested
                FROM
                    v$lock l1,
                    v$session s1,
                    v$lock l2,
                    v$session s2
                WHERE
                    l1.sid = s1.sid
                    AND l2.sid = s2.sid
                    AND l1.id1 = l2.id1
                    AND l1.id2 = l2.id2
                    AND l1.type = l2.type
                    AND l1.mode_held > 0
                    AND l2.mode_requested > 0
                    AND l1.sid != l2.sid
            """

            blocking_result = await self.connection_service.execute_query(
                blocking_query,
            )

            blocking_sessions = []
            if (
                blocking_result.is_success
                and blocking_result.data
                and blocking_result.data.rows
            ):
                blocking_sessions = [
                    {
                        "blocking_user": row[0],
                        "blocking_sid": row[1],
                        "blocking_serial": row[2],
                        "blocked_user": row[3],
                        "blocked_sid": row[4],
                        "blocked_serial": row[5],
                        "lock_type": row[6],
                        "mode_held": row[7],
                        "mode_requested": row[8],
                    }
                    for row in blocking_result.data.rows
                ]

            # Get total locks count
            locks_count_query = "SELECT COUNT(*) FROM v$lock WHERE mode_held > 0"
            locks_result = await self.connection_service.execute_query(
                locks_count_query,
            )
            total_locks = (
                locks_result.data.rows[0][0]
                if locks_result.is_success
                and locks_result.data
                and locks_result.data.rows
                else 0
            )

            lock_analysis = {
                "total_locks": total_locks,
                "blocking_sessions_count": len(blocking_sessions),
                "blocking_sessions": blocking_sessions,
                "lock_status": "critical" if len(blocking_sessions) > 0 else "normal",
            }

            logger.info(
                "Checked database locks: %d total, %d blocking",
                total_locks,
                len(blocking_sessions),
            )
            return ServiceResult.ok(lock_analysis)

        except Exception as e:
            logger.exception("Failed to check database locks")
            return ServiceResult.fail(f"Failed to check database locks: {e}")

    async def check_redo_log_activity(self) -> ServiceResult[dict[str, Any]]:
        """Check redo log activity and switches."""
        try:
            # Get redo log switches in last 24 hours
            log_switches_query = """
                SELECT
                    TO_CHAR(first_time, 'YYYY-MM-DD HH24') as hour,
                    COUNT(*) as switches
                FROM v$log_history
                WHERE first_time >= SYSDATE - 1
                GROUP BY TO_CHAR(first_time, 'YYYY-MM-DD HH24')
                ORDER BY hour DESC
            """

            switches_result = await self.connection_service.execute_query(
                log_switches_query,
            )

            log_switches = []
            if (
                switches_result.is_success
                and switches_result.data
                and switches_result.data.rows
            ):
                log_switches = [
                    {
                        "hour": row[0],
                        "switches": row[1],
                    }
                    for row in switches_result.data.rows
                ]

            # Get current redo log status
            redo_status_query = """
                SELECT
                    group#,
                    status,
                    archived,
                    bytes / 1024 / 1024 as size_mb
                FROM v$log
                ORDER BY group#
            """

            status_result = await self.connection_service.execute_query(
                redo_status_query,
            )

            redo_logs = []
            if (
                status_result.is_success
                and status_result.data
                and status_result.data.rows
            ):
                redo_logs = [
                    {
                        "group_number": row[0],
                        "status": row[1],
                        "archived": row[2],
                        "size_mb": round(row[3], 2),
                    }
                    for row in status_result.data.rows
                ]

            # Calculate average switches per hour
            total_switches = sum(switch["switches"] for switch in log_switches)
            avg_switches_per_hour = total_switches / max(len(log_switches), 1)

            redo_analysis = {
                "log_switches_24h": log_switches,
                "total_switches_24h": total_switches,
                "avg_switches_per_hour": round(avg_switches_per_hour, 1),
                "redo_logs_status": redo_logs,
                "redo_activity_level": (
                    "high"
                    if avg_switches_per_hour > HIGH_REDO_ACTIVITY_THRESHOLD
                    else "normal"
                ),
            }

            logger.info("Checked redo log activity: %d switches in 24h", total_switches)
            return ServiceResult.ok(redo_analysis)

        except Exception as e:
            logger.exception("Failed to check redo log activity")
            return ServiceResult.fail(f"Failed to check redo log activity: {e}")

    async def generate_comprehensive_health_report(
        self,
    ) -> ServiceResult[dict[str, Any]]:
        """Generate comprehensive health report with all metrics."""
        try:
            logger.info("Generating comprehensive health report")

            # Get all health metrics
            basic_health_result = await self.check_overall_health()
            performance_result = await self.check_database_performance_metrics()
            locks_result = await self.check_database_locks()
            redo_result = await self.check_redo_log_activity()

            report = {
                "report_timestamp": str(logger.info),
                "basic_health": (
                    basic_health_result.data if basic_health_result.is_success else None
                ),
                "performance_metrics": (
                    performance_result.data if performance_result.is_success else None
                ),
                "lock_analysis": (
                    locks_result.data if locks_result.is_success else None
                ),
                "redo_log_analysis": (
                    redo_result.data if redo_result.is_success else None
                ),
                "overall_assessment": self._calculate_overall_assessment(
                    basic_health_result,
                    performance_result,
                    locks_result,
                    redo_result,
                ),
            }

            logger.info("Generated comprehensive health report")
            return ServiceResult.ok(report)

        except Exception as e:
            logger.exception("Failed to generate comprehensive health report")
            return ServiceResult.fail(
                f"Failed to generate comprehensive health report: {e}",
            )

    def _calculate_overall_assessment(self, *results: ServiceResult[Any]) -> str:
        """Calculate overall database assessment."""
        failure_count = sum(1 for result in results if not result.is_success)

        if failure_count == 0:
            return "excellent"
        if failure_count <= MAX_ACCEPTABLE_FAILURES:
            return "good"
        if failure_count <= MAX_CONCERNING_FAILURES:
            return "concerning"
        return "critical"
