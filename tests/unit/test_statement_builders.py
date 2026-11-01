"""Statement builders and column types published through the db-oracle facades.

Consumers build SQL functions with ``u.DbOracle.func`` and declare ORM column
types with ``t.DbOracle.SqlDateTime``/``SqlText`` instead of importing
SQLAlchemy. These tests assert the rendered SQL and the column-type contract
those members promise. No database connection.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from tests import t, tm, u


class TestsFlextDbOracleStatementBuilders:
    """The published builders render the SQL their native owner renders."""

    @staticmethod
    def test_func_count_renders_count_star() -> None:
        """``u.DbOracle.func.count()`` is the SQL aggregate ``count(*)``."""
        tm.that(str(u.DbOracle.func.count()), eq="count(*)")

    @staticmethod
    def test_func_builds_named_sql_functions() -> None:
        """Any attribute of ``u.DbOracle.func`` names a SQL function call."""
        tm.that(str(u.DbOracle.func.max(u.DbOracle.text("dh_exec"))), has="max(")

    @staticmethod
    def test_sql_datetime_reads_oracle_date_as_naive() -> None:
        """``SqlDateTime()`` keeps Oracle DATE as a timezone-naive timestamp."""
        tm.ok(not t.DbOracle.SqlDateTime().timezone)

    @staticmethod
    def test_sql_text_is_an_unbounded_text_column() -> None:
        """``SqlText()`` declares a text column without a length bound."""
        tm.ok(t.DbOracle.SqlText().length is None)


__all__: list[str] = ["TestsFlextDbOracleStatementBuilders"]
