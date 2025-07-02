"""Oracle database optimization utilities."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from flext_db_oracle.connection.connection import OracleConnection

logger = logging.getLogger(__name__)


class DatabaseOptimizer:
    """Provides Oracle database optimization utilities."""

    def __init__(self, connection: OracleConnection) -> None:
        """Initialize database optimizer.

        Args:
            connection: Database connection.

        """
        self.connection = connection

    def analyze_table_statistics(
        self, schema_name: str, table_name: str
    ) -> dict[str, Any]:
        """Analyze table statistics.

        Args:
            schema_name: Schema name.
            table_name: Table name.

        Returns:
            Table statistics analysis.

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
                    "status": "success",
                    "table_name": table_name,
                    "schema_name": schema_name,
                    "num_rows": result[0],
                    "blocks": result[1],
                    "empty_blocks": result[2],
                    "avg_space": result[3],
                    "chain_cnt": result[4],
                    "avg_row_len": result[5],
                    "last_analyzed": str(result[6]) if result[6] else None,
                }

            return {
                "status": "not_found",
                "table_name": table_name,
                "schema_name": schema_name,
            }

        except Exception as e:
            logger.exception("Failed to analyze table statistics: %s", e)
            return {
                "status": "failed",
                "error": str(e),
            }

    def get_optimization_recommendations(self, schema_name: str) -> dict[str, Any]:
        """Get optimization recommendations for a schema.

        Args:
            schema_name: Schema name to analyze.

        Returns:
            Optimization recommendations.

        """
        recommendations = []

        # Check for tables without statistics
        tables_without_stats = self._find_tables_without_statistics(schema_name)
        if tables_without_stats:
            recommendations.append(
                {
                    "type": "statistics",
                    "priority": "high",
                    "description": "Tables without recent statistics",
                    "tables": tables_without_stats,
                    "action": "Run DBMS_STATS.GATHER_TABLE_STATS",
                }
            )

        # Check for missing indexes
        missing_indexes = self._find_potential_missing_indexes(schema_name)
        if missing_indexes:
            recommendations.append(
                {
                    "type": "indexes",
                    "priority": "medium",
                    "description": "Potential missing indexes",
                    "suggestions": missing_indexes,
                    "action": "Consider creating indexes on frequently queried columns",
                }
            )

        return {
            "status": "completed",
            "schema_name": schema_name,
            "recommendation_count": len(recommendations),
            "recommendations": recommendations,
        }

    def _find_tables_without_statistics(self, schema_name: str) -> list[str]:
        """Find tables without recent statistics."""
        try:
            sql = """
            SELECT table_name
            FROM all_tables
            WHERE owner = UPPER(:schema_name)
                AND (last_analyzed IS NULL
                     OR last_analyzed < SYSDATE - 30)
            ORDER BY table_name
            """

            results = self.connection.fetch_all(sql, {"schema_name": schema_name})
            return [row[0] for row in results]

        except Exception as e:
            logger.exception("Failed to find tables without statistics: %s", e)
            return []

    def _find_potential_missing_indexes(self, schema_name: str) -> list[dict[str, Any]]:
        """Find potential missing indexes (simplified heuristic)."""
        try:
            # Look for foreign key columns without indexes
            sql = """
            SELECT
                cc.table_name,
                cc.column_name,
                c.constraint_name
            FROM all_cons_columns cc
            JOIN all_constraints c ON cc.constraint_name = c.constraint_name
                AND cc.owner = c.owner
            WHERE c.owner = UPPER(:schema_name)
                AND c.constraint_type = 'R'
                AND NOT EXISTS (
                    SELECT 1
                    FROM all_ind_columns ic
                    WHERE ic.table_owner = cc.owner
                        AND ic.table_name = cc.table_name
                        AND ic.column_name = cc.column_name
                        AND ic.column_position = 1
                )
            ORDER BY cc.table_name, cc.column_name
            """

            results = self.connection.fetch_all(sql, {"schema_name": schema_name})

            return [{
                        "table_name": row[0],
                        "column_name": row[1],
                        "constraint_name": row[2],
                        "reason": "Foreign key column without index",
                    } for row in results]

        except Exception as e:
            logger.exception("Failed to find potential missing indexes: %s", e)
            return []
