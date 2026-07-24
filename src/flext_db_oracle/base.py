"""Base service mixin for flext-db-oracle.

Provides shared state, typed contracts, and SQLAlchemy wrappers
for all DB Oracle service mixins.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import time
from typing import TYPE_CHECKING

from sqlalchemy import Engine as SAEngine

from flext_core import s
from flext_db_oracle import FlextDbOracleSettings, m, p, r, t, u
from flext_db_oracle._utilities.db_oracle import FlextDbOracleUtilitiesDbOracle

if TYPE_CHECKING:
    from collections.abc import MutableMapping, MutableSequence, Sequence


class FlextDbOracleServiceBase(s, FlextDbOracleUtilitiesDbOracle):
    """Base mixin providing static helpers and SQLAlchemy wrappers.

    All service mixins inherit from this base, which provides:
    - Shared Oracle service state and configuration access
    - Oracle exception type aliases
    - Parameter normalization
    - SQLAlchemy engine/connection wrappers
    - Count parsing utilities
    """

    _db_config: FlextDbOracleSettings | None = u.PrivateAttr()
    _engine: SAEngine | None = u.PrivateAttr(default_factory=lambda: None)
    _operations: MutableSequence[m.DbOracle.OperationRecord] = u.PrivateAttr(
        default_factory=list[m.DbOracle.OperationRecord]
    )
    _plugins: MutableMapping[str, t.JsonPayload] = u.PrivateAttr(
        default_factory=dict[str, t.JsonPayload]
    )
    _metrics: t.MutableJsonMapping = u.PrivateAttr(default_factory=dict)

    def __init__(self, settings: FlextDbOracleSettings) -> None:
        """Initialize shared Oracle service state."""
        super().__init__()
        self._db_config = settings

    @property
    def db_config(self) -> FlextDbOracleSettings:
        """The initialized Oracle database configuration."""
        settings = self._db_config
        if settings is None:
            msg = "Database configuration not initialized"
            raise RuntimeError(msg)
        return settings

    def connected(self) -> bool:
        """Check if the service has an active SQLAlchemy engine."""
        return self._engine is not None

    def _parse_count_from_rows(self, rows: t.SequenceOf[m.Dict]) -> int:
        """Parse COUNT(*) value from normalized query rows."""
        if not rows:
            return 0
        count_raw = rows[0].root.get("count")
        if count_raw is None:
            return 0
        return self._parse_count_value(str(count_raw))

    def _get_current_timestamp(self) -> str:
        """Get current timestamp for operation tracking."""
        return str(int(time.time()))

    def _get_engine(self) -> p.Result[SAEngine]:
        """Get database engine."""
        engine = self._engine
        if engine is None or not self.connected():
            return r[SAEngine].fail("Not connected to database")
        return r[SAEngine].ok(engine)

    def execute_query(
        self, sql: str, params: m.ConfigMap | None = None
    ) -> p.Result[Sequence[m.Dict]]:
        """Execute a SQL query in composed service facades."""
        del sql, params
        msg = "execute_query requires the composed DB Oracle service facade"
        raise NotImplementedError(msg)


s = FlextDbOracleServiceBase

__all__: list[str] = ["FlextDbOracleServiceBase", "s"]
