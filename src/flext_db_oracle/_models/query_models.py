"""Oracle Database query and row models for the DbOracle namespace.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import ClassVar

from flext_cli import FlextCliModels
from flext_core import u as core_u

from flext_db_oracle import c, t


class DbOracleDomainModel(FlextCliModels.BaseModel):
    """Base model for FlextDbOracle with standard Pydantic v2 configuration."""

    model_config: ClassVar[FlextCliModels.ConfigDict] = FlextCliModels.ConfigDict(
        use_enum_values=True,
        validate_default=True,
        str_strip_whitespace=True,
        extra="forbid",
    )


class RowData(DbOracleDomainModel):
    """Typed row payload for query results."""

    values: t.JsonList = core_u.Field(
        default_factory=tuple[t.JsonValue, ...],
        description="Row column values",
    )


class ColumnMetadata(DbOracleDomainModel):
    """Typed column metadata payload."""

    name: str
    data_type: str
    nullable: bool = True


class QueryResult(FlextCliModels.Entity, FlextCliModels.FlexibleModel):
    """Query result using flext-core Entity."""

    model_config: ClassVar[FlextCliModels.ConfigDict] = FlextCliModels.ConfigDict(
        frozen=False
    )

    query: str = core_u.Field(description="SQL query that produced the result")
    result_data: t.JsonList = core_u.Field(
        default_factory=tuple[t.JsonValue, ...],
        description="Raw result data from query execution",
    )
    row_count: t.NonNegativeInt = core_u.Field(
        0,
        description="Number of rows returned",
        validate_default=True,
    )
    execution_time_ms: t.NonNegativeInt = core_u.Field(
        0,
        description="Query execution time in milliseconds",
        validate_default=True,
    )

    # Additional Oracle-specific query result details
    columns: t.StrSequence = core_u.Field(
        default_factory=tuple[str, ...],
        description="Column names in result set",
    )
    rows: t.SequenceOf[RowData] = core_u.Field(
        default_factory=lambda: (),
        description="Typed row data from query result",
    )
    query_hash: str = core_u.Field(
        "",
        description="Query hash for caching",
        validate_default=True,
    )
    explain_plan: str = core_u.Field(
        "",
        description="Query execution plan",
        validate_default=True,
    )

    @property
    def column_count(self) -> int:
        """Number of columns."""
        return len(self.columns)

    @property
    def data_size_bytes(self) -> int:
        """Estimated data size in bytes."""
        return (
            len(self.rows) * len(self.columns) * c.DbOracle.DATA_SIZE_ESTIMATION_FACTOR
            if self.rows
            else 0
        )

    @property
    def execution_time_seconds(self) -> float:
        """Execution time in seconds."""
        execution_time_ms: float = float(self.execution_time_ms)
        return execution_time_ms / 1000.0

    @property
    def has_results(self) -> bool:
        """Whether query returned results."""
        row_count: int = self.row_count
        return row_count > 0

    @property
    def memory_usage_mb(self) -> float:
        """Estimated memory usage in MB."""
        data_size = (
            len(self.rows) * len(self.columns) * c.DbOracle.DATA_SIZE_ESTIMATION_FACTOR
            if self.rows
            else 0
        )
        return data_size / (1024 * 1024)

    @property
    def performance_rating(self) -> str:
        """Query performance rating."""
        result_acceptance_threshold_ms = c.DbOracle.QUERY_ACCEPTABLE_THRESHOLD_MS + 500
        if (
            self.has_results
            and self.execution_time_ms <= result_acceptance_threshold_ms
        ):
            return "Acceptable"
        return (
            "Excellent"
            if self.execution_time_ms < c.DbOracle.QUERY_EXCELLENT_THRESHOLD_MS
            else "Good"
            if self.execution_time_ms < c.DbOracle.QUERY_GOOD_THRESHOLD_MS
            else "Acceptable"
            if self.execution_time_ms < c.DbOracle.QUERY_ACCEPTABLE_THRESHOLD_MS
            else "Slow"
        )

    @core_u.field_serializer("execution_time_ms", when_used="json")
    @staticmethod
    def serialize_execution_time(value: int) -> str:
        """Format execution time with appropriate units.

        Returns:
            The resulting ``str``.

        """
        threshold = c.DbOracle.MILLISECONDS_TO_SECONDS_THRESHOLD
        return f"{value}ms" if value < threshold else f"{value / threshold:.2f}s"

    @core_u.model_validator(mode="after")
    def validate_query_result_consistency(self) -> QueryResult:
        """Validate query result consistency.

        Returns:
            The resulting ``FlextDbOracleModels.DbOracle.QueryResult``.

        Raises:
            ValueError: If Execution time cannot be negative; or if Row length.

        """
        if len(self.rows) != self.row_count:
            self.row_count = len(self.rows)
        if self.rows and self.columns:
            for row in self.rows:
                if len(row.values) != len(self.columns):
                    msg = (
                        f"Row length {len(row.values)} doesn't match "
                        f"column count {len(self.columns)}"
                    )
                    raise ValueError(msg)
        if self.execution_time_ms < 0:
            msg = "Execution time cannot be negative"
            raise ValueError(msg)
        return self


__all__: list[str] = [
    "ColumnMetadata",
    "DbOracleDomainModel",
    "QueryResult",
    "RowData",
]
