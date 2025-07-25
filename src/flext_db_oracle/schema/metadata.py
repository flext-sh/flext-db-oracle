"""Database schema metadata classes for Oracle.

Built on flext-core foundation with comprehensive Oracle schema support.
Uses modern Python 3.13 typing and Pydantic v2 for validation.
"""

from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from typing import Any
from uuid import uuid4

from flext_core import (
    FlextEntity as DomainEntity,
    FlextEntityId as EntityId,
    FlextValueObject,
)
from pydantic import Field


class ConstraintType(StrEnum):
    """Database constraint types."""

    PRIMARY_KEY = "PRIMARY_KEY"
    FOREIGN_KEY = "FOREIGN_KEY"
    UNIQUE = "UNIQUE"
    CHECK = "CHECK"
    NOT_NULL = "NOT_NULL"


class ObjectStatus(StrEnum):
    """Database object status."""

    VALID = "VALID"
    INVALID = "INVALID"
    DISABLED = "DISABLED"
    ENABLED = "ENABLED"


class ColumnMetadata(FlextValueObject):
    """Metadata for an Oracle database column."""

    name: str = Field(..., description="Column name")
    data_type: str = Field(..., description="Oracle data type")
    nullable: bool = Field(
        default=True,
        description="Whether column allows NULL values",
    )
    default_value: str | None = Field(None, description="Default value")
    max_length: int | None = Field(None, description="Maximum length", ge=0)
    precision: int | None = Field(None, description="Numeric precision", ge=0)
    scale: int | None = Field(None, description="Numeric scale", ge=0)
    column_id: int = Field(..., description="Column position", ge=1)
    is_primary_key: bool = Field(default=False, description="Is primary key column")
    is_foreign_key: bool = Field(default=False, description="Is foreign key column")
    foreign_key_table: str | None = Field(None, description="Referenced table name")
    foreign_key_column: str | None = Field(None, description="Referenced column name")
    comments: str | None = Field(None, description="Column comments")

    @property
    def is_numeric(self) -> bool:
        """Check if column is numeric type."""
        return self.data_type.upper() in {
            "NUMBER",
            "DECIMAL",
            "FLOAT",
            "BINARY_FLOAT",
            "BINARY_DOUBLE",
        }

    @property
    def is_date(self) -> bool:
        """Check if column is date/time type."""
        return self.data_type.upper() in {
            "DATE",
            "TIMESTAMP",
            "TIMESTAMP WITH TIME ZONE",
            "TIMESTAMP WITH LOCAL TIME ZONE",
            "INTERVAL YEAR TO MONTH",
            "INTERVAL DAY TO SECOND",
        }

    @property
    def is_lob(self) -> bool:
        """Check if column is LOB type."""
        return self.data_type.upper() in {"CLOB", "BLOB", "NCLOB", "BFILE"}

    def validate_domain_rules(self) -> None:
        """Validate domain rules for column metadata."""
        if not self.name.strip():
            msg = "Column name cannot be empty"
            raise ValueError(msg)
        if not self.data_type.strip():
            msg = "Data type cannot be empty"
            raise ValueError(msg)
        if self.column_id <= 0:
            msg = "Column ID must be positive"
            raise ValueError(msg)
        if self.max_length is not None and self.max_length <= 0:
            msg = "Max length must be positive"
            raise ValueError(msg)
        if self.precision is not None and self.precision <= 0:
            msg = "Precision must be positive"
            raise ValueError(msg)
        if self.scale is not None and self.scale < 0:
            msg = "Scale cannot be negative"
            raise ValueError(msg)


class ConstraintMetadata(FlextValueObject):
    """Metadata for an Oracle database constraint."""

    name: str = Field(..., description="Constraint name")
    constraint_type: ConstraintType = Field(..., description="Constraint type")
    table_name: str = Field(..., description="Table name")
    column_names: list[str] = Field(..., description="Constrained column names")
    referenced_table: str | None = Field(None, description="Referenced table (FK only)")
    referenced_columns: list[str] = Field(
        default_factory=list,
        description="Referenced columns (FK only)",
    )
    check_condition: str | None = Field(None, description="Check constraint condition")
    status: ObjectStatus = Field(ObjectStatus.ENABLED, description="Constraint status")
    deferrable: bool = Field(default=False, description="Is constraint deferrable")
    initially_deferred: bool = Field(default=False, description="Is initially deferred")

    @property
    def is_foreign_key(self) -> bool:
        """Check if this is a foreign key constraint."""
        return self.constraint_type == ConstraintType.FOREIGN_KEY

    @property
    def is_primary_key(self) -> bool:
        """Check if this is a primary key constraint."""
        return self.constraint_type == ConstraintType.PRIMARY_KEY

    def validate_domain_rules(self) -> None:
        """Validate domain rules for constraint metadata."""
        if not self.name.strip():
            msg = "Constraint name cannot be empty"
            raise ValueError(msg)
        if not self.table_name.strip():
            msg = "Table name cannot be empty"
            raise ValueError(msg)
        if not self.column_names:
            msg = "Column names cannot be empty"
            raise ValueError(msg)
        if self.constraint_type == ConstraintType.FOREIGN_KEY:
            if not self.referenced_table:
                msg = "Foreign key must have referenced table"
                raise ValueError(msg)
            if not self.referenced_columns:
                msg = "Foreign key must have referenced columns"
                raise ValueError(msg)


class IndexMetadata(FlextValueObject):
    """Metadata for an Oracle database index."""

    name: str = Field(..., description="Index name")
    table_name: str = Field(..., description="Table name")
    column_names: list[str] = Field(..., description="Indexed column names")
    is_unique: bool = Field(default=False, description="Is unique index")
    is_primary: bool = Field(default=False, description="Is primary key index")
    index_type: str = Field("NORMAL", description="Index type")
    tablespace_name: str | None = Field(None, description="Tablespace name")
    status: ObjectStatus = Field(ObjectStatus.VALID, description="Index status")
    degree: int = Field(1, description="Parallel degree", ge=1)
    compression: str | None = Field(None, description="Compression type")

    @property
    def is_functional(self) -> bool:
        """Check if this is a function-based index."""
        return self.index_type.upper() == "FUNCTION-BASED NORMAL"

    @property
    def is_bitmap(self) -> bool:
        """Check if this is a bitmap index."""
        return self.index_type.upper() == "BITMAP"

    def validate_domain_rules(self) -> None:
        """Validate domain rules for index metadata."""
        if not self.name.strip():
            msg = "Index name cannot be empty"
            raise ValueError(msg)
        if not self.table_name.strip():
            msg = "Table name cannot be empty"
            raise ValueError(msg)
        if not self.column_names:
            msg = "Column names cannot be empty"
            raise ValueError(msg)
        if self.degree <= 0:
            msg = "Degree must be positive"
            raise ValueError(msg)


class TableMetadata(DomainEntity):
    """Metadata for an Oracle database table."""

    id: EntityId = Field(default_factory=lambda: str(uuid4()))
    name: str = Field(..., description="Table name")
    schema_name: str = Field(..., description="Schema/owner name")
    tablespace_name: str | None = Field(None, description="Tablespace name")
    status: ObjectStatus = Field(ObjectStatus.VALID, description="Table status")
    num_rows: int | None = Field(None, description="Estimated row count", ge=0)
    blocks: int | None = Field(None, description="Allocated blocks", ge=0)
    avg_row_len: int | None = Field(None, description="Average row length", ge=0)
    compression: str | None = Field(None, description="Compression type")
    degree: int = Field(1, description="Parallel degree", ge=1)

    # Related metadata
    columns: list[ColumnMetadata] = Field(
        default_factory=list,
        description="Table columns",
    )
    constraints: list[ConstraintMetadata] = Field(
        default_factory=list,
        description="Table constraints",
    )
    indexes: list[IndexMetadata] = Field(
        default_factory=list,
        description="Table indexes",
    )

    # Timestamps
    created: datetime | None = Field(None, description="Creation timestamp")
    last_ddl_time: datetime | None = Field(None, description="Last DDL timestamp")
    last_analyzed: datetime | None = Field(None, description="Last statistics analysis")

    @property
    def primary_key_columns(self) -> list[str]:
        """Get primary key column names."""
        for constraint in self.constraints:
            if constraint.is_primary_key:
                return constraint.column_names
        return []

    @property
    def foreign_key_constraints(self) -> list[ConstraintMetadata]:
        """Get all foreign key constraints."""
        return [c for c in self.constraints if c.is_foreign_key]

    @property
    def unique_indexes(self) -> list[IndexMetadata]:
        """Get all unique indexes."""
        return [i for i in self.indexes if i.is_unique]

    @property
    def is_partitioned(self) -> bool:
        """Check if table is partitioned (placeholder)."""
        # This would need additional metadata from DBA_TAB_PARTITIONS
        return False

    @property
    def estimated_size_mb(self) -> float:
        """Estimate table size in MB."""
        if self.blocks and self.avg_row_len and self.num_rows:
            # Oracle block size is typically 8KB
            return (self.blocks * 8) / 1024
        return 0.0

    def validate_domain_rules(self) -> None:
        """Validate domain rules for table metadata."""
        if not self.name.strip():
            msg = "Table name cannot be empty"
            raise ValueError(msg)
        if not self.schema_name.strip():
            msg = "Schema name cannot be empty"
            raise ValueError(msg)
        if self.num_rows is not None and self.num_rows < 0:
            msg = "Number of rows cannot be negative"
            raise ValueError(msg)
        if self.blocks is not None and self.blocks < 0:
            msg = "Blocks cannot be negative"
            raise ValueError(msg)
        if self.avg_row_len is not None and self.avg_row_len < 0:
            msg = "Average row length cannot be negative"
            raise ValueError(msg)
        if self.degree <= 0:
            msg = "Degree must be positive"
            raise ValueError(msg)


class ViewMetadata(DomainEntity):
    """Metadata for an Oracle database view."""

    id: EntityId = Field(default_factory=lambda: str(uuid4()))
    name: str = Field(..., description="View name")
    schema_name: str = Field(..., description="Schema/owner name")
    text_length: int = Field(0, description="View definition length", ge=0)
    text: str | None = Field(None, description="View definition SQL")
    status: ObjectStatus = Field(ObjectStatus.VALID, description="View status")

    # Related metadata
    columns: list[ColumnMetadata] = Field(
        default_factory=list,
        description="View columns",
    )

    # Timestamps
    created: datetime | None = Field(None, description="Creation timestamp")
    last_ddl_time: datetime | None = Field(None, description="Last DDL timestamp")

    @property
    def is_materialized(self) -> bool:
        """Check if this is a materialized view."""
        # This would need to be determined from DBA_MVIEWS
        return False

    def validate_domain_rules(self) -> None:
        """Validate domain rules for view metadata."""
        if not self.name.strip():
            msg = "View name cannot be empty"
            raise ValueError(msg)
        if not self.schema_name.strip():
            msg = "Schema name cannot be empty"
            raise ValueError(msg)
        if self.text_length < 0:
            msg = "Text length cannot be negative"
            raise ValueError(msg)


class SchemaMetadata(DomainEntity):
    """Complete metadata for an Oracle database schema."""

    id: EntityId = Field(default_factory=lambda: str(uuid4()))
    name: str = Field(..., description="Schema name")
    default_tablespace: str | None = Field(None, description="Default tablespace")
    temporary_tablespace: str | None = Field(None, description="Temporary tablespace")
    status: ObjectStatus = Field(ObjectStatus.VALID, description="Schema status")

    # Schema objects
    tables: list[TableMetadata] = Field(
        default_factory=list,
        description="Schema tables",
    )
    views: list[ViewMetadata] = Field(default_factory=list, description="Schema views")
    sequences: list[dict[str, Any]] = Field(
        default_factory=list,
        description="Schema sequences",
    )
    procedures: list[dict[str, Any]] = Field(
        default_factory=list,
        description="Schema procedures/functions",
    )

    # Analysis metadata
    analyzed_at: datetime = Field(
        default_factory=datetime.now,
        description="Analysis timestamp",
    )
    total_objects: int = Field(0, description="Total object count", ge=0)
    total_size_mb: float = Field(0.0, description="Total estimated size in MB", ge=0.0)

    @property
    def table_count(self) -> int:
        """Get number of tables."""
        return len(self.tables)

    @property
    def view_count(self) -> int:
        """Get number of views."""
        return len(self.views)

    @property
    def sequence_count(self) -> int:
        """Get number of sequences."""
        return len(self.sequences)

    @property
    def procedure_count(self) -> int:
        """Get number of procedures/functions."""
        return len(self.procedures)

    def get_table(self, table_name: str) -> TableMetadata | None:
        """Get table metadata by name."""
        for table in self.tables:
            if table.name.upper() == table_name.upper():
                return table
        return None

    def get_view(self, view_name: str) -> ViewMetadata | None:
        """Get view metadata by name."""
        for view in self.views:
            if view.name.upper() == view_name.upper():
                return view
        return None

    def validate_domain_rules(self) -> None:
        """Validate domain rules for schema metadata."""
        if not self.name.strip():
            msg = "Schema name cannot be empty"
            raise ValueError(msg)
        if self.total_objects < 0:
            msg = "Total objects cannot be negative"
            raise ValueError(msg)
        if self.total_size_mb < 0:
            msg = "Total size cannot be negative"
            raise ValueError(msg)
