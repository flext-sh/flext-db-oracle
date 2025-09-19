"""Oracle Database models using FLEXT ecosystem patterns.

This module provides Oracle-specific models extending flext-core patterns
for configuration, validation, and data structures.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import os
import re
from datetime import datetime
from typing import ClassVar

from pydantic import Field, ValidationInfo, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from flext_core import FlextModels, FlextResult

from .constants import FlextDbOracleConstants


class FlextDbOracleModels(FlextModels.Entity):
    """Oracle database models using flext-core exclusively."""

    # Use flext-core for ALL model functionality - NO custom implementations

    # Nested validation helper (single class per module pattern)
    class _OracleValidation:
        """Centralized Oracle validation using flext-core exclusively."""

        @staticmethod
        def validate_identifier(identifier: str) -> FlextResult[str]:
            """Validate Oracle identifier using direct validation - Single Source of Truth."""
            # Convert to uppercase for Oracle convention
            upper_identifier = identifier.upper()

            # Basic validation
            if not isinstance(upper_identifier, str) or not upper_identifier.strip():
                return FlextResult[str].fail("Oracle identifier cannot be empty")

            # Length validation
            if (
                len(upper_identifier)
                > FlextDbOracleConstants.OracleValidation.MAX_ORACLE_IDENTIFIER_LENGTH
            ):
                error_msg = f"Oracle identifier too long (max {FlextDbOracleConstants.OracleValidation.MAX_ORACLE_IDENTIFIER_LENGTH} chars)"
                return FlextResult[str].fail(error_msg)

            # Pattern validation
            if not re.match(
                FlextDbOracleConstants.OracleValidation.ORACLE_IDENTIFIER_PATTERN,
                upper_identifier,
            ):
                error_msg = "Oracle identifier contains invalid characters"
                return FlextResult[str].fail(error_msg)

            return FlextResult[str].ok(upper_identifier)

    # Public alias for validation - FLEXT unified class pattern
    OracleValidation = _OracleValidation

    # Base models from flext-core
    Entity: ClassVar[type] = FlextModels.Entity
    Value: ClassVar[type] = FlextModels.Value

    # Database configuration from flext-core
    DatabaseConfig: ClassVar[type] = FlextModels.Entity

    # Oracle-specific field definitions using flext-core patterns
    host_field: ClassVar[object] = Field(
        default="localhost",
        description="Oracle database host",
    )
    port_field: ClassVar[object] = Field(
        default=1521,
        description="Oracle database port",
    )
    username_field: ClassVar[object] = Field(
        ...,
        description="Oracle database username",
    )
    password_field: ClassVar[object] = Field(
        ...,
        description="Oracle database password",
    )
    service_name_field: ClassVar[object] = Field(
        default="XE",
        description="Oracle service name",
    )

    class OracleConfig(FlextModels.Entity):
        """Oracle-specific configuration extending flext-core DatabaseConfig with pydantic-settings support."""

        # Oracle-specific defaults using flext-core field validation
        host: str = Field(default="localhost", description="Oracle database host")
        port: int = Field(default=1521, description="Oracle database port")
        name: str = Field(default="XE", description="Oracle database name")

        # Authentication fields
        username: str = Field(description="Oracle database username")
        password: str = Field(description="Oracle database password")

        # Oracle-specific fields not in base DatabaseConfig
        service_name: str | None = Field(
            default=None,
            description="Oracle service name",
        )
        sid: str | None = Field(
            default=None,
            description="Oracle SID (System Identifier)",
        )
        ssl_server_cert_dn: str | None = Field(
            default=None,
            description="SSL server certificate DN",
        )

        # Connection pool configuration
        pool_min: int = Field(default=2, description="Minimum pool size")
        pool_max: int = Field(default=20, description="Maximum pool size")
        timeout: int = Field(default=60, description="Connection timeout in seconds")

        @classmethod
        def from_env(
            cls,
            prefix: str = "ORACLE",
        ) -> FlextResult[FlextDbOracleModels.OracleConfig]:
            """Create OracleConfig from environment variables with optional prefix."""
            try:
                # Type-safe config creation using prefix
                config = cls(
                    host=os.getenv(f"{prefix}_HOST", "localhost"),
                    port=int(os.getenv(f"{prefix}_PORT", "1521")),
                    name=os.getenv(f"{prefix}_DB", "XE"),
                    username=os.getenv(f"{prefix}_USER", "flext_user"),
                    password=os.getenv(f"{prefix}_PASSWORD", ""),
                    service_name=os.getenv(f"{prefix}_SERVICE_NAME"),
                    pool_min=int(os.getenv(f"{prefix}_POOL_MIN", "2")),
                    pool_max=int(os.getenv(f"{prefix}_POOL_MAX", "20")),
                    timeout=int(os.getenv(f"{prefix}_TIMEOUT", "60")),
                )
                return FlextResult[FlextDbOracleModels.OracleConfig].ok(config)
            except Exception as e:
                return FlextResult[FlextDbOracleModels.OracleConfig].fail(
                    f"Failed to create config from env: {e}",
                )

        @classmethod
        def from_url(cls, url: str) -> FlextResult[FlextDbOracleModels.OracleConfig]:
            """Create OracleConfig from database URL."""
            try:
                # Simple URL parsing for Oracle
                # oracle://user:password@host:port/service_name
                if not url.startswith("oracle://"):
                    return FlextResult[FlextDbOracleModels.OracleConfig].fail(
                        "URL must start with oracle://",
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
                        "Invalid URL format",
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
                    username=user,
                    password=password,
                    service_name=service_name,
                )
                return FlextResult[FlextDbOracleModels.OracleConfig].ok(config)
            except Exception as e:
                return FlextResult[FlextDbOracleModels.OracleConfig].fail(
                    f"Failed to parse URL: {e}",
                )

        @field_validator("host")
        @classmethod
        def validate_host(cls, v: str) -> str:
            """Validate host using direct validation."""
            if not isinstance(v, str) or not v.strip():
                msg = "Host cannot be empty"
                raise ValueError(msg)
            if len(v) > FlextDbOracleConstants.OracleValidation.MAX_HOSTNAME_LENGTH:
                msg = f"Host too long (max {FlextDbOracleConstants.OracleValidation.MAX_HOSTNAME_LENGTH} chars)"
                raise ValueError(msg)
            return v.strip()

        @field_validator("port")
        @classmethod
        def validate_port(cls, v: int) -> int:
            """Validate port using direct validation."""
            if not isinstance(v, int) or isinstance(v, bool):
                msg = "Port must be an integer"
                raise TypeError(msg)

            if not (
                FlextDbOracleConstants.OracleValidation.MIN_PORT
                <= v
                <= FlextDbOracleConstants.OracleValidation.MAX_PORT
            ):
                error_msg = f"Port must be between {FlextDbOracleConstants.OracleValidation.MIN_PORT}-{FlextDbOracleConstants.OracleValidation.MAX_PORT}, got {v}"
                raise ValueError(error_msg)
            return v

        @field_validator("name")
        @classmethod
        def validate_database_name(cls, v: str) -> str:
            """Validate database name using direct validation."""
            # Oracle normalizes to uppercase
            upper_name = v.upper()

            # Basic validation
            if not isinstance(upper_name, str) or not upper_name.strip():
                msg = "Database name cannot be empty"
                raise ValueError(msg)

            # Length validation
            if (
                len(upper_name)
                > FlextDbOracleConstants.OracleValidation.MAX_ORACLE_IDENTIFIER_LENGTH
            ):
                msg = f"Database name too long (max {FlextDbOracleConstants.OracleValidation.MAX_ORACLE_IDENTIFIER_LENGTH} chars)"
                raise ValueError(msg)

            # Pattern validation
            if not re.match(
                FlextDbOracleConstants.OracleValidation.ORACLE_IDENTIFIER_PATTERN,
                upper_name,
            ):
                msg = "Database name contains invalid characters"
                raise ValueError(msg)

            return upper_name

        @field_validator("service_name")
        @classmethod
        def validate_service_name(cls, v: str | None) -> str | None:
            """Validate Oracle service name."""
            if v is None:
                return None

            # Check if empty string
            if not isinstance(v, str) or not v.strip():
                msg = "Service name cannot be empty when provided"
                raise ValueError(msg)

            # Validate identifier if not empty
            upper_name = v.upper()
            if (
                len(upper_name)
                > FlextDbOracleConstants.OracleValidation.MAX_ORACLE_IDENTIFIER_LENGTH
            ):
                msg = f"Service name too long (max {FlextDbOracleConstants.OracleValidation.MAX_ORACLE_IDENTIFIER_LENGTH} chars)"
                raise ValueError(msg)

            if not re.match(
                FlextDbOracleConstants.OracleValidation.ORACLE_IDENTIFIER_PATTERN,
                upper_name,
            ):
                msg = "Service name contains invalid characters"
                raise ValueError(msg)

            return upper_name

        @field_validator("sid")
        @classmethod
        def validate_sid(cls, v: str | None) -> str | None:
            """Validate Oracle SID."""
            if v is None:
                return None

            # Check if empty string
            if not isinstance(v, str) or not v.strip():
                msg = "SID cannot be empty when provided"
                raise ValueError(msg)

            # Validate identifier if not empty
            upper_name = v.upper()
            if (
                len(upper_name)
                > FlextDbOracleConstants.OracleValidation.MAX_ORACLE_IDENTIFIER_LENGTH
            ):
                msg = f"SID too long (max {FlextDbOracleConstants.OracleValidation.MAX_ORACLE_IDENTIFIER_LENGTH} chars)"
                raise ValueError(msg)

            if not re.match(
                FlextDbOracleConstants.OracleValidation.ORACLE_IDENTIFIER_PATTERN,
                upper_name,
            ):
                msg = "SID contains invalid characters"
                raise ValueError(msg)

            return upper_name

    class OracleSettings(BaseSettings):
        """Oracle database settings using pydantic-settings BaseSettings for configuration management.

        This class provides enterprise-grade configuration management with environment variable support,
        validation, and integration with flext models architecture and patterns.
        """

        # Oracle connection settings
        oracle_host: str = Field(
            default="localhost",
            description="Oracle database host",
            validation_alias="ORACLE_HOST",
        )
        oracle_port: int = Field(
            default=1521,
            description="Oracle database port",
            ge=1,
            le=65535,
            validation_alias="ORACLE_PORT",
        )
        oracle_user: str = Field(
            default="system",
            description="Oracle database username",
            validation_alias="ORACLE_USER",
        )
        oracle_password: str = Field(
            default="",
            description="Oracle database password",
            validation_alias="ORACLE_PASSWORD",
        )
        oracle_service_name: str = Field(
            default="XEPDB1",
            description="Oracle service name",
            validation_alias="ORACLE_SERVICE_NAME",
        )
        oracle_database_name: str = Field(
            default="XE",
            description="Oracle database name",
            validation_alias="ORACLE_DATABASE_NAME",
        )

        # Oracle-specific settings
        oracle_sid: str | None = Field(
            default=None,
            description="Oracle SID (System Identifier)",
            validation_alias="ORACLE_SID",
        )
        oracle_ssl_server_cert_dn: str | None = Field(
            default=None,
            description="SSL server certificate DN",
            validation_alias="ORACLE_SSL_SERVER_CERT_DN",
        )
        oracle_ssl_verify: bool = Field(
            default=True,
            description="Verify SSL certificates",
            validation_alias="ORACLE_SSL_VERIFY",
        )

        # Connection pool settings
        oracle_pool_min_size: int = Field(
            default=2,
            description="Minimum pool size",
            ge=1,
        )
        oracle_pool_max_size: int = Field(
            default=20,
            description="Maximum pool size",
            ge=1,
        )
        oracle_pool_timeout: int = Field(
            default=60,
            description="Connection timeout in seconds",
            ge=1,
        )
        oracle_pool_recycle: int = Field(
            default=3600,
            description="Pool recycle time in seconds",
            ge=60,
        )
        oracle_pool_pre_ping: bool = Field(
            default=True,
            description="Enable connection pre-ping",
        )

        # Query settings
        oracle_query_timeout: int = Field(
            default=300,
            description="Query timeout in seconds",
            ge=1,
        )
        oracle_fetch_size: int = Field(
            default=1000,
            description="Default fetch size",
            ge=1,
        )
        oracle_max_rows: int = Field(
            default=100000,
            description="Maximum rows per query",
            ge=1,
        )

        # Performance settings
        oracle_enable_autocommit: bool = Field(
            default=False,
            description="Enable autocommit",
        )
        oracle_isolation_level: str = Field(
            default="READ_COMMITTED",
            description="Transaction isolation level",
        )
        oracle_echo_queries: bool = Field(
            default=False,
            description="Echo SQL queries (debug only)",
        )

        # Monitoring settings
        oracle_enable_metrics: bool = Field(
            default=True,
            description="Enable performance metrics",
        )
        oracle_slow_query_threshold: float = Field(
            default=1.0,
            description="Slow query threshold in seconds",
            ge=0.1,
        )
        oracle_log_queries: bool = Field(
            default=False,
            description="Log queries (security risk in production)",
        )

        model_config = SettingsConfigDict(
            env_file=".env",
            env_file_encoding="utf-8",
            case_sensitive=False,
            validate_assignment=True,
            extra="ignore",
        )

        @field_validator("oracle_host")
        @classmethod
        def validate_oracle_host(cls, v: str) -> str:
            """Validate Oracle host using direct validation."""
            if not isinstance(v, str) or not v.strip():
                msg = "Oracle host cannot be empty"
                raise ValueError(msg)
            if len(v) > FlextDbOracleConstants.OracleValidation.MAX_HOSTNAME_LENGTH:
                msg = f"Oracle host too long (max {FlextDbOracleConstants.OracleValidation.MAX_HOSTNAME_LENGTH} chars)"
                raise ValueError(msg)
            return v.strip()

        @field_validator("oracle_service_name", "oracle_database_name")
        @classmethod
        def validate_oracle_identifier(cls, v: str) -> str:
            """Validate Oracle identifiers using direct validation."""
            # Oracle normalizes to uppercase
            upper_v = v.upper()

            # Basic validation
            if not isinstance(upper_v, str) or not upper_v.strip():
                msg = "Oracle identifier cannot be empty"
                raise ValueError(msg)

            # Length validation
            if (
                len(upper_v)
                > FlextDbOracleConstants.OracleValidation.MAX_ORACLE_IDENTIFIER_LENGTH
            ):
                msg = f"Oracle identifier too long (max {FlextDbOracleConstants.OracleValidation.MAX_ORACLE_IDENTIFIER_LENGTH} chars)"
                raise ValueError(msg)

            # Pattern validation
            if not re.match(
                FlextDbOracleConstants.OracleValidation.ORACLE_IDENTIFIER_PATTERN,
                upper_v,
            ):
                msg = "Oracle identifier contains invalid characters"
                raise ValueError(msg)

            return upper_v

        @field_validator("oracle_pool_max_size")
        @classmethod
        def validate_pool_sizes(cls, v: int, info: ValidationInfo) -> int:
            """Validate that max pool size is greater than min pool size."""
            # Use proper Pydantic V2 context access instead of legacy .data
            if info.context and "oracle_pool_min_size" in info.context:
                min_size = info.context["oracle_pool_min_size"]
                if v < min_size:
                    msg = f"Max pool size ({v}) must be >= min pool size ({min_size})"
                    raise ValueError(msg)
            return v

        @field_validator("oracle_isolation_level")
        @classmethod
        def validate_isolation_level(cls, v: str) -> str:
            """Validate Oracle isolation level."""
            valid_levels = [
                "READ_UNCOMMITTED",
                "READ_COMMITTED",
                "REPEATABLE_READ",
                "SERIALIZABLE",
            ]
            v_upper = v.upper()
            if v_upper not in valid_levels:
                msg = f"Invalid isolation level: {v}. Valid levels: {', '.join(valid_levels)}"
                raise ValueError(msg)
            return v_upper

        def to_oracle_config(self) -> FlextResult[FlextDbOracleModels.OracleConfig]:
            """Convert OracleSettings to OracleConfig using flext models architecture."""
            try:
                config = FlextDbOracleModels.OracleConfig(
                    host=self.oracle_host,
                    port=self.oracle_port,
                    name=self.oracle_database_name,
                    username=self.oracle_user,
                    password=self.oracle_password,
                    service_name=self.oracle_service_name,
                    sid=self.oracle_sid,
                    ssl_server_cert_dn=self.oracle_ssl_server_cert_dn,
                    pool_min=self.oracle_pool_min_size,
                    pool_max=self.oracle_pool_max_size,
                    timeout=self.oracle_pool_timeout,
                )
                return FlextResult[FlextDbOracleModels.OracleConfig].ok(config)
            except Exception as e:
                return FlextResult[FlextDbOracleModels.OracleConfig].fail(
                    f"Failed to convert settings to Oracle config: {e}",
                )

        def get_connection_url(self) -> FlextResult[str]:
            """Generate Oracle connection URL from settings."""
            try:
                # Build Oracle connection URL
                if self.oracle_service_name:
                    url = (
                        f"oracle+oracledb://{self.oracle_user}:{self.oracle_password}"
                        f"@{self.oracle_host}:{self.oracle_port}/?service_name={self.oracle_service_name}"
                    )
                else:
                    url = (
                        f"oracle+oracledb://{self.oracle_user}:{self.oracle_password}"
                        f"@{self.oracle_host}:{self.oracle_port}/{self.oracle_database_name}"
                    )

                return FlextResult[str].ok(url)
            except Exception as e:
                return FlextResult[str].fail(f"Failed to generate connection URL: {e}")

        def validate_configuration(self) -> FlextResult[None]:
            """Validate complete Oracle configuration using flext patterns."""
            # Check for required password in production-like settings
            if not self.oracle_password and self.oracle_host != "localhost":
                return FlextResult[None].fail(
                    "Password required for non-localhost connections",
                )

            # Validate pool configuration
            if self.oracle_pool_max_size < self.oracle_pool_min_size:
                return FlextResult[None].fail("Max pool size must be >= min pool size")

            # Validate timeout settings
            if (
                self.oracle_query_timeout
                > FlextDbOracleConstants.OracleValidation.MAX_QUERY_TIMEOUT_SECONDS
            ):
                return FlextResult[None].fail(
                    f"Query timeout too high (max {FlextDbOracleConstants.OracleValidation.MAX_QUERY_TIMEOUT_SECONDS} seconds)",
                )

            # Security validations
            if self.oracle_log_queries and self.oracle_host != "localhost":
                return FlextResult[None].fail(
                    "Query logging disabled for security in non-localhost environments",
                )

            return FlextResult[None].ok(None)

        @classmethod
        def load_from_file(
            cls,
            config_file: str = ".env",
        ) -> FlextResult[FlextDbOracleModels.OracleSettings]:
            """Load Oracle settings from configuration file."""
            try:
                settings = cls()

                # Validate the loaded settings
                validation_result = settings.validate_configuration()
                if validation_result.is_failure:
                    return FlextResult["FlextDbOracleModels.OracleSettings"].fail(
                        f"Configuration validation failed: {validation_result.error}",
                    )

                return FlextResult["FlextDbOracleModels.OracleSettings"].ok(settings)
            except Exception as e:
                return FlextResult["FlextDbOracleModels.OracleSettings"].fail(
                    f"Failed to load settings from {config_file}: {e}",
                )

        @classmethod
        def create_development_config(cls) -> FlextDbOracleModels.OracleSettings:
            """Create Oracle settings for development environment."""
            # Use model_validate to bypass mypy constructor signature issues
            return cls.model_validate(
                {
                    "oracle_host": "localhost",
                    "oracle_port": 1521,
                    "oracle_user": "system",
                    "oracle_password": "Oracle123",
                    "oracle_service_name": "XEPDB1",
                    "oracle_database_name": "XE",
                    "oracle_pool_min_size": 2,
                    "oracle_pool_max_size": 10,
                    "oracle_pool_timeout": 30,
                    "oracle_query_timeout": 60,
                    "oracle_echo_queries": True,  # OK for development
                    "oracle_log_queries": True,  # OK for development
                    "oracle_ssl_verify": False,  # OK for local development
                },
            )

        @classmethod
        def create_production_config(cls) -> FlextDbOracleModels.OracleSettings:
            """Create Oracle settings template for production environment."""
            # Use model_validate to bypass mypy constructor signature issues
            return cls.model_validate(
                {
                    "oracle_host": "${ORACLE_HOST}",
                    "oracle_port": 1521,
                    "oracle_user": "${ORACLE_USER}",
                    "oracle_password": "${ORACLE_PASSWORD}",
                    "oracle_service_name": "${ORACLE_SERVICE_NAME}",
                    "oracle_database_name": "${ORACLE_DATABASE_NAME}",
                    "oracle_pool_min_size": 10,
                    "oracle_pool_max_size": 50,
                    "oracle_pool_timeout": 60,
                    "oracle_query_timeout": 300,
                    "oracle_echo_queries": False,
                    "oracle_log_queries": False,
                    "oracle_ssl_verify": True,
                    "oracle_enable_metrics": True,
                    "oracle_slow_query_threshold": 2.0,
                },
            )

    class ConnectionStatus(FlextModels.Entity):
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
        db_version: str | None = None

    class QueryResult(FlextModels.Entity):
        """Query result using flext-core Entity."""

        query: str
        result_data: list[dict[str, object]] = Field(default_factory=list)
        row_count: int = 0
        execution_time_ms: int = 0

        # Additional Oracle-specific query result details
        columns: list[str] = Field(default_factory=list, description="Column names")
        rows: list[list[object]] = Field(default_factory=list, description="Row data")
        query_hash: str | None = Field(
            default=None,
            description="Query hash for caching",
        )
        explain_plan: str | None = Field(
            default=None,
            description="Query execution plan",
        )

    class Table(FlextModels.Entity):
        """Oracle table using flext-core Entity."""

        name: str
        owner: str = "USER"
        columns: list[FlextDbOracleModels.Column] = Field(default_factory=list)

        @field_validator("name", "owner")
        @classmethod
        def validate_oracle_identifier(cls, v: str) -> str:
            """Validate Oracle identifiers using direct validation."""
            # Oracle normalizes to uppercase
            upper_v = v.upper()

            # Basic validation
            if not isinstance(upper_v, str) or not upper_v.strip():
                msg = "Oracle identifier cannot be empty"
                raise ValueError(msg)

            # Length validation
            if (
                len(upper_v)
                > FlextDbOracleConstants.OracleValidation.MAX_ORACLE_IDENTIFIER_LENGTH
            ):
                msg = f"Oracle identifier too long (max {FlextDbOracleConstants.OracleValidation.MAX_ORACLE_IDENTIFIER_LENGTH} chars)"
                raise ValueError(msg)

            # Pattern validation
            if not re.match(
                FlextDbOracleConstants.OracleValidation.ORACLE_IDENTIFIER_PATTERN,
                upper_v,
            ):
                msg = "Oracle identifier contains invalid characters"
                raise ValueError(msg)

            return upper_v

    class Column(FlextModels.Entity):
        """Oracle column using flext-core Entity."""

        name: str
        data_type: str
        nullable: bool = True
        default_value: str | None = None

        @field_validator("name")
        @classmethod
        def validate_column_name(cls, v: str) -> str:
            """Validate column name using direct validation."""
            # Oracle normalizes to uppercase
            upper_v = v.upper()

            # Basic validation
            if not isinstance(upper_v, str) or not upper_v.strip():
                msg = "Column name cannot be empty"
                raise ValueError(msg)

            # Length validation
            if (
                len(upper_v)
                > FlextDbOracleConstants.OracleValidation.MAX_ORACLE_IDENTIFIER_LENGTH
            ):
                msg = f"Column name too long (max {FlextDbOracleConstants.OracleValidation.MAX_ORACLE_IDENTIFIER_LENGTH} chars)"
                raise ValueError(msg)

            # Pattern validation
            if not re.match(
                FlextDbOracleConstants.OracleValidation.ORACLE_IDENTIFIER_PATTERN,
                upper_v,
            ):
                msg = "Column name contains invalid characters"
                raise ValueError(msg)

            return upper_v

    class Schema(FlextModels.Entity):
        """Oracle schema using flext-core Entity."""

        name: str
        tables: list[FlextDbOracleModels.Table] = Field(default_factory=list)

        @field_validator("name")
        @classmethod
        def validate_schema_name(cls, v: str) -> str:
            """Validate schema name using flext-core."""
            # Direct validation using isinstance and basic checks
            schema_name = v.upper()

            # Length validation
            if not isinstance(schema_name, str) or len(schema_name) < 1:
                msg = "Schema name must be a non-empty string"
                raise ValueError(msg)
            if (
                len(schema_name)
                > FlextDbOracleConstants.OracleValidation.MAX_ORACLE_IDENTIFIER_LENGTH
            ):
                msg = f"Schema name too long (max {FlextDbOracleConstants.OracleValidation.MAX_ORACLE_IDENTIFIER_LENGTH} characters)"
                raise ValueError(msg)

            # Pattern validation
            if not re.match(
                FlextDbOracleConstants.OracleValidation.ORACLE_IDENTIFIER_PATTERN,
                schema_name,
            ):
                msg = f"Invalid schema name format: {schema_name}"
                raise ValueError(msg)

            return schema_name

    class CreateIndexConfig(FlextModels.Entity):
        """Index creation config using flext-core Value."""

        index_name: str
        table_name: str
        columns: list[str]
        schema_name: str | None = None
        unique: bool = False
        tablespace: str | None = None
        parallel: int | None = None

    class MergeStatementConfig(FlextModels.Entity):
        """Merge statement config using flext-core Value."""

        target_table: str
        source_query: str
        merge_conditions: list[str]
        update_columns: list[str] = Field(default_factory=list)
        insert_columns: list[str] = Field(default_factory=list)


# ZERO TOLERANCE: No compatibility aliases - use FlextDbOracleModels.ClassName directly

__all__: list[str] = [
    "FlextDbOracleModels",
]


# ZERO TOLERANCE: All functionality accessed through FlextDbOracleModels unified class
