"""Oracle Database models using FLEXT ecosystem patterns.

This module provides Oracle-specific models extending flext-core patterns
for configuration, validation, and data structures.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import re
from datetime import UTC, datetime
from typing import ClassVar

from pydantic import (
    ConfigDict,
    Field,
    ValidationInfo,
    computed_field,
    field_serializer,
    field_validator,
    model_validator,
)
from pydantic_settings import BaseSettings, SettingsConfigDict

from flext_core import FlextModels, FlextResult, FlextTypes
from flext_db_oracle.config import FlextDbOracleConfig
from flext_db_oracle.constants import FlextDbOracleConstants


class FlextDbOracleModels(FlextModels):
    """Oracle database models using flext-core exclusively with advanced Pydantic 2.11 features."""

    model_config = ConfigDict(
        validate_assignment=True,
        use_enum_values=True,
        arbitrary_types_allowed=True,
        extra="forbid",
        frozen=False,
        str_strip_whitespace=True,
        validate_return=True,
        ser_json_timedelta="iso8601",
        ser_json_bytes="base64",
    )

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
                > FlextDbOracleConstants.Validation.MAX_ORACLE_IDENTIFIER_LENGTH
            ):
                error_msg = f"Oracle identifier too long (max {FlextDbOracleConstants.Validation.MAX_ORACLE_IDENTIFIER_LENGTH} chars)"
                return FlextResult[str].fail(error_msg)

            # Pattern validation
            if not re.match(
                FlextDbOracleConstants.Validation.ORACLE_IDENTIFIER_PATTERN,
                upper_identifier,
            ):
                error_msg = "Oracle identifier contains invalid characters"
                return FlextResult[str].fail(error_msg)

            return FlextResult[str].ok(upper_identifier)

    # Public alias for validation - FLEXT unified class pattern
    OracleValidation = _OracleValidation

    # Base models from flext-core
    Entity: ClassVar[type[FlextModels.Entity]] = FlextModels.Entity
    Value: ClassVar[type[FlextModels.Value]] = FlextModels.Value

    # Database configuration from flext-core
    DatabaseConfig: ClassVar[type] = FlextModels.Entity

    # Oracle-specific field definitions using flext-core patterns
    host_field: ClassVar[object] = Field(
        default=FlextDbOracleConstants.Defaults.DEFAULT_HOST,
        description="Oracle database host",
    )
    port_field: ClassVar[object] = Field(
        default=FlextDbOracleConstants.Connection.DEFAULT_PORT,
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
        default=FlextDbOracleConstants.Defaults.DEFAULT_DATABASE_NAME,
        description="Oracle service name",
    )

    class OracleConfig(FlextModels.Entity):
        """Oracle-specific configuration extending flext-core DatabaseConfig with advanced Pydantic 2.11 features."""

        # Oracle-specific defaults using flext-core field validation
        host: str = Field(
            default=FlextDbOracleConstants.Defaults.DEFAULT_HOST,
            description="Oracle database host",
        )
        port: int = Field(
            default=FlextDbOracleConstants.Connection.DEFAULT_PORT,
            description="Oracle database port",
        )
        name: str = Field(
            default=FlextDbOracleConstants.Defaults.DEFAULT_DATABASE_NAME,
            description="Oracle database name",
        )

        # Authentication fields
        username: str = Field(description="Oracle database username")
        password: str | None = Field(
            default=None, description="Oracle database password"
        )

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
        pool_min: int = Field(
            default=FlextDbOracleConstants.Connection.DEFAULT_POOL_MIN,
            description="Minimum pool size",
        )
        pool_max: int = Field(
            default=FlextDbOracleConstants.Connection.DEFAULT_POOL_MAX,
            description="Maximum pool size",
        )
        timeout: int = Field(
            default=FlextDbOracleConstants.Connection.DEFAULT_POOL_TIMEOUT,
            description="Connection timeout in seconds",
        )

        @property
        @computed_field
        def connection_string(self) -> str:
            """Computed field for Oracle connection string."""
            if self.service_name:
                return f"oracle://{self.username}@{self.host}:{self.port}/{self.service_name}"
            if self.sid:
                return f"oracle://{self.username}@{self.host}:{self.port}:{self.sid}"
            return f"oracle://{self.username}@{self.host}:{self.port}/{self.name}"

        @property
        @computed_field
        def is_ssl_enabled(self) -> bool:
            """Computed field indicating if SSL is configured."""
            return self.ssl_server_cert_dn is not None

        @property
        @computed_field
        def pool_capacity(self) -> int:
            """Computed field for total pool capacity."""
            return self.pool_max

        @property
        @computed_field
        def connection_identifier(self) -> str:
            """Computed field for connection identifier (service name or SID)."""
            if self.service_name:
                return self.service_name
            if self.sid:
                return self.sid
            return self.name

        @property
        @computed_field
        def is_local_connection(self) -> bool:
            """Computed field indicating if this is a local connection."""
            local_hosts = {"localhost", "127.0.0.1", "::1"}
            return self.host.lower() in local_hosts

        @model_validator(mode="after")
        def validate_oracle_config_consistency(
            self,
        ) -> FlextDbOracleModels.OracleConfig:
            """Model validator for Oracle configuration consistency."""
            # Ensure either service_name or SID is provided, but not both
            if self.service_name and self.sid:
                msg = "Cannot specify both service_name and SID"
                raise ValueError(msg)

            # Validate pool configuration
            if self.pool_max < self.pool_min:
                msg = (
                    f"pool_max ({self.pool_max}) must be >= pool_min ({self.pool_min})"
                )
                raise ValueError(msg)

            # Validate timeout configuration
            min_timeout = 1
            max_timeout = 3600  # 1 hour
            if not (min_timeout <= self.timeout <= max_timeout):
                msg = f"timeout must be between {min_timeout} and {max_timeout} seconds"
                raise ValueError(msg)

            return self

        @field_serializer("password")
        def serialize_password(self, value: str) -> str:
            """Field serializer for password protection."""
            return "[PROTECTED]" if value else ""

        def serialize_connection_string(self, value: str) -> str:
            """Field serializer for connection string with password masking."""
            # Replace password in connection string for serialization
            if "@" in value:
                parts = value.split("@")
                if ":" in parts[0]:
                    protocol_user = parts[0].rsplit(":", 1)[0]
                    return f"{protocol_user}:[PROTECTED]@{parts[1]}"
            return value

        @field_serializer("host")
        def serialize_host(self, value: str) -> str:
            """Field serializer for host normalization."""
            return value.strip().lower()

        @classmethod
        def from_env(
            cls,
            prefix: str = "ORACLE",
        ) -> FlextResult[FlextDbOracleModels.OracleConfig]:
            """Create OracleConfig from environment variables using FlextDbOracleConfig.

            DEPRECATED: Use FlextDbOracleConfig directly for standardized configuration.
            This method now uses FlextDbOracleConfig enhanced singleton pattern internally.

            Args:
                prefix: Environment variable prefix (deprecated, not used with FlextDbOracleConfig)

            """
            _ = prefix  # Parameter required by API but not used in standardized config
            try:
                # Use the enhanced singleton pattern from FlextDbOracleConfig
                standardized_config = FlextDbOracleConfig.get_or_create_shared_instance(
                    project_name="flext-db-oracle"
                )

                # Validate required fields are set
                if (
                    not standardized_config.oracle_username
                    or not standardized_config.oracle_username.strip()
                ):
                    return FlextResult[FlextDbOracleModels.OracleConfig].fail(
                        "Oracle username is required but not configured",
                    )

                if (
                    not standardized_config.oracle_password
                    or not standardized_config.oracle_password.get_secret_value().strip()
                ):
                    return FlextResult[FlextDbOracleModels.OracleConfig].fail(
                        "Oracle password is required but not configured",
                    )

                # Map from FlextDbOracleConfig to OracleConfig for backward compatibility
                config = cls(
                    host=standardized_config.oracle_host,
                    port=standardized_config.oracle_port,
                    name=standardized_config.oracle_database_name,
                    username=standardized_config.oracle_username,
                    password=standardized_config.oracle_password.get_secret_value(),
                    service_name=standardized_config.oracle_service_name,
                    pool_min=standardized_config.pool_min,
                    pool_max=standardized_config.pool_max,
                    timeout=standardized_config.pool_timeout,
                )
                return FlextResult[FlextDbOracleModels.OracleConfig].ok(config)
            except (ValueError, TypeError, AttributeError) as e:
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
                        password = None
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
                    port = FlextDbOracleConstants.Connection.DEFAULT_PORT

                config = cls(
                    host=host,
                    port=port,
                    name=service_name
                    or FlextDbOracleConstants.Defaults.DEFAULT_DATABASE_NAME,
                    username=user,
                    password=password,
                    service_name=service_name,
                )
                return FlextResult[FlextDbOracleModels.OracleConfig].ok(config)
            except (ValueError, TypeError, AttributeError) as e:
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
            if len(v) > FlextDbOracleConstants.Validation.MAX_HOSTNAME_LENGTH:
                msg = f"Host too long (max {FlextDbOracleConstants.Validation.MAX_HOSTNAME_LENGTH} chars)"
                raise ValueError(msg)
            return v.strip()

        @field_validator("password")
        @classmethod
        def validate_password(cls, v: str | None) -> str | None:
            """Validate password is not empty if provided."""
            if v is not None and not v.strip():
                msg = "Password cannot be empty string"
                raise ValueError(msg)
            return v

        @field_validator("port")
        @classmethod
        def validate_port(cls, v: int) -> int:
            """Validate port using direct validation."""
            if not isinstance(v, int) or isinstance(v, bool):
                msg = "Port must be an integer"
                raise TypeError(msg)

            if not (
                FlextDbOracleConstants.Network.MIN_PORT
                <= v
                <= FlextDbOracleConstants.Network.MAX_PORT
            ):
                error_msg = f"Port must be between {FlextDbOracleConstants.Network.MIN_PORT}-{FlextDbOracleConstants.Network.MAX_PORT}, got {v}"
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
                > FlextDbOracleConstants.Validation.MAX_ORACLE_IDENTIFIER_LENGTH
            ):
                msg = f"Database name too long (max {FlextDbOracleConstants.Validation.MAX_ORACLE_IDENTIFIER_LENGTH} chars)"
                raise ValueError(msg)

            # Pattern validation
            if not re.match(
                FlextDbOracleConstants.Validation.ORACLE_IDENTIFIER_PATTERN,
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
                > FlextDbOracleConstants.Validation.MAX_ORACLE_IDENTIFIER_LENGTH
            ):
                msg = f"Service name too long (max {FlextDbOracleConstants.Validation.MAX_ORACLE_IDENTIFIER_LENGTH} chars)"
                raise ValueError(msg)

            if not re.match(
                FlextDbOracleConstants.Validation.ORACLE_IDENTIFIER_PATTERN,
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
                > FlextDbOracleConstants.Validation.MAX_ORACLE_IDENTIFIER_LENGTH
            ):
                msg = f"SID too long (max {FlextDbOracleConstants.Validation.MAX_ORACLE_IDENTIFIER_LENGTH} chars)"
                raise ValueError(msg)

            if not re.match(
                FlextDbOracleConstants.Validation.ORACLE_IDENTIFIER_PATTERN,
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
            default=FlextDbOracleConstants.Defaults.DEFAULT_HOST,
            description="Oracle database host",
            validation_alias="ORACLE_HOST",
        )
        oracle_port: int = Field(
            default=FlextDbOracleConstants.Connection.DEFAULT_PORT,
            description="Oracle database port",
            ge=1,
            le=65535,
            validation_alias="ORACLE_PORT",
        )
        oracle_user: str = Field(
            default=FlextDbOracleConstants.Defaults.DEFAULT_USERNAME,
            description="Oracle database username",
            validation_alias="ORACLE_USER",
        )
        oracle_password: str = Field(
            default="",
            description="Oracle database password",
            validation_alias="ORACLE_PASSWORD",
        )
        oracle_service_name: str = Field(
            default=FlextDbOracleConstants.Connection.DEFAULT_SERVICE_NAME,
            description="Oracle service name",
            validation_alias="ORACLE_SERVICE_NAME",
        )
        oracle_database_name: str = Field(
            default=FlextDbOracleConstants.Defaults.DEFAULT_DATABASE_NAME,
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
            default=FlextDbOracleConstants.Connection.DEFAULT_POOL_MIN,
            description="Minimum pool size",
            ge=1,
        )
        oracle_pool_max_size: int = Field(
            default=FlextDbOracleConstants.Connection.DEFAULT_POOL_MAX,
            description="Maximum pool size",
            ge=1,
        )
        oracle_pool_timeout: int = Field(
            default=FlextDbOracleConstants.Connection.DEFAULT_POOL_TIMEOUT,
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
            default=FlextDbOracleConstants.Query.DEFAULT_QUERY_LIMIT,
            description="Default fetch size",
            ge=1,
        )
        oracle_max_rows: int = Field(
            default=FlextDbOracleConstants.Query.MAX_QUERY_ROWS,
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
            if len(v) > FlextDbOracleConstants.Validation.MAX_HOSTNAME_LENGTH:
                msg = f"Oracle host too long (max {FlextDbOracleConstants.Validation.MAX_HOSTNAME_LENGTH} chars)"
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
                > FlextDbOracleConstants.Validation.MAX_ORACLE_IDENTIFIER_LENGTH
            ):
                msg = f"Oracle identifier too long (max {FlextDbOracleConstants.Validation.MAX_ORACLE_IDENTIFIER_LENGTH} chars)"
                raise ValueError(msg)

            # Pattern validation
            if not re.match(
                FlextDbOracleConstants.Validation.ORACLE_IDENTIFIER_PATTERN,
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

        def to_oracle_config(
            self,
        ) -> FlextResult[FlextDbOracleModels.OracleConfig]:
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
            except (ValueError, TypeError, AttributeError) as e:
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
            except (ValueError, TypeError, AttributeError) as e:
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
                > FlextDbOracleConstants.Query.MAX_QUERY_TIMEOUT
            ):
                return FlextResult[None].fail(
                    f"Query timeout too high (max {FlextDbOracleConstants.Query.MAX_QUERY_TIMEOUT} seconds)",
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
            """Load Oracle settings from configuration file.

            Returns:
                FlextResult[FlextDbOracleModels.OracleSettings]: Settings or error.

            """
            try:
                settings = cls()

                # Validate the loaded settings
                validation_result = settings.validate_configuration()
                if validation_result.is_failure:
                    return FlextResult[FlextDbOracleModels.OracleSettings].fail(
                        f"Configuration validation failed: {validation_result.error}",
                    )

                return FlextResult[FlextDbOracleModels.OracleSettings].ok(settings)
            except (ValueError, TypeError, AttributeError, FileNotFoundError) as e:
                return FlextResult[FlextDbOracleModels.OracleSettings].fail(
                    f"Failed to load settings from {config_file}: {e}",
                )

        @classmethod
        def create_development_config(
            cls,
        ) -> FlextDbOracleModels.OracleSettings:
            """Create Oracle settings for development environment."""
            # Use model_validate to bypass mypy constructor signature issues
            return cls.model_validate(
                {
                    "oracle_host": "localhost",
                    "oracle_port": FlextDbOracleConstants.Connection.DEFAULT_PORT,
                    "oracle_user": FlextDbOracleConstants.Connection.DEFAULT_USERNAME,
                    "oracle_password": "Oracle123",
                    "oracle_service_name": FlextDbOracleConstants.Connection.DEFAULT_SERVICE_NAME,
                    "oracle_database_name": FlextDbOracleConstants.Defaults.DEFAULT_DATABASE_NAME,
                    "oracle_pool_min_size": FlextDbOracleConstants.Connection.DEFAULT_POOL_MIN,
                    "oracle_pool_max_size": 10,
                    "oracle_pool_timeout": FlextDbOracleConstants.Connection.DEFAULT_CONNECTION_TIMEOUT,
                    "oracle_query_timeout": FlextDbOracleConstants.Query.DEFAULT_QUERY_TIMEOUT,
                    "oracle_echo_queries": "True",  # OK for development
                    "oracle_log_queries": "True",  # OK for development
                    "oracle_ssl_verify": "False",  # OK for local development
                },
            )

        @classmethod
        def create_production_config(cls) -> FlextDbOracleModels.OracleSettings:
            """Create Oracle settings template for production environment."""
            # Use model_validate to bypass mypy constructor signature issues
            return cls.model_validate(
                {
                    "oracle_host": "${ORACLE_HOST}",
                    "oracle_port": FlextDbOracleConstants.Connection.DEFAULT_PORT,
                    "oracle_user": "${ORACLE_USER}",
                    "oracle_password": "${ORACLE_PASSWORD}",
                    "oracle_service_name": "${ORACLE_SERVICE_NAME}",
                    "oracle_database_name": "${ORACLE_DATABASE_NAME}",
                    "oracle_pool_min_size": 10,
                    "oracle_pool_max_size": 50,
                    "oracle_pool_timeout": 60,
                    "oracle_query_timeout": 300,
                    "oracle_echo_queries": "False",
                    "oracle_log_queries": "False",
                    "oracle_ssl_verify": "True",
                    "oracle_enable_metrics": "True",
                    "oracle_slow_query_threshold": 2.0,
                },
            )

    class ConnectionStatus(FlextModels.Entity):
        """Connection status using flext-core Entity with advanced Pydantic 2.11 features."""

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

        @property
        @computed_field
        def status_description(self) -> str:
            """Computed field for human-readable status description."""
            if self.is_connected:
                return "Connected"
            if self.error_message:
                return f"Disconnected: {self.error_message}"
            return "Disconnected"

        @property
        @computed_field
        def connection_age_seconds(self) -> float | None:
            """Computed field for connection age in seconds."""
            if not self.is_connected or not self.last_activity:
                return None
            return (datetime.now(UTC) - self.last_activity).total_seconds()

        @property
        @computed_field
        def is_healthy(self) -> bool:
            """Computed field indicating if connection is healthy."""
            if not self.is_connected:
                return False

            # Consider connection unhealthy if no activity for more than 1 hour
            max_idle_seconds = 3600  # 1 hour
            return not (
                self.connection_age_seconds
                and self.connection_age_seconds > max_idle_seconds
            )

        @property
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

        @property
        @computed_field
        def performance_info(self) -> str:
            """Computed field for connection performance information."""
            if not self.is_connected or self.connection_time is None:
                return "No performance data"

            # Performance thresholds
            excellent_threshold = 0.1
            good_threshold = 0.5
            acceptable_threshold = 2.0

            if self.connection_time < excellent_threshold:
                return f"Excellent ({self.connection_time:.3f}s)"
            if self.connection_time < good_threshold:
                return f"Good ({self.connection_time:.3f}s)"
            if self.connection_time < acceptable_threshold:
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
        """Query result using flext-core Entity with advanced Pydantic 2.11 features."""

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

        @property
        @computed_field
        def execution_time_seconds(self) -> float:
            """Computed field for execution time in seconds."""
            return self.execution_time_ms / 1000.0

        @property
        @computed_field
        def has_results(self) -> bool:
            """Computed field indicating if query returned results."""
            return self.row_count > 0

        @property
        @computed_field
        def column_count(self) -> int:
            """Computed field for number of columns."""
            return len(self.columns)

        @property
        @computed_field
        def performance_rating(self) -> str:
            """Computed field for query performance rating."""
            excellent_threshold_ms = 100
            good_threshold_ms = 500
            acceptable_threshold_ms = 2000

            if self.execution_time_ms < excellent_threshold_ms:
                return "excellent"
            if self.execution_time_ms < good_threshold_ms:
                return "good"
            if self.execution_time_ms < acceptable_threshold_ms:
                return "acceptable"
            return "slow"

        @property
        @computed_field
        def is_cached(self) -> bool:
            """Computed field indicating if query result was cached."""
            return self.query_hash is not None

        @model_validator(mode="after")
        def validate_query_result_consistency(self) -> FlextDbOracleModels.QueryResult:
            """Model validator for query result consistency."""
            # Ensure row count matches actual rows
            if len(self.rows) != self.row_count:
                msg = f"Row count ({self.row_count}) doesn't match actual rows ({len(self.rows)})"
                raise ValueError(msg)

            # Ensure each row has the correct number of columns
            if self.rows and self.columns:
                expected_columns = len(self.columns)
                for i, row in enumerate(self.rows):
                    if len(row) != expected_columns:
                        msg = f"Row {i} has {len(row)} columns, expected {expected_columns}"
                        raise ValueError(msg)

            # Validate execution time
            if self.execution_time_ms < 0:
                msg = "Execution time cannot be negative"
                raise ValueError(msg)

            return self

        @field_serializer("query")
        def serialize_query(self, value: str) -> str:
            """Field serializer for SQL query normalization."""
            # Normalize whitespace in SQL query
            return " ".join(value.split())

        @field_serializer("result_data")
        def serialize_result_data(
            self, value: list[FlextTypes.Dict]
        ) -> list[FlextTypes.Dict]:
            """Field serializer for result data with None handling."""
            # Convert None values to empty strings for JSON serialization
            serialized = []
            for row in value:
                serialized_row = {}
                for key, val in row.items():
                    serialized_row[key] = "" if val is None else val
                serialized.append(serialized_row)
            return serialized

        @field_serializer("explain_plan")
        def serialize_explain_plan(self, value: str | None) -> str | None:
            """Field serializer for explain plan formatting."""
            if value is None:
                return None
            # Clean up and format explain plan
            lines = value.split("\n")
            cleaned_lines = [line.strip() for line in lines if line.strip()]
            return "\n".join(cleaned_lines)

    class Table(FlextModels.Entity):
        """Oracle table using flext-core Entity."""

        name: str
        owner: str = "USER"
        columns: list[FlextDbOracleModels.Column] = Field(default_factory=list)

        @field_validator("name", "owner")
        @classmethod
        def validate_oracle_identifier(cls, v: str) -> str:
            """Validate Oracle identifiers using direct validation.

            Returns:
                str: Validated Oracle identifier.

            """
            # Oracle normalizes to uppercase
            upper_v = v.upper()

            # Basic validation
            if not isinstance(upper_v, str) or not upper_v.strip():
                msg = "Oracle identifier cannot be empty"
                raise ValueError(msg)

            # Length validation
            if (
                len(upper_v)
                > FlextDbOracleConstants.Validation.MAX_ORACLE_IDENTIFIER_LENGTH
            ):
                msg = f"Oracle identifier too long (max {FlextDbOracleConstants.Validation.MAX_ORACLE_IDENTIFIER_LENGTH} chars)"
                raise ValueError(msg)

            # Pattern validation
            if not re.match(
                FlextDbOracleConstants.Validation.ORACLE_IDENTIFIER_PATTERN,
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
            """Validate column name using direct validation.

            Returns:
                str: Validated column name.

            """
            # Oracle normalizes to uppercase
            upper_v = v.upper()

            # Basic validation
            if not isinstance(upper_v, str) or not upper_v.strip():
                msg = "Column name cannot be empty"
                raise ValueError(msg)

            # Length validation
            if (
                len(upper_v)
                > FlextDbOracleConstants.Validation.MAX_ORACLE_IDENTIFIER_LENGTH
            ):
                msg = f"Column name too long (max {FlextDbOracleConstants.Validation.MAX_ORACLE_IDENTIFIER_LENGTH} chars)"
                raise ValueError(msg)

            # Pattern validation
            if not re.match(
                FlextDbOracleConstants.Validation.ORACLE_IDENTIFIER_PATTERN,
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
            """Validate schema name using flext-core.

            Returns:
                str: Validated schema name.

            """
            # Direct validation using isinstance and basic checks
            schema_name = v.upper()

            # Length validation
            if not isinstance(schema_name, str) or len(schema_name) < 1:
                msg = "Schema name must be a non-empty string"
                raise ValueError(msg)
            if (
                len(schema_name)
                > FlextDbOracleConstants.Validation.MAX_ORACLE_IDENTIFIER_LENGTH
            ):
                msg = f"Schema name too long (max {FlextDbOracleConstants.Validation.MAX_ORACLE_IDENTIFIER_LENGTH} characters)"
                raise ValueError(msg)

            # Pattern validation
            if not re.match(
                FlextDbOracleConstants.Validation.ORACLE_IDENTIFIER_PATTERN,
                schema_name,
            ):
                msg = f"Invalid schema name format: {schema_name}"
                raise ValueError(msg)

            return schema_name

    class CreateIndexConfig(FlextModels.Entity):
        """Index creation config using flext-core Value."""

        index_name: str
        table_name: str
        columns: FlextTypes.StringList
        schema_name: str | None = None
        unique: bool = False
        tablespace: str | None = None
        parallel: int | None = None

    class MergeStatementConfig(FlextModels.Entity):
        """Merge statement config using flext-core Value."""

        target_table: str
        source_query: str
        merge_conditions: FlextTypes.StringList
        update_columns: FlextTypes.StringList = Field(default_factory=list)
        insert_columns: FlextTypes.StringList = Field(default_factory=list)


# ZERO TOLERANCE: No compatibility aliases - use FlextDbOracleModels.ClassName directly

__all__: FlextTypes.StringList = [
    "FlextDbOracleModels",
]


# ZERO TOLERANCE: All functionality accessed through FlextDbOracleModels unified class
