"""Base service mixin for flext-db-oracle.

Provides shared state, typed contracts, and SQLAlchemy wrappers
for all DB Oracle service mixins.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import contextlib
import time
from collections.abc import MutableMapping, MutableSequence, Sequence

from pydantic import PrivateAttr, RootModel, ValidationError
from sqlalchemy import (
    Connection as SAConnection,
    Engine as SAEngine,
    TextClause,
    create_engine,
    text,
)
from sqlalchemy.engine import CursorResult

from flext_core import r, s
from flext_db_oracle import (
    FlextDbOracleModels,
    FlextDbOracleSettings,
    FlextDbOracleTypes as t,
)


class FlextDbOracleServiceBase(s[FlextDbOracleSettings]):
    """Base mixin providing static helpers and SQLAlchemy wrappers.

    All service mixins inherit from this base, which provides:
    - Shared Oracle service state and configuration access
    - Oracle exception type aliases
    - Parameter normalization
    - SQLAlchemy engine/connection wrappers
    - Count parsing utilities
    """

    _db_config: FlextDbOracleSettings | None = PrivateAttr(default=None)
    _engine: SAEngine | None = PrivateAttr(default=None)
    _operations: MutableSequence[FlextDbOracleModels.DbOracle.OperationRecord] = (
        PrivateAttr(
            default_factory=lambda: list[
                FlextDbOracleModels.DbOracle.OperationRecord
            ](),
        )
    )
    _plugins: MutableMapping[str, t.ContainerValue] = PrivateAttr(
        default_factory=lambda: dict[str, t.ContainerValue](),
    )
    _metrics: MutableMapping[str, t.ContainerValue] = PrivateAttr(
        default_factory=lambda: dict[str, t.ContainerValue](),
    )

    class _CountValue(RootModel[int | str]):
        """Pydantic root model for count value (int or numeric string)."""

        root: int | str

    def __init__(self, config: FlextDbOracleSettings) -> None:
        """Initialize shared Oracle service state."""
        super().__init__()
        self._db_config = config
        self._config = config

    @property
    def db_config(self) -> FlextDbOracleSettings:
        """Return initialized Oracle database configuration."""
        config = self._db_config
        if config is None:
            msg = "Database configuration not initialized"
            raise RuntimeError(msg)
        return config

    def connected(self) -> bool:
        """Check if the service has an active SQLAlchemy engine."""
        return self._engine is not None

    @staticmethod
    def _validate_config_map(value: t.ContainerValue) -> t.ConfigMap | None:
        """Validate arbitrary mapping input as ConfigMap."""
        if not isinstance(value, dict):
            return None
        try:
            return t.ConfigMap.model_validate({"root": value})
        except ValidationError:
            return None

    @staticmethod
    def _normalize_params(params: t.ConfigMap | None) -> t.ConfigMap:
        """Normalize optional parameters into ConfigMap."""
        if params is not None:
            return params
        return t.ConfigMap(root={})

    @staticmethod
    def _parse_count_value(value: t.ContainerValue) -> int:
        """Parse row count value accepting int or numeric string."""
        if isinstance(value, int):
            return value
        if isinstance(value, str):
            try:
                return int(value)
            except ValueError:
                return 0
        try:
            validated = FlextDbOracleServiceBase._CountValue.model_validate(value).root
        except ValidationError:
            return 0
        try:
            return int(validated)
        except (TypeError, ValueError):
            return 0

    def _parse_count_from_rows(self, rows: Sequence[t.Dict]) -> int:
        """Parse COUNT(*) value from normalized query rows."""
        if not rows:
            return 0
        count_raw = rows[0].root.get("count")
        if count_raw is None:
            return 0
        return self._parse_count_value(str(count_raw))

    @staticmethod
    def _normalize_singer_type(value: str | t.StrSequence) -> str:
        """Normalize Singer type input to a single string value."""
        try:
            values = t.STR_SEQUENCE_ADAPTER.validate_python(value)
        except ValidationError:
            return str(value)
        return values[0] if values else "string"

    @staticmethod
    def _sqlalchemy_create_engine(
        url: str,
        connect_timeout: int | None = None,
    ) -> SAEngine:
        """Create SQLAlchemy engine with optional connection timeout."""
        connect_args: dict[str, int] = {}
        if connect_timeout is not None:
            connect_args["tcp_connect_timeout"] = connect_timeout
        return create_engine(
            url,
            pool_pre_ping=True,
            pool_recycle=3600,
            echo=False,
            connect_args=connect_args,
        )

    @staticmethod
    def _sqlalchemy_text(statement: str) -> TextClause:
        """Build SQL text value."""
        return text(statement)

    @staticmethod
    def _engine_connect(engine: SAEngine) -> SAConnection:
        """Open connection context manager from engine."""
        return engine.connect()

    @staticmethod
    def _engine_begin(
        engine: SAEngine,
    ) -> contextlib.AbstractContextManager[SAConnection]:
        """Open transaction context manager from engine."""
        return engine.begin()

    @staticmethod
    def _context_enter[T](context_manager: contextlib.AbstractContextManager[T]) -> T:
        """Enter dynamic context manager and return inner value."""
        return context_manager.__enter__()

    @staticmethod
    def _context_exit(
        context_manager: contextlib.AbstractContextManager[SAConnection],
    ) -> None:
        """Exit dynamic context manager safely."""
        context_manager.__exit__(None, None, None)

    @staticmethod
    def _engine_dispose(engine: SAEngine) -> None:
        """Dispose engine resources."""
        engine.dispose()

    def _get_current_timestamp(self) -> str:
        """Get current timestamp for operation tracking."""
        return str(int(time.time()))

    def _get_engine(self) -> r[SAEngine]:
        """Get database engine."""
        engine = self._engine
        if engine is None or not self.connected():
            return r[SAEngine].fail("Not connected to database")
        return r[SAEngine].ok(engine)

    @staticmethod
    def _connection_execute(
        connection: SAConnection,
        statement: TextClause,
        parameters: t.ConfigMap | None = None,
    ) -> CursorResult[tuple[t.ContainerValue, ...]]:
        """Execute statement on SQL connection."""
        normalized_params = FlextDbOracleServiceBase._normalize_params(parameters)
        return connection.execute(statement, normalized_params.root)

    def execute_query(
        self,
        sql: str,
        params: t.ConfigMap | None = None,
    ) -> r[Sequence[t.Dict]]:
        """Execute a SQL query in composed service facades."""
        del sql, params
        msg = "execute_query requires the composed DB Oracle service facade"
        raise NotImplementedError(msg)


__all__ = ["FlextDbOracleServiceBase"]
