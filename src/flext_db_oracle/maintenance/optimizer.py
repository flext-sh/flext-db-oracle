"""Oracle database optimization utilities.

Built on flext-core foundation for comprehensive database optimization.
Uses ServiceResult pattern and async operations for robust performance analysis.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from pydantic import Field

from flext_core import DomainValueObject, ServiceResult

from flext_observability.logging import get_logger

if TYPE_CHECKING:
    from flext_db_oracle.application.services import OracleConnectionService

logger = get_logger(__name__)


class TableStatistics(DomainValueObject):
    """Oracle table statistics information."""

    table_name: str = Field(..., description="Table name")
    schema_name: str = Field(..., description="Schema name")
    num_rows: int | None = Field(None, description="Number of rows", ge=0)
    blocks: int | None = Field(None, description="Number of blocks", ge=0)
    empty_blocks: int | None = Field(None, description="Number of empty blocks", ge=0)
    avg_space: int | None = Field(None, description="Average space per block", ge=0)
    chain_cnt: int | None = Field(None, description="Number of chained rows", ge=0)
    avg_row_len: int | None = Field(None, description="Average row length", ge=0)
    sample_size: int | None = Field(None, description="Sample size used", ge=0)
    last_analyzed: str | None = Field(None, description="Last analyzed timestamp")
    compression: str | None = Field(None, description="Compression type")

    @property
    def is_analyzed(self) -> bool:
        """Check if table has been analyzed."""
        return self.last_analyzed is not None

    @property
    def estimated_size_mb(self) -> float:
        """Estimate table size in MB."""
        if self.blocks:
            # Oracle block size is typically 8KB
            return (self.blocks * 8) / 1024
        return 0.0

    @property
    def space_utilization(self) -> float:
        """Calculate space utilization percentage."""
        if self.blocks and self.empty_blocks is not None:
            used_blocks = self.blocks - self.empty_blocks
            return (used_blocks / self.blocks) * 100
        return 0.0


class IndexStatistics(DomainValueObject):
    """Oracle index statistics information."""

    index_name: str = Field(..., description="Index name")
    table_name: str = Field(..., description="Table name")
    schema_name: str = Field(..., description="Schema name")
    uniqueness: str = Field(..., description="Index uniqueness")
    blevel: int | None = Field(None, description="B-tree level", ge=0)
    leaf_blocks: int | None = Field(None, description="Number of leaf blocks", ge=0)
    distinct_keys: int | None = Field(None, description="Number of distinct keys", ge=0)
    avg_leaf_blocks_per_key: float | None = Field(None, description="Average leaf blocks per key", ge=0.0)
    clustering_factor: int | None = Field(None, description="Clustering factor", ge=0)
    sample_size: int | None = Field(None, description="Sample size used", ge=0)
    last_analyzed: str | None = Field(None, description="Last analyzed timestamp")

    @property
    def is_analyzed(self) -> bool:
        """Check if index has been analyzed."""
        return self.last_analyzed is not None

    @property
    def selectivity(self) -> float:
        """Calculate index selectivity."""
        if self.distinct_keys and self.sample_size:
            return self.distinct_keys / self.sample_size
        return 0.0


class OptimizationRecommendation(DomainValueObject):
    """Database optimization recommendation."""

    recommendation_type: str = Field(..., description="Type of recommendation")
    object_name: str = Field(..., description="Database object name")
    object_type: str = Field(..., description="Database object type")
    priority: str = Field(..., description="Priority level (HIGH, MEDIUM, LOW)")
    description: str = Field(..., description="Recommendation description")
    estimated_improvement: str | None = Field(None, description="Estimated performance improvement")
    implementation_sql: str | None = Field(None, description="SQL to implement recommendation")


class DatabaseOptimizer:
    """Provides Oracle database optimization utilities using flext-core patterns."""

    def __init__(self, connection_service: OracleConnectionService) -> None:
        self.connection_service = connection_service

    async def analyze_table_statistics(
        self,
        schema_name: str,
        table_name: str,
    ) -> ServiceResult[TableStatistics]:
        """Analyze table statistics for optimization."""
        try:
            query = """
                SELECT
                    table_name,
                    owner,
                    num_rows,
                    blocks,
                    empty_blocks,
                    avg_space,
                    chain_cnt,
                    avg_row_len,
                    sample_size,
                    TO_CHAR(last_analyzed, 'YYYY-MM-DD HH24:MI:SS') as last_analyzed,
                    compression
                FROM all_tables
                WHERE owner = :schema_name
                AND table_name = :table_name
            """

            result = await self.connection_service.execute_query(
                query,
                {
                    "schema_name": schema_name.upper(),
                    "table_name": table_name.upper(),
                },
            )

            if result.is_failure:
                return result

            if not result.value.rows:
                return ServiceResult.failure(f"Table {schema_name}.{table_name} not found")

            row = result.value.rows[0]
            stats = TableStatistics(
                table_name=row[0],
                schema_name=row[1],
                num_rows=row[2],
                blocks=row[3],
                empty_blocks=row[4],
                avg_space=row[5],
                chain_cnt=row[6],
                avg_row_len=row[7],
                sample_size=row[8],
                last_analyzed=row[9],
                compression=row[10],
            )

            logger.info("Retrieved table statistics for %s.%s", schema_name, table_name)
            return ServiceResult.success(stats)

        except Exception as e:
            logger.exception("Failed to analyze table statistics: %s", e)
            return ServiceResult.failure(f"Failed to analyze table statistics: {e}")

    async def analyze_index_statistics(
        self,
        schema_name: str,
        index_name: str | None = None,
    ) -> ServiceResult[list[IndexStatistics]]:
        """Analyze index statistics for optimization."""
        try:
            query = """
                SELECT
                    index_name,
                    table_name,
                    owner,
                    uniqueness,
                    blevel,
                    leaf_blocks,
                    distinct_keys,
                    avg_leaf_blocks_per_key,
                    clustering_factor,
                    sample_size,
                    TO_CHAR(last_analyzed, 'YYYY-MM-DD HH24:MI:SS') as last_analyzed
                FROM all_indexes
                WHERE owner = :schema_name
            """

            params = {"schema_name": schema_name.upper()}

            if index_name:
                query += " AND index_name = :index_name"
                params["index_name"] = index_name.upper()

            query += " ORDER BY index_name"

            result = await self.connection_service.execute_query(query, params)

            if result.is_failure:
                return result

            statistics = []
            for row in result.value.rows:
                stats = IndexStatistics(
                    index_name=row[0],
                    table_name=row[1],
                    schema_name=row[2],
                    uniqueness=row[3],
                    blevel=row[4],
                    leaf_blocks=row[5],
                    distinct_keys=row[6],
                    avg_leaf_blocks_per_key=row[7],
                    clustering_factor=row[8],
                    sample_size=row[9],
                    last_analyzed=row[10],
                )
                statistics.append(stats)

            logger.info("Retrieved statistics for %d indexes in schema %s", len(statistics), schema_name)
            return ServiceResult.success(statistics)

        except Exception as e:
            logger.exception("Failed to analyze index statistics: %s", e)
            return ServiceResult.failure(f"Failed to analyze index statistics: {e}")

    async def gather_table_statistics(
        self,
        schema_name: str,
        table_name: str,
        estimate_percent: int = 10,
    ) -> ServiceResult[str]:
        """Gather fresh statistics for a table."""
        try:
            # Use DBMS_STATS to gather table statistics
            gather_sql = f"""
                BEGIN
                    DBMS_STATS.GATHER_TABLE_STATS(
                        ownname => '{schema_name.upper()}',
                        tabname => '{table_name.upper()}',
                        estimate_percent => {estimate_percent},
                        cascade => TRUE,
                        method_opt => 'FOR ALL COLUMNS SIZE AUTO'
                    );
                END;
            """

            result = await self.connection_service.execute_query(gather_sql)

            if result.is_failure:
                return result

            message = f"Statistics gathered for {schema_name}.{table_name} with {estimate_percent}% estimate"
            logger.info(message)
            return ServiceResult.success(message)

        except Exception as e:
            logger.exception("Failed to gather table statistics: %s", e)
            return ServiceResult.failure(f"Failed to gather table statistics: {e}")

    async def analyze_schema_optimization(
        self,
        schema_name: str,
    ) -> ServiceResult[list[OptimizationRecommendation]]:
        """Analyze schema and provide optimization recommendations."""
        try:
            recommendations = []

            # Check for tables without statistics
            tables_result = await self._get_tables_without_stats(schema_name)
            if tables_result.is_success:
                recommendations.extend(OptimizationRecommendation(
                        recommendation_type="STATISTICS",
                        object_name=table_name,
                        object_type="TABLE",
                        priority="HIGH",
                        description=f"Table {table_name} lacks current statistics",
                        estimated_improvement="Query performance improvement up to 50%",
                        implementation_sql=f"EXEC DBMS_STATS.GATHER_TABLE_STATS('{schema_name.upper()}', '{table_name.upper()}')",
                    ) for table_name in tables_result.value)

            # Check for unused indexes
            unused_indexes_result = await self._get_unused_indexes(schema_name)
            if unused_indexes_result.is_success:
                recommendations.extend(OptimizationRecommendation(
                        recommendation_type="INDEX_CLEANUP",
                        object_name=index_name,
                        object_type="INDEX",
                        priority="MEDIUM",
                        description=f"Index {index_name} appears to be unused",
                        estimated_improvement="Storage savings and reduced maintenance overhead",
                        implementation_sql=f"DROP INDEX {schema_name.upper()}.{index_name}",
                    ) for index_name in unused_indexes_result.value)

            # Check for tables with high chain count
            chained_tables_result = await self._get_chained_tables(schema_name)
            if chained_tables_result.is_success:
                recommendations.extend(OptimizationRecommendation(
                        recommendation_type="REORGANIZATION",
                        object_name=table_name,
                        object_type="TABLE",
                        priority="MEDIUM",
                        description=f"Table {table_name} has high row chaining",
                        estimated_improvement="I/O reduction and query performance improvement",
                        implementation_sql=f"ALTER TABLE {schema_name.upper()}.{table_name} MOVE",
                    ) for table_name in chained_tables_result.value)

            logger.info("Generated %d optimization recommendations for schema %s", len(recommendations), schema_name)
            return ServiceResult.success(recommendations)

        except Exception as e:
            logger.exception("Failed to analyze schema optimization: %s", e)
            return ServiceResult.failure(f"Failed to analyze schema optimization: {e}")

    async def _get_tables_without_stats(self, schema_name: str) -> ServiceResult[list[str]]:
        """Get tables that lack current statistics."""
        try:
            query = """
                SELECT table_name
                FROM all_tables
                WHERE owner = :schema_name
                AND (last_analyzed IS NULL OR last_analyzed < SYSDATE - 7)
                ORDER BY table_name
            """

            result = await self.connection_service.execute_query(
                query,
                {"schema_name": schema_name.upper()},
            )

            if result.is_failure:
                return result

            tables = [row[0] for row in result.value.rows]
            return ServiceResult.success(tables)

        except Exception as e:
            logger.exception("Failed to get tables without stats: %s", e)
            return ServiceResult.failure(f"Failed to get tables without stats: {e}")

    async def _get_unused_indexes(self, schema_name: str) -> ServiceResult[list[str]]:
        """Get potentially unused indexes."""
        try:
            # This would require access to DBA_INDEX_USAGE or V$OBJECT_USAGE
            # For now, return empty list as placeholder
            return ServiceResult.success([])

        except Exception as e:
            logger.exception("Failed to get unused indexes: %s", e)
            return ServiceResult.failure(f"Failed to get unused indexes: {e}")

    async def _get_chained_tables(self, schema_name: str) -> ServiceResult[list[str]]:
        """Get tables with high row chaining."""
        try:
            query = """
                SELECT table_name
                FROM all_tables
                WHERE owner = :schema_name
                AND chain_cnt > num_rows * 0.1
                AND num_rows > 1000
                ORDER BY chain_cnt DESC
            """

            result = await self.connection_service.execute_query(
                query,
                {"schema_name": schema_name.upper()},
            )

            if result.is_failure:
                return result

            tables = [row[0] for row in result.value.rows]
            return ServiceResult.success(tables)

        except Exception as e:
            logger.exception("Failed to get chained tables: %s", e)
            return ServiceResult.failure(f"Failed to get chained tables: {e}")

    async def generate_optimization_report(
        self,
        schema_name: str,
    ) -> ServiceResult[dict[str, Any]]:
        """Generate comprehensive optimization report."""
        try:
            # Get recommendations
            recommendations_result = await self.analyze_schema_optimization(schema_name)
            if recommendations_result.is_failure:
                return recommendations_result

            recommendations = recommendations_result.value

            # Group recommendations by priority
            high_priority = [r for r in recommendations if r.priority == "HIGH"]
            medium_priority = [r for r in recommendations if r.priority == "MEDIUM"]
            low_priority = [r for r in recommendations if r.priority == "LOW"]

            report = {
                "schema_name": schema_name,
                "total_recommendations": len(recommendations),
                "high_priority_count": len(high_priority),
                "medium_priority_count": len(medium_priority),
                "low_priority_count": len(low_priority),
                "recommendations": {
                    "high": high_priority,
                    "medium": medium_priority,
                    "low": low_priority,
                },
                "summary": f"Found {len(recommendations)} optimization opportunities for schema {schema_name}",
            }

            logger.info("Generated optimization report for schema %s", schema_name)
            return ServiceResult.success(report)

        except Exception as e:
            logger.exception("Failed to generate optimization report: %s", e)
            return ServiceResult.failure(f"Failed to generate optimization report: {e}")
