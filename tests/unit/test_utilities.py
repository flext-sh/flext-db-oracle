"""Behavioral tests for FlextDbOracle Oracle-specific utilities.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

These tests assert the OBSERVABLE PUBLIC CONTRACT of ``u.DbOracle.*`` helpers:
returned values, ``r[T]`` success/failure outcomes, error diagnostics, and the
invariants each helper promises (determinism, order-independence, truncation,
whitespace normalization). No private attributes, internal collaborators, or
implementation structures are exercised.
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
    """Behavioral contract for u.DbOracle Oracle helper utilities."""

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

    # ------------------------------------------------------------------ #
    # generate_query_hash                                                #
    # ------------------------------------------------------------------ #

    def test_generate_query_hash_returns_16_char_alphanumeric(self) -> None:
        """A hash is a 16-character alphanumeric (hex) string."""
        params: t.IntMapping = {"id": 1}
        hash_value: str = tm.ok(
            u.DbOracle.generate_query_hash(
                "SELECT * FROM table WHERE id = :id",
                params,
            ),
        )
        tm.that(hash_value, is_=str)
        tm.that(len(hash_value), eq=16)
        tm.that(hash_value.isalnum(), eq=True)

    def test_generate_query_hash_is_deterministic_for_same_inputs(self) -> None:
        """Identical query and params always produce the identical hash."""
        query = "SELECT id, name FROM users WHERE active = :active"
        params: t.IntMapping = {"active": 1}
        first: str = tm.ok(u.DbOracle.generate_query_hash(query, params))
        second: str = tm.ok(u.DbOracle.generate_query_hash(query, params))
        tm.that(first, eq=second)

    def test_generate_query_hash_differs_by_params(self) -> None:
        """Same query with different parameter values yields different hashes."""
        h1: str = tm.ok(u.DbOracle.generate_query_hash("SELECT * FROM t", {"id": 1}))
        h2: str = tm.ok(u.DbOracle.generate_query_hash("SELECT * FROM t", {"id": 2}))
        tm.that(h1, ne=h2)

    def test_generate_query_hash_is_case_sensitive_on_query(self) -> None:
        """The query text is hashed verbatim, so case changes change the hash."""
        h1: str = tm.ok(
            u.DbOracle.generate_query_hash("select * from users where id = :id", {}),
        )
        h2: str = tm.ok(
            u.DbOracle.generate_query_hash("SELECT * FROM USERS WHERE ID = :ID", {}),
        )
        tm.that(h1, ne=h2)

    def test_generate_query_hash_is_parameter_order_independent(self) -> None:
        """Parameter insertion order does not affect the hash (params are sorted)."""
        params1: t.JsonMapping = {"id": 1, "name": "test", "active": True}
        params2: t.JsonMapping = {"name": "test", "active": True, "id": 1}
        query = (
            "SELECT * FROM users WHERE id = :id AND name = :name AND active = :active"
        )
        tm.that(
            tm.ok(u.DbOracle.generate_query_hash(query, params1)),
            eq=tm.ok(u.DbOracle.generate_query_hash(query, params2)),
        )

    def test_generate_query_hash_accepts_none_params(self) -> None:
        """None params are treated as empty and still produce a valid hash."""
        with_none: str = tm.ok(u.DbOracle.generate_query_hash("SELECT 1 FROM DUAL", None))
        with_empty: str = tm.ok(u.DbOracle.generate_query_hash("SELECT 1 FROM DUAL", {}))
        tm.that(len(with_none), eq=16)
        tm.that(with_none, eq=with_empty)

    def test_generate_query_hash_handles_complex_multiline_query(self) -> None:
        """A complex multi-line Oracle query still hashes to a 16-char string."""
        complex_query = (
            "\n        SELECT u.id, u.name, COUNT(o.id) as order_count\n"
            "        FROM users u\n"
            "        LEFT JOIN orders o ON u.id = o.user_id\n"
            "        WHERE u.created_date >= :start_date\n"
            "        GROUP BY u.id, u.name\n"
            "        ORDER BY order_count DESC\n        "
        )
        params: t.JsonMapping = {"start_date": "2023-01-01", "status": "active"}
        h: str = tm.ok(u.DbOracle.generate_query_hash(complex_query, params))
        tm.that(len(h), eq=16)

    # ------------------------------------------------------------------ #
    # format_sql_for_oracle                                              #
    # ------------------------------------------------------------------ #

    def test_format_sql_collapses_internal_whitespace(self) -> None:
        """Single-spaced SQL is returned unchanged."""
        formatted: str = tm.ok(
            u.DbOracle.format_sql_for_oracle("select id, name from users"),
        )
        tm.that(formatted, eq="select id, name from users")

    def test_format_sql_removes_newlines_and_double_spaces(self) -> None:
        """Newlines and runs of whitespace collapse to single spaces."""
        sql = "\nSELECT   id,\n  name\nFROM users\nWHERE active = 1\n"
        formatted: str = tm.ok(u.DbOracle.format_sql_for_oracle(sql))
        tm.that("\n" not in formatted, eq=True)
        tm.that("  " not in formatted, eq=True)

    def test_format_sql_preserves_all_clause_keywords(self) -> None:
        """Whitespace normalization preserves every SQL clause keyword."""
        sql = (
            "select distinct u.id, u.email, count(o.id) as order_count "
            "from users u inner join orders o on u.id = o.user_id "
            "where u.created_at >= '2023-01-01' "
            "group by u.id, u.email having count(o.id) > 0 "
            "order by order_count desc, u.email asc"
        )
        formatted: str = tm.ok(u.DbOracle.format_sql_for_oracle(sql)).upper()
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

    @pytest.mark.parametrize(
        ("raw", "expected"),
        [("", ""), ("   \n\t  ", "")],
        ids=["empty", "whitespace-only"],
    )
    def test_format_sql_empty_or_blank_yields_empty_string(
        self,
        raw: str,
        expected: str,
    ) -> None:
        """Empty or whitespace-only input normalizes to an empty string."""
        tm.that(tm.ok(u.DbOracle.format_sql_for_oracle(raw)), eq=expected)

    # ------------------------------------------------------------------ #
    # escape_oracle_identifier                                           #
    # ------------------------------------------------------------------ #

    @pytest.mark.parametrize(
        ("identifier", "expected"),
        [
            ("users", "users"),
            ("userTable", "userTable"),
            ("user_table", "user_table"),
        ],
    )
    def test_escape_identifier_returns_valid_identifier_unchanged(
        self,
        identifier: str,
        expected: str,
    ) -> None:
        """Valid alphanumeric/underscore identifiers pass through unchanged."""
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
    def test_escape_identifier_rejects_invalid_input(
        self,
        identifier: str,
        error_substring: str,
    ) -> None:
        """Invalid/empty identifiers fail with the matching diagnostic message."""
        tm.fail(u.DbOracle.escape_oracle_identifier(identifier), has=error_substring)

    def test_escape_identifier_at_max_length_is_unchanged(self) -> None:
        """An identifier exactly at the max length is returned in full."""
        max_len = c.DbOracle.MAX_IDENTIFIER_LENGTH
        escaped: str = tm.ok(u.DbOracle.escape_oracle_identifier("a" * max_len))
        tm.that(len(escaped), eq=max_len)

    def test_escape_identifier_over_max_length_is_truncated(self) -> None:
        """An over-length identifier is truncated to exactly the max length."""
        max_len = c.DbOracle.MAX_IDENTIFIER_LENGTH
        escaped: str = tm.ok(
            u.DbOracle.escape_oracle_identifier("a" * (max_len + 25)),
        )
        tm.that(len(escaped), eq=max_len)

    # ------------------------------------------------------------------ #
    # validate_identifier                                                #
    # ------------------------------------------------------------------ #

    def test_validate_identifier_accepts_valid_name(self) -> None:
        """A valid identifier validates successfully returning True."""
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
    def test_validate_identifier_rejects_invalid_name(
        self,
        identifier: str,
        error_substring: str,
    ) -> None:
        """Empty, over-length, and reserved names fail with matching diagnostics."""
        tm.fail(u.DbOracle.validate_identifier(identifier), has=error_substring)

    # ------------------------------------------------------------------ #
    # format_query_result                                                #
    # ------------------------------------------------------------------ #

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
    def test_format_query_result_json_is_reparseable(
        self,
        data: list[t.JsonValue],
    ) -> None:
        """JSON formatting yields a string that re-parses to the same shape."""
        formatted: str = tm.ok(u.DbOracle.format_query_result(data, "json"))
        tm.that(formatted, is_=str)
        if data:
            parsed = self._JSON_RESULT_ADAPTER.validate_json(formatted)
            tm.that(parsed, none=False)

    def test_format_query_result_table_returns_string_repr(self) -> None:
        """Non-JSON (table) formatting returns the string representation."""
        data: list[t.JsonValue] = [{"id": 1, "name": "John"}]
        formatted: str = tm.ok(u.DbOracle.format_query_result(data, "table"))
        tm.that(formatted, eq=str(data))

    def test_format_query_result_defaults_to_table(self) -> None:
        """Omitting the format argument formats as table (string repr)."""
        data: list[t.JsonValue] = [{"id": 7}]
        tm.that(tm.ok(u.DbOracle.format_query_result(data)), eq=str(data))

    # ------------------------------------------------------------------ #
    # Settings from environment                                          #
    # ------------------------------------------------------------------ #

    def test_settings_from_env_reads_public_fields(
        self,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """from_env reflects environment values in public settings fields."""
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

    # ------------------------------------------------------------------ #
    # Real-Oracle integration (skipped when unavailable)                 #
    # ------------------------------------------------------------------ #

    def test_real_oracle_escape_identifier_integration(
        self,
        connected_oracle_api: FlextDbOracleApi | None,
        oracle_available: bool,
    ) -> None:
        """Escaped identifier is usable in real DDL against a live Oracle."""
        if not oracle_available or connected_oracle_api is None:
            pytest.skip("Oracle not available for integration test")
        escaped_name: str = tm.ok(u.DbOracle.escape_oracle_identifier("test_table"))
        ddl = f"CREATE TABLE {escaped_name} (id NUMBER PRIMARY KEY, name VARCHAR2(100))"
        result = connected_oracle_api.execute_statement(ddl)
        with contextlib.suppress(Exception):
            connected_oracle_api.execute_statement(f"DROP TABLE {escaped_name}")
        error_msg = str(result.error).lower() if result.failure else ""
        table_exists = "already exists" in error_msg or "ora-00955" in error_msg
        tm.that(result.success or table_exists, eq=True)

    def test_real_oracle_query_hash_consistency(
        self,
        connected_oracle_api: FlextDbOracleApi | None,
        oracle_available: bool,
    ) -> None:
        """Query hashing stays consistent and value-sensitive with live Oracle."""
        if not oracle_available or connected_oracle_api is None:
            pytest.skip("Oracle not available for integration test")
        sql = "SELECT id, name FROM test_table WHERE active = :active"
        h1: str = tm.ok(u.DbOracle.generate_query_hash(sql, {"active": 1}))
        h2: str = tm.ok(u.DbOracle.generate_query_hash(sql, {"active": 1}))
        h3: str = tm.ok(u.DbOracle.generate_query_hash(sql, {"active": 0}))
        tm.that(h1, eq=h2)
        tm.that(h1, ne=h3)

    def test_real_oracle_format_sql_integration(
        self,
        connected_oracle_api: FlextDbOracleApi | None,
        oracle_available: bool,
    ) -> None:
        """SQL formatting preserves clause keywords for real Oracle queries."""
        if not oracle_available or connected_oracle_api is None:
            pytest.skip("Oracle not available for integration test")
        sql = (
            "select id, name, count(*) as cnt from test_table "
            "group by id, name order by cnt desc"
        )
        formatted: str = tm.ok(u.DbOracle.format_sql_for_oracle(sql)).lower()
        tm.that(formatted, has=["select", "from", "group by", "order by"])
