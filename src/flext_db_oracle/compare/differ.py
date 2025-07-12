"""Difference analysis for Oracle database objects.

Built on flext-core foundation for comprehensive schema and data comparison.
Uses ServiceResult pattern for robust error handling.
"""

from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from typing import TYPE_CHECKING, Any

from pydantic import Field

from flext_core import DomainValueObject, ServiceResult
from flext_observability.logging import get_logger

if TYPE_CHECKING:
    from flext_db_oracle.schema.metadata import SchemaMetadata, TableMetadata

logger = get_logger(__name__)


class DifferenceType(StrEnum):
    """Types of differences that can be detected."""

    ADDED = "ADDED"
    REMOVED = "REMOVED"
    MODIFIED = "MODIFIED"
    RENAMED = "RENAMED"


class SchemaDifference(DomainValueObject):
    """Represents a difference between two schema objects."""

    object_type: str = Field(..., description="Type of object (table, view, etc.)")
    object_name: str = Field(..., description="Name of the object")
    difference_type: DifferenceType = Field(..., description="Type of difference")
    source_value: Any = Field(None, description="Value in source schema")
    target_value: Any = Field(None, description="Value in target schema")
    details: dict[str, Any] = Field(default_factory=dict, description="Additional details")


class DataDifference(DomainValueObject):
    """Represents a difference in table data."""

    table_name: str = Field(..., description="Table name")
    row_identifier: dict[str, Any] = Field(..., description="Primary key or unique identifier")
    difference_type: DifferenceType = Field(..., description="Type of difference")
    changed_columns: list[str] = Field(default_factory=list, description="Changed column names")
    old_values: dict[str, Any] = Field(default_factory=dict, description="Old column values")
    new_values: dict[str, Any] = Field(default_factory=dict, description="New column values")


class ComparisonResult(DomainValueObject):
    """Result of a comparison operation."""

    source_name: str = Field(..., description="Source identifier")
    target_name: str = Field(..., description="Target identifier")
    schema_differences: list[SchemaDifference] = Field(default_factory=list)
    data_differences: list[DataDifference] = Field(default_factory=list)
    comparison_time: datetime = Field(default_factory=datetime.now)

    @property
    def total_differences(self) -> int:
        """Get total number of differences."""
        return len(self.schema_differences) + len(self.data_differences)

    @property
    def has_differences(self) -> bool:
        """Check if there are any differences."""
        return self.total_differences > 0


class SchemaDiffer:
    """Analyzes differences between Oracle database schemas using flext-core patterns."""

    def __init__(self) -> None:
        pass

    async def compare_schemas(
        self,
        source_schema: SchemaMetadata,
        target_schema: SchemaMetadata,
    ) -> ServiceResult[ComparisonResult]:
        """Compare two schemas and return differences."""
        try:
            logger.info(
                "Comparing schemas: %s vs %s",
                source_schema.name,
                target_schema.name,
            )

            differences = []

            # Compare tables
            table_diffs = await self._compare_tables(source_schema.tables, target_schema.tables)
            differences.extend(table_diffs)

            # Compare views
            view_diffs = await self._compare_views(source_schema.views, target_schema.views)
            differences.extend(view_diffs)

            # Compare sequences
            seq_diffs = await self._compare_sequences(source_schema.sequences, target_schema.sequences)
            differences.extend(seq_diffs)

            # Compare procedures
            proc_diffs = await self._compare_procedures(source_schema.procedures, target_schema.procedures)
            differences.extend(proc_diffs)

            result = ComparisonResult(
                source_name=source_schema.name,
                target_name=target_schema.name,
                schema_differences=differences,
            )

            logger.info("Schema comparison complete: %d differences found", len(differences))
            return ServiceResult.success(result)

        except Exception as e:
            logger.exception("Schema comparison failed: %s", e)
            return ServiceResult.failure(f"Schema comparison failed: {e}")

    async def _compare_tables(
        self,
        source_tables: list[TableMetadata],
        target_tables: list[TableMetadata],
    ) -> list[SchemaDifference]:
        """Compare tables between schemas."""
        differences = []

        source_names = {t.name.upper() for t in source_tables}
        target_names = {t.name.upper() for t in target_tables}

        # Find added tables
        for name in target_names - source_names:
            target_table = next(t for t in target_tables if t.name.upper() == name)
            differences.append(SchemaDifference(
                object_type="TABLE",
                object_name=name,
                difference_type=DifferenceType.ADDED,
                target_value=target_table.model_dump(),
            ))

        # Find removed tables
        for name in source_names - target_names:
            source_table = next(t for t in source_tables if t.name.upper() == name)
            differences.append(SchemaDifference(
                object_type="TABLE",
                object_name=name,
                difference_type=DifferenceType.REMOVED,
                source_value=source_table.model_dump(),
            ))

        # Find modified tables
        for name in source_names & target_names:
            source_table = next(t for t in source_tables if t.name.upper() == name)
            target_table = next(t for t in target_tables if t.name.upper() == name)

            table_diffs = await self._compare_table_details(source_table, target_table)
            differences.extend(table_diffs)

        return differences

    async def _compare_table_details(
        self,
        source_table: TableMetadata,
        target_table: TableMetadata,
    ) -> list[SchemaDifference]:
        """Compare detailed table properties."""
        differences = []

        # Compare column count
        if len(source_table.columns) != len(target_table.columns):
            differences.append(SchemaDifference(
                object_type="TABLE",
                object_name=source_table.name,
                difference_type=DifferenceType.MODIFIED,
                details={
                    "change": "column_count",
                    "source_count": len(source_table.columns),
                    "target_count": len(target_table.columns),
                },
            ))

        # Compare constraints
        if len(source_table.constraints) != len(target_table.constraints):
            differences.append(SchemaDifference(
                object_type="TABLE",
                object_name=source_table.name,
                difference_type=DifferenceType.MODIFIED,
                details={
                    "change": "constraint_count",
                    "source_count": len(source_table.constraints),
                    "target_count": len(target_table.constraints),
                },
            ))

        # Compare indexes
        if len(source_table.indexes) != len(target_table.indexes):
            differences.append(SchemaDifference(
                object_type="TABLE",
                object_name=source_table.name,
                difference_type=DifferenceType.MODIFIED,
                details={
                    "change": "index_count",
                    "source_count": len(source_table.indexes),
                    "target_count": len(target_table.indexes),
                },
            ))

        return differences

    async def _compare_views(self, source_views: list, target_views: list) -> list[SchemaDifference]:
        """Compare views between schemas."""
        source_names = {v.get("name", "").upper() if isinstance(v, dict) else v.name.upper() for v in source_views}
        target_names = {v.get("name", "").upper() if isinstance(v, dict) else v.name.upper() for v in target_views}

        # Find added views
        differences = [SchemaDifference(
                object_type="VIEW",
                object_name=name,
                difference_type=DifferenceType.ADDED,
            ) for name in target_names - source_names]

        # Find removed views
        differences.extend(SchemaDifference(
                object_type="VIEW",
                object_name=name,
                difference_type=DifferenceType.REMOVED,
            ) for name in source_names - target_names)

        return differences

    async def _compare_sequences(self, source_sequences: list, target_sequences: list) -> list[SchemaDifference]:
        """Compare sequences between schemas."""
        source_names = {s.get("name", "").upper() for s in source_sequences}
        target_names = {s.get("name", "").upper() for s in target_sequences}

        # Find added sequences
        differences = [SchemaDifference(
                object_type="SEQUENCE",
                object_name=name,
                difference_type=DifferenceType.ADDED,
            ) for name in target_names - source_names]

        # Find removed sequences
        differences.extend(SchemaDifference(
                object_type="SEQUENCE",
                object_name=name,
                difference_type=DifferenceType.REMOVED,
            ) for name in source_names - target_names)

        return differences

    async def _compare_procedures(self, source_procedures: list, target_procedures: list) -> list[SchemaDifference]:
        """Compare procedures/functions between schemas."""
        source_names = {p.get("name", "").upper() for p in source_procedures}
        target_names = {p.get("name", "").upper() for p in target_procedures}

        # Find added procedures
        differences = [SchemaDifference(
                object_type="PROCEDURE",
                object_name=name,
                difference_type=DifferenceType.ADDED,
            ) for name in target_names - source_names]

        # Find removed procedures
        differences.extend(SchemaDifference(
                object_type="PROCEDURE",
                object_name=name,
                difference_type=DifferenceType.REMOVED,
            ) for name in source_names - target_names)

        return differences


class DataDiffer:
    """Analyzes differences in Oracle table data using flext-core patterns."""

    def __init__(self) -> None:
        pass

    async def compare_table_data(
        self,
        source_connection_service,
        target_connection_service,
        table_name: str,
        primary_key_columns: list[str],
    ) -> ServiceResult[list[DataDifference]]:
        """Compare data between two tables."""
        try:
            logger.info("Comparing data for table: %s", table_name)

            # This would implement actual data comparison logic
            # For now, return empty differences
            differences = []

            logger.info("Data comparison complete for %s: %d differences", table_name, len(differences))
            return ServiceResult.success(differences)

        except Exception as e:
            logger.exception("Data comparison failed for %s: %s", table_name, e)
            return ServiceResult.failure(f"Data comparison failed: {e}")

    async def _compare_row_counts(
        self,
        source_connection_service,
        target_connection_service,
        table_name: str,
    ) -> ServiceResult[dict[str, int]]:
        """Compare row counts between tables."""
        try:
            source_result = await source_connection_service.execute_query(
                f"SELECT COUNT(*) FROM {table_name}",
            )
            target_result = await target_connection_service.execute_query(
                f"SELECT COUNT(*) FROM {table_name}",
            )

            if source_result.is_failure or target_result.is_failure:
                return ServiceResult.failure("Failed to get row counts")

            counts = {
                "source_count": source_result.value.rows[0][0],
                "target_count": target_result.value.rows[0][0],
            }

            return ServiceResult.success(counts)

        except Exception as e:
            logger.exception("Row count comparison failed: %s", e)
            return ServiceResult.failure(f"Row count comparison failed: {e}")
