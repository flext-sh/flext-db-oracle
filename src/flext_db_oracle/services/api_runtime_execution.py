"""SQL execution behavior of the public DB Oracle API facade runtime.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from collections.abc import MutableSequence, Sequence
from typing import override

from flext_db_oracle import m, p, r, t, u
from flext_db_oracle.services.api_runtime_state import FlextDbOracleApiRuntimeState


class FlextDbOracleApiRuntimeExecution(FlextDbOracleApiRuntimeState):
    """SQL execution and query behavior of the facade."""

    @override
    def execute(self) -> p.Result[p.Base]:
        """Execute default domain service operation - return settings.

        Returns:
            The resulting ``p.Result[p.Base]``.
        """
        return r[p.Base].ok(self._oracle_config)

    def execute_many(
        self,
        sql: str,
        params_list: t.SequenceOf[t.JsonMapping],
    ) -> p.Result[int]:
        """Execute a statement multiple times with different parameters.

        Returns:
            The resulting ``p.Result[int]``.
        """
        self.logger.debug("Executing bulk statement", batch_size=len(params_list))
        return self._normalize_parameters_list(params_list).flat_map(
            lambda normalized_parameters: self._services.execute_many(
                sql,
                normalized_parameters,
            ),
        )

    def execute_sql(
        self,
        sql: str,
        parameters: t.JsonMapping | None = None,
    ) -> p.Result[int]:
        """Execute an INSERT/UPDATE/DELETE statement and return rows affected.

        Returns:
            The resulting ``p.Result[int]``.
        """
        return self.execute_statement(sql, parameters)

    def execute_statement(
        self,
        sql: str | t.JsonValue,
        params: t.JsonMapping | None = None,
    ) -> p.Result[int]:
        """Execute SQL statement directly and return affected rows.

        Returns:
            The resulting ``p.Result[int]``.
        """
        sql_text = str(sql)
        self.logger.debug("Executing SQL statement", statement_length=len(sql_text))
        return self._normalize_parameters(params).flat_map(
            lambda normalized_parameters: self._services.execute_statement(
                sql_text,
                normalized_parameters,
            ),
        )

    @staticmethod
    def optimize_query(sql: str) -> p.Result[str]:
        """Optimize a SQL query for Oracle.

        Returns:
            The resulting ``p.Result[str]``.
        """
        return u.try_(
            lambda: " ".join(sql.split()),
            catch=(AttributeError, ValueError, TypeError),
        ).map_error(lambda e: f"Query optimization failed: {e}")

    def query(
        self,
        sql: str,
        parameters: t.JsonMapping | None = None,
    ) -> p.Result[Sequence[m.Dict]]:
        """Execute a SELECT query and return all results.

        Returns:
            The resulting ``p.Result[Sequence[m.Dict]]``.
        """
        self.logger.debug("Executing query", query_length=len(sql))
        return self._normalize_parameters(parameters).flat_map(
            lambda normalized_parameters: self._services.execute_query(
                sql,
                normalized_parameters,
            ),
        )

    def query_one(
        self,
        sql: str,
        parameters: t.JsonMapping | None = None,
    ) -> p.Result[m.Dict | None]:
        """Execute a SELECT query and return first result or None.

        Returns:
            The resulting ``p.Result[m.Dict | None]``.
        """
        return self._normalize_parameters(parameters).flat_map(
            lambda normalized_parameters: self._services.fetch_one(
                sql,
                normalized_parameters,
            ),
        )

    @staticmethod
    def _normalize_parameters(
        parameters: t.JsonMapping | None = None,
    ) -> p.Result[m.ConfigMap]:
        """Normalize query parameters into the canonical ConfigMap contract.

        Returns:
            The resulting ``p.Result[m.ConfigMap]``.
        """
        if parameters is None:
            return r[m.ConfigMap].ok(m.ConfigMap(root={}))
        return (
            u
            .try_(lambda: dict(parameters))
            .map(m.ConfigMap.model_validate)
            .lash(
                lambda error: r[m.ConfigMap].fail(f"Invalid query parameters: {error}"),
            )
        )

    @classmethod
    def _normalize_parameters_list(
        cls,
        parameters_list: t.SequenceOf[t.JsonMapping],
    ) -> p.Result[Sequence[m.ConfigMap]]:
        """Normalize bulk query parameters into canonical ConfigMap values.

        Returns:
            The resulting ``p.Result[Sequence[m.ConfigMap]]``.
        """
        normalized: MutableSequence[m.ConfigMap] = []
        for parameters in parameters_list:
            result = cls._normalize_parameters(parameters)
            if result.failure:
                return r[Sequence[m.ConfigMap]].from_failure(result)
            normalized.append(result.value)
        return r[Sequence[m.ConfigMap]].ok(normalized)

    @staticmethod
    def _convert_to_query_result(
        sql: str,
        data: t.SequenceOf[m.Dict],
    ) -> m.DbOracle.QueryResult:
        """Convert raw query data to QueryResult model.

        Returns:
            The resulting ``m.DbOracle.QueryResult``.
        """
        if not data:
            return m.DbOracle.QueryResult(
                query=sql,
                columns=[],
                rows=[],
                row_count=0,
                domain_events=[],
                result_data=[],
                query_hash="",
                explain_plan="",
            )
        first_row = data[0].root
        columns = list(first_row.keys())
        rows = [
            m.DbOracle.RowData(values=[str(value) for value in row.root.values()])
            for row in data
        ]
        return m.DbOracle.QueryResult(
            query=sql,
            columns=columns,
            rows=rows,
            row_count=len(data),
            domain_events=[],
            result_data=[],
            query_hash="",
            explain_plan="",
        )

    def _execute_query_sql(self, sql: str) -> p.Result[m.DbOracle.QueryResult]:
        """Execute SQL query and return results as QueryResult.

        Returns:
            The resulting ``p.Result[m.DbOracle.QueryResult]``.
        """
        return self._services.execute_query(sql).map(
            lambda data: self._convert_to_query_result(sql, data),
        )


__all__: list[str] = ["FlextDbOracleApiRuntimeExecution"]
