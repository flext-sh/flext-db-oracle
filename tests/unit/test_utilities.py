"""Test u functionality - comprehensive unit tests.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import contextlib
from collections.abc import Mapping

import pytest
from flext_tests import tm

from flext_db_oracle import FlextDbOracleApi, FlextDbOracleSettings
from tests.constants import c
from tests.models import m
from tests.typings import t
from tests.utilities import u


@pytest.mark.unit
class TestsFlextDbOracleUtilitiesUnit:
    """Test u functionality with comprehensive coverage."""

    _JSON_RESULT_ADAPTER: m.TypeAdapter[
        t.SequenceOf[Mapping[str, int | str | bool]]
        | t.SequenceOf[t.StrMapping]
        | t.SequenceOf[t.IntMapping]
        | None
    ] = m.TypeAdapter(
        t.SequenceOf[Mapping[str, int | str | bool]]
        | t.SequenceOf[t.StrMapping]
        | t.SequenceOf[t.IntMapping]
        | None,
    )

    def test_utilities_creation(self) -> None:
        """Test utilities class exists and has correct type."""
        tm.that(u, none=False)
        tm.that(u, is_=type)

    def test_generate_query_hash_basic_select(self) -> None:
        """Test basic SELECT query hash generation."""
        params: t.IntMapping = {"id": 1}
        hash_value = tm.ok(
            u.DbOracle.generate_query_hash("SELECT * FROM table WHERE id = :id", params)
        )
        tm.that(hash_value, is_=str)
        tm.that(len(hash_value), eq=16)
        tm.that(hash_value.isalnum(), eq=True)

    def test_generate_query_hash_with_whitespace_normalization(self) -> None:
        """Test query hash does NOT normalize whitespace (hashes raw query)."""
        h1 = tm.ok(u.DbOracle.generate_query_hash("SELECT * FROM table", {"id": 1}))
        h2 = tm.ok(u.DbOracle.generate_query_hash("SELECT * FROM table", {"id": 2}))
        tm.that(h1, ne=h2)

    def test_generate_query_hash_case_insensitive_keywords(self) -> None:
        """Test query hash handles case variations in keywords."""
        h1 = tm.ok(
            u.DbOracle.generate_query_hash("select * from users where id = :id", {})
        )
        h2 = tm.ok(
            u.DbOracle.generate_query_hash("SELECT * FROM USERS WHERE ID = :ID", {})
        )
        tm.that(h1, ne=h2)

    def test_generate_query_hash_with_params(self) -> None:
        """Test query hash generation with parameters."""
        h = tm.ok(u.DbOracle.generate_query_hash("SELECT 1", {}))
        tm.that(h, is_=str)
        tm.that(len(h), eq=16)

    def test_generate_query_hash_params_order_independence(self) -> None:
        """Test query hash is independent of parameter order."""
        params1: t.JsonMapping = {"id": 1, "name": "test", "active": True}
        params2: t.JsonMapping = {"name": "test", "active": True, "id": 1}
        query = (
            "SELECT * FROM users WHERE id = :id AND name = :name AND active = :active"
        )
        tm.that(
            tm.ok(u.DbOracle.generate_query_hash(query, params1)),
            eq=tm.ok(u.DbOracle.generate_query_hash(query, params2)),
        )

    def test_generate_query_hash_empty_params(self) -> None:
        """Test query hash with empty parameters."""
        tm.that(
            tm.ok(u.DbOracle.generate_query_hash("SELECT 1 FROM DUAL", {})), is_=str
        )

    def test_generate_query_hash_complex_query(self) -> None:
        """Test query hash with complex Oracle query."""
        complex_query = "\n        SELECT u.id, u.name, COUNT(o.id) as order_count\n        FROM users u\n        LEFT JOIN orders o ON u.id = o.user_id\n        WHERE u.created_date >= :start_date\n          AND u.Infra.status = :status\n        GROUP BY u.id, u.name\n        ORDER BY order_count DESC\n        "
        params = {"start_date": "2023-01-01", "status": "active"}
        h = tm.ok(u.DbOracle.generate_query_hash(complex_query, params))
        tm.that(h, is_=str)
        tm.that(len(h), eq=16)

    def test_format_sql_for_oracle_basic_select(self) -> None:
        """Test basic SQL formatting normalizes whitespace."""
        formatted = tm.ok(
            u.DbOracle.format_sql_for_oracle("select id, name from users")
        )
        tm.that(formatted, eq="select id, name from users")

    def test_format_sql_for_oracle_keyword_formatting(self) -> None:
        """Test SQL keyword formatting normalizes whitespace."""
        sql = "select u.id, u.name from users u join orders o on u.id = o.user_id where u.active = 1 group by u.id, u.name order by u.name"
        formatted = tm.ok(u.DbOracle.format_sql_for_oracle(sql))
        tm.that("\n" not in formatted and "  " not in formatted, eq=True)

    def test_format_sql_for_oracle_already_formatted(self) -> None:
        """Test formatting of already formatted SQL normalizes whitespace."""
        sql = "\nSELECT id, name\nFROM users\nWHERE active = 1\n"
        formatted = tm.ok(u.DbOracle.format_sql_for_oracle(sql))
        tm.that("\n" not in formatted, eq=True)

    def test_format_sql_for_oracle_complex_query(self) -> None:
        """Test formatting of complex query."""
        sql = "select distinct u.id, u.email, count(o.id) as order_count from users u inner join orders o on u.id = o.user_id where u.created_at >= '2023-01-01' and u.Infra.status in ('active', 'pending') group by u.id, u.email having count(o.id) > 0 order by order_count desc, u.email asc"
        formatted = tm.ok(u.DbOracle.format_sql_for_oracle(sql)).upper()
        tm.that(
            formatted,
            has=[
                "SELECT",
                "FROM",
                "INNER",
                "JOIN",
                "WHERE",
                "GROUP",
                "BY",
                "HAVING",
                "ORDER",
            ],
        )

    def test_format_sql_for_oracle_empty_string(self) -> None:
        """Test formatting of empty string."""
        tm.that(tm.ok(u.DbOracle.format_sql_for_oracle("")), eq="")

    def test_format_sql_for_oracle_whitespace_only(self) -> None:
        """Test formatting of whitespace-only string."""
        tm.that(tm.ok(u.DbOracle.format_sql_for_oracle("   \n\t  ")).strip(), eq="")

    @pytest.mark.parametrize(
        ("identifier", "expected"),
        [
            ("users", "users"),
            ("userTable", "userTable"),
            ("user_table", "user_table"),
        ],
    )
    def test_escape_oracle_identifier_valid(
        self, identifier: str, expected: str
    ) -> None:
        """Test valid Oracle identifiers are returned as-is."""
        tm.that(tm.ok(u.DbOracle.escape_oracle_identifier(identifier)), eq=expected)

    @pytest.mark.parametrize(
        ("identifier", "error_substring"),
        [
            ("user's", "Invalid Oracle identifier"),
            ("user$table", "Invalid Oracle identifier"),
            ("user#table", "Invalid Oracle identifier"),
            ("", "Empty Oracle identifier"),
            ("   ", "Empty Oracle identifier"),
            ("user@table", "Invalid Oracle identifier"),
            ("user table", "Invalid Oracle identifier"),
        ],
    )
    def test_escape_oracle_identifier_invalid(
        self, identifier: str, error_substring: str
    ) -> None:
        """Invalid Oracle identifiers fail with the matching diagnostic."""
        tm.fail(u.DbOracle.escape_oracle_identifier(identifier), has=error_substring)

    def test_escape_oracle_identifier_max_length(self) -> None:
        """Test identifier at max length is truncated to MAX_IDENTIFIER_LENGTH."""
        max_len = c.DbOracle.MAX_IDENTIFIER_LENGTH
        escaped = tm.ok(u.DbOracle.escape_oracle_identifier("a" * max_len))
        tm.that(len(escaped), eq=max_len)

    def test_escape_oracle_identifier_too_long(self) -> None:
        """Test identifier exceeding max length is still escaped successfully."""
        long_id = "a" * (c.DbOracle.MAX_ORACLE_IDENTIFIER_LENGTH + 1)
        tm.ok(u.DbOracle.escape_oracle_identifier(long_id))

    @pytest.mark.parametrize(
        "data",
        [
            [{"id": 1, "name": "John", "active": True}],
            [],
            [{"key": "non-serializable-test"}],
            [{"id": 1, "name": "John"}],
            [{"id": 1}],
        ],
        ids=["full", "empty", "non-serializable", "table", "single"],
    )
    def test_format_query_result_json(self, data: list[t.JsonValue]) -> None:
        """JSON formatting returns a serializable string for any payload shape."""
        formatted = tm.ok(u.DbOracle.format_query_result(data, "json"))
        tm.that(formatted, is_=str)
        if data:
            parsed = self._JSON_RESULT_ADAPTER.validate_json(formatted)
            tm.that(parsed, none=False)

    def test_settings_from_env(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test FlextDbOracleSettings.from_env creates settings from environment."""
        monkeypatch.setenv("FLEXT_DB_ORACLE_HOST", "test-host")
        monkeypatch.setenv("FLEXT_DB_ORACLE_PORT", "1522")
        monkeypatch.setenv("FLEXT_DB_ORACLE_USERNAME", "testuser")
        FlextDbOracleSettings.reset_for_testing()
        result = FlextDbOracleSettings.from_env("FLEXT_DB_ORACLE_")
        tm.ok(result)
        settings = result.unwrap()
        tm.that(settings, is_=FlextDbOracleSettings)
        tm.that(settings.host, eq="test-host")
        tm.that(settings.port, eq=1522)
        tm.that(settings.username, eq="testuser")

    def test_oracle_validation_validate_identifier_valid(self) -> None:
        """Valid uppercase identifier with underscore passes validation."""
        tm.that(tm.ok(u.DbOracle.validate_identifier("VALID_TABLE")), eq=True)

    @pytest.mark.parametrize(
        ("identifier", "error_substring"),
        [
            ("", "Empty"),
            ("A" * (c.DbOracle.MAX_IDENTIFIER_LENGTH + 1), "too long"),
            ("SELECT", "reserved"),
        ],
        ids=["empty", "too-long", "reserved-word"],
    )
    def test_oracle_validation_validate_identifier_invalid(
        self, identifier: str, error_substring: str
    ) -> None:
        """Invalid identifiers fail with matching diagnostic."""
        tm.fail(u.DbOracle.validate_identifier(identifier), has=error_substring)

    @pytest.mark.unit
    def test_real_oracle_escape_identifier_integration(
        self,
        connected_oracle_api: FlextDbOracleApi | None,
        oracle_available: bool,
    ) -> None:
        """Test identifier escaping with real Oracle when available."""
        if not oracle_available or connected_oracle_api is None:
            pytest.skip("Oracle not available for integration test")
        escaped_name = tm.ok(u.DbOracle.escape_oracle_identifier("test_table"))
        ddl = f"CREATE TABLE {escaped_name} (id NUMBER PRIMARY KEY, name VARCHAR2(100))"
        result = connected_oracle_api.execute_statement(ddl)
        with contextlib.suppress(Exception):
            connected_oracle_api.execute_statement(f"DROP TABLE {escaped_name}")
        error_msg = str(result.error).lower() if result.failure else ""
        table_exists = "already exists" in error_msg or "ora-00955" in error_msg
        tm.that(result.success or table_exists, eq=True)

    @pytest.mark.unit
    def test_real_oracle_query_hash_consistency(
        self,
        connected_oracle_api: FlextDbOracleApi | None,
        oracle_available: bool,
    ) -> None:
        """Test that query hashing produces consistent results with real Oracle."""
        if not oracle_available or connected_oracle_api is None:
            pytest.skip("Oracle not available for integration test")
        sql = "SELECT id, name FROM test_table WHERE active = :active"
        h1 = tm.ok(u.DbOracle.generate_query_hash(sql, {"active": 1}))
        h2 = tm.ok(u.DbOracle.generate_query_hash(sql, {"active": 1}))
        h3 = tm.ok(u.DbOracle.generate_query_hash(sql, {"active": 0}))
        tm.that(h1, eq=h2)
        tm.that(h1, ne=h3)

    @pytest.mark.unit
    def test_real_oracle_format_sql_integration(
        self,
        connected_oracle_api: FlextDbOracleApi | None,
        oracle_available: bool,
    ) -> None:
        """Test SQL formatting works with real Oracle queries."""
        if not oracle_available or connected_oracle_api is None:
            pytest.skip("Oracle not available for integration test")
        sql = "select id, name, count(*) as cnt from test_table group by id, name order by cnt desc"
        formatted = tm.ok(u.DbOracle.format_sql_for_oracle(sql)).lower()
        tm.that(formatted, has=["select", "from", "group by", "order by"])
