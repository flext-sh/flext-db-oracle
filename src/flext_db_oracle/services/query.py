"""Query execution service mixin for flext-db-oracle.

Provides SQL query/statement execution and bulk operations.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from collections.abc import Sequence

from sqlalchemy import Executable, text

from flext_db_oracle import FlextDbOracleServiceBase, c, m, p, r, t, u


class FlextDbOracleServiceQuery(FlextDbOracleServiceBase):
    """Mixin providing query execution for FlextDbOracleServices.

    Handles: execute_query, execute_statement, execute_many, fetch_one.
    """

    # flext-1wjg1.16: see services/plugin.py -- explicit wrapper keeps this
    # mixin's __init__ positional instead of pydantic's synthesized kwargs-only one.
    def __init__(self, settings: t.DbOracle.Settings) -> None:
        """Initialize shared Oracle service state for this mixin."""
        FlextDbOracleServiceBase.__init__(self, settings)

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
        engine_result = self._get_engine()
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

    def execute_query(
        self,
        sql: str,
        params: p.ConfigMap | None = None,
    ) -> p.Result[Sequence[m.Dict]]:
        """Execute SQL query and return its rows with driver-native values.

        Returns:
            The resulting ``p.Result[Sequence[p.Dict]]``.

        """
        normalized = m.ConfigMap.model_validate(params) if params is not None else None
        return self.execute_rows(sql, normalized)

    def execute_statement(
        self,
        sql: str,
        params: p.ConfigMap | None = None,
    ) -> p.Result[int]:
        """Execute SQL statement and return affected rows.

        Returns:
            The resulting ``p.Result[int]``.

        """
        engine_result = self._get_engine()
        if engine_result.failure:
            return r[int].from_failure(engine_result)
        try:
            with self._engine_begin(engine_result.value) as conn:
                result = self._connection_execute(conn, text(sql), params)
                rowcount = max(result.rowcount, 0)
                return r[int].ok(rowcount)
        except c.DbOracle.EXC_DB_BROAD as exc:
            return r[int].fail_op("Statement execution", exc)

    def fetch_models[M: m.BaseModel](
        self,
        sql: Executable | str,
        params: p.ConfigMap | None = None,
        *,
        model: type[M],
    ) -> p.Result[Sequence[M]]:
        """Fetch rows on the service connection and validate them into the model.

        Returns:
            The validated rows, or the first engine/execution failure.

        """
        engine_result = self._get_engine()
        if engine_result.failure:
            return r[Sequence[M]].from_failure(engine_result)
        try:
            with self._engine_begin(engine_result.value) as conn:
                rows = u.DbOracle.fetch_models_on_connection(
                    sql,
                    params.root if params is not None else None,
                    model=model,
                    connection=conn,
                )
                return r[Sequence[M]].ok(tuple(rows))
        except c.DbOracle.EXC_DB_BROAD as exc:
            return r[Sequence[M]].fail_op("Typed fetch", exc)

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


__all__: list[str] = ["FlextDbOracleServiceQuery"]
