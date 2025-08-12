"""Oracle database types and value objects - centralized.

This module centralizes type/value object definitions for flext-db-oracle,
following the flext-core typing pattern. Prefer importing from here.
"""
from __future__ import annotations

from flext_core import FlextResult, FlextValueObject, get_logger
from pydantic import Field

from .constants import MAX_PORT
from .metadata import (
    FlextDbOracleColumn,
    FlextDbOracleSchema,
    FlextDbOracleTable,
)

# Constants for business logic
SESSION_UTILIZATION_THRESHOLD = 90.0

logger = get_logger(__name__)

# =============================================================================
# BACKWARD COMPATIBILITY ALIASES - Eliminate duplication
# =============================================================================

# Create aliases for existing TDbOracle* classes to maintain compatibility
TDbOracleColumn = FlextDbOracleColumn
TDbOracleTable = FlextDbOracleTable
TDbOracleSchema = FlextDbOracleSchema

# =============================================================================
# UNIQUE VALUE OBJECTS - Not duplicated in metadata.py
# =============================================================================


class CreateIndexConfig(FlextValueObject):
    """Configuration for CREATE INDEX statement building."""

    index_name: str = Field(..., description="Index name")
    table_name: str = Field(..., description="Table name")
    columns: list[str] = Field(..., description="Index columns")
    schema_name: str | None = Field(None, description="Schema name")
    unique: bool = Field(default=False, description="Unique index")
    tablespace: str | None = Field(None, description="Tablespace")
    parallel: int | None = Field(None, description="Parallel degree")

    def validate_business_rules(self) -> FlextResult[None]:
        """Validate create index configuration."""
        try:
            # Collect all validation errors
            errors = []

            if not self.index_name or not self.index_name.strip():
                errors.append("Index name cannot be empty")

            if not self.table_name or not self.table_name.strip():
                errors.append("Table name cannot be empty")

            if self.columns:
                if any(not col or not col.strip() for col in self.columns):
                    errors.append("Column names cannot be empty")
            else:
                errors.append("At least one column is required")

            if self.parallel is not None and self.parallel <= 0:
                errors.append("Parallel degree must be positive")

            if errors:
                return FlextResult.fail("; ".join(errors))

            return FlextResult.ok(None)
        except (ValueError, TypeError, AttributeError) as e:
            return FlextResult.fail(f"Create index config validation failed: {e}")


class TDbOracleQueryResult(FlextValueObject):
    """Oracle query result value object."""

    columns: list[str] = Field(..., description="Column names")
    rows: list[list[object]] = Field(..., description="Result rows")
    row_count: int = Field(default=0, description="Number of rows")
    execution_time_ms: float = Field(default=0.0, description="Execution time")
    query_hash: str | None = Field(None, description="Query hash for caching")

    def validate_business_rules(self) -> FlextResult[None]:
        """Validate query result business rules."""
        if self.row_count < 0:
            return FlextResult.fail("Row count cannot be negative")

        if self.execution_time_ms < 0:
            return FlextResult.fail("Execution time cannot be negative")

        if len(self.rows) != self.row_count:
            return FlextResult.fail("Row count mismatch with actual rows")

        return FlextResult.ok(None)

    @property
    def is_empty(self) -> bool:
        """Check if result is empty."""
        return self.row_count == 0

    def get_column_values(self, column_name: str) -> FlextResult[list[object]]:
        """Get values for a specific column."""
        if column_name not in self.columns:
            return FlextResult.fail(f"Column '{column_name}' not found")

        column_index = self.columns.index(column_name)
        values = [
            row[column_index] if column_index < len(row) else None for row in self.rows
        ]

        return FlextResult.ok(values)


class TDbOracleConnectionStatus(FlextValueObject):
    """Oracle connection status value object."""

    is_connected: bool = Field(..., description="Connection status")
    host: str = Field(..., description="Oracle host")
    port: int = Field(..., description="Oracle port")
    service_name: str = Field(..., description="Oracle service name")
    username: str = Field(..., description="Connection username")
    connection_time_ms: float | None = Field(None, description="Connection time")
    last_error: str | None = Field(None, description="Last connection error")
    active_sessions: int = Field(default=0, description="Active sessions")
    max_sessions: int = Field(default=100, description="Max sessions")

    def validate_business_rules(self) -> FlextResult[None]:
        """Validate connection status business rules."""
        if self.port <= 0 or self.port > MAX_PORT:
            return FlextResult.fail(f"Port must be between 1 and {MAX_PORT}")

        if self.active_sessions < 0:
            return FlextResult.fail("Active sessions cannot be negative")

        if self.max_sessions <= 0:
            return FlextResult.fail("Max sessions must be positive")

        if self.active_sessions > self.max_sessions:
            return FlextResult.fail("Active sessions cannot exceed max sessions")

        return FlextResult.ok(None)

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


__all__ = [
    "CreateIndexConfig",
    "TDbOracleColumn",
    "TDbOracleConnectionStatus",
    "TDbOracleQueryResult",
    "TDbOracleSchema",
    "TDbOracleTable",
]
