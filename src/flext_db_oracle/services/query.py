"""Query execution service mixin for flext-db-oracle.

Provides SQL query/statement execution, bulk operations,
and result normalization.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import hashlib
from collections.abc import (
    Sequence,
)
from typing import override

from sqlalchemy.engine import CursorResult
from sqlalchemy.exc import (
    DatabaseError as SQLAlchemyDatabaseError,
    OperationalError as SQLAlchemyOperationalError,
    SQLAlchemyError,
)

from flext_db_oracle import FlextDbOracleServiceBase, m, p, r, t


class FlextDbOracleServiceQuery(FlextDbOracleServiceBase):
    """Mixin providing query execution for FlextDbOracleServices.

    Handles: execute_query, execute_statement, execute_many,
    fetch_one, generate_query_hash, result normalization.
    """

    def execute_many(
        self,
        sql: str,
        params_list: Sequence[t.ContainerValueMapping | m.ConfigMap],
    ) -> p.Result[int]:
        """Execute SQL statement multiple times."""
        if not self.connected():
            return r[int].fail("Not connected to database")
        engine_result = self._get_engine()
        if engine_result.failure:
            return r[int].fail(engine_result.error or "Failed to get database engine")
        try:
            with self._engine_connect(engine_result.value) as conn:
                total_affected = 0
                for params in params_list:
                    typed_params = (
                        params
                        if isinstance(params, m.ConfigMap)
                        else m.ConfigMap(root=dict(params))
                    )
                    result = self._connection_execute(
                        conn,
                        self._sqlalchemy_text(sql),
                        typed_params,
                    )
                    total_affected += max(result.rowcount, 0)
                return r[int].ok(total_affected)
        except (
            t.DbOracle.OracleDatabaseError,
            t.DbOracle.OracleInterfaceError,
            ConnectionError,
            SQLAlchemyDatabaseError,
            SQLAlchemyOperationalError,
            SQLAlchemyError,
            OSError,
        ) as e:
            return r[int].fail(f"Bulk execution failed: {e}")

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
                    self._sqlalchemy_text(sql),
                    params,
                )
                rows: Sequence[m.Dict] = self._normalize_query_rows(result)
                return r[Sequence[m.Dict]].ok(rows)
        except (
            t.DbOracle.OracleDatabaseError,
            t.DbOracle.OracleInterfaceError,
            ConnectionError,
            SQLAlchemyDatabaseError,
            SQLAlchemyOperationalError,
            SQLAlchemyError,
            OSError,
        ) as e:
            return r[Sequence[m.Dict]].fail(f"Query execution failed: {e}")

    def execute_statement(
        self, sql: str, params: m.ConfigMap | None = None
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
                    self._sqlalchemy_text(sql),
                    params,
                )
                rowcount = max(result.rowcount, 0)
                return r[int].ok(rowcount)
        except (
            t.DbOracle.OracleDatabaseError,
            t.DbOracle.OracleInterfaceError,
            ConnectionError,
            SQLAlchemyDatabaseError,
            SQLAlchemyOperationalError,
            SQLAlchemyError,
            OSError,
        ) as e:
            return r[int].fail(f"Statement execution failed: {e}")

    def fetch_one(
        self,
        sql: str,
        params: m.ConfigMap | None = None,
    ) -> p.Result[m.Dict | None]:
        """Execute query and return first result."""
        return self.execute_query(sql, params).map(
            lambda rows: rows[0] if rows else None,
        )

    def generate_query_hash(
        self,
        sql: str = "",
        params: m.ConfigMap | t.ContainerValueMapping | None = None,
    ) -> p.Result[str]:
        """Generate query hash - simplified."""
        typed_params = (
            params
            if isinstance(params, m.ConfigMap) or params is None
            else m.ConfigMap(root=dict(params))
        )
        hash_input = f"{sql}_{typed_params!s}"
        return r[str].ok(hashlib.sha256(hash_input.encode()).hexdigest()[:16])

    def _normalize_query_rows(
        self,
        query_result: CursorResult[tuple[t.ContainerValue, ...]],
    ) -> Sequence[m.Dict]:
        """Normalize SQLAlchemy query result rows into typed mapping models."""
        mapping_result = query_result.mappings()
        rows = mapping_result.all()
        result: Sequence[m.Dict] = [
            m.Dict(root={str(key): str(val) for key, val in dict(row).items()})
            for row in rows
        ]
        return result

    def _normalize_row(self, row: t.ContainerValueMapping) -> m.Dict:
        """Normalize a single SQLAlchemy mapping row into a typed map."""
        return m.Dict(root={str(key): value for key, value in row.items()})


__all__: list[str] = ["FlextDbOracleServiceQuery"]
