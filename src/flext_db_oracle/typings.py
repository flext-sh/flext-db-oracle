"""Oracle database types and value objects - centralized.

This module centralizes type/value object definitions for flext-db-oracle,
following the flext-core typing pattern. Prefer importing from here.
"""

from __future__ import annotations

from collections.abc import Iterator
from datetime import datetime
from typing import TypedDict

from flext_core import FlextResult, FlextValidators, FlextValueObject, get_logger
from pydantic import Field, field_validator

from flext_db_oracle.constants import MAX_PORT
from flext_db_oracle.metadata import (
    FlextDbOracleColumn as _FlextDbOracleColumn,
    FlextDbOracleSchema as _FlextDbOracleSchema,
    FlextDbOracleTable as _FlextDbOracleTable,
)

# Constants for business logic
SESSION_UTILIZATION_THRESHOLD = 90.0

logger = get_logger(__name__)

# =============================================================================
# BACKWARD COMPATIBILITY ALIASES - Eliminate duplication
# =============================================================================

# Create aliases for existing TDbOracle* classes to maintain compatibility
FlextDbOracleColumn = _FlextDbOracleColumn
FlextDbOracleTable = _FlextDbOracleTable
FlextDbOracleSchema = _FlextDbOracleSchema

FlextDbOracleQueryResult = None  # will be assigned after class definition
FlextDbOracleConnectionStatus = None  # will be assigned after class definition


# =============================================================================
# UNIQUE VALUE OBJECTS - Not duplicated in metadata.py
# =============================================================================


class TDbOracleQueryResult(FlextValueObject):
    """Oracle query result value object."""

    columns: list[str] = Field(..., description="Column names")
    rows: list[tuple[object, ...]] = Field(..., description="Result rows")
    row_count: int = Field(default=0, description="Number of rows")
    execution_time_ms: float = Field(default=0.0, description="Execution time")
    query_hash: str | None = Field(None, description="Query hash for caching")

    @field_validator("row_count")
    @classmethod
    def validate_row_count(cls, v: int) -> int:
        """Validate row count is non-negative."""
        if v < 0:
            msg = "Row count cannot be negative"
            raise ValueError(msg)
        return v

    @field_validator("execution_time_ms")
    @classmethod
    def validate_execution_time(cls, v: float) -> float:
        """Validate execution time is non-negative."""
        if v < 0:
            msg = "Execution time cannot be negative"
            raise ValueError(msg)
        return v

    def validate_business_rules(self) -> FlextResult[None]:
        """Validate query result business rules.

        Note: Basic field validations are now handled by @field_validator decorators.
        This method performs cross-field validation and additional business rules.
        """
        # Cross-field validation: row count must match actual rows
        if len(self.rows) != self.row_count:
            return FlextResult[None].fail("Row count mismatch with actual rows")
        return FlextResult[None].ok(None)

    # Backward compatibility alias expected by some tests
    def validate_domain_rules(self) -> FlextResult[None]:  # pragma: no cover - alias
        return self.validate_business_rules()

    # Backward compatibility helpers expected by tests
    def to_dict_list(self) -> list[dict[str, object]]:
        """Convert rows to list of dicts using columns as keys."""
        if not self.columns:
            return [
                {str(index): value for index, value in enumerate(row)}
                for row in self.rows
            ]
        return [
            {
                str(self.columns[i]): row[i] if i < len(row) else None
                for i in range(len(self.columns))
            }
            for row in self.rows
        ]

    def __iter__(self) -> Iterator[tuple[object, ...]]:
        """Iterate over rows to satisfy tests that iterate result.data."""
        return iter(self.rows)

    @property
    def is_empty(self) -> bool:
        """Check if result is empty."""
        return self.row_count == 0

    def __len__(self) -> int:
        """Support len() to satisfy tests that call len(result.data)."""
        return int(self.row_count)

    def get_column_values(self, column_name: str) -> FlextResult[list[object]]:
        """Get values for a specific column."""
        if column_name not in self.columns:
            return FlextResult[list[object]].fail(f"Column '{column_name}' not found")

        column_index = self.columns.index(column_name)
        values = [
            row[column_index] if column_index < len(row) else None for row in self.rows
        ]

        return FlextResult[list[object]].ok(values)


class TDbOracleConnectionStatus(FlextValueObject):
    """Oracle connection status value object."""

    is_connected: bool = Field(..., description="Connection status")
    host: str = Field(..., description="Oracle host")
    port: int = Field(..., description="Oracle port")
    service_name: str = Field(default="", description="Oracle service name")
    username: str = Field(..., description="Connection username")
    connection_time_ms: float | None = Field(None, description="Connection time")
    last_error: str | None = Field(None, description="Last connection error")
    # Legacy/compatibility fields expected by tests
    last_check: datetime | None = Field(None, description="Last check timestamp")
    database: str | None = Field(None, description="Database/service name")
    active_sessions: int = Field(default=0, description="Active sessions")
    max_sessions: int = Field(default=100, description="Max sessions")

    @field_validator("host")
    @classmethod
    def validate_host(cls, v: str) -> str:
        """Validate host is non-empty."""
        if not FlextValidators.is_non_empty_string(v):
            msg = "Host cannot be empty"
            raise ValueError(msg)
        return v

    @field_validator("port")
    @classmethod
    def validate_port(cls, v: int) -> int:
        """Validate port is within valid range."""
        if v <= 0 or v > MAX_PORT:
            msg = f"Port must be between 1 and {MAX_PORT}"
            raise ValueError(msg)
        return v

    @field_validator("service_name")
    @classmethod
    def validate_service_name(cls, v: str) -> str:
        """Validate service name is non-empty."""
        if not FlextValidators.is_non_empty_string(v):
            msg = "Service name cannot be empty"
            raise ValueError(msg)
        return v

    @field_validator("username")
    @classmethod
    def validate_username(cls, v: str) -> str:
        """Validate username is non-empty."""
        if not FlextValidators.is_non_empty_string(v):
            msg = "Username cannot be empty"
            raise ValueError(msg)
        return v

    @field_validator("active_sessions")
    @classmethod
    def validate_active_sessions(cls, v: int) -> int:
        """Validate active sessions is non-negative."""
        if v < 0:
            msg = "Active sessions cannot be negative"
            raise ValueError(msg)
        return v

    @field_validator("max_sessions")
    @classmethod
    def validate_max_sessions(cls, v: int) -> int:
        """Validate max sessions is positive."""
        if v <= 0:
            msg = "Max sessions must be positive"
            raise ValueError(msg)
        return v

    def validate_business_rules(self) -> FlextResult[None]:
        """Validate connection status business rules.

        Note: Basic field validations are now handled by @field_validator decorators.
        This method performs cross-field validation and additional business rules.
        """
        # Cross-field validation: active sessions cannot exceed max sessions
        if self.active_sessions > self.max_sessions:
            return FlextResult[None].fail("Active sessions cannot exceed max sessions")
        return FlextResult[None].ok(None)

    # Backward compatibility alias expected by some tests
    def validate_domain_rules(self) -> FlextResult[None]:  # pragma: no cover - alias
        return self.validate_business_rules()

    def to_dict(
        self,
        *,
        by_alias: bool = True,  # noqa: ARG002
        exclude_none: bool = True,  # noqa: ARG002
    ) -> dict[str, object]:
        """Convert connection status to dictionary for convenience.

        Provides a helper expected by some tests to access connection data.

        Args:
            by_alias: Use field aliases in output
            exclude_none: Exclude None values from output

        """
        return {
            "is_connected": self.is_connected,
            "host": self.host,
            "port": self.port,
            "service_name": self.service_name,
            "username": self.username,
            "connection_time_ms": self.connection_time_ms,
            "last_error": self.last_error,
            "active_sessions": self.active_sessions,
            "max_sessions": self.max_sessions,
            "session_utilization_percent": self.session_utilization_percent,
            "is_healthy": self.is_healthy(),
        }

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
            and self.session_utilization_percent < SESSION_UTILIZATION_THRESHOLD
        )


class TDbOracleColumn(_FlextDbOracleColumn):
    """Typed shim that accepts legacy kwargs and maps them appropriately.

    Enables tests to pass legacy constructor arguments while preserving
    strong typing for the underlying model.
    """

    def __init__(self, **kwargs: object) -> None:
        mapped = dict(kwargs)
        # Legacy aliases
        if "precision" in mapped and "data_precision" not in mapped:
            mapped["data_precision"] = mapped.pop("precision")
        if "scale" in mapped and "data_scale" not in mapped:
            mapped["data_scale"] = mapped.pop("scale")
        if "position" in mapped and "column_id" not in mapped:
            mapped["column_id"] = mapped.pop("position")
        if "max_length" in mapped and "data_length" not in mapped:
            mapped["data_length"] = mapped.pop("max_length")
        super().__init__(**mapped)


class TDbOracleTable(_FlextDbOracleTable):
    """Typed shim for table that forwards kwargs to base model."""

    def __init__(self, **kwargs: object) -> None:
        # Accept columns as either list of dicts or TDbOracleColumn/_FlextDbOracleColumn
        mapped = dict(kwargs)
        cols = mapped.get("columns")
        if isinstance(cols, list):
            normalized_cols: list[_FlextDbOracleColumn] = []
            for c in cols:
                if isinstance(c, _FlextDbOracleColumn):
                    normalized_cols.append(c)
                elif isinstance(c, dict):
                    normalized_cols.append(TDbOracleColumn(**c))
            mapped["columns"] = normalized_cols
        super().__init__(**mapped)


class TDbOracleSchema(_FlextDbOracleSchema):
    """Typed shim for schema that forwards kwargs to base model."""

    def __init__(self, **kwargs: object) -> None:
        mapped = dict(kwargs)
        tables = mapped.get("tables")
        if isinstance(tables, list):
            normalized_tables: list[_FlextDbOracleTable] = []
            for t in tables:
                if isinstance(t, _FlextDbOracleTable):
                    normalized_tables.append(t)
                elif isinstance(t, dict):
                    normalized_tables.append(TDbOracleTable(**t))
            mapped["tables"] = normalized_tables
        super().__init__(**mapped)


# Assign public aliases after classes are defined
FlextDbOracleQueryResult = TDbOracleQueryResult
FlextDbOracleConnectionStatus = TDbOracleConnectionStatus


class OracleColumnInfo(TypedDict, total=False):
    column_name: str
    data_type: str
    nullable: bool
    data_length: int | None
    data_precision: int | None
    data_scale: int | None
    column_id: int
    default_value: str | None
    comments: str | None


__all__ = [
    "FlextDbOracleColumn",
    "FlextDbOracleConnectionStatus",
    "FlextDbOracleQueryResult",
    "FlextDbOracleSchema",
    "FlextDbOracleTable",
    "TDbOracleColumn",
    "TDbOracleConnectionStatus",
    "TDbOracleQueryResult",
    "TDbOracleSchema",
    "TDbOracleTable",
]
