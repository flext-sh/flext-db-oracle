"""Comprehensive unit tests for Oracle SQL query optimizer.

Tests the SQL optimization functionality with proper pytest structure,
mocking, and comprehensive coverage of all optimization methods.
"""

from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest
from flext_core import FlextResult as ServiceResult
from src.flext_db_oracle.sql.optimizer import (
    QueryAnalysis,
    QueryOptimizer,
    QueryPlanStep,
)


@pytest.fixture
def mock_connection_service() -> AsyncMock:
    """Create mock connection service for tests."""
    return AsyncMock()


@pytest.fixture
def query_optimizer(mock_connection_service: AsyncMock) -> QueryOptimizer:
    """Create QueryOptimizer instance with mock connection."""
    return QueryOptimizer(mock_connection_service)


@pytest.fixture
def sample_execution_plan_data() -> list[list[Any]]:
    """Sample execution plan data for testing."""
    return [
        [0, "SELECT STATEMENT", None, None, 100, 10, 1024, 50, 30, 0],
        [1, "TABLE ACCESS", "FULL", "EMPLOYEES", 80, 1000, 8000, 40, 20, 1],
        [2, "SORT", "ORDER BY", None, 20, 1000, 8000, 10, 5, 1],
    ]


@pytest.fixture
def sample_sql_query() -> str:
    """Sample SQL query for testing."""
    return "SELECT * FROM employees WHERE department_id = 10 ORDER BY last_name"


class TestQueryOptimizer:
    """Test cases for QueryOptimizer class."""

    async def test_optimize_query_success(
        self, query_optimizer: Any, mock_connection_service: Any, sample_sql_query: Any
    ) -> None:
        """Test successful query optimization."""
        # Mock successful plan analysis and index suggestions
        mock_connection_service.execute_query.side_effect = [
            ServiceResult.ok(None),  # EXPLAIN PLAN
            ServiceResult.ok(
                MagicMock(
                    rows=[
                        [0, "SELECT STATEMENT", None, None, 100, 10, 1024, 50, 30],
                        [
                            1,
                            "TABLE ACCESS",
                            "FULL",
                            "EMPLOYEES",
                            80,
                            1000,
                            8000,
                            40,
                            20,
                        ],
                    ]
                )
            ),  # Plan query
            ServiceResult.ok(None),  # Cleanup
        ]

        result = await query_optimizer.optimize_query(sample_sql_query)

        assert result.success
        analysis = result.data
        assert analysis["original_query"] == sample_sql_query
        assert analysis["optimization_score"] == "EXCELLENT"  # 2 plan steps = EXCELLENT
        assert analysis["analysis_method"] == "advanced"
        assert (
            "SELECT *" in analysis["recommendations"][0]
        )  # Should suggest not using SELECT *

    async def test_optimize_query_plan_failure_graceful_degradation(
        self, query_optimizer: Any, mock_connection_service: Any, sample_sql_query: Any
    ) -> None:
        """Test optimization with plan analysis failure but graceful degradation."""
        # Mock plan analysis failure
        mock_connection_service.execute_query.return_value = ServiceResult.fail(
            "Access denied to plan_table"
        )

        result = await query_optimizer.optimize_query(sample_sql_query)

        assert result.success  # Should still succeed with basic analysis
        analysis = result.data
        assert analysis["original_query"] == sample_sql_query
        assert analysis["execution_plan"] is None
        assert analysis["optimization_score"] == "UNKNOWN"
        assert analysis["analysis_method"] == "basic"
        assert len(analysis["recommendations"]) > 0  # Should have basic recommendations

    async def test_analyze_query_plan_success(
        self,
        query_optimizer: Any,
        mock_connection_service: Any,
        sample_execution_plan_data: Any,
        sample_sql_query: Any,
    ) -> None:
        """Test successful query plan analysis."""
        mock_connection_service.execute_query.side_effect = [
            ServiceResult.ok(None),  # EXPLAIN PLAN
            ServiceResult.ok(MagicMock(rows=sample_execution_plan_data)),  # Plan query
            ServiceResult.ok(None),  # Cleanup
        ]

        result = await query_optimizer.analyze_query_plan(sample_sql_query)

        assert result.success
        analysis = result.data
        assert isinstance(analysis, QueryAnalysis)
        assert analysis.sql_text == sample_sql_query
        assert len(analysis.execution_plan) == 3
        assert analysis.total_cost == 100  # Max cost from plan steps
        assert analysis.estimated_rows == 2010  # Sum of cardinalities: 10+1000+1000

        # Check first plan step
        first_step = analysis.execution_plan[0]
        assert isinstance(first_step, QueryPlanStep)
        assert first_step.operation == "SELECT STATEMENT"
        assert first_step.cost == 100
        assert first_step.cardinality == 10

    async def test_analyze_query_plan_explain_failure(
        self, query_optimizer: Any, mock_connection_service: Any, sample_sql_query: Any
    ) -> None:
        """Test query plan analysis with EXPLAIN PLAN failure."""
        mock_connection_service.execute_query.return_value = ServiceResult.fail(
            "Invalid SQL syntax"
        )

        result = await query_optimizer.analyze_query_plan(sample_sql_query)

        assert not result.success
        assert "Failed to generate execution plan" in result.error

    async def test_analyze_query_plan_retrieve_failure(
        self, query_optimizer: Any, mock_connection_service: Any, sample_sql_query: Any
    ) -> None:
        """Test query plan analysis with plan retrieval failure."""
        mock_connection_service.execute_query.side_effect = [
            ServiceResult.ok(None),  # EXPLAIN PLAN succeeds
            ServiceResult.fail("Access denied to plan_table"),  # Plan query fails
        ]

        result = await query_optimizer.analyze_query_plan(sample_sql_query)

        assert not result.success
        assert "Failed to retrieve execution plan" in result.error

    async def test_analyze_query_plan_empty_result(
        self, query_optimizer: Any, mock_connection_service: Any, sample_sql_query: Any
    ) -> None:
        """Test query plan analysis with empty plan result."""
        mock_connection_service.execute_query.side_effect = [
            ServiceResult.ok(None),  # EXPLAIN PLAN
            ServiceResult.ok(None),  # Plan query returns None
        ]

        result = await query_optimizer.analyze_query_plan(sample_sql_query)

        assert not result.success
        assert "Execution plan result is empty" in result.error

    async def test_analyze_query_plan_no_rows(
        self, query_optimizer: Any, mock_connection_service: Any, sample_sql_query: Any
    ) -> None:
        """Test query plan analysis with no plan rows."""
        mock_connection_service.execute_query.side_effect = [
            ServiceResult.ok(None),  # EXPLAIN PLAN
            ServiceResult.ok(MagicMock(rows=[])),  # Plan query returns empty rows
            ServiceResult.ok(None),  # Cleanup
        ]

        result = await query_optimizer.analyze_query_plan(sample_sql_query)

        assert result.success
        analysis = result.data
        assert len(analysis.execution_plan) == 0  # Empty execution plan
        assert analysis.performance_rating == "unknown"

    async def test_suggest_indexes_where_clause(
        self, query_optimizer: Any, mock_connection_service: Any
    ) -> None:
        """Test index suggestions for WHERE clause columns."""
        sql = "SELECT name, email FROM employees WHERE department_id = 10 AND status = 'ACTIVE'"

        result = await query_optimizer.suggest_indexes(sql)

        assert result.success
        suggestions = result.data
        assert len(suggestions) >= 1
        # Should suggest index on WHERE clause columns
        assert any("department_id" in suggestion for suggestion in suggestions)

    async def test_suggest_indexes_join_conditions(
        self, query_optimizer: Any, mock_connection_service: Any
    ) -> None:
        """Test index suggestions for JOIN conditions."""
        sql = """
        SELECT e.name, d.department_name
        FROM employees e
        JOIN departments d ON e.department_id = d.id
        """

        result = await query_optimizer.suggest_indexes(sql)

        assert result.success
        suggestions = result.data
        assert len(suggestions) >= 1
        # Should suggest foreign key indexes on JOIN columns
        assert any("JOIN columns" in suggestion for suggestion in suggestions)

    async def test_suggest_indexes_order_by(
        self, query_optimizer: Any, mock_connection_service: Any
    ) -> None:
        """Test index suggestions for ORDER BY columns."""
        sql = "SELECT name, email FROM employees ORDER BY last_name, first_name"

        result = await query_optimizer.suggest_indexes(sql)

        assert result.success
        suggestions = result.data
        assert len(suggestions) >= 1
        # Should suggest ORDER BY optimization index
        assert any("ORDER BY optimization" in suggestion for suggestion in suggestions)

    async def test_suggest_indexes_no_patterns(
        self, query_optimizer: Any, mock_connection_service: Any
    ) -> None:
        """Test index suggestions when no specific patterns are found."""
        sql = "SELECT COUNT(*) FROM employees"

        result = await query_optimizer.suggest_indexes(sql)

        assert result.success
        suggestions = result.data
        assert len(suggestions) >= 4  # Default suggestions
        assert any("WHERE clause columns" in suggestion for suggestion in suggestions)
        assert any("composite indexes" in suggestion for suggestion in suggestions)

    async def test_analyze_query_performance_success(
        self,
        query_optimizer: Any,
        mock_connection_service: Any,
        sample_execution_plan_data: Any,
        sample_sql_query: Any,
    ) -> None:
        """Test successful query performance analysis."""
        # Mock plan analysis success
        mock_connection_service.execute_query.side_effect = [
            ServiceResult.ok(None),  # EXPLAIN PLAN
            ServiceResult.ok(MagicMock(rows=sample_execution_plan_data)),  # Plan query
            ServiceResult.ok(None),  # Cleanup
        ]

        result = await query_optimizer.analyze_query_performance(sample_sql_query)

        assert result.success
        report = result.data
        assert report["sql_text"] == sample_sql_query
        assert report["performance_rating"] == "poor"  # Has TABLE ACCESS FULL
        assert report["total_cost"] == 100
        assert report["estimated_rows"] == 2010
        assert report["has_expensive_operations"] is True
        assert len(report["optimization_hints"]) > 0
        assert report["execution_plan_steps"] == 3
        assert report["execution_stats_included"] is False

    async def test_analyze_query_performance_with_execution_stats(
        self,
        query_optimizer: Any,
        mock_connection_service: Any,
        sample_execution_plan_data: Any,
        sample_sql_query: Any,
    ) -> None:
        """Test query performance analysis with execution statistics."""
        # Mock plan analysis success
        mock_connection_service.execute_query.side_effect = [
            ServiceResult.ok(None),  # EXPLAIN PLAN
            ServiceResult.ok(MagicMock(rows=sample_execution_plan_data)),  # Plan query
            ServiceResult.ok(None),  # Cleanup
        ]

        result = await query_optimizer.analyze_query_performance(
            sample_sql_query, execution_stats=True
        )

        assert result.success
        report = result.data
        assert report["execution_stats_included"] is True
        assert "execution_time_estimate" in report
        assert "buffer_gets_estimate" in report
        assert "disk_reads_estimate" in report

    async def test_analyze_query_performance_plan_failure(
        self, query_optimizer: Any, mock_connection_service: Any, sample_sql_query: Any
    ) -> None:
        """Test query performance analysis with plan analysis failure."""
        mock_connection_service.execute_query.return_value = ServiceResult.fail(
            "Plan analysis failed"
        )

        result = await query_optimizer.analyze_query_performance(sample_sql_query)

        assert not result.success
        assert "Plan analysis failed" in result.error

    async def test_analyze_sql_performance_statistics_success(
        self,
        query_optimizer: Any,
        mock_connection_service: Any,
        sample_execution_plan_data: Any,
        sample_sql_query: Any,
    ) -> None:
        """Test SQL performance statistics analysis."""
        # Mock explain plan success and v$sql statistics
        mock_connection_service.execute_query.side_effect = [
            ServiceResult.ok(None),  # EXPLAIN PLAN
            ServiceResult.ok(MagicMock(rows=sample_execution_plan_data)),  # Plan query
            ServiceResult.ok(None),  # Cleanup
            ServiceResult.ok(
                MagicMock(
                    rows=[["abc123", 5, 500000, 200000, 1000, 50, 100, 150, "ALL_ROWS"]]
                )
            ),  # v$sql statistics
        ]

        result = await query_optimizer.analyze_sql_performance_statistics(
            sample_sql_query
        )

        assert result.success
        stats = result.data
        assert stats["sql_id"] == "abc123"
        assert stats["executions"] == 5
        assert stats["elapsed_time_ms"] == 500.0  # 500000 microseconds / 1000
        assert stats["cpu_time_ms"] == 200.0
        assert stats["buffer_gets"] == 1000
        assert stats["avg_elapsed_time_ms"] == 100.0  # 500.0 / 5
        assert stats["performance_rating"] == "good"  # 100ms < 1000ms threshold

    async def test_analyze_sql_performance_statistics_no_stats(
        self,
        query_optimizer: Any,
        mock_connection_service: Any,
        sample_execution_plan_data: Any,
        sample_sql_query: Any,
    ) -> None:
        """Test SQL performance statistics with no v$sql data."""
        # Mock explain plan success but no v$sql statistics
        mock_connection_service.execute_query.side_effect = [
            ServiceResult.ok(None),  # EXPLAIN PLAN (first call)
            ServiceResult.ok(
                MagicMock(rows=sample_execution_plan_data)
            ),  # Plan query (first call)
            ServiceResult.ok(None),  # Cleanup (first call)
            ServiceResult.ok(MagicMock(rows=[])),  # Empty v$sql statistics
            ServiceResult.ok(None),  # EXPLAIN PLAN (fallback call)
            ServiceResult.ok(
                MagicMock(rows=sample_execution_plan_data)
            ),  # Plan query (fallback call)
            ServiceResult.ok(None),  # Cleanup (fallback call)
        ]

        # Should fallback to basic performance analysis
        result = await query_optimizer.analyze_sql_performance_statistics(
            sample_sql_query
        )

        assert result.success
        # Should return basic performance analysis instead
        assert "performance_rating" in result.data

    async def test_analyze_sql_performance_statistics_explain_failure(
        self, query_optimizer: Any, mock_connection_service: Any, sample_sql_query: Any
    ) -> None:
        """Test SQL performance statistics with explain plan failure."""
        mock_connection_service.execute_query.return_value = ServiceResult.fail(
            "Explain plan failed"
        )

        result = await query_optimizer.analyze_sql_performance_statistics(
            sample_sql_query
        )

        assert not result.success
        assert "Failed to generate execution plan" in result.error

    async def test_get_session_statistics_success(
        self, query_optimizer: Any, mock_connection_service: Any
    ) -> None:
        """Test successful session statistics retrieval."""
        stats_data = [
            ["session logical reads", 10000],
            ["session physical reads", 1000],
            ["CPU used by this session", 5000],
            ["DB time", 8000],
            ["execute count", 50],
            ["parse count (total)", 20],
            ["parse count (hard)", 5],
            ["user commits", 10],
            ["user rollbacks", 2],
        ]
        mock_connection_service.execute_query.return_value = ServiceResult.ok(
            MagicMock(rows=stats_data)
        )

        result = await query_optimizer.get_session_statistics()

        assert result.success
        stats = result.data
        assert stats["session logical reads"] == 10000
        assert stats["session physical reads"] == 1000
        assert stats["buffer_hit_ratio"] == 90.0  # (10000-1000)/10000 * 100
        assert stats["soft_parse_ratio"] == 75.0  # (20-5)/20 * 100

    async def test_get_session_statistics_empty_result(
        self, query_optimizer: Any, mock_connection_service: Any
    ) -> None:
        """Test session statistics with empty result."""
        mock_connection_service.execute_query.return_value = ServiceResult.ok(None)

        result = await query_optimizer.get_session_statistics()

        assert not result.success
        assert "Session statistics result is empty" in result.error

    async def test_get_session_statistics_query_failure(
        self, query_optimizer: Any, mock_connection_service: Any
    ) -> None:
        """Test session statistics with query failure."""
        mock_connection_service.execute_query.return_value = ServiceResult.fail(
            "Access denied to v$sesstat"
        )

        result = await query_optimizer.get_session_statistics()

        assert not result.success
        assert "Access denied to v$sesstat" in result.error

    async def test_analyze_wait_events_success(
        self, query_optimizer: Any, mock_connection_service: Any
    ) -> None:
        """Test successful wait events analysis."""
        wait_events_data = [
            ["db file sequential read", "USER I/O", 1000, 500, 5000],
            ["log file sync", "COMMIT", 800, 100, 3000],
            ["db file scattered read", "USER I/O", 600, 50, 2000],
        ]
        mock_connection_service.execute_query.return_value = ServiceResult.ok(
            MagicMock(rows=wait_events_data)
        )

        result = await query_optimizer.analyze_wait_events()

        assert result.success
        analysis = result.data
        assert len(analysis["wait_events"]) == 3
        assert analysis["total_wait_time_centiseconds"] == 10000  # 5000+3000+2000
        assert analysis["top_wait_event"]["event"] == "db file sequential read"

        # Check percentage calculations
        first_event = analysis["wait_events"][0]
        assert first_event["percentage_of_total"] == 50.0  # 5000/10000 * 100

    async def test_analyze_wait_events_empty_result(
        self, query_optimizer: Any, mock_connection_service: Any
    ) -> None:
        """Test wait events analysis with empty result."""
        mock_connection_service.execute_query.return_value = ServiceResult.ok(None)

        result = await query_optimizer.analyze_wait_events()

        assert not result.success
        assert "Wait events result is empty" in result.error

    async def test_get_sql_plan_statistics_success(
        self, query_optimizer: Any, mock_connection_service: Any
    ) -> None:
        """Test successful SQL plan statistics retrieval."""
        plan_stats_data = [
            ["TABLE ACCESS", "FULL", "EMPLOYEES", 1, 1000, 500, 100, 50, 10000],
            ["SORT", "ORDER BY", None, 1, 1000, 200, 50, 10, 5000],
        ]
        mock_connection_service.execute_query.return_value = ServiceResult.ok(
            MagicMock(rows=plan_stats_data)
        )

        result = await query_optimizer.get_sql_plan_statistics("abc123")

        assert result.success
        stats = result.data
        assert stats["sql_id"] == "abc123"
        assert len(stats["plan_steps"]) == 2
        assert stats["total_elapsed_time_microseconds"] == 15000  # 10000 + 5000
        assert stats["total_buffer_gets"] == 850  # (500+100) + (200+50)

        # Check most expensive step
        most_expensive = stats["most_expensive_step"]
        assert most_expensive["operation"] == "TABLE ACCESS"
        assert most_expensive["elapsed_time_microseconds"] == 10000

        # Check percentage calculations
        first_step = stats["plan_steps"][0]
        assert first_step["time_percentage"] == pytest.approx(
            66.67, rel=1e-2
        )  # 10000/15000 * 100

    async def test_get_sql_plan_statistics_empty_result(
        self, query_optimizer: Any, mock_connection_service: Any
    ) -> None:
        """Test SQL plan statistics with empty result."""
        mock_connection_service.execute_query.return_value = ServiceResult.ok(None)

        result = await query_optimizer.get_sql_plan_statistics("abc123")

        assert not result.success
        assert "SQL plan statistics result is empty" in result.error

    async def test_optimization_score_calculation(
        self, query_optimizer: Any, mock_connection_service: Any
    ) -> None:
        """Test optimization score calculation logic."""
        # Test different plan complexities
        assert (
            query_optimizer._calculate_optimization_score([1, 2]) == "EXCELLENT"
        )  # <= 3 steps
        assert (
            query_optimizer._calculate_optimization_score([1, 2, 3, 4, 5]) == "GOOD"
        )  # <= 6 steps
        assert (
            query_optimizer._calculate_optimization_score([1, 2, 3, 4, 5, 6, 7, 8])
            == "FAIR"
        )  # <= 10 steps
        assert (
            query_optimizer._calculate_optimization_score([1] * 15)
            == "NEEDS_OPTIMIZATION"
        )  # > 10 steps
        assert (
            query_optimizer._calculate_optimization_score(None) == "UNKNOWN"
        )  # No plan
        assert (
            query_optimizer._calculate_optimization_score("invalid") == "UNKNOWN"
        )  # Invalid type

    async def test_generate_recommendations_comprehensive(
        self, query_optimizer: Any, mock_connection_service: Any
    ) -> None:
        """Test comprehensive recommendation generation."""
        # SQL with multiple issues
        sql = "SELECT * FROM employees ORDER BY last_name"
        recommendations = query_optimizer._generate_recommendations(
            sql, [1] * 8
        )  # Complex plan

        # Should have multiple recommendations
        assert any("SELECT *" in rec for rec in recommendations)
        assert any("WHERE clause" in rec for rec in recommendations)
        assert any("complex execution plan" in rec for rec in recommendations)

    async def test_exception_handling(
        self, query_optimizer: Any, mock_connection_service: Any
    ) -> None:
        """Test exception handling in optimizer methods."""
        # Mock connection service to raise exception
        mock_connection_service.execute_query.side_effect = Exception(
            "Database connection lost"
        )

        result = await query_optimizer.optimize_query("SELECT 1 FROM dual")

        # optimize_query has graceful degradation, so it succeeds with basic analysis
        assert result.success
        analysis = result.data
        assert analysis["analysis_method"] == "basic"
        assert analysis["execution_plan"] is None  # Plan analysis failed
        assert len(analysis["recommendations"]) > 0  # Has basic recommendations

    async def test_assess_performance_ratings(
        self, query_optimizer: Any, mock_connection_service: Any, sample_sql_query: Any
    ) -> None:
        """Test performance rating assessment."""
        # Create execution plans with different characteristics

        # Plan with expensive operations (TABLE ACCESS FULL)
        expensive_plan = [
            QueryPlanStep(
                id=0, operation="SELECT STATEMENT", cost=100, cardinality=10, depth=0
            ),
            QueryPlanStep(
                id=1,
                operation="TABLE ACCESS FULL",
                options="",
                cost=80,
                cardinality=1000,
                depth=1,
            ),
        ]

        rating = query_optimizer._assess_performance(expensive_plan, 100)
        assert rating == "poor"  # Has expensive operations

        # Plan with high cost but no expensive operations
        high_cost_plan = [
            QueryPlanStep(
                id=0, operation="INDEX RANGE SCAN", cost=15000, cardinality=10, depth=0
            ),
        ]

        rating = query_optimizer._assess_performance(high_cost_plan, 15000)
        assert rating == "poor"  # Cost > 10000

        # Plan with medium cost
        medium_cost_plan = [
            QueryPlanStep(
                id=0, operation="INDEX RANGE SCAN", cost=5000, cardinality=10, depth=0
            ),
        ]

        rating = query_optimizer._assess_performance(medium_cost_plan, 5000)
        assert rating == "fair"  # 1000 < cost <= 10000

        # Plan with low cost
        good_plan = [
            QueryPlanStep(
                id=0, operation="INDEX UNIQUE SCAN", cost=500, cardinality=1, depth=0
            ),
        ]

        rating = query_optimizer._assess_performance(good_plan, 500)
        assert rating == "good"  # Cost <= 1000

        # Empty plan
        rating = query_optimizer._assess_performance([], None)
        assert rating == "unknown"


@pytest.mark.asyncio
class TestQueryOptimizerIntegration:
    """Integration-style tests for QueryOptimizer."""

    async def test_full_optimization_workflow(
        self, query_optimizer: Any, mock_connection_service: Any
    ) -> None:
        """Test complete optimization workflow."""
        complex_sql = """
        SELECT e.employee_id, e.first_name, e.last_name, d.department_name
        FROM employees e
        JOIN departments d ON e.department_id = d.department_id
        WHERE e.salary > 50000
        ORDER BY e.last_name, e.first_name
        """

        # Mock comprehensive optimization workflow
        mock_connection_service.execute_query.side_effect = [
            ServiceResult.ok(None),  # EXPLAIN PLAN
            ServiceResult.ok(
                MagicMock(
                    rows=[
                        [0, "SELECT STATEMENT", None, None, 200, 50, 4000, 100, 80, 0],
                        [1, "SORT", "ORDER BY", None, 180, 50, 4000, 90, 70, 1],
                        [2, "HASH JOIN", "", None, 160, 50, 4000, 80, 60, 2],
                        [
                            3,
                            "TABLE ACCESS",
                            "FULL",
                            "EMPLOYEES",
                            80,
                            1000,
                            8000,
                            40,
                            20,
                            3,
                        ],
                        [
                            4,
                            "TABLE ACCESS",
                            "FULL",
                            "DEPARTMENTS",
                            80,
                            100,
                            800,
                            40,
                            20,
                            3,
                        ],
                    ]
                )
            ),  # Plan query
            ServiceResult.ok(None),  # Cleanup
        ]

        result = await query_optimizer.optimize_query(complex_sql)

        assert result.success
        analysis = result.data
        assert analysis["original_query"] == complex_sql
        assert analysis["optimization_score"] == "GOOD"  # 5 steps = GOOD
        assert len(analysis["index_suggestions"]) > 0
        assert len(analysis["recommendations"]) > 0

        # Should have JOIN-related index suggestions
        assert any(
            "JOIN columns" in suggestion for suggestion in analysis["index_suggestions"]
        )
        # Should have ORDER BY index suggestion
        assert any(
            "ORDER BY optimization" in suggestion
            for suggestion in analysis["index_suggestions"]
        )


class TestDomainModels:
    """Test domain model functionality."""

    def test_query_plan_step_validation(self) -> None:
        """Test QueryPlanStep domain validation."""
        step = QueryPlanStep(
            id=1,
            operation="TABLE ACCESS",
            options="FULL",
            object_name="EMPLOYEES",
            cost=100,
            cardinality=1000,
        )

        # Should not raise exception
        step.validate_domain_rules()

        # Test empty operation validation
        invalid_step = QueryPlanStep(
            id=1,
            operation="",
            cost=100,
        )
        with pytest.raises(ValueError, match="Operation cannot be empty"):
            invalid_step.validate_domain_rules()

    def test_query_analysis_validation(self) -> None:
        """Test QueryAnalysis domain validation."""
        analysis = QueryAnalysis(
            sql_text="SELECT * FROM test",
            total_cost=100,
            estimated_rows=1000,
            performance_rating="good",
        )

        # Should not raise exception
        analysis.validate_domain_rules()

        # Test empty SQL text validation
        invalid_analysis = QueryAnalysis(
            sql_text="",
            performance_rating="good",
        )
        with pytest.raises(ValueError, match="SQL text cannot be empty"):
            invalid_analysis.validate_domain_rules()

        # Test invalid performance rating
        invalid_analysis = QueryAnalysis(
            sql_text="SELECT 1",
            performance_rating="invalid_rating",
        )
        with pytest.raises(ValueError, match="Invalid performance rating"):
            invalid_analysis.validate_domain_rules()

    def test_query_analysis_expensive_operations(self) -> None:
        """Test QueryAnalysis expensive operations detection."""
        execution_plan = [
            QueryPlanStep(
                id=0, operation="SELECT STATEMENT", cost=100, cardinality=10, depth=0
            ),
            QueryPlanStep(
                id=1, operation="TABLE ACCESS FULL", cost=80, cardinality=1000, depth=1
            ),
            QueryPlanStep(
                id=2,
                operation="SORT",
                options="ORDER BY",
                cost=20,
                cardinality=1000,
                depth=1,
            ),
        ]

        analysis = QueryAnalysis(
            sql_text="SELECT * FROM test ORDER BY id",
            execution_plan=execution_plan,
            performance_rating="poor",
        )

        assert analysis.has_expensive_operations  # Has TABLE ACCESS FULL and SORT

        # Analysis without expensive operations
        cheap_plan = [
            QueryPlanStep(
                id=0, operation="INDEX UNIQUE SCAN", cost=5, cardinality=1, depth=0
            ),
        ]

        cheap_analysis = QueryAnalysis(
            sql_text="SELECT * FROM test WHERE id = 1",
            execution_plan=cheap_plan,
            performance_rating="excellent",
        )

        assert not cheap_analysis.has_expensive_operations
