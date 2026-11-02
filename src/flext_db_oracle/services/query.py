"""Query execution service mixin for flext-db-oracle.

Provides SQL query/statement execution and bulk operations.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from collections.abc import Sequence

from sqlalchemy import text

from flext_db_oracle import FlextDbOracleServiceBase, c, m, p, r, t


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
        params_list: Sequence[t.JsonMapping | m.ConfigMap],
    ) -> p.Result[int]:
        """Execute SQL statement multiple times.

        Returns:
            The resulting ``p.Result[int]``.

        """
        engine_result = self._get_engine()
        if engine_result.failure:
            return r[int].from_failure(engine_result)
        try:
            with self._engine_begin(engine_result.value) as conn:
                total_affected = 0
                for params in params_list:
                    typed_params = (
                        params
                        if isinstance(params, m.ConfigMap)
                        else m.ConfigMap.model_validate(params)
                    )
                    result = self._connection_execute(conn, text(sql), typed_params)
                    total_affected += max(result.rowcount, 0)
                return r[int].ok(total_affected)
        except c.DbOracle.EXC_DB_BROAD as exc:
            return r[int].fail_op("Bulk execution", exc)

    def execute_query(
        self,
        sql: str,
        params: m.ConfigMap | None = None,
    ) -> p.Result[Sequence[m.Dict]]:
        """Execute SQL query and return its rows with driver-native values.

        Returns:
            The resulting ``p.Result[Sequence[m.Dict]]``.

        """
        return self.execute_rows(sql, params)

    def execute_statement(
        self,
        sql: str,
        params: m.ConfigMap | None = None,
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

    def fetch_one(
        self,
        sql: str,
        params: m.ConfigMap | None = None,
    ) -> p.Result[m.Dict | None]:
        """Execute query and return first result.

        Returns:
            The resulting ``p.Result[m.Dict | None]``.

        """
        return self.execute_query(sql, params).map(
            lambda rows: rows[0] if rows else None,
        )


__all__: list[str] = ["FlextDbOracleServiceQuery"]
