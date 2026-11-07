# AUTO-GENERATED FILE — Regenerate with: make gen
"""Source-derived structural model contracts.

Copyright (c) 2026 FLEXT Team. All rights reserved.
src/flext_db_oracle/_protocols/command_models
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


class FlextDbOracleProtocolsCommandModels:
    """Own the structural contracts declared by its model source."""

    @runtime_checkable
    class ConnectCommand(FlextCliProtocols.BaseModel, Protocol):
        """Structural data contract projected from the owning model."""

        version: t.NonNegativeInt
        unique_id: t.NonEmptyStr

        @property
        def created_at(self) -> datetime:
            """Creation timestamp (configured timezone)."""
            ...

        updated_at: datetime | None

        @property
        def domain_events(self) -> Sequence[p.DomainEvent]:
            """List of uncommitted domain events for event sourcing."""
            ...

    @runtime_checkable
    class DisconnectCommand(FlextCliProtocols.BaseModel, Protocol):
        """Structural data contract projected from the owning model."""

        version: t.NonNegativeInt
        unique_id: t.NonEmptyStr

        @property
        def created_at(self) -> datetime:
            """Creation timestamp (configured timezone)."""
            ...

        updated_at: datetime | None

        @property
        def domain_events(self) -> Sequence[p.DomainEvent]:
            """List of uncommitted domain events for event sourcing."""
            ...

    @runtime_checkable
    class TestConnectionCommand(FlextCliProtocols.BaseModel, Protocol):
        """Structural data contract projected from the owning model."""

        version: t.NonNegativeInt
        unique_id: t.NonEmptyStr

        @property
        def created_at(self) -> datetime:
            """Creation timestamp (configured timezone)."""
            ...

        updated_at: datetime | None

        @property
        def domain_events(self) -> Sequence[p.DomainEvent]:
            """List of uncommitted domain events for event sourcing."""
            ...

    @runtime_checkable
    class ExecuteQueryCommand(FlextCliProtocols.BaseModel, Protocol):
        """Structural data contract projected from the owning model."""

        version: t.NonNegativeInt
        unique_id: t.NonEmptyStr

        @property
        def created_at(self) -> datetime:
            """Creation timestamp (configured timezone)."""
            ...

        updated_at: datetime | None

        @property
        def domain_events(self) -> Sequence[p.DomainEvent]:
            """List of uncommitted domain events for event sourcing."""
            ...

        sql: str
        parameters: t.JsonMapping | None

    @runtime_checkable
    class FetchOneCommand(FlextCliProtocols.BaseModel, Protocol):
        """Structural data contract projected from the owning model."""

        version: t.NonNegativeInt
        unique_id: t.NonEmptyStr

        @property
        def created_at(self) -> datetime:
            """Creation timestamp (configured timezone)."""
            ...

        updated_at: datetime | None

        @property
        def domain_events(self) -> Sequence[p.DomainEvent]:
            """List of uncommitted domain events for event sourcing."""
            ...

        sql: str
        parameters: t.JsonMapping | None

    @runtime_checkable
    class ExecuteStatementCommand(FlextCliProtocols.BaseModel, Protocol):
        """Structural data contract projected from the owning model."""

        version: t.NonNegativeInt
        unique_id: t.NonEmptyStr

        @property
        def created_at(self) -> datetime:
            """Creation timestamp (configured timezone)."""
            ...

        updated_at: datetime | None

        @property
        def domain_events(self) -> Sequence[p.DomainEvent]:
            """List of uncommitted domain events for event sourcing."""
            ...

        sql: str
        parameters: t.JsonMapping | None

    @runtime_checkable
    class ExecuteManyCommand(FlextCliProtocols.BaseModel, Protocol):
        """Structural data contract projected from the owning model."""

        version: t.NonNegativeInt
        unique_id: t.NonEmptyStr

        @property
        def created_at(self) -> datetime:
            """Creation timestamp (configured timezone)."""
            ...

        updated_at: datetime | None

        @property
        def domain_events(self) -> Sequence[p.DomainEvent]:
            """List of uncommitted domain events for event sourcing."""
            ...

        sql: str
        parameters_list: Sequence[t.JsonMapping]

    @runtime_checkable
    class GetSchemasCommand(FlextCliProtocols.BaseModel, Protocol):
        """Structural data contract projected from the owning model."""

        version: t.NonNegativeInt
        unique_id: t.NonEmptyStr

        @property
        def created_at(self) -> datetime:
            """Creation timestamp (configured timezone)."""
            ...

        updated_at: datetime | None

        @property
        def domain_events(self) -> Sequence[p.DomainEvent]:
            """List of uncommitted domain events for event sourcing."""
            ...

    @runtime_checkable
    class GetTablesCommand(FlextCliProtocols.BaseModel, Protocol):
        """Structural data contract projected from the owning model."""

        version: t.NonNegativeInt
        unique_id: t.NonEmptyStr

        @property
        def created_at(self) -> datetime:
            """Creation timestamp (configured timezone)."""
            ...

        updated_at: datetime | None

        @property
        def domain_events(self) -> Sequence[p.DomainEvent]:
            """List of uncommitted domain events for event sourcing."""
            ...

        schema_name: str | None

    @runtime_checkable
    class GetColumnsCommand(FlextCliProtocols.BaseModel, Protocol):
        """Structural data contract projected from the owning model."""

        version: t.NonNegativeInt
        unique_id: t.NonEmptyStr

        @property
        def created_at(self) -> datetime:
            """Creation timestamp (configured timezone)."""
            ...

        updated_at: datetime | None

        @property
        def domain_events(self) -> Sequence[p.DomainEvent]:
            """List of uncommitted domain events for event sourcing."""
            ...

        table: str
        schema_name: str | None


__all__: list[str] = [
    "FlextDbOracleProtocolsCommandModels",
]
