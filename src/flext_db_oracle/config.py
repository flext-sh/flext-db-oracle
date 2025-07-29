"""Oracle Database Configuration using flext-core patterns."""

from __future__ import annotations

import os
import urllib.parse
from typing import Any

from flext_core import FlextResult, FlextValueObject, get_logger
from pydantic import ConfigDict, Field, SecretStr, field_validator, model_validator

from .constants import (
    ERROR_MSG_HOST_EMPTY,
    ERROR_MSG_USERNAME_EMPTY,
    MAX_PORT,
    ORACLE_DEFAULT_PORT,
)

logger = get_logger(__name__)


class FlextDbOracleConfig(FlextValueObject):
    """Oracle database configuration using flext-core patterns."""

    model_config = ConfigDict(extra="forbid")

    host: str = Field("localhost", description="Database host")
    port: int = Field(ORACLE_DEFAULT_PORT, description="Database port", ge=1, le=MAX_PORT)
    sid: str | None = Field(None, description="Oracle SID")
    service_name: str | None = Field(None, description="Oracle service name")
    username: str = Field("user", description="Database username")
    password: SecretStr = Field(SecretStr("password"), description="Database password")

    # Connection pool settings
    pool_min: int = Field(1, description="Minimum pool connections", ge=1)
    pool_max: int = Field(10, description="Maximum pool connections", ge=1)
    pool_increment: int = Field(1, description="Pool increment", ge=1)

    # Connection options
    timeout: int = Field(30, description="Connection timeout", ge=1)
    autocommit: bool = Field(default=False, description="Auto-commit transactions")
    encoding: str = Field("UTF-8", description="Character encoding")

    # SSL/Security options
    ssl_enabled: bool = Field(default=False, description="Enable SSL connection")
    ssl_cert_path: str | None = Field(None, description="SSL certificate path")
    ssl_key_path: str | None = Field(None, description="SSL key path")

    # Protocol options (from application services)
    protocol: str = Field("tcp", description="Connection protocol (tcp/tcps)")
    ssl_server_dn_match: bool = Field(default=True, description="SSL server DN match")
    ssl_server_cert_dn: str | None = Field(None, description="SSL server certificate DN")

    def validate_domain_rules(self) -> FlextResult[None]:
        """Validate Oracle connection configuration domain rules."""
        try:
            # Collect all validation errors
            errors = []

            # Validate that either SID or service_name is provided
            if not self.sid and not self.service_name:
                errors.append("Either SID or service_name must be provided")

            # Validate pool configuration
            if self.pool_max < self.pool_min:
                errors.append("pool_max must be >= pool_min")

            if self.pool_increment > self.pool_max:
                errors.append("pool_increment cannot exceed pool_max")

            # Validate SSL configuration
            if self.ssl_enabled and not self.ssl_cert_path:
                errors.append("ssl_cert_path required when SSL is enabled")

            # Validate host is not empty
            if not self.host or not self.host.strip():
                errors.append(ERROR_MSG_HOST_EMPTY)

            # Validate username is not empty
            if not self.username or not self.username.strip():
                errors.append(ERROR_MSG_USERNAME_EMPTY)

            if errors:
                return FlextResult.fail("; ".join(errors))

            return FlextResult.ok(None)

        except (ValueError, TypeError, AttributeError) as e:
            return FlextResult.fail(f"Configuration validation failed: {e}")

    @field_validator("host")
    @classmethod
    def validate_host(cls, v: str) -> str:
        """Validate host format."""
        if not v or not v.strip():
            raise ValueError(ERROR_MSG_HOST_EMPTY)
        return v.strip()

    @field_validator("username")
    @classmethod
    def validate_username(cls, v: str) -> str:
        """Validate username format."""
        if not v or not v.strip():
            raise ValueError(ERROR_MSG_USERNAME_EMPTY)
        return v.strip()

    @classmethod
    def from_env(cls, prefix: str = "FLEXT_TARGET_ORACLE_") -> FlextResult[FlextDbOracleConfig]:
        """Create configuration from environment variables."""
        try:
            config = cls(
                host=os.getenv(f"{prefix}HOST", "localhost"),
                port=int(os.getenv(f"{prefix}PORT", str(ORACLE_DEFAULT_PORT))),
                username=os.getenv(f"{prefix}USERNAME", "oracle"),
                password=SecretStr(os.getenv(f"{prefix}PASSWORD", "oracle")),
                service_name=os.getenv(f"{prefix}SERVICE_NAME"),
                sid=os.getenv(f"{prefix}SID"),
                pool_min=int(os.getenv(f"{prefix}POOL_MIN", "1")),
                pool_max=int(os.getenv(f"{prefix}POOL_MAX", "10")),
                pool_increment=int(os.getenv(f"{prefix}POOL_INCREMENT", "1")),
                timeout=int(os.getenv(f"{prefix}TIMEOUT", "30")),
                encoding=os.getenv(f"{prefix}ENCODING", "UTF-8"),
                ssl_cert_path=os.getenv(f"{prefix}SSL_CERT_PATH"),
                ssl_key_path=os.getenv(f"{prefix}SSL_KEY_PATH"),
                protocol=os.getenv(f"{prefix}PROTOCOL", "tcp"),
                ssl_server_cert_dn=os.getenv(f"{prefix}SSL_SERVER_CERT_DN"),
            )
            return FlextResult.ok(config)
        except (ValueError, TypeError, KeyError) as e:
            return FlextResult.fail(f"Failed to create config from environment: {e}")

    @classmethod
    def from_url(cls, url: str) -> FlextResult[FlextDbOracleConfig]:
        """Create configuration from connection URL."""
        try:
            # Parse Oracle URL format: oracle://user:pass@host:port/service_name
            parsed = urllib.parse.urlparse(url)

            config = cls(
                host=parsed.hostname or "localhost",
                port=parsed.port or ORACLE_DEFAULT_PORT,
                username=parsed.username or "oracle",
                password=SecretStr(parsed.password or "oracle"),
                service_name=parsed.path.lstrip("/") if parsed.path else None,
                sid=None,  # URL format typically uses service_name
                pool_min=1,
                pool_max=10,
                pool_increment=1,
                timeout=30,
                encoding="UTF-8",
                ssl_cert_path=None,
                ssl_key_path=None,
                protocol="tcp",
                ssl_server_cert_dn=None,
            )
            return FlextResult.ok(config)
        except (ValueError, TypeError, AttributeError) as e:
            return FlextResult.fail(f"Failed to parse URL: {e}")

    @model_validator(mode="after")
    def validate_connection_identifier(self) -> FlextDbOracleConfig:
        """Validate that either SID or service_name is provided."""
        if not self.sid and not self.service_name:
            msg = "Either SID or service_name must be provided"
            raise ValueError(msg)
        return self

    @model_validator(mode="after")
    def validate_pool_settings(self) -> FlextDbOracleConfig:
        """Validate pool configuration."""
        if self.pool_max < self.pool_min:
            msg = "pool_max must be >= pool_min"
            raise ValueError(msg)

        if self.pool_increment > self.pool_max:
            msg = "pool_increment cannot exceed pool_max"
            raise ValueError(msg)

        return self

    def to_connect_params(self) -> dict[str, Any]:
        """Convert to Oracle connection parameters."""
        params = {
            "host": self.host,
            "port": self.port,
            "user": self.username,
            "password": self.password.get_secret_value(),
            "encoding": self.encoding,
        }

        # Add connection identifier
        if self.service_name:
            params["service_name"] = self.service_name
        elif self.sid:
            params["sid"] = self.sid

        # Add SSL options if enabled
        if self.ssl_enabled:
            params["ssl_context"] = True
            if self.ssl_cert_path:
                params["ssl_cert_path"] = self.ssl_cert_path
            if self.ssl_key_path:
                params["ssl_key_path"] = self.ssl_key_path

        return params

    def to_pool_params(self) -> dict[str, Any]:
        """Convert to Oracle connection pool parameters."""
        connect_params = self.to_connect_params()

        # Add pool-specific parameters
        connect_params.update({
            "min": self.pool_min,
            "max": self.pool_max,
            "increment": self.pool_increment,
            "timeout": self.timeout,
        })

        return connect_params

    def get_connection_string(self) -> str:
        """Get Oracle connection string for logging purposes."""
        if self.service_name:
            return f"{self.host}:{self.port}/{self.service_name}"
        if self.sid:
            return f"{self.host}:{self.port}:{self.sid}"
        return f"{self.host}:{self.port}"

    @classmethod
    def from_dict(cls, config_dict: dict[str, Any]) -> FlextResult[FlextDbOracleConfig]:
        """Create configuration from dictionary with validation."""
        try:
            config = cls(**config_dict)
            validation_result = config.validate_domain_rules()

            if validation_result.is_failure:
                return FlextResult.fail(f"Configuration validation failed: {validation_result.error}")

            logger.info("Created Oracle connection config for %s", config.get_connection_string())
            return FlextResult.ok(config)

        except (ValueError, TypeError, KeyError) as e:
            return FlextResult.fail(f"Configuration creation failed: {e}")

    def __str__(self) -> str:
        """Return string representation without sensitive data."""
        return f"FlextDbOracleConfig(host={self.host}, port={self.port}, username={self.username}, service_name={self.service_name})"


__all__ = ["FlextDbOracleConfig"]
