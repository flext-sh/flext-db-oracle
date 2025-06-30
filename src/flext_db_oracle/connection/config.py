"""Oracle Database Connection Configuration."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class ConnectionConfig:
    """Oracle database connection configuration.

    Provides secure and validated configuration for Oracle database connections
    with support for various connection modes and security features.
    """

    host: str = "localhost"
    port: int = 1521
    sid: str | None = None
    service_name: str | None = None
    username: str = "user"
    password: str = "password"

    # Connection pool settings
    pool_min: int = 1
    pool_max: int = 10
    pool_increment: int = 1

    # Connection options
    timeout: int = 30
    autocommit: bool = False
    encoding: str = "UTF-8"

    # SSL/Security options
    ssl_enabled: bool = False
    ssl_cert_path: str | None = None
    ssl_key_path: str | None = None

    def __post_init__(self) -> None:
        """Validate configuration after initialization."""
        if not self.sid and not self.service_name:
            raise ValueError("Either sid or service_name must be provided")

        if self.port < 1 or self.port > 65535:
            raise ValueError("Port must be between 1 and 65535")

        if self.pool_min < 1:
            raise ValueError("pool_min must be at least 1")

        if self.pool_max < self.pool_min:
            raise ValueError("pool_max must be greater than or equal to pool_min")

    def to_dsn(self) -> str:
        """Generate Oracle DSN string from configuration.

        Returns:
            Oracle database DSN string for connection.
        """
        if self.sid:
            return f"{self.host}:{self.port}/{self.sid}"
        else:
            return f"{self.host}:{self.port}/{self.service_name}"

    def to_connect_params(self) -> dict[str, Any]:
        """Generate connection parameters dictionary.

        Returns:
            Dictionary of connection parameters for oracledb.connect().
        """
        params = {
            "host": self.host,
            "port": self.port,
            "user": self.username,
            "password": self.password,
            "encoding": self.encoding,
        }

        if self.sid:
            params["sid"] = self.sid
        elif self.service_name:
            params["service_name"] = self.service_name

        return params

    @classmethod
    def from_url(cls, url: str) -> ConnectionConfig:
        """Create configuration from database URL.

        Args:
            url: Database URL in format oracle://user:pass@host:port/service

        Returns:
            ConnectionConfig instance.
        """
        # Simple URL parsing - in production would use urllib.parse
        if not url.startswith("oracle://"):
            raise ValueError("URL must start with oracle://")

        # Extract components (simplified)
        url = url[9:]  # Remove oracle://
        if "@" in url:
            auth, location = url.split("@", 1)
            if ":" in auth:
                username, password = auth.split(":", 1)
            else:
                username = auth
                password = ""
        else:
            username = ""
            password = ""
            location = url

        if "/" in location:
            host_port, service = location.split("/", 1)
        else:
            host_port = location
            service = ""

        if ":" in host_port:
            host, port_str = host_port.split(":", 1)
            port = int(port_str)
        else:
            host = host_port
            port = 1521

        return cls(
            host=host,
            port=port,
            service_name=service if service else None,
            username=username,
            password=password,
        )
