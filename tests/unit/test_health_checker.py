"""Comprehensive unit tests for Oracle database health checker.

Tests the health monitoring functionality with proper pytest structure,
mocking, and comprehensive coverage of all health checking methods.
"""

from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest
from flext_core import FlextResult as ServiceResult
from src.flext_db_oracle.maintenance.health import (
    DatabaseHealth,
    HealthChecker,
    SessionInfo,
    TablespaceInfo,
)


@pytest.fixture
def mock_connection_service() -> AsyncMock:
    """Create mock connection service for tests."""
    return AsyncMock()


@pytest.fixture
def health_checker(mock_connection_service: AsyncMock) -> HealthChecker:
    """Create HealthChecker instance with mock connection."""
    return HealthChecker(mock_connection_service)


@pytest.fixture
def sample_tablespace_data() -> list[list[Any]]:
    """Sample tablespace data for testing."""
    return [
        ["SYSTEM", "ONLINE", "PERMANENT", "LOGGING", 1024.0, 512.0, 512.0],
        ["USERS", "ONLINE", "PERMANENT", "LOGGING", 2048.0, 1024.0, 1024.0],
        ["TEMP", "ONLINE", "TEMPORARY", "NOLOGGING", 512.0, 256.0, 256.0],
    ]


@pytest.fixture
def sample_session_data() -> list[list[Any]]:
    """Sample session data for testing."""
    return [
        [
            "SCOTT",
            "ACTIVE",
            "CLIENT_01",
            "sqlplus.exe",
            "2024-07-24 10:30:00",
            "abc123",
        ],
        ["HR", "INACTIVE", "CLIENT_02", "toad.exe", "2024-07-24 09:15:00", None],
        ["SYS", "ACTIVE", "SERVER", "DEDICATED", "2024-07-24 08:00:00", "def456"],
    ]


class TestHealthChecker:
    """Test cases for HealthChecker class."""

    async def test_check_connection_success(
        self, health_checker: HealthChecker, mock_connection_service: AsyncMock
    ) -> None:
        """Test successful connection health check."""
        mock_connection_service.execute_query.return_value = ServiceResult.ok(
            MagicMock(rows=[[1]])
        )

        result = await health_checker.check_connection()

        assert result.success
        data = result.data
        assert data["status"] == "active"
        assert data["test_query"] == "passed"
        assert data["result"] == 1

    async def test_check_connection_query_failure(
        self, health_checker: HealthChecker, mock_connection_service: AsyncMock
    ) -> None:
        """Test connection health check with query failure."""
        mock_connection_service.execute_query.return_value = ServiceResult.fail(
            "Connection timeout"
        )

        result = await health_checker.check_connection()

        assert not result.success
        assert "Connection timeout" in result.error

    async def test_check_connection_empty_result(
        self, health_checker: HealthChecker, mock_connection_service: AsyncMock
    ) -> None:
        """Test connection health check with empty result."""
        mock_connection_service.execute_query.return_value = ServiceResult.ok(
            MagicMock(rows=[])
        )

        result = await health_checker.check_connection()

        assert not result.success
        assert "Connection test query returned no data" in result.error

    async def test_check_tablespaces_success(
        self,
        health_checker: HealthChecker,
        mock_connection_service: AsyncMock,
        sample_tablespace_data: list[list[Any]],
    ) -> None:
        """Test successful tablespace health check."""
        mock_connection_service.execute_query.return_value = ServiceResult.ok(
            MagicMock(rows=sample_tablespace_data)
        )

        result = await health_checker.check_tablespaces()

        assert result.success
        tablespaces = result.data
        assert len(tablespaces) == 3

        # Check first tablespace
        system_ts = tablespaces[0]
        assert isinstance(system_ts, TablespaceInfo)
        assert system_ts.name == "SYSTEM"
        assert system_ts.status == "ONLINE"
        assert system_ts.contents == "PERMANENT"
        assert system_ts.size_mb == 1024.0
        assert system_ts.usage_percent == 50.0  # 512/1024 * 100

    async def test_check_tablespaces_empty_result(
        self, health_checker: HealthChecker, mock_connection_service: AsyncMock
    ) -> None:
        """Test tablespace check with empty result."""
        mock_connection_service.execute_query.return_value = ServiceResult.ok(
            MagicMock(rows=[])
        )

        result = await health_checker.check_tablespaces()

        assert result.success
        assert result.data == []

    async def test_check_tablespaces_query_failure(
        self, health_checker: Any, mock_connection_service: Any
    ) -> None:
        """Test tablespace check with query failure."""
        mock_connection_service.execute_query.return_value = ServiceResult.fail(
            "Access denied to dba_tablespaces"
        )

        result = await health_checker.check_tablespaces()

        assert not result.success
        assert "Access denied to dba_tablespaces" in result.error

    async def test_check_tablespaces_incomplete_rows(
        self, health_checker: Any, mock_connection_service: Any
    ) -> None:
        """Test tablespace check with incomplete row data."""
        # Rows with insufficient columns should be skipped
        incomplete_data = [
            ["SYSTEM", "ONLINE"],  # Only 2 columns instead of 7
            [
                "USERS",
                "ONLINE",
                "PERMANENT",
                "LOGGING",
                2048.0,
                1024.0,
                1024.0,
            ],  # Complete row
        ]
        mock_connection_service.execute_query.return_value = ServiceResult.ok(
            MagicMock(rows=incomplete_data)
        )

        result = await health_checker.check_tablespaces()

        assert result.success
        tablespaces = result.data
        assert len(tablespaces) == 1  # Only complete row processed
        assert tablespaces[0].name == "USERS"

    async def test_check_sessions_success(
        self,
        health_checker: Any,
        mock_connection_service: Any,
        sample_session_data: Any,
    ) -> None:
        """Test successful session health check."""
        mock_connection_service.execute_query.return_value = ServiceResult.ok(
            MagicMock(rows=sample_session_data)
        )

        result = await health_checker.check_sessions()

        assert result.success
        sessions = result.data
        assert len(sessions) == 3

        # Check first session
        scott_session = sessions[0]
        assert isinstance(scott_session, SessionInfo)
        assert scott_session.username == "SCOTT"
        assert scott_session.status == "ACTIVE"
        assert scott_session.machine == "CLIENT_01"
        assert scott_session.program == "sqlplus.exe"
        assert scott_session.sql_id == "abc123"

    async def test_check_sessions_with_limit(
        self,
        health_checker: Any,
        mock_connection_service: Any,
        sample_session_data: Any,
    ) -> None:
        """Test session check with custom limit."""
        mock_connection_service.execute_query.return_value = ServiceResult.ok(
            MagicMock(rows=sample_session_data[:2])  # Return only first 2 sessions
        )

        result = await health_checker.check_sessions(limit=2)

        assert result.success
        sessions = result.data
        assert len(sessions) == 2

    async def test_check_sessions_empty_result(
        self, health_checker: Any, mock_connection_service: Any
    ) -> None:
        """Test session check with empty result."""
        mock_connection_service.execute_query.return_value = ServiceResult.ok(
            MagicMock(rows=[])
        )

        result = await health_checker.check_sessions()

        assert result.success
        assert result.data == []

    async def test_check_sessions_query_failure(
        self, health_checker: Any, mock_connection_service: Any
    ) -> None:
        """Test session check with query failure."""
        mock_connection_service.execute_query.return_value = ServiceResult.fail(
            "Access denied to v$session"
        )

        result = await health_checker.check_sessions()

        assert not result.success
        assert "Access denied to v$session" in result.error

    async def test_check_overall_health_success(
        self, health_checker: Any, mock_connection_service: Any
    ) -> None:
        """Test successful overall health check."""
        # Mock all sub-checks to succeed
        mock_connection_service.execute_query.side_effect = [
            ServiceResult.ok(MagicMock(rows=[[1]])),  # connection check
            ServiceResult.ok(MagicMock(rows=[])),  # tablespace check
            ServiceResult.ok(MagicMock(rows=[])),  # session check
        ]

        result = await health_checker.check_overall_health()

        assert result.success
        health = result.data
        assert isinstance(health, DatabaseHealth)
        assert health.overall_status == "healthy"
        assert health.is_healthy
        assert health.connection_status == "healthy"
        assert health.tablespace_status == "healthy"
        assert health.session_status == "healthy"

    async def test_check_overall_health_partial_failure(
        self, health_checker: Any, mock_connection_service: Any
    ) -> None:
        """Test overall health check with partial failures."""
        # Mock connection success, tablespace failure, session success
        mock_connection_service.execute_query.side_effect = [
            ServiceResult.ok(MagicMock(rows=[[1]])),  # connection check - success
            ServiceResult.fail(
                "Tablespace access denied"
            ),  # tablespace check - failure
            ServiceResult.ok(MagicMock(rows=[])),  # session check - success
        ]

        result = await health_checker.check_overall_health()

        assert result.success
        health = result.data
        assert health.overall_status == "unhealthy"
        assert not health.is_healthy
        assert health.connection_status == "healthy"
        assert health.tablespace_status == "unhealthy"
        assert health.session_status == "healthy"

    async def test_generate_health_report_success(
        self, health_checker: Any, mock_connection_service: Any
    ) -> None:
        """Test successful health report generation."""
        # Mock successful overall health check
        mock_connection_service.execute_query.side_effect = [
            ServiceResult.ok(MagicMock(rows=[[1]])),  # connection check
            ServiceResult.ok(MagicMock(rows=[])),  # tablespace check
            ServiceResult.ok(MagicMock(rows=[])),  # session check
        ]

        result = await health_checker.generate_health_report()

        assert result.success
        report = result.data
        assert report["overall_status"] == "healthy"
        assert report["is_healthy"] is True
        assert "components" in report
        assert "details" in report
        assert "summary" in report
        assert report["summary"] == "Database is healthy"

    async def test_check_database_performance_metrics_success(
        self, health_checker: Any, mock_connection_service: Any
    ) -> None:
        """Test successful performance metrics check."""
        # Mock performance queries
        mock_connection_service.execute_query.side_effect = [
            ServiceResult.ok(MagicMock(rows=[[95.5]])),  # buffer cache hit ratio
            ServiceResult.ok(MagicMock(rows=[[92.3]])),  # library cache hit ratio
            ServiceResult.ok(MagicMock(rows=[[75.0]])),  # shared pool usage
            ServiceResult.ok(MagicMock(rows=[[256.5]])),  # PGA usage
            ServiceResult.ok(MagicMock(rows=[[15]])),  # active sessions
            ServiceResult.ok(
                MagicMock(
                    rows=[  # wait events
                        ["db file sequential read", 1000, 5000],
                        ["log file sync", 500, 2000],
                    ]
                )
            ),
        ]

        result = await health_checker.check_database_performance_metrics()

        assert result.success
        metrics = result.data
        assert metrics["buffer_cache_hit_ratio"] == 95.5
        assert metrics["library_cache_hit_ratio"] == 92.3
        assert metrics["shared_pool_used_percent"] == 75.0
        assert metrics["pga_used_mb"] == 256.5
        assert metrics["active_sessions"] == 15
        assert len(metrics["top_wait_events"]) == 2
        assert metrics["performance_assessment"] == "good"

    async def test_check_database_performance_metrics_poor_performance(
        self, health_checker: Any, mock_connection_service: Any
    ) -> None:
        """Test performance metrics check with poor performance indicators."""
        # Mock poor performance metrics
        mock_connection_service.execute_query.side_effect = [
            ServiceResult.ok(MagicMock(rows=[[70.0]])),  # low buffer cache hit ratio
            ServiceResult.ok(MagicMock(rows=[[65.0]])),  # low library cache hit ratio
            ServiceResult.ok(MagicMock(rows=[[98.0]])),  # high shared pool usage
            ServiceResult.ok(MagicMock(rows=[[512.0]])),  # high PGA usage
            ServiceResult.ok(MagicMock(rows=[[50]])),  # many active sessions
            ServiceResult.ok(MagicMock(rows=[])),  # no wait events
        ]

        result = await health_checker.check_database_performance_metrics()

        assert result.success
        metrics = result.data
        assert metrics["performance_assessment"] == "poor"

    async def test_check_database_locks_no_blocking(
        self, health_checker: Any, mock_connection_service: Any
    ) -> None:
        """Test database locks check with no blocking sessions."""
        mock_connection_service.execute_query.side_effect = [
            ServiceResult.ok(MagicMock(rows=[])),  # no blocking sessions
            ServiceResult.ok(MagicMock(rows=[[25]])),  # total locks count
        ]

        result = await health_checker.check_database_locks()

        assert result.success
        lock_analysis = result.data
        assert lock_analysis["total_locks"] == 25
        assert lock_analysis["blocking_sessions_count"] == 0
        assert lock_analysis["blocking_sessions"] == []
        assert lock_analysis["lock_status"] == "normal"

    async def test_check_database_locks_with_blocking(
        self, health_checker: Any, mock_connection_service: Any
    ) -> None:
        """Test database locks check with blocking sessions."""
        blocking_data = [
            ["SCOTT", 123, 456, "HR", 789, 101, "TX", 6, 4],
            ["SYS", 111, 222, "APPS", 333, 444, "TM", 3, 5],
        ]
        mock_connection_service.execute_query.side_effect = [
            ServiceResult.ok(MagicMock(rows=blocking_data)),  # blocking sessions
            ServiceResult.ok(MagicMock(rows=[[50]])),  # total locks count
        ]

        result = await health_checker.check_database_locks()

        assert result.success
        lock_analysis = result.data
        assert lock_analysis["total_locks"] == 50
        assert lock_analysis["blocking_sessions_count"] == 2
        assert len(lock_analysis["blocking_sessions"]) == 2
        assert lock_analysis["lock_status"] == "critical"

        # Check first blocking session details
        first_block = lock_analysis["blocking_sessions"][0]
        assert first_block["blocking_user"] == "SCOTT"
        assert first_block["blocked_user"] == "HR"
        assert first_block["lock_type"] == "TX"

    async def test_check_redo_log_activity_success(
        self, health_checker: Any, mock_connection_service: Any
    ) -> None:
        """Test successful redo log activity check."""
        log_switches_data = [
            ["2024-07-24 14", 3],
            ["2024-07-24 13", 2],
            ["2024-07-24 12", 4],
        ]
        redo_status_data = [
            [1, "CURRENT", "NO", 50.0],
            [2, "INACTIVE", "YES", 50.0],
            [3, "INACTIVE", "YES", 50.0],
        ]
        mock_connection_service.execute_query.side_effect = [
            ServiceResult.ok(MagicMock(rows=log_switches_data)),  # log switches
            ServiceResult.ok(MagicMock(rows=redo_status_data)),  # redo status
        ]

        result = await health_checker.check_redo_log_activity()

        assert result.success
        redo_analysis = result.data
        assert redo_analysis["total_switches_24h"] == 9  # 3+2+4
        assert redo_analysis["avg_switches_per_hour"] == 3.0  # 9/3
        assert len(redo_analysis["log_switches_24h"]) == 3
        assert len(redo_analysis["redo_logs_status"]) == 3
        assert redo_analysis["redo_activity_level"] == "normal"  # <= 4 threshold

    async def test_check_redo_log_activity_high_activity(
        self, health_checker: Any, mock_connection_service: Any
    ) -> None:
        """Test redo log activity check with high activity."""
        log_switches_data = [
            ["2024-07-24 14", 6],
            ["2024-07-24 13", 5],
        ]
        mock_connection_service.execute_query.side_effect = [
            ServiceResult.ok(MagicMock(rows=log_switches_data)),  # log switches
            ServiceResult.ok(MagicMock(rows=[])),  # redo status
        ]

        result = await health_checker.check_redo_log_activity()

        assert result.success
        redo_analysis = result.data
        assert redo_analysis["avg_switches_per_hour"] == 5.5  # 11/2
        assert redo_analysis["redo_activity_level"] == "high"  # > 4 threshold

    async def test_generate_comprehensive_health_report_success(
        self, health_checker: Any, mock_connection_service: Any
    ) -> None:
        """Test comprehensive health report generation."""
        # Mock all health check queries to succeed
        mock_connection_service.execute_query.side_effect = [
            # Basic health checks
            ServiceResult.ok(MagicMock(rows=[[1]])),  # connection
            ServiceResult.ok(MagicMock(rows=[])),  # tablespaces
            ServiceResult.ok(MagicMock(rows=[])),  # sessions
            # Performance metrics
            ServiceResult.ok(MagicMock(rows=[[95.0]])),  # buffer cache
            ServiceResult.ok(MagicMock(rows=[[92.0]])),  # library cache
            ServiceResult.ok(MagicMock(rows=[[75.0]])),  # shared pool
            ServiceResult.ok(MagicMock(rows=[[256.0]])),  # PGA
            ServiceResult.ok(MagicMock(rows=[[10]])),  # active sessions
            ServiceResult.ok(MagicMock(rows=[])),  # wait events
            # Lock analysis
            ServiceResult.ok(MagicMock(rows=[])),  # blocking sessions
            ServiceResult.ok(MagicMock(rows=[[20]])),  # total locks
            # Redo log analysis
            ServiceResult.ok(MagicMock(rows=[])),  # log switches
            ServiceResult.ok(MagicMock(rows=[])),  # redo status
        ]

        result = await health_checker.generate_comprehensive_health_report()

        assert result.success
        report = result.data
        assert "basic_health" in report
        assert "performance_metrics" in report
        assert "lock_analysis" in report
        assert "redo_log_analysis" in report
        assert "overall_assessment" in report
        assert report["overall_assessment"] == "excellent"  # All checks succeeded

    async def test_generate_comprehensive_health_report_partial_failures(
        self, health_checker: Any, mock_connection_service: Any
    ) -> None:
        """Test comprehensive health report with partial failures."""
        # Mock some checks to fail - need to account for ALL calls made
        mock_connection_service.execute_query.side_effect = [
            # Basic health checks
            ServiceResult.ok(MagicMock(rows=[[1]])),  # connection - success
            ServiceResult.fail("Tablespace access denied"),  # tablespaces - fail
            ServiceResult.ok(MagicMock(rows=[])),  # sessions - success
            # Performance metrics - fail (first call)
            ServiceResult.fail("Performance data unavailable"),
            # Lock analysis - fail (first call)
            ServiceResult.fail("Lock data unavailable"),
            # Redo log analysis - fail (first call)
            ServiceResult.fail("Redo log data unavailable"),
        ]

        result = await health_checker.generate_comprehensive_health_report()

        assert result.success
        report = result.data
        assert report["basic_health"] is not None  # Partial success
        assert report["performance_metrics"] is None  # Failed
        assert report["lock_analysis"] is None  # Failed
        assert report["redo_log_analysis"] is None  # Failed
        assert report["overall_assessment"] == "critical"  # Multiple failures

    async def test_exception_handling(
        self, health_checker: Any, mock_connection_service: Any
    ) -> None:
        """Test exception handling in health checker methods."""
        # Mock connection service to raise exception
        mock_connection_service.execute_query.side_effect = Exception(
            "Database connection lost"
        )

        result = await health_checker.check_connection()

        assert not result.success
        assert "Connection check failed" in result.error

    async def test_incomplete_performance_data(
        self, health_checker: Any, mock_connection_service: Any
    ) -> None:
        """Test performance metrics with incomplete data."""
        # Mock some queries to return empty results
        mock_connection_service.execute_query.side_effect = [
            ServiceResult.ok(MagicMock(rows=[])),  # buffer cache - empty
            ServiceResult.ok(MagicMock(rows=[[85.0]])),  # library cache - has data
            ServiceResult.ok(MagicMock(rows=[])),  # shared pool - empty
            ServiceResult.ok(MagicMock(rows=[])),  # PGA - empty
            ServiceResult.ok(MagicMock(rows=[[5]])),  # active sessions - has data
            ServiceResult.ok(MagicMock(rows=[])),  # wait events - empty
        ]

        result = await health_checker.check_database_performance_metrics()

        assert result.success
        metrics = result.data
        # Empty results should default to 0
        assert metrics["buffer_cache_hit_ratio"] == 0.0
        assert metrics["library_cache_hit_ratio"] == 85.0
        assert metrics["shared_pool_used_percent"] == 0.0
        assert metrics["pga_used_mb"] == 0
        assert metrics["active_sessions"] == 5
        assert metrics["top_wait_events"] == []


@pytest.mark.asyncio
class TestHealthCheckerIntegration:
    """Integration-style tests for HealthChecker."""

    async def test_full_health_workflow(
        self, health_checker: Any, mock_connection_service: Any
    ) -> None:
        """Test complete health checking workflow."""
        # Mock comprehensive health check workflow
        mock_connection_service.execute_query.side_effect = [
            # Basic health checks
            ServiceResult.ok(MagicMock(rows=[[1]])),  # connection
            ServiceResult.ok(
                MagicMock(
                    rows=[
                        [
                            "SYSTEM",
                            "ONLINE",
                            "PERMANENT",
                            "LOGGING",
                            1024.0,
                            512.0,
                            512.0,
                        ]
                    ]
                )
            ),  # tablespaces
            ServiceResult.ok(
                MagicMock(
                    rows=[
                        [
                            "SCOTT",
                            "ACTIVE",
                            "CLIENT_01",
                            "sqlplus.exe",
                            "2024-07-24 10:30:00",
                            "abc123",
                        ]
                    ]
                )
            ),  # sessions
        ]

        result = await health_checker.check_overall_health()

        assert result.success
        health = result.data
        assert health.overall_status == "healthy"
        assert len(health.details["tablespaces"]) == 1
        assert len(health.details["sessions"]) == 1

        # Verify tablespace details
        tablespace = health.details["tablespaces"][0]
        assert tablespace.name == "SYSTEM"
        assert tablespace.usage_percent == 50.0

        # Verify session details
        session = health.details["sessions"][0]
        assert session.username == "SCOTT"
        assert session.status == "ACTIVE"


class TestDomainModels:
    """Test domain model functionality."""

    def test_tablespace_info_usage_calculation(self) -> None:
        """Test tablespace usage percentage calculation."""
        tablespace = TablespaceInfo(
            name="TEST",
            status="ONLINE",
            contents="PERMANENT",
            logging="LOGGING",
            size_mb=1000.0,
            used_mb=750.0,
            free_mb=250.0,
        )

        assert tablespace.usage_percent == 75.0

    def test_tablespace_info_zero_size(self) -> None:
        """Test tablespace with zero size."""
        tablespace = TablespaceInfo(
            name="EMPTY",
            status="ONLINE",
            contents="PERMANENT",
            logging="LOGGING",
            size_mb=0.0,
            used_mb=0.0,
            free_mb=0.0,
        )

        assert tablespace.usage_percent == 0.0

    def test_database_health_is_healthy_property(self) -> None:
        """Test DatabaseHealth is_healthy property."""
        healthy_db = DatabaseHealth(
            connection_status="healthy",
            tablespace_status="healthy",
            session_status="healthy",
            overall_status="healthy",
        )

        assert healthy_db.is_healthy

        unhealthy_db = DatabaseHealth(
            connection_status="healthy",
            tablespace_status="unhealthy",
            session_status="healthy",
            overall_status="unhealthy",
        )

        assert not unhealthy_db.is_healthy

    def test_session_info_validation(self) -> None:
        """Test SessionInfo domain validation."""
        session = SessionInfo(
            username="SCOTT",
            status="ACTIVE",
            machine="CLIENT_01",
            program="sqlplus.exe",
        )

        # Should not raise exception
        session.validate_domain_rules()

        # Test empty status validation
        invalid_session = SessionInfo(
            username="SCOTT",
            status="",
            machine="CLIENT_01",
        )
        with pytest.raises(ValueError, match="Session status cannot be empty"):
            invalid_session.validate_domain_rules()
