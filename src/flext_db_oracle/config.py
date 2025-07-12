"""Oracle Database Configuration.

Using flext-core BaseConfig patterns for consistent configuration management.
"""

from __future__ import annotations

from pydantic import ConfigDict, Field, field_validator

from flext_core import BaseConfig


class OracleConfig(BaseConfig):
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
    fetch_size: int = Field(1000, ge=1, description="Default fetch size for large queries")

    # Connection settings
    connect_timeout: int = Field(10, ge=1, description="Connection timeout in seconds")
    retry_attempts: int = Field(3, ge=0, description="Connection retry attempts")
    retry_delay: float = Field(1.0, ge=0, description="Delay between retries in seconds")

    @field_validator("service_name", "sid", mode="before")
    @classmethod
    def validate_service_or_sid(cls, v, info):
        """Ensure either service_name or sid is provided."""
        if info.data:
            service_name = info.data.get("service_name")
            sid = info.data.get("sid")

            if not service_name and not sid and not v:
                msg = "Either service_name or sid must be provided"
                raise ValueError(msg)
        return v

    @field_validator("pool_max_size")
    @classmethod
    def validate_pool_max_greater_than_min(cls, v, info):
        """Ensure max pool size is greater than or equal to min."""
        if info.data:
            min_size = info.data.get("pool_min_size", 1)
            if v < min_size:
                msg = "pool_max_size must be >= pool_min_size"
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

    model_config = ConfigDict(
        env_prefix="FLEXT_TARGET_ORACLE_",
        case_sensitive=False,
    )
