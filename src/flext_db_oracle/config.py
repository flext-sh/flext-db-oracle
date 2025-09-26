"""Oracle Database Configuration - Settings using flext-core patterns.

Provides Oracle-specific configuration management extending FlextConfig
with Pydantic Settings for environment variable support and validation.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import threading
from typing import ClassVar

from pydantic import Field, SecretStr, ValidationInfo, field_validator
from pydantic_settings import SettingsConfigDict

from flext_core import FlextConfig, FlextResult
from flext_db_oracle.constants import FlextDbOracleConstants


class FlextDbOracleConfig(FlextConfig):
    """Oracle Database Configuration extending FlextConfig.

    Provides comprehensive configuration for Oracle database operations including
    connection settings, pool configuration, performance tuning, and security.
    Uses Pydantic BaseSettings for validation and environment variable support.
    """

    # Singleton pattern attributes
    _global_instance: ClassVar[FlextDbOracleConfig | None] = None
    _lock: ClassVar[threading.Lock] = threading.Lock()

    model_config = SettingsConfigDict(
        env_prefix="FLEXT_DB_ORACLE_",
        case_sensitive=False,
        extra="ignore",
        use_enum_values=True,
        validate_assignment=True,
        validate_default=True,
        frozen=False,
        # Pydantic 2.11 enhanced features
        arbitrary_types_allowed=True,
        validate_return=True,
        serialize_by_alias=True,
        populate_by_name=True,
        ser_json_timedelta="iso8601",
        ser_json_bytes="base64",
        str_strip_whitespace=True,
        enable_decoding=True,
        nested_model_default_partial_update=True,
    )

    # Oracle Connection Configuration
    oracle_host: str = Field(
        default=FlextDbOracleConstants.Defaults.DEFAULT_HOST,
        description="Oracle database hostname or IP address",
    )

    oracle_port: int = Field(
        default=FlextDbOracleConstants.Connection.DEFAULT_PORT,
        ge=1,
        le=65535,
        description="Oracle database port number",
    )

    oracle_service_name: str = Field(
        default=FlextDbOracleConstants.Connection.DEFAULT_SERVICE_NAME,
        description="Oracle service name",
    )

    oracle_database_name: str = Field(
        default=FlextDbOracleConstants.Connection.DEFAULT_DATABASE_NAME,
        description="Oracle database name",
    )

    oracle_sid: str = Field(
        default=FlextDbOracleConstants.Connection.DEFAULT_SID,
        description="Oracle SID (System Identifier)",
    )

    oracle_username: str = Field(
        default="",
        description="Oracle database username",
    )

    oracle_password: SecretStr = Field(
        default_factory=lambda: SecretStr(""),
        description="Oracle database password (sensitive)",
    )

    oracle_charset: str = Field(
        default=FlextDbOracleConstants.Connection.DEFAULT_CHARSET,
        description="Oracle database character set",
    )

    # Connection Pool Configuration
    pool_min: int = Field(
        default=FlextDbOracleConstants.Connection.DEFAULT_POOL_MIN,
        ge=1,
        le=100,
        description="Minimum number of connections in pool",
    )

    pool_max: int = Field(
        default=FlextDbOracleConstants.Connection.DEFAULT_POOL_MAX,
        ge=1,
        le=100,
        description="Maximum number of connections in pool",
    )

    pool_increment: int = Field(
        default=FlextDbOracleConstants.Connection.DEFAULT_POOL_INCREMENT,
        ge=1,
        le=10,
        description="Number of connections to increment when pool grows",
    )

    pool_timeout: int = Field(
        default=FlextDbOracleConstants.Connection.DEFAULT_POOL_TIMEOUT,
        ge=1,
        le=3600,
        description="Connection pool timeout in seconds",
    )

    # Performance Configuration
    query_timeout: int = Field(
        default=FlextDbOracleConstants.Defaults.DEFAULT_QUERY_TIMEOUT,
        ge=1,
        le=3600,
        description="Query timeout in seconds",
    )

    fetch_size: int = Field(
        default=FlextDbOracleConstants.Query.DEFAULT_ARRAY_SIZE,
        ge=1,
        le=10000,
        description="Default fetch size for queries",
    )

    max_retries: int = Field(
        default=3,
        ge=0,
        le=10,
        description="Maximum number of retry attempts",
    )

    retry_delay: float = Field(
        default=1.0,
        ge=0.1,
        le=60.0,
        description="Delay between retry attempts in seconds",
    )

    # Security Configuration
    use_ssl: bool = Field(
        default=False,
        description="Use SSL/TLS for database connection",
    )

    ssl_verify: bool = Field(
        default=True,
        description="Verify SSL certificates",
    )

    ssl_cert_file: str | None = Field(
        default=None,
        description="Path to SSL certificate file",
    )

    ssl_key_file: str | None = Field(
        default=None,
        description="Path to SSL private key file",
    )

    ssl_ca_file: str | None = Field(
        default=None,
        description="Path to SSL CA certificate file",
    )

    # Logging Configuration
    log_queries: bool = Field(
        default=False,
        description="Log SQL queries",
    )

    log_query_params: bool = Field(
        default=False,
        description="Log query parameters",
    )

    log_performance: bool = Field(
        default=False,
        description="Log query performance metrics",
    )

    performance_threshold_warning: float = Field(
        default=5.0,
        ge=0.1,
        le=60.0,
        description="Performance warning threshold in seconds",
    )

    performance_threshold_critical: float = Field(
        default=30.0,
        ge=0.1,
        le=300.0,
        description="Performance critical threshold in seconds",
    )

    # Validation methods
    @field_validator("oracle_service_name")
    @classmethod
    def validate_service_name(cls, v: str) -> str:
        """Validate Oracle service name."""
        if not v or not v.strip():
            msg = "Oracle service name cannot be empty"
            raise ValueError(msg)

        # Check length
        if len(v) > FlextDbOracleConstants.Validation.MAX_ORACLE_IDENTIFIER_LENGTH:
            msg = f"Oracle service name too long (max {FlextDbOracleConstants.Validation.MAX_ORACLE_IDENTIFIER_LENGTH} chars)"
            raise ValueError(msg)

        return v.strip().upper()

    @field_validator("oracle_database_name")
    @classmethod
    def validate_database_name(cls, v: str) -> str:
        """Validate Oracle database name."""
        if not v or not v.strip():
            msg = "Oracle database name cannot be empty"
            raise ValueError(msg)

        # Check length
        if len(v) > FlextDbOracleConstants.Validation.MAX_ORACLE_IDENTIFIER_LENGTH:
            msg = f"Oracle database name too long (max {FlextDbOracleConstants.Validation.MAX_ORACLE_IDENTIFIER_LENGTH} chars)"
            raise ValueError(msg)

        return v.strip().upper()

    @field_validator("oracle_sid")
    @classmethod
    def validate_sid(cls, v: str) -> str:
        """Validate Oracle SID."""
        if not v or not v.strip():
            msg = "Oracle SID cannot be empty"
            raise ValueError(msg)

        # Check length
        if len(v) > FlextDbOracleConstants.Validation.MAX_ORACLE_IDENTIFIER_LENGTH:
            msg = f"Oracle SID too long (max {FlextDbOracleConstants.Validation.MAX_ORACLE_IDENTIFIER_LENGTH} chars)"
            raise ValueError(msg)

        return v.strip().upper()

    @field_validator("pool_max")
    @classmethod
    def validate_pool_max(cls, v: int, info: ValidationInfo) -> int:
        """Validate pool_max is greater than pool_min."""
        if "pool_min" in info.data and v < info.data["pool_min"]:
            msg = "pool_max must be greater than or equal to pool_min"
            raise ValueError(msg)
        return v

    def validate_connection_config(self) -> FlextResult[None]:
        """Validate the complete connection configuration."""
        # Validate required fields
        if not self.oracle_host:
            return FlextResult[None].fail("Oracle host is required")

        if not self.oracle_username:
            return FlextResult[None].fail("Oracle username is required")

        if not self.oracle_password.get_secret_value():
            return FlextResult[None].fail("Oracle password is required")

        # Validate pool configuration
        if self.pool_max < self.pool_min:
            return FlextResult[None].fail(
                "pool_max must be greater than or equal to pool_min"
            )

        # Validate SSL configuration
        if self.use_ssl:
            if self.ssl_cert_file and not self.ssl_key_file:
                return FlextResult[None].fail(
                    "SSL key file is required when SSL cert file is provided"
                )

            if self.ssl_key_file and not self.ssl_cert_file:
                return FlextResult[None].fail(
                    "SSL cert file is required when SSL key file is provided"
                )

        return FlextResult[None].ok(None)

    def get_connection_string(self) -> str:
        """Generate Oracle connection string."""
        if self.oracle_service_name:
            return f"{self.oracle_host}:{self.oracle_port}/{self.oracle_service_name}"
        if self.oracle_sid:
            return f"{self.oracle_host}:{self.oracle_port}:{self.oracle_sid}"
        return f"{self.oracle_host}:{self.oracle_port}"

    def get_connection_config(self) -> dict[str, object]:
        """Get connection configuration (without exposing secrets)."""
        return {
            "host": self.oracle_host,
            "port": self.oracle_port,
            "service_name": self.oracle_service_name,
            "database_name": self.oracle_database_name,
            "sid": self.oracle_sid,
            "username": self.oracle_username,
            "charset": self.oracle_charset,
            "password_configured": bool(self.oracle_password.get_secret_value()),
        }

    @classmethod
    def create_for_environment(
        cls, environment: str, **overrides: object
    ) -> FlextDbOracleConfig:
        """Create configuration for specific environment."""
        return cls(environment=environment, **overrides)

    @classmethod
    def create_default(cls) -> FlextDbOracleConfig:
        """Create default configuration instance."""
        return cls()

    # Singleton pattern override for proper typing
    @classmethod
    def get_global_instance(cls) -> FlextDbOracleConfig:
        """Get the global singleton instance of FlextDbOracleConfig."""
        if cls._global_instance is None:
            with cls._lock:
                if cls._global_instance is None:
                    cls._global_instance = cls()
        return cls._global_instance

    @classmethod
    def reset_global_instance(cls) -> None:
        """Reset the global FlextDbOracleConfig instance (mainly for testing)."""
        cls._global_instance = None
