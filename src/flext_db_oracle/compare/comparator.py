"""Oracle database comparison functionality.

Built on flext-core foundation for comprehensive database comparison.
Orchestrates schema and data comparison operations.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from pydantic import Field

from flext_core import DomainValueObject, ServiceResult
from flext_observability.logging import get_logger

if TYPE_CHECKING:
    from flext_db_oracle.application.services import OracleConnectionService
    from flext_db_oracle.compare.differ import (
        ComparisonResult,
        DataDiffer,
        SchemaDiffer,
    )

logger = get_logger(__name__)


class ComparisonConfig(DomainValueObject):
    """Configuration for database comparison operations."""

    include_schema: bool = Field(True, description="Include schema comparison")
    include_data: bool = Field(False, description="Include data comparison")
    schema_objects: list[str] = Field(
        default_factory=lambda: ["tables", "views", "sequences", "procedures"],
        description="Schema object types to compare",
    )
    table_filters: list[str] = Field(default_factory=list, description="Table name patterns to include")
    exclude_tables: list[str] = Field(default_factory=list, description="Table names to exclude")
    sample_size: int | None = Field(None, description="Sample size for data comparison", ge=1)


class DatabaseComparator:
    """Compares Oracle databases using flext-core patterns."""

    def __init__(
        self,
        source_service: OracleConnectionService,
        target_service: OracleConnectionService,
        schema_differ: SchemaDiffer,
        data_differ: DataDiffer | None = None,
    ) -> None:
        self.source_service = source_service
        self.target_service = target_service
        self.schema_differ = schema_differ
        self.data_differ = data_differ

    async def compare_databases(
        self,
        source_schema: str,
        target_schema: str,
        config: ComparisonConfig,
    ) -> ServiceResult[ComparisonResult]:
        """Compare two Oracle databases comprehensively."""
        try:
            logger.info(
                "Starting database comparison: %s vs %s",
                source_schema,
                target_schema,
            )

            comparison_result = None

            if config.include_schema:
                schema_result = await self._compare_schemas(
                    source_schema,
                    target_schema,
                    config,
                )
                if schema_result.is_failure:
                    return schema_result
                comparison_result = schema_result.value

            if config.include_data and self.data_differ:
                data_result = await self._compare_data(
                    source_schema,
                    target_schema,
                    config,
                    comparison_result,
                )
                if data_result.is_failure:
                    return data_result
                # Data comparison would update the comparison_result

            if comparison_result is None:
                return ServiceResult.failure("No comparison operations performed")

            logger.info(
                "Database comparison complete: %d total differences",
                comparison_result.total_differences,
            )
            return ServiceResult.success(comparison_result)

        except Exception as e:
            logger.exception("Database comparison failed: %s", e)
            return ServiceResult.failure(f"Database comparison failed: {e}")

    async def _compare_schemas(
        self,
        source_schema: str,
        target_schema: str,
        config: ComparisonConfig,
    ) -> ServiceResult[ComparisonResult]:
        """Compare schema structures."""
        try:
            logger.info("Comparing schemas: %s vs %s", source_schema, target_schema)

            # Get schema metadata from both databases
            source_metadata = await self._get_schema_metadata(
                self.source_service,
                source_schema,
                config,
            )
            target_metadata = await self._get_schema_metadata(
                self.target_service,
                target_schema,
                config,
            )

            if source_metadata.is_failure or target_metadata.is_failure:
                return ServiceResult.failure("Failed to retrieve schema metadata")

            # Perform schema comparison
            return await self.schema_differ.compare_schemas(
                source_metadata.value,
                target_metadata.value,
            )

        except Exception as e:
            logger.exception("Schema comparison failed: %s", e)
            return ServiceResult.failure(f"Schema comparison failed: {e}")

    async def _compare_data(
        self,
        source_schema: str,
        target_schema: str,
        config: ComparisonConfig,
        schema_comparison: ComparisonResult | None,
    ) -> ServiceResult[dict[str, Any]]:
        """Compare data between databases."""
        try:
            logger.info("Comparing data: %s vs %s", source_schema, target_schema)

            if not self.data_differ:
                return ServiceResult.failure("Data differ not configured")

            # Get list of tables to compare
            tables_to_compare = await self._get_comparable_tables(
                source_schema,
                config,
                schema_comparison,
            )

            if tables_to_compare.is_failure:
                return tables_to_compare

            data_differences = []

            for table_name in tables_to_compare.value:
                # Get primary key columns for the table
                pk_result = await self._get_primary_key_columns(source_schema, table_name)
                if pk_result.is_failure:
                    logger.warning("Skipping table %s: no primary key found", table_name)
                    continue

                # Compare table data
                table_diff_result = await self.data_differ.compare_table_data(
                    self.source_service,
                    self.target_service,
                    table_name,
                    pk_result.value,
                )

                if table_diff_result.is_success:
                    data_differences.extend(table_diff_result.value)
                else:
                    logger.error("Data comparison failed for table %s", table_name)

            result = {
                "tables_compared": len(tables_to_compare.value),
                "total_differences": len(data_differences),
                "differences": data_differences,
            }

            logger.info("Data comparison complete: %d differences found", len(data_differences))
            return ServiceResult.success(result)

        except Exception as e:
            logger.exception("Data comparison failed: %s", e)
            return ServiceResult.failure(f"Data comparison failed: {e}")

    async def _get_schema_metadata(
        self,
        connection_service: OracleConnectionService,
        schema_name: str,
        config: ComparisonConfig,
    ) -> ServiceResult[Any]:
        """Get comprehensive schema metadata."""
        try:
            # This would use the SchemaAnalyzer to get complete metadata
            # For now, return a placeholder
            metadata = {
                "name": schema_name,
                "tables": [],
                "views": [],
                "sequences": [],
                "procedures": [],
            }

            return ServiceResult.success(metadata)

        except Exception as e:
            logger.exception("Failed to get schema metadata for %s: %s", schema_name, e)
            return ServiceResult.failure(f"Failed to get schema metadata: {e}")

    async def _get_comparable_tables(
        self,
        schema_name: str,
        config: ComparisonConfig,
        schema_comparison: ComparisonResult | None,
    ) -> ServiceResult[list[str]]:
        """Get list of tables that can be compared."""
        try:
            # Get all tables in schema
            query = """
                SELECT table_name
                FROM all_tables
                WHERE owner = :schema_name
                ORDER BY table_name
            """

            result = await self.source_service.execute_query(
                query,
                {"schema_name": schema_name.upper()},
            )

            if result.is_failure:
                return result

            all_tables = [row[0] for row in result.value.rows]

            # Apply filters
            filtered_tables = []
            for table_name in all_tables:
                # Check exclude list
                if table_name in config.exclude_tables:
                    continue

                # Check include filters
                if config.table_filters:
                    include = False
                    for pattern in config.table_filters:
                        if pattern.upper() in table_name.upper():
                            include = True
                            break
                    if not include:
                        continue

                filtered_tables.append(table_name)

            return ServiceResult.success(filtered_tables)

        except Exception as e:
            logger.exception("Failed to get comparable tables: %s", e)
            return ServiceResult.failure(f"Failed to get comparable tables: {e}")

    async def _get_primary_key_columns(
        self,
        schema_name: str,
        table_name: str,
    ) -> ServiceResult[list[str]]:
        """Get primary key columns for a table."""
        try:
            query = """
                SELECT column_name
                FROM all_cons_columns
                WHERE owner = :schema_name
                AND table_name = :table_name
                AND constraint_name = (
                    SELECT constraint_name
                    FROM all_constraints
                    WHERE owner = :schema_name
                    AND table_name = :table_name
                    AND constraint_type = 'P'
                )
                ORDER BY position
            """

            result = await self.source_service.execute_query(
                query,
                {
                    "schema_name": schema_name.upper(),
                    "table_name": table_name.upper(),
                },
            )

            if result.is_failure:
                return result

            pk_columns = [row[0] for row in result.value.rows]

            if not pk_columns:
                return ServiceResult.failure(f"No primary key found for table {table_name}")

            return ServiceResult.success(pk_columns)

        except Exception as e:
            logger.exception("Failed to get primary key columns: %s", e)
            return ServiceResult.failure(f"Failed to get primary key columns: {e}")

    async def get_comparison_summary(
        self,
        comparison_result: ComparisonResult,
    ) -> ServiceResult[dict[str, Any]]:
        """Generate a summary of comparison results."""
        try:
            summary = {
                "source": comparison_result.source_name,
                "target": comparison_result.target_name,
                "comparison_time": comparison_result.comparison_time,
                "total_differences": comparison_result.total_differences,
                "schema_differences": len(comparison_result.schema_differences),
                "data_differences": len(comparison_result.data_differences),
                "has_differences": comparison_result.has_differences,
            }

            # Group schema differences by type
            schema_by_type = {}
            for diff in comparison_result.schema_differences:
                obj_type = diff.object_type
                if obj_type not in schema_by_type:
                    schema_by_type[obj_type] = 0
                schema_by_type[obj_type] += 1

            summary["schema_differences_by_type"] = schema_by_type

            return ServiceResult.success(summary)

        except Exception as e:
            logger.exception("Failed to generate comparison summary: %s", e)
            return ServiceResult.failure(f"Failed to generate summary: {e}")
