"""Oracle Database Types using flext-core patterns.

Consolidated type definitions using proper FlextDbOracle prefixing.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

from flext_core import FlextResult, FlextValueObject
from pydantic import Field

from .constants import (
    ERROR_MSG_COLUMN_NAME_EMPTY,
    ERROR_MSG_DATA_TYPE_EMPTY,
    ERROR_MSG_HOST_EMPTY,
    ERROR_MSG_PORT_INVALID,
    ERROR_MSG_POSITION_INVALID,
    ERROR_MSG_SCHEMA_NAME_EMPTY,
    ERROR_MSG_TABLE_NAME_EMPTY,
    ERROR_MSG_USERNAME_EMPTY,
    MAX_PORT,
)


class TDbOracleColumn(FlextValueObject):
    """Oracle column type definition."""

    name: str = Field(..., description="Column name")
    data_type: str = Field(..., description="Oracle data type")
    nullable: bool = Field(default=True, description="Nullable flag")
    default_value: str | None = Field(None, description="Default value")
    max_length: int | None = Field(None, description="Maximum length")
    precision: int | None = Field(None, description="Numeric precision")
    scale: int | None = Field(None, description="Numeric scale")
    position: int = Field(..., description="Column position")
    comments: str | None = Field(None, description="Column comments")

    # Consolidated functionality from domain models
    is_primary_key: bool = Field(
        default=False, description="Whether column is primary key",
    )
    is_foreign_key: bool = Field(
        default=False, description="Whether column is foreign key",
    )

    def validate_domain_rules(self) -> FlextResult[None]:
        """Validate column type domain rules."""
        try:
            if not self.name or not self.name.strip():
                return FlextResult.fail(ERROR_MSG_COLUMN_NAME_EMPTY)

            if not self.data_type or not self.data_type.strip():
                return FlextResult.fail(ERROR_MSG_DATA_TYPE_EMPTY)

            if self.position <= 0:
                return FlextResult.fail(ERROR_MSG_POSITION_INVALID)

            return FlextResult.ok(None)
        except (ValueError, TypeError, AttributeError) as e:
            return FlextResult.fail(f"Column validation failed: {e}")

    @property
    def full_type_spec(self) -> str:
        """Get complete Oracle type specification."""
        type_spec = self.data_type.upper()

        if self.max_length and "VARCHAR" in type_spec:
            type_spec = f"{type_spec}({self.max_length})"
        elif self.precision and "NUMBER" in type_spec:
            if self.scale is not None:
                type_spec = f"{type_spec}({self.precision},{self.scale})"
            else:
                type_spec = f"{type_spec}({self.precision})"

        return type_spec

    @property
    def is_key_column(self) -> bool:
        """Check if column is primary or foreign key (consolidated logic)."""
        return self.is_primary_key or self.is_foreign_key


class TDbOracleTable(FlextValueObject):
    """Oracle table type definition."""

    name: str = Field(..., description="Table name")
    schema_name: str = Field(..., description="Schema name")
    columns: list[TDbOracleColumn] = Field(
        default_factory=list, description="Table columns",
    )
    row_count: int | None = Field(None, description="Estimated row count")
    size_bytes: int | None = Field(None, description="Table size in bytes")
    tablespace: str | None = Field(None, description="Tablespace name")
    created_date: datetime | None = Field(None, description="Creation date")
    comments: str | None = Field(None, description="Table comments")

    def validate_domain_rules(self) -> FlextResult[None]:
        """Validate table type domain rules."""
        try:
            if not self.name or not self.name.strip():
                return FlextResult.fail(ERROR_MSG_TABLE_NAME_EMPTY)

            if not self.schema_name or not self.schema_name.strip():
                return FlextResult.fail(ERROR_MSG_SCHEMA_NAME_EMPTY)

            if not self.columns:
                return FlextResult.fail("Table must have at least one column")

            # Validate columns
            for column in self.columns:
                validation = column.validate_domain_rules()
                if validation.is_failure:
                    return FlextResult.fail(f"Column {column.name}: {validation.error}")

            return FlextResult.ok(None)
        except (ValueError, TypeError, AttributeError) as e:
            return FlextResult.fail(f"Table validation failed: {e}")

    def get_column(self, column_name: str) -> TDbOracleColumn | None:
        """Get column by name."""
        for column in self.columns:
            if column.name.upper() == column_name.upper():
                return column
        return None

    @property
    def column_names(self) -> list[str]:
        """Get list of column names."""
        return [col.name for col in self.columns]

    @property
    def qualified_name(self) -> str:
        """Get fully qualified table name."""
        return f"{self.schema_name}.{self.name}"

    @property
    def primary_key_columns(self) -> list[TDbOracleColumn]:
        """Get primary key columns (consolidated logic)."""
        return [col for col in self.columns if col.is_primary_key]

    @property
    def foreign_key_columns(self) -> list[TDbOracleColumn]:
        """Get foreign key columns (consolidated logic)."""
        return [col for col in self.columns if col.is_foreign_key]


class TDbOracleSchema(FlextValueObject):
    """Oracle schema type definition."""

    name: str = Field(..., description="Schema name")
    tables: list[TDbOracleTable] = Field(
        default_factory=list, description="Schema tables",
    )
    created_date: datetime | None = Field(None, description="Schema creation date")
    default_tablespace: str | None = Field(None, description="Default tablespace")

    def validate_domain_rules(self) -> FlextResult[None]:
        """Validate schema type domain rules."""
        try:
            if not self.name or not self.name.strip():
                return FlextResult.fail(ERROR_MSG_SCHEMA_NAME_EMPTY)

            # Validate tables
            for table in self.tables:
                validation = table.validate_domain_rules()
                if validation.is_failure:
                    return FlextResult.fail(f"Table {table.name}: {validation.error}")

            return FlextResult.ok(None)
        except (ValueError, TypeError, AttributeError) as e:
            return FlextResult.fail(f"Schema validation failed: {e}")

    def get_table(self, table_name: str) -> TDbOracleTable | None:
        """Get table by name."""
        for table in self.tables:
            if table.name.upper() == table_name.upper():
                return table
        return None

    @property
    def table_count(self) -> int:
        """Get number of tables."""
        return len(self.tables)

    @property
    def total_columns(self) -> int:
        """Get total number of columns across all tables."""
        return sum(len(table.columns) for table in self.tables)


class TDbOracleQueryResult(FlextValueObject):
    """Oracle query result type definition."""

    rows: list[tuple[Any, ...]] = Field(default_factory=list, description="Result rows")
    columns: list[str] = Field(default_factory=list, description="Column names")
    row_count: int = Field(default=0, description="Number of rows")
    execution_time_ms: float = Field(
        default=0.0, description="Execution time in milliseconds",
    )

    def validate_domain_rules(self) -> FlextResult[None]:
        """Validate query result domain rules."""
        try:
            if self.row_count != len(self.rows):
                return FlextResult.fail("Row count mismatch")

            if self.execution_time_ms < 0:
                return FlextResult.fail("Execution time cannot be negative")

            return FlextResult.ok(None)
        except (ValueError, TypeError, AttributeError) as e:
            return FlextResult.fail(f"Query result validation failed: {e}")

    def to_dict_list(self) -> list[dict[str, Any]]:
        """Convert rows to list of dictionaries."""
        if not self.columns:
            return []

        return [dict(zip(self.columns, row, strict=False)) for row in self.rows]

    @property
    def is_empty(self) -> bool:
        """Check if result is empty."""
        return self.row_count == 0


class TDbOracleConnectionStatus(FlextValueObject):
    """Oracle connection status type definition."""

    is_connected: bool = Field(..., description="Connection status")
    host: str = Field(..., description="Database host")
    port: int = Field(..., description="Database port")
    database: str = Field(..., description="Database identifier")
    username: str = Field(..., description="Connection username")
    last_check: datetime = Field(..., description="Last check timestamp")
    error_message: str | None = Field(None, description="Error message if any")

    def validate_domain_rules(self) -> FlextResult[None]:
        """Validate connection status domain rules."""
        try:
            if not self.host or not self.host.strip():
                return FlextResult.fail(ERROR_MSG_HOST_EMPTY)

            if self.port <= 0 or self.port > MAX_PORT:
                return FlextResult.fail(ERROR_MSG_PORT_INVALID)

            if not self.username or not self.username.strip():
                return FlextResult.fail(ERROR_MSG_USERNAME_EMPTY)

            return FlextResult.ok(None)
        except (ValueError, TypeError, AttributeError) as e:
            return FlextResult.fail(f"Connection status validation failed: {e}")

    @property
    def connection_string(self) -> str:
        """Get connection string representation."""
        return f"{self.username}@{self.host}:{self.port}/{self.database}"


__all__ = [
    "TDbOracleColumn",
    "TDbOracleConnectionStatus",
    "TDbOracleQueryResult",
    "TDbOracleSchema",
    "TDbOracleTable",
]
