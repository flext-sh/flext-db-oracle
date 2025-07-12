"""Oracle database health checking utilities.

Built on flext-core foundation for comprehensive health monitoring.
Uses ServiceResult pattern and async operations for robust health checks.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from pydantic import Field

from flext_core import DomainValueObject, ServiceResult
from flext_observability.logging import get_logger

if TYPE_CHECKING:
    from flext_db_oracle.application.services import OracleConnectionService

logger = get_logger(__name__)


class DatabaseHealth(DomainValueObject):
    """Overall database health status."""

    connection_status: str = Field(..., description="Connection status")
    tablespace_status: str = Field(..., description="Tablespace status")
    session_status: str = Field(..., description="Session status")
    overall_status: str = Field(..., description="Overall health status")
    details: dict[str, Any] = Field(default_factory=dict, description="Health check details")

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
            if (connection_result.is_failure or
                tablespace_result.is_failure or
                session_result.is_failure):
                overall_status = "unhealthy"

            health = DatabaseHealth(
                connection_status="healthy" if connection_result.is_success else "unhealthy",
                tablespace_status="healthy" if tablespace_result.is_success else "unhealthy",
                session_status="healthy" if session_result.is_success else "unhealthy",
                overall_status=overall_status,
                details={
                    "connection": connection_result.value if connection_result.is_success else connection_result.error,
                    "tablespaces": tablespace_result.value if tablespace_result.is_success else [],
                    "sessions": session_result.value if session_result.is_success else [],
                },
            )

            logger.info("Health check completed: %s", overall_status)
            return ServiceResult.success(health)

        except Exception as e:
            logger.exception("Health check failed: %s", e)
            return ServiceResult.failure(f"Health check failed: {e}")

    async def check_connection(self) -> ServiceResult[dict[str, Any]]:
        """Check database connection health."""
        try:
            result = await self.connection_service.execute_query("SELECT 1 FROM DUAL")

            if result.is_failure:
                return result

            connection_info = {
                "status": "active",
                "test_query": "passed",
                "result": result.value.rows[0][0] if result.value.rows else None,
            }

            logger.info("Connection health check passed")
            return ServiceResult.success(connection_info)

        except Exception as e:
            logger.exception("Connection health check failed: %s", e)
            return ServiceResult.failure(f"Connection check failed: {e}")

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

            if result.is_failure:
                return result

            tablespaces = []
            for row in result.value.rows:
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
            return ServiceResult.success(tablespaces)

        except Exception as e:
            logger.exception("Tablespace health check failed: %s", e)
            return ServiceResult.failure(f"Tablespace check failed: {e}")

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

            if result.is_failure:
                return result

            sessions = []
            for row in result.value.rows:
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
            return ServiceResult.success(sessions)

        except Exception as e:
            logger.exception("Session health check failed: %s", e)
            return ServiceResult.failure(f"Session check failed: {e}")

    async def generate_health_report(self) -> ServiceResult[dict[str, Any]]:
        """Generate comprehensive health report."""
        try:
            health_result = await self.check_overall_health()

            if health_result.is_failure:
                return health_result

            health = health_result.value

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
            return ServiceResult.success(report)

        except Exception as e:
            logger.exception("Failed to generate health report: %s", e)
            return ServiceResult.failure(f"Health report generation failed: {e}")
