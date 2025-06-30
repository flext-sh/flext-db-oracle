"""Database schema metadata classes for Oracle."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class ColumnMetadata:
    """Metadata for a database column."""

    name: str
    data_type: str
    nullable: bool
    default_value: str | None = None
    max_length: int | None = None
    precision: int | None = None
    scale: int | None = None
    is_primary_key: bool = False
    is_foreign_key: bool = False
    foreign_key_table: str | None = None
    foreign_key_column: str | None = None
    comments: str | None = None


@dataclass
class ConstraintMetadata:
    """Metadata for a database constraint."""

    name: str
    constraint_type: str  # PRIMARY_KEY, FOREIGN_KEY, UNIQUE, CHECK, NOT_NULL
    table_name: str
    column_names: list[str]
    referenced_table: str | None = None
    referenced_columns: list[str] | None = None
    condition: str | None = None  # For CHECK constraints
    is_enabled: bool = True
    is_validated: bool = True


@dataclass
class IndexMetadata:
    """Metadata for a database index."""

    name: str
    table_name: str
    column_names: list[str]
    is_unique: bool = False
    is_primary: bool = False
    index_type: str = "NORMAL"  # NORMAL, BITMAP, FUNCTION_BASED, etc.
    tablespace: str | None = None
    is_valid: bool = True
    comments: str | None = None


@dataclass
class TableMetadata:
    """Metadata for a database table."""

    name: str
    schema_name: str
    table_type: str = "TABLE"  # TABLE, VIEW, MATERIALIZED_VIEW
    columns: list[ColumnMetadata] | None = None
    constraints: list[ConstraintMetadata] | None = None
    indexes: list[IndexMetadata] | None = None
    row_count: int | None = None
    tablespace: str | None = None
    comments: str | None = None
    created_date: str | None = None
    last_modified: str | None = None

    def get_primary_key_columns(self) -> list[str]:
        """Get primary key column names."""
        if not self.columns:
            return []
        return [col.name for col in self.columns if col.is_primary_key]

    def get_foreign_key_columns(self) -> list[str]:
        """Get foreign key column names."""
        if not self.columns:
            return []
        return [col.name for col in self.columns if col.is_foreign_key]


@dataclass
class SchemaMetadata:
    """Metadata for a database schema."""

    name: str
    tables: list[TableMetadata] | None = None
    views: list[TableMetadata] | None = None
    sequences: list[str] | None = None
    procedures: list[str] | None = None
    functions: list[str] | None = None
    packages: list[str] | None = None
    triggers: list[str] | None = None
    created_date: str | None = None

    def get_table_names(self) -> list[str]:
        """Get all table names in the schema."""
        if not self.tables:
            return []
        return [table.name for table in self.tables]

    def get_view_names(self) -> list[str]:
        """Get all view names in the schema."""
        if not self.views:
            return []
        return [view.name for view in self.views]

    def find_table(self, table_name: str) -> TableMetadata | None:
        """Find table metadata by name."""
        if not self.tables:
            return None

        for table in self.tables:
            if table.name.upper() == table_name.upper():
                return table
        return None
