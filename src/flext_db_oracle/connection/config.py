"""Oracle Database Connection Configuration - Modern Python 3.13 + flext-core patterns."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from pydantic import Field, SecretStr, field_validator, model_validator

from flext_core.config import BaseConfig

if TYPE_CHECKING:
    from pydantic import ValidationInfo


class ConnectionConfig(BaseConfig):
    """Oracle database connection configuration.

    REFACTORED:
        Uses flext-core BaseConfig with modern validation patterns.
    Provides secure and validated configuration for Oracle database connections
    with support for various connection modes and security features.
    """

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
    autocommit: bool = Field(False, description="Auto-commit transactions")
    encoding: str = Field("UTF-8", description="Character encoding")

    # SSL/Security options
    ssl_enabled: bool = Field(False, description="Enable SSL connection")
    ssl_cert_path: str | None = Field(None, description="SSL certificate path")
    ssl_key_path: str | None = Field(None, description="SSL key path")
    ssl_server_dn_match: bool = Field(True, description="Verify SSL server DN")
    protocol: str = Field("tcp", description="Connection protocol (tcp/tcps)")  # For Oracle Cloud

    @field_validator("pool_max")
    @classmethod
    def validate_pool_max(cls, v: int, info: ValidationInfo) -> int:
        """Validate that pool_max >= pool_min."""
        if hasattr(info, "data") and "pool_min" in info.data:
            pool_min = info.data.get("pool_min", 1)
            if v < pool_min:
                msg = f"pool_max ({v}) must be >= pool_min ({pool_min})"
                raise ValueError(msg)
        return v

    @model_validator(mode="after")
    def validate_connection_identifier(self) -> ConnectionConfig:
        """Validate that either SID or service_name is provided."""
        if not self.sid and not self.service_name:
            msg = "Either 'service_name' or 'sid' must be provided"
            raise ValueError(msg)
        return self

    def to_connect_params(self) -> dict[str, Any]:
        """Convert configuration to oracledb connection parameters."""
        params = {
            "host": self.host,
            "port": self.port,
            "user": self.username,
            "password": self.password.get_secret_value(),
            # "encoding": self.encoding,  # Not supported in modern oracledb
        }

        # Add SID or service_name
        if self.service_name:
            params["service_name"] = self.service_name
        elif self.sid:
            params["sid"] = self.sid

        # Add protocol (tcp/tcps for SSL)
        if self.protocol:
            params["protocol"] = self.protocol

        # Add SSL parameters if enabled
        if self.ssl_enabled:
            if self.ssl_cert_path:
                params["wallet_location"] = self.ssl_cert_path
            if not self.ssl_server_dn_match:
                params["ssl_server_dn_match"] = False

        return params

    def get_dsn(self) -> str:
        """Get Oracle DSN string."""
        if self.service_name:
            return f"{self.host}:{self.port}/{self.service_name}"
        if self.sid:
            return f"{self.host}:{self.port}:{self.sid}"
        msg = "Either service_name or sid must be configured"
        raise ValueError(msg)

    def test_connection_params(self) -> bool:
        """Validate connection parameters."""
        try:
            self.to_connect_params()
            return True
        except Exception:
            return False

    @classmethod
    def from_url(cls, url: str) -> ConnectionConfig:
        """Create configuration from Oracle connection URL.

        Example: oracle://user:pass@host:port/service_name
        """
        # Simple URL parsing - could be enhanced with urllib.parse
        if not url.startswith("oracle://"):
            msg = "URL must start with 'oracle://'"
            raise ValueError(msg)

        # Basic parsing for now - this could be made more robust
        url_parts = url[9:].split("@")  # Remove oracle://
        if len(url_parts) != 2:
            msg = "Invalid URL format"
            raise ValueError(msg)

        credentials, connection_part = url_parts
        user, password = credentials.split(":")
        host_part, service_name = connection_part.split("/")
        host, port = host_part.split(":")

        return cls(
            host=host,
            port=int(port),
            username=user,
            password=SecretStr(password),
            service_name=service_name,
        )

    def __repr__(self) -> str:
        """Safe representation without password."""
        return (
            f"ConnectionConfig(host={self.host}, port={self.port}, "
            f"username={self.username}, service_name={self.service_name})"
        )


# Alias for backward compatibility
OracleConnectionConfig = ConnectionConfig
