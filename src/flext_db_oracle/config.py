"""Oracle Database Configuration - Settings using flext-core patterns.

Provides Oracle-specific configuration management extending FlextConfig
with Pydantic Settings for environment variable support and validation.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_core import (
    FlextConfig,
    FlextConstants,
    FlextResult,
    FlextTypes,
)
from pydantic import Field, SecretStr, ValidationInfo, computed_field, field_validator
from pydantic_settings import SettingsConfigDict

from flext_db_oracle.constants import FlextDbOracleConstants


class FlextDbOracleConfig(FlextConfig):
    """Oracle Database Configuration extending FlextConfig.

    Provides comprehensive configuration for Oracle database operations including
    connection settings, pool configuration, performance tuning, and security.
    Uses enhanced singleton pattern with inverse dependency injection.
    """

    model_config = SettingsConfigDict(
        env_prefix="FLEXT_DB_ORACLE_",
        case_sensitive=False,
        extra="ignore",
        use_enum_values=True,
        # Inherit enhanced Pydantic 2.11+ features from FlextConfig
        validate_assignment=True,
        str_strip_whitespace=True,
        json_schema_extra={
            "title": "FLEXT DB Oracle Configuration",
            "description": "Enterprise Oracle database configuration extending FlextConfig",
        },
    )

    # Oracle Connection Configuration
    oracle_host: str = Field(
        default=FlextDbOracleConstants.OracleDefaults.DEFAULT_HOST,
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

    # Backward compatibility properties for old attribute names
    @property
    def host(self) -> str:
        """Backward compatibility property for oracle_host."""
        return self.oracle_host

    @property
    def port(self) -> int:
        """Backward compatibility property for oracle_port."""
        return self.oracle_port

    @property
    def service_name(self) -> str:
        """Backward compatibility property for oracle_service_name."""
        return self.oracle_service_name

    @property
    def username(self) -> str:
        """Backward compatibility property for oracle_username."""
        return self.oracle_username

    @computed_field
    @property
    def connection_string(self) -> str:
        """Computed Oracle connection string for SQLAlchemy."""
        # Build connection string using Oracle format
        user = self.oracle_username
        password = (
            self.oracle_password.get_secret_value() if self.oracle_password else ""
        )
        host = self.oracle_host
        port = self.oracle_port
        service = self.oracle_service_name

        return f"oracle+oracledb://{user}:{password}@{host}:{port}/{service}"

    @property
    def protocol(self) -> str:
        """Backward compatibility property for connection protocol."""
        return "tcps"  # Default protocol for Oracle connections

    @property
    def ssl_enabled(self) -> bool:
        """Backward compatibility property for SSL configuration."""
        return True  # Default SSL enabled for Oracle connections

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
        default=FlextDbOracleConstants.OracleDefaults.DEFAULT_QUERY_TIMEOUT,
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
        default=FlextConstants.Reliability.MAX_RETRY_ATTEMPTS,
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
        default=FlextDbOracleConstants.OraclePerformance.PERFORMANCE_WARNING_THRESHOLD_SECONDS,
        ge=0.1,
        le=60.0,
        description="Performance warning threshold in seconds",
    )

    performance_threshold_critical: float = Field(
        default=float(FlextDbOracleConstants.Connection.DEFAULT_TIMEOUT),
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
        if (
            len(v)
            > FlextDbOracleConstants.OracleValidation.MAX_ORACLE_IDENTIFIER_LENGTH
        ):
            msg = f"Oracle service name too long (max {FlextDbOracleConstants.OracleValidation.MAX_ORACLE_IDENTIFIER_LENGTH} chars)"
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
        if (
            len(v)
            > FlextDbOracleConstants.OracleValidation.MAX_ORACLE_IDENTIFIER_LENGTH
        ):
            msg = f"Oracle database name too long (max {FlextDbOracleConstants.OracleValidation.MAX_ORACLE_IDENTIFIER_LENGTH} chars)"
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
        if (
            len(v)
            > FlextDbOracleConstants.OracleValidation.MAX_ORACLE_IDENTIFIER_LENGTH
        ):
            msg = f"Oracle SID too long (max {FlextDbOracleConstants.OracleValidation.MAX_ORACLE_IDENTIFIER_LENGTH} chars)"
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

    def get_connection_config(self) -> FlextTypes.Dict:
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
        """Create configuration for specific environment using enhanced singleton pattern."""
        return cls.get_or_create_shared_instance(
            "flext-db-oracle", environment=environment, **overrides
        )

    @classmethod
    def get_or_create_shared_instance(
        cls, project_name: str | None = None, **overrides: object
    ) -> FlextDbOracleConfig:
        """Create a new configuration instance with environment loading and overrides.

        Note: project_name parameter is required for parent class compatibility but not used.
        """
        # project_name is unused but required for parent class interface compatibility
        _ = project_name
        # Create instance to load from environment variables, then apply overrides
        instance = cls()
        for key, value in overrides.items():
            if hasattr(instance, key):
                setattr(instance, key, value)
        return instance

    @classmethod
    def create_default(cls) -> FlextDbOracleConfig:
        """Create default configuration instance using enhanced singleton pattern."""
        return cls.get_or_create_shared_instance("flext-db-oracle")

    @classmethod
    def get_global_instance(cls) -> FlextDbOracleConfig:
        """Get the global singleton instance using enhanced FlextConfig pattern."""
        # Create a default instance instead of using shared instance to avoid recursion
        return cls()

    @classmethod
    def reset_global_instance(cls) -> None:
        """Reset the global FlextDbOracleConfig instance (mainly for testing)."""
        # Use the enhanced FlextConfig reset mechanism
        if hasattr(cls, "reset_shared_instance"):
            cls.reset_shared_instance()
        else:
            # Fallback: clear any cached instances
            pass
