"""SQL query optimization utilities for Oracle databases.

Built on flext-core foundation for robust SQL optimization analysis.
Uses ServiceResult pattern and async operations.
"""

from __future__ import annotations

import operator
import re
import uuid
from typing import TYPE_CHECKING, Any

from flext_core import DomainValueObject, Field, ServiceResult
from flext_observability.logging import get_logger

if TYPE_CHECKING:
    from flext_db_oracle.application.services import OracleConnectionService

logger = get_logger(__name__)

# Constants
EXECUTION_PLAN_MIN_COLUMNS = 9
HIGH_COST_THRESHOLD = 10000
MEDIUM_COST_THRESHOLD = 1000

# Performance thresholds (in milliseconds)
EXCELLENT_ELAPSED_TIME_MS = 100
GOOD_ELAPSED_TIME_MS = 1000
ACCEPTABLE_ELAPSED_TIME_MS = 5000


class QueryPlanStep(DomainValueObject):
    """Represents a step in an Oracle execution plan."""

    id: int = Field(..., description="Step ID", ge=0)
    operation: str = Field(..., description="Operation type")
    options: str | None = Field(None, description="Operation options")
    object_name: str | None = Field(None, description="Object name")
    cost: int | None = Field(None, description="Estimated cost", ge=0)
    cardinality: int | None = Field(None, description="Estimated rows", ge=0)
    bytes_estimate: int | None = Field(None, description="Estimated bytes", ge=0)
    cpu_cost: int | None = Field(None, description="CPU cost", ge=0)
    io_cost: int | None = Field(None, description="I/O cost", ge=0)
    depth: int = Field(0, description="Nesting depth", ge=0)


class QueryAnalysis(DomainValueObject):
    """Complete query analysis results."""

    sql_text: str = Field(..., description="Original SQL text")
    execution_plan: list[QueryPlanStep] = Field(
        default_factory=list,
        description="Execution plan steps",
    )
    total_cost: int | None = Field(None, description="Total estimated cost", ge=0)
    estimated_rows: int | None = Field(None, description="Total estimated rows", ge=0)
    optimization_hints: list[str] = Field(
        default_factory=list,
        description="Optimization suggestions",
    )
    performance_rating: str = Field("unknown", description="Performance assessment")

    @property
    def has_expensive_operations(self) -> bool:
        """Check if plan has expensive operations."""
        expensive_ops = ["TABLE ACCESS FULL", "SORT", "HASH JOIN", "NESTED LOOPS"]
        return any(step.operation in expensive_ops for step in self.execution_plan)


class QueryOptimizer:
    """Analyzes and optimizes Oracle SQL queries using flext-core patterns."""

    def __init__(self, connection_service: OracleConnectionService) -> None:
        """Initialize the query optimizer.

        Args:
            connection_service: Oracle connection service for database operations

        """
        self.connection_service = connection_service

    async def analyze_query_plan(self, sql: str) -> ServiceResult[QueryAnalysis]:
        """Analyze execution plan for a SQL query."""
        try:
            logger.info("Analyzing query execution plan")

            # Generate unique statement ID
            statement_id = f"FLEXT_{uuid.uuid4().hex[:8]}"

            # Generate execution plan
            plan_sql = f"EXPLAIN PLAN SET STATEMENT_ID = '{statement_id}' FOR {sql}"
            plan_result = await self.connection_service.execute_query(plan_sql)

            if not plan_result.is_success:
                return ServiceResult.fail(
                    f"Failed to generate execution plan: {plan_result.error}",
                )

            # Retrieve the execution plan
            plan_query = """
                SELECT
                    id,
                    operation,
                    options,
                    object_name,
                    cost,
                    cardinality,
                    bytes,
                    cpu_cost,
                    io_cost,
                    depth
                FROM plan_table
                WHERE statement_id = :statement_id
                ORDER BY id
            """

            plan_rows_result = await self.connection_service.execute_query(
                plan_query,
                {"statement_id": statement_id},
            )

            if not plan_rows_result.is_success:
                return ServiceResult.fail(
                    f"Failed to retrieve execution plan: {plan_rows_result.error}",
                )

            if not plan_rows_result.value:
                return ServiceResult.fail("Execution plan result is empty")

            # Build execution plan
            execution_plan = []
            for row in plan_rows_result.value.rows:
                step = QueryPlanStep(
                    id=row[0],
                    operation=row[1],
                    options=row[2],
                    object_name=row[3],
                    cost=row[4],
                    cardinality=row[5],
                    bytes_estimate=row[6],
                    cpu_cost=row[7],
                    io_cost=row[8],
                    depth=(
                        row[EXECUTION_PLAN_MIN_COLUMNS]
                        if len(row) > EXECUTION_PLAN_MIN_COLUMNS
                        else 0
                    ),
                )
                execution_plan.append(step)

            # Clean up plan table
            cleanup_sql = "DELETE FROM plan_table WHERE statement_id = :statement_id"
            await self.connection_service.execute_query(
                cleanup_sql,
                {"statement_id": statement_id},
            )

            # Analyze the plan
            analysis = await self._analyze_execution_plan(sql, execution_plan)

            logger.info("Query plan analysis completed")
            if analysis.is_success and analysis.value:
                return ServiceResult.ok(analysis.value)
            return ServiceResult.ok(
                QueryAnalysis(
                    sql_text=sql,
                    total_cost=None,
                    estimated_rows=None,
                    performance_rating="unknown",
                ),
            )

        except Exception as e:
            logger.exception("Query plan analysis failed")
            return ServiceResult.fail(f"Query plan analysis failed: {e}")

    async def _analyze_execution_plan(
        self,
        sql: str,
        execution_plan: list[QueryPlanStep],
    ) -> ServiceResult[QueryAnalysis]:
        """Analyze execution plan and provide optimization hints."""
        try:
            # Calculate total cost
            total_cost = None
            if execution_plan:
                costs = [step.cost for step in execution_plan if step.cost is not None]
                total_cost = max(costs) if costs else None

            # Calculate estimated rows
            estimated_rows = None
            if execution_plan:
                cardinalities = [
                    step.cardinality
                    for step in execution_plan
                    if step.cardinality is not None
                ]
                estimated_rows = sum(cardinalities) if cardinalities else None

            # Generate optimization hints
            hints = []

            # Check for full table scans
            full_scans = [
                step for step in execution_plan if step.operation == "TABLE ACCESS FULL"
            ]
            if full_scans:
                hints.append("Consider adding indexes for full table scans")

            # Check for expensive sorts
            sorts = [step for step in execution_plan if "SORT" in step.operation]
            if sorts:
                hints.append("Consider adding ORDER BY indexes to avoid sorts")

            # Check for hash joins on large tables
            hash_joins = [
                step for step in execution_plan if "HASH JOIN" in step.operation
            ]
            if hash_joins:
                hints.append("Review hash join conditions and table statistics")

            # Assess performance
            performance_rating = self._assess_performance(execution_plan, total_cost)

            analysis = QueryAnalysis(
                sql_text=sql,
                execution_plan=execution_plan,
                total_cost=total_cost,
                estimated_rows=estimated_rows,
                optimization_hints=hints,
                performance_rating=performance_rating,
            )

            return ServiceResult.ok(analysis)

        except Exception as e:
            logger.exception("Execution plan analysis failed")
            return ServiceResult.fail(f"Execution plan analysis failed: {e}")

    def _assess_performance(
        self,
        execution_plan: list[QueryPlanStep],
        total_cost: int | None,
    ) -> str:
        """Assess query performance based on execution plan."""
        if not execution_plan:
            return "unknown"

        # Check for concerning operations
        expensive_ops = ["TABLE ACCESS FULL", "CARTESIAN", "SORT"]
        has_expensive = any(
            any(op in step.operation for op in expensive_ops) for step in execution_plan
        )

        if has_expensive:
            return "poor"

        # Check cost
        if total_cost is not None:
            if total_cost > HIGH_COST_THRESHOLD:
                return "poor"
            if total_cost > MEDIUM_COST_THRESHOLD:
                return "fair"
            return "good"

        return "fair"

    async def suggest_indexes(self, sql: str) -> ServiceResult[list[str]]:
        """Suggest indexes based on query analysis."""
        try:
            suggestions = []

            # Extract WHERE clause columns for indexing suggestions
            where_match = re.search(
                r"\bWHERE\s+(.*?)(?:\s+(?:GROUP|ORDER|HAVING|LIMIT|$))",
                sql,
                re.IGNORECASE | re.DOTALL,
            )
            if where_match:
                where_clause = where_match.group(1)
                # Find equality conditions that could benefit from indexes
                column_conditions = re.findall(
                    r"(\w+\.?\w*)\s*=\s*",
                    where_clause,
                    re.IGNORECASE,
                )
                if column_conditions:
                    suggestions.append(
                        f"Consider index on columns: {', '.join(set(column_conditions))}",
                    )

            # Extract JOIN conditions
            join_matches = re.findall(
                r"\bJOIN\s+\w+\s+\w+\s+ON\s+(\w+\.?\w*)\s*=\s*(\w+\.?\w*)",
                sql,
                re.IGNORECASE,
            )
            if join_matches:
                join_columns = [f"{col1}, {col2}" for col1, col2 in join_matches]
                suggestions.append(
                    f"Consider foreign key indexes on JOIN columns: {'; '.join(join_columns)}",
                )

            # Extract ORDER BY columns
            order_match = re.search(
                r"\bORDER\s+BY\s+(.*?)(?:\s+(?:LIMIT|OFFSET|$))",
                sql,
                re.IGNORECASE | re.DOTALL,
            )
            if order_match:
                order_clause = order_match.group(1)
                order_columns = re.findall(r"(\w+\.?\w*)", order_clause)
                if order_columns:
                    suggestions.append(
                        f"Consider index for ORDER BY optimization: {', '.join(set(order_columns))}",
                    )

            # Default suggestions if no specific patterns found
            if not suggestions:
                suggestions = [
                    "Analyze WHERE clause columns for potential indexes",
                    "Consider composite indexes for multi-column conditions",
                    "Review JOIN conditions for foreign key indexes",
                    "Consider covering indexes for SELECT columns",
                ]

            logger.info("Generated %d index suggestions", len(suggestions))
            return ServiceResult.ok(suggestions)

        except Exception as e:
            logger.exception("Index suggestion failed")
            return ServiceResult.fail(f"Index suggestion failed: {e}")

    async def analyze_query_performance(
        self,
        sql: str,
        *,
        execution_stats: bool = False,
    ) -> ServiceResult[dict[str, Any]]:
        """Perform comprehensive query performance analysis."""
        try:
            # Get execution plan
            plan_result = await self.analyze_query_plan(sql)
            if not plan_result.is_success:
                return ServiceResult.fail(
                    plan_result.error or "Failed to generate execution plan",
                )

            analysis = plan_result.value
            if not analysis:
                return ServiceResult.fail("Query analysis result is empty")

            # Get index suggestions
            index_result = await self.suggest_indexes(sql)
            index_suggestions = index_result.value if index_result.is_success else []

            performance_report = {
                "sql_text": sql,
                "performance_rating": analysis.performance_rating,
                "total_cost": analysis.total_cost,
                "estimated_rows": analysis.estimated_rows,
                "has_expensive_operations": analysis.has_expensive_operations,
                "optimization_hints": analysis.optimization_hints,
                "index_suggestions": index_suggestions,
                "execution_plan_steps": len(analysis.execution_plan),
                "execution_stats_included": execution_stats,
            }

            # Add actual execution statistics if requested
            if execution_stats:
                performance_report.update(
                    {
                        "execution_time_estimate": "Not implemented - would require actual execution",
                        "buffer_gets_estimate": "Not implemented - would require v$sql_plan_statistics",
                        "disk_reads_estimate": "Not implemented - would require actual execution",
                    },
                )

            logger.info("Query performance analysis completed")
            return ServiceResult.ok(performance_report)

        except Exception as e:
            logger.exception("Query performance analysis failed")
            return ServiceResult.fail(f"Query performance analysis failed: {e}")

    async def analyze_sql_performance_statistics(
        self,
        sql_text: str,
    ) -> ServiceResult[dict[str, Any]]:
        """Analyze SQL performance using Oracle's v$sql statistics."""
        try:
            # First, execute the query to get it into v$sql
            explain_result = await self.analyze_query_plan(sql_text)
            if not explain_result.is_success:
                return ServiceResult.fail(
                    explain_result.error or "Failed to explain query plan",
                )

            # Get SQL statistics from v$sql
            stats_query = """
                SELECT sql_id, executions, elapsed_time, cpu_time,
                       buffer_gets, disk_reads, rows_processed,
                       optimizer_cost, optimizer_mode
                FROM v$sql
                WHERE sql_text LIKE :sql_pattern
                AND rownum = 1
            """

            # Use first 100 characters as pattern
            sql_pattern = sql_text[:100].replace("'", "''") + "%"

            stats_result = await self.connection_service.execute_query(
                stats_query,
                {"sql_pattern": sql_pattern},
            )

            if (
                not stats_result.is_success
                or not stats_result.value
                or not stats_result.value.rows
            ):
                # Fallback to basic analysis
                return await self.analyze_query_performance(sql_text)

            row = stats_result.value.rows[0]

            statistics = {
                "sql_id": row[0],
                "executions": row[1] or 0,
                "elapsed_time_ms": (row[2] or 0)
                / 1000,  # Convert microseconds to milliseconds
                "cpu_time_ms": (row[3] or 0) / 1000,
                "buffer_gets": row[4] or 0,
                "disk_reads": row[5] or 0,
                "rows_processed": row[6] or 0,
                "optimizer_cost": row[7] or 0,
                "optimizer_mode": row[8] or "UNKNOWN",
            }

            # Calculate derived metrics
            if statistics["executions"] > 0:
                statistics["avg_elapsed_time_ms"] = (
                    statistics["elapsed_time_ms"] / statistics["executions"]
                )
                statistics["avg_cpu_time_ms"] = (
                    statistics["cpu_time_ms"] / statistics["executions"]
                )
                statistics["avg_buffer_gets"] = (
                    statistics["buffer_gets"] / statistics["executions"]
                )
                statistics["avg_disk_reads"] = (
                    statistics["disk_reads"] / statistics["executions"]
                )

            # Performance assessment
            if statistics["avg_elapsed_time_ms"] < EXCELLENT_ELAPSED_TIME_MS:
                statistics["performance_rating"] = "excellent"
            elif statistics["avg_elapsed_time_ms"] < GOOD_ELAPSED_TIME_MS:
                statistics["performance_rating"] = "good"
            elif statistics["avg_elapsed_time_ms"] < ACCEPTABLE_ELAPSED_TIME_MS:
                statistics["performance_rating"] = "acceptable"
            else:
                statistics["performance_rating"] = "poor"

            logger.info("Retrieved SQL performance statistics for query")
            return ServiceResult.ok(statistics)

        except Exception as e:
            logger.exception("Failed to analyze SQL performance statistics")
            return ServiceResult.fail(
                f"Failed to analyze SQL performance statistics: {e}",
            )

    async def get_session_statistics(self) -> ServiceResult[dict[str, Any]]:
        """Get current session performance statistics."""
        try:
            # Get session statistics from v$sesstat
            session_query = """
                SELECT s.name, ss.value
                FROM v$sesstat ss, v$statname s
                WHERE ss.statistic# = s.statistic#
                AND ss.sid = (SELECT sid FROM v$mystat WHERE rownum = 1)
                AND s.name IN (
                    'session logical reads',
                    'session physical reads',
                    'CPU used by this session',
                    'DB time',
                    'execute count',
                    'parse count (total)',
                    'parse count (hard)',
                    'user commits',
                    'user rollbacks'
                )
                ORDER BY s.name
            """

            result = await self.connection_service.execute_query(session_query)

            if not result.is_success:
                return ServiceResult.fail(
                    result.error or "Failed to get session statistics",
                )

            if not result.value:
                return ServiceResult.fail("Session statistics result is empty")

            statistics = {row[0]: row[1] for row in result.value.rows}

            # Calculate ratios
            if statistics.get("session logical reads", 0) > 0:
                physical_reads = statistics.get("session physical reads", 0)
                logical_reads = statistics["session logical reads"]
                statistics["buffer_hit_ratio"] = (
                    (logical_reads - physical_reads) / logical_reads
                ) * 100

            if statistics.get("parse count (total)", 0) > 0:
                hard_parses = statistics.get("parse count (hard)", 0)
                total_parses = statistics["parse count (total)"]
                statistics["soft_parse_ratio"] = (
                    (total_parses - hard_parses) / total_parses
                ) * 100

            logger.info("Retrieved session performance statistics")
            return ServiceResult.ok(statistics)

        except Exception as e:
            logger.exception("Failed to get session statistics")
            return ServiceResult.fail(f"Failed to get session statistics: {e}")

    async def analyze_wait_events(self) -> ServiceResult[dict[str, Any]]:
        """Analyze current session wait events."""
        try:
            # Get wait events from v$session_wait
            wait_query = """
                SELECT event, wait_class, total_waits, total_timeouts, time_waited
                FROM v$system_event
                WHERE wait_class != 'Idle'
                AND total_waits > 0
                ORDER BY time_waited DESC
                FETCH FIRST 20 ROWS ONLY
            """

            result = await self.connection_service.execute_query(wait_query)

            if not result.is_success:
                return ServiceResult.fail(
                    result.error or "Failed to analyze wait events",
                )

            if not result.value:
                return ServiceResult.fail("Wait events result is empty")

            wait_events = []
            total_wait_time = 0

            for row in result.value.rows:
                event_data = {
                    "event": row[0],
                    "wait_class": row[1],
                    "total_waits": row[2],
                    "total_timeouts": row[3],
                    "time_waited_centiseconds": row[4],
                    "avg_wait_time": (row[4] / row[2]) if row[2] > 0 else 0,
                }
                wait_events.append(event_data)
                total_wait_time += row[4]

            # Calculate percentages
            for event in wait_events:
                if total_wait_time > 0:
                    event["percentage_of_total"] = (
                        event["time_waited_centiseconds"] / total_wait_time
                    ) * 100
                else:
                    event["percentage_of_total"] = 0

            analysis = {
                "wait_events": wait_events,
                "total_wait_time_centiseconds": total_wait_time,
                "top_wait_event": wait_events[0] if wait_events else None,
            }

            logger.info("Analyzed wait events: %d events found", len(wait_events))
            return ServiceResult.ok(analysis)

        except Exception as e:
            logger.exception("Failed to analyze wait events")
            return ServiceResult.fail(f"Failed to analyze wait events: {e}")

    async def get_sql_plan_statistics(
        self,
        sql_id: str,
    ) -> ServiceResult[dict[str, Any]]:
        """Get detailed execution plan statistics for a specific SQL."""
        try:
            # Get plan statistics from v$sql_plan_statistics_all
            plan_stats_query = """
                SELECT operation, options, object_name,
                       executions, output_rows, cr_buffer_gets,
                       cu_buffer_gets, disk_reads, elapsed_time
                FROM v$sql_plan_statistics_all
                WHERE sql_id = :sql_id
                ORDER BY id
            """

            result = await self.connection_service.execute_query(
                plan_stats_query,
                {"sql_id": sql_id},
            )

            if not result.is_success:
                return ServiceResult.fail(
                    result.error or "Failed to get SQL plan statistics",
                )

            if not result.value:
                return ServiceResult.fail("SQL plan statistics result is empty")

            plan_steps = []
            total_time = 0
            total_buffer_gets = 0

            for row in result.value.rows:
                step = {
                    "operation": row[0],
                    "options": row[1],
                    "object_name": row[2],
                    "executions": row[3] or 0,
                    "output_rows": row[4] or 0,
                    "cr_buffer_gets": row[5] or 0,
                    "cu_buffer_gets": row[6] or 0,
                    "disk_reads": row[7] or 0,
                    "elapsed_time_microseconds": row[8] or 0,
                }

                total_time += step["elapsed_time_microseconds"]
                total_buffer_gets += step["cr_buffer_gets"] + step["cu_buffer_gets"]

                plan_steps.append(step)

            # Calculate percentages
            for step in plan_steps:
                if total_time > 0:
                    step["time_percentage"] = (
                        step["elapsed_time_microseconds"] / total_time
                    ) * 100
                if total_buffer_gets > 0:
                    step_buffer_gets = step["cr_buffer_gets"] + step["cu_buffer_gets"]
                    step["buffer_percentage"] = (
                        step_buffer_gets / total_buffer_gets
                    ) * 100

            statistics = {
                "sql_id": sql_id,
                "plan_steps": plan_steps,
                "total_elapsed_time_microseconds": total_time,
                "total_buffer_gets": total_buffer_gets,
                "most_expensive_step": (
                    max(
                        plan_steps,
                        key=operator.itemgetter("elapsed_time_microseconds"),
                    )
                    if plan_steps
                    else None
                ),
            }

            logger.info(
                "Retrieved plan statistics for SQL ID: %s (%d steps)",
                sql_id,
                len(plan_steps),
            )
            return ServiceResult.ok(statistics)

        except Exception as e:
            logger.exception("Failed to get SQL plan statistics")
            return ServiceResult.fail(f"Failed to get SQL plan statistics: {e}")
