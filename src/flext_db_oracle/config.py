"""Oracle Database Configuration - Settings using flext-core patterns.

Provides Oracle-specific configuration management extending FlextConfig
with Pydantic Settings for environment variable support and validation.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from urllib.parse import urlparse

from flext_core import FlextConfig, FlextConstants, FlextResult
from pydantic import (
    Field,
    SecretStr,
    ValidationInfo,
    computed_field,
    field_validator,
)
from pydantic_settings import SettingsConfigDict

from flext_db_oracle.constants import FlextDbOracleConstants


@FlextConfig.auto_register("db_oracle")
class FlextDbOracleConfig(FlextConfig.AutoConfig):
    """Oracle Database Configuration using AutoConfig pattern.

    **ARCHITECTURAL PATTERN**: Zero-Boilerplate Auto-Registration

    This class uses FlextConfig.AutoConfig for automatic:
    - Singleton pattern (thread-safe)
    - Namespace registration (accessible via config.db_oracle)
    - Environment variable loading from FLEXT_DB_ORACLE_* variables
    - .env file loading (production/development)
    - Automatic type conversion and validation via Pydantic v2

    Provides complete configuration for Oracle database operations including
    connection settings, pool configuration, performance tuning, and security.
    """

    model_config = SettingsConfigDict(
        env_prefix="FLEXT_DB_ORACLE_",
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
        validate_assignment=True,
        str_strip_whitespace=True,
        validate_default=True,
        frozen=False,
        arbitrary_types_allowed=True,
        strict=False,
        json_schema_extra={
            "title": "FLEXT DB Oracle Configuration",
            "description": (
                "Enterprise Oracle database configuration extending FlextConfig"
            ),
        },
    )

    # Oracle Connection Configuration - matching model field names
    host: str = Field(
        default=FlextDbOracleConstants.OracleDefaults.DEFAULT_HOST,
        min_length=1,
        description="Oracle database hostname or IP address",
    )

    port: int = Field(
        default=FlextDbOracleConstants.Connection.DEFAULT_PORT,
        ge=1,
        le=65535,
        description="Oracle database port number",
    )

    service_name: str = Field(
        default=FlextDbOracleConstants.Connection.DEFAULT_SERVICE_NAME,
        min_length=1,
        description="Oracle service name",
    )

    name: str = Field(
        default=FlextDbOracleConstants.Connection.DEFAULT_DATABASE_NAME,
        min_length=1,
        description="Oracle database name",
    )

    sid: str = Field(
        default=FlextDbOracleConstants.Connection.DEFAULT_SID,
        min_length=1,
        description="Oracle SID (System Identifier)",
    )

    username: str = Field(
        default="",
        description="Oracle database username",
    )

    password: SecretStr = Field(
        default_factory=lambda: SecretStr(""),
        description="Oracle database password (sensitive)",
    )

    @computed_field
    def connection_string(self) -> str:
        """Computed Oracle connection string for SQLAlchemy."""
        # Build connection string using Oracle format
        user = self.username
        password = self.password.get_secret_value() if self.password else ""
        host = self.host
        port = self.port
        service = self.service_name

        return f"oracle+oracledb://{user}:{password}@{host}:{port}/{service}"

    charset: str = Field(
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
    timeout: int = Field(
        default=60,
        ge=1,
        le=3600,
        description="General timeout in seconds",
    )

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
        default=FlextConstants.Reliability.DEFAULT_RETRY_DELAY_SECONDS,
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
    @field_validator("service_name")
    @classmethod
    def validate_service_name(cls, v: str) -> str:
        """Validate Oracle service name (length check + uppercase transformation)."""
        # Check length
        if (
            len(v)
            > FlextDbOracleConstants.OracleValidation.MAX_ORACLE_IDENTIFIER_LENGTH
        ):
            msg = f"Oracle service name too long (max {FlextDbOracleConstants.OracleValidation.MAX_ORACLE_IDENTIFIER_LENGTH} chars)"
            raise ValueError(msg)

        return v.strip().upper()

    @field_validator("name")
    @classmethod
    def validate_database_name(cls, v: str) -> str:
        """Validate Oracle database name (length check + uppercase transformation)."""
        # Check length
        if (
            len(v)
            > FlextDbOracleConstants.OracleValidation.MAX_ORACLE_IDENTIFIER_LENGTH
        ):
            msg = f"Oracle database name too long (max {FlextDbOracleConstants.OracleValidation.MAX_ORACLE_IDENTIFIER_LENGTH} chars)"
            raise ValueError(msg)

        return v.strip().upper()

    @field_validator("sid")
    @classmethod
    def validate_sid(cls, v: str) -> str:
        """Validate Oracle SID (length check + uppercase transformation)."""
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
        if not self.host:
            return FlextResult[None].fail("Oracle host is required")

        if not self.username:
            return FlextResult[None].fail("Oracle username is required")

        if not self.password.get_secret_value():
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
        if self.service_name:
            return f"{self.host}:{self.port}/{self.service_name}"
        if self.sid:
            return f"{self.host}:{self.port}:{self.sid}"
        return f"{self.host}:{self.port}"

    def get_connection_config(self) -> dict[str, object]:
        """Get connection configuration (without exposing secrets)."""
        return {
            "host": self.host,
            "port": self.port,
            "service_name": self.service_name,
            "database_name": self.name,
            "sid": self.sid,
            "username": self.username,
            "charset": self.charset,
            "password_configured": bool(self.password.get_secret_value()),
        }

    @classmethod
    def from_env(cls, _prefix: str = "ORACLE_") -> FlextResult[FlextDbOracleConfig]:
        """Create OracleConfig from environment variables.

        **DEPRECATED**: Use `FlextDbOracleConfig.get_instance()` instead.
        AutoConfig automatically loads from FLEXT_DB_ORACLE_* environment variables.

        This method is kept for backward compatibility but uses Pydantic Settings
        automatically via AutoConfig pattern.

        Returns:
            FlextResult[FlextDbOracleConfig]: Configuration or error.

        """
        try:
            # Use AutoConfig singleton which automatically loads from environment
            # Pydantic Settings handles FLEXT_DB_ORACLE_* variables automatically
            config = cls.get_instance()
            return FlextResult[FlextDbOracleConfig].ok(config)
        except Exception as e:
            return FlextResult[FlextDbOracleConfig].fail(
                f"Failed to create config from environment: {e}"
            )

    @classmethod
    def from_url(cls, url: str) -> FlextResult[FlextDbOracleConfig]:
        """Create OracleConfig from Oracle URL string.

        Args:
        url: Oracle connection URL (oracle://user:pass@host:port/service)

        Returns:
        FlextResult[FlextDbOracleConfig]: Configuration or error.

        """
        try:
            # Parse the URL
            parsed = urlparse(url)
            if parsed.scheme != "oracle":
                return FlextResult[FlextDbOracleConfig].fail(
                    f"Invalid URL scheme: {parsed.scheme}. Expected 'oracle'"
                )

            # Extract components
            host = parsed.hostname
            port = parsed.port
            username = parsed.username
            password = parsed.password
            path = parsed.path.lstrip("/")  # Remove leading slash

            if not host:
                return FlextResult[FlextDbOracleConfig].fail("Host is required in URL")
            if not port:
                return FlextResult[FlextDbOracleConfig].fail("Port is required in URL")
            if not username:
                return FlextResult[FlextDbOracleConfig].fail(
                    "Username is required in URL"
                )
            if not password:
                return FlextResult[FlextDbOracleConfig].fail(
                    "Password is required in URL"
                )
            if not path:
                return FlextResult[FlextDbOracleConfig].fail(
                    "Service name is required in URL path"
                )

            # Create config
            config = FlextDbOracleConfig(
                host=host,
                port=port,
                username=username,
                password=password,
                service_name=path,
            )

            return FlextResult[FlextDbOracleConfig].ok(config)
        except Exception as e:
            return FlextResult[FlextDbOracleConfig].fail(
                f"Failed to create config from URL: {e}"
            )

    @classmethod
    def reset_global_instance(cls) -> None:
        """Reset the global FlextDbOracleConfig instance (mainly for testing)."""
        # Clear any cached instances
