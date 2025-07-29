"""Oracle Database Configuration using flext-core patterns."""

from __future__ import annotations

import os
from typing import Any

from flext_core import FlextResult, FlextValueObject, get_logger
from pydantic import ConfigDict, Field, SecretStr, field_validator, model_validator

logger = get_logger(__name__)


class FlextDbOracleConfig(FlextValueObject):
    """Oracle database configuration using flext-core patterns."""

    model_config = ConfigDict(extra="forbid")

    host: str = Field("localhost", description="Database host")
    port: int = Field(1521, description="Database port", ge=1, le=65535)
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
    ssl_server_dn_match: bool = Field(True, description="SSL server DN match")
    ssl_server_cert_dn: str | None = Field(None, description="SSL server certificate DN")

    def validate_domain_rules(self) -> FlextResult[None]:
        """Validate Oracle connection configuration domain rules."""
        try:
            # Validate that either SID or service_name is provided
            if not self.sid and not self.service_name:
                return FlextResult.fail("Either SID or service_name must be provided")

            # Validate pool configuration
            if self.pool_max < self.pool_min:
                return FlextResult.fail("pool_max must be >= pool_min")

            if self.pool_increment > self.pool_max:
                return FlextResult.fail("pool_increment cannot exceed pool_max")

            # Validate SSL configuration
            if self.ssl_enabled:
                if not self.ssl_cert_path:
                    return FlextResult.fail("ssl_cert_path required when SSL is enabled")

            # Validate host is not empty
            if not self.host or not self.host.strip():
                return FlextResult.fail("Host cannot be empty")

            # Validate username is not empty
            if not self.username or not self.username.strip():
                return FlextResult.fail("Username cannot be empty")

            return FlextResult.ok(None)

        except Exception as e:
            return FlextResult.fail(f"Configuration validation failed: {e}")

    @field_validator("host")
    @classmethod
    def validate_host(cls, v: str) -> str:
        """Validate host format."""
        if not v or not v.strip():
            msg = "Host cannot be empty"
            raise ValueError(msg)
        return v.strip()

    @field_validator("username")
    @classmethod
    def validate_username(cls, v: str) -> str:
        """Validate username format."""
        if not v or not v.strip():
            msg = "Username cannot be empty"
            raise ValueError(msg)
        return v.strip()

    @classmethod
    def from_env(cls, prefix: str = "FLEXT_TARGET_ORACLE_") -> FlextResult[FlextDbOracleConfig]:
        """Create configuration from environment variables."""
        try:
            config = cls(
                host=os.getenv(f"{prefix}HOST", "localhost"),
                port=int(os.getenv(f"{prefix}PORT", "1521")),
                username=os.getenv(f"{prefix}USERNAME", "oracle"),
                password=os.getenv(f"{prefix}PASSWORD", "oracle"),
                service_name=os.getenv(f"{prefix}SERVICE_NAME"),
                sid=os.getenv(f"{prefix}SID"),
            )
            return FlextResult.ok(config)
        except Exception as e:
            return FlextResult.fail(f"Failed to create config from environment: {e}")

    @classmethod
    def from_url(cls, url: str) -> FlextResult[FlextDbOracleConfig]:
        """Create configuration from connection URL."""
        try:
            # Parse Oracle URL format: oracle://user:pass@host:port/service_name
            import urllib.parse
            parsed = urllib.parse.urlparse(url)

            config = cls(
                host=parsed.hostname or "localhost",
                port=parsed.port or 1521,
                username=parsed.username or "oracle",
                password=parsed.password or "oracle",
                service_name=parsed.path.lstrip("/") if parsed.path else None,
            )
            return FlextResult.ok(config)
        except Exception as e:
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
    
    def build_oracle_dsn(self) -> FlextResult[str]:
        """Build Oracle DSN with protocol support (consolidated from services)."""
        try:
            import oracledb
            
            if self.protocol == "tcps":
                # For TCPS, build custom DSN string with SSL options
                service_or_sid = (
                    f"SERVICE_NAME={self.service_name}"
                    if self.service_name
                    else f"SID={self.sid}"
                )
                dsn = (
                    f"(DESCRIPTION=(ADDRESS=(PROTOCOL=TCPS)"
                    f"(HOST={self.host})(PORT={self.port}))"
                    f"(CONNECT_DATA=({service_or_sid})))"
                )
                return FlextResult.ok(dsn)
            
            # For TCP, use standard makedsn
            if self.service_name:
                dsn = oracledb.makedsn(
                    host=self.host,
                    port=self.port,
                    service_name=self.service_name,
                )
            elif self.sid:
                dsn = oracledb.makedsn(
                    host=self.host,
                    port=self.port,
                    sid=self.sid,
                )
            else:
                return FlextResult.fail("Must provide either service_name or sid")
            
            return FlextResult.ok(dsn)
            
        except Exception as e:
            return FlextResult.fail(f"DSN building failed: {e}")
    
    def to_oracledb_params(self) -> dict[str, Any]:
        """Convert to native oracledb connection parameters (consolidated)."""
        dsn_result = self.build_oracle_dsn()
        if dsn_result.is_failure:
            raise ValueError(f"Cannot build DSN: {dsn_result.error}")
            
        params = {
            "user": self.username,
            "password": self.password.get_secret_value(),
            "dsn": dsn_result.data,
        }
        
        # Add SSL options for TCPS
        if self.protocol == "tcps":
            params["ssl_server_dn_match"] = self.ssl_server_dn_match
            if self.ssl_server_cert_dn:
                params["ssl_server_cert_dn"] = self.ssl_server_cert_dn
                
        return params

    @classmethod
    def from_dict(cls, config_dict: dict[str, Any]) -> FlextResult[FlextDbOracleConfig]:
        """Create configuration from dictionary with validation."""
        try:
            config = cls(**config_dict)
            validation_result = config.validate_domain_rules()

            if validation_result.is_failure:
                return FlextResult.fail(f"Configuration validation failed: {validation_result.error}")

            logger.info(f"Created Oracle connection config for {config.get_connection_string()}")
            return FlextResult.ok(config)

        except Exception as e:
            return FlextResult.fail(f"Configuration creation failed: {e}")

    def __str__(self) -> str:
        """String representation without sensitive data."""
        return f"FlextDbOracleConfig(host={self.host}, port={self.port}, username={self.username}, service_name={self.service_name})"


__all__ = ["FlextDbOracleConfig"]
