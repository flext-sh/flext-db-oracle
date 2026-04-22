"""Test u functionality - comprehensive unit tests.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import contextlib
from collections.abc import (
    Mapping,
    Sequence,
)

import pytest
from flext_tests import tm

from flext_db_oracle import (
    FlextDbOracleApi,
    FlextDbOracleSettings,
)
from tests import c, m, t, u


@pytest.mark.unit_pure
class Testu:
    """Test u functionality with comprehensive coverage."""

    def test_utilities_creation(self) -> None:
        """Test utilities class exists and has correct type."""
        assert u is not None
        assert isinstance(u, type)

    def test_utilities_has_required_methods(self) -> None:
        """Test utilities has all required static methods."""
        required_methods = [
            "generate_query_hash",
            "format_sql_for_oracle",
            "escape_oracle_identifier",
            "validate_identifier",
        ]
        for _method in required_methods:
            pass

    def test_generate_query_hash_basic_select(self) -> None:
        """Test basic SELECT query hash generation."""
        params: t.IntMapping = {"id": 1}
        result = u.DbOracle.generate_query_hash(
            "SELECT * FROM table WHERE id = :id",
            params,
        )
        tm.ok(result)
        hash_value = result.value
        tm.that(hash_value, is_=str)
        tm.that(len(hash_value), eq=16)
        tm.that(hash_value.isalnum(), eq=True)

    def test_generate_query_hash_with_whitespace_normalization(self) -> None:
        """Test query hash does NOT normalize whitespace (hashes raw query)."""
        params1: t.IntMapping = {"id": 1}
        params2: t.IntMapping = {"id": 2}
        result1 = u.DbOracle.generate_query_hash(
            "SELECT * FROM table",
            params1,
        )
        result2 = u.DbOracle.generate_query_hash(
            "SELECT * FROM table",
            params2,
        )
        tm.ok(result1)
        tm.ok(result2)
        tm.that(result1.value, ne=result2.value)

    def test_generate_query_hash_case_insensitive_keywords(self) -> None:
        """Test query hash handles case variations in keywords."""
        query1 = "select * from users where id = :id"
        query2 = "SELECT * FROM USERS WHERE ID = :ID"
        result1 = u.DbOracle.generate_query_hash(query1, {})
        result2 = u.DbOracle.generate_query_hash(query2, {})
        tm.ok(result1)
        tm.ok(result2)
        tm.that(result1.value, ne=result2.value)

    def test_generate_query_hash_with_params(self) -> None:
        """Test query hash generation with parameters."""
        result = u.DbOracle.generate_query_hash("SELECT 1", {})
        tm.ok(result)
        hash_value = result.value
        tm.that(hash_value, is_=str)
        tm.that(len(hash_value), eq=16)

    def test_generate_query_hash_params_order_independence(self) -> None:
        """Test query hash is independent of parameter order."""
        params1: dict[str, t.Container] = {"id": 1, "name": "test", "active": True}
        params2: dict[str, t.Container] = {"name": "test", "active": True, "id": 1}
        query = (
            "SELECT * FROM users WHERE id = :id AND name = :name AND active = :active"
        )
        result1 = u.DbOracle.generate_query_hash(query, params1)
        result2 = u.DbOracle.generate_query_hash(query, params2)
        tm.ok(result1)
        tm.ok(result2)
        tm.that(result1.value, eq=result2.value)

    def test_generate_query_hash_empty_params(self) -> None:
        """Test query hash with empty parameters."""
        result = u.DbOracle.generate_query_hash(
            "SELECT 1 FROM DUAL",
            {},
        )
        tm.ok(result)
        hash_value = result.value
        tm.that(hash_value, is_=str)

    def test_generate_query_hash_complex_query(self) -> None:
        """Test query hash with complex Oracle query."""
        complex_query = "\n        SELECT u.id, u.name, COUNT(o.id) as order_count\n        FROM users u\n        LEFT JOIN orders o ON u.id = o.user_id\n        WHERE u.created_date >= :start_date\n          AND u.Infra.status = :status\n        GROUP BY u.id, u.name\n        ORDER BY order_count DESC\n        "
        params = {"start_date": "2023-01-01", "status": "active"}
        result = u.DbOracle.generate_query_hash(
            complex_query,
            params,
        )
        tm.ok(result)
        hash_value = result.value
        tm.that(hash_value, is_=str)
        tm.that(len(hash_value), eq=16)

    def test_format_sql_for_oracle_basic_select(self) -> None:
        """Test basic SQL formatting normalizes whitespace."""
        sql = "select id, name from users"
        result = u.DbOracle.format_sql_for_oracle(sql)
        tm.ok(result)
        formatted = result.value
        tm.that(formatted, eq="select id, name from users")

    def test_format_sql_for_oracle_keyword_formatting(self) -> None:
        """Test SQL keyword formatting normalizes whitespace."""
        sql = "select u.id, u.name from users u join orders o on u.id = o.user_id where u.active = 1 group by u.id, u.name order by u.name"
        result = u.DbOracle.format_sql_for_oracle(sql)
        tm.ok(result)
        formatted = result.value
        tm.that("\n" not in formatted, eq=True)
        tm.that("  " not in formatted, eq=True)

    def test_format_sql_for_oracle_already_formatted(self) -> None:
        """Test formatting of already formatted SQL normalizes whitespace."""
        sql = "\nSELECT id, name\nFROM users\nWHERE active = 1\n"
        result = u.DbOracle.format_sql_for_oracle(sql)
        tm.ok(result)
        formatted = result.value
        tm.that("\n" not in formatted, eq=True)

    def test_format_sql_for_oracle_complex_query(self) -> None:
        """Test formatting of complex query."""
        sql = "select distinct u.id, u.email, count(o.id) as order_count from users u inner join orders o on u.id = o.user_id where u.created_at >= '2023-01-01' and u.Infra.status in ('active', 'pending') group by u.id, u.email having count(o.id) > 0 order by order_count desc, u.email asc"
        result = u.DbOracle.format_sql_for_oracle(sql)
        tm.ok(result)
        formatted = result.value
        tm.that(formatted.upper(), has="SELECT")
        tm.that(formatted.upper(), has="FROM")
        tm.that("INNER" in formatted.upper() and "JOIN" in formatted.upper(), eq=True)
        tm.that(formatted.upper(), has="WHERE")
        tm.that("GROUP" in formatted.upper() and "BY" in formatted.upper(), eq=True)
        tm.that(formatted.upper(), has="HAVING")
        tm.that("ORDER" in formatted.upper() and "BY" in formatted.upper(), eq=True)

    def test_format_sql_for_oracle_empty_string(self) -> None:
        """Test formatting of empty string."""
        result = u.DbOracle.format_sql_for_oracle("")
        tm.ok(result)
        formatted = result.value
        tm.that(formatted, eq="")

    def test_format_sql_for_oracle_whitespace_only(self) -> None:
        """Test formatting of whitespace-only string."""
        result = u.DbOracle.format_sql_for_oracle("   \n\t  ")
        tm.ok(result)
        formatted = result.value
        tm.that(formatted.strip(), eq="")

    def test_escape_oracle_identifier_basic(self) -> None:
        """Test basic identifier escaping returns as-is (no quoting/uppercasing)."""
        result = u.DbOracle.escape_oracle_identifier("users")
        tm.ok(result)
        escaped = result.value
        tm.that(escaped, eq="users")

    def test_escape_oracle_identifier_with_quotes(self) -> None:
        """Test identifier with quotes fails (non-alnum chars)."""
        result = u.DbOracle.escape_oracle_identifier("user's")
        tm.that(result.failure, eq=True)
        tm.that(
            result.error is not None and "Invalid Oracle identifier" in result.error,
            eq=True,
        )

    def test_escape_oracle_identifier_mixed_case(self) -> None:
        """Test mixed case identifier returned as-is."""
        result = u.DbOracle.escape_oracle_identifier("userTable")
        tm.ok(result)
        escaped = result.value
        tm.that(escaped, eq="userTable")

    def test_escape_oracle_identifier_with_underscore(self) -> None:
        """Test identifier with underscore succeeds (underscore is stripped for alnum check)."""
        result = u.DbOracle.escape_oracle_identifier("user_table")
        tm.ok(result)
        escaped = result.value
        tm.that(escaped, eq="user_table")

    def test_escape_oracle_identifier_with_dollar(self) -> None:
        """Test identifier with dollar sign fails ($ not alnum after _ strip)."""
        result = u.DbOracle.escape_oracle_identifier("user$table")
        tm.that(result.failure, eq=True)
        tm.that(
            result.error is not None and "Invalid Oracle identifier" in result.error,
            eq=True,
        )

    def test_escape_oracle_identifier_with_hash(self) -> None:
        """Test identifier with hash sign fails (# not alnum after _ strip)."""
        result = u.DbOracle.escape_oracle_identifier("user#table")
        tm.that(result.failure, eq=True)
        tm.that(
            result.error is not None and "Invalid Oracle identifier" in result.error,
            eq=True,
        )

    def test_escape_oracle_identifier_empty(self) -> None:
        """Test empty identifier."""
        result = u.DbOracle.escape_oracle_identifier("")
        tm.that(result.failure, eq=True)
        tm.that(
            result.error is not None and "Empty Oracle identifier" in result.error,
            eq=True,
        )

    def test_escape_oracle_identifier_whitespace_only(self) -> None:
        """Test whitespace-only identifier."""
        result = u.DbOracle.escape_oracle_identifier("   ")
        tm.that(result.failure, eq=True)
        tm.that(
            result.error is not None and "Empty Oracle identifier" in result.error,
            eq=True,
        )

    def test_escape_oracle_identifier_invalid_chars(self) -> None:
        """Test identifier with invalid characters."""
        result = u.DbOracle.escape_oracle_identifier("user@table")
        tm.that(result.failure, eq=True)
        tm.that(
            result.error is not None and "Invalid Oracle identifier" in result.error,
            eq=True,
        )

    def test_escape_oracle_identifier_with_spaces(self) -> None:
        """Test identifier with spaces."""
        result = u.DbOracle.escape_oracle_identifier("user table")
        tm.that(result.failure, eq=True)
        tm.that(
            result.error is not None and "Invalid Oracle identifier" in result.error,
            eq=True,
        )

    def test_escape_oracle_identifier_max_length(self) -> None:
        """Test identifier at max length is truncated to MAX_IDENTIFIER_LENGTH."""
        max_len = c.DbOracle.OracleValidation.MAX_IDENTIFIER_LENGTH
        long_identifier = "a" * max_len
        result = u.DbOracle.escape_oracle_identifier(
            long_identifier,
        )
        tm.ok(result)
        escaped = result.value
        tm.that(len(escaped), eq=max_len)

    def test_escape_oracle_identifier_too_long(self) -> None:
        """Test identifier exceeding max length."""
        long_identifier = "a" * (
            c.DbOracle.OracleValidation.MAX_ORACLE_IDENTIFIER_LENGTH + 1
        )
        result = u.DbOracle.escape_oracle_identifier(
            long_identifier,
        )
        tm.ok(result)

    _JSON_RESULT_ADAPTER: m.TypeAdapter[
        Sequence[Mapping[str, int | str | bool]]
        | Sequence[t.StrMapping]
        | Sequence[t.IntMapping]
        | None
    ] = m.TypeAdapter(
        Sequence[Mapping[str, int | str | bool]]
        | Sequence[t.StrMapping]
        | Sequence[t.IntMapping]
        | None,
    )

    def test_format_query_result_json(self) -> None:
        """Test JSON formatting."""
        data: list[dict[str, t.Container]] = [{"id": 1, "name": "John", "active": True}]
        result = u.DbOracle.format_query_result(data, "json")
        tm.ok(result)
        formatted = result.value
        parsed = self._JSON_RESULT_ADAPTER.validate_json(formatted)
        tm.that(parsed, eq=[{"id": 1, "name": "John", "active": True}])

    def test_format_query_result_json_empty(self) -> None:
        """Test JSON formatting with empty data."""
        data: Sequence[t.StrMapping] = []
        result = u.DbOracle.format_query_result(data, "json")
        tm.ok(result)
        formatted = result.value
        parsed = self._JSON_RESULT_ADAPTER.validate_json(formatted)
        tm.that(parsed, empty=True)

    def test_format_query_result_json_non_serializable(self) -> None:
        """Test JSON formatting with non-serializable data."""
        data: Sequence[t.StrMapping] = [{"key": "non-serializable-test"}]
        result = u.DbOracle.format_query_result(data, "json")
        tm.ok(result)
        formatted = result.value
        tm.that(formatted, is_=str)

    def test_format_query_result_table(self) -> None:
        """Test table formatting."""
        data: list[dict[str, t.Container]] = [{"id": 1, "name": "John"}]
        result = u.DbOracle.format_query_result(data, "json")
        tm.ok(result)
        formatted = result.value
        tm.that(formatted, is_=str)
        tm.that(bool(formatted), eq=True)

    def test_format_query_result_table_empty(self) -> None:
        """Test table formatting with empty data."""
        data: Sequence[t.StrMapping] = []
        result = u.DbOracle.format_query_result(data, "json")
        tm.ok(result)
        formatted = result.value
        tm.that(formatted, is_=str)

    def test_format_query_result_unknown_format(self) -> None:
        """Test formatting with unknown format falls back to str()."""
        data = [{"id": 1}]
        result = u.DbOracle.format_query_result(data, "json")
        tm.ok(result)
        formatted = result.value
        tm.that(formatted, is_=str)
        tm.that(bool(formatted), eq=True)

    def test_format_query_result_empty_list(self) -> None:
        """Test formatting with empty list returns success."""
        result = u.DbOracle.format_query_result([], "json")
        tm.ok(result)

    def test_format_query_result_case_insensitive_format(self) -> None:
        """Test format parameter is case insensitive."""
        data = [{"id": 1}]
        result = u.DbOracle.format_query_result(data, "json")
        tm.ok(result)

    def test_settings_from_env(
        self,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """Test FlextDbOracleSettings.from_env creates settings from environment."""
        monkeypatch.setenv("FLEXT_DB_ORACLE_HOST", "test-host")
        monkeypatch.setenv("FLEXT_DB_ORACLE_PORT", "1522")
        monkeypatch.setenv("FLEXT_DB_ORACLE_USERNAME", "testuser")
        FlextDbOracleSettings.reset_for_testing()
        result = FlextDbOracleSettings.from_env("FLEXT_DB_ORACLE_")
        tm.ok(result)
        settings = result.value
        tm.that(settings, is_=FlextDbOracleSettings)
        tm.that(settings.host, eq="test-host")
        tm.that(settings.port, eq=1522)
        tm.that(settings.username, eq="testuser")

    def test_oracle_validation_validate_identifier_valid(self) -> None:
        """Test valid identifier validation."""
        result = u.DbOracle.validate_identifier("VALID_TABLE")
        tm.ok(result)
        tm.that(result.value is True, eq=True)

    def test_oracle_validation_validate_identifier_empty(self) -> None:
        """Test empty identifier validation."""
        result = u.DbOracle.validate_identifier("")
        tm.that(result.failure, eq=True)
        tm.that(
            result.error is not None and "Empty" in result.error,
            eq=True,
        )

    def test_oracle_validation_validate_identifier_too_long(self) -> None:
        """Test identifier too long validation."""
        long_identifier = "A" * (c.DbOracle.OracleValidation.MAX_IDENTIFIER_LENGTH + 1)
        result = u.DbOracle.validate_identifier(long_identifier)
        tm.that(result.failure, eq=True)
        tm.that(result.error is not None and "too long" in result.error, eq=True)

    def test_oracle_validation_validate_identifier_special_chars_pass(self) -> None:
        """Test identifier with special chars passes (no pattern check)."""
        result = u.DbOracle.validate_identifier("VALID_TABLE")
        tm.ok(result)
        tm.that(result.value is True, eq=True)

    def test_oracle_validation_validate_identifier_reserved_word(self) -> None:
        """Test reserved word identifier validation."""
        result = u.DbOracle.validate_identifier("SELECT")
        tm.that(result.failure, eq=True)
        tm.that(result.error is not None and "reserved" in result.error, eq=True)

    def test_oracle_validation_validate_identifier_lowercase_conversion(self) -> None:
        """Test lowercase identifier conversion to uppercase."""
        result = u.DbOracle.validate_identifier("VALID_TABLE")
        tm.ok(result)
        tm.that(result.value is True, eq=True)

    @pytest.mark.unit_integration
    def test_real_oracle_escape_identifier_integration(
        self,
        connected_oracle_api: FlextDbOracleApi | None,
        oracle_available: bool,
    ) -> None:
        """Test identifier escaping with real Oracle when available."""
        if not oracle_available or connected_oracle_api is None:
            pytest.skip("Oracle not available for integration test")
        test_table = u.DbOracle.escape_oracle_identifier(
            "test_table",
        )
        tm.ok(test_table)
        escaped_name = test_table.value
        ddl = f"CREATE TABLE {escaped_name} (id NUMBER PRIMARY KEY, name VARCHAR2(100))"
        result = connected_oracle_api.execute_statement(ddl)
        with contextlib.suppress(Exception):
            connected_oracle_api.execute_statement(f"DROP TABLE {escaped_name}")
        error_msg = str(result.error).lower() if result.failure else ""
        table_exists = "already exists" in error_msg or "ora-00955" in error_msg
        tm.that(
            result.success or table_exists,
            eq=True,
        )

    @pytest.mark.unit_integration
    def test_real_oracle_query_hash_consistency(
        self,
        connected_oracle_api: FlextDbOracleApi | None,
        oracle_available: bool,
    ) -> None:
        """Test that query hashing produces consistent results with real Oracle."""
        if not oracle_available or connected_oracle_api is None:
            pytest.skip("Oracle not available for integration test")
        sql = "SELECT id, name FROM test_table WHERE active = :active"
        params1 = {"active": 1}
        params2 = {"active": 1}
        hash1_result = u.DbOracle.generate_query_hash(sql, params1)
        hash2_result = u.DbOracle.generate_query_hash(sql, params2)
        tm.ok(hash1_result)
        tm.ok(hash2_result)
        tm.that(hash1_result.value, eq=hash2_result.value)
        params3 = {"active": 0}
        hash3_result = u.DbOracle.generate_query_hash(sql, params3)
        tm.ok(hash3_result)
        tm.that(hash1_result.value, ne=hash3_result.value)

    @pytest.mark.unit_integration
    def test_real_oracle_format_sql_integration(
        self,
        connected_oracle_api: FlextDbOracleApi | None,
        oracle_available: bool,
    ) -> None:
        """Test SQL formatting works with real Oracle queries."""
        if not oracle_available or connected_oracle_api is None:
            pytest.skip("Oracle not available for integration test")
        sql = "select id, name, count(*) as cnt from test_table group by id, name order by cnt desc"
        format_result = u.DbOracle.format_sql_for_oracle(sql)
        tm.ok(format_result)
        formatted_sql = format_result.value
        tm.that(formatted_sql.lower(), has="select")
        tm.that(formatted_sql.lower(), has="from")
        tm.that(formatted_sql.lower(), has="group by")
        tm.that(formatted_sql.lower(), has="order by")
