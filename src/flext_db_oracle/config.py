"""Oracle Database Configuration - Settings using flext-core patterns.

Provides Oracle-specific configuration management extending FlextConfig
with Pydantic Settings for environment variable support and validation.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import ClassVar

from flext_core import (
    FlextConfig,
    FlextConstants,
    FlextResult,
    FlextTypes,
)
from pydantic import (
    Field,
    SecretStr,
    ValidationInfo,
    computed_field,
    field_validator,
)

from flext_db_oracle.constants import FlextDbOracleConstants


class FlextDbOracleConfig(FlextConfig):
    """Oracle Database Configuration extending FlextConfig.

    Provides comprehensive configuration for Oracle database operations including
    connection settings, pool configuration, performance tuning, and security.
    Uses enhanced singleton pattern with inverse dependency injection.
    """

    # Configuration inherited from FlextConfig with Oracle-specific env prefix
    model_config: ClassVar[dict] = {
        **FlextConfig.model_config,
        "env_prefix": "FLEXT_DB_ORACLE_",
        "json_schema_extra": {
            "title": "FLEXT DB Oracle Configuration",
            "description": "Enterprise Oracle database configuration extending FlextConfig",
        },
    }

    def __init__(self, **data: object) -> None:
        """Initialize Oracle configuration with keyword arguments."""
        # Extract required parameters for FlextConfig
        app_name = str(data.pop("app_name", "flext-db-oracle"))
        version = str(data.pop("version", "1.0.0"))
        environment = str(data.pop("environment", "development"))
        debug = bool(data.pop("debug", False))
        trace = bool(data.pop("trace", False))
        log_level = str(data.pop("log_level", "INFO"))
        json_output = data.pop("json_output", None)
        if json_output is not None:
            json_output = bool(json_output)
        include_source = bool(data.pop("include_source", True))
        structured_output = bool(data.pop("structured_output", False))
        log_verbosity = str(data.pop("log_verbosity", "normal"))
        log_format = str(
            data.pop(
                "log_format", "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )
        )
        log_file = data.pop("log_file", None)
        if log_file is not None:
            log_file = str(log_file)
        log_file_max_size = int(
            str(data.pop("log_file_max_size", "10485760"))
        )  # 10MB default
        log_file_backup_count = int(
            str(data.pop("log_file_backup_count", "5"))
        )  # 5 backups default
        console_enabled = bool(data.pop("console_enabled", True))
        console_color_enabled = bool(data.pop("console_color_enabled", True))
        track_performance = bool(data.pop("track_performance", False))
        track_timing = bool(data.pop("track_timing", False))
        include_context = bool(data.pop("include_context", True))
        include_correlation_id = bool(data.pop("include_correlation_id", True))
        mask_sensitive_data = bool(data.pop("mask_sensitive_data", True))
        database_url = data.pop("database_url", None)
        if database_url is not None:
            database_url = str(database_url)
        database_pool_size = int(
            str(data.pop("database_pool_size", "10"))
        )  # 10 connections default
        cache_ttl = int(str(data.pop("cache_ttl", "300")))  # 5 minutes default
        cache_max_size = int(
            str(data.pop("cache_max_size", "1000"))
        )  # 1000 items default
        secret_key = data.pop("secret_key", None)
        if secret_key is not None:
            from pydantic import SecretStr

            secret_key = SecretStr(str(secret_key))
        api_key = data.pop("api_key", None)
        if api_key is not None:
            from pydantic import SecretStr

            api_key = SecretStr(str(api_key))
        max_retry_attempts = int(
            str(data.pop("max_retry_attempts", "3"))
        )  # 3 retries default
        timeout_seconds = int(
            str(data.pop("timeout_seconds", "30"))
        )  # 30 seconds default
        enable_caching = bool(data.pop("enable_caching", True))
        enable_metrics = bool(data.pop("enable_metrics", True))
        enable_tracing = bool(data.pop("enable_tracing", False))
        jwt_expiry_minutes = int(
            str(data.pop("jwt_expiry_minutes", "60"))
        )  # 60 minutes default
        bcrypt_rounds = int(str(data.pop("bcrypt_rounds", "12")))  # 12 rounds default
        jwt_secret = str(data.pop("jwt_secret", "change-me-in-production"))
        max_workers = int(str(data.pop("max_workers", "10")))  # 10 workers default
        enable_circuit_breaker = bool(data.pop("enable_circuit_breaker", False))
        circuit_breaker_threshold = int(
            str(data.pop("circuit_breaker_threshold", "5"))
        )  # 5 failures default
        rate_limit_max_requests = int(
            str(data.pop("rate_limit_max_requests", "100"))
        )  # 100 requests default
        rate_limit_window_seconds = int(
            str(data.pop("rate_limit_window_seconds", "60"))
        )  # 60 seconds default
        batch_size = int(str(data.pop("batch_size", "100")))  # 100 items default
        cache_size = int(str(data.pop("cache_size", "1000")))  # 1000 items default
        retry_delay_seconds = float(
            str(data.pop("retry_delay_seconds", "1.0"))
        )  # 1.0 seconds default
        validation_timeout_ms = int(
            str(data.pop("validation_timeout_ms", "100"))
        )  # 100ms default
        validation_strict_mode = bool(data.pop("validation_strict_mode", False))
        serialization_encoding = str(data.pop("serialization_encoding", "utf-8"))
        dispatcher_auto_context = bool(data.pop("dispatcher_auto_context", True))
        dispatcher_timeout_seconds = int(
            str(data.pop("dispatcher_timeout_seconds", "30"))
        )  # 30 seconds default
        dispatcher_enable_metrics = bool(data.pop("dispatcher_enable_metrics", True))
        dispatcher_enable_logging = bool(data.pop("dispatcher_enable_logging", True))
        json_indent = int(str(data.pop("json_indent", "2")))  # 2 spaces default
        json_sort_keys = bool(data.pop("json_sort_keys", False))
        ensure_json_serializable = bool(data.pop("ensure_json_serializable", True))
        use_utc_timestamps = bool(data.pop("use_utc_timestamps", True))
        timestamp_auto_update = bool(data.pop("timestamp_auto_update", True))
        max_name_length = int(
            str(data.pop("max_name_length", "100"))
        )  # 100 chars default
        min_phone_digits = int(
            str(data.pop("min_phone_digits", "10"))
        )  # 10 digits default
        super().__init__(
            app_name=app_name,
            version=version,
            environment=environment,
            debug=debug,
            trace=trace,
            log_level=log_level,
            json_output=json_output,
            include_source=include_source,
            structured_output=structured_output,
            log_verbosity=log_verbosity,
            log_format=log_format,
            log_file=log_file,
            log_file_max_size=log_file_max_size,
            log_file_backup_count=log_file_backup_count,
            console_enabled=console_enabled,
            console_color_enabled=console_color_enabled,
            track_performance=track_performance,
            track_timing=track_timing,
            include_context=include_context,
            include_correlation_id=include_correlation_id,
            mask_sensitive_data=mask_sensitive_data,
            database_url=database_url,
            database_pool_size=database_pool_size,
            cache_ttl=cache_ttl,
            cache_max_size=cache_max_size,
            secret_key=secret_key,
            api_key=api_key,
            max_retry_attempts=max_retry_attempts,
            timeout_seconds=timeout_seconds,
            enable_caching=enable_caching,
            enable_metrics=enable_metrics,
            enable_tracing=enable_tracing,
            jwt_expiry_minutes=jwt_expiry_minutes,
            bcrypt_rounds=bcrypt_rounds,
            jwt_secret=jwt_secret,
            max_workers=max_workers,
            enable_circuit_breaker=enable_circuit_breaker,
            circuit_breaker_threshold=circuit_breaker_threshold,
            rate_limit_max_requests=rate_limit_max_requests,
            rate_limit_window_seconds=rate_limit_window_seconds,
            batch_size=batch_size,
            cache_size=cache_size,
            retry_delay_seconds=retry_delay_seconds,
            validation_timeout_ms=validation_timeout_ms,
            validation_strict_mode=validation_strict_mode,
            serialization_encoding=serialization_encoding,
            dispatcher_auto_context=dispatcher_auto_context,
            dispatcher_timeout_seconds=dispatcher_timeout_seconds,
            dispatcher_enable_metrics=dispatcher_enable_metrics,
            dispatcher_enable_logging=dispatcher_enable_logging,
            json_indent=json_indent,
            json_sort_keys=json_sort_keys,
            ensure_json_serializable=ensure_json_serializable,
            use_utc_timestamps=use_utc_timestamps,
            timestamp_auto_update=timestamp_auto_update,
            max_name_length=max_name_length,
            min_phone_digits=min_phone_digits,
            **data,
        )

    # Oracle Connection Configuration - matching model field names
    host: str = Field(
        default=FlextDbOracleConstants.OracleDefaults.DEFAULT_HOST,
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
        description="Oracle service name",
    )

    name: str = Field(
        default=FlextDbOracleConstants.Connection.DEFAULT_DATABASE_NAME,
        description="Oracle database name",
    )

    sid: str = Field(
        default=FlextDbOracleConstants.Connection.DEFAULT_SID,
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
    @property
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
    @field_validator("service_name")
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

    @field_validator("name")
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

    @field_validator("sid")
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

    def get_connection_config(self) -> FlextTypes.Dict:
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
    def from_env(cls, prefix: str = "ORACLE_") -> FlextResult[FlextDbOracleConfig]:
        """Create OracleConfig from environment variables.

        Args:
            prefix: Environment variable prefix (default: "ORACLE_")

        Returns:
            FlextResult[FlextDbOracleConfig]: Configuration or error.

        """
        try:
            import os

            # Extract environment variables
            host = os.getenv(f"{prefix}HOST", "localhost")
            port_str = os.getenv(f"{prefix}PORT", "1521")
            name = os.getenv(f"{prefix}NAME", "XE")
            username = os.getenv(f"{prefix}USERNAME", "")
            password = os.getenv(f"{prefix}PASSWORD")
            service_name = os.getenv(f"{prefix}SERVICE_NAME")
            sid = os.getenv(f"{prefix}SID")

            # Validate port
            try:
                port = int(port_str)
            except ValueError:
                return FlextResult[FlextDbOracleConfig].fail(
                    f"Invalid port: {port_str}"
                )

            # Create config
            config = FlextDbOracleConfig(
                host=host,
                port=port,
                name=name,
                username=username,
                password=password,
                service_name=service_name,
                sid=sid,
            )

            return FlextResult[FlextDbOracleConfig].ok(config)
        except Exception as e:
            return FlextResult[FlextDbOracleConfig].fail(
                f"Failed to create config from environment: {e}"
            )

    @classmethod
    def reset_global_instance(cls) -> None:
        """Reset the global FlextDbOracleConfig instance (mainly for testing)."""
        # Clear any cached instances
