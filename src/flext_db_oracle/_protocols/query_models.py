# AUTO-GENERATED FILE — Regenerate with: make gen
"""Source-derived structural model contracts.

Copyright (c) 2026 FLEXT Team. All rights reserved.
src/flext_db_oracle/_protocols/query_models
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from collections.abc import Sequence
from typing import TYPE_CHECKING, Protocol, runtime_checkable

from flext_cli import FlextCliProtocols

from flext_db_oracle import t

if TYPE_CHECKING:
    from flext_cli import p


class FlextDbOracleProtocolsQueryModels:
    """Own the structural contracts declared by its model source."""

    @runtime_checkable
    class DbOracleDomainModel(FlextCliProtocols.Model, Protocol):
        """Structural data contract projected from the owning model."""

    @runtime_checkable
    class RowData(FlextCliProtocols.Model, Protocol):
        """Structural data contract projected from the owning model."""

        values: t.JsonList

    @runtime_checkable
    class ColumnMetadata(FlextCliProtocols.Model, Protocol):
        """Structural data contract projected from the owning model."""

        name: str
        data_type: str
        nullable: bool

    @runtime_checkable
    class QueryResult(FlextCliProtocols.Model, Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def domain_events(self) -> Sequence[p.DomainEvent]:
            """List of uncommitted domain events for event sourcing."""
            ...

        query: str
        result_data: t.JsonList
        row_count: t.NonNegativeInt
        execution_time_ms: t.NonNegativeInt
        columns: Sequence[str]

        @property
        def rows(self) -> Sequence[FlextDbOracleProtocolsQueryModels.RowData]:
            """Typed row data from query result."""
            ...

        query_hash: str
        explain_plan: str

        @property
        def column_count(self) -> int:
            """Number of columns."""
            ...

        @property
        def data_size_bytes(self) -> int:
            """Estimated data size in bytes."""
            ...

        @property
        def execution_time_seconds(self) -> float:
            """Execution time in seconds."""
            ...

        @property
        def has_results(self) -> bool:
            """Whether query returned results."""
            ...

        @property
        def memory_usage_mb(self) -> float:
            """Estimated memory usage in MB."""
            ...

        @property
        def performance_rating(self) -> str:
            """Query performance rating."""
            ...


__all__: list[str] = [
    "FlextDbOracleProtocolsQueryModels",
]
