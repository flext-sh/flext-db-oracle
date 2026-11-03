"""Query execution service mixin for flext-db-oracle.

Provides SQL query/statement execution, bulk operations,
and result normalization.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from collections.abc import Sequence
from typing import TYPE_CHECKING

from pydantic import BaseModel, ValidationError
from sqlalchemy import Engine as SAEngine, Executable, text

from flext_db_oracle import FlextDbOracleServiceBase, c, m, p, r, t

if TYPE_CHECKING:
    from sqlalchemy.engine import CursorResult


class FlextDbOracleServiceQuery(FlextDbOracleServiceBase):
    """Mixin providing query execution for FlextDbOracleServices.

    Handles: execute_query, execute_statement, execute_many,
    fetch_one, fetch_models, result normalization.
    """

    # flext-1wjg1.16: see services/plugin.py -- explicit wrapper keeps this
    # mixin's __init__ positional instead of pydantic's synthesized kwargs-only one.
    def __init__(self, settings: t.DbOracle.Settings) -> None:
        """Initialize shared Oracle service state for this mixin."""
        FlextDbOracleServiceBase.__init__(self, settings)

    def _connected_engine(self) -> p.Result[SAEngine]:
        """Return the active engine as a result, failing when disconnected.

        Returns:
            The resulting ``p.Result[SAEngine]``.

        """
        if not self.connected():
            return r[SAEngine].fail("Not connected to database")
        return self._get_engine()

    def execute_many(
        self,
        sql: str,
        params_list: Sequence[t.JsonMapping | p.ConfigMap],
    ) -> p.Result[int]:
        """Execute SQL statement multiple times (native driver executemany).

        One round trip with the whole parameter batch instead of a Python
        loop over single executions; the transaction commits on context exit.

        Returns:
            The resulting ``p.Result[int]``.

        """
        if not params_list:
            return r[int].ok(value=0)
        engine_result = self._connected_engine()
        if engine_result.failure:
            return r[int].from_failure(engine_result)
        batch = [
            params.root
            if isinstance(params, m.ConfigMap)
            else m.ConfigMap.model_validate(params).root
            for params in params_list
        ]
        try:
            with self._engine_begin(engine_result.value) as conn:
                result = conn.execute(text(sql), batch)
                return r[int].ok(max(result.rowcount, 0))
        except c.DbOracle.EXC_DB_BROAD as exc:
            return r[int].fail_op("Bulk execution", exc)

    # flext-1wjg1.16: not a real override -- QueryExecutor is a structural
    # Protocol (protocols.py), never a base class of this mixin, so pyrefly's
    # nominal @override check has no matching parent attribute to verify.
    def execute_query(
        self,
        sql: str,
        params: p.ConfigMap | None = None,
    ) -> p.Result[Sequence[p.Dict]]:
        """Execute SQL query and return results.

        Returns:
            The resulting ``p.Result[Sequence[p.Dict]]``.

        """
        engine_result = self._connected_engine()
        if engine_result.failure:
            return r[Sequence[p.Dict]].from_failure(engine_result)
        try:
            with self._engine_connect(engine_result.value) as conn:
                result = self._connection_execute(conn, text(sql), params)
                rows: Sequence[p.Dict] = self._normalize_query_rows(result)
                return r[Sequence[p.Dict]].ok(rows)
        except c.DbOracle.EXC_DB_BROAD as exc:
            return r[Sequence[p.Dict]].fail_op("Query execution", exc)

    def execute_statement(
        self,
        sql: str,
        params: p.ConfigMap | None = None,
    ) -> p.Result[int]:
        """Execute SQL statement and return affected rows.

        Returns:
            The resulting ``p.Result[int]``.

        """
        engine_result = self._connected_engine()
        if engine_result.failure:
            return r[int].from_failure(engine_result)
        try:
            with self._engine_begin(engine_result.value) as conn:
                result = self._connection_execute(conn, text(sql), params)
                rowcount = max(result.rowcount, 0)
                return r[int].ok(rowcount)
        except c.DbOracle.EXC_DB_BROAD as exc:
            return r[int].fail_op("Statement execution", exc)

    def fetch_one(
        self,
        sql: str,
        params: p.ConfigMap | None = None,
    ) -> p.Result[p.Dict | None]:
        """Execute query and return first result.

        Returns:
            The resulting ``p.Result[p.Dict | None]``.

        """
        return self.execute_query(sql, params).map(
            lambda rows: rows[0] if rows else None,
        )

    def fetch_models[T: BaseModel](
        self,
        sql: str | Executable,
        params: p.ConfigMap | None = None,
        *,
        model: type[T],
    ) -> p.Result[Sequence[T]]:
        """Execute a query and validate each native row into ``model``.

        Rows keep the driver's native values (dates, decimals — no string
        coercion): the mapping of each cursor row validates directly into the
        pydantic/SQLModel ``model``. Accepts raw SQL or a SQLAlchemy
        ``Selectable`` (the typed-statement path of the golden pattern).

        Returns:
            The resulting ``p.Result[Sequence[T]]``.

        """
        engine_result = self._connected_engine()
        if engine_result.failure:
            return r[Sequence[T]].from_failure(engine_result)
        statement = text(sql) if isinstance(sql, str) else sql
        try:
            with self._engine_connect(engine_result.value) as conn:
                result = conn.execute(statement, params.root if params else {})
                rows: Sequence[T] = [
                    model.model_validate(dict(row)) for row in result.mappings().all()
                ]
                return r[Sequence[T]].ok(rows)
        except c.DbOracle.EXC_DB_BROAD as exc:
            return r[Sequence[T]].fail_op("Typed query execution", exc)
        except ValidationError as exc:
            return r[Sequence[T]].fail_op("Row validation", exc)

    @staticmethod
    def _normalize_query_rows(
        query_result: CursorResult[tuple[t.JsonValue, ...]],
    ) -> Sequence[p.Dict]:
        """Normalize SQLAlchemy query result rows into typed mapping models.

        Returns:
            The resulting ``Sequence[p.Dict]``.

        """
        mapping_result = query_result.mappings()
        rows = mapping_result.all()
        result: Sequence[p.Dict] = [
            m.Dict(root={str(key): str(val) for key, val in dict(row).items()})
            for row in rows
        ]
        return result


__all__: list[str] = ["FlextDbOracleServiceQuery"]
