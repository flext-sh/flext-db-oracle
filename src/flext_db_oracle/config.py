"""Oracle Database Configuration.

Using flext-core BaseConfig patterns for consistent configuration management.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from flext_core import FlextValueObject as BaseConfig
from pydantic import Field, SecretStr, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from flext_db_oracle.connection.config import ConnectionConfig

if TYPE_CHECKING:
    from pydantic import ValidationInfo



class FlextDbOracleConfig(BaseConfig):
    """Oracle database configuration using flext-core patterns."""

    # Connection settings
    host: str = Field("localhost", description="Oracle database host")
    port: int = Field(1521, ge=1, le=65535, description="Oracle database port")
    service_name: str | None = Field(None, description="Oracle service name")
    sid: str | None = Field(None, description="Oracle SID")
    username: str = Field(..., description="Database username")
    password: str = Field(..., description="Database password")
    protocol: str = Field("tcp", description="Connection protocol (tcp or tcps)")

    # Connection pool settings
    pool_min_size: int = Field(1, ge=1, description="Minimum pool connections")
    pool_max_size: int = Field(10, ge=1, description="Maximum pool connections")
    pool_increment: int = Field(1, ge=1, description="Pool increment size")

    # Query settings
    query_timeout: int = Field(30, ge=1, description="Query timeout in seconds")
    fetch_size: int = Field(
        1000,
        ge=1,
        description="Default fetch size for large queries",
    )

    # Connection settings
    connect_timeout: int = Field(10, ge=1, description="Connection timeout in seconds")
    retry_attempts: int = Field(3, ge=0, description="Connection retry attempts")
    retry_delay: float = Field(
        1.0,
        ge=0,
        description="Delay between retries in seconds",
    )

    @model_validator(mode="after")
    def validate_service_or_sid(self) -> FlextDbOracleConfig:
        """Ensure either service_name or sid is provided."""
        if not self.service_name and not self.sid:
            msg = "Either service_name or sid must be provided"
            raise ValueError(msg)
        return self

    @field_validator("pool_max_size")
    @classmethod
    def validate_pool_max_greater_than_min(cls, v: int, info: ValidationInfo) -> int:
        """Ensure max pool size is greater than or equal to min."""
        if info.data:
            min_size = info.data.get("pool_min_size", 1)
            if v < min_size:
                msg = (
                    f"pool_max_size ({v}) must be greater than or equal to "
                    f"pool_min_size ({min_size})"
                )
                raise ValueError(msg)
        return v

    @property
    def database_identifier(self) -> str:
        """Get the database identifier (service_name or sid)."""
        return self.service_name or self.sid or "unknown"

    @property
    def connection_string(self) -> str:
        """Generate safe connection string for logging."""
        return f"oracle://{self.username}:***@{self.host}:{self.port}/{self.database_identifier}"

    def validate_domain_rules(self) -> None:
        """Validate domain rules for Oracle configuration."""
        # Additional domain validation beyond Pydantic
        if not self.host.strip():
            msg = "Host cannot be empty"
            raise ValueError(msg)
        if not self.username.strip():
            msg = "Username cannot be empty"
            raise ValueError(msg)
        if not self.password.strip():
            msg = "Password cannot be empty"
            raise ValueError(msg)

        # Validate port range is reasonable for Oracle
        if self.port < 1 or self.port > 65535:
            msg = f"Port {self.port} is not in valid range 1-65535"
            raise ValueError(msg)

        # Validate protocol
        valid_protocols = {"tcp", "tcps"}
        if self.protocol.lower() not in valid_protocols:
            msg = f"Protocol must be one of {valid_protocols}"
            raise ValueError(msg)

        # Validate pool settings
        if self.pool_max_size < self.pool_min_size:
            msg = "pool_max_size must be >= pool_min_size"
            raise ValueError(msg)

        # Validate timeout settings are reasonable
        if self.query_timeout <= 0:
            msg = "Query timeout must be positive"
            raise ValueError(msg)
        if self.connect_timeout <= 0:
            msg = "Connect timeout must be positive"
            raise ValueError(msg)

    @classmethod
    def from_url(cls, url: str) -> FlextDbOracleConfig:
        """Create configuration from Oracle connection URL.

        Args:
            url: Oracle connection URL in format: oracle://user:pass@host:port/service_name

        Returns:
            FlextDbOracleConfig instance

        Raises:
            ValueError: If URL format is invalid

        """
        if not url.startswith("oracle://"):
            msg = "URL must start with 'oracle://'"
            raise ValueError(msg)

        # Parse URL: oracle://user:pass@host:port/service_name
        try:
            url_content = url[9:]  # Remove oracle://
            credentials, connection_part = url_content.split("@")
            username, password = credentials.split(":")
            host_part, service_name = connection_part.split("/")
            host, port = host_part.split(":")

            return cls(
                host=host,
                port=int(port),
                username=username,
                password=password,
                service_name=service_name,
                sid=None,
            )
        except (ValueError, IndexError) as e:
            msg = f"Invalid Oracle URL format: {e}"
            raise ValueError(msg) from e

    def to_connection_config(self) -> ConnectionConfig:
        """Convert to ConnectionConfig for connection layer compatibility.

        Returns:
            ConnectionConfig instance with mapped fields

        """
        return ConnectionConfig(
            host=self.host,
            port=self.port,
            username=self.username,
            password=SecretStr(self.password),
            service_name=self.service_name,
            sid=self.sid,
            protocol=self.protocol,
            pool_min=self.pool_min_size,
            pool_max=self.pool_max_size,
            pool_increment=self.pool_increment,
            timeout=self.connect_timeout,
        )

    @classmethod
    def from_env(cls, env_prefix: str = "FLEXT_TARGET_ORACLE_") -> FlextDbOracleConfig:
        """Create configuration from environment variables (meltano pattern).

        Args:
            env_prefix: Environment variable prefix

        Returns:
            FlextDbOracleConfig instance loaded from environment

        """

        # Use temporary settings class for env loading
        class _TempSettings(BaseSettings):
            host: str = Field("localhost", description="Oracle database host")
            port: int = Field(1521, ge=1, le=65535, description="Oracle database port")
            service_name: str | None = Field(None, description="Oracle service name")
            sid: str | None = Field(None, description="Oracle SID")
            username: str = Field(..., description="Database username")
            password: str = Field(..., description="Database password")
            protocol: str = Field("tcp", description="Connection protocol")
            pool_min_size: int = Field(1, ge=1, description="Minimum pool connections")
            pool_max_size: int = Field(10, ge=1, description="Maximum pool connections")
            pool_increment: int = Field(1, ge=1, description="Pool increment size")
            query_timeout: int = Field(30, ge=1, description="Query timeout in seconds")
            fetch_size: int = Field(1000, ge=1, description="Default fetch size")
            connect_timeout: int = Field(10, ge=1, description="Connection timeout")
            retry_attempts: int = Field(
                3,
                ge=0,
                description="Connection retry attempts",
            )
            retry_delay: float = Field(1.0, ge=0, description="Delay between retries")

            model_config = SettingsConfigDict(
                env_prefix=env_prefix,
                case_sensitive=False,
            )

        # Load from environment
        temp_config = _TempSettings()

        # Create FlextDbOracleConfig with loaded values
        return cls(
            host=temp_config.host,
            port=temp_config.port,
            service_name=temp_config.service_name,
            sid=temp_config.sid,
            username=temp_config.username,
            password=temp_config.password,
            protocol=temp_config.protocol,
            pool_min_size=temp_config.pool_min_size,
            pool_max_size=temp_config.pool_max_size,
            pool_increment=temp_config.pool_increment,
            query_timeout=temp_config.query_timeout,
            fetch_size=temp_config.fetch_size,
            connect_timeout=temp_config.connect_timeout,
            retry_attempts=temp_config.retry_attempts,
            retry_delay=temp_config.retry_delay,
        )

    def __str__(self) -> str:
        """Safe string representation without sensitive data."""
        return (
            f"FlextDbOracleConfig(host={self.host}, port={self.port}, "
            f"service_name={self.service_name}, username={self.username})"
        )


# Alias for backward compatibility
OracleConfig = FlextDbOracleConfig
