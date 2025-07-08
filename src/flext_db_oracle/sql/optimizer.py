"""SQL query optimization utilities for Oracle databases."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from flext_db_oracle.connection.connection import OracleConnection

logger = logging.getLogger(__name__)


class QueryOptimizer:
    """Analyzes and optimizes Oracle SQL queries."""

    def __init__(self, connection: OracleConnection) -> None:
        """Initialize query optimizer.

        Args:
            connection: Database connection for plan analysis.

        """
        self.connection = connection

    def analyze_query_plan(self, sql: str) -> dict[str, Any]:
        """Analyze execution plan for a SQL query.

        Args:
            sql: SQL query to analyze.

        Returns:
            Query execution plan analysis.

        """
        try:
            # Generate execution plan
            plan_sql = f"EXPLAIN PLAN FOR {sql}"
            self.connection.execute(plan_sql)

            # Retrieve the plan
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
                io_cost
            FROM plan_table
            WHERE statement_id IS NULL
            ORDER BY id
            """

            plan_rows = self.connection.fetch_all(plan_query)

            # Clean up plan table
            self.connection.execute("DELETE FROM plan_table WHERE statement_id IS NULL")

            plan_steps = [{
                        "id": row[0],
                        "operation": row[1],
                        "options": row[2],
                        "object_name": row[3],
                        "cost": row[4],
                        "cardinality": row[5],
                        "bytes": row[6],
                        "cpu_cost": row[7],
                        "io_cost": row[8],
                    } for row in plan_rows]

            # Calculate total cost
            total_cost = sum(step["cost"] for step in plan_steps if step["cost"])

            return {
                "status": "success",
                "sql": sql,
                "total_cost": total_cost,
                "plan_steps": plan_steps,
                "step_count": len(plan_steps),
            }

        except Exception as e:
            logger.exception("Failed to analyze query plan: %s", e)
            return {
                "status": "failed",
                "error": str(e),
                "sql": sql,
            }

    def suggest_optimizations(self, sql: str) -> dict[str, Any]:
        """Suggest optimizations for a SQL query.

        Args:
            sql: SQL query to analyze.

        Returns:
            Optimization suggestions.

        """
        suggestions = []

        # Analyze the query
        sql_upper = sql.upper()

        # Check for missing WHERE clause in UPDATE/DELETE
        if (
            "UPDATE " in sql_upper or "DELETE " in sql_upper
        ) and "WHERE " not in sql_upper:
            suggestions.append(
                {
                    "type": "warning",
                    "severity": "high",
                    "message": "UPDATE/DELETE without WHERE clause affects all rows",
                    "recommendation": "Add WHERE clause to limit affected rows",
                }
            )

        # Check for SELECT * usage
        if "SELECT *" in sql_upper:
            suggestions.append(
                {
                    "type": "performance",
                    "severity": "medium",
                    "message": "SELECT * retrieves all columns",
                    "recommendation": "Specify only needed columns for better performance",
                }
            )

        # Check for potential cartesian products
        if (
            "FROM " in sql_upper
            and "," in sql_upper
            and "WHERE " not in sql_upper
            and "JOIN " not in sql_upper
        ):
            suggestions.append(
                {
                    "type": "performance",
                    "severity": "high",
                    "message": "Potential cartesian product detected",
                    "recommendation": "Add WHERE clause or use explicit JOINs",
                }
            )

        # Check for functions in WHERE clause
        if any(
            func in sql_upper for func in ["UPPER(", "LOWER(", "SUBSTR(", "TO_CHAR("]
        ):
            if "WHERE " in sql_upper:
                suggestions.append(
                    {
                        "type": "performance",
                        "severity": "medium",
                        "message": "Functions in WHERE clause may prevent index usage",
                        "recommendation": "Consider function-based indexes or query rewrite",
                    }
                )

        # Check for OR conditions
        if " OR " in sql_upper and "WHERE " in sql_upper:
            suggestions.append(
                {
                    "type": "performance",
                    "severity": "medium",
                    "message": "OR conditions may prevent efficient index usage",
                    "recommendation": "Consider rewriting with UNION or separate queries",
                }
            )

        return {
            "status": "completed",
            "sql": sql,
            "suggestion_count": len(suggestions),
            "suggestions": suggestions,
        }

    def get_table_statistics(self, schema_name: str, table_name: str) -> dict[str, Any]:
        """Get table statistics for optimization analysis.

        Args:
            schema_name: Schema name.
            table_name: Table name.

        Returns:
            Table statistics.

        """
        try:
            sql = """
            SELECT
                num_rows,
                blocks,
                empty_blocks,
                avg_space,
                chain_cnt,
                avg_row_len,
                sample_size,
                last_analyzed
            FROM all_tables
            WHERE owner = UPPER(:schema_name)
                AND table_name = UPPER(:table_name)
            """

            result = self.connection.fetch_one(
                sql, {"schema_name": schema_name, "table_name": table_name}
            )

            if result:
                return {
                    "status": "found",
                    "table_name": table_name,
                    "schema_name": schema_name,
                    "num_rows": result[0],
                    "blocks": result[1],
                    "empty_blocks": result[2],
                    "avg_space": result[3],
                    "chain_cnt": result[4],
                    "avg_row_len": result[5],
                    "sample_size": result[6],
                    "last_analyzed": str(result[7]) if result[7] else None,
                }

            return {
                "status": "not_found",
                "table_name": table_name,
                "schema_name": schema_name,
            }

        except Exception as e:
            logger.exception("Failed to get table statistics: %s", e)
            return {
                "status": "failed",
                "error": str(e),
            }

    def recommend_indexes(self, schema_name: str, table_name: str) -> dict[str, Any]:
        """Recommend indexes for a table based on usage patterns.

        Args:
            schema_name: Schema name.
            table_name: Table name.

        Returns:
            Index recommendations.

        """
        recommendations: list[dict[str, Any]] = []

        try:
            # Check for foreign key columns without indexes
            fk_sql = """
            SELECT cc.column_name
            FROM all_cons_columns cc
            JOIN all_constraints c ON cc.constraint_name = c.constraint_name
                AND cc.owner = c.owner
            WHERE c.owner = UPPER(:schema_name)
                AND c.table_name = UPPER(:table_name)
                AND c.constraint_type = 'R'
                AND NOT EXISTS (
                    SELECT 1
                    FROM all_ind_columns ic
                    WHERE ic.table_owner = cc.owner
                        AND ic.table_name = cc.table_name
                        AND ic.column_name = cc.column_name
                        AND ic.column_position = 1
                )
            """

            fk_results = self.connection.fetch_all(
                fk_sql, {"schema_name": schema_name, "table_name": table_name}
            )

            recommendations.extend({
                        "type": "foreign_key",
                        "column": row[0],
                        "priority": "high",
                        "reason": "Foreign key column without index",
                        "sql": f"CREATE INDEX idx_{table_name.lower()}_{row[0].lower()} ON {schema_name}.{table_name} ({row[0]})",
                    } for row in fk_results)

            return {
                "status": "completed",
                "table_name": table_name,
                "schema_name": schema_name,
                "recommendation_count": len(recommendations),
                "recommendations": recommendations,
            }

        except Exception as e:
            logger.exception("Failed to recommend indexes: %s", e)
            return {
                "status": "failed",
                "error": str(e),
            }
