"""Oracle Database models using FLEXT ecosystem patterns.

This module provides Oracle-specific models extending flext-core patterns
for data structures and domain objects.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from datetime import UTC, datetime

from flext_core import FlextModels, FlextTypes
from pydantic import (
    Field,
    computed_field,
    field_serializer,
    model_validator,
)

from flext_db_oracle.constants import FlextDbOracleConstants


class FlextDbOracleModels(FlextModels):
    """Oracle database models using flext-core exclusively.

    Contains ONLY pure domain models (Entity, Value, AggregateRoot, etc.).
    All config-like classes moved to config.py.
    All constants moved to constants.py.
    All types moved to typings.py.
    """

    class ConnectionStatus(FlextModels.Entity):
        """Connection status using flext-core Entity."""

        is_connected: bool = False
        last_check: datetime = Field(default_factory=lambda: datetime.now(UTC))
        error_message: str | None = None

        # Additional Oracle-specific connection details
        connection_time: float | None = None
        last_activity: datetime | None = None
        session_id: str | None = None
        host: str | None = None
        port: int | None = None
        service_name: str | None = None
        username: str | None = None
        db_version: str | None = None

        @computed_field
        def status_description(self) -> str:
            """Computed field for human-readable status description."""
            if self.is_connected:
                return "Connected"
            if self.error_message:
                return f"Disconnected: {self.error_message}"
            return "Disconnected"

        @computed_field
        def connection_age_seconds(self) -> float | None:
            """Computed field for connection age in seconds."""
            if not self.is_connected or not self.last_activity:
                return None
            return (datetime.now(UTC) - self.last_activity).total_seconds()

        @computed_field
        def is_healthy(self) -> bool:
            """Computed field indicating if connection is healthy."""
            if not self.is_connected:
                return False

            # Consider connection unhealthy if no activity for more than configured timeout
            return not (
                self.connection_age_seconds
                and self.connection_age_seconds
                > FlextDbOracleConstants.OraclePerformance.CONNECTION_IDLE_TIMEOUT_SECONDS
            )

        @computed_field
        def connection_info(self) -> str:
            """Computed field for connection information summary."""
            if not self.is_connected:
                return "Not connected"

            parts = []
            if self.host:
                parts.append(f"host={self.host}")
            if self.port:
                parts.append(f"port={self.port}")
            if self.service_name:
                parts.append(f"service={self.service_name}")
            if self.username:
                parts.append(f"user={self.username}")

            return ", ".join(parts) if parts else "Connected"

        @computed_field
        def performance_info(self) -> str:
            """Computed field for connection performance information."""
            if not self.is_connected or self.connection_time is None:
                return "No performance data"

            # Performance thresholds from constants
            if (
                self.connection_time
                < FlextDbOracleConstants.OraclePerformance.CONNECTION_EXCELLENT_THRESHOLD_SECONDS
            ):
                return f"Excellent ({self.connection_time:.3f}s)"
            if (
                self.connection_time
                < FlextDbOracleConstants.OraclePerformance.CONNECTION_GOOD_THRESHOLD_SECONDS
            ):
                return f"Good ({self.connection_time:.3f}s)"
            if (
                self.connection_time
                < FlextDbOracleConstants.OraclePerformance.CONNECTION_ACCEPTABLE_THRESHOLD_SECONDS
            ):
                return f"Acceptable ({self.connection_time:.3f}s)"
            return f"Slow ({self.connection_time:.3f}s)"

        @model_validator(mode="after")
        def validate_connection_status_consistency(
            self,
        ) -> FlextDbOracleModels.ConnectionStatus:
            """Model validator for connection status consistency."""
            # If connected, ensure we have basic connection info
            if self.is_connected:
                if not self.host:
                    msg = "Connected status requires host information"
                    raise ValueError(msg)

                max_port = 65535
                if self.port and not (1 <= self.port <= max_port):
                    msg = f"Invalid port number: {self.port}"
                    raise ValueError(msg)

            # If not connected, error message should be provided
            if not self.is_connected and not self.error_message:
                self.error_message = "Connection failed"

            # Validate connection time
            if self.connection_time is not None and self.connection_time < 0:
                msg = "Connection time cannot be negative"
                raise ValueError(msg)

            return self

        @field_serializer("error_message")
        def serialize_error_message(self, value: str | None) -> str | None:
            """Field serializer for error message truncation."""
            if value is None:
                return None
            # Truncate very long error messages for serialization
            max_length = 500
            if len(value) > max_length:
                return f"{value[:max_length]}... (truncated)"
            return value

        @field_serializer("last_check", "last_activity")
        def serialize_datetime(self, value: datetime | None) -> str | None:
            """Field serializer for datetime formatting."""
            if value is None:
                return None
            return value.isoformat()

        @field_serializer("connection_time")
        def serialize_connection_time(self, value: float | None) -> str | None:
            """Field serializer for connection time formatting."""
            if value is None:
                return None
            return f"{value:.3f}s"

    class QueryResult(FlextModels.Entity):
        """Query result using flext-core Entity."""

        query: str
        result_data: list[FlextTypes.Dict] = Field(default_factory=list)
        row_count: int = 0
        execution_time_ms: int = 0

        # Additional Oracle-specific query result details
        columns: FlextTypes.StringList = Field(
            default_factory=list, description="Column names"
        )
        rows: list[FlextTypes.List] = Field(
            default_factory=list, description="Row data"
        )
        query_hash: str | None = Field(
            default=None,
            description="Query hash for caching",
        )
        explain_plan: str | None = Field(
            default=None,
            description="Query execution plan",
        )

        @computed_field
        def execution_time_seconds(self) -> float:
            """Computed field for execution time in seconds."""
            return self.execution_time_ms / 1000.0

        @computed_field
        def has_results(self) -> bool:
            """Computed field indicating if query returned results."""
            return self.row_count > 0

        @computed_field
        def column_count(self) -> int:
            """Computed field for number of columns."""
            return len(self.columns)

        @computed_field
        def performance_rating(self) -> str:
            """Computed field for query performance rating."""
            if (
                self.execution_time_ms
                < FlextDbOracleConstants.OraclePerformance.QUERY_EXCELLENT_THRESHOLD_MS
            ):
                return "Excellent"
            if (
                self.execution_time_ms
                < FlextDbOracleConstants.OraclePerformance.QUERY_GOOD_THRESHOLD_MS
            ):
                return "Good"
            if (
                self.execution_time_ms
                < FlextDbOracleConstants.OraclePerformance.QUERY_ACCEPTABLE_THRESHOLD_MS
            ):
                return "Acceptable"
            return "Slow"

        @computed_field
        def data_size_bytes(self) -> int:
            """Computed field for estimated data size in bytes."""
            if not self.rows:
                return 0

            # Rough estimation using configured factor
            cells = len(self.rows) * len(self.columns)
            return (
                cells
                * FlextDbOracleConstants.OraclePerformance.DATA_SIZE_ESTIMATION_FACTOR
            )

        @computed_field
        def memory_usage_mb(self) -> float:
            """Computed field for estimated memory usage in MB."""
            return self.data_size_bytes / (1024 * 1024)

        @model_validator(mode="after")
        def validate_query_result_consistency(
            self,
        ) -> FlextDbOracleModels.QueryResult:
            """Model validator for query result consistency."""
            # Ensure row count matches actual rows
            if len(self.rows) != self.row_count:
                self.row_count = len(self.rows)

            # Ensure column count is consistent
            if self.rows and len(self.columns) > 0:
                for row in self.rows:
                    if len(row) != len(self.columns):
                        msg = f"Row length {len(row)} doesn't match column count {len(self.columns)}"
                        raise ValueError(msg)

            # Validate execution time
            if self.execution_time_ms < 0:
                msg = "Execution time cannot be negative"
                raise ValueError(msg)

            return self

        @field_serializer("execution_time_ms")
        def serialize_execution_time(self, value: int) -> str:
            """Field serializer for execution time formatting."""
            if (
                value
                < FlextDbOracleConstants.OraclePerformance.MILLISECONDS_TO_SECONDS_THRESHOLD
            ):
                return f"{value}ms"
            return f"{value / FlextDbOracleConstants.OraclePerformance.MILLISECONDS_TO_SECONDS_THRESHOLD:.2f}s"

    class Table(FlextModels.Entity):
        """Table metadata using flext-core Entity."""

        name: str
        schema_name: str = Field(alias="schema")
        columns: list[FlextDbOracleModels.Column] = Field(default_factory=list)

    class Column(FlextModels.Entity):
        """Column metadata using flext-core Entity."""

        name: str
        data_type: str
        nullable: bool = True
        default_value: str | None = None

    class Schema(FlextModels.Entity):
        """Schema metadata using flext-core Entity."""

        name: str
        tables: list[FlextDbOracleModels.Table] = Field(default_factory=list)

    class CreateIndexConfig(FlextModels.Entity):
        """Create index config using flext-core Entity."""

        table_name: str
        index_name: str
        columns: FlextTypes.StringList
        unique: bool = False
        schema_name: str | None = None
        tablespace: str | None = None
        parallel: int | None = None

    class MergeStatementConfig(FlextModels.Entity):
        """Merge statement config using flext-core Entity."""

        target_table: str
        source_query: str
        merge_conditions: FlextTypes.StringList
        update_columns: FlextTypes.StringList = Field(default_factory=list)
        insert_columns: FlextTypes.StringList = Field(default_factory=list)


# ZERO TOLERANCE: No compatibility aliases - use FlextDbOracleModels.ClassName directly

__all__ = [
    "FlextDbOracleModels",
]
