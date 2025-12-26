"""Oracle Database models using FLEXT ecosystem patterns.

This module provides Oracle-specific models extending flext-core patterns
for data structures and domain objects.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from datetime import UTC, datetime

from flext_core import FlextTypes, c as c_core, m as m_core
from flext_core.typings import t
from flext_core.utilities import u as flext_u
from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    computed_field,
    field_serializer,
    model_validator,
)

from flext_db_oracle.constants import c


class FlextDbOracleBaseModel(BaseModel):
    """Base model for FlextDbOracle with standard Pydantic v2 configuration."""

    model_config = ConfigDict(
        use_enum_values=True,
        validate_default=True,
        str_strip_whitespace=True,
        extra="forbid",
    )


class FlextDbOracleModels(m_core):
    """Oracle database models using flext-core exclusively.

    Contains ONLY pure domain models (Entity, Value, AggregateRoot, etc.).
    All config-like classes moved to config.py.
    All constants moved to constants.py.
    All types moved to typings.py.
    """

    def __init_subclass__(cls, **kwargs: t.GeneralValueType) -> None:
        """Warn when FlextDbOracleModels is subclassed directly."""
        super().__init_subclass__(**kwargs)
        flext_u.Deprecation.warn_once(
            f"subclass:{cls.__name__}",
            "Subclassing FlextDbOracleModels is deprecated. Use FlextModels directly with composition instead.",
        )

    class ConnectionStatus(m_core.Entity):
        """Connection status using flext-core Entity."""

        is_connected: bool = False
        last_check: datetime = Field(default_factory=lambda: datetime.now(UTC))
        error_message: str = Field(
            default="",
            description="Error message when disconnected",
        )

        # Additional Oracle-specific connection details
        connection_time: float = Field(
            default=0.0,
            description="Connection establishment time in seconds",
        )
        last_activity: datetime = Field(default_factory=lambda: datetime.now(UTC))
        session_id: str = Field(default="", description="Oracle session identifier")
        host: str = Field(default="", description="Database host")
        port: int = Field(
            default=c.DbOracle.Connection.DEFAULT_PORT,
            description="Database port",
        )
        service_name: str = Field(default="", description="Oracle service name")
        username: str = Field(default="", description="Database username")
        db_version: str = Field(default="", description="Oracle database version")

        @computed_field
        def status_description(self) -> str:
            """Human-readable status description."""
            if self.is_connected:
                return "Connected"
            return (
                f"Disconnected: {self.error_message}"
                if self.error_message
                else "Disconnected"
            )

        @computed_field
        def connection_age_seconds(self) -> float:
            """Connection age in seconds."""
            if self.is_connected:
                return (datetime.now(UTC) - self.last_activity).total_seconds()
            return 0.0

        @computed_field
        def is_healthy(self) -> bool:
            """Connection health status."""
            if not self.is_connected:
                return False
            age_seconds = self.connection_age_seconds()
            return (
                age_seconds
                <= c.DbOracle.OraclePerformance.CONNECTION_IDLE_TIMEOUT_SECONDS
            )

        @computed_field
        def connection_info(self) -> str:
            """Connection information summary."""
            if not self.is_connected:
                return "Not connected"
            parts = [
                f"{k}={v}"
                for k, v in [
                    ("host", self.host),
                    ("port", self.port),
                    ("service", self.service_name),
                    ("user", self.username),
                ]
                if v  # Empty strings are falsy, so this works
            ]
            return ", ".join(parts) or "Connected"

        @computed_field
        def performance_info(self) -> str:
            """Connection performance information."""
            if not self.is_connected or self.connection_time <= 0:
                return "No performance data"
            thresholds = c.OraclePerformance
            if self.connection_time < thresholds.CONNECTION_EXCELLENT_THRESHOLD_SECONDS:
                return f"Excellent ({self.connection_time:.3f}s)"
            if self.connection_time < thresholds.CONNECTION_GOOD_THRESHOLD_SECONDS:
                return f"Good ({self.connection_time:.3f}s)"
            if (
                self.connection_time
                < thresholds.CONNECTION_ACCEPTABLE_THRESHOLD_SECONDS
            ):
                return f"Acceptable ({self.connection_time:.3f}s)"
            return f"Slow ({self.connection_time:.3f}s)"

        @model_validator(mode="after")
        def validate_connection_status_consistency(
            self,
        ) -> FlextDbOracleModels.ConnectionStatus:
            """Validate connection status consistency."""
            if self.is_connected and not self.host:
                msg = "Connected status requires host information"
                raise ValueError(msg)
            if self.is_connected and not (
                c_core.Network.MIN_PORT <= self.port <= c_core.Network.MAX_PORT
            ):
                msg = f"Invalid port number: {self.port}"
                raise ValueError(msg)
            if not self.is_connected and not self.error_message:
                self.error_message = "Connection failed"
            if self.connection_time < 0:
                msg = "Connection time cannot be negative"
                raise ValueError(msg)
            return self

        @field_serializer("error_message")
        def serialize_error_message(self, value: str) -> str:
            """Truncate long error messages."""
            max_error_length = 500
            if len(value) > max_error_length:
                return f"{value[:max_error_length]}... (truncated)"
            return value

        @field_serializer("last_check", "last_activity")
        def serialize_datetime(self, value: datetime) -> str:
            """Format datetime as ISO string."""
            return value.isoformat()

        @field_serializer("connection_time")
        def serialize_connection_time(self, value: float) -> str:
            """Format connection time with units."""
            return f"{value:.3f}s"

    class QueryResult(m_core.Entity):
        """Query result using flext-core Entity."""

        query: str
        result_data: list[dict[str, FlextTypes.JsonValue]] = Field(default_factory=list)
        row_count: int = 0
        execution_time_ms: int = 0

        # Additional Oracle-specific query result details
        columns: list[str] = Field(default_factory=list, description="Column names")
        rows: list[list[FlextTypes.JsonValue]] = Field(
            default_factory=list,
            description="Row data",
        )
        query_hash: str = Field(default="", description="Query hash for caching")
        explain_plan: str = Field(default="", description="Query execution plan")

        @computed_field
        def execution_time_seconds(self) -> float:
            """Execution time in seconds."""
            return self.execution_time_ms / 1000.0

        @computed_field
        def has_results(self) -> bool:
            """Whether query returned results."""
            return self.row_count > 0

        @computed_field
        def column_count(self) -> int:
            """Number of columns."""
            return len(self.columns)

        @computed_field
        def performance_rating(self) -> str:
            """Query performance rating."""
            thresholds = c.OraclePerformance
            return (
                "Excellent"
                if self.execution_time_ms < thresholds.QUERY_EXCELLENT_THRESHOLD_MS
                else "Good"
                if self.execution_time_ms < thresholds.QUERY_GOOD_THRESHOLD_MS
                else "Acceptable"
                if self.execution_time_ms < thresholds.QUERY_ACCEPTABLE_THRESHOLD_MS
                else "Slow"
            )

        @computed_field
        def data_size_bytes(self) -> int:
            """Estimated data size in bytes."""
            return (
                len(self.rows)
                * len(self.columns)
                * c.DbOracle.OraclePerformance.DATA_SIZE_ESTIMATION_FACTOR
                if self.rows
                else 0
            )

        @computed_field
        def memory_usage_mb(self) -> float:
            """Estimated memory usage in MB."""
            data_size = (
                len(self.rows)
                * len(self.columns)
                * c.DbOracle.OraclePerformance.DATA_SIZE_ESTIMATION_FACTOR
                if self.rows
                else 0
            )
            return data_size / (1024 * 1024)

        @model_validator(mode="after")
        def validate_query_result_consistency(self) -> FlextDbOracleModels.QueryResult:
            """Validate query result consistency."""
            if len(self.rows) != self.row_count:
                self.row_count = len(self.rows)
            if self.rows and len(self.columns) > 0:
                for row in self.rows:
                    if len(row) != len(self.columns):
                        msg = f"Row length {len(row)} doesn't match column count {len(self.columns)}"
                        raise ValueError(msg)
            if self.execution_time_ms < 0:
                msg = "Execution time cannot be negative"
                raise ValueError(msg)
            return self

        @field_serializer("execution_time_ms")
        def serialize_execution_time(self, value: int) -> str:
            """Format execution time with appropriate units."""
            threshold = c.DbOracle.OraclePerformance.MILLISECONDS_TO_SECONDS_THRESHOLD
            return f"{value}ms" if value < threshold else f"{value / threshold:.2f}s"

    class Table(m_core.Entity):
        """Table metadata using flext-core Entity."""

        name: str
        owner: str = Field(alias="schema")
        columns: list[FlextDbOracleModels.Column] = Field(default_factory=list)

    class Column(m_core.Entity):
        """Column metadata using flext-core Entity."""

        name: str
        data_type: str
        nullable: bool = True
        default_value: str = Field(
            default="",
            description="Default value for the column",
        )

    class Schema(m_core.Entity):
        """Schema metadata using flext-core Entity."""

        name: str
        tables: list[FlextDbOracleModels.Table] = Field(default_factory=list)

    class CreateIndexConfig(m_core.Entity):
        """Create index config using flext-core Entity."""

        table_name: str
        index_name: str
        columns: list[str]
        unique: bool = False
        schema_name: str = Field(default="", description="Schema name")
        tablespace: str = Field(default="", description="Tablespace name")
        parallel: int = Field(
            default=1,
            description="Parallel degree for index creation",
        )

    class MergeStatementConfig(m_core.Entity):
        """Merge statement config using flext-core Entity."""

        target_table: str
        source_query: str
        merge_conditions: list[str]
        update_columns: list[str] = Field(default_factory=list)
        insert_columns: list[str] = Field(default_factory=list)


# Zero Tolerance: No compatibility aliases - use FlextDbOracleModels.ClassName directly

m = FlextDbOracleModels
m_db_oracle = FlextDbOracleModels

__all__ = [
    "FlextDbOracleBaseModel",
    "FlextDbOracleModels",
    "m",
    "m_db_oracle",
]
