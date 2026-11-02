"""Typed-row and executemany contracts of the query service mixin.

These tests exercise the OBSERVABLE public behavior of the golden-pattern
facilities added to ``FlextDbOracleServiceQuery``: the ``fetch_models``
typed-row port, native ``execute_many`` batching, and the structural
satisfaction of the ``QueryExecutor`` protocol. No database connection.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from pydantic import BaseModel

from flext_db_oracle.services import FlextDbOracleServices
from tests import p, tm


class TypedRow(BaseModel):
    """Row projection consumed by the typed-fetch contract."""

    user_id: str
    status: str


class TestsFetchModelsContract:
    """fetch_models behaves as a typed, disconnected-safe query port."""

    @staticmethod
    def test_fetch_models_fails_when_disconnected(
        oracle_unit_services: FlextDbOracleServices,
    ) -> None:
        """A typed fetch on an unconnected service returns a failure result."""
        result = oracle_unit_services.fetch_models(
            "SELECT username AS user_id, status FROM dba_users",
            model=TypedRow,
        )
        tm.ok(result.failure)
        tm.that((result.error or "").lower(), has="not connected")

    @staticmethod
    def test_facade_serves_the_query_executor_port(
        oracle_unit_services: FlextDbOracleServices,
    ) -> None:
        """Consumers typed on the query port get the facade's typed failure."""
        port: p.DbOracle.QueryExecutor = oracle_unit_services
        result = port.fetch_models("SELECT 1 AS user_id FROM dual", model=TypedRow)
        tm.ok(result.failure)
        tm.that((result.error or "").lower(), has="not connected")


class TestsExecuteManyContract:
    """execute_many batches parameters through one native executemany."""

    @staticmethod
    def test_empty_batch_reports_zero_rows_without_connection(
        oracle_unit_services: FlextDbOracleServices,
    ) -> None:
        """An empty parameter batch short-circuits to zero affected rows."""
        result = oracle_unit_services.execute_many(
            "INSERT INTO t VALUES (:a)",
            [],
        )
        tm.ok(result)
        tm.that(result.value, eq=0)

    @staticmethod
    def test_nonempty_batch_fails_when_disconnected(
        oracle_unit_services: FlextDbOracleServices,
    ) -> None:
        """A real batch requires an active connection and fails cleanly."""
        result = oracle_unit_services.execute_many(
            "INSERT INTO t VALUES (:a)",
            [{"a": 1}, {"a": 2}],
        )
        tm.ok(result.failure)
        tm.that((result.error or "").lower(), has="not connected")
