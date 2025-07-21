"""Oracle database comparison functionality.

Built on flext-core foundation for comprehensive database comparison.
Orchestrates schema and data comparison operations.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from flext_core import DomainValueObject, Field, ServiceResult
from flext_observability.logging import get_logger

if TYPE_CHECKING:
    from flext_db_oracle.application.services import OracleConnectionService
    from flext_db_oracle.compare.differ import (
        ComparisonResult,
        DataDiffer,
        DifferenceType,
        SchemaDiffer,
    )
    from flext_db_oracle.schema.analyzer import SchemaAnalyzer
else:
    from flext_db_oracle.compare.differ import DataDiffer, DifferenceType
    from flext_db_oracle.schema.analyzer import SchemaAnalyzer

logger = get_logger(__name__)


class ComparisonConfig(DomainValueObject):
    """Configuration for database comparison operations."""

    include_schema: bool = Field(default=True, description="Include schema comparison")
    include_data: bool = Field(default=False, description="Include data comparison")
    schema_objects: list[str] = Field(
        default_factory=lambda: ["tables", "views", "sequences", "procedures"],
        description="Schema object types to compare",
    )
    table_filters: list[str] = Field(
        default_factory=list,
        description="Table name patterns to include",
    )
    exclude_tables: list[str] = Field(
        default_factory=list,
        description="Table names to exclude",
    )
    sample_size: int | None = Field(
        None,
        description="Sample size for data comparison",
        ge=1,
    )


class DatabaseComparator:
    """Compares Oracle databases using flext-core patterns."""

    def __init__(
        self,
        source_service: OracleConnectionService,
        target_service: OracleConnectionService,
        schema_differ: SchemaDiffer,
        data_differ: DataDiffer | None = None,
    ) -> None:
        """Initialize the database comparator.

        Args:
            source_service: Connection service for source database
            target_service: Connection service for target database
            schema_differ: Service for performing schema comparisons
            data_differ: Optional service for performing data comparisons

        """
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
                if not schema_result.is_success:
                    return schema_result
                comparison_result = schema_result.data

            if config.include_data and self.data_differ:
                data_result = await self._compare_data(
                    source_schema,
                    target_schema,
                    config,
                    comparison_result,
                )
                if not data_result.is_success:
                    return ServiceResult.fail(
                        data_result.error or "Data comparison failed",
                    )
                # Data comparison would update the comparison_result

            if comparison_result is None:
                return ServiceResult.fail("No comparison operations performed")

            logger.info(
                "Database comparison complete: %d total differences",
                comparison_result.total_differences,
            )
            return ServiceResult.ok(comparison_result)

        except Exception as e:
            logger.exception("Database comparison failed")
            return ServiceResult.fail(f"Database comparison failed: {e}")

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

            if not source_metadata.is_success or not target_metadata.is_success:
                return ServiceResult.fail("Failed to retrieve schema metadata")

            if not source_metadata.data or not target_metadata.data:
                return ServiceResult.fail("Schema metadata is empty")

            # Perform schema comparison
            return await self.schema_differ.compare_schemas(
                source_metadata.data,
                target_metadata.data,
            )

        except Exception as e:
            logger.exception("Schema comparison failed")
            return ServiceResult.fail(f"Schema comparison failed: {e}")

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
                return ServiceResult.fail("Data differ not configured")

            # Get list of tables to compare
            tables_to_compare = await self._get_comparable_tables(
                source_schema,
                config,
                schema_comparison,
            )

            if not tables_to_compare.is_success:
                return ServiceResult.fail(
                    tables_to_compare.error or "Failed to get tables to compare",
                )

            data_differences = []

            tables_list = tables_to_compare.data
            if not tables_list:
                return ServiceResult.ok({"data_differences": []})

            for table_name in tables_list:
                # Get primary key columns for the table
                pk_result = await self._get_primary_key_columns(
                    source_schema,
                    table_name,
                )
                if not pk_result.is_success:
                    logger.warning(
                        "Skipping table %s: no primary key found",
                        table_name,
                    )
                    continue

                # Compare table data
                table_diff_result = await self.data_differ.compare_table_data(
                    self.source_service,
                    self.target_service,
                    table_name,
                    pk_result.data or [],
                )

                if table_diff_result.is_success and table_diff_result.data:
                    data_differences.extend(table_diff_result.data)
                else:
                    logger.error("Data comparison failed for table %s", table_name)

            result = {
                "tables_compared": len(tables_to_compare.data or []),
                "total_differences": len(data_differences),
                "differences": data_differences,
            }

            logger.info(
                "Data comparison complete: %d differences found",
                len(data_differences),
            )
            return ServiceResult.ok(result)

        except Exception as e:
            logger.exception("Data comparison failed")
            return ServiceResult.fail(f"Data comparison failed: {e}")

    async def _get_schema_metadata(
        self,
        connection_service: OracleConnectionService,
        schema_name: str,
        config: ComparisonConfig,
    ) -> ServiceResult[Any]:
        """Get comprehensive schema metadata."""
        try:
            # Use the connection service to actually get schema metadata
            analyzer = SchemaAnalyzer(connection_service)
            schema_result = await analyzer.analyze_schema(schema_name)

            if not schema_result.is_success:
                return schema_result

            # Convert the analyzed data based on config requirements
            metadata = schema_result.data
            if not metadata:
                return ServiceResult.fail("Schema analysis returned no metadata")

            # Filter based on config if needed
            if config.schema_objects == ["tables"] and "tables" in metadata:
                tables = metadata.get("tables", [])
                metadata = {
                    "name": schema_name,
                    "tables": tables,
                    "total_objects": len(tables),
                }

            logger.info("Retrieved metadata for schema: %s", schema_name)
            return ServiceResult.ok(metadata)

        except Exception as e:
            logger.exception("Failed to get schema metadata for %s", schema_name)
            return ServiceResult.fail(f"Failed to get schema metadata: {e}")

    async def _get_comparable_tables(
        self,
        schema_name: str,
        config: ComparisonConfig,
        schema_comparison: ComparisonResult | None,
    ) -> ServiceResult[list[str]]:
        """Get list of tables that can be compared."""
        try:
            # Get all tables from database
            all_tables_result = await self._fetch_schema_tables(schema_name)
            if not all_tables_result.is_success:
                return all_tables_result

            all_tables = all_tables_result.data or []

            # Filter based on schema comparison results
            if schema_comparison is not None:
                all_tables = self._filter_common_tables(all_tables, schema_comparison)

            # Apply configuration filters
            filtered_tables = self._apply_table_filters(all_tables, config)

            logger.info(
                "Found %d comparable tables after filtering",
                len(filtered_tables),
            )
            return ServiceResult.ok(filtered_tables)

        except Exception as e:
            logger.exception("Failed to get comparable tables")
            return ServiceResult.fail(f"Failed to get comparable tables: {e}")

    async def _fetch_schema_tables(self, schema_name: str) -> ServiceResult[list[str]]:
        """Fetch all tables from schema."""
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

        if not result.is_success:
            return ServiceResult.fail(
                result.error or "Failed to fetch schema tables",
            )

        if not result.data or not result.data.rows:
            return ServiceResult.ok([])

        return ServiceResult.ok([row[0] for row in result.data.rows])

    def _filter_common_tables(
        self,
        all_tables: list[str],
        schema_comparison: ComparisonResult,
    ) -> list[str]:
        """Filter tables based on schema comparison results."""
        existing_tables = set(all_tables)

        # Remove tables that have schema differences (ADDED/REMOVED)
        for diff in schema_comparison.schema_differences:
            if diff.object_type.lower() == "table" and diff.difference_type in {
                DifferenceType.ADDED,
                DifferenceType.REMOVED,
            }:
                existing_tables.discard(diff.object_name)

        logger.info(
            "Filtered to %d common tables based on schema comparison",
            len(existing_tables),
        )
        return list(existing_tables)

    def _apply_table_filters(
        self,
        all_tables: list[str],
        config: ComparisonConfig,
    ) -> list[str]:
        """Apply configuration filters to table list."""
        filtered_tables = []

        for table_name in all_tables:
            # Check exclude list
            if table_name in config.exclude_tables:
                continue

            # Check include filters
            if config.table_filters:
                include = any(
                    pattern.upper() in table_name.upper()
                    for pattern in config.table_filters
                )
                if not include:
                    continue

            filtered_tables.append(table_name)

        return filtered_tables

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

            if not result.is_success:
                return ServiceResult.fail(
                    result.error or "Failed to get primary key columns",
                )

            if not result.data or not result.data.rows:
                return ServiceResult.fail(
                    f"No primary key found for table {table_name}",
                )

            pk_columns = [row[0] for row in result.data.rows]

            if not pk_columns:
                return ServiceResult.fail(
                    f"No primary key found for table {table_name}",
                )

            return ServiceResult.ok(pk_columns)

        except Exception as e:
            logger.exception("Failed to get primary key columns")
            return ServiceResult.fail(f"Failed to get primary key columns: {e}")

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

            return ServiceResult.ok(summary)

        except Exception as e:
            logger.exception("Failed to generate comparison summary")
            return ServiceResult.fail(f"Failed to generate summary: {e}")


class DataComparator:
    """Simplified data comparison interface for backward compatibility."""

    def __init__(
        self,
        source_service: OracleConnectionService,
        target_service: OracleConnectionService,
    ) -> None:
        """Initialize data comparator with connection services."""
        self.source_service = source_service
        self.target_service = target_service

    async def compare_table_data(
        self,
        table_name: str,
        primary_key_columns: list[str],
    ) -> ServiceResult[list[Any]]:
        """Compare data between tables in source and target databases."""
        try:
            differ = DataDiffer()
            return await differ.compare_table_data(
                self.source_service,
                self.target_service,
                table_name,
                primary_key_columns,
            )
        except Exception as e:
            logger.exception("Data comparison failed")
            return ServiceResult.fail(f"Data comparison failed: {e}")


class SchemaComparator:
    """Simplified schema comparison interface for backward compatibility."""

    def __init__(
        self,
        source_service: OracleConnectionService,
        target_service: OracleConnectionService,
    ) -> None:
        """Initialize schema comparator with connection services."""
        self.source_service = source_service
        self.target_service = target_service

    async def compare_schemas(
        self,
        source_schema: str,
        target_schema: str,
    ) -> ServiceResult[dict[str, Any]]:
        """Compare schemas between source and target databases."""
        try:
            source_analyzer = SchemaAnalyzer(self.source_service)
            target_analyzer = SchemaAnalyzer(self.target_service)

            # Get schema analysis for both
            source_result = await source_analyzer.analyze_schema(source_schema)
            target_result = await target_analyzer.analyze_schema(target_schema)

            if not source_result.is_success or not target_result.is_success:
                return ServiceResult.fail("Failed to analyze schemas")

            if not source_result.data or not target_result.data:
                return ServiceResult.fail("Schema analysis returned empty results")

            # Basic comparison - return structured differences
            comparison = {
                "source_schema": source_schema,
                "target_schema": target_schema,
                "source_analysis": source_result.data,
                "target_analysis": target_result.data,
                "differences": self._calculate_differences(
                    source_result.data,
                    target_result.data,
                ),
            }

            return ServiceResult.ok(comparison)

        except Exception as e:
            logger.exception("Schema comparison failed")
            return ServiceResult.fail(f"Schema comparison failed: {e}")

    def _calculate_differences(
        self,
        source: dict[str, Any],
        target: dict[str, Any],
    ) -> dict[str, Any]:
        """Calculate basic differences between schema analyses."""
        differences = {}

        # Compare table counts
        source_tables = len(source.get("tables", []))
        target_tables = len(target.get("tables", []))
        differences["table_count_diff"] = target_tables - source_tables

        # Compare view counts
        source_views = len(source.get("views", []))
        target_views = len(target.get("views", []))
        differences["view_count_diff"] = target_views - source_views

        # Compare sequence counts
        source_sequences = len(source.get("sequences", []))
        target_sequences = len(target.get("sequences", []))
        differences["sequence_count_diff"] = target_sequences - source_sequences

        # Compare procedure counts
        source_procedures = len(source.get("procedures", []))
        target_procedures = len(target.get("procedures", []))
        differences["procedure_count_diff"] = target_procedures - source_procedures

        return differences
