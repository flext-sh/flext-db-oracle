"""Oracle Database models using FLEXT ecosystem patterns.

This module provides Oracle-specific models extending flext-core patterns
for data structures and domain objects.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from types import MappingProxyType
from typing import TYPE_CHECKING, ClassVar

from flext_cli import m, u
from flext_db_oracle import c, t
from flext_db_oracle._models.password import FlextDbOraclePassword

if TYPE_CHECKING:
    from datetime import datetime


class FlextDbOracleModels(m):
    """Oracle database models using flext-core exclusively.

    Contains ONLY pure domain models (Entity, Value, AggregateRoot, etc.).
    All settings-like classes moved to settings.py.
    All constants moved to constants.py.
    All types moved to typings.py.
    """

    class DbOracle:
        """DbOracle domain namespace."""

        Password: type[FlextDbOraclePassword] = FlextDbOraclePassword

        class DbOracleDomainModel(m.BaseModel):
            """Base model for FlextDbOracle with standard Pydantic v2 configuration."""

            model_config: ClassVar[m.ConfigDict] = m.ConfigDict(
                use_enum_values=True,
                validate_default=True,
                str_strip_whitespace=True,
                extra="forbid",
            )

        class RowData(DbOracleDomainModel):
            """Typed row payload for query results."""

            values: t.JsonList = u.Field(
                default_factory=tuple,
                description="Row column values",
            )

        class ColumnMetadata(DbOracleDomainModel):
            """Typed column metadata payload."""

            name: str
            data_type: str
            nullable: bool = True

        class ConnectionStatus(m.Entity, m.FlexibleModel):
            """Connection status using flext-core Entity."""

            model_config: ClassVar[m.ConfigDict] = m.ConfigDict(frozen=False)

            connected: bool = u.Field(
                False,
                description="Whether connection is active",
                validate_default=True,
            )
            last_check: datetime = u.Field(
                default_factory=u.now,
                description="Timestamp of last connection check",
            )
            error_message: str = u.Field(
                "",
                description="Error message when disconnected",
                validate_default=True,
            )

            # Additional Oracle-specific connection details
            connection_time: t.NonNegativeFloat = u.Field(
                0.0,
                description="Connection establishment time in seconds",
                validate_default=True,
            )
            last_activity: datetime = u.Field(
                default_factory=u.now,
                description="Timestamp of last database activity",
            )
            session_id: str = u.Field(
                "",
                description="Oracle session identifier",
                validate_default=True,
            )
            host: str = u.Field("", description="Database host", validate_default=True)
            port: t.PortNumber = u.Field(
                c.DbOracle.DEFAULT_PORT,
                description="Database port",
                validate_default=True,
            )
            service_name: str = u.Field(
                "",
                description="Oracle service name",
                validate_default=True,
            )
            username: str = u.Field(
                "",
                description="Database username",
                validate_default=True,
            )
            db_version: str = u.Field(
                "",
                description="Oracle database version",
                validate_default=True,
            )

            @u.computed_field(return_type=float)
            @property
            def connection_age_seconds(self) -> float:
                """Connection age in seconds."""
                if self.connected:
                    return (u.now() - self.last_activity).total_seconds()
                return 0.0

            @u.computed_field(return_type=str)
            @property
            def connection_info(self) -> str:
                """Connection information summary."""
                if not self.connected:
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

            @u.computed_field(return_type=bool)
            @property
            def healthy(self) -> bool:
                """Connection health status."""
                if not self.connected:
                    return False
                idle_timeout_seconds: float = float(
                    c.DbOracle.CONNECTION_IDLE_TIMEOUT_SECONDS,
                )
                return self.connection_age_seconds <= idle_timeout_seconds

            @u.computed_field(return_type=str)
            @property
            def performance_info(self) -> str:
                """Connection performance information."""
                if not self.connected or self.connection_time <= 0:
                    return "No performance data"
                if (
                    self.connection_time
                    < c.DbOracle.CONNECTION_EXCELLENT_THRESHOLD_SECONDS
                ):
                    return f"Excellent ({self.connection_time:.3f}s)"
                if self.connection_time < c.DbOracle.CONNECTION_GOOD_THRESHOLD_SECONDS:
                    return f"Good ({self.connection_time:.3f}s)"
                if (
                    self.connection_time
                    < c.DbOracle.CONNECTION_ACCEPTABLE_THRESHOLD_SECONDS
                ):
                    return f"Acceptable ({self.connection_time:.3f}s)"
                return f"Slow ({self.connection_time:.3f}s)"

            @u.computed_field(return_type=str)
            @property
            def status_description(self) -> str:
                """Human-readable status description."""
                if self.connected:
                    return "Connected"
                return (
                    f"Disconnected: {self.error_message}"
                    if self.error_message
                    else "Disconnected"
                )

            @u.field_serializer("connection_time", when_used="json")
            def serialize_connection_time(self, value: float) -> str:
                """Format connection time with units."""
                return f"{value:.3f}s"

            @u.field_serializer("last_check", "last_activity", when_used="json")
            def serialize_datetime(self, value: datetime) -> str:
                """Format datetime as ISO string."""
                return value.isoformat()

            @u.field_serializer("error_message")
            def serialize_error_message(self, value: str) -> str:
                """Truncate long error messages."""
                max_error_length = c.DbOracle.MAX_ERROR_MESSAGE_LENGTH
                if len(value) > max_error_length:
                    return f"{value[:max_error_length]}... (truncated)"
                return value

            @u.model_validator(mode="after")
            def validate_connection_status_consistency(
                self,
            ) -> FlextDbOracleModels.DbOracle.ConnectionStatus:
                """Validate connection status consistency."""
                if self.connected and not self.host:
                    msg = "Connected status requires host information"
                    raise ValueError(msg)
                if self.connected and not (
                    c.DbOracle.MIN_PORT <= self.port <= c.DbOracle.MAX_PORT
                ):
                    msg = f"Invalid port number: {self.port}"
                    raise ValueError(msg)
                if self.connection_time < 0:
                    msg = "Connection time cannot be negative"
                    raise ValueError(msg)
                return self

        class QueryResult(m.Entity, m.FlexibleModel):
            """Query result using flext-core Entity."""

            model_config: ClassVar[m.ConfigDict] = m.ConfigDict(frozen=False)

            query: str = u.Field(description="SQL query that produced the result")
            result_data: t.JsonList = u.Field(
                default_factory=tuple,
                description="Raw result data from query execution",
            )
            row_count: t.NonNegativeInt = u.Field(
                0,
                description="Number of rows returned",
                validate_default=True,
            )
            execution_time_ms: t.NonNegativeInt = u.Field(
                0,
                description="Query execution time in milliseconds",
                validate_default=True,
            )

            # Additional Oracle-specific query result details
            columns: t.StrSequence = u.Field(
                default_factory=tuple,
                description="Column names in result set",
            )
            rows: t.SequenceOf[FlextDbOracleModels.DbOracle.RowData] = u.Field(
                default_factory=list[FlextDbOracleModels.DbOracle.RowData],
                description="Typed row data from query result",
            )
            query_hash: str = u.Field(
                "",
                description="Query hash for caching",
                validate_default=True,
            )
            explain_plan: str = u.Field(
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
                    len(self.rows)
                    * len(self.columns)
                    * c.DbOracle.DATA_SIZE_ESTIMATION_FACTOR
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
                    len(self.rows)
                    * len(self.columns)
                    * c.DbOracle.DATA_SIZE_ESTIMATION_FACTOR
                    if self.rows
                    else 0
                )
                return data_size / (1024 * 1024)

            @property
            def performance_rating(self) -> str:
                """Query performance rating."""
                result_acceptance_threshold_ms = (
                    c.DbOracle.QUERY_ACCEPTABLE_THRESHOLD_MS + 500
                )
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

            @u.field_serializer("execution_time_ms", when_used="json")
            def serialize_execution_time(self, value: int) -> str:
                """Format execution time with appropriate units."""
                threshold = c.DbOracle.MILLISECONDS_TO_SECONDS_THRESHOLD
                return (
                    f"{value}ms" if value < threshold else f"{value / threshold:.2f}s"
                )

            @u.model_validator(mode="after")
            def validate_query_result_consistency(
                self,
            ) -> FlextDbOracleModels.DbOracle.QueryResult:
                """Validate query result consistency."""
                if len(self.rows) != self.row_count:
                    self.row_count = len(self.rows)
                if self.rows and self.columns:
                    for row in self.rows:
                        if len(row.values) != len(self.columns):
                            msg = f"Row length {len(row.values)} doesn't match column count {len(self.columns)}"
                            raise ValueError(msg)
                if self.execution_time_ms < 0:
                    msg = "Execution time cannot be negative"
                    raise ValueError(msg)
                return self

        class OperationRecord(m.Entity):
            """Operation tracking record for observability workflows."""

            operation_type: str = u.Field(description="Type of database operation")
            duration: float = u.Field(description="Operation duration in seconds")
            success: bool = u.Field(description="Whether the operation succeeded")
            metadata_info: str = u.Field(
                "",
                description="Operation metadata",
                validate_default=True,
            )
            timestamp: str = u.Field(description="ISO timestamp of operation")

        class HealthStatus(m.Entity):
            """Service health status record."""

            status: str = u.Field(description="Health status indicator")
            timestamp: str = u.Field(description="ISO timestamp of health check")
            service: str = u.Field(
                "oracle",
                description="Service name being checked",
                validate_default=True,
            )
            database: str = u.Field(
                "oracle",
                description="Database engine identifier",
                validate_default=True,
            )
            metrics: t.JsonMapping = u.Field(
                default_factory=lambda: MappingProxyType({}),
                description="Health check metric values",
            )

            def __getitem__(self, key: str) -> t.JsonValue:
                """Get item from health status."""
                if key in self.metrics:
                    return self.metrics[key]
                dump = self.model_dump()
                value = dump.get(key, "")
                return str(value)

            def __contains__(self, key: str) -> bool:
                """Check if key is in health status."""
                if key in self.metrics:
                    return True
                return key in self.model_dump()

        class TableMetadata(m.Entity):
            """Complete table metadata for Oracle introspection."""

            table_name: str = u.Field(description="Oracle table name")
            schema_name: str = u.Field(
                "",
                description="Oracle schema name",
                validate_default=True,
            )
            columns: t.SequenceOf[FlextDbOracleModels.DbOracle.ColumnMetadata] = (
                u.Field(
                    default_factory=list[FlextDbOracleModels.DbOracle.ColumnMetadata],
                    description="Column metadata for the table",
                )
            )
            primary_keys: t.StrSequence = u.Field(
                default_factory=tuple,
                description="Primary key column names",
            )

            def __getitem__(self, key: str) -> t.JsonValue:
                """Get item from table metadata."""
                dump = self.model_dump()
                value = dump.get(key, "")
                return str(value)

            def __contains__(self, key: str) -> bool:
                """Check if key is in table metadata."""
                return key in self.model_dump()

        class TypeMapping(m.Entity):
            """Singer-to-Oracle type mapping."""

            mapping: t.StrMapping = u.Field(
                default_factory=lambda: MappingProxyType({}),
                description="Singer-to-Oracle type conversion map",
            )

            def __getitem__(self, key: str) -> str:
                """Get mapped type for key."""
                value: str = self.mapping[key]
                return value

            def __len__(self) -> int:
                """Get number of type mappings."""
                return len(self.mapping)

            def __contains__(self, key: str) -> bool:
                """Check if key is in type mapping."""
                return key in self.mapping

        class SingerField(m.Entity):
            """Singer field definition."""

            type: str | t.StrSequence = u.Field(
                "string",
                description="Singer JSON Schema type or type array",
                validate_default=True,
            )

        class SingerSchema(m.Entity):
            """Singer schema container with typed properties."""

            properties: t.MappingKV[str, FlextDbOracleModels.DbOracle.SingerField] = (
                u.Field(
                    default_factory=lambda: MappingProxyType({}),
                    description="Singer schema property definitions",
                )
            )

        class Table(m.Entity):
            """Table metadata using flext-core Entity."""

            name: str = u.Field(description="Table name")
            owner: str = u.Field(
                "",
                description="Table owner or schema",
                validate_default=True,
            )
            columns: t.SequenceOf[FlextDbOracleModels.DbOracle.Column] = u.Field(
                default_factory=list[FlextDbOracleModels.DbOracle.Column],
                description="Column definitions for the table",
            )

        class Column(m.Entity):
            """Column metadata using flext-core Entity."""

            name: str = u.Field(description="Column name")
            data_type: str = u.Field(description="Oracle data type")
            nullable: bool = u.Field(
                True,
                description="Whether the column allows NULL values",
                validate_default=True,
            )
            primary_key: bool = u.Field(
                False,
                description="Whether this column is a primary key",
                validate_default=True,
            )
            default_value: str = u.Field(
                "",
                description="Default value for the column",
                validate_default=True,
            )

            def __getitem__(self, key: str) -> t.JsonValue:
                """Get item from column metadata."""
                key_map: t.JsonMapping = {
                    "column_name": self.name,
                    "name": self.name,
                    "data_type": self.data_type,
                    "nullable": self.nullable,
                    "primary_key": self.primary_key,
                    "default_value": self.default_value,
                }
                if key in key_map:
                    return key_map[key]
                return ""

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

        class Schema(m.Entity):
            """Schema metadata using flext-core Entity."""

            name: str = u.Field(description="Schema name")
            tables: t.SequenceOf[FlextDbOracleModels.DbOracle.Table] = u.Field(
                default_factory=list[FlextDbOracleModels.DbOracle.Table],
                description="Tables within this schema",
            )

        class CreateIndexConfig(m.Entity):
            """Create index settings using flext-core Entity."""

            table_name: str = u.Field(description="Target table for the index")
            index_name: str = u.Field(description="Name of the index to create")
            columns: t.StrSequence = u.Field(
                description="Columns to include in the index",
            )
            unique: bool = u.Field(
                False,
                description="Whether the index enforces uniqueness",
                validate_default=True,
            )
            schema_name: str = u.Field(
                "",
                description="Schema name",
                validate_default=True,
            )
            tablespace: str = u.Field(
                "",
                description="Tablespace name",
                validate_default=True,
            )
            parallel: t.PositiveInt = u.Field(
                1,
                description="Parallel degree for index creation",
                validate_default=True,
            )

        # Command classes for dispatcher integration
        class ConnectCommand(m.Entity):
            """Command to establish Oracle connection."""

        class DisconnectCommand(m.Entity):
            """Command to close Oracle connection."""

        class TestConnectionCommand(m.Entity):
            """Command to test Oracle connection."""

        class ExecuteQueryCommand(m.Entity):
            """Command to execute SELECT query."""

            sql: str = u.Field(description="SQL SELECT query to execute")
            parameters: t.JsonMapping | None = u.Field(
                None,
                description="Query bind parameters",
                validate_default=True,
            )

        class FetchOneCommand(m.Entity):
            """Command to fetch single row."""

            sql: str = u.Field(description="SQL query to fetch a single row")
            parameters: t.JsonMapping | None = u.Field(
                None,
                description="Query bind parameters",
                validate_default=True,
            )

        class ExecuteStatementCommand(m.Entity):
            """Command to execute INSERT/UPDATE/DELETE."""

            sql: str = u.Field(description="SQL DML statement to execute")
            parameters: t.JsonMapping | None = u.Field(
                None,
                description="Statement bind parameters",
                validate_default=True,
            )

        class ExecuteManyCommand(m.Entity):
            """Command to execute batch statements."""

            sql: str = u.Field(description="SQL statement for batch execution")
            parameters_list: t.SequenceOf[t.JsonMapping] = u.Field(
                default_factory=list[t.JsonMapping],
                description="List of parameter sets for batch execution",
            )

        class GetSchemasCommand(m.Entity):
            """Command to retrieve all schemas."""

        class GetTablesCommand(m.Entity):
            """Command to retrieve tables in schema."""

            schema_name: str | None = u.Field(
                None,
                description="Schema to list tables from",
                validate_default=True,
            )

        class GetColumnsCommand(m.Entity):
            """Command to retrieve columns in table."""

            table: str = u.Field(description="Table to retrieve columns from")
            schema_name: str | None = u.Field(
                None,
                description="Schema containing the table",
                validate_default=True,
            )


m = FlextDbOracleModels

__all__: list[str] = [
    "FlextDbOracleModels",
    "m",
]
