"""Difference analysis for Oracle database objects.

Built on flext-core foundation for comprehensive schema and data comparison.
Uses FlextResult pattern for robust error handling.
"""

from __future__ import annotations

import re
from datetime import datetime
from enum import StrEnum
from typing import TYPE_CHECKING, Any, TypeGuard

from flext_core import (
    FlextResult,
    FlextValueObject,
    get_logger,
)
from pydantic import Field

from flext_db_oracle.constants import FlextDbOracleConstants

# Import TableMetadata for runtime type guard

if TYPE_CHECKING:
    from flext_db_oracle.application.services import FlextDbOracleConnectionService
    from flext_db_oracle.schema.metadata import SchemaMetadata, TableMetadata
logger = get_logger(__name__)


def flext_db_oracle_validate_sql_identifier(identifier: str) -> bool:
    """Validate SQL identifier for Oracle."""
    if not identifier or not identifier.strip():
        return False
    # Use FlextDbOracleConstants for validation
    return FlextDbOracleConstants.is_valid_oracle_identifier(identifier)


def flext_db_oracle_validate_table_name(table_name: str) -> FlextResult[Any]:
    """Validate table name for safe SQL construction."""
    if not flext_db_oracle_validate_sql_identifier(table_name):
        return FlextResult.fail(f"Invalid table name: {table_name}")
    return FlextResult.ok(table_name)


def flext_db_oracle_validate_column_names(
    column_names: list[str],
) -> FlextResult[Any]:
    """Validate column names for safe SQL construction."""
    for column_name in column_names:
        if not flext_db_oracle_validate_sql_identifier(column_name):
            return FlextResult.fail(f"Invalid column name: {column_name}")
    return FlextResult.ok(column_names)


class DifferenceType(StrEnum):
    """Types of differences that can be detected."""

    ADDED = "ADDED"
    REMOVED = "REMOVED"
    MODIFIED = "MODIFIED"
    RENAMED = "RENAMED"


class SchemaDifference(FlextValueObject):
    """Represents a difference between two schema objects."""

    object_type: str = Field(..., description="Type of object (table, view, etc.)")
    object_name: str = Field(..., description="Name of the object")
    difference_type: DifferenceType = Field(..., description="Type of difference")
    source_value: Any = Field(None, description="Value in source schema")
    target_value: Any = Field(None, description="Value in target schema")
    details: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional details",
    )

    def validate_domain_rules(self) -> None:
        """Validate domain rules for schema difference."""
        if not self.object_type.strip():
            msg = "Object type cannot be empty"
            raise ValueError(msg)
        if not self.object_name.strip():
            msg = "Object name cannot be empty"
            raise ValueError(msg)


class DataDifference(FlextValueObject):
    """Represents a difference in table data."""

    table_name: str = Field(..., description="Table name")
    row_identifier: dict[str, Any] = Field(
        ...,
        description="Primary key or unique identifier",
    )
    difference_type: DifferenceType = Field(..., description="Type of difference")
    changed_columns: list[str] = Field(
        default_factory=list,
        description="Changed column names",
    )
    old_values: dict[str, Any] = Field(
        default_factory=dict,
        description="Old column values",
    )
    new_values: dict[str, Any] = Field(
        default_factory=dict,
        description="New column values",
    )

    def validate_domain_rules(self) -> None:
        """Validate domain rules for data difference."""
        if not self.table_name.strip():
            msg = "Table name cannot be empty"
            raise ValueError(msg)
        if not self.row_identifier:
            msg = "Row identifier cannot be empty"
            raise ValueError(msg)


class ComparisonResult(FlextValueObject):
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

    def validate_domain_rules(self) -> None:
        """Validate domain rules for comparison result."""
        if not self.source_name.strip():
            msg = "Source name cannot be empty"
            raise ValueError(msg)
        if not self.target_name.strip():
            msg = "Target name cannot be empty"
            raise ValueError(msg)


class SchemaDiffer:
    """Analyzes differences between Oracle database schemas using flext-core."""

    def __init__(self) -> None:
        """Initialize the schema differ.

        No parameters required for this service.
        """

    def _is_table_metadata(self, obj: Any) -> TypeGuard[TableMetadata]:
        """Type guard to check if object is TableMetadata."""
        return (
            hasattr(obj, "columns")
            and hasattr(obj, "constraints")
            and hasattr(obj, "name")
        )

    async def compare_schemas(
        self,
        source_schema: SchemaMetadata | dict[str, Any],
        target_schema: SchemaMetadata | dict[str, Any],
    ) -> FlextResult[Any]:
        """Compare two schemas and return differences."""
        try:
            # Handle both dict and SchemaMetadata input types
            source_name = (
                source_schema.name
                if hasattr(source_schema, "name")
                else source_schema.get("schema_name", "unknown")
            )
            target_name = (
                target_schema.name
                if hasattr(target_schema, "name")
                else target_schema.get("schema_name", "unknown")
            )

            logger.info(
                "Comparing schemas: %s vs %s",
                source_name,
                target_name,
            )
            differences = []
            # Compare tables
            source_tables = (
                source_schema.tables
                if hasattr(source_schema, "tables")
                else source_schema.get("tables", [])
            )
            target_tables = (
                target_schema.tables
                if hasattr(target_schema, "tables")
                else target_schema.get("tables", [])
            )

            table_diffs = await self._compare_tables(
                source_tables,
                target_tables,
            )
            differences.extend(table_diffs)
            # Compare views
            source_views = (
                source_schema.views
                if hasattr(source_schema, "views")
                else source_schema.get("views", [])
            )
            target_views = (
                target_schema.views
                if hasattr(target_schema, "views")
                else target_schema.get("views", [])
            )
            view_diffs = await self._compare_views(
                source_views,
                target_views,
            )
            differences.extend(view_diffs)
            # Compare sequences
            source_sequences = (
                source_schema.sequences
                if hasattr(source_schema, "sequences")
                else source_schema.get("sequences", [])
            )
            target_sequences = (
                target_schema.sequences
                if hasattr(target_schema, "sequences")
                else target_schema.get("sequences", [])
            )
            seq_diffs = await self._compare_sequences(
                source_sequences,
                target_sequences,
            )
            differences.extend(seq_diffs)
            # Compare procedures
            source_procedures = (
                source_schema.procedures
                if hasattr(source_schema, "procedures")
                else source_schema.get("procedures", [])
            )
            target_procedures = (
                target_schema.procedures
                if hasattr(target_schema, "procedures")
                else target_schema.get("procedures", [])
            )
            proc_diffs = await self._compare_procedures(
                source_procedures,
                target_procedures,
            )
            differences.extend(proc_diffs)
            result = ComparisonResult(
                source_name=source_name,
                target_name=target_name,
                schema_differences=differences,
            )
            logger.info(
                "Schema comparison complete: %d differences found",
                len(differences),
            )
            return FlextResult.ok(result)
        except Exception as e:
            logger.exception("Schema comparison failed")
            return FlextResult.fail(f"Schema comparison failed: {e}")

    def _get_object_name(self, obj: dict[str, Any] | Any) -> str:
        """Get name from object (handle both dict and object types)."""
        if isinstance(obj, dict):
            return str(obj.get("table_name", obj.get("name", "unknown")))
        return str(getattr(obj, "name", "unknown"))

    async def _compare_tables(
        self,
        source_tables: list[TableMetadata] | list[dict[str, Any]],
        target_tables: list[TableMetadata] | list[dict[str, Any]],
    ) -> list[SchemaDifference]:
        """Compare tables between schemas."""
        differences = []
        source_names = {self._get_object_name(t).upper() for t in source_tables}
        target_names = {self._get_object_name(t).upper() for t in target_tables}
        # Find added tables
        for name in target_names - source_names:
            target_table = next(
                t for t in target_tables if self._get_object_name(t).upper() == name
            )
            target_value = (
                target_table.model_dump()
                if hasattr(target_table, "model_dump")
                else target_table
            )
            differences.append(
                SchemaDifference(
                    object_type="TABLE",
                    object_name=name,
                    difference_type=DifferenceType.ADDED,
                    source_value=None,
                    target_value=target_value,
                ),
            )
        # Find removed tables
        for name in source_names - target_names:
            source_table = next(
                t for t in source_tables if self._get_object_name(t).upper() == name
            )
            source_value = (
                source_table.model_dump()
                if hasattr(source_table, "model_dump")
                else source_table
            )
            differences.append(
                SchemaDifference(
                    object_type="TABLE",
                    object_name=name,
                    difference_type=DifferenceType.REMOVED,
                    source_value=source_value,
                    target_value=None,
                ),
            )
        # Find modified tables - only compare TableMetadata objects
        for name in source_names & target_names:
            source_table = next(
                t for t in source_tables if self._get_object_name(t).upper() == name
            )
            target_table = next(
                t for t in target_tables if self._get_object_name(t).upper() == name
            )

            # Only perform detailed comparison if both are TableMetadata objects
            if self._is_table_metadata(source_table) and self._is_table_metadata(
                target_table,
            ):
                table_diffs = await self._compare_table_details(
                    source_table,
                    target_table,
                )
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
            differences.append(
                SchemaDifference(
                    object_type="TABLE",
                    object_name=source_table.name,
                    difference_type=DifferenceType.MODIFIED,
                    source_value=len(source_table.columns),
                    target_value=len(target_table.columns),
                    details={
                        "change": "column_count",
                        "source_count": len(source_table.columns),
                        "target_count": len(target_table.columns),
                    },
                ),
            )
        # Compare constraints
        if len(source_table.constraints) != len(target_table.constraints):
            differences.append(
                SchemaDifference(
                    object_type="TABLE",
                    object_name=source_table.name,
                    difference_type=DifferenceType.MODIFIED,
                    source_value=len(source_table.constraints),
                    target_value=len(target_table.constraints),
                    details={
                        "change": "constraint_count",
                        "source_count": len(source_table.constraints),
                        "target_count": len(target_table.constraints),
                    },
                ),
            )
        # Compare indexes
        if len(source_table.indexes) != len(target_table.indexes):
            differences.append(
                SchemaDifference(
                    object_type="TABLE",
                    object_name=source_table.name,
                    difference_type=DifferenceType.MODIFIED,
                    source_value=len(source_table.indexes),
                    target_value=len(target_table.indexes),
                    details={
                        "change": "index_count",
                        "source_count": len(source_table.indexes),
                        "target_count": len(target_table.indexes),
                    },
                ),
            )
        return differences

    async def _compare_views(
        self,
        source_views: list[Any],
        target_views: list[Any],
    ) -> list[SchemaDifference]:
        """Compare views between schemas."""
        source_names = {
            v.get("name", "").upper() if isinstance(v, dict) else v.name.upper()
            for v in source_views
        }
        target_names = {
            v.get("name", "").upper() if isinstance(v, dict) else v.name.upper()
            for v in target_views
        }
        # Find added views
        differences = [
            SchemaDifference(
                object_type="VIEW",
                object_name=name,
                difference_type=DifferenceType.ADDED,
                source_value=None,
                target_value=None,
            )
            for name in target_names - source_names
        ]
        # Find removed views
        differences.extend(
            SchemaDifference(
                object_type="VIEW",
                object_name=name,
                difference_type=DifferenceType.REMOVED,
                source_value=None,
                target_value=None,
            )
            for name in source_names - target_names
        )
        return differences

    async def _compare_sequences(
        self,
        source_sequences: list[Any],
        target_sequences: list[Any],
    ) -> list[SchemaDifference]:
        """Compare sequences between schemas."""
        source_names = {s.get("name", "").upper() for s in source_sequences}
        target_names = {s.get("name", "").upper() for s in target_sequences}
        # Find added sequences
        differences = [
            SchemaDifference(
                object_type="SEQUENCE",
                object_name=name,
                difference_type=DifferenceType.ADDED,
                source_value=None,
                target_value=None,
            )
            for name in target_names - source_names
        ]
        # Find removed sequences
        differences.extend(
            SchemaDifference(
                object_type="SEQUENCE",
                object_name=name,
                difference_type=DifferenceType.REMOVED,
                source_value=None,
                target_value=None,
            )
            for name in source_names - target_names
        )
        return differences

    async def _compare_procedures(
        self,
        source_procedures: list[Any],
        target_procedures: list[Any],
    ) -> list[SchemaDifference]:
        """Compare procedures/functions between schemas."""
        source_names = {p.get("name", "").upper() for p in source_procedures}
        target_names = {p.get("name", "").upper() for p in target_procedures}
        # Find added procedures
        differences = [
            SchemaDifference(
                object_type="PROCEDURE",
                object_name=name,
                difference_type=DifferenceType.ADDED,
                source_value=None,
                target_value=None,
            )
            for name in target_names - source_names
        ]
        # Find removed procedures
        differences.extend(
            SchemaDifference(
                object_type="PROCEDURE",
                object_name=name,
                difference_type=DifferenceType.REMOVED,
                source_value=None,
                target_value=None,
            )
            for name in source_names - target_names
        )
        return differences


class DataDiffer:
    """Analyzes differences in Oracle table data using flext-core patterns."""

    def __init__(self) -> None:
        """Initialize the data differ.

        No parameters required for this service.
        """

    async def compare_table_data(
        self,
        source_connection_service: FlextDbOracleConnectionService,
        target_connection_service: FlextDbOracleConnectionService,
        table_name: str,
        primary_key_columns: list[str],
    ) -> FlextResult[Any]:
        """Compare data between two tables using primary key columns."""
        try:
            logger.info(
                "Comparing data for table: %s using PK: %s",
                table_name,
                primary_key_columns,
            )
            # First, compare row counts
            row_count_result = await self._compare_row_counts(
                source_connection_service,
                target_connection_service,
                table_name,
            )
            if not row_count_result.success:
                return FlextResult.fail(
                    row_count_result.error or "Row count comparison failed",
                )
            counts = row_count_result.data
            if not counts:
                return FlextResult.fail("Row count result is empty")
            source_count = counts["source_count"]
            target_count = counts["target_count"]
            logger.info(
                "Row counts - Source: %d, Target: %d",
                source_count,
                target_count,
            )
            # If counts differ, perform detailed comparison
            if source_count != target_count:
                return await self._perform_detailed_comparison(
                    source_connection_service,
                    target_connection_service,
                    table_name,
                    primary_key_columns,
                )
            # Counts are equal, return no differences
            logger.info("Data comparison complete for %s: 0 differences", table_name)
            return FlextResult.ok([])
        except Exception as e:
            logger.exception("Data comparison failed for %s", table_name)
            return FlextResult.fail(f"Data comparison failed: {e}")

    async def _perform_detailed_comparison(
        self,
        source_connection_service: FlextDbOracleConnectionService,
        target_connection_service: FlextDbOracleConnectionService,
        table_name: str,
        primary_key_columns: list[str],
    ) -> FlextResult[Any]:
        """Perform detailed row-by-row comparison when row counts differ."""
        logger.info("Row count mismatch detected, performing detailed comparison")
        # Validate identifiers first
        validation_result = await self._validate_identifiers(
            table_name,
            primary_key_columns,
        )
        if not validation_result.success:
            return FlextResult.fail(validation_result.error or "Validation failed")
        # Get data from both tables
        data_result = await self._fetch_table_data(
            source_connection_service,
            target_connection_service,
            table_name,
            primary_key_columns,
        )
        if not data_result.success:
            return FlextResult.fail(data_result.error or "Failed to fetch table data")
        if not data_result.data:
            return FlextResult.fail("Table data result is empty")
        source_rows, target_rows = data_result.data
        # Build dictionaries for efficient comparison
        source_dict, target_dict = self._build_row_dictionaries(
            source_rows,
            target_rows,
            primary_key_columns,
        )
        # Find and categorize differences
        differences = self._find_row_differences(
            source_dict,
            target_dict,
            table_name,
            primary_key_columns,
        )
        logger.info(
            "Data comparison complete for %s: %d differences",
            table_name,
            len(differences),
        )
        return FlextResult.ok(differences)

    async def _validate_identifiers(
        self,
        table_name: str,
        primary_key_columns: list[str],
    ) -> FlextResult[Any]:
        """Validate table and column names to prevent SQL injection."""
        oracle_identifier_pattern = re.compile(r"^[A-Za-z][A-Za-z0-9_#$]{0,29}$")
        if not oracle_identifier_pattern.match(table_name):
            return FlextResult.fail(f"Invalid table name: {table_name}")

        for pk_col in primary_key_columns:
            if not oracle_identifier_pattern.match(pk_col):
                return FlextResult.fail(f"Invalid column name: {pk_col}")

        return FlextResult.ok(None)

    async def _fetch_table_data(
        self,
        source_connection_service: FlextDbOracleConnectionService,
        target_connection_service: FlextDbOracleConnectionService,
        table_name: str,
        primary_key_columns: list[str],
    ) -> FlextResult[Any]:
        """Fetch ordered data from both tables."""
        # Validate identifiers to prevent SQL injection
        table_validation = flext_db_oracle_validate_table_name(table_name)
        if not table_validation.success:
            return FlextResult.fail(
                table_validation.error or "Table validation failed",
            )
        column_validation = flext_db_oracle_validate_column_names(primary_key_columns)
        if not column_validation.success:
            return FlextResult.fail(
                column_validation.error or "Column validation failed",
            )
        # Now safe to construct queries with validated identifiers
        # Build query using safe identifier substitution (already validated above)
        pk_columns_str = ", ".join(primary_key_columns)
        query_template = "SELECT * FROM {} ORDER BY {}"
        source_query = query_template.format(table_name, pk_columns_str)
        target_query = query_template.format(table_name, pk_columns_str)
        source_data_result = await source_connection_service.execute_query(source_query)
        target_data_result = await target_connection_service.execute_query(target_query)
        if not source_data_result.success or not target_data_result.success:
            return FlextResult.fail("Failed to retrieve table data for comparison")
        if not source_data_result.data or not target_data_result.data:
            return FlextResult.fail("Query results are empty")
        return FlextResult.ok(
            (
                source_data_result.data.rows,
                target_data_result.data.rows,
            ),
        )

    def _build_row_dictionaries(
        self,
        source_rows: list[tuple[Any, ...]],
        target_rows: list[tuple[Any, ...]],
        primary_key_columns: list[str],
    ) -> tuple[
        dict[tuple[Any, ...], tuple[Any, ...]],
        dict[tuple[Any, ...], tuple[Any, ...]],
    ]:
        """Build dictionaries using primary key as index for efficient comparison."""
        source_dict = {}
        target_dict = {}
        for row in source_rows:
            pk_key = tuple(row[i] for i in range(len(primary_key_columns)))
            source_dict[pk_key] = row
        for row in target_rows:
            pk_key = tuple(row[i] for i in range(len(primary_key_columns)))
            target_dict[pk_key] = row
        return source_dict, target_dict

    def _find_row_differences(
        self,
        source_dict: dict[tuple[Any, ...], tuple[Any, ...]],
        target_dict: dict[tuple[Any, ...], tuple[Any, ...]],
        table_name: str,
        primary_key_columns: list[str],
    ) -> list[DataDifference]:
        """Find and categorize differences between source and target data."""
        differences = []
        all_keys = set(source_dict.keys()) | set(target_dict.keys())
        for pk_key in all_keys:
            pk_dict = {
                pk_col: pk_key[i] for i, pk_col in enumerate(primary_key_columns)
            }
            if pk_key in source_dict and pk_key not in target_dict:
                # Row removed
                differences.append(
                    self._create_removed_difference(
                        table_name,
                        pk_dict,
                        source_dict[pk_key],
                    ),
                )
            elif pk_key not in source_dict and pk_key in target_dict:
                # Row added
                differences.append(
                    self._create_added_difference(
                        table_name,
                        pk_dict,
                        target_dict[pk_key],
                    ),
                )
            elif source_dict[pk_key] != target_dict[pk_key]:
                # Row modified
                modified_diff = self._create_modified_difference(
                    table_name,
                    pk_dict,
                    source_dict[pk_key],
                    target_dict[pk_key],
                )
                if modified_diff:
                    differences.append(modified_diff)
        return differences

    def _create_removed_difference(
        self,
        table_name: str,
        pk_dict: dict[str, Any],
        source_row: tuple[Any, ...],
    ) -> DataDifference:
        """Create a DataDifference for a removed row."""
        return DataDifference(
            table_name=table_name,
            row_identifier=pk_dict,
            difference_type=DifferenceType.REMOVED,
            old_values={f"col_{i}": val for i, val in enumerate(source_row)},
            new_values={},
        )

    def _create_added_difference(
        self,
        table_name: str,
        pk_dict: dict[str, Any],
        target_row: tuple[Any, ...],
    ) -> DataDifference:
        """Create a DataDifference for an added row."""
        return DataDifference(
            table_name=table_name,
            row_identifier=pk_dict,
            difference_type=DifferenceType.ADDED,
            old_values={},
            new_values={f"col_{i}": val for i, val in enumerate(target_row)},
        )

    def _create_modified_difference(
        self,
        table_name: str,
        pk_dict: dict[str, Any],
        source_row: tuple[Any, ...],
        target_row: tuple[Any, ...],
    ) -> DataDifference | None:
        """Create a DataDifference for a modified row."""
        changed_columns = []
        old_values = {}
        new_values = {}
        for i, (source_val, target_val) in enumerate(
            zip(source_row, target_row, strict=True),
        ):
            if source_val != target_val:
                col_name = f"col_{i}"
                changed_columns.append(col_name)
                old_values[col_name] = source_val
                new_values[col_name] = target_val
        if not changed_columns:
            return None
        return DataDifference(
            table_name=table_name,
            row_identifier=pk_dict,
            difference_type=DifferenceType.MODIFIED,
            changed_columns=changed_columns,
            old_values=old_values,
            new_values=new_values,
        )

    async def _compare_row_counts(
        self,
        source_connection_service: FlextDbOracleConnectionService,
        target_connection_service: FlextDbOracleConnectionService,
        table_name: str,
    ) -> FlextResult[Any]:
        """Compare row counts between tables."""
        try:
            # Validate table name to prevent SQL injection
            table_validation = flext_db_oracle_validate_table_name(table_name)
            if not table_validation.success:
                return FlextResult.fail(
                    table_validation.error or "Table validation failed",
                )
            # Now safe to construct queries with validated identifier
            count_query = f"SELECT COUNT(*) FROM {table_name}"
            source_result = await source_connection_service.execute_query(count_query)
            target_result = await target_connection_service.execute_query(count_query)
            if not source_result.success or not target_result.success:
                return FlextResult.fail("Failed to get row counts")
            if not source_result.data or not source_result.data.rows:
                return FlextResult.fail("Source count query returned no results")
            if not target_result.data or not target_result.data.rows:
                return FlextResult.fail("Target count query returned no results")
            counts = {
                "source_count": source_result.data.rows[0][0],
                "target_count": target_result.data.rows[0][0],
            }
            return FlextResult.ok(counts)
        except Exception as e:
            logger.exception("Row count comparison failed")
            return FlextResult.fail(f"Row count comparison failed: {e}")

    async def compare_large_table_data(
        self,
        source_connection_service: FlextDbOracleConnectionService,
        target_connection_service: FlextDbOracleConnectionService,
        table_name: str,
        primary_key_columns: list[str],
        batch_size: int = 10000,
    ) -> FlextResult[Any]:
        """Compare data between two large tables using batched approach."""
        try:
            logger.info(
                "Starting large table comparison for: %s (batch size: %d)",
                table_name,
                batch_size,
            )
            # Get total row counts first
            row_count_result = await self._compare_row_counts(
                source_connection_service,
                target_connection_service,
                table_name,
            )
            if not row_count_result.success:
                return FlextResult.fail(
                    row_count_result.error or "Failed to get row counts",
                )
            counts = row_count_result.data
            if not counts:
                return FlextResult.fail("Row count result is empty")
            source_count = counts["source_count"]
            target_count = counts["target_count"]
            logger.info(
                "Large table comparison - Source: %d rows, Target: %d rows",
                source_count,
                target_count,
            )
            # If counts are equal and tables are large, use hash-based comparison
            if source_count == target_count and source_count > batch_size:
                hash_result = await self._compare_using_hashes(
                    source_connection_service,
                    target_connection_service,
                    table_name,
                    primary_key_columns,
                    batch_size=batch_size,
                )
                if hash_result.success:
                    return hash_result
            # Fall back to batched row-by-row comparison
            return await self._compare_in_batches(
                source_connection_service,
                target_connection_service,
                table_name,
                primary_key_columns,
                batch_size,
            )
        except Exception as e:
            logger.exception("Large table comparison failed for %s", table_name)
            return FlextResult.fail(f"Large table comparison failed: {e}")

    async def _compare_using_hashes(
        self,
        source_connection_service: FlextDbOracleConnectionService,
        target_connection_service: FlextDbOracleConnectionService,
        table_name: str,
        primary_key_columns: list[str],
        *,
        batch_size: int,  # Used for fallback decision in calling method
    ) -> FlextResult[Any]:
        """Compare tables using hash-based approach for performance."""
        try:
            logger.info("Using hash-based comparison for table: %s", table_name)

            # Validate identifiers to prevent SQL injection
            validation_result = await self._validate_identifiers(
                table_name,
                primary_key_columns,
            )
            if not validation_result.success:
                return validation_result

            # Execute hash queries on both tables
            hash_result = await self._execute_hash_queries(
                source_connection_service,
                target_connection_service,
                table_name,
                primary_key_columns,
            )
            if not hash_result.success:
                return hash_result

            if hash_result.data is None:
                return FlextResult.fail("Hash computation returned no data")

            source_hashes, target_hashes = hash_result.data

            # Find and categorize differences using hash comparison
            differences = self._find_hash_differences(
                source_hashes,
                target_hashes,
                table_name,
                primary_key_columns,
            )

            logger.info(
                "Hash-based comparison complete: %d differences found",
                len(differences),
            )
            return FlextResult.ok(differences)
        except Exception as e:
            logger.exception("Hash-based comparison failed")
            return FlextResult.fail(f"Hash-based comparison failed: {e}")

    async def _execute_hash_queries(
        self,
        source_connection_service: FlextDbOracleConnectionService,
        target_connection_service: FlextDbOracleConnectionService,
        table_name: str,
        primary_key_columns: list[str],
    ) -> FlextResult[Any]:
        """Execute hash queries on both source and target tables."""
        pk_columns_str = ", ".join(primary_key_columns)
        # Create hash query with validated identifiers
        hash_query_template = """
            SELECT {},
                   ORA_HASH(CONCAT_WS('|', *)) as row_hash
            FROM {}
            ORDER BY {}
        """
        hash_query = hash_query_template.format(
            pk_columns_str,
            table_name,
            pk_columns_str,
        )

        # Get hashes from both tables
        source_hashes_result = await source_connection_service.execute_query(
            hash_query,
        )
        target_hashes_result = await target_connection_service.execute_query(
            hash_query,
        )

        if not source_hashes_result.success or not target_hashes_result.success:
            logger.warning("Hash comparison failed, falling back to row comparison")
            return FlextResult.fail("Hash comparison not supported")

        # Check if results have value and rows
        source_result = source_hashes_result.data
        target_result = target_hashes_result.data
        if not source_result or not target_result:
            return FlextResult.fail("Query results are empty")

        source_hashes = {tuple(row[:-1]): row[-1] for row in source_result.rows}
        target_hashes = {tuple(row[:-1]): row[-1] for row in target_result.rows}

        return FlextResult.ok((source_hashes, target_hashes))

    def _find_hash_differences(
        self,
        source_hashes: dict[tuple[Any, ...], Any],
        target_hashes: dict[tuple[Any, ...], Any],
        table_name: str,
        primary_key_columns: list[str],
    ) -> list[DataDifference]:
        """Find differences by comparing hash values."""
        differences = []
        all_keys = set(source_hashes.keys()) | set(target_hashes.keys())

        for pk_key in all_keys:
            pk_dict = {
                pk_col: pk_key[i] for i, pk_col in enumerate(primary_key_columns)
            }

            if pk_key in source_hashes and pk_key not in target_hashes:
                # Row removed
                differences.append(
                    DataDifference(
                        table_name=table_name,
                        row_identifier=pk_dict,
                        difference_type=DifferenceType.REMOVED,
                        changed_columns=["*"],
                        old_values={"status": "exists_in_source"},
                        new_values={},
                    ),
                )
            elif pk_key not in source_hashes and pk_key in target_hashes:
                # Row added
                differences.append(
                    DataDifference(
                        table_name=table_name,
                        row_identifier=pk_dict,
                        difference_type=DifferenceType.ADDED,
                        changed_columns=["*"],
                        old_values={},
                        new_values={"status": "exists_in_target"},
                    ),
                )
            elif source_hashes[pk_key] != target_hashes[pk_key]:
                # Row modified (hashes differ)
                differences.append(
                    DataDifference(
                        table_name=table_name,
                        row_identifier=pk_dict,
                        difference_type=DifferenceType.MODIFIED,
                        changed_columns=["*"],
                        old_values={"hash": str(source_hashes[pk_key])},
                        new_values={"hash": str(target_hashes[pk_key])},
                    ),
                )

        return differences

    async def _compare_in_batches(
        self,
        source_connection_service: FlextDbOracleConnectionService,
        target_connection_service: FlextDbOracleConnectionService,
        table_name: str,
        primary_key_columns: list[str],
        batch_size: int,
    ) -> FlextResult[Any]:
        """Compare tables in batches for memory efficiency."""
        try:
            logger.info("Using batched comparison for table: %s", table_name)
            # Validate identifiers to prevent SQL injection
            table_validation = flext_db_oracle_validate_table_name(table_name)
            if not table_validation.success:
                return FlextResult.fail(
                    table_validation.error or "Table validation failed",
                )
            column_validation = flext_db_oracle_validate_column_names(
                primary_key_columns,
            )
            if not column_validation.success:
                return FlextResult.fail(
                    column_validation.error or "Column validation failed",
                )
            pk_columns_str = ", ".join(primary_key_columns)
            # Get total row count for progress tracking with validated identifier
            count_query = f"SELECT COUNT(*) FROM {table_name}"
            count_result = await source_connection_service.execute_query(count_query)
            total_rows = 0
            if count_result.success and count_result.data and count_result.data.rows:
                total_rows = count_result.data.rows[0][0]
            all_differences = []
            offset = 0
            while True:
                # Fetch batch from both tables with validated identifiers
                # Build batch query with validated identifiers
                batch_query_template = """
                    SELECT * FROM (
                        SELECT t.*, ROW_NUMBER() OVER (ORDER BY {}) as rn
                        FROM {} t
                    ) WHERE rn > {} AND rn <= {}
                    ORDER BY {}
                """
                batch_query = batch_query_template.format(
                    pk_columns_str,
                    table_name,
                    offset,
                    offset + batch_size,
                    pk_columns_str,
                )
                source_batch_result = await source_connection_service.execute_query(
                    batch_query,
                )
                target_batch_result = await target_connection_service.execute_query(
                    batch_query,
                )
                if not source_batch_result.success or not target_batch_result.success:
                    return FlextResult.fail("Failed to fetch batch data")
                # Check if batch results have value and rows
                source_result = source_batch_result.data
                target_result = target_batch_result.data
                if not source_result or not target_result:
                    return FlextResult.fail("Batch query results are empty")
                source_rows = source_result.rows
                target_rows = target_result.rows
                # No more data to process
                if not source_rows and not target_rows:
                    break
                # Process this batch
                batch_differences = self._compare_batch_data(
                    source_rows,
                    target_rows,
                    table_name,
                    primary_key_columns,
                )
                all_differences.extend(batch_differences)
                logger.info(
                    "Processed batch %d-%d of %d rows (%d differences found)",
                    offset + 1,
                    offset + len(source_rows),
                    total_rows,
                    len(batch_differences),
                )
                offset += batch_size
                # If we got less than batch_size, we're done
                if len(source_rows) < batch_size:
                    break
            logger.info(
                "Batched comparison complete: %d total differences",
                len(all_differences),
            )
            return FlextResult.ok(all_differences)
        except Exception as e:
            logger.exception("Batched comparison failed")
            return FlextResult.fail(f"Batched comparison failed: {e}")

    def _compare_batch_data(
        self,
        source_rows: list[tuple[Any, ...]],
        target_rows: list[tuple[Any, ...]],
        table_name: str,
        primary_key_columns: list[str],
    ) -> list[DataDifference]:
        """Compare a batch of rows efficiently."""
        # Build dictionaries for this batch
        source_dict, target_dict = self._build_row_dictionaries(
            source_rows,
            target_rows,
            primary_key_columns,
        )
        # Find differences in this batch
        return self._find_row_differences(
            source_dict,
            target_dict,
            table_name,
            primary_key_columns,
        )
