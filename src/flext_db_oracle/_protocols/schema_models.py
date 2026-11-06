# AUTO-GENERATED FILE — Regenerate with: make gen
"""Source-derived structural model contracts.

Copyright (c) 2026 FLEXT Team. All rights reserved.
src/flext_db_oracle/_protocols/schema_models
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import TYPE_CHECKING, Protocol, runtime_checkable

from flext_cli import FlextCliProtocols

if TYPE_CHECKING:
    from flext_cli import p

    from flext_db_oracle import t
    from flext_db_oracle._protocols import FlextDbOracleProtocolsQueryModels


class FlextDbOracleProtocolsSchemaModels:
    """Own the structural contracts declared by its model source."""

    @runtime_checkable
    class TableMetadata(FlextCliProtocols.BaseModel, Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def domain_events(self) -> Sequence[p.DomainEvent]:
            """List of uncommitted domain events for event sourcing."""
            ...

        table_name: str
        schema_name: str

        @property
        def columns(self) -> Sequence[FlextDbOracleProtocolsQueryModels.ColumnMetadata]:
            """Column metadata for the table."""
            ...

        primary_keys: Sequence[str]

        def __getitem__(self, key: str) -> t.JsonValue:
            """Get item from table metadata."""
            ...

        def __contains__(self, key: str) -> bool:
            """Check if key is in table metadata."""
            ...

    @runtime_checkable
    class TypeMapping(FlextCliProtocols.BaseModel, Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def domain_events(self) -> Sequence[p.DomainEvent]:
            """List of uncommitted domain events for event sourcing."""
            ...

        mapping: Mapping[str, str]

        def __getitem__(self, key: str) -> str:
            """Get mapped type for key."""
            ...

        def __len__(self) -> int:
            """Get number of type mappings."""
            ...

        def __contains__(self, key: str) -> bool:
            """Check if key is in type mapping."""
            ...

    @runtime_checkable
    class SingerField(FlextCliProtocols.BaseModel, Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def domain_events(self) -> Sequence[p.DomainEvent]:
            """List of uncommitted domain events for event sourcing."""
            ...

        type: str | Sequence[str]

    @runtime_checkable
    class SingerSchema(FlextCliProtocols.BaseModel, Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def domain_events(self) -> Sequence[p.DomainEvent]:
            """List of uncommitted domain events for event sourcing."""
            ...

        @property
        def properties(
            self,
        ) -> Mapping[str, FlextDbOracleProtocolsSchemaModels.SingerField]:
            """Singer schema property definitions."""
            ...

    @runtime_checkable
    class Table(FlextCliProtocols.BaseModel, Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def domain_events(self) -> Sequence[p.DomainEvent]:
            """List of uncommitted domain events for event sourcing."""
            ...

        name: str
        owner: str

        @property
        def columns(self) -> Sequence[FlextDbOracleProtocolsSchemaModels.Column]:
            """Column definitions for the table."""
            ...

    @runtime_checkable
    class Column(FlextCliProtocols.BaseModel, Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def domain_events(self) -> Sequence[p.DomainEvent]:
            """List of uncommitted domain events for event sourcing."""
            ...

        name: str
        data_type: str
        nullable: bool
        primary_key: bool
        default_value: str

        def __getitem__(self, key: str) -> t.JsonValue:
            """Get item from column metadata."""
            ...

        def __contains__(self, key: str) -> bool:
            """Check if key is in column metadata."""
            ...

    @runtime_checkable
    class Schema(FlextCliProtocols.BaseModel, Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def domain_events(self) -> Sequence[p.DomainEvent]:
            """List of uncommitted domain events for event sourcing."""
            ...

        name: str

        @property
        def tables(self) -> Sequence[FlextDbOracleProtocolsSchemaModels.Table]:
            """Tables within this schema."""
            ...

    @runtime_checkable
    class CreateIndexConfig(FlextCliProtocols.BaseModel, Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def domain_events(self) -> Sequence[p.DomainEvent]:
            """List of uncommitted domain events for event sourcing."""
            ...

        table_name: str
        index_name: str
        columns: Sequence[str]
        unique: bool
        schema_name: str
        tablespace: str
        parallel: t.PositiveInt


__all__: list[str] = [
    "FlextDbOracleProtocolsSchemaModels",
]
