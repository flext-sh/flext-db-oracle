"""Oracle Database connection, operation and health models.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from datetime import datetime
from types import MappingProxyType
from typing import ClassVar

from flext_cli import m, u

from flext_db_oracle import c, t


class FlextModelsDbOracleConnection:
    """Oracle Database connection models composed into ``m.DbOracle``."""

    class ConnectionStatus(m.Entity):
        """Connection status using flext-core Entity."""

        model_config: ClassVar[m.ConfigDict] = m.ConfigDict(
            frozen=False, extra="ignore", strict=False
        )

        connected: bool = m.Field(
            default=False,
            description="Whether connection is active",
            validate_default=True,
        )
        last_check: datetime = m.Field(
            default_factory=u.now,
            description="Timestamp of last connection check",
        )
        error_message: str = m.Field(
            default="",
            description="Error message when disconnected",
            validate_default=True,
        )

        # Additional Oracle-specific connection details
        connection_time: t.NonNegativeFloat = m.Field(
            default=0.0,
            description="Connection establishment time in seconds",
            validate_default=True,
        )
        last_activity: datetime = m.Field(
            default_factory=u.now,
            description="Timestamp of last database activity",
        )
        session_id: str = m.Field(
            default="",
            description="Oracle session identifier",
            validate_default=True,
        )
        host: str = m.Field(
            default="",
            description="Database host",
            validate_default=True,
        )
        port: t.PortNumber = m.Field(
            default=c.DbOracle.DEFAULT_PORT,
            description="Database port",
            validate_default=True,
        )
        service_name: str = m.Field(
            default="",
            description="Oracle service name",
            validate_default=True,
        )
        username: str = m.Field(
            default="",
            description="Database username",
            validate_default=True,
        )
        db_version: str = m.Field(
            default="",
            description="Oracle database version",
            validate_default=True,
        )

        # return_type= kwarg dropped: it hit computed_field's kwargs-only
        # overload, which flext-core's `staticmethod(computed_field)` wrap
        # does not expose to pyrefly (flext-1wjg1.16 fleet defect); the
        # bare form already infers the type from the property annotation.
        @m.computed_field
        @property
        def connection_age_seconds(self) -> float:
            """Connection age in seconds."""
            if self.connected:
                current_time: datetime = u.now()
                age_seconds: float = (current_time - self.last_activity).total_seconds()
                return age_seconds
            return 0.0

        @m.computed_field
        @property
        def connection_info(self) -> str:
            """Connection information summary."""
            if not self.connected:
                return "Not connected"
            parts = [
                f"{k}={v}"
                for k, v in [
                    ("host", self.host),
                    ("port", self.port),
                    ("service", self.service_name),
                    (c.ContextScope.USER, self.username),
                ]
                if v  # Empty strings are falsy, so this works
            ]
            return ", ".join(parts) or "Connected"

        @m.computed_field
        @property
        def healthy(self) -> bool:
            """Connection health status."""
            if not self.connected:
                return False
            idle_timeout_seconds: float = float(
                c.DbOracle.CONNECTION_IDLE_TIMEOUT_SECONDS,
            )
            age_seconds: float = self.connection_age_seconds
            is_healthy: bool = age_seconds <= idle_timeout_seconds
            return is_healthy

        @m.computed_field
        @property
        def performance_info(self) -> str:
            """Connection performance information."""
            if not self.connected or self.connection_time <= 0:
                return "No performance data"
            if self.connection_time < c.DbOracle.CONNECTION_EXCELLENT_THRESHOLD_SECONDS:
                return f"Excellent ({self.connection_time:.3f}s)"
            if self.connection_time < c.DbOracle.CONNECTION_GOOD_THRESHOLD_SECONDS:
                return f"Good ({self.connection_time:.3f}s)"
            if (
                self.connection_time
                < c.DbOracle.CONNECTION_ACCEPTABLE_THRESHOLD_SECONDS
            ):
                return f"Acceptable ({self.connection_time:.3f}s)"
            return f"Slow ({self.connection_time:.3f}s)"

        @m.computed_field
        @property
        def status_description(self) -> str:
            """Human-readable status description."""
            if self.connected:
                return "Connected"
            return (
                f"Disconnected: {self.error_message}"
                if self.error_message
                else "Disconnected"
            )

        @m.field_serializer("connection_time", when_used="json")
        @staticmethod
        def serialize_connection_time(value: float) -> str:
            """Format connection time with units.

            Returns:
                The resulting ``str``.

            """
            return f"{value:.3f}s"

        @m.field_serializer("last_check", "last_activity", when_used="json")
        @staticmethod
        def serialize_datetime(value: datetime) -> str:
            """Format datetime as ISO string.

            Returns:
                The resulting ``str``.

            """
            return value.isoformat()

        @m.field_serializer("error_message")
        @staticmethod
        def serialize_error_message(value: str) -> str:
            """Truncate long error messages.

            Returns:
                The resulting ``str``.

            """
            max_error_length = c.DbOracle.MAX_ERROR_MESSAGE_LENGTH
            if len(value) > max_error_length:
                return f"{value[:max_error_length]}... (truncated)"
            return value

        @m.model_validator(mode="after")
        def validate_connection_status_consistency(
            self,
        ) -> FlextModelsDbOracleConnection.ConnectionStatus:
            """Validate connection status consistency.

            Returns:
                The resulting ``FlextModelsDbOracle.DbOracle.ConnectionStatus``.

            Raises:
                ValueError: If Connected status requires host information; or if
                    Invalid port number; or if Connection time cannot be negative.

            """
            if self.connected and not self.host:
                msg = "Connected status requires host information"
                raise ValueError(msg)
            if self.connected and not (
                c.DbOracle.MIN_PORT <= self.port <= c.DbOracle.MAX_PORT
            ):
                msg = f"Invalid port number: {self.port}"
                raise ValueError(msg)
            if self.connection_time < 0:
                msg = "Connection time cannot be negative"
                raise ValueError(msg)
            return self

    class OperationRecord(m.Entity):
        """Operation tracking record for observability workflows."""

        operation_type: str = m.Field(description="Type of database operation")
        duration: float = m.Field(description="Operation duration in seconds")
        success: bool = m.Field(description="Whether the operation succeeded")
        metadata_info: str = m.Field(
            default="",
            description="Operation metadata",
            validate_default=True,
        )
        timestamp: str = m.Field(description="ISO timestamp of operation")

    class HealthStatus(m.Entity):
        """Service health status record."""

        status: str = m.Field(description="Health status indicator")
        timestamp: str = m.Field(description="ISO timestamp of health check")
        service: str = m.Field(
            default="oracle",
            description="Service name being checked",
            validate_default=True,
        )
        database: str = m.Field(
            default="oracle",
            description="Database engine identifier",
            validate_default=True,
        )
        metrics: t.JsonMapping = m.Field(
            default_factory=lambda: MappingProxyType[str, t.JsonValue]({}),
            description="Health check metric values",
        )

        def __getitem__(self, key: str) -> t.JsonValue:
            """Get item from health status.

            Returns:
                The resulting ``t.JsonValue``.

            """
            if key in self.metrics:
                return self.metrics[key]
            dump = self.model_dump()
            value = dump.get(key, "")
            return str(value)

        def __contains__(self, key: str) -> bool:
            """Check if key is in health status.

            Returns:
                The resulting ``bool``.

            """
            if key in self.metrics:
                return True
            return key in self.model_dump()


__all__: list[str] = ["FlextModelsDbOracleConnection"]
