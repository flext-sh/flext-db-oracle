"""Oracle database health checking utilities."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from ..connection.connection import OracleConnection

logger = logging.getLogger(__name__)


class HealthChecker:
    """Monitors Oracle database health and performance."""

    def __init__(self, connection: OracleConnection) -> None:
        """Initialize health checker.

        Args:
            connection: Database connection.
        """
        self.connection = connection

    def check_connection(self) -> dict[str, Any]:
        """Check database connection health.

        Returns:
            Connection health status.
        """
        try:
            result = self.connection.fetch_one("SELECT 1 FROM DUAL")
            return {
                "status": "healthy",
                "connection": "active",
                "test_query": "passed",
                "result": result[0] if result else None,
            }
        except Exception as e:
            logger.error("Health check failed: %s", e)
            return {
                "status": "unhealthy",
                "connection": "failed",
                "error": str(e),
            }

    def check_tablespaces(self) -> dict[str, Any]:
        """Check tablespace usage and health.

        Returns:
            Tablespace health information.
        """
        try:
            sql = """
            SELECT
                tablespace_name,
                status,
                contents,
                logging
            FROM dba_tablespaces
            ORDER BY tablespace_name
            """

            results = self.connection.fetch_all(sql)

            tablespaces = []
            for row in results:
                tablespaces.append(
                    {
                        "name": row[0],
                        "status": row[1],
                        "contents": row[2],
                        "logging": row[3],
                    }
                )

            return {
                "status": "completed",
                "tablespace_count": len(tablespaces),
                "tablespaces": tablespaces,
            }

        except Exception as e:
            logger.error("Tablespace check failed: %s", e)
            return {
                "status": "failed",
                "error": str(e),
            }

    def check_user_sessions(self) -> dict[str, Any]:
        """Check active user sessions.

        Returns:
            Session information.
        """
        try:
            sql = """
            SELECT
                username,
                status,
                machine,
                program,
                logon_time
            FROM v$session
            WHERE username IS NOT NULL
            ORDER BY logon_time DESC
            """

            results = self.connection.fetch_all(sql)

            sessions = []
            for row in results:
                sessions.append(
                    {
                        "username": row[0],
                        "status": row[1],
                        "machine": row[2],
                        "program": row[3],
                        "logon_time": str(row[4]) if row[4] else None,
                    }
                )

            return {
                "status": "completed",
                "active_sessions": len(sessions),
                "sessions": sessions,
            }

        except Exception as e:
            logger.error("Session check failed: %s", e)
            return {
                "status": "failed",
                "error": str(e),
            }
