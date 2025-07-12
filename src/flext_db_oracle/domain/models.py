"""Oracle Database Domain Models.

Following flext-core DDD patterns for Oracle-specific entities and value objects.
All models extend flext-core base classes for consistency.
"""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Any
from uuid import uuid4

from pydantic import Field, field_validator

if TYPE_CHECKING:
    from pydantic import ValidationInfo

from flext_core import (
    DomainEntity,
    DomainValueObject,
    EntityId,
)


class OracleConnectionInfo(DomainValueObject):
    """Oracle database connection configuration."""

    host: str = Field(..., description="Database host")
    port: int = Field(1521, ge=1, le=65535, description="Database port")
    service_name: str | None = Field(None, description="Oracle service name")
    sid: str | None = Field(None, description="Oracle SID")
    username: str = Field(..., description="Database username")
    password: str = Field(..., description="Database password")

    @field_validator("service_name", "sid")
    @classmethod
    def validate_service_or_sid(cls, v: str | None, info: ValidationInfo) -> str | None:
        """At least one of service_name or sid must be provided."""
        if (
            info.data
            and not v
            and not info.data.get("service_name")
            and not info.data.get("sid")
        ):
            msg = "Either service_name or sid must be provided"
            raise ValueError(msg)
        return v

    @property
    def connection_string(self) -> str:
        """Generate Oracle connection string."""
        service = self.service_name or self.sid
        return f"oracle://{self.username}:***@{self.host}:{self.port}/{service}"


class OracleColumnInfo(DomainValueObject):
    """Oracle table column metadata."""

    name: str = Field(..., description="Column name")
    data_type: str = Field(..., description="Oracle data type")
    nullable: bool = Field(default=True, description="Whether column allows NULL")
    default_value: str | None = Field(None, description="Default value")
    max_length: int | None = Field(None, description="Maximum character length")
    precision: int | None = Field(None, description="Numeric precision")
    scale: int | None = Field(None, description="Numeric scale")
    is_primary_key: bool = Field(
        default=False, description="Whether column is primary key",
    )
    is_foreign_key: bool = Field(
        default=False, description="Whether column is foreign key",
    )
    comments: str | None = Field(None, description="Column comments")


class OracleTableMetadata(DomainEntity):
    """Oracle table metadata entity."""

    id: EntityId = Field(default_factory=uuid4)
    schema_name: str = Field(..., description="Schema name")
    table_name: str = Field(..., description="Table name")
    columns: list[OracleColumnInfo] = Field(
        default_factory=list, description="Table columns",
    )
    row_count: int | None = Field(None, ge=0, description="Approximate row count")
    tablespace: str | None = Field(None, description="Tablespace name")
    comments: str | None = Field(None, description="Table comments")
    created_date: datetime | None = Field(None, description="Creation timestamp")

    @property
    def full_name(self) -> str:
        """Get fully qualified table name."""
        return f"{self.schema_name}.{self.table_name}"

    @property
    def primary_key_columns(self) -> list[str]:
        """Get list of primary key column names."""
        return [col.name for col in self.columns if col.is_primary_key]


class OracleSchemaInfo(DomainValueObject):
    """Oracle schema information."""

    name: str = Field(..., description="Schema name")
    tables: list[OracleTableMetadata] = Field(
        default_factory=list, description="Schema tables",
    )
    table_count: int = Field(0, ge=0, description="Number of tables")
    created_date: datetime | None = Field(None, description="Schema creation date")

    @property
    def table_names(self) -> list[str]:
        """Get list of table names in schema."""
        return [table.table_name for table in self.tables]


class OracleQueryResult(DomainValueObject):
    """Result of Oracle query execution."""

    rows: list[tuple[Any, ...]] = Field(
        default_factory=list, description="Query result rows as tuples",
    )
    row_count: int = Field(0, ge=0, description="Number of rows returned")
    columns: list[str] = Field(default_factory=list, description="Column names")
    execution_time_ms: float = Field(
        0.0, ge=0, description="Query execution time in milliseconds",
    )

    @property
    def is_empty(self) -> bool:
        """Check if query returned no rows."""
        return self.row_count == 0

    def get_column_values(self, column_index: int) -> list[Any]:
        """Get all values for a specific column by index."""
        return [
            row[column_index] if column_index < len(row) else None for row in self.rows
        ]


class OracleConnectionStatus(DomainValueObject):
    """Oracle connection health status."""

    is_connected: bool = Field(..., description="Connection status")
    host: str = Field(..., description="Database host")
    port: int = Field(..., description="Database port")
    database: str = Field(..., description="Database name/service")
    username: str = Field(..., description="Connected username")
    last_check: datetime = Field(
        default_factory=datetime.now, description="Last status check",
    )
    error_message: str | None = Field(
        None, description="Error message if connection failed",
    )

    @property
    def connection_info(self) -> str:
        """Get formatted connection information."""
        return f"{self.username}@{self.host}:{self.port}/{self.database}"
