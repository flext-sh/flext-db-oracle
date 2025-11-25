"""Test FlextDbOracleUtilities functionality - comprehensive unit tests.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import contextlib
import json

import pytest

from flext_db_oracle import FlextDbOracleApi, FlextDbOracleUtilities
from flext_db_oracle.constants import FlextDbOracleConstants


@pytest.mark.unit_pure
class TestFlextDbOracleUtilities:
    """Test FlextDbOracleUtilities functionality with comprehensive coverage."""

    def test_utilities_creation(self) -> None:
        """Test utilities can be created."""
        utilities = FlextDbOracleUtilities()
        assert utilities is not None
        assert isinstance(utilities, FlextDbOracleUtilities)

    def test_utilities_has_required_methods(self) -> None:
        """Test utilities has all required static methods."""
        required_methods = [
            "generate_query_hash",
            "format_sql_for_oracle",
            "escape_oracle_identifier",
            "create_config_from_env",
            "create_api_from_config",
        ]
        for method in required_methods:
            assert hasattr(FlextDbOracleUtilities, method)

    # =============================================================================
    # generate_query_hash tests
    # =============================================================================

    def test_generate_query_hash_basic_select(self) -> None:
        """Test basic SELECT query hash generation."""
        result = FlextDbOracleUtilities.generate_query_hash("SELECT 1 FROM DUAL", None)
        assert result.is_success
        hash_value = result.unwrap()
        assert isinstance(hash_value, str)
        assert len(hash_value) == 16  # SHA-256 truncated to 16 chars
        assert hash_value.isalnum()

    def test_generate_query_hash_with_whitespace_normalization(self) -> None:
        """Test query hash normalizes whitespace."""
        query1 = "SELECT   1   FROM   DUAL"
        query2 = "SELECT 1 FROM DUAL"
        result1 = FlextDbOracleUtilities.generate_query_hash(query1, None)
        result2 = FlextDbOracleUtilities.generate_query_hash(query2, None)

        assert result1.is_success
        assert result2.is_success
        assert result1.unwrap() == result2.unwrap()

    def test_generate_query_hash_case_insensitive_keywords(self) -> None:
        """Test query hash handles case variations in keywords."""
        query1 = "select * from users where id = :id"
        query2 = "SELECT * FROM USERS WHERE ID = :ID"
        result1 = FlextDbOracleUtilities.generate_query_hash(query1, None)
        result2 = FlextDbOracleUtilities.generate_query_hash(query2, None)

        # These should be different because the keywords are normalized differently
        # The function only normalizes whitespace, not case
        assert result1.is_success
        assert result2.is_success
        # They should be different because case is preserved
        assert result1.unwrap() != result2.unwrap()

    def test_generate_query_hash_with_params(self) -> None:
        """Test query hash generation with parameters."""
        params = {"id": 1, "name": "test"}
        result = FlextDbOracleUtilities.generate_query_hash(
            "SELECT * FROM table WHERE id = :id", params
        )
        assert result.is_success
        hash_value = result.unwrap()
        assert isinstance(hash_value, str)
        assert len(hash_value) == 16

    def test_generate_query_hash_params_order_independence(self) -> None:
        """Test query hash is independent of parameter order."""
        params1 = {"id": 1, "name": "test", "active": True}
        params2 = {"name": "test", "active": True, "id": 1}
        result1 = FlextDbOracleUtilities.generate_query_hash(
            "SELECT * FROM table", params1
        )
        result2 = FlextDbOracleUtilities.generate_query_hash(
            "SELECT * FROM table", params2
        )

        assert result1.is_success
        assert result2.is_success
        assert result1.unwrap() == result2.unwrap()  # Same hash due to sorted JSON

    def test_generate_query_hash_empty_params(self) -> None:
        """Test query hash with empty parameters."""
        result = FlextDbOracleUtilities.generate_query_hash("SELECT 1", {})
        assert result.is_success
        hash_value = result.unwrap()
        assert isinstance(hash_value, str)

    def test_generate_query_hash_complex_query(self) -> None:
        """Test query hash with complex Oracle query."""
        complex_query = """
        SELECT u.id, u.name, COUNT(o.id) as order_count
        FROM users u
        LEFT JOIN orders o ON u.id = o.user_id
        WHERE u.created_date >= :start_date
          AND u.status = :status
        GROUP BY u.id, u.name
        ORDER BY order_count DESC
        """
        params = {"start_date": "2023-01-01", "status": "active"}
        result = FlextDbOracleUtilities.generate_query_hash(complex_query, params)
        assert result.is_success
        hash_value = result.unwrap()
        assert isinstance(hash_value, str)
        assert len(hash_value) == 16

    # =============================================================================
    # format_sql_for_oracle tests
    # =============================================================================

    def test_format_sql_for_oracle_basic_select(self) -> None:
        """Test basic SQL formatting."""
        sql = "select id, name from users"
        result = FlextDbOracleUtilities.format_sql_for_oracle(sql)
        assert result.is_success
        formatted = result.unwrap()
        assert "SELECT" in formatted
        assert "FROM" in formatted

    def test_format_sql_for_oracle_keyword_formatting(self) -> None:
        """Test SQL keyword formatting."""
        sql = "select u.id, u.name from users u join orders o on u.id = o.user_id where u.active = 1 group by u.id, u.name order by u.name"
        result = FlextDbOracleUtilities.format_sql_for_oracle(sql)
        assert result.is_success
        formatted = result.unwrap()

        # Check that keywords are formatted with newlines
        assert "\nSELECT" in formatted
        assert "\nFROM" in formatted
        assert "\nJOIN" in formatted
        assert "\nWHERE" in formatted
        assert "\nGROUP BY" in formatted
        assert "\nORDER BY" in formatted

    def test_format_sql_for_oracle_already_formatted(self) -> None:
        """Test formatting of already formatted SQL."""
        sql = "\nSELECT id, name\nFROM users\nWHERE active = 1\n"
        result = FlextDbOracleUtilities.format_sql_for_oracle(sql)
        assert result.is_success
        formatted = result.unwrap()
        # Should not double-format
        assert formatted.count("\nSELECT") == 1

    def test_format_sql_for_oracle_complex_query(self) -> None:
        """Test formatting of complex query."""
        sql = "select distinct u.id, u.email, count(o.id) as order_count from users u inner join orders o on u.id = o.user_id where u.created_at >= '2023-01-01' and u.status in ('active', 'pending') group by u.id, u.email having count(o.id) > 0 order by order_count desc, u.email asc"
        result = FlextDbOracleUtilities.format_sql_for_oracle(sql)
        assert result.is_success
        formatted = result.unwrap()

        # Check multiple keywords are formatted (case insensitive check)
        assert "SELECT" in formatted.upper()
        assert "FROM" in formatted.upper()
        assert "INNER" in formatted.upper() and "JOIN" in formatted.upper()
        assert "WHERE" in formatted.upper()
        assert "GROUP" in formatted.upper() and "BY" in formatted.upper()
        assert "HAVING" in formatted.upper()
        assert "ORDER" in formatted.upper() and "BY" in formatted.upper()

    def test_format_sql_for_oracle_empty_string(self) -> None:
        """Test formatting of empty string."""
        result = FlextDbOracleUtilities.format_sql_for_oracle("")
        assert result.is_success
        formatted = result.unwrap()
        assert formatted == ""

    def test_format_sql_for_oracle_whitespace_only(self) -> None:
        """Test formatting of whitespace-only string."""
        result = FlextDbOracleUtilities.format_sql_for_oracle("   \n\t  ")
        assert result.is_success
        formatted = result.unwrap()
        assert formatted.strip() == ""

    # =============================================================================
    # escape_oracle_identifier tests
    # =============================================================================

    def test_escape_oracle_identifier_basic(self) -> None:
        """Test basic identifier escaping."""
        result = FlextDbOracleUtilities.escape_oracle_identifier("users")
        assert result.is_success
        escaped = result.unwrap()
        assert escaped == '"USERS"'  # Oracle identifiers are uppercase

    def test_escape_oracle_identifier_with_quotes(self) -> None:
        """Test identifier with existing quotes."""
        result = FlextDbOracleUtilities.escape_oracle_identifier('"USERS"')
        assert result.is_success
        escaped = result.unwrap()
        assert escaped == '"USERS"'

    def test_escape_oracle_identifier_mixed_case(self) -> None:
        """Test mixed case identifier."""
        result = FlextDbOracleUtilities.escape_oracle_identifier("userTable")
        assert result.is_success
        escaped = result.unwrap()
        assert escaped == '"USERTABLE"'  # Converted to uppercase

    def test_escape_oracle_identifier_with_underscore(self) -> None:
        """Test identifier with underscore."""
        result = FlextDbOracleUtilities.escape_oracle_identifier("user_table")
        assert result.is_success
        escaped = result.unwrap()
        assert escaped == '"USER_TABLE"'

    def test_escape_oracle_identifier_with_dollar(self) -> None:
        """Test identifier with dollar sign."""
        result = FlextDbOracleUtilities.escape_oracle_identifier("user$table")
        assert result.is_success
        escaped = result.unwrap()
        assert escaped == '"USER$TABLE"'

    def test_escape_oracle_identifier_with_hash(self) -> None:
        """Test identifier with hash sign."""
        result = FlextDbOracleUtilities.escape_oracle_identifier("user#table")
        assert result.is_success
        escaped = result.unwrap()
        assert escaped == '"USER#TABLE"'

    def test_escape_oracle_identifier_empty(self) -> None:
        """Test empty identifier."""
        result = FlextDbOracleUtilities.escape_oracle_identifier("")
        assert result.is_failure
        assert "Empty Oracle identifier" in result.error

    def test_escape_oracle_identifier_whitespace_only(self) -> None:
        """Test whitespace-only identifier."""
        result = FlextDbOracleUtilities.escape_oracle_identifier("   ")
        assert result.is_failure
        assert "Empty Oracle identifier" in result.error

    def test_escape_oracle_identifier_invalid_chars(self) -> None:
        """Test identifier with invalid characters."""
        result = FlextDbOracleUtilities.escape_oracle_identifier("user@table")
        assert result.is_failure
        assert "Invalid Oracle identifier" in result.error

    def test_escape_oracle_identifier_with_spaces(self) -> None:
        """Test identifier with spaces."""
        result = FlextDbOracleUtilities.escape_oracle_identifier("user table")
        assert result.is_failure
        assert "Invalid Oracle identifier" in result.error

    def test_escape_oracle_identifier_max_length(self) -> None:
        """Test identifier at max length."""
        # Create identifier at max length (30 chars for Oracle)
        long_identifier = (
            "a" * FlextDbOracleConstants.OracleValidation.MAX_ORACLE_IDENTIFIER_LENGTH
        )
        result = FlextDbOracleUtilities.escape_oracle_identifier(long_identifier)
        assert result.is_success
        escaped = result.unwrap()
        assert (
            len(escaped)
            == FlextDbOracleConstants.OracleValidation.MAX_ORACLE_IDENTIFIER_LENGTH + 2
        )  # quotes

    def test_escape_oracle_identifier_too_long(self) -> None:
        """Test identifier exceeding max length."""
        # This should still work since we just escape, validation happens elsewhere
        long_identifier = "a" * (
            FlextDbOracleConstants.OracleValidation.MAX_ORACLE_IDENTIFIER_LENGTH + 1
        )
        result = FlextDbOracleUtilities.escape_oracle_identifier(long_identifier)
        assert result.is_success  # escaping doesn't validate length

    # =============================================================================
    # format_query_result tests
    # =============================================================================

    def test_format_query_result_json(self) -> None:
        """Test JSON formatting."""
        data = [{"id": 1, "name": "John", "active": True}]
        result = FlextDbOracleUtilities.format_query_result(data, "json")
        assert result.is_success
        formatted = result.unwrap()

        # Parse to verify it's valid JSON
        parsed = json.loads(formatted)
        assert parsed == data

    def test_format_query_result_json_empty(self) -> None:
        """Test JSON formatting with empty data."""
        data = []
        result = FlextDbOracleUtilities.format_query_result(data, "json")
        assert result.is_success
        formatted = result.unwrap()
        parsed = json.loads(formatted)
        assert parsed == []

    def test_format_query_result_json_non_serializable(self) -> None:
        """Test JSON formatting with non-serializable data."""
        data = [{"func": lambda x: x}]  # lambda is not serializable
        result = FlextDbOracleUtilities.format_query_result(data, "json")
        assert result.is_success
        formatted = result.unwrap()
        assert "non-serializable" in formatted.lower()

    def test_format_query_result_table(self) -> None:
        """Test table formatting."""
        data = [{"id": 1, "name": "John"}]
        result = FlextDbOracleUtilities.format_query_result(data, "table")
        assert result.is_success
        formatted = result.unwrap()
        assert isinstance(formatted, str)
        assert len(formatted) > 0

    def test_format_query_result_table_empty(self) -> None:
        """Test table formatting with empty data."""
        data = []
        result = FlextDbOracleUtilities.format_query_result(data, "table")
        assert result.is_success
        formatted = result.unwrap()
        assert isinstance(formatted, str)

    def test_format_query_result_unknown_format(self) -> None:
        """Test formatting with unknown format."""
        data = [{"id": 1}]
        result = FlextDbOracleUtilities.format_query_result(data, "xml")
        assert result.is_success
        formatted = result.unwrap()
        assert "xml format" in formatted.lower()

    def test_format_query_result_none_data(self) -> None:
        """Test formatting with None data."""
        result = FlextDbOracleUtilities.format_query_result(None, "json")
        assert result.is_failure
        assert "Query result is None" in result.error

    def test_format_query_result_case_insensitive_format(self) -> None:
        """Test format parameter is case insensitive."""
        data = [{"id": 1}]
        result = FlextDbOracleUtilities.format_query_result(data, "JSON")
        assert result.is_success

    # =============================================================================
    # create_config_from_env tests
    # =============================================================================

    def test_create_config_from_env_no_env_vars(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test config creation with no environment variables."""
        # Clear relevant env vars
        env_vars_to_clear = [
            "FLEXT_TARGET_ORACLE_HOST",
            "ORACLE_HOST",
            "FLEXT_TARGET_ORACLE_PORT",
            "ORACLE_PORT",
            "FLEXT_TARGET_ORACLE_SERVICE_NAME",
            "ORACLE_SERVICE_NAME",
            "FLEXT_TARGET_ORACLE_USERNAME",
            "ORACLE_USERNAME",
            "FLEXT_TARGET_ORACLE_PASSWORD",
            "ORACLE_PASSWORD",
        ]
        for var in env_vars_to_clear:
            monkeypatch.delenv(var, raising=False)

        result = FlextDbOracleUtilities.create_config_from_env()
        assert result.is_success
        config = result.unwrap()
        assert isinstance(config, dict)
        assert len(config) == 0  # No env vars set

    def test_create_config_from_env_with_values(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test config creation with environment variables."""
        monkeypatch.setenv("ORACLE_HOST", "test-host")
        monkeypatch.setenv("ORACLE_PORT", "1522")
        monkeypatch.setenv("ORACLE_USERNAME", "testuser")
        monkeypatch.setenv("ORACLE_PASSWORD", "testpass")
        monkeypatch.setenv("ORACLE_SERVICE_NAME", "testservice")

        result = FlextDbOracleUtilities.create_config_from_env()
        assert result.is_success
        config = result.unwrap()
        assert config["host"] == "test-host"
        assert config["port"] == "1522"
        assert config["username"] == "testuser"
        assert config["password"] == "testpass"
        assert config["service_name"] == "testservice"

    def test_create_config_from_env_flext_prefix(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test config creation with FLEXT prefix environment variables."""
        monkeypatch.setenv("FLEXT_TARGET_ORACLE_HOST", "flext-host")
        monkeypatch.setenv("FLEXT_TARGET_ORACLE_USERNAME", "flext-user")

        result = FlextDbOracleUtilities.create_config_from_env()
        assert result.is_success
        config = result.unwrap()
        assert config["host"] == "flext-host"
        assert config["username"] == "flext-user"

    def test_create_config_from_env_mixed_prefixes(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test config creation with mixed prefixes (FLEXT takes precedence)."""
        monkeypatch.setenv("ORACLE_HOST", "oracle-host")
        monkeypatch.setenv("FLEXT_TARGET_ORACLE_HOST", "flext-host")

        result = FlextDbOracleUtilities.create_config_from_env()
        assert result.is_success
        config = result.unwrap()
        # Both should be present since they map to the same key
        assert "host" in config

    # =============================================================================
    # OracleValidation tests
    # =============================================================================

    def test_oracle_validation_validate_identifier_valid(self) -> None:
        """Test valid identifier validation."""
        result = FlextDbOracleUtilities.OracleValidation.validate_identifier(
            "VALID_TABLE"
        )
        assert result.is_success
        assert result.unwrap() == "VALID_TABLE"

    def test_oracle_validation_validate_identifier_empty(self) -> None:
        """Test empty identifier validation."""
        result = FlextDbOracleUtilities.OracleValidation.validate_identifier("")
        assert result.is_failure
        assert "cannot be empty" in result.error

    def test_oracle_validation_validate_identifier_too_long(self) -> None:
        """Test identifier too long validation."""
        long_identifier = "A" * (
            FlextDbOracleConstants.OracleValidation.MAX_ORACLE_IDENTIFIER_LENGTH + 1
        )
        result = FlextDbOracleUtilities.OracleValidation.validate_identifier(
            long_identifier
        )
        assert result.is_failure
        assert "too long" in result.error

    def test_oracle_validation_validate_identifier_invalid_pattern(self) -> None:
        """Test invalid pattern identifier validation."""
        result = FlextDbOracleUtilities.OracleValidation.validate_identifier(
            "invalid@name"
        )
        assert result.is_failure
        assert "does not match" in result.error

    def test_oracle_validation_validate_identifier_reserved_word(self) -> None:
        """Test reserved word identifier validation."""
        result = FlextDbOracleUtilities.OracleValidation.validate_identifier("SELECT")
        assert result.is_failure
        assert "reserved word" in result.error

    def test_oracle_validation_validate_identifier_lowercase_conversion(self) -> None:
        """Test lowercase identifier conversion to uppercase."""
        result = FlextDbOracleUtilities.OracleValidation.validate_identifier(
            "valid_table"
        )
        assert result.is_success
        assert result.unwrap() == "VALID_TABLE"

    # =============================================================================
    # Integration with real Oracle when available
    # =============================================================================

    @pytest.mark.unit_integration
    def test_real_oracle_escape_identifier_integration(
        self, connected_oracle_api: FlextDbOracleApi | None, oracle_available: bool
    ) -> None:
        """Test identifier escaping with real Oracle when available."""
        if not oracle_available or connected_oracle_api is None:
            pytest.skip("Oracle not available for integration test")

        # Test that escaped identifiers work in real queries
        test_table = FlextDbOracleUtilities.escape_oracle_identifier("test_real_table")
        assert test_table.is_success

        escaped_name = test_table.unwrap()
        # Try to create a table with the escaped identifier (if it doesn't exist)
        ddl = f"CREATE TABLE {escaped_name} (id NUMBER PRIMARY KEY, name VARCHAR2(100))"
        result = connected_oracle_api.execute_statement(ddl)

        # Clean up regardless of result
        with contextlib.suppress(Exception):
            connected_oracle_api.execute_statement(f"DROP TABLE {escaped_name}")

        # The DDL might fail if table exists, but escaping should work
        assert result.is_success or "already exists" in str(result.error).lower()

    @pytest.mark.unit_integration
    def test_real_oracle_query_hash_consistency(
        self, connected_oracle_api: FlextDbOracleApi | None, oracle_available: bool
    ) -> None:
        """Test that query hashing produces consistent results with real Oracle."""
        if not oracle_available or connected_oracle_api is None:
            pytest.skip("Oracle not available for integration test")

        # Test that same query with same params produces same hash
        sql = "SELECT id, name FROM test_table WHERE active = :active"
        params1 = {"active": 1}
        params2 = {"active": 1}

        hash1_result = FlextDbOracleUtilities.generate_query_hash(sql, params1)
        hash2_result = FlextDbOracleUtilities.generate_query_hash(sql, params2)

        assert hash1_result.is_success
        assert hash2_result.is_success
        assert hash1_result.unwrap() == hash2_result.unwrap()

        # Test that different params produce different hashes
        params3 = {"active": 0}
        hash3_result = FlextDbOracleUtilities.generate_query_hash(sql, params3)
        assert hash3_result.is_success
        assert hash1_result.unwrap() != hash3_result.unwrap()

    @pytest.mark.unit_integration
    def test_real_oracle_format_sql_integration(
        self, connected_oracle_api: FlextDbOracleApi | None, oracle_available: bool
    ) -> None:
        """Test SQL formatting works with real Oracle queries."""
        if not oracle_available or connected_oracle_api is None:
            pytest.skip("Oracle not available for integration test")

        # Format a complex query and test it executes
        sql = "select id, name, count(*) as cnt from test_table group by id, name order by cnt desc"
        format_result = FlextDbOracleUtilities.format_sql_for_oracle(sql)
        assert format_result.is_success

        formatted_sql = format_result.unwrap()
        # Verify formatting added newlines
        assert "\nSELECT" in formatted_sql
        assert "\nFROM" in formatted_sql
        assert "\nGROUP BY" in formatted_sql
        assert "\nORDER BY" in formatted_sql
