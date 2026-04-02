"""Query execution service mixin for flext-db-oracle.

Provides SQL query/statement execution, bulk operations,
and result normalization.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import hashlib
from collections.abc import Mapping, Sequence
from typing import override

import oracledb
from flext_core import r
from sqlalchemy.engine import CursorResult
from sqlalchemy.exc import (
    DatabaseError as SQLAlchemyDatabaseError,
    OperationalError as SQLAlchemyOperationalError,
    SQLAlchemyError,
)

from flext_db_oracle import FlextDbOracleServiceBase, t


class FlextDbOracleServiceQuery(FlextDbOracleServiceBase):
    """Mixin providing query execution for FlextDbOracleServices.

    Handles: execute_query, execute_statement, execute_many,
    fetch_one, generate_query_hash, result normalization.
    """

    def execute_many(
        self,
        sql: str,
        params_list: Sequence[Mapping[str, t.ContainerValue] | t.ConfigMap],
    ) -> r[int]:
        """Execute SQL statement multiple times."""
        if not self.is_connected():
            return r[int].fail("Not connected to database")
        engine_result = self._get_engine()
        if engine_result.is_failure:
            return r[int].fail(engine_result.error or "Failed to get database engine")
        try:
            connect_ctx = self._engine_connect(engine_result.value)
            conn = self._context_enter(connect_ctx)
            try:
                total_affected = 0
                for params in params_list:
                    typed_params = (
                        params
                        if isinstance(params, t.ConfigMap)
                        else t.ConfigMap.model_validate({"root": dict(params)})
                    )
                    result = self._connection_execute(
                        conn,
                        self._sqlalchemy_text(sql),
                        typed_params,
                    )
                    total_affected += max(result.rowcount, 0)
                return r[int].ok(total_affected)
            finally:
                self._context_exit(connect_ctx)
        except (
            oracledb.DatabaseError,
            oracledb.InterfaceError,
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
        params: t.ConfigMap | None = None,
    ) -> r[Sequence[t.Dict]]:
        """Execute SQL query and return results."""
        if not self.is_connected():
            return r[Sequence[t.Dict]].fail("Not connected to database")
        engine_result = self._get_engine()
        if engine_result.is_failure:
            return r[Sequence[t.Dict]].fail(
                engine_result.error or "Failed to get database engine",
            )
        try:
            connect_ctx = self._engine_connect(engine_result.value)
            conn = self._context_enter(connect_ctx)
            try:
                result = self._connection_execute(
                    conn,
                    self._sqlalchemy_text(sql),
                    params,
                )
                rows: Sequence[t.Dict] = self._normalize_query_rows(result)
                return r[Sequence[t.Dict]].ok(rows)
            finally:
                self._context_exit(connect_ctx)
        except (
            oracledb.DatabaseError,
            oracledb.InterfaceError,
            ConnectionError,
            SQLAlchemyDatabaseError,
            SQLAlchemyOperationalError,
            SQLAlchemyError,
            OSError,
        ) as e:
            return r[Sequence[t.Dict]].fail(f"Query execution failed: {e}")

    def execute_statement(self, sql: str, params: t.ConfigMap | None = None) -> r[int]:
        """Execute SQL statement and return affected rows."""
        if not self.is_connected():
            return r[int].fail("Not connected to database")
        engine_result = self._get_engine()
        if engine_result.is_failure:
            return r[int].fail(engine_result.error or "Failed to get database engine")
        try:
            transaction_ctx = self._engine_begin(engine_result.value)
            conn = self._context_enter(transaction_ctx)
            try:
                result = self._connection_execute(
                    conn,
                    self._sqlalchemy_text(sql),
                    params,
                )
                rowcount = max(result.rowcount, 0)
                return r[int].ok(rowcount)
            finally:
                self._context_exit(transaction_ctx)
        except (
            oracledb.DatabaseError,
            oracledb.InterfaceError,
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
        params: t.ConfigMap | None = None,
    ) -> r[t.Dict | None]:
        """Execute query and return first result."""
        return self.execute_query(sql, params).map(
            lambda rows: rows[0] if rows else None,
        )

    def generate_query_hash(
        self,
        sql: str = "",
        params: t.ConfigMap | t.ContainerValueMapping | None = None,
    ) -> r[str]:
        """Generate query hash - simplified."""
        typed_params = (
            params
            if isinstance(params, t.ConfigMap) or params is None
            else t.ConfigMap.model_validate({"root": dict(params)})
        )
        hash_input = f"{sql}_{typed_params!s}"
        return r[str].ok(hashlib.sha256(hash_input.encode()).hexdigest()[:16])

    def _normalize_query_rows(
        self,
        query_result: CursorResult[tuple[t.ContainerValue, ...]],
    ) -> Sequence[t.Dict]:
        """Normalize SQLAlchemy query result rows into typed mapping models."""
        mapping_result = query_result.mappings()
        rows = mapping_result.all()
        result: Sequence[t.Dict] = [
            t.Dict.model_validate({
                "root": {str(key): str(val) for key, val in dict(row).items()},
            })
            for row in rows
        ]
        return result

    def _normalize_row(self, row: Mapping[str, t.ContainerValue]) -> t.Dict:
        """Normalize a single SQLAlchemy mapping row into a typed map."""
        return t.Dict.model_validate(
            {"root": {str(key): value for key, value in row.items()}},
        )


__all__ = ["FlextDbOracleServiceQuery"]
