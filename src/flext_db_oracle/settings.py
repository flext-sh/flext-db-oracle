"""Oracle Database Configuration - Settings using flext-core patterns.

Provides Oracle-specific configuration management extending FlextSettings
with Pydantic Settings for environment variable support and validation.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from urllib.parse import urlparse

from flext_core import r
from flext_core.settings import FlextSettings
from pydantic import (
    Field,
    SecretStr,
    ValidationInfo,
    computed_field,
    field_validator,
)
from pydantic_settings import SettingsConfigDict

from flext_db_oracle.constants import c


@FlextSettings.auto_register("db_oracle")
class FlextDbOracleSettings(FlextSettings):
    """Oracle Database Configuration using AutoConfig pattern.

    **ARCHITECTURAL PATTERN**: Zero-Boilerplate Auto-Registration

    This class uses FlextSettings.AutoConfig for automatic:
    - Singleton pattern (thread-safe)
    - Namespace registration (accessible via config.db_oracle)
    - Environment variable loading from FLEXT_DB_ORACLE_* variables
    - .env file loading (production/development)
    - Automatic type conversion and validation via Pydantic v2

    Provides complete configuration for Oracle database operations including
    connection settings, pool configuration, performance tuning, and security.
    """

    # Use FlextSettings.resolve_env_file() to ensure all FLEXT configs use same .env
    model_config = SettingsConfigDict(
        env_prefix="FLEXT_DB_ORACLE_",
        env_file=FlextSettings.resolve_env_file(),
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
                "Enterprise Oracle database configuration extending FlextSettings"
            ),
        },
    )

    # Oracle Connection Configuration - matching model field names
    host: str = Field(
        default=c.DbOracle.OracleDefaults.DEFAULT_HOST,
        min_length=1,
        description="Oracle database hostname or IP address",
    )

    port: int = Field(
        default=c.DbOracle.Connection.DEFAULT_PORT,
        ge=1,
        le=c.DbOracle.OracleNetwork.MAX_PORT,
        description="Oracle database port number",
    )

    service_name: str = Field(
        default=c.DbOracle.Connection.DEFAULT_SERVICE_NAME,
        min_length=1,
        description="Oracle service name",
    )

    name: str = Field(
        default=c.DbOracle.Connection.DEFAULT_DATABASE_NAME,
        min_length=1,
        description="Oracle database name",
    )

    sid: str = Field(
        default=c.DbOracle.Connection.DEFAULT_SID,
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
        default=c.DbOracle.Connection.DEFAULT_CHARSET,
        description="Oracle database character set",
    )

    # Connection Pool Configuration
    pool_min: int = Field(
        default=c.DbOracle.Connection.DEFAULT_POOL_MIN,
        ge=1,
        le=c.DbOracle.Query.DEFAULT_ARRAY_SIZE,
        description="Minimum number of connections in pool",
    )

    pool_max: int = Field(
        default=c.DbOracle.Connection.DEFAULT_POOL_MAX,
        ge=1,
        le=c.DbOracle.Query.DEFAULT_ARRAY_SIZE,
        description="Maximum number of connections in pool",
    )

    pool_increment: int = Field(
        default=c.DbOracle.Connection.DEFAULT_POOL_INCREMENT,
        ge=1,
        le=c.DbOracle.Connection.DEFAULT_POOL_MAX // 2,  # Half of max pool size
        description="Number of connections to increment when pool grows",
    )

    pool_timeout: int = Field(
        default=c.DbOracle.Connection.DEFAULT_POOL_TIMEOUT,
        ge=1,
        le=c.DbOracle.Query.MAX_QUERY_TIMEOUT,
        description="Connection pool timeout in seconds",
    )

    # Performance Configuration
    timeout: int = Field(
        default=c.DbOracle.Connection.DEFAULT_TIMEOUT,
        ge=1,
        le=c.DbOracle.Query.MAX_QUERY_TIMEOUT,
        description="General timeout in seconds",
    )

    query_timeout: int = Field(
        default=c.DbOracle.OracleDefaults.DEFAULT_QUERY_TIMEOUT,
        ge=1,
        le=c.DbOracle.Query.MAX_QUERY_TIMEOUT,
        description="Query timeout in seconds",
    )

    fetch_size: int = Field(
        default=c.DbOracle.Query.DEFAULT_ARRAY_SIZE,
        ge=1,
        le=c.DbOracle.Query.MAX_QUERY_ROWS // 10,  # 1/10 of max query rows
        description="Default fetch size for queries",
    )

    max_retries: int = Field(
        default=c.Reliability.MAX_RETRY_ATTEMPTS,
        ge=0,
        le=c.DbOracle.Connection.DEFAULT_POOL_MAX // 2,  # Half of max pool size
        description="Maximum number of retry attempts",
    )

    retry_delay: int = Field(
        default=c.Reliability.DEFAULT_RETRY_DELAY_SECONDS,
        ge=1,
        le=int(c.Reliability.DEFAULT_MAX_DELAY_SECONDS),
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
        default=c.DbOracle.OraclePerformance.PERFORMANCE_WARNING_THRESHOLD_SECONDS,
        ge=0.1,
        le=c.Reliability.DEFAULT_MAX_DELAY_SECONDS,
        description="Performance warning threshold in seconds",
    )

    performance_threshold_critical: float = Field(
        default=float(c.DbOracle.Connection.DEFAULT_TIMEOUT),
        ge=0.1,
        le=300.0,  # 5 minutes max for performance threshold
        description="Performance critical threshold in seconds",
    )

    # Validation methods
    @field_validator("service_name", mode="before")
    @classmethod
    def validate_service_name(cls, v: str) -> str:
        """Validate Oracle service name (length check + uppercase transformation)."""
        # Check length
        if len(v) > c.DbOracle.OracleValidation.MAX_ORACLE_IDENTIFIER_LENGTH:
            msg = f"Oracle service name too long (max {c.DbOracle.OracleValidation.MAX_ORACLE_IDENTIFIER_LENGTH} chars)"
            raise ValueError(msg)

        return v.strip().upper()

    @field_validator("name", mode="before")
    @classmethod
    def validate_database_name(cls, v: str) -> str:
        """Validate Oracle database name (length check + uppercase transformation)."""
        # Check length
        if len(v) > c.DbOracle.OracleValidation.MAX_ORACLE_IDENTIFIER_LENGTH:
            msg = f"Oracle database name too long (max {c.DbOracle.OracleValidation.MAX_ORACLE_IDENTIFIER_LENGTH} chars)"
            raise ValueError(msg)

        return v.strip().upper()

    @field_validator("sid", mode="before")
    @classmethod
    def validate_sid(cls, v: str) -> str:
        """Validate Oracle SID (length check + uppercase transformation)."""
        # Check length
        if len(v) > c.DbOracle.OracleValidation.MAX_ORACLE_IDENTIFIER_LENGTH:
            msg = f"Oracle SID too long (max {c.DbOracle.OracleValidation.MAX_ORACLE_IDENTIFIER_LENGTH} chars)"
            raise ValueError(msg)

        return v.strip().upper()

    @field_validator("pool_max", mode="before")
    @classmethod
    def validate_pool_max(cls, v: int, info: ValidationInfo) -> int:
        """Validate pool_max is greater than pool_min."""
        if "pool_min" in info.data and v < info.data["pool_min"]:
            msg = "pool_max must be greater than or equal to pool_min"
            raise ValueError(msg)
        return v

    def validate_connection_config(self) -> r[None]:
        """Validate the complete connection configuration."""
        # Validate required fields
        if not self.host:
            return r[None].fail("Oracle host is required")

        if not self.username:
            return r[None].fail("Oracle username is required")

        if not self.password.get_secret_value():
            return r[None].fail("Oracle password is required")

        # Validate pool configuration
        if self.pool_max < self.pool_min:
            return r[None].fail(
                "pool_max must be greater than or equal to pool_min",
            )

        # Validate SSL configuration
        if self.use_ssl:
            if self.ssl_cert_file and not self.ssl_key_file:
                return r[None].fail(
                    "SSL key file is required when SSL cert file is provided",
                )

            if self.ssl_key_file and not self.ssl_cert_file:
                return r[None].fail(
                    "SSL cert file is required when SSL key file is provided",
                )

        return r[None].ok(None)

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
    def from_env(cls, _prefix: str = "ORACLE_") -> r[FlextDbOracleSettings]:
        """Create OracleConfig from environment variables.

        **DEPRECATED**: Use `FlextDbOracleSettings.get_global_instance()` instead.
        AutoConfig automatically loads from FLEXT_DB_ORACLE_* environment variables.

        This method is kept for backward compatibility but uses Pydantic Settings
        automatically via AutoConfig pattern.

        Returns:
            r[FlextDbOracleSettings]: Configuration or error.

        """
        try:
            # Use AutoConfig singleton which automatically loads from environment
            # Pydantic Settings handles FLEXT_DB_ORACLE_* variables automatically
            config = cls.get_global_instance()
            return r[FlextDbOracleSettings].ok(config)
        except Exception as e:
            return r[FlextDbOracleSettings].fail(
                f"Failed to create config from environment: {e}",
            )

    @classmethod
    def from_url(cls, url: str) -> r[FlextDbOracleSettings]:
        """Create OracleConfig from Oracle URL string.

        Args:
        url: Oracle connection URL (oracle://user:pass@host:port/service)

        Returns:
        r[FlextDbOracleSettings]: Configuration or error.

        """
        try:
            # Parse the URL
            parsed = urlparse(url)
            if parsed.scheme != "oracle":
                return r[FlextDbOracleSettings].fail(
                    f"Invalid URL scheme: {parsed.scheme}. Expected 'oracle'",
                )

            # Extract components
            host = parsed.hostname
            port = parsed.port
            username = parsed.username
            password = parsed.password
            path = parsed.path.lstrip("/")  # Remove leading slash

            if not host:
                return r[FlextDbOracleSettings].fail("Host is required in URL")
            if not port:
                return r[FlextDbOracleSettings].fail("Port is required in URL")
            if not username:
                return r[FlextDbOracleSettings].fail(
                    "Username is required in URL",
                )
            if not password:
                return r[FlextDbOracleSettings].fail(
                    "Password is required in URL",
                )
            if not path:
                return r[FlextDbOracleSettings].fail(
                    "Service name is required in URL path",
                )

            # Create config
            config = FlextDbOracleSettings(
                host=host,
                port=port,
                username=username,
                password=password,
                service_name=path,
            )

            return r[FlextDbOracleSettings].ok(config)
        except Exception as e:
            return r[FlextDbOracleSettings].fail(
                f"Failed to create config from URL: {e}",
            )

    @classmethod
    def reset_global_instance(cls) -> None:
        """Reset the global FlextDbOracleSettings instance (mainly for testing)."""
        # Clear any cached instances
