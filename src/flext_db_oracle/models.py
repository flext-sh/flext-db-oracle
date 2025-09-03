"""Oracle database Pydantic models following Flext[Area][Module] pattern.

This module contains Oracle-specific models using modern patterns from flext-core.
Single class inheriting from FlextModels with all Oracle model functionality
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
from datetime import datetime
from typing import TypedDict, TypeGuard

from flext_core import (
    FlextLogger,
    FlextModels,
    FlextResult,
    FlextUtilities,
)
from pydantic import Field, SecretStr, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from flext_db_oracle.constants import FlextDbOracleConstants

# Python 3.13+ type aliases (replacing TypeVar pattern)
type T = object

logger = FlextLogger(__name__)

# No loose constants - use FlextDbOracleConstants directly

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

    class Column(FlextModels.Value):
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

        @classmethod
        def _is_safe_sql_identifier(cls, identifier: str) -> bool:
            """Validate SQL identifier to prevent injection."""
            if not identifier or not isinstance(identifier, str):
                return False

            # Oracle identifiers: alphanumeric, underscore, dollar sign, hash
            # First character must be letter or underscore
            # Max length 128 characters (Oracle standard)
            max_identifier_length = 128
            if len(identifier) > max_identifier_length:
                return False

            # Check first character
            if not (identifier[0].isalpha() or identifier[0] == "_"):
                return False

            # Check remaining characters
            for char in identifier[1:]:
                if not (char.isalnum() or char in ("_", "$", "#")):
                    return False

            # Prevent SQL keywords (basic set)
            reserved_words = {
                "SELECT", "INSERT", "UPDATE", "DELETE", "DROP", "CREATE",
                "ALTER", "TRUNCATE", "GRANT", "REVOKE", "UNION", "ORDER",
                "GROUP", "HAVING", "WHERE", "FROM", "INTO", "VALUES"
            }

            return identifier.upper() not in reserved_words

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

            # Oracle SQL identifier validation (comprehensive security check)
            if not cls._is_safe_sql_identifier(v):
                msg = f"Invalid column name '{v}': contains unsafe characters or is a reserved word"
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

        def validate_business_rules(self) -> FlextResult[None]:
            """Validate Oracle column business rules."""
            # Column name validation
            if not self.column_name or not self.column_name.strip():
                return FlextResult[None].fail("Column name cannot be empty")

            # Data type validation
            if not self.data_type:
                return FlextResult[None].fail("Data type cannot be empty")

            # Precision and scale validation for numeric types
            if self.is_numeric():
                if self.data_precision and self.data_precision < 0:
                    return FlextResult[None].fail("Data precision cannot be negative")
                if self.data_scale and self.data_scale < 0:
                    return FlextResult[None].fail("Data scale cannot be negative")
                if (
                    self.data_precision
                    and self.data_scale
                    and self.data_scale > self.data_precision
                ):
                    return FlextResult[None].fail("Data scale cannot exceed precision")

            return FlextResult[None].ok(None)

    class Table(FlextModels.Value):
        """Oracle database table model with metadata and relationships.

        Simplified model without external timestamp dependencies.
        """

        table_name: str = Field(..., description="Table name")
        schema_name: str = Field(default="", description="Schema name")
        columns: list[FlextDbOracleModels.Column] = Field(
            default_factory=list, description="Table columns"
        )
        row_count: int | None = Field(None, description="Approximate row count")
        # created_date removed - using Timestampable.created_at instead
        last_analyzed: datetime | None = Field(
            None, description="Last statistics analysis date"
        )
        table_type: str = Field(
            default="TABLE", description="Table type (TABLE, VIEW, etc.)"
        )
        comments: str | None = Field(None, description="Table comments")

        @classmethod
        def _is_safe_sql_identifier(cls, identifier: str) -> bool:
            """Validate SQL identifier to prevent injection."""
            if not identifier or not isinstance(identifier, str):
                return False

            # Oracle identifiers: alphanumeric, underscore, dollar sign, hash
            # First character must be letter or underscore
            # Max length 128 characters (Oracle standard)
            max_identifier_length = 128
            if len(identifier) > max_identifier_length:
                return False

            # Check first character
            if not (identifier[0].isalpha() or identifier[0] == "_"):
                return False

            # Check remaining characters
            for char in identifier[1:]:
                if not (char.isalnum() or char in ("_", "$", "#")):
                    return False

            # Prevent SQL keywords (basic set)
            reserved_words = {
                "SELECT", "INSERT", "UPDATE", "DELETE", "DROP", "CREATE",
                "ALTER", "TRUNCATE", "GRANT", "REVOKE", "UNION", "ORDER",
                "GROUP", "HAVING", "WHERE", "FROM", "INTO", "VALUES"
            }

            return identifier.upper() not in reserved_words

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

            # Oracle SQL identifier validation (comprehensive security check)
            if not cls._is_safe_sql_identifier(v):
                msg = f"Invalid table name '{v}': contains unsafe characters or is a reserved word"
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

            # Oracle SQL identifier validation (comprehensive security check) - only if not empty
            if v and not cls._is_safe_sql_identifier(v):
                msg = f"Invalid schema name '{v}': contains unsafe characters or is a reserved word"
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

        def validate_business_rules(self) -> FlextResult[None]:
            """Validate Oracle table business rules."""
            # Table name validation
            if not self.table_name or not self.table_name.strip():
                return FlextResult[None].fail("Table name cannot be empty")

            # Schema name validation (optional)
            if (
                self.schema_name
                and len(self.schema_name)
                > FlextDbOracleConstants.OracleValidation.MAX_SCHEMA_NAME_LENGTH
            ):
                return FlextResult[None].fail(
                    f"Schema name exceeds maximum length of {FlextDbOracleConstants.OracleValidation.MAX_SCHEMA_NAME_LENGTH}"
                )

            # Column validation
            if not self.columns:
                return FlextResult[None].fail("Table must have at least one column")

            # Validate each column's business rules
            for column in self.columns:
                column_validation = column.validate_business_rules()
                if not column_validation.success:
                    return FlextResult[None].fail(
                        f"Column '{column.column_name}' validation failed: {column_validation.error}"
                    )

            return FlextResult[None].ok(None)

    class Schema(FlextModels.Entity):
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

        def validate_business_rules(self) -> FlextResult[None]:
            """Validate Oracle schema business rules."""
            # Schema name validation
            if not self.schema_name or not self.schema_name.strip():
                return FlextResult[None].fail("Schema name cannot be empty")

            # Schema name length validation
            if (
                len(self.schema_name)
                > FlextDbOracleConstants.OracleValidation.MAX_SCHEMA_NAME_LENGTH
            ):
                return FlextResult[None].fail(
                    f"Schema name exceeds maximum length of {FlextDbOracleConstants.OracleValidation.MAX_SCHEMA_NAME_LENGTH}"
                )

            # Tables validation
            if self.tables:
                for table in self.tables:
                    table_validation = table.validate_business_rules()
                    if not table_validation.success:
                        return FlextResult[None].fail(
                            f"Table '{table.table_name}' validation failed: {table_validation.error}"
                        )

            return FlextResult[None].ok(None)

    class QueryResult(FlextModels.Value):
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

        def validate_business_rules(self) -> FlextResult[None]:
            """Validate Oracle query result business rules."""
            # Basic validation for Oracle query results
            if self.row_count < 0:
                return FlextResult.fail("Row count cannot be negative")

            if len(self.rows) > self.row_count:
                return FlextResult.fail("Actual rows exceed declared count")

            if len(self.columns) > 0:
                for i, row in enumerate(self.rows):
                    if len(row) > len(self.columns):
                        return FlextResult.fail(f"Row {i} has more values than columns")

            return FlextResult.ok(None)

    class ConnectionStatus(FlextModels.Value):
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
            max_port = 65535
            if v is not None and not (1 <= v <= max_port):
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

            current_time = self.last_activity or FlextUtilities.generate_timestamp()
            uptime = current_time - self.connection_time
            return uptime.total_seconds()

        def is_active(self) -> bool:
            """Check if connection is active and healthy."""
            return self.is_connected and self.error_message is None

        def validate_business_rules(self) -> FlextResult[None]:
            """Validate Oracle connection status business rules."""
            # Basic validation for Oracle connection status
            # Connected status consistency
            if self.is_connected and self.error_message is not None:
                return FlextResult.fail("Connected status cannot have error message")

            # Error message should exist when not connected and no other details
            if (
                not self.is_connected
                and self.error_message is None
                and (self.connection_time is None and self.last_activity is None)
            ):
                return FlextResult.fail(
                    "Disconnected status should provide error or timing information"
                )

            return FlextResult.ok(None)

    # =============================================================================
    # ORACLE CONFIGURATION MODELS - Consolidated from config.py
    # =============================================================================

    class OracleConfig(BaseSettings):
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
                raise ValueError(FlextDbOracleConstants.ErrorMessages.HOST_EMPTY)
            return v

        @field_validator("username")
        @classmethod
        def validate_username_not_empty(cls, v: str) -> str:
            """Validate username is not empty or whitespace only."""
            if not v or not isinstance(v, str) or not v.strip():
                raise ValueError(FlextDbOracleConstants.ErrorMessages.USERNAME_EMPTY)
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
            return cls.model_validate(
                {
                    "host": os.getenv("FLEXT_TARGET_ORACLE_HOST", "localhost"),
                    "port": int(os.getenv("FLEXT_TARGET_ORACLE_PORT", "1521")),
                    "username": os.getenv("FLEXT_TARGET_ORACLE_USERNAME", "system"),
                    "password": SecretStr(
                        os.getenv("FLEXT_TARGET_ORACLE_PASSWORD", "oracle")
                    ),
                    "service_name": os.getenv(
                        "FLEXT_TARGET_ORACLE_SERVICE_NAME", "XEPDB1"
                    ),
                    "ssl_server_cert_dn": os.getenv("FLEXT_TARGET_ORACLE_SSL_CERT_DN"),
                }
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

        def validate_business_rules(self) -> FlextResult[None]:
            """Validate index configuration business rules."""
            # Validate index name
            if not self.index_name or not self.index_name.strip():
                return FlextResult[None].fail("Index name cannot be empty")

            # Validate table name
            if not self.table_name or not self.table_name.strip():
                return FlextResult[None].fail("Table name cannot be empty")

            # Validate columns
            if not self.columns or len(self.columns) == 0:
                return FlextResult[None].fail("Index must have at least one column")

            # Validate each column name
            for column in self.columns:
                if not column or not column.strip():
                    return FlextResult[None].fail("Column names cannot be empty")

            return FlextResult[None].ok(None)

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


# Export API - ONLY single class (no compatibility aliases)
__all__: list[str] = [
    "CreateIndexConfig",
    "FlextDbOracleConfig",  # Aliases for tests compatibility
    "FlextDbOracleModels",
    "MergeStatementConfig",
]

# Compatibility aliases for tests
FlextDbOracleConfig = FlextDbOracleModels.OracleConfig
CreateIndexConfig = FlextDbOracleModels.CreateIndex
MergeStatementConfig = FlextDbOracleModels.MergeStatement


# Deprecated field classes ELIMINATED following flext-core single class pattern
# Use FlextDbOracleModels directly for all field access
