"""Oracle Database models using FLEXT ecosystem patterns.

This module provides Oracle-specific models extending flext-core patterns
for configuration, validation, and data structures.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import os
from datetime import datetime

from flext_core import FlextModels, FlextResult, FlextTypes, FlextValidations
from pydantic import Field, field_validator

# Oracle-specific constants from domain requirements
MAX_PORT = 65535
MIN_PORT = 1
MAX_ORACLE_IDENTIFIER_LENGTH = 30
ORACLE_IDENTIFIER_PATTERN = r"^[A-Z][A-Z0-9_$#]*$"
MAX_HOSTNAME_LENGTH = 253


class FlextDbOracleModels(FlextModels):
    """Oracle database models using flext-core exclusively - ZERO duplication."""

    # Use flext-core for ALL model functionality - NO custom implementations

    # Nested validation helper (single class per module pattern)
    class _OracleValidation:
        """Centralized Oracle validation using flext-core exclusively."""

        @staticmethod
        def validate_identifier(identifier: str) -> FlextResult[str]:
            """Validate Oracle identifier using flext-core BusinessValidators - Single Source of Truth."""
            result = FlextValidations.BusinessValidators.validate_string_field(
                identifier.upper(),
                min_length=1,
                max_length=MAX_ORACLE_IDENTIFIER_LENGTH,
                pattern=ORACLE_IDENTIFIER_PATTERN,
            )
            if result.is_failure:
                error_msg = f"Invalid Oracle identifier: {result.error}"
                return FlextResult[str].fail(error_msg)
            return FlextResult[str].ok(result.unwrap())

    # Base models from flext-core
    Entity = FlextModels.Entity
    Value = FlextModels.Value

    # Database configuration from flext-core
    DatabaseConfig = FlextModels.DatabaseConfig

    # Oracle-specific field definitions using flext-core patterns
    host_field = Field(default="localhost", description="Oracle database host")
    port_field = Field(default=1521, description="Oracle database port")
    username_field = Field(..., description="Oracle database username")
    password_field = Field(..., description="Oracle database password")
    service_name_field = Field(default="XE", description="Oracle service name")

    class OracleConfig(FlextModels.SystemConfigs.DatabaseConfig):
        """Oracle-specific configuration extending flext-core DatabaseConfig."""

        # Oracle-specific defaults using flext-core field validation
        host: str = "localhost"
        port: int = 1521  # Oracle default port
        name: str = "XE"  # Oracle Express default

        # Oracle-specific fields not in base DatabaseConfig
        service_name: str | None = Field(
            default=None, description="Oracle service name"
        )
        sid: str | None = Field(
            default=None, description="Oracle SID (System Identifier)"
        )
        ssl_server_cert_dn: str | None = Field(
            default=None, description="SSL server certificate DN"
        )

        # Connection pool configuration
        pool_min: int = Field(default=2, description="Minimum pool size")
        pool_max: int = Field(default=20, description="Maximum pool size")
        timeout: int = Field(default=60, description="Connection timeout in seconds")

        # Add properties for backward compatibility
        @property
        def username(self) -> str:
            """Alias for user field from base DatabaseConfig."""
            return self.user

        @classmethod
        def from_env(
            cls, prefix: str = "ORACLE"
        ) -> FlextResult[FlextDbOracleModels.OracleConfig]:
            """Create OracleConfig from environment variables with optional prefix."""
            try:
                # Type-safe config creation using prefix
                config = cls(
                    host=os.getenv(f"{prefix}_HOST", "localhost"),
                    port=int(os.getenv(f"{prefix}_PORT", "1521")),
                    name=os.getenv(f"{prefix}_DB", "XE"),
                    user=os.getenv(f"{prefix}_USER", "flext_user"),
                    password=os.getenv(f"{prefix}_PASSWORD", ""),
                    service_name=os.getenv(f"{prefix}_SERVICE_NAME"),
                    pool_min=int(os.getenv(f"{prefix}_POOL_MIN", "2")),
                    pool_max=int(os.getenv(f"{prefix}_POOL_MAX", "20")),
                    timeout=int(os.getenv(f"{prefix}_TIMEOUT", "60")),
                )
                return FlextResult[FlextDbOracleModels.OracleConfig].ok(config)
            except Exception as e:
                return FlextResult[FlextDbOracleModels.OracleConfig].fail(
                    f"Failed to create config from env: {e}"
                )

        @classmethod
        def from_url(cls, url: str) -> FlextResult[FlextDbOracleModels.OracleConfig]:
            """Create OracleConfig from database URL."""
            try:
                # Simple URL parsing for Oracle
                # oracle://user:password@host:port/service_name
                if not url.startswith("oracle://"):
                    return FlextResult[FlextDbOracleModels.OracleConfig].fail(
                        "URL must start with oracle://"
                    )

                # Remove protocol
                url_parts = url[9:]  # Remove "oracle://"

                # Parse user:password@host:port/service_name
                if "@" in url_parts:
                    user_pass, host_port_service = url_parts.split("@", 1)
                    if ":" in user_pass:
                        user, password = user_pass.split(":", 1)
                    else:
                        user = user_pass
                        password = ""
                else:
                    return FlextResult[FlextDbOracleModels.OracleConfig].fail(
                        "Invalid URL format"
                    )

                # Parse host:port/service_name
                if "/" in host_port_service:
                    host_port, service_name = host_port_service.split("/", 1)
                else:
                    host_port = host_port_service
                    service_name = None

                if ":" in host_port:
                    host, port_str = host_port.split(":", 1)
                    port = int(port_str)
                else:
                    host = host_port
                    port = 1521

                config = cls(
                    host=host,
                    port=port,
                    name=service_name or "XE",
                    user=user,
                    password=password,
                    service_name=service_name,
                )
                return FlextResult[FlextDbOracleModels.OracleConfig].ok(config)
            except Exception as e:
                return FlextResult[FlextDbOracleModels.OracleConfig].fail(
                    f"Failed to parse URL: {e}"
                )

        @field_validator("host")
        @classmethod
        def validate_host(cls, v: str) -> str:
            """Validate host using flext-core BusinessValidators."""
            result = FlextValidations.BusinessValidators.validate_string_field(
                v, min_length=1, max_length=MAX_HOSTNAME_LENGTH
            )
            if result.is_failure:
                error_msg = f"Invalid host: {result.error}"
                raise ValueError(error_msg)
            return result.unwrap()

        @field_validator("port")
        @classmethod
        def validate_port(cls, v: int) -> int:
            """Validate port using flext-core TypeValidators."""
            int_result = FlextValidations.TypeValidators.validate_integer(v)
            if int_result.is_failure:
                error_msg = f"Invalid port: {int_result.error}"
                raise ValueError(error_msg)

            port_val = int_result.unwrap()
            if not (MIN_PORT <= port_val <= MAX_PORT):
                error_msg = (
                    f"Port must be between {MIN_PORT}-{MAX_PORT}, got {port_val}"
                )
                raise ValueError(error_msg)
            return port_val

        @field_validator("name")
        @classmethod
        def validate_database_name(cls, v: str) -> str:
            """Validate database name using flext-core BusinessValidators."""
            result = FlextValidations.BusinessValidators.validate_string_field(
                v.upper(),  # Oracle normalizes to uppercase
                min_length=1,
                max_length=MAX_ORACLE_IDENTIFIER_LENGTH,
                pattern=ORACLE_IDENTIFIER_PATTERN,
            )
            if result.is_failure:
                error_msg = f"Invalid database name: {result.error}"
                raise ValueError(error_msg)
            return result.unwrap()

    class ConnectionStatus(FlextModels.Value):
        """Connection status using flext-core Value object."""

        is_connected: bool = False
        last_check: datetime = Field(default_factory=datetime.now)
        error_message: str | None = None

        # Additional Oracle-specific connection details
        connection_time: float | None = None
        last_activity: datetime | None = None
        session_id: str | None = None
        host: str | None = None
        port: int | None = None
        service_name: str | None = None
        username: str | None = None
        version: str | None = None

    class QueryResult(FlextModels.Entity):
        """Query result using flext-core Entity."""

        query: str
        result_data: list[FlextTypes.Core.Dict] = Field(default_factory=list)
        row_count: int = 0
        execution_time_ms: int = 0

        # Additional Oracle-specific query result details
        columns: list[str] = Field(default_factory=list, description="Column names")
        rows: list[list[object]] = Field(default_factory=list, description="Row data")
        query_hash: str | None = Field(
            default=None, description="Query hash for caching"
        )
        explain_plan: str | None = Field(
            default=None, description="Query execution plan"
        )

    class Table(FlextModels.Entity):
        """Oracle table using flext-core Entity."""

        name: str
        owner: str = "USER"
        columns: list[Column] = Field(default_factory=list)

        @field_validator("name", "owner")
        @classmethod
        def validate_oracle_identifier(cls, v: str) -> str:
            """Validate Oracle identifiers using flext-core."""
            result = FlextValidations.BusinessValidators.validate_string_field(
                v.upper(),
                min_length=1,
                max_length=MAX_ORACLE_IDENTIFIER_LENGTH,
                pattern=ORACLE_IDENTIFIER_PATTERN,
            )
            if result.is_failure:
                error_msg = f"Invalid Oracle identifier: {result.error}"
                raise ValueError(error_msg)
            return result.unwrap()

    class Column(FlextModels.Entity):
        """Oracle column using flext-core Entity."""

        name: str
        data_type: str
        nullable: bool = True
        default_value: str | None = None

        @field_validator("name")
        @classmethod
        def validate_column_name(cls, v: str) -> str:
            """Validate column name using flext-core."""
            result = FlextValidations.BusinessValidators.validate_string_field(
                v.upper(),
                min_length=1,
                max_length=MAX_ORACLE_IDENTIFIER_LENGTH,
                pattern=ORACLE_IDENTIFIER_PATTERN,
            )
            if result.is_failure:
                error_msg = f"Invalid column name: {result.error}"
                raise ValueError(error_msg)
            return result.unwrap()

    class Schema(FlextModels.Entity):
        """Oracle schema using flext-core Entity."""

        name: str
        tables: list[Table] = Field(default_factory=list)

        @field_validator("name")
        @classmethod
        def validate_schema_name(cls, v: str) -> str:
            """Validate schema name using flext-core."""
            result = FlextValidations.BusinessValidators.validate_string_field(
                v.upper(),
                min_length=1,
                max_length=MAX_ORACLE_IDENTIFIER_LENGTH,
                pattern=ORACLE_IDENTIFIER_PATTERN,
            )
            if result.is_failure:
                error_msg = f"Invalid schema name: {result.error}"
                raise ValueError(error_msg)
            return result.unwrap()

    class CreateIndexConfig(FlextModels.Value):
        """Index creation config using flext-core Value."""

        index_name: str
        table_name: str
        columns: list[str]
        schema_name: str | None = None
        unique: bool = False
        tablespace: str | None = None
        parallel: int | None = None

    class MergeStatementConfig(FlextModels.Value):
        """Merge statement config using flext-core Value."""

        target_table: str
        source_query: str
        merge_conditions: list[str]
        update_columns: list[str] = Field(default_factory=list)
        insert_columns: list[str] = Field(default_factory=list)


# Module-level aliases for backward compatibility - direct references to flext-core generated classes
OracleConfig = FlextDbOracleModels.OracleConfig
ConnectionStatus = FlextDbOracleModels.ConnectionStatus
QueryResult = FlextDbOracleModels.QueryResult
Table = FlextDbOracleModels.Table
Column = FlextDbOracleModels.Column
Schema = FlextDbOracleModels.Schema
CreateIndexConfig = FlextDbOracleModels.CreateIndexConfig
MergeStatementConfig = FlextDbOracleModels.MergeStatementConfig

__all__: FlextTypes.Core.StringList = [
    "Column",
    "ConnectionStatus",
    "CreateIndexConfig",
    "FlextDbOracleModels",
    "MergeStatementConfig",
    "OracleConfig",
    "OracleValidation",
    "QueryResult",
    "Schema",
    "Table",
]


# Expose validation methods through the unified class
OracleValidation = FlextDbOracleModels._OracleValidation
