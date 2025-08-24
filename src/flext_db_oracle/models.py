"""Oracle database Pydantic models following flext-core patterns.

This module contains all Pydantic models used throughout the flext-db-oracle library,
following the flext-core model patterns and Clean Architecture principles.

Models are organized by domain:
- Configuration models (connection, pool, query settings)
- Domain models (table, column, schema metadata)
- Result models (query results, connection status)

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from datetime import datetime
from typing import ClassVar

from flext_core import FlextFactory, FlextModel, FlextResult, FlextValidation
from pydantic import Field, field_validator

from flext_db_oracle.constants import FlextDbOracleConstants

__all__ = [
    "FlextDbOracleColumn",
    "FlextDbOracleConnectionStatus",
    "FlextDbOracleModels",
    "FlextDbOracleQueryResult",
    "FlextDbOracleSchema",
    "FlextDbOracleTable",
]

# =============================================================================
# FLEXT MODELS - Single Class Pattern (SOLID + PEP8)
# =============================================================================


class FlextDbOracleModels(FlextFactory):
    """Oracle database models following single-class FLEXT pattern.

    Inherits from FlextFactory to leverage FLEXT Core model creation patterns.
    Consolidates all Oracle model functionality into a single class with internal methods
    following SOLID principles, PEP8, Python 3.13+, and FLEXT structural patterns.
    """

    @staticmethod
    def create_column(
        column_name: str,
        data_type: str,
        *,
        nullable: bool = True,
        data_length: int | None = None,
        data_precision: int | None = None,
        data_scale: int | None = None,
        column_id: int = 1,
        default_value: str | None = None,
        comments: str | None = None,
    ) -> FlextDbOracleColumn:
        """Create Oracle database column model."""
        return FlextDbOracleColumn(
            column_name=column_name,
            data_type=data_type,
            nullable=nullable,
            data_length=data_length,
            data_precision=data_precision,
            data_scale=data_scale,
            column_id=column_id,
            default_value=default_value,
            comments=comments,
        )

    @staticmethod
    def create_table(
        table_name: str,
        schema_name: str,
        columns: list[FlextDbOracleColumn] | None = None,
        table_comment: str | None = None,
        tablespace_name: str | None = None,
    ) -> FlextDbOracleTable:
        """Create Oracle database table model."""
        return FlextDbOracleTable(
            table_name=table_name,
            schema_name=schema_name,
            columns=columns or [],
            table_comment=table_comment,
            tablespace_name=tablespace_name,
        )

    @staticmethod
    def create_schema(
        schema_name: str,
        tables: list[FlextDbOracleTable] | None = None,
        default_tablespace: str | None = None,
        temporary_tablespace: str | None = None,
    ) -> FlextDbOracleSchema:
        """Create Oracle database schema model."""
        return FlextDbOracleSchema(
            schema_name=schema_name,
            tables=tables or [],
            default_tablespace=default_tablespace,
            temporary_tablespace=temporary_tablespace,
        )

    @staticmethod
    def create_query_result(
        columns: list[str] | None = None,
        rows: list[tuple[object, ...]] | None = None,
        row_count: int = 0,
        execution_time_ms: float = 0.0,
        query_hash: str | None = None,
    ) -> FlextDbOracleQueryResult:
        """Create Oracle query result model."""
        return FlextDbOracleQueryResult(
            columns=columns or [],
            rows=rows or [],
            row_count=row_count,
            execution_time_ms=execution_time_ms,
            query_hash=query_hash,
        )

    @staticmethod
    def create_connection_status(
        *,
        is_connected: bool,
        host: str,
        port: int,
        service_name: str = "",
        username: str = "unknown",
        connection_time_ms: float | None = None,
        last_error: str | None = None,
        last_check: datetime | None = None,
        active_sessions: int = 0,
        max_sessions: int = 100,
    ) -> FlextDbOracleConnectionStatus:
        """Create Oracle connection status model."""
        return FlextDbOracleConnectionStatus(
            is_connected=is_connected,
            host=host,
            port=port,
            service_name=service_name,
            username=username,
            connection_time_ms=connection_time_ms,
            last_error=last_error,
            last_check=last_check,
            active_sessions=active_sessions,
            max_sessions=max_sessions,
        )


# =============================================================================
# DOMAIN MODELS - Database Metadata (Backward Compatibility)
# =============================================================================


class FlextDbOracleColumn(FlextModel):
    """Oracle database column model with complete metadata."""

    column_name: str = Field(..., description="Column name")
    data_type: str = Field(..., description="Oracle data type")
    nullable: bool = Field(default=True, description="Column nullable flag")
    data_length: int | None = Field(None, description="Data length for character types")
    data_precision: int | None = Field(None, description="Numeric precision")
    data_scale: int | None = Field(None, description="Numeric scale")
    column_id: int = Field(..., description="Column position/ID")
    default_value: str | None = Field(None, description="Default value")
    comments: str | None = Field(None, description="Column comments")

    @field_validator("column_name")
    @classmethod
    def validate_column_name(cls, v: str) -> str:
        """Validate column name."""
        if not FlextValidation.Validators.is_non_empty_string(v):
            msg = FlextDbOracleConstants.ErrorMessages.COLUMN_NAME_EMPTY
            raise ValueError(msg)
        if len(v) > FlextDbOracleConstants.OracleValidation.MAX_COLUMN_NAME_LENGTH:
            msg = f"Column name exceeds maximum length of {FlextDbOracleConstants.OracleValidation.MAX_COLUMN_NAME_LENGTH}"
            raise ValueError(msg)
        return v.upper()

    @field_validator("data_type")
    @classmethod
    def validate_data_type(cls, v: str) -> str:
        """Validate data type."""
        if not FlextValidation.Validators.is_non_empty_string(v):
            msg = FlextDbOracleConstants.ErrorMessages.DATA_TYPE_EMPTY
            raise ValueError(msg)
        return v.upper()

    @field_validator("column_id")
    @classmethod
    def validate_column_id(cls, v: int) -> int:
        """Validate column ID."""
        if v <= 0:
            msg = FlextDbOracleConstants.ErrorMessages.COLUMN_ID_INVALID
            raise ValueError(msg)
        return v

    @field_validator("data_length")
    @classmethod
    def validate_data_length(cls, v: int | None) -> int | None:
        """Validate data length."""
        if v is not None and v <= 0:
            msg = "Data length must be positive"
            raise ValueError(msg)
        return v

    @field_validator("data_precision")
    @classmethod
    def validate_data_precision(cls, v: int | None) -> int | None:
        """Validate data precision."""
        if v is not None and v <= 0:
            msg = "Data precision must be positive"
            raise ValueError(msg)
        return v

    def validate_business_rules(self) -> FlextResult[None]:
        """Validate column business rules."""
        # Cross-field validations
        if (
            self.data_type in {"VARCHAR2", "CHAR", "NVARCHAR2", "NCHAR"}
            and self.data_length is None
        ):
            return FlextResult[None].fail(f"Data length required for {self.data_type}")

        if (
            self.data_type in {"NUMBER", "FLOAT"}
            and self.data_precision is not None
            and self.data_scale is not None
            and self.data_scale > self.data_precision
        ):
            return FlextResult[None].fail("Scale cannot exceed precision")

        return FlextResult[None].ok(None)

    @property
    def sql_definition(self) -> str:
        """Generate SQL column definition."""
        parts = [self.column_name, self.data_type]

        if self.data_length and self.data_type in {
            "VARCHAR2",
            "CHAR",
            "NVARCHAR2",
            "NCHAR",
        }:
            parts[1] = f"{self.data_type}({self.data_length})"
        elif self.data_precision and self.data_type == "NUMBER":
            if self.data_scale:
                parts[1] = f"NUMBER({self.data_precision},{self.data_scale})"
            else:
                parts[1] = f"NUMBER({self.data_precision})"

        if not self.nullable:
            parts.append("NOT NULL")

        if self.default_value:
            parts.append(f"DEFAULT {self.default_value}")

        return " ".join(parts)


class FlextDbOracleTable(FlextModel):
    """Oracle database table model with columns."""

    table_name: str = Field(..., description="Table name")
    schema_name: str = Field(..., description="Schema/owner name")
    columns: list[FlextDbOracleColumn] = Field(
        default_factory=list, description="Table columns"
    )
    table_comment: str | None = Field(None, description="Table comment")
    tablespace_name: str | None = Field(None, description="Tablespace name")

    @field_validator("table_name")
    @classmethod
    def validate_table_name(cls, v: str) -> str:
        """Validate table name."""
        if not FlextValidation.Validators.is_non_empty_string(v):
            msg = FlextDbOracleConstants.ErrorMessages.TABLE_NAME_EMPTY
            raise ValueError(msg)
        if len(v) > FlextDbOracleConstants.OracleValidation.MAX_TABLE_NAME_LENGTH:
            msg = f"Table name exceeds maximum length of {FlextDbOracleConstants.OracleValidation.MAX_TABLE_NAME_LENGTH}"
            raise ValueError(msg)
        return v.upper()

    @field_validator("schema_name")
    @classmethod
    def validate_schema_name(cls, v: str) -> str:
        """Validate schema name."""
        if not FlextValidation.Validators.is_non_empty_string(v):
            msg = FlextDbOracleConstants.ErrorMessages.SCHEMA_NAME_EMPTY
            raise ValueError(msg)
        if len(v) > FlextDbOracleConstants.OracleValidation.MAX_SCHEMA_NAME_LENGTH:
            msg = f"Schema name exceeds maximum length of {FlextDbOracleConstants.OracleValidation.MAX_SCHEMA_NAME_LENGTH}"
            raise ValueError(msg)
        return v.upper()

    def validate_business_rules(self) -> FlextResult[None]:
        """Validate table business rules."""
        # Validate all columns
        for column in self.columns:
            result = column.validate_business_rules()
            # Modern FlextResult pattern: For FlextResult[None], check error instead of unwrap_or
            if result.error:
                return FlextResult[None].fail(
                    f"Column {column.column_name}: {result.error or 'Column validation failed'}"
                )

        # Check for duplicate column names
        column_names = [col.column_name for col in self.columns]
        if len(column_names) != len(set(column_names)):
            return FlextResult[None].fail("Duplicate column names found")

        return FlextResult[None].ok(None)

    @property
    def fully_qualified_name(self) -> str:
        """Get fully qualified table name."""
        return f"{self.schema_name}.{self.table_name}"

    def get_column(self, column_name: str) -> FlextDbOracleColumn | None:
        """Get column by name."""
        column_upper = column_name.upper()
        return next(
            (col for col in self.columns if col.column_name == column_upper), None
        )

    @property
    def primary_key_columns(self) -> list[FlextDbOracleColumn]:
        """Get primary key columns (placeholder - would need constraint info)."""
        # This would require constraint metadata which we don't have in this model
        return []


class FlextDbOracleSchema(FlextModel):
    """Oracle database schema model with tables."""

    schema_name: str = Field(..., description="Schema name")
    tables: list[FlextDbOracleTable] = Field(
        default_factory=list, description="Schema tables"
    )
    default_tablespace: str | None = Field(None, description="Default tablespace")
    temporary_tablespace: str | None = Field(None, description="Temporary tablespace")

    @field_validator("schema_name")
    @classmethod
    def validate_schema_name(cls, v: str) -> str:
        """Validate schema name."""
        if not FlextValidation.Validators.is_non_empty_string(v):
            msg = FlextDbOracleConstants.ErrorMessages.SCHEMA_NAME_EMPTY
            raise ValueError(msg)
        if len(v) > FlextDbOracleConstants.OracleValidation.MAX_SCHEMA_NAME_LENGTH:
            msg = f"Schema name exceeds maximum length of {FlextDbOracleConstants.OracleValidation.MAX_SCHEMA_NAME_LENGTH}"
            raise ValueError(msg)
        return v.upper()

    def validate_business_rules(self) -> FlextResult[None]:
        """Validate schema business rules."""
        # Validate all tables
        for table in self.tables:
            result = table.validate_business_rules()
            # Modern FlextResult pattern: For FlextResult[None], check error instead of unwrap_or
            if result.error:
                return FlextResult[None].fail(
                    f"Table {table.table_name}: {result.error or 'Table validation failed'}"
                )

        # Check for duplicate table names
        table_names = [table.table_name for table in self.tables]
        if len(table_names) != len(set(table_names)):
            return FlextResult[None].fail("Duplicate table names found")

        return FlextResult[None].ok(None)

    def get_table(self, table_name: str) -> FlextDbOracleTable | None:
        """Get table by name."""
        table_upper = table_name.upper()
        return next(
            (table for table in self.tables if table.table_name == table_upper), None
        )

    @property
    def table_count(self) -> int:
        """Get number of tables in schema."""
        return len(self.tables)


# =============================================================================
# RESULT MODELS - Query and Operation Results
# =============================================================================


class FlextDbOracleQueryResult(FlextModel):
    """Oracle query result model with metadata."""

    columns: list[str] = Field(default_factory=list, description="Column names")
    rows: list[tuple[object, ...]] = Field(
        default_factory=list, description="Result rows"
    )
    row_count: int = Field(default=0, description="Number of rows")
    execution_time_ms: float = Field(
        default=0.0, description="Execution time in milliseconds"
    )
    query_hash: str | None = Field(None, description="Query hash for caching")

    @field_validator("row_count")
    @classmethod
    def validate_row_count(cls, v: int) -> int:
        """Validate row count."""
        if v < 0:
            msg = "Row count cannot be negative"
            raise ValueError(msg)
        return v

    @field_validator("execution_time_ms")
    @classmethod
    def validate_execution_time(cls, v: float) -> float:
        """Validate execution time."""
        if v < 0:
            msg = "Execution time cannot be negative"
            raise ValueError(msg)
        return v

    def validate_business_rules(self) -> FlextResult[None]:
        """Validate query result business rules."""
        # Cross-field validation: row count must match actual rows
        if len(self.rows) != self.row_count:
            return FlextResult[None].fail("Row count mismatch with actual rows")

        # Validate column count consistency
        if self.rows and self.columns:
            for i, row in enumerate(self.rows):
                if len(row) != len(self.columns):
                    return FlextResult[None].fail(f"Row {i} column count mismatch")

        return FlextResult[None].ok(None)

    @property
    def is_empty(self) -> bool:
        """Check if result is empty."""
        return self.row_count == 0

    def to_dict_list(self) -> list[dict[str, object]]:
        """Convert rows to list of dicts using columns as keys."""
        if not self.columns:
            return [
                {str(index): value for index, value in enumerate(row)}
                for row in self.rows
            ]

        result = []
        for row in self.rows:
            row_dict = {}
            for i, column in enumerate(self.columns):
                row_dict[column] = row[i] if i < len(row) else None
            result.append(row_dict)

        return result

    def get_column_values(self, column_name: str) -> FlextResult[list[object]]:
        """Get values for a specific column."""
        if column_name not in self.columns:
            return FlextResult[list[object]].fail(f"Column '{column_name}' not found")

        column_index = self.columns.index(column_name)
        values = [
            row[column_index] if column_index < len(row) else None for row in self.rows
        ]

        return FlextResult[list[object]].ok(values)


class FlextDbOracleConnectionStatus(FlextModel):
    """Oracle connection status model with health metrics."""

    is_connected: bool = Field(..., description="Connection status")
    host: str = Field(..., description="Oracle host")
    port: int = Field(..., description="Oracle port")
    service_name: str = Field(default="", description="Oracle service name")
    username: str = Field(..., description="Connection username")
    connection_time_ms: float | None = Field(
        None, description="Connection time in milliseconds"
    )
    last_error: str | None = Field(None, description="Last connection error")
    last_check: datetime | None = Field(None, description="Last health check timestamp")
    active_sessions: int = Field(default=0, description="Active sessions")
    max_sessions: int = Field(default=100, description="Maximum sessions")

    # Validation constants
    SESSION_UTILIZATION_THRESHOLD: ClassVar[float] = 90.0

    @field_validator("host")
    @classmethod
    def validate_host(cls, v: str) -> str:
        """Validate host."""
        if not FlextValidation.Validators.is_non_empty_string(v):
            msg = FlextDbOracleConstants.ErrorMessages.HOST_EMPTY
            raise ValueError(msg)
        return v

    @field_validator("port")
    @classmethod
    def validate_port(cls, v: int) -> int:
        """Validate port."""
        if v <= 0 or v > FlextDbOracleConstants.Connection.MAX_PORT:
            msg = f"Port must be between 1 and {FlextDbOracleConstants.Connection.MAX_PORT}"
            raise ValueError(msg)
        return v

    @field_validator("service_name")
    @classmethod
    def validate_service_name(cls, v: str) -> str:
        """Validate service name."""
        if not FlextValidation.Validators.is_non_empty_string(v):
            msg = "Service name cannot be empty"
            raise ValueError(msg)
        return v

    @field_validator("username")
    @classmethod
    def validate_username(cls, v: str) -> str:
        """Validate username."""
        if not FlextValidation.Validators.is_non_empty_string(v):
            msg = FlextDbOracleConstants.ErrorMessages.USERNAME_EMPTY
            raise ValueError(msg)
        return v

    @field_validator("active_sessions")
    @classmethod
    def validate_active_sessions(cls, v: int) -> int:
        """Validate active sessions."""
        if v < 0:
            msg = "Active sessions cannot be negative"
            raise ValueError(msg)
        return v

    @field_validator("max_sessions")
    @classmethod
    def validate_max_sessions(cls, v: int) -> int:
        """Validate max sessions."""
        if v <= 0:
            msg = "Max sessions must be positive"
            raise ValueError(msg)
        return v

    def validate_business_rules(self) -> FlextResult[None]:
        """Validate connection status business rules."""
        # Cross-field validation: active sessions cannot exceed max sessions
        if self.active_sessions > self.max_sessions:
            return FlextResult[None].fail("Active sessions cannot exceed max sessions")

        return FlextResult[None].ok(None)

    @property
    def connection_string(self) -> str:
        """Get connection string without password."""
        return f"{self.username}@{self.host}:{self.port}/{self.service_name}"

    @property
    def session_utilization_percent(self) -> float:
        """Get session utilization as percentage."""
        if self.max_sessions == 0:
            return 0.0
        return (self.active_sessions / self.max_sessions) * 100.0

    def is_healthy(self) -> bool:
        """Check if connection is healthy."""
        return (
            self.is_connected
            and self.last_error is None
            and self.session_utilization_percent < self.SESSION_UTILIZATION_THRESHOLD
        )
