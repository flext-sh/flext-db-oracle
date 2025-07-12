"""SQL query optimization utilities for Oracle databases.

Built on flext-core foundation for robust SQL optimization analysis.
Uses ServiceResult pattern and async operations.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from pydantic import Field

from flext_core import DomainValueObject, ServiceResult

from flext_observability.logging import get_logger

if TYPE_CHECKING:
    from flext_db_oracle.application.services import OracleConnectionService

logger = get_logger(__name__)


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
    execution_plan: list[QueryPlanStep] = Field(default_factory=list, description="Execution plan steps")
    total_cost: int | None = Field(None, description="Total estimated cost", ge=0)
    estimated_rows: int | None = Field(None, description="Total estimated rows", ge=0)
    optimization_hints: list[str] = Field(default_factory=list, description="Optimization suggestions")
    performance_rating: str = Field("unknown", description="Performance assessment")

    @property
    def has_expensive_operations(self) -> bool:
        """Check if plan has expensive operations."""
        expensive_ops = ["TABLE ACCESS FULL", "SORT", "HASH JOIN", "NESTED LOOPS"]
        return any(
            step.operation in expensive_ops
            for step in self.execution_plan
        )


class QueryOptimizer:
    """Analyzes and optimizes Oracle SQL queries using flext-core patterns."""

    def __init__(self, connection_service: OracleConnectionService) -> None:
        self.connection_service = connection_service

    async def analyze_query_plan(self, sql: str) -> ServiceResult[QueryAnalysis]:
        """Analyze execution plan for a SQL query."""
        try:
            logger.info("Analyzing query execution plan")

            # Generate unique statement ID
            import uuid
            statement_id = f"FLEXT_{uuid.uuid4().hex[:8]}"

            # Generate execution plan
            plan_sql = f"EXPLAIN PLAN SET STATEMENT_ID = '{statement_id}' FOR {sql}"
            plan_result = await self.connection_service.execute_query(plan_sql)

            if plan_result.is_failure:
                return plan_result

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

            if plan_rows_result.is_failure:
                return plan_rows_result

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
                    depth=row[9] if len(row) > 9 else 0,
                )
                execution_plan.append(step)

            # Clean up plan table
            cleanup_sql = f"DELETE FROM plan_table WHERE statement_id = '{statement_id}'"
            await self.connection_service.execute_query(cleanup_sql)

            # Analyze the plan
            analysis = await self._analyze_execution_plan(sql, execution_plan)

            logger.info("Query plan analysis completed")
            return ServiceResult.success(analysis.value if analysis.is_success else QueryAnalysis(sql_text=sql))

        except Exception as e:
            logger.exception("Query plan analysis failed: %s", e)
            return ServiceResult.failure(f"Query plan analysis failed: {e}")

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
                cardinalities = [step.cardinality for step in execution_plan if step.cardinality is not None]
                estimated_rows = sum(cardinalities) if cardinalities else None

            # Generate optimization hints
            hints = []

            # Check for full table scans
            full_scans = [step for step in execution_plan if step.operation == "TABLE ACCESS FULL"]
            if full_scans:
                hints.append("Consider adding indexes for full table scans")

            # Check for expensive sorts
            sorts = [step for step in execution_plan if "SORT" in step.operation]
            if sorts:
                hints.append("Consider adding ORDER BY indexes to avoid sorts")

            # Check for hash joins on large tables
            hash_joins = [step for step in execution_plan if "HASH JOIN" in step.operation]
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

            return ServiceResult.success(analysis)

        except Exception as e:
            logger.exception("Execution plan analysis failed: %s", e)
            return ServiceResult.failure(f"Execution plan analysis failed: {e}")

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
            any(op in step.operation for op in expensive_ops)
            for step in execution_plan
        )

        if has_expensive:
            return "poor"

        # Check cost
        if total_cost is not None:
            if total_cost > 10000:
                return "poor"
            if total_cost > 1000:
                return "fair"
            return "good"

        return "fair"

    async def suggest_indexes(self, sql: str) -> ServiceResult[list[str]]:
        """Suggest indexes based on query analysis."""
        try:
            # This would require parsing the SQL to identify:
            # - WHERE clause columns
            # - JOIN conditions
            # - ORDER BY columns
            # - GROUP BY columns

            # For now, return placeholder suggestions
            suggestions = [
                "Analyze WHERE clause columns for potential indexes",
                "Consider composite indexes for multi-column conditions",
                "Review JOIN conditions for foreign key indexes",
                "Consider covering indexes for SELECT columns",
            ]

            logger.info("Generated %d index suggestions", len(suggestions))
            return ServiceResult.success(suggestions)

        except Exception as e:
            logger.exception("Index suggestion failed: %s", e)
            return ServiceResult.failure(f"Index suggestion failed: {e}")

    async def analyze_query_performance(
        self,
        sql: str,
        execution_stats: bool = False,
    ) -> ServiceResult[dict[str, Any]]:
        """Perform comprehensive query performance analysis."""
        try:
            # Get execution plan
            plan_result = await self.analyze_query_plan(sql)
            if plan_result.is_failure:
                return plan_result

            analysis = plan_result.value

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
            }

            logger.info("Query performance analysis completed")
            return ServiceResult.success(performance_report)

        except Exception as e:
            logger.exception("Query performance analysis failed: %s", e)
            return ServiceResult.failure(f"Query performance analysis failed: {e}")
