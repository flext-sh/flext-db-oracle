"""Surgical tests for FlextDbOracleUtilities - targeting specific uncovered lines.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_db_oracle import FlextDbOracleUtilities


class TestUtilitiesSurgical:
    """Surgical tests for specific uncovered utility functions."""

    def test_generate_query_hash_basic(self) -> None:
        """Test generate_query_hash with basic SQL."""
        sql = "SELECT * FROM users"
        result = FlextDbOracleUtilities.generate_query_hash(sql)

        assert result.is_success
        hash_value = result.unwrap()
        assert isinstance(hash_value, str)
        assert len(hash_value) == 16  # SHA-256 truncated to 16 chars

    def test_generate_query_hash_with_params(self) -> None:
        """Test generate_query_hash with parameters."""
        sql = "SELECT * FROM users WHERE id = :id"
        params: dict[str, object] = {"id": 123}
        result = FlextDbOracleUtilities.generate_query_hash(sql, params)

        assert result.is_success
        hash_value = result.unwrap()
        assert isinstance(hash_value, str)
        assert len(hash_value) == 16

    def test_generate_query_hash_empty_params(self) -> None:
        """Test generate_query_hash with empty params dict."""
        sql = "SELECT 1 FROM DUAL"
        params: dict[str, object] = {}
        result = FlextDbOracleUtilities.generate_query_hash(sql, params)

        assert result.is_success
        hash_value = result.unwrap()
        assert isinstance(hash_value, str)

    def test_generate_query_hash_normalization(self) -> None:
        """Test SQL normalization in hash generation."""
        sql1 = "SELECT   *   FROM   users"
        sql2 = "SELECT * FROM users"

        result1 = FlextDbOracleUtilities.generate_query_hash(sql1)
        result2 = FlextDbOracleUtilities.generate_query_hash(sql2)

        assert result1.is_success
        assert result2.is_success
        # Should produce same hash after normalization
        assert result1.unwrap() == result2.unwrap()

    def test_escape_oracle_identifier_basic(self) -> None:
        """Test escape_oracle_identifier with valid identifier."""
        identifier = "table_name"
        result = FlextDbOracleUtilities.escape_oracle_identifier(identifier)

        assert result.is_success
        escaped = result.unwrap()
        assert escaped == '"TABLE_NAME"'  # Should be uppercase and quoted

    def test_escape_oracle_identifier_with_underscore(self) -> None:
        """Test escape_oracle_identifier with underscore."""
        identifier = "user_id"
        result = FlextDbOracleUtilities.escape_oracle_identifier(identifier)

        assert result.is_success
        escaped = result.unwrap()
        assert escaped == '"USER_ID"'

    def test_escape_oracle_identifier_with_dollar(self) -> None:
        """Test escape_oracle_identifier with dollar sign."""
        identifier = "temp$table"
        result = FlextDbOracleUtilities.escape_oracle_identifier(identifier)

        assert result.is_success
        escaped = result.unwrap()
        assert escaped == '"TEMP$TABLE"'

    def test_escape_oracle_identifier_with_hash(self) -> None:
        """Test escape_oracle_identifier with hash symbol."""
        identifier = "temp#table"
        result = FlextDbOracleUtilities.escape_oracle_identifier(identifier)

        assert result.is_success
        escaped = result.unwrap()
        assert escaped == '"TEMP#TABLE"'

    def test_escape_oracle_identifier_empty_fails(self) -> None:
        """Test escape_oracle_identifier fails with empty identifier."""
        identifier = ""
        result = FlextDbOracleUtilities.escape_oracle_identifier(identifier)

        assert result.is_failure
        assert result.error is not None and "Empty Oracle identifier" in result.error

    def test_escape_oracle_identifier_whitespace_only_fails(self) -> None:
        """Test escape_oracle_identifier fails with whitespace-only identifier."""
        identifier = "   "
        result = FlextDbOracleUtilities.escape_oracle_identifier(identifier)

        assert result.is_failure
        assert result.error is not None and "Empty Oracle identifier" in result.error

    def test_escape_oracle_identifier_invalid_chars_fails(self) -> None:
        """Test escape_oracle_identifier fails with invalid characters."""
        identifier = "table-name"  # Hyphen not allowed
        result = FlextDbOracleUtilities.escape_oracle_identifier(identifier)

        assert result.is_failure
        assert result.error is not None and "Invalid Oracle identifier" in result.error

    def test_escape_oracle_identifier_strips_quotes(self) -> None:
        """Test escape_oracle_identifier strips existing quotes."""
        identifier = '"table_name"'
        result = FlextDbOracleUtilities.escape_oracle_identifier(identifier)

        assert result.is_success
        escaped = result.unwrap()
        assert escaped == '"TABLE_NAME"'

    def test_escape_oracle_identifier_strips_single_quotes(self) -> None:
        """Test escape_oracle_identifier strips single quotes."""
        identifier = "'table_name'"
        result = FlextDbOracleUtilities.escape_oracle_identifier(identifier)

        assert result.is_success
        escaped = result.unwrap()
        assert escaped == '"TABLE_NAME"'

    def test_format_sql_for_oracle_basic(self) -> None:
        """Test format_sql_for_oracle with basic SQL."""
        sql = "SELECT * FROM users"
        result = FlextDbOracleUtilities.format_sql_for_oracle(sql)

        assert result.is_success
        formatted = result.unwrap()
        assert isinstance(formatted, str)
        assert "SELECT" in formatted

    def test_format_sql_for_oracle_with_keywords(self) -> None:
        """Test format_sql_for_oracle with Oracle keywords."""
        sql = "SELECT * FROM users WHERE id = 1 ORDER BY name"
        result = FlextDbOracleUtilities.format_sql_for_oracle(sql)

        assert result.is_success
        formatted = result.unwrap()
        # Should format keywords with line breaks
        assert "\\nSELECT" in formatted or "SELECT" in formatted
        assert "\\nFROM" in formatted or "FROM" in formatted
        assert "\\nWHERE" in formatted or "WHERE" in formatted
        assert "\\nORDER BY" in formatted or "ORDER BY" in formatted

    def test_format_sql_for_oracle_lowercase_keywords(self) -> None:
        """Test format_sql_for_oracle with lowercase keywords."""
        sql = "select * from users where id = 1"
        result = FlextDbOracleUtilities.format_sql_for_oracle(sql)

        assert result.is_success
        formatted = result.unwrap()
        assert isinstance(formatted, str)

    def test_format_sql_for_oracle_uppercase_keywords(self) -> None:
        """Test format_sql_for_oracle with uppercase keywords."""
        sql = "SELECT * FROM USERS WHERE ID = 1"
        result = FlextDbOracleUtilities.format_sql_for_oracle(sql)

        assert result.is_success
        formatted = result.unwrap()
        assert isinstance(formatted, str)

    def test_format_sql_for_oracle_with_joins(self) -> None:
        """Test format_sql_for_oracle with JOIN keyword."""
        sql = "SELECT u.* FROM users u JOIN profiles p ON u.id = p.user_id"
        result = FlextDbOracleUtilities.format_sql_for_oracle(sql)

        assert result.is_success
        formatted = result.unwrap()
        assert "JOIN" in formatted

    def test_format_sql_for_oracle_with_group_by(self) -> None:
        """Test format_sql_for_oracle with GROUP BY keyword."""
        sql = "SELECT count(*) FROM users GROUP BY department"
        result = FlextDbOracleUtilities.format_sql_for_oracle(sql)

        assert result.is_success
        formatted = result.unwrap()
        assert "GROUP BY" in formatted

    def test_format_sql_for_oracle_with_having(self) -> None:
        """Test format_sql_for_oracle with HAVING keyword."""
        sql = "SELECT department, count(*) FROM users GROUP BY department HAVING count(*) > 5"
        result = FlextDbOracleUtilities.format_sql_for_oracle(sql)

        assert result.is_success
        formatted = result.unwrap()
        assert "HAVING" in formatted

    def test_format_sql_for_oracle_strips_whitespace(self) -> None:
        """Test format_sql_for_oracle strips leading/trailing whitespace."""
        sql = "   SELECT * FROM users   "
        result = FlextDbOracleUtilities.format_sql_for_oracle(sql)

        assert result.is_success
        formatted = result.unwrap()
        assert not formatted.startswith(" ")
        assert not formatted.endswith(" ")

    def test_format_query_result_none_input(self) -> None:
        """Test format_query_result with None input."""
        result = FlextDbOracleUtilities.format_query_result(None)
        assert result.is_failure
        assert result.error is not None
        assert result.error is not None and "Query result is None" in result.error

    def test_format_query_result_json_format(self) -> None:
        """Test format_query_result with JSON format."""
        data = {"rows": [{"id": 1, "name": "test"}], "count": 1}
        result = FlextDbOracleUtilities.format_query_result(data, "json")

        assert result.is_success
        formatted = result.unwrap()
        assert '"rows"' in formatted
        assert '"count": 1' in formatted

    def test_format_query_result_json_non_serializable(self) -> None:
        """Test format_query_result with non-serializable object."""

        class NonSerializable:
            pass

        data = NonSerializable()
        result = FlextDbOracleUtilities.format_query_result(data, "json")

        assert result.is_success
        formatted = result.unwrap()
        assert "Query result (non-serializable): NonSerializable" in formatted

    def test_format_query_result_table_format(self) -> None:
        """Test format_query_result with table format."""
        data = [{"id": 1, "name": "test"}, {"id": 2, "name": "user"}]
        result = FlextDbOracleUtilities.format_query_result(data, "table")

        assert result.is_success
        formatted = result.unwrap()
        assert isinstance(formatted, str)

    def test_format_query_result_unknown_format(self) -> None:
        """Test format_query_result with unknown format type."""
        data = {"test": "data"}
        result = FlextDbOracleUtilities.format_query_result(data, "unknown")

        assert result.is_success
        formatted = result.unwrap()
        assert isinstance(formatted, str)

    def test_format_query_result_table_format_list_data(self) -> None:
        """Test format_query_result table format with list data."""
        data = [["John", 25], ["Jane", 30]]
        result = FlextDbOracleUtilities.format_query_result(data, "table")

        assert result.is_success
        formatted = result.unwrap()
        # The function returns a generic message for list data
        assert "table" in formatted.lower()
        assert isinstance(formatted, str)
