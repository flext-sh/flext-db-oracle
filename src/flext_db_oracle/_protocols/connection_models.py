# AUTO-GENERATED FILE — Regenerate with: make gen
"""Source-derived structural model contracts.

Copyright (c) 2026 FLEXT Team. All rights reserved.
src/flext_db_oracle/_protocols/connection_models
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from collections.abc import Sequence
from datetime import datetime
from typing import TYPE_CHECKING, Protocol, runtime_checkable

from flext_cli import FlextCliProtocols

if TYPE_CHECKING:
    from flext_cli import p

    from flext_db_oracle import t
    from flext_db_oracle._typings import FlextDbOracleTypesDbOracle


class FlextDbOracleProtocolsConnectionModels:
    """Own the structural contracts declared by its model source."""

    @runtime_checkable
    class ConnectionStatus(FlextCliProtocols.Model, Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def domain_events(self) -> Sequence[p.DomainEvent]:
            """List of uncommitted domain events for event sourcing."""
            ...

        connected: bool
        last_check: datetime
        error_message: str
        connection_time: t.NonNegativeFloat
        last_activity: datetime
        session_id: str
        host: str
        port: t.PortNumber
        service_name: str
        username: str
        db_version: str

        @property
        def connection_age_seconds(self) -> float:
            """Connection age in seconds."""
            ...

        @property
        def connection_info(self) -> str:
            """Connection information summary."""
            ...

        @property
        def healthy(self) -> bool:
            """Connection health status."""
            ...

        @property
        def performance_info(self) -> str:
            """Connection performance information."""
            ...

        @property
        def status_description(self) -> str:
            """Human-readable status description."""
            ...

    @runtime_checkable
    class EngineOptions(FlextCliProtocols.Model, Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def dsn(self) -> str | None:
            """TNS descriptor or alias; None = host/port/service of the URL."""
            ...

        @property
        def mode(self) -> FlextDbOracleTypesDbOracle.DbOracle.PrivilegeMode | None:
            """Oracledb privilege mode (SYSDBA/SYSOPER); None = normal."""
            ...

        @property
        def connect_timeout(self) -> int | None:
            """TCP connect timeout in seconds."""
            ...

        @property
        def pool_size(self) -> int | None:
            """Pool size; None = SQLAlchemy default."""
            ...

        @property
        def max_overflow(self) -> int | None:
            """Pool overflow; None = SQLAlchemy default."""
            ...

        @property
        def pool_recycle(self) -> int:
            """Seconds before a pooled connection is recycled."""
            ...

    @runtime_checkable
    class OperationRecord(FlextCliProtocols.Model, Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def domain_events(self) -> Sequence[p.DomainEvent]:
            """List of uncommitted domain events for event sourcing."""
            ...

        operation_type: str
        duration: float
        success: bool
        metadata_info: str
        timestamp: str

    @runtime_checkable
    class HealthStatus(FlextCliProtocols.Model, Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def domain_events(self) -> Sequence[p.DomainEvent]:
            """List of uncommitted domain events for event sourcing."""
            ...

        status: str
        timestamp: str
        service: str
        database: str
        metrics: t.JsonMapping

        def __getitem__(self, key: str) -> t.JsonValue:
            """Get item from health status."""
            ...

        def __contains__(self, key: str) -> bool:
            """Check if key is in health status."""
            ...


__all__: list[str] = [
    "FlextDbOracleProtocolsConnectionModels",
]
