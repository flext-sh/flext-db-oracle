"""Oracle Database models using FLEXT ecosystem patterns.

This module provides Oracle-specific models extending flext-core patterns
for data structures and domain objects.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from datetime import UTC, datetime
from typing import Annotated

from flext_core import FlextModels
from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_serializer,
    model_validator,
)

from flext_db_oracle.constants import c
from flext_db_oracle.typings import t


def _default_parameters_list() -> list[Mapping[str, t.ContainerValue]]:
    return []


class FlextDbOracleModels(FlextModels):
    """Oracle database models using flext-core exclusively.

    Contains ONLY pure domain models (Entity, Value, AggregateRoot, etc.).
    All config-like classes moved to config.py.
    All constants moved to constants.py.
    All types moved to typings.py.
    """

    class DbOracle:
        """DbOracle domain namespace."""

        class FlextDbOracleBaseModel(BaseModel):
            """Base model for FlextDbOracle with standard Pydantic v2 configuration."""

            model_config = ConfigDict(
                use_enum_values=True,
                validate_default=True,
                str_strip_whitespace=True,
                extra="forbid",
            )

        class RowData(FlextDbOracleBaseModel):
            """Typed row payload for query results."""

            values: Annotated[Sequence[t.ContainerValue], Field(default_factory=list)]

        class ColumnMetadata(FlextDbOracleBaseModel):
            """Typed column metadata payload."""

            name: str
            data_type: str
            nullable: bool = True

        class SingerSchemaField(FlextDbOracleBaseModel):
            """Typed singer schema field."""

            name: str
            definition: FlextDbOracleModels.DbOracle.SingerField

        class ConnectionStatus(FlextModels.Entity):
            """Connection status using flext-core Entity."""

            model_config = ConfigDict(frozen=False, extra="ignore")

            is_connected: bool = False
            last_check: Annotated[
                datetime, Field(default_factory=lambda: datetime.now(UTC))
            ]
            error_message: Annotated[
                str,
                Field(
                    default="",
                    description="Error message when disconnected",
                ),
            ]

            # Additional Oracle-specific connection details
            connection_time: Annotated[
                float,
                Field(
                    default=0.0,
                    description="Connection establishment time in seconds",
                ),
            ]
            last_activity: Annotated[
                datetime, Field(default_factory=lambda: datetime.now(UTC))
            ]
            session_id: Annotated[
                str, Field(default="", description="Oracle session identifier")
            ]
            host: Annotated[str, Field(default="", description="Database host")]
            port: Annotated[
                int,
                Field(
                    default=c.DbOracle.Connection.DEFAULT_PORT,
                    description="Database port",
                ),
            ]
            service_name: Annotated[
                str, Field(default="", description="Oracle service name")
            ]
            username: Annotated[str, Field(default="", description="Database username")]
            db_version: Annotated[
                str, Field(default="", description="Oracle database version")
            ]

            @property
            def connection_age_seconds(self) -> float:
                """Connection age in seconds."""
                if self.is_connected:
                    return (datetime.now(UTC) - self.last_activity).total_seconds()
                return 0.0

            @property
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

            @property
            def is_healthy(self) -> bool:
                """Connection health status."""
                if not self.is_connected:
                    return False
                age_seconds = float((datetime.now(UTC) - self.last_activity).seconds)
                return (
                    age_seconds
                    <= c.DbOracle.OraclePerformance.CONNECTION_IDLE_TIMEOUT_SECONDS
                )

            @property
            def performance_info(self) -> str:
                """Connection performance information."""
                if not self.is_connected or self.connection_time <= 0:
                    return "No performance data"
                thresholds = c.DbOracle.OraclePerformance
                if (
                    self.connection_time
                    < thresholds.CONNECTION_EXCELLENT_THRESHOLD_SECONDS
                ):
                    return f"Excellent ({self.connection_time:.3f}s)"
                if self.connection_time < thresholds.CONNECTION_GOOD_THRESHOLD_SECONDS:
                    return f"Good ({self.connection_time:.3f}s)"
                if (
                    self.connection_time
                    < thresholds.CONNECTION_ACCEPTABLE_THRESHOLD_SECONDS
                ):
                    return f"Acceptable ({self.connection_time:.3f}s)"
                return f"Slow ({self.connection_time:.3f}s)"

            @property
            def status_description(self) -> str:
                """Human-readable status description."""
                if self.is_connected:
                    return "Connected"
                return (
                    f"Disconnected: {self.error_message}"
                    if self.error_message
                    else "Disconnected"
                )

            @field_serializer("connection_time", when_used="json")
            def serialize_connection_time(self, value: float) -> str:
                """Format connection time with units."""
                return f"{value:.3f}s"

            @field_serializer("last_check", "last_activity", when_used="json")
            def serialize_datetime(self, value: datetime) -> str:
                """Format datetime as ISO string."""
                return value.isoformat()

            @field_serializer("error_message")
            def serialize_error_message(self, value: str) -> str:
                """Truncate long error messages."""
                max_error_length = c.DbOracle.Error.MAX_ERROR_MESSAGE_LENGTH
                if len(value) > max_error_length:
                    return f"{value[:max_error_length]}... (truncated)"
                return value

            @model_validator(mode="after")
            def validate_connection_status_consistency(
                self,
            ) -> FlextDbOracleModels.DbOracle.ConnectionStatus:
                """Validate connection status consistency."""
                if self.is_connected and not self.host:
                    msg = "Connected status requires host information"
                    raise ValueError(msg)
                if self.is_connected and not (
                    c.DbOracle.OracleNetwork.MIN_PORT
                    <= self.port
                    <= c.DbOracle.OracleNetwork.MAX_PORT
                ):
                    msg = f"Invalid port number: {self.port}"
                    raise ValueError(msg)
                if self.connection_time < 0:
                    msg = "Connection time cannot be negative"
                    raise ValueError(msg)
                return self

        class QueryResult(FlextModels.Entity):
            """Query result using flext-core Entity."""

            model_config = ConfigDict(frozen=False, extra="ignore")

            query: str
            result_data: Annotated[
                Sequence[t.ContainerValue], Field(default_factory=list)
            ]
            row_count: int = 0
            execution_time_ms: int = 0

            # Additional Oracle-specific query result details
            columns: Annotated[list[str], Field(default_factory=list)]
            rows: Annotated[
                Sequence[FlextDbOracleModels.DbOracle.RowData],
                Field(default_factory=list),
            ]
            query_hash: Annotated[
                str, Field(default="", description="Query hash for caching")
            ]
            explain_plan: Annotated[
                str, Field(default="", description="Query execution plan")
            ]

            @property
            def column_count(self) -> int:
                """Number of columns."""
                return len(self.columns)

            @property
            def data_size_bytes(self) -> int:
                """Estimated data size in bytes."""
                return (
                    len(self.rows)
                    * len(self.columns)
                    * c.DbOracle.OraclePerformance.DATA_SIZE_ESTIMATION_FACTOR
                    if self.rows
                    else 0
                )

            @property
            def execution_time_seconds(self) -> float:
                """Execution time in seconds."""
                return self.execution_time_ms / 1000.0

            @property
            def has_results(self) -> bool:
                """Whether query returned results."""
                return self.row_count > 0

            @property
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

            @property
            def performance_rating(self) -> str:
                """Query performance rating."""
                thresholds = c.DbOracle.OraclePerformance
                result_acceptance_threshold_ms = (
                    thresholds.QUERY_ACCEPTABLE_THRESHOLD_MS + 500
                )
                if (
                    self.has_results
                    and self.execution_time_ms <= result_acceptance_threshold_ms
                ):
                    return "Acceptable"
                return (
                    "Excellent"
                    if self.execution_time_ms < thresholds.QUERY_EXCELLENT_THRESHOLD_MS
                    else "Good"
                    if self.execution_time_ms < thresholds.QUERY_GOOD_THRESHOLD_MS
                    else "Acceptable"
                    if self.execution_time_ms < thresholds.QUERY_ACCEPTABLE_THRESHOLD_MS
                    else "Slow"
                )

            @field_serializer("execution_time_ms", when_used="json")
            def serialize_execution_time(self, value: int) -> str:
                """Format execution time with appropriate units."""
                threshold = (
                    c.DbOracle.OraclePerformance.MILLISECONDS_TO_SECONDS_THRESHOLD
                )
                return (
                    f"{value}ms" if value < threshold else f"{value / threshold:.2f}s"
                )

            @model_validator(mode="after")
            def validate_query_result_consistency(
                self,
            ) -> FlextDbOracleModels.DbOracle.QueryResult:
                """Validate query result consistency."""
                if len(self.rows) != self.row_count:
                    self.row_count = len(self.rows)
                if self.rows and len(self.columns) > 0:
                    for row in self.rows:
                        if isinstance(
                            row, FlextDbOracleModels.DbOracle.RowData
                        ) and len(row.values) != len(self.columns):
                            msg = f"Row length {len(row.values)} doesn't match column count {len(self.columns)}"
                            raise ValueError(msg)
                if self.execution_time_ms < 0:
                    msg = "Execution time cannot be negative"
                    raise ValueError(msg)
                return self

        class OperationRecord(FlextModels.Entity):
            """Operation tracking record for observability workflows."""

            operation_type: str
            duration: float
            success: bool
            metadata_info: Annotated[
                str, Field(default="", description="Operation metadata")
            ]
            timestamp: str

        class HealthStatus(FlextModels.Entity):
            """Service health status record."""

            status: str
            timestamp: str
            service: str = "oracle"
            database: str = "oracle"
            metrics: Annotated[
                Mapping[str, t.ContainerValue], Field(default_factory=dict)
            ]

            def __getitem__(self, key: str) -> t.ContainerValue:
                """Get item from health status."""
                if key in self.metrics:
                    return self.metrics[key]
                return self.model_dump().get(key)

            def __contains__(self, key: str) -> bool:
                """Check if key is in health status."""
                if key in self.metrics:
                    return True
                return key in self.model_dump()

        class TableMetadata(FlextModels.Entity):
            """Complete table metadata for Oracle introspection."""

            table_name: str
            schema_name: str = ""
            columns: Annotated[
                Sequence[FlextDbOracleModels.DbOracle.ColumnMetadata],
                Field(default_factory=list),
            ]
            primary_keys: Annotated[list[str], Field(default_factory=list)]

            def __getitem__(self, key: str) -> t.ContainerValue:
                """Get item from table metadata."""
                return self.model_dump().get(key)

            def __contains__(self, key: str) -> bool:
                """Check if key is in table metadata."""
                return key in self.model_dump()

        class TypeMapping(FlextModels.Entity):
            """Singer-to-Oracle type mapping."""

            mapping: Annotated[Mapping[str, str], Field(default_factory=dict)]

            def __getitem__(self, key: str) -> str:
                """Get mapped type for key."""
                return self.mapping[key]

            def __len__(self) -> int:
                """Get number of type mappings."""
                return len(self.mapping)

            def __contains__(self, key: str) -> bool:
                """Check if key is in type mapping."""
                return key in self.mapping

        class SingerField(FlextModels.Entity):
            """Singer field definition."""

            type: str | list[str] = "string"

        class SingerSchema(FlextModels.Entity):
            """Singer schema container with typed properties."""

            properties: Annotated[
                Mapping[str, FlextDbOracleModels.DbOracle.SingerField],
                Field(default_factory=dict),
            ]

        class Table(FlextModels.Entity):
            """Table metadata using flext-core Entity."""

            name: str
            owner: str = ""
            columns: Annotated[
                Sequence[FlextDbOracleModels.DbOracle.Column],
                Field(default_factory=list),
            ]

        class Column(FlextModels.Entity):
            """Column metadata using flext-core Entity."""

            name: str
            data_type: str
            nullable: bool = True
            primary_key: Annotated[
                bool,
                Field(
                    default=False,
                    description="Whether this column is a primary key",
                ),
            ]
            default_value: Annotated[
                str,
                Field(
                    default="",
                    description="Default value for the column",
                ),
            ]

            def __getitem__(self, key: str) -> t.ContainerValue:
                """Get item from column metadata."""
                key_map: dict[str, t.ContainerValue] = {
                    "column_name": self.name,
                    "name": self.name,
                    "data_type": self.data_type,
                    "nullable": self.nullable,
                    "primary_key": self.primary_key,
                    "default_value": self.default_value,
                }
                if key in key_map:
                    return key_map[key]
                return None

            def __contains__(self, key: str) -> bool:
                """Check if key is in column metadata."""
                return key in {
                    "name",
                    "column_name",
                    "data_type",
                    "nullable",
                    "primary_key",
                    "default_value",
                }

        class Schema(FlextModels.Entity):
            """Schema metadata using flext-core Entity."""

            name: str
            tables: Annotated[
                Sequence[FlextDbOracleModels.DbOracle.Table],
                Field(default_factory=list),
            ]

        class CreateIndexConfig(FlextModels.Entity):
            """Create index config using flext-core Entity."""

            table_name: str
            index_name: str
            columns: list[str]
            unique: bool = False
            schema_name: Annotated[str, Field(default="", description="Schema name")]
            tablespace: Annotated[str, Field(default="", description="Tablespace name")]
            parallel: Annotated[
                int,
                Field(
                    default=1,
                    description="Parallel degree for index creation",
                ),
            ]

        class MergeStatementConfig(FlextModels.Entity):
            """Merge statement config using flext-core Entity."""

            target_table: str
            source_query: str
            merge_conditions: list[str]
            update_columns: Annotated[list[str], Field(default_factory=list)]
            insert_columns: Annotated[list[str], Field(default_factory=list)]

        # Command classes for dispatcher integration
        class ConnectCommand(FlextModels.Entity):
            """Command to establish Oracle connection."""

            pass

        class DisconnectCommand(FlextModels.Entity):
            """Command to close Oracle connection."""

            pass

        class TestConnectionCommand(FlextModels.Entity):
            """Command to test Oracle connection."""

            pass

        class ExecuteQueryCommand(FlextModels.Entity):
            """Command to execute SELECT query."""

            sql: str
            parameters: dict[str, t.ContainerValue] | None = None

        class FetchOneCommand(FlextModels.Entity):
            """Command to fetch single row."""

            sql: str
            parameters: dict[str, t.ContainerValue] | None = None

        class ExecuteStatementCommand(FlextModels.Entity):
            """Command to execute INSERT/UPDATE/DELETE."""

            sql: str
            parameters: dict[str, t.ContainerValue] | None = None

        class ExecuteManyCommand(FlextModels.Entity):
            """Command to execute batch statements."""

            sql: str
            parameters_list: Annotated[
                Sequence[Mapping[str, t.ContainerValue]],
                Field(default_factory=_default_parameters_list),
            ]

        class GetSchemasCommand(FlextModels.Entity):
            """Command to retrieve all schemas."""

            pass

        class GetTablesCommand(FlextModels.Entity):
            """Command to retrieve tables in schema."""

            schema_name: str | None = None

        class GetColumnsCommand(FlextModels.Entity):
            """Command to retrieve columns in table."""

            table: str
            schema_name: str | None = None


m = FlextDbOracleModels

__all__ = [
    "FlextDbOracleModels",
    "m",
]
