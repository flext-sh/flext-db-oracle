"""Query execution service mixin for flext-db-oracle.

Provides SQL query/statement execution, bulk operations,
and result normalization.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from collections.abc import (
    Sequence,
)
from typing import TYPE_CHECKING, override

from sqlalchemy import text

from flext_db_oracle import FlextDbOracleServiceBase, c, m, p, r, t

if TYPE_CHECKING:
    from sqlalchemy.engine import CursorResult


class FlextDbOracleServiceQuery(FlextDbOracleServiceBase):
    """Mixin providing query execution for FlextDbOracleServices.

    Handles: execute_query, execute_statement, execute_many,
    fetch_one, generate_query_hash, result normalization.
    """

    def execute_many(
        self,
        sql: str,
        params_list: t.SequenceOf[t.JsonMapping | m.ConfigMap],
    ) -> p.Result[int]:
        """Execute SQL statement multiple times."""
        if not self.connected():
            return r[int].fail("Not connected to database")
        engine_result = self._get_engine()
        if engine_result.failure:
            return r[int].fail(engine_result.error or "Failed to get database engine")
        try:
            with self._engine_begin(engine_result.value) as conn:
                total_affected = 0
                for params in params_list:
                    typed_params = (
                        params
                        if isinstance(params, m.ConfigMap)
                        else m.ConfigMap.model_validate(params)
                    )
                    result = self._connection_execute(
                        conn,
                        text(sql),
                        typed_params,
                    )
                    total_affected += max(result.rowcount, 0)
                return r[int].ok(total_affected)
        except c.DbOracle.EXC_DB_BROAD as e:
            return r[int].fail_op("Bulk execution", e)

    @override
    def execute_query(
        self,
        sql: str,
        params: m.ConfigMap | None = None,
    ) -> p.Result[Sequence[m.Dict]]:
        """Execute SQL query and return results."""
        if not self.connected():
            return r[Sequence[m.Dict]].fail("Not connected to database")
        engine_result = self._get_engine()
        if engine_result.failure:
            return r[Sequence[m.Dict]].fail(
                engine_result.error or "Failed to get database engine",
            )
        try:
            with self._engine_connect(engine_result.value) as conn:
                result = self._connection_execute(
                    conn,
                    text(sql),
                    params,
                )
                rows: t.SequenceOf[m.Dict] = self._normalize_query_rows(result)
                return r[Sequence[m.Dict]].ok(rows)
        except c.DbOracle.EXC_DB_BROAD as e:
            return r[Sequence[m.Dict]].fail_op("Query execution", e)

    def execute_statement(
        self,
        sql: str,
        params: m.ConfigMap | None = None,
    ) -> p.Result[int]:
        """Execute SQL statement and return affected rows."""
        if not self.connected():
            return r[int].fail("Not connected to database")
        engine_result = self._get_engine()
        if engine_result.failure:
            return r[int].fail(engine_result.error or "Failed to get database engine")
        try:
            with self._engine_begin(engine_result.value) as conn:
                result = self._connection_execute(
                    conn,
                    text(sql),
                    params,
                )
                rowcount = max(result.rowcount, 0)
                return r[int].ok(rowcount)
        except c.DbOracle.EXC_DB_BROAD as e:
            return r[int].fail_op("Statement execution", e)

    def fetch_one(
        self,
        sql: str,
        params: m.ConfigMap | None = None,
    ) -> p.Result[m.Dict | None]:
        """Execute query and return first result."""
        return self.execute_query(sql, params).map(
            lambda rows: rows[0] if rows else None,
        )

    def _normalize_query_rows(
        self,
        query_result: CursorResult[tuple[t.JsonValue, ...]],
    ) -> t.SequenceOf[m.Dict]:
        """Normalize SQLAlchemy query result rows into typed mapping models."""
        mapping_result = query_result.mappings()
        rows = mapping_result.all()
        result: t.SequenceOf[m.Dict] = [
            m.Dict(root={str(key): str(val) for key, val in dict(row).items()})
            for row in rows
        ]
        return result

    def _normalize_row(self, row: t.JsonMapping) -> m.Dict:
        """Normalize a single SQLAlchemy mapping row into a typed map."""
        payload: dict[str, t.JsonPayload] = dict(row)
        return m.Dict(root=payload)


__all__: list[str] = ["FlextDbOracleServiceQuery"]
