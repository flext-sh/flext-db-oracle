"""Oracle database Pydantic models following Flext[Area][Module] pattern.

This module contains Oracle-specific models using modern patterns from flext-core.
Single class inheriting from FlextModel with all Oracle model functionality
as internal classes, following SOLID principles, PEP8, Python 3.13+, and FLEXT
structural patterns.

This class consolidates all Oracle model functionality into a single entry
point with internal organization.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import TypedDict, TypeGuard, cast

from flext_core import (
    FlextLogger,
    FlextModel,
)
from pydantic import Field, SecretStr, field_validator, model_validator
from pydantic_settings import SettingsConfigDict

from flext_db_oracle.constants import (
    FlextDbOracleConstants,
    FlextOracleDbSemanticConstants,
)

# Python 3.13+ type aliases (replacing TypeVar pattern)
type T = object

logger = FlextLogger(__name__)

# Constants
MAX_PORT_NUMBER = 65535  # Maximum valid TCP port number

# =============================================================================
# FLEXT[AREA][MODULE] PATTERN - Oracle Database Models
# =============================================================================


class FlextDbOracleModels:
    """Oracle database models following Flext[Area][Module] pattern.

    Single consolidated class with all Oracle model functionality
    as internal classes, following SOLID principles,
    PEP8, Python 3.13+, and FLEXT structural patterns.

    This class consolidates all Oracle model functionality
    into a single entry point with internal organization.
    """

    class Column(FlextModel):
        """Oracle database column model with complete metadata."""

        column_name: str = Field(..., description="Column name")
        data_type: str = Field(..., description="Oracle data type")
        nullable: bool = Field(default=True, description="Column nullable flag")
        data_length: int | None = Field(
            None, description="Data length for character types"
        )
        data_precision: int | None = Field(None, description="Numeric precision")
        data_scale: int | None = Field(None, description="Numeric scale")
        column_id: int = Field(..., description="Column position/ID")
        default_value: str | None = Field(None, description="Default value")
        comments: str | None = Field(None, description="Column comments")

        @field_validator("column_name")
        @classmethod
        def validate_column_name(cls, v: str) -> str:
            """Validate column name."""
            if not v or not isinstance(v, str) or not v.strip():
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
            if not v or not isinstance(v, str) or not v.strip():
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

        @field_validator("data_scale")
        @classmethod
        def validate_data_scale(cls, v: int | None) -> int | None:
            """Validate data scale."""
            if v is not None and v < 0:
                msg = "Data scale cannot be negative"
                raise ValueError(msg)
            return v

        def to_oracle_ddl(self) -> str:
            """Generate Oracle DDL for column definition."""
            ddl_parts = [self.column_name, self.data_type]

            if self.data_type in {"VARCHAR2", "CHAR", "NVARCHAR2", "NCHAR"}:
                if self.data_length:
                    ddl_parts[1] = f"{self.data_type}({self.data_length})"
            elif self.data_type == "NUMBER":
                if self.data_precision and self.data_scale is not None:
                    ddl_parts[1] = f"NUMBER({self.data_precision},{self.data_scale})"
                elif self.data_precision:
                    ddl_parts[1] = f"NUMBER({self.data_precision})"

            if not self.nullable:
                ddl_parts.append("NOT NULL")

            if self.default_value:
                ddl_parts.append(f"DEFAULT {self.default_value}")

            return " ".join(ddl_parts)

        def is_numeric(self) -> bool:
            """Check if column is numeric type."""
            return self.data_type in {
                "NUMBER",
                "INTEGER",
                "FLOAT",
                "BINARY_DOUBLE",
                "BINARY_FLOAT",
            }

        def is_character(self) -> bool:
            """Check if column is character type."""
            return self.data_type in {
                "VARCHAR2",
                "CHAR",
                "NVARCHAR2",
                "NCHAR",
                "CLOB",
                "NCLOB",
            }

        def is_datetime(self) -> bool:
            """Check if column is date/time type."""
            return self.data_type in {
                "DATE",
                "TIMESTAMP",
                "TIMESTAMP WITH TIME ZONE",
                "TIMESTAMP WITH LOCAL TIME ZONE",
            }

    class Table(FlextModel):
        """Oracle database table model with metadata and relationships."""

        table_name: str = Field(..., description="Table name")
        schema_name: str = Field(default="", description="Schema name")
        columns: list[FlextDbOracleModels.Column] = Field(
            default_factory=list, description="Table columns"
        )
        row_count: int | None = Field(None, description="Approximate row count")
        created_date: datetime | None = Field(None, description="Table creation date")
        last_analyzed: datetime | None = Field(
            None, description="Last statistics analysis date"
        )
        table_type: str = Field(
            default="TABLE", description="Table type (TABLE, VIEW, etc.)"
        )
        comments: str | None = Field(None, description="Table comments")

        @field_validator("table_name")
        @classmethod
        def validate_table_name(cls, v: str) -> str:
            """Validate table name."""
            if not v or not isinstance(v, str) or not v.strip():
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
            if (
                v
                and len(v)
                > FlextDbOracleConstants.OracleValidation.MAX_SCHEMA_NAME_LENGTH
            ):
                msg = f"Schema name exceeds maximum length of {FlextDbOracleConstants.OracleValidation.MAX_SCHEMA_NAME_LENGTH}"
                raise ValueError(msg)
            return v.upper() if v else ""

        def get_full_name(self) -> str:
            """Get fully qualified table name."""
            if self.schema_name:
                return f"{self.schema_name}.{self.table_name}"
            return self.table_name

        def get_primary_key_columns(self) -> list[FlextDbOracleModels.Column]:
            """Get primary key columns (placeholder - requires constraint metadata)."""
            # This would require additional constraint metadata in a real implementation
            return []

        def get_column_by_name(
            self, column_name: str
        ) -> FlextDbOracleModels.Column | None:
            """Get column by name."""
            for column in self.columns:
                if column.column_name.upper() == column_name.upper():
                    return column
            return None

        def get_numeric_columns(self) -> list[FlextDbOracleModels.Column]:
            """Get all numeric columns."""
            return [col for col in self.columns if col.is_numeric()]

        def get_character_columns(self) -> list[FlextDbOracleModels.Column]:
            """Get all character columns."""
            return [col for col in self.columns if col.is_character()]

        def get_datetime_columns(self) -> list[FlextDbOracleModels.Column]:
            """Get all datetime columns."""
            return [col for col in self.columns if col.is_datetime()]

    class Schema(FlextModel):
        """Oracle database schema model with tables and metadata."""

        schema_name: str = Field(..., description="Schema name")
        tables: list[FlextDbOracleModels.Table] = Field(
            default_factory=list, description="Tables in schema"
        )
        created_date: datetime | None = Field(None, description="Schema creation date")
        default_tablespace: str | None = Field(None, description="Default tablespace")
        temporary_tablespace: str | None = Field(
            None, description="Temporary tablespace"
        )
        profile: str | None = Field(None, description="User profile")
        account_status: str = Field(default="OPEN", description="Account status")

        @field_validator("schema_name")
        @classmethod
        def validate_schema_name(cls, v: str) -> str:
            """Validate schema name."""
            if not v or not isinstance(v, str) or not v.strip():
                msg = FlextDbOracleConstants.ErrorMessages.SCHEMA_NAME_EMPTY
                raise ValueError(msg)
            if len(v) > FlextDbOracleConstants.OracleValidation.MAX_SCHEMA_NAME_LENGTH:
                msg = f"Schema name exceeds maximum length of {FlextDbOracleConstants.OracleValidation.MAX_SCHEMA_NAME_LENGTH}"
                raise ValueError(msg)
            return v.upper()

        def get_table_by_name(
            self, table_name: str
        ) -> FlextDbOracleModels.Table | None:
            """Get table by name."""
            for table in self.tables:
                if table.table_name.upper() == table_name.upper():
                    return table
            return None

        def get_table_count(self) -> int:
            """Get count of tables in schema."""
            return len(self.tables)

        def get_total_columns(self) -> int:
            """Get total number of columns across all tables."""
            return sum(len(table.columns) for table in self.tables)

    class QueryResult(FlextModel):
        """Oracle query result model with execution metadata."""

        columns: list[str] = Field(default_factory=list, description="Column names")
        rows: list[tuple[object, ...]] = Field(
            default_factory=list, description="Result rows"
        )
        row_count: int = Field(default=0, description="Number of rows returned")
        execution_time_ms: float = Field(
            default=0.0, description="Query execution time in milliseconds"
        )
        query_hash: str | None = Field(None, description="Query hash for caching")
        explain_plan: str | None = Field(None, description="Query execution plan")

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

        def to_dict_list(self) -> list[dict[str, object]]:
            """Convert result to list of dictionaries."""
            if not self.columns:
                return []

            result = []
            for row in self.rows:
                row_dict = {}
                for i, column in enumerate(self.columns):
                    row_dict[column] = row[i] if i < len(row) else None
                result.append(row_dict)
            return result

        def get_column_index(self, column_name: str) -> int | None:
            """Get index of column by name."""
            try:
                return self.columns.index(column_name)
            except ValueError:
                return None

        def get_column_values(self, column_name: str) -> list[object]:
            """Get all values for a specific column."""
            column_index = self.get_column_index(column_name)
            if column_index is None:
                return []

            return [
                row[column_index] if column_index < len(row) else None
                for row in self.rows
            ]

        def is_empty(self) -> bool:
            """Check if result is empty."""
            return self.row_count == 0

    class ConnectionStatus(FlextModel):
        """Oracle database connection status model."""

        is_connected: bool = Field(default=False, description="Connection status")
        connection_time: datetime | None = Field(
            None, description="Connection timestamp"
        )
        last_activity: datetime | None = Field(
            None, description="Last activity timestamp"
        )
        session_id: str | None = Field(None, description="Oracle session ID")
        host: str | None = Field(None, description="Database host")
        port: int | None = Field(None, description="Database port")
        service_name: str | None = Field(None, description="Oracle service name")
        username: str | None = Field(None, description="Database username")
        version: str | None = Field(None, description="Oracle database version")
        error_message: str | None = Field(None, description="Connection error message")

        @field_validator("port")
        @classmethod
        def validate_port(cls, v: int | None) -> int | None:
            """Validate port number."""
            if v is not None and not (1 <= v <= MAX_PORT_NUMBER):
                msg = FlextDbOracleConstants.ErrorMessages.PORT_INVALID
                raise ValueError(msg)
            return v

        def get_connection_string_safe(self) -> str:
            """Get connection string without password."""
            if not all([self.host, self.port, self.service_name]):
                return "Connection details incomplete"

            return f"{self.username}@{self.host}:{self.port}/{self.service_name}"

        def get_uptime_seconds(self) -> float | None:
            """Get connection uptime in seconds."""
            if not self.connection_time:
                return None

            current_time = self.last_activity or datetime.now(UTC)
            uptime = current_time - self.connection_time
            return uptime.total_seconds()

        def is_active(self) -> bool:
            """Check if connection is active and healthy."""
            return self.is_connected and self.error_message is None

    # =============================================================================
    # ORACLE CONFIGURATION MODELS - Consolidated from config.py
    # =============================================================================

    class OracleConfig(FlextModel):
        """Oracle database configuration extending flext-core centralized config."""

        # Core Oracle connection fields
        host: str = Field(description="Oracle database hostname")
        port: int = Field(default=1521, description="Oracle database port")
        username: str = Field(description="Oracle database username")
        password: SecretStr = Field(description="Oracle database password")
        service_name: str | None = Field(
            default=None, description="Oracle service name"
        )
        sid: str | None = Field(default=None, description="Oracle SID")
        oracle_schema: str = Field(default="PUBLIC", description="Oracle schema name")

        # Connection pool settings
        pool_min: int = Field(default=1, description="Minimum pool connections")
        pool_max: int = Field(default=10, description="Maximum pool connections")
        pool_increment: int = Field(default=1, description="Connection pool increment")

        # Additional Oracle-specific options
        ssl_enabled: bool = Field(default=False, description="Enable SSL connections")
        ssl_cert_path: str | None = Field(
            default=None, description="SSL certificate path"
        )
        ssl_key_path: str | None = Field(default=None, description="SSL key path")
        ssl_server_dn_match: bool = Field(
            default=True, description="SSL server DN match"
        )
        ssl_server_cert_dn: str | None = Field(
            None, description="SSL server certificate DN"
        )
        timeout: int = Field(default=30, description="Connection timeout seconds")
        encoding: str = Field(default="UTF-8", description="Character encoding")
        protocol: str = Field(default="tcp", description="Connection protocol")
        autocommit: bool = Field(default=False, description="Enable autocommit mode")
        retry_attempts: int = Field(
            default=1, description="Number of connection retry attempts"
        )
        retry_delay: float = Field(
            default=1.0, description="Delay between retry attempts in seconds"
        )

        # BaseSettings configuration for automatic environment loading
        model_config = SettingsConfigDict(
            env_prefix="FLEXT_TARGET_ORACLE_", env_file=".env"
        )

        @field_validator("host")
        @classmethod
        def validate_host_not_empty(cls, v: str) -> str:
            """Validate host is not empty or whitespace only."""
            if not v or not isinstance(v, str) or not v.strip():
                raise ValueError(
                    FlextOracleDbSemanticConstants.ErrorMessages.HOST_EMPTY
                )
            return v

        @field_validator("username")
        @classmethod
        def validate_username_not_empty(cls, v: str) -> str:
            """Validate username is not empty or whitespace only."""
            if not v or not isinstance(v, str) or not v.strip():
                raise ValueError(
                    FlextOracleDbSemanticConstants.ErrorMessages.USERNAME_EMPTY
                )
            return v

        @field_validator("port")
        @classmethod
        def validate_port_range(cls, v: int) -> int:
            """Validate port is within valid range."""
            max_port_number = 65535
            if not (1 <= v <= max_port_number):
                msg = f"Port must be between 1 and {max_port_number}"
                raise ValueError(msg)
            return v

        @field_validator("password", mode="before")
        @classmethod
        def coerce_password(cls, v: object) -> SecretStr:
            """Coerce incoming password to SecretStr for compatibility."""
            if isinstance(v, SecretStr):
                return v
            return SecretStr(str(v))

        @model_validator(mode="after")
        def validate_pool_settings(self) -> FlextDbOracleModels.OracleConfig:
            """Validate pool configuration consistency."""
            if self.pool_max < self.pool_min:
                msg = "pool_max must be >= pool_min"
                raise ValueError(msg)
            return self

        @model_validator(mode="after")
        def validate_connection_identifiers(self) -> FlextDbOracleModels.OracleConfig:
            """Validate that either SID or service_name is provided."""
            if not self.sid and not self.service_name:
                msg = "Either SID or service_name must be provided"
                raise ValueError(msg)
            return self

        @classmethod
        def from_env(cls) -> FlextDbOracleModels.OracleConfig:
            """Create configuration from environment variables."""
            return cls(
                host=os.getenv("FLEXT_TARGET_ORACLE_HOST", "localhost"),
                port=int(os.getenv("FLEXT_TARGET_ORACLE_PORT", "1521")),
                username=os.getenv("FLEXT_TARGET_ORACLE_USERNAME", "system"),
                password=SecretStr(os.getenv("FLEXT_TARGET_ORACLE_PASSWORD", "oracle")),
                service_name=os.getenv("FLEXT_TARGET_ORACLE_SERVICE_NAME", "XEPDB1"),
                ssl_server_cert_dn=os.getenv("FLEXT_TARGET_ORACLE_SSL_CERT_DN"),
            )

        def get_connection_string(self) -> str:
            """Get Oracle connection string for logging purposes."""
            if self.service_name:
                return f"{self.host}:{self.port}/{self.service_name}"
            if self.sid:
                return f"{self.host}:{self.port}:{self.sid}"
            return f"{self.host}:{self.port}"

    # =============================================================================
    # CONFIGURATION TYPES - Consolidated from config_types.py
    # =============================================================================

    @dataclass
    class MergeStatement:
        """Configuration for Oracle MERGE statement generation."""

        target_table: str
        source_columns: list[str]
        merge_keys: list[str]
        update_columns: list[str] | None = None
        insert_columns: list[str] | None = None
        schema_name: str | None = None
        hints: list[str] | None = None

    @dataclass
    class CreateIndex:
        """Configuration for Oracle CREATE INDEX statement generation."""

        index_name: str
        table_name: str
        columns: list[str]
        unique: bool = False
        schema_name: str | None = None
        tablespace: str | None = None
        parallel: int | None = None

    # =============================================================================
    # ORACLE TYPINGS - Consolidated from typings.py
    # =============================================================================

    class OracleColumnInfo(TypedDict, total=False):
        """TypedDict for Oracle column information from database queries."""

        column_name: str
        data_type: str
        nullable: bool
        data_length: int | None
        data_precision: int | None
        data_scale: int | None
        column_id: int
        default_value: str | None
        comments: str | None

    class OracleConnectionInfo(TypedDict, total=False):
        """TypedDict for Oracle connection information."""

        host: str
        port: int
        service_name: str
        username: str
        password: str
        charset: str | None
        pool_min: int | None
        pool_max: int | None
        connect_timeout: int | None

    class OracleTableInfo(TypedDict, total=False):
        """TypedDict for Oracle table information from database queries."""

        table_name: str
        schema_name: str
        tablespace_name: str | None
        table_comment: str | None
        column_count: int | None
        row_count: int | None
        created_date: str | None
        last_analyzed: str | None

    # Type aliases
    type DatabaseRowProtocol = dict[str, object]
    type DatabaseRowDict = dict[str, object]
    type SafeStringList = list[str]
    type PluginLikeProtocol = object  # Simplified without non-existent FlextProtocols

    # =============================================================================
    # FIELD DEFINITIONS - Consolidated from fields.py
    # =============================================================================

    # Connection fields
    host_field = Field(
        ..., description="Oracle database host", min_length=1, max_length=255
    )
    port_field = Field(
        default=1521, description="Oracle database port number", ge=1, le=65535
    )
    service_name_field = Field(
        default="XE",
        description="Oracle service name or SID",
        min_length=1,
        max_length=128,
    )
    username_field = Field(
        ..., description="Database username", min_length=1, max_length=128
    )
    password_field = Field(
        ..., description="Database password", min_length=1, max_length=256, repr=False
    )

    # Metadata fields
    schema_name_field = Field(
        ..., description="Database schema name", min_length=1, max_length=128
    )
    table_name_field = Field(
        ..., description="Database table name", min_length=1, max_length=128
    )
    column_name_field = Field(
        ..., description="Database column name", min_length=1, max_length=128
    )

    # =============================================================================
    # TYPE GUARDS AND UTILITIES
    # =============================================================================

    @staticmethod
    def is_plugin_like(obj: object) -> TypeGuard[object]:
        """Type guard to check if object has plugin-like attributes."""
        return (
            hasattr(obj, "name")
            and hasattr(obj, "version")
            and hasattr(obj, "get_info")
            and callable(getattr(obj, "get_info", None))
        )

    @staticmethod
    def is_dict_like(obj: object) -> TypeGuard[dict[str, object]]:
        """Type guard for dict-like objects."""
        return hasattr(obj, "get") and hasattr(obj, "items") and hasattr(obj, "keys")

    @staticmethod
    def is_string_list(obj: object) -> TypeGuard[SafeStringList]:
        """Type guard for list of strings."""
        return isinstance(obj, list) and all(isinstance(item, str) for item in obj)

    @staticmethod
    def has_get_info_method(obj: object) -> TypeGuard[object]:
        """Type guard for objects with get_info method."""
        return hasattr(obj, "get_info") and callable(getattr(obj, "get_info", None))

    @staticmethod
    def is_result_like(obj: object) -> TypeGuard[object]:
        """Type guard for FlextResult-like objects."""
        return (
            hasattr(obj, "success") and hasattr(obj, "error") and hasattr(obj, "value")
        )

    # =============================================================================
    # Factory Methods for Model Creation
    # =============================================================================

    @classmethod
    def create_column(
        cls,
        column_name: str,
        data_type: str,
        *,
        nullable: bool = True,
        column_id: int = 1,
        **kwargs: object,
    ) -> Column:
        """Create Oracle column model using factory pattern."""
        # Extract known fields from kwargs with proper type casting
        data_length = kwargs.pop("data_length", None)
        data_precision = kwargs.pop("data_precision", None)
        data_scale = kwargs.pop("data_scale", None)
        default_value = kwargs.pop("default_value", None)
        comments = kwargs.pop("comments", None)

        # Type casting for MyPy with proper type checks
        data_length_typed = (
            int(data_length) if isinstance(data_length, (int, str)) else None
        )
        data_precision_typed = (
            int(data_precision) if isinstance(data_precision, (int, str)) else None
        )
        data_scale_typed = (
            int(data_scale) if isinstance(data_scale, (int, str)) else None
        )
        default_value_typed = str(default_value) if default_value is not None else None
        comments_typed = str(comments) if comments is not None else None

        return cls.Column(
            column_name=column_name,
            data_type=data_type,
            nullable=nullable,
            column_id=column_id,
            data_length=data_length_typed,
            data_precision=data_precision_typed,
            data_scale=data_scale_typed,
            default_value=default_value_typed,
            comments=comments_typed,
        )

    @classmethod
    def create_table(
        cls,
        table_name: str,
        *,
        schema_name: str = "",
        columns: list[Column] | None = None,
        **kwargs: object,
    ) -> Table:
        """Create Oracle table model using factory pattern."""
        # Extract known fields from kwargs with proper type casting
        row_count = kwargs.pop("row_count", None)
        created_date = kwargs.pop("created_date", None)
        last_analyzed = kwargs.pop("last_analyzed", None)
        table_type = kwargs.pop("table_type", "TABLE")
        comments = kwargs.pop("comments", None)

        # Type casting for MyPy with proper type checks
        row_count_typed = int(row_count) if isinstance(row_count, (int, str)) else None
        created_date_typed = (
            created_date if isinstance(created_date, datetime) else None
        )
        last_analyzed_typed = (
            last_analyzed if isinstance(last_analyzed, datetime) else None
        )
        table_type_typed = str(table_type) if table_type is not None else "TABLE"
        comments_typed = str(comments) if comments is not None else None

        return cls.Table(
            table_name=table_name,
            schema_name=schema_name,
            columns=columns or [],
            row_count=row_count_typed,
            created_date=created_date_typed,
            last_analyzed=last_analyzed_typed,
            table_type=table_type_typed,
            comments=comments_typed,
        )

    @classmethod
    def create_schema(
        cls,
        schema_name: str,
        *,
        tables: list[Table] | None = None,
        **kwargs: object,
    ) -> Schema:
        """Create Oracle schema model using factory pattern."""
        # Extract known fields from kwargs with proper type casting
        created_date = kwargs.pop("created_date", None)
        default_tablespace = kwargs.pop("default_tablespace", None)
        temporary_tablespace = kwargs.pop("temporary_tablespace", None)
        profile = kwargs.pop("profile", None)
        account_status = kwargs.pop("account_status", "OPEN")

        # Type casting for MyPy
        created_date_typed = (
            created_date if isinstance(created_date, datetime) else None
        )
        default_tablespace_typed = (
            str(default_tablespace) if default_tablespace is not None else None
        )
        temporary_tablespace_typed = (
            str(temporary_tablespace) if temporary_tablespace is not None else None
        )
        profile_typed = str(profile) if profile is not None else None
        account_status_typed = (
            str(account_status) if account_status is not None else "OPEN"
        )

        return cls.Schema(
            schema_name=schema_name,
            tables=tables or [],
            created_date=created_date_typed,
            default_tablespace=default_tablespace_typed,
            temporary_tablespace=temporary_tablespace_typed,
            profile=profile_typed,
            account_status=account_status_typed,
        )

    @classmethod
    def create_query_result(
        cls,
        *,
        columns: list[str] | None = None,
        rows: list[tuple[object, ...]] | None = None,
        execution_time_ms: float = 0.0,
        **kwargs: object,
    ) -> QueryResult:
        """Create Oracle query result model using factory pattern."""
        columns = columns or []
        rows = rows or []

        # Extract known fields from kwargs with proper type casting
        query_hash = kwargs.pop("query_hash", None)
        explain_plan = kwargs.pop("explain_plan", None)

        # Type casting for MyPy
        query_hash_typed = str(query_hash) if query_hash is not None else None
        explain_plan_typed = str(explain_plan) if explain_plan is not None else None

        return cls.QueryResult(
            columns=columns,
            rows=rows,
            row_count=len(rows),
            execution_time_ms=execution_time_ms,
            query_hash=query_hash_typed,
            explain_plan=explain_plan_typed,
        )

    @classmethod
    def create_connection_status(
        cls,
        *,
        is_connected: bool = False,
        **kwargs: object,
    ) -> ConnectionStatus:
        """Create Oracle connection status model using factory pattern."""
        # Extract known fields from kwargs with proper type casting
        connection_time = kwargs.pop("connection_time", None)
        last_activity = kwargs.pop("last_activity", None)
        session_id = kwargs.pop("session_id", None)
        host = kwargs.pop("host", None)
        port = kwargs.pop("port", None)
        service_name = kwargs.pop("service_name", None)
        username = kwargs.pop("username", None)
        version = kwargs.pop("version", None)
        error_message = kwargs.pop("error_message", None)

        # Type casting for MyPy with proper type checks
        connection_time_typed = (
            connection_time if isinstance(connection_time, datetime) else None
        )
        last_activity_typed = (
            last_activity if isinstance(last_activity, datetime) else None
        )
        session_id_typed = str(session_id) if session_id is not None else None
        host_typed = str(host) if host is not None else None
        port_typed = int(port) if isinstance(port, (int, str)) else None
        service_name_typed = str(service_name) if service_name is not None else None
        username_typed = str(username) if username is not None else None
        version_typed = str(version) if version is not None else None
        error_message_typed = str(error_message) if error_message is not None else None

        return cls.ConnectionStatus(
            is_connected=is_connected,
            connection_time=connection_time_typed,
            last_activity=last_activity_typed,
            session_id=session_id_typed,
            host=host_typed,
            port=port_typed,
            service_name=service_name_typed,
            username=username_typed,
            version=version_typed,
            error_message=error_message_typed,
        )

    @classmethod
    def create_oracle_config(
        cls,
        *,
        host: str,
        username: str,
        password: str,
        **kwargs: object,
    ) -> OracleConfig:
        """Create Oracle configuration model using factory pattern."""
        # Extract optional fields with type casting
        port = kwargs.pop("port", 1521)
        service_name = kwargs.pop("service_name", None)
        sid = kwargs.pop("sid", None)

        config_data = {
            "host": host,
            "port": int(port) if isinstance(port, (int, str)) else 1521,
            "username": username,
            "password": SecretStr(str(password)),
        }

        if service_name:
            config_data["service_name"] = str(service_name)
        if sid:
            config_data["sid"] = str(sid)

        # Add any additional kwargs
        config_data.update({
            key: value
            for key, value in kwargs.items()
            if hasattr(cls.OracleConfig, key)
        })

        return cls.OracleConfig.model_validate(config_data)

    @classmethod
    def create_merge_config(
        cls,
        target_table: str,
        source_columns: list[str],
        merge_keys: list[str],
        **kwargs: object,
    ) -> MergeStatement:
        """Create MERGE statement configuration."""
        return cls.MergeStatement(
            target_table=target_table,
            source_columns=source_columns,
            merge_keys=merge_keys,
            update_columns=cast("list[str] | None", kwargs.get("update_columns"))
            if isinstance(kwargs.get("update_columns"), list)
            else None,
            insert_columns=cast("list[str] | None", kwargs.get("insert_columns"))
            if isinstance(kwargs.get("insert_columns"), list)
            else None,
            schema_name=cast("str | None", kwargs.get("schema_name"))
            if isinstance(kwargs.get("schema_name"), str)
            else None,
            hints=cast("list[str] | None", kwargs.get("hints"))
            if isinstance(kwargs.get("hints"), list)
            else None,
        )

    @classmethod
    def create_index_config(
        cls,
        index_name: str,
        table_name: str,
        columns: list[str],
        **kwargs: object,
    ) -> CreateIndex:
        """Create CREATE INDEX configuration."""
        return cls.CreateIndex(
            index_name=index_name,
            table_name=table_name,
            columns=columns,
            unique=bool(kwargs.get("unique")),
            schema_name=cast("str | None", kwargs.get("schema_name"))
            if isinstance(kwargs.get("schema_name"), str)
            else None,
            tablespace=cast("str | None", kwargs.get("tablespace"))
            if isinstance(kwargs.get("tablespace"), str)
            else None,
            parallel=cast("int | None", kwargs.get("parallel"))
            if isinstance(kwargs.get("parallel"), int)
            else None,
        )

    # =============================================================================
    # Backward Compatibility Aliases
    # =============================================================================

    # Maintain existing functionality as aliases
    FlextDbOracleColumn = Column
    FlextDbOracleTable = Table
    FlextDbOracleSchema = Schema
    FlextDbOracleQueryResult = QueryResult
    FlextDbOracleConnectionStatus = ConnectionStatus
    FlextDbOracleConfig = OracleConfig
    MergeStatementConfig = MergeStatement
    CreateIndexConfig = CreateIndex


# Export API - ONLY single class with backward compatibility
__all__: list[str] = [
    # Backward compatibility exports - Fields (deprecated)
    "ConnectionFields",
    "CreateIndexConfig",
    "DatabaseMetadataFields",
    "DatabaseRowDict",
    # Backward compatibility exports - Database models
    "FlextDbOracleColumn",
    # Backward compatibility exports - Configuration
    "FlextDbOracleConfig",
    "FlextDbOracleConnectionStatus",
    # Main consolidated class
    "FlextDbOracleModels",
    "FlextDbOracleQueryResult",
    "FlextDbOracleSchema",
    "FlextDbOracleTable",
    "MergeStatementConfig",
    # Backward compatibility exports - Types
    "OracleColumnInfo",
    "OracleConnectionInfo",
    "OracleTableInfo",
    "PluginLikeProtocol",
    "QueryFields",
    "SafeStringList",
    "ValidationFields",
]

# Create backward compatibility module-level aliases
FlextDbOracleColumn = FlextDbOracleModels.Column
FlextDbOracleTable = FlextDbOracleModels.Table
FlextDbOracleSchema = FlextDbOracleModels.Schema
FlextDbOracleQueryResult = FlextDbOracleModels.QueryResult
FlextDbOracleConnectionStatus = FlextDbOracleModels.ConnectionStatus
FlextDbOracleConfig = FlextDbOracleModels.OracleConfig
MergeStatementConfig = FlextDbOracleModels.MergeStatement
CreateIndexConfig = FlextDbOracleModels.CreateIndex

# Type aliases
OracleColumnInfo = FlextDbOracleModels.OracleColumnInfo
OracleConnectionInfo = FlextDbOracleModels.OracleConnectionInfo
OracleTableInfo = FlextDbOracleModels.OracleTableInfo
DatabaseRowDict = FlextDbOracleModels.DatabaseRowDict
SafeStringList = FlextDbOracleModels.SafeStringList
PluginLikeProtocol = FlextDbOracleModels.PluginLikeProtocol


# Fields backward compatibility (deprecated - use models directly)
class ConnectionFields:
    """Deprecated: Use FlextDbOracleModels directly."""

    def __getattr__(self, name: str) -> object:
        """Deprecated attribute access."""
        return getattr(FlextDbOracleModels, f"{name}_field", None)


class DatabaseMetadataFields:
    """Deprecated: Use FlextDbOracleModels directly."""

    def __getattr__(self, name: str) -> object:
        """Deprecated attribute access."""
        return getattr(FlextDbOracleModels, f"{name}_field", None)


class QueryFields:
    """Deprecated: Use FlextDbOracleModels directly."""

    def __getattr__(self, name: str) -> object:
        """Deprecated attribute access."""
        return getattr(FlextDbOracleModels, f"{name}_field", None)


class ValidationFields:
    """Deprecated: Use FlextDbOracleModels directly."""

    def __getattr__(self, name: str) -> object:
        """Deprecated attribute access."""
        return getattr(FlextDbOracleModels, f"{name}_field", None)
