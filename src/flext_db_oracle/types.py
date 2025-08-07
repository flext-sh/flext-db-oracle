"""FLEXT DB Oracle Type Definitions.

This module provides comprehensive type definitions for Oracle database operations
using FLEXT Core patterns and Domain-Driven Design principles. It implements Clean
Architecture with strong type safety, validation, and domain logic encapsulation
for Oracle-specific data structures and value objects.

Key Components:
    - TDbOracleColumn: Value object for Oracle column metadata with type specifications
    - TDbOracleTable: Value object for Oracle table metadata with column relationships
    - TDbOracleSchema: Value object for Oracle schema metadata with table collections
    - TDbOracleQueryResult: Value object for Oracle query results with performance metrics
    - TDbOracleConnectionStatus: Value object for Oracle connection status information

Architecture:
    This module implements the Domain layer's value object concern, providing
    immutable, validated data structures that encapsulate Oracle database
    concepts. It follows Domain-Driven Design principles with rich domain models
    that include business logic and validation rules specific to Oracle systems.

Example:
    Working with Oracle domain types:

    >>> from flext_db_oracle.types import TDbOracleColumn, TDbOracleTable
    >>> column = TDbOracleColumn(
    ...     name="employee_id",
    ...     data_type="NUMBER",
    ...     precision=10,
    ...     position=1,
    ...     is_primary_key=True,
    ... )
    >>> validation_result = column.validate_domain_rules()
    >>> if validation_result.success:
    ...     print(f"Column type: {column.full_type_spec}")  # "NUMBER(10)"

Integration:
    - Built on flext-core FlextValueObject foundation for immutability
    - Integrates with flext-core FlextResult patterns for validation
    - Supports Oracle-specific type mapping and schema introspection
    - Compatible with Singer ecosystem type definitions and conversions
    - Provides foundation for metadata management and DDL generation

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

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

if TYPE_CHECKING:
    from datetime import datetime


def _handle_validation_error(context: str, exception: Exception) -> FlextResult[None]:
    """DRY helper: Handle validation errors with consistent formatting.

    Args:
        context: The validation context (e.g., "Column", "Table", "Schema")
        exception: The exception that occurred during validation

    Returns:
        FlextResult with failure containing formatted error message

    """
    return FlextResult.fail(f"{context} validation failed: {exception}")


def _is_empty_string(value: str | None) -> bool:
    """DRY helper: Check if string is None, empty, or whitespace-only.

    Args:
        value: String value to check

    Returns:
        True if string is empty or whitespace-only, False otherwise

    """
    return not value or not value.strip()


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
        default=False,
        description="Whether column is primary key",
    )
    is_foreign_key: bool = Field(
        default=False,
        description="Whether column is foreign key",
    )

    def validate_domain_rules(self) -> FlextResult[None]:
        """Validate column type domain rules."""
        try:
            if _is_empty_string(self.name):
                return FlextResult.fail(ERROR_MSG_COLUMN_NAME_EMPTY)

            if _is_empty_string(self.data_type):
                return FlextResult.fail(ERROR_MSG_DATA_TYPE_EMPTY)

            if self.position <= 0:
                return FlextResult.fail(ERROR_MSG_POSITION_INVALID)

            return FlextResult.ok(None)
        except (ValueError, TypeError, AttributeError) as e:
            return _handle_validation_error("Column", e)

    def validate_business_rules(self) -> FlextResult[None]:
        """Validate business rules - delegates to domain rules."""
        return self.validate_domain_rules()

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
        default_factory=list,
        description="Table columns",
    )
    row_count: int | None = Field(None, description="Estimated row count")
    size_bytes: int | None = Field(None, description="Table size in bytes")
    tablespace: str | None = Field(None, description="Tablespace name")
    created_date: datetime | None = Field(None, description="Creation date")
    comments: str | None = Field(None, description="Table comments")

    def validate_domain_rules(self) -> FlextResult[None]:
        """Validate table type domain rules.

        SOLID REFACTORING: Reduced from 6 returns to 3 using Guard Clauses pattern.
        """
        try:
            # SOLID Guard Clauses - Early exits for validation errors
            validation_error = self._get_basic_validation_error()
            if validation_error:
                return FlextResult.fail(validation_error)

            column_validation_error = self._get_column_validation_error()
            if column_validation_error:
                return FlextResult.fail(column_validation_error)

            return FlextResult.ok(None)
        except (ValueError, TypeError, AttributeError) as e:
            return _handle_validation_error("Table", e)

    def validate_business_rules(self) -> FlextResult[None]:
        """Validate business rules - delegates to domain rules."""
        return self.validate_domain_rules()

    def _get_basic_validation_error(self) -> str | None:
        """SOLID REFACTORING: Extract Method for basic validations."""
        if _is_empty_string(self.name):
            return ERROR_MSG_TABLE_NAME_EMPTY

        if _is_empty_string(self.schema_name):
            return ERROR_MSG_SCHEMA_NAME_EMPTY

        if not self.columns:
            return "Table must have at least one column"

        return None

    def _get_column_validation_error(self) -> str | None:
        """SOLID REFACTORING: Extract Method for column validations."""
        for column in self.columns:
            validation = column.validate_domain_rules()
            if validation.is_failure:
                return f"Column {column.name}: {validation.error}"
        return None

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
        default_factory=list,
        description="Schema tables",
    )
    created_date: datetime | None = Field(None, description="Schema creation date")
    default_tablespace: str | None = Field(None, description="Default tablespace")

    def validate_domain_rules(self) -> FlextResult[None]:
        """Validate schema type domain rules."""
        try:
            if _is_empty_string(self.name):
                return FlextResult.fail(ERROR_MSG_SCHEMA_NAME_EMPTY)

            # Validate tables
            for table in self.tables:
                validation = table.validate_domain_rules()
                if validation.is_failure:
                    return FlextResult.fail(f"Table {table.name}: {validation.error}")

            return FlextResult.ok(None)
        except (ValueError, TypeError, AttributeError) as e:
            return _handle_validation_error("Schema", e)

    def validate_business_rules(self) -> FlextResult[None]:
        """Validate business rules - delegates to domain rules."""
        return self.validate_domain_rules()

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

    rows: list[tuple[object, ...]] = Field(
        default_factory=list,
        description="Result rows",
    )
    columns: list[str] = Field(default_factory=list, description="Column names")
    row_count: int = Field(default=0, description="Number of rows")
    execution_time_ms: float = Field(
        default=0.0,
        description="Execution time in milliseconds",
    )

    def validate_business_rules(self) -> FlextResult[None]:
        """REAL REFACTORING: Implement abstract method from FlextValueObject."""
        return self.validate_domain_rules()

    def validate_domain_rules(self) -> FlextResult[None]:
        """Validate query result domain rules."""
        try:
            if self.row_count != len(self.rows):
                return FlextResult.fail("Row count mismatch")

            if self.execution_time_ms < 0:
                return FlextResult.fail("Execution time cannot be negative")

            return FlextResult.ok(None)
        except (ValueError, TypeError, AttributeError) as e:
            return _handle_validation_error("Query result", e)

    def to_dict_list(self) -> list[dict[str, object]]:
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
            if _is_empty_string(self.host):
                return FlextResult.fail(ERROR_MSG_HOST_EMPTY)

            if self.port <= 0 or self.port > MAX_PORT:
                return FlextResult.fail(ERROR_MSG_PORT_INVALID)

            if _is_empty_string(self.username):
                return FlextResult.fail(ERROR_MSG_USERNAME_EMPTY)

            return FlextResult.ok(None)
        except (ValueError, TypeError, AttributeError) as e:
            return _handle_validation_error("Connection status", e)

    def validate_business_rules(self) -> FlextResult[None]:
        """Validate business rules - delegates to domain rules."""
        return self.validate_domain_rules()

    @property
    def connection_string(self) -> str:
        """Get connection string representation."""
        return f"{self.username}@{self.host}:{self.port}/{self.database}"


class CreateIndexConfig(FlextValueObject):
    """Configuration for CREATE INDEX statement building."""

    index_name: str = Field(..., description="Index name")
    table_name: str = Field(..., description="Table name")
    columns: list[str] = Field(..., description="Index columns")
    schema_name: str | None = Field(None, description="Schema name")
    unique: bool = Field(default=False, description="Unique index")
    tablespace: str | None = Field(None, description="Tablespace")
    parallel: int | None = Field(None, description="Parallel degree")

    def validate_domain_rules(self) -> FlextResult[None]:
        """Validate create index configuration."""
        try:
            # Collect all validation errors
            errors = []

            if _is_empty_string(self.index_name):
                errors.append("Index name cannot be empty")

            if _is_empty_string(self.table_name):
                errors.append("Table name cannot be empty")

            if not self.columns:
                errors.append("At least one column is required")
            elif any(_is_empty_string(col) for col in self.columns):
                errors.append("Column names cannot be empty")

            if self.parallel is not None and self.parallel <= 0:
                errors.append("Parallel degree must be positive")

            if errors:
                return FlextResult.fail("; ".join(errors))

            return FlextResult.ok(None)
        except (ValueError, TypeError, AttributeError) as e:
            return _handle_validation_error("Create index config", e)

    def validate_business_rules(self) -> FlextResult[None]:
        """Validate business rules - delegates to domain rules."""
        return self.validate_domain_rules()


__all__: list[str] = [
    "CreateIndexConfig",
    "TDbOracleColumn",
    "TDbOracleConnectionStatus",
    "TDbOracleQueryResult",
    "TDbOracleSchema",
    "TDbOracleTable",
]

# Rebuild Pydantic models to resolve forward references
TDbOracleSchema.model_rebuild()
TDbOracleTable.model_rebuild()
TDbOracleColumn.model_rebuild()
