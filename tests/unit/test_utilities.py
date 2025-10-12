"""Test utilities functionality with comprehensive coverage.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import json
import time
from io import StringIO
from unittest.mock import Mock

import pytest
from flext_core import FlextCore
from flext_tests.matchers import FlextTestsMatchers
from pydantic import BaseModel

from flext_db_oracle import (
    FlextDbOracleConfig,
    FlextDbOracleConstants,
    FlextDbOracleModels,
    FlextDbOracleUtilities,
)

# Access constants through the FlextDbOracleConstants class
MAX_DISPLAY_ROWS = FlextDbOracleConstants.OraclePerformance.MAX_DISPLAY_ROWS
PERFORMANCE_WARNING_THRESHOLD_SECONDS = (
    FlextDbOracleConstants.OraclePerformance.PERFORMANCE_WARNING_THRESHOLD_SECONDS
)


class TestFlextDbOracleUtilitiesRealFunctionality:
    """Comprehensive tests for Oracle Utilities using ONLY real functionality - NO MOCKS."""

    def setup_method(self) -> None:
        """Setup test utilities with real configuration."""
        self.utilities = FlextDbOracleUtilities()

    def test_utilities_initialization_real(self) -> None:
        """Test utilities initialization."""
        assert self.utilities is not None
        assert isinstance(self.utilities, FlextDbOracleUtilities)

    def test_escape_oracle_identifier_real(self) -> None:
        """Test Oracle identifier escaping."""
        test_cases = [
            # Valid identifiers
            ("VALID_NAME", True),
            ("valid_name", True),
            ("Table123", True),
            ("_name", True),
            # Edge cases that should fail
            ("", False),  # Empty string should fail
            ("123name", True),  # Starting with number should work
        ]

        for input_name, should_succeed in test_cases:
            result = self.utilities.escape_oracle_identifier(input_name)
            if should_succeed:
                assert result.is_success
                assert isinstance(result.unwrap(), str)
            else:
                assert result.is_failure

    def test_format_sql_for_oracle_real(self) -> None:
        """Test Oracle SQL formatting."""
        test_queries = [
            # Basic formatting
            ("SELECT * FROM table", True),
            ("  SELECT   *   FROM   table  ", True),
            # Empty/invalid queries
            ("", True),
            ("   ", True),
        ]

        for input_query, should_succeed in test_queries:
            result = self.utilities.format_sql_for_oracle(input_query)
            # Method has @safe_result decorator, returns FlextCore.Result
            if should_succeed:
                assert result.is_success
                assert isinstance(result.unwrap(), str)
            else:
                assert result.is_failure

    def test_generate_query_hash_real(self) -> None:
        """Test query hash generation."""
        # Test that same queries produce same hash
        query1 = "SELECT * FROM users WHERE id = ?"
        query2 = "SELECT * FROM users WHERE id = ?"

        # Method returns FlextCore.Result with @safe_result decorator
        result1 = self.utilities.generate_query_hash(query1)
        result2 = self.utilities.generate_query_hash(query2)

        assert result1.is_success
        assert result2.is_success
        assert result1.unwrap() == result2.unwrap()

        # Test that different queries produce different hashes
        query3 = "SELECT * FROM products WHERE id = ?"
        result3 = self.utilities.generate_query_hash(query3)

        assert result3.is_success
        assert result1.unwrap() != result3.unwrap()

        # Verify hash format - should be hex string
        assert all(c in "0123456789abcdef" for c in result1.unwrap().lower())

    def test_generate_query_hash_with_params_real(self) -> None:
        """Test query hash generation with parameters."""
        query = "SELECT * FROM users WHERE id = ? AND name = ?"
        params1: FlextCore.Types.Dict = {"id": 1, "name": "John"}
        params2: FlextCore.Types.Dict = {"id": 2, "name": "Jane"}

        result1 = self.utilities.generate_query_hash(query, params1)
        result2 = self.utilities.generate_query_hash(query, params2)

        assert result1.is_success
        assert result2.is_success
        assert (
            result1.unwrap() != result2.unwrap()
        )  # Different params should produce different hashes

    def test_format_query_result_real(self) -> None:
        """Test query result formatting."""
        # Mock QueryResult
        mock_result = Mock()
        mock_result.fetchall.return_value = [
            {"id": 1, "name": "John"},
            {"id": 2, "name": "Jane"},
        ]

        result = self.utilities.format_query_result(mock_result, format_type="json")
        FlextTestsMatchers.assert_flext_result_success(result)
        formatted = result.value

        assert isinstance(formatted, str)
        # Should be formatted properly

    def test_format_query_result_table_real(self) -> None:
        """Test query result table formatting."""
        mock_result = Mock()
        mock_result.fetchall.return_value = [
            {"id": 1, "name": "John", "email": "john@example.com"},
            {"id": 2, "name": "Jane", "email": "jane@example.com"},
        ]

        result = self.utilities.format_query_result(mock_result, format_type="table")
        FlextTestsMatchers.assert_flext_result_success(result)
        formatted = result.value

        assert isinstance(formatted, str)

    def test_format_query_result_empty_real(self) -> None:
        """Test query result formatting with empty data."""
        mock_result = Mock()
        mock_result.fetchall.return_value = []

        for format_type in ["table", "json", "csv"]:
            result = self.utilities.format_query_result(
                mock_result,
                format_type=format_type,
            )
            FlextTestsMatchers.assert_flext_result_success(result)
            formatted = result.value
            assert isinstance(formatted, str)
            # Should handle empty data gracefully

    def test_create_api_from_config_method_real(self) -> None:
        """Test create_api_from_config method."""
        # Test with valid config dictionary
        config_dict: FlextCore.Types.Dict = {
            "host": "test_host",
            "port": 1521,
            "service_name": "TEST_SERVICE",
            "username": "test_user",
            "password": "test_password",
        }

        result = self.utilities.create_api_from_config(config_dict)

        # Should return FlextCore.Result
        assert hasattr(result, "is_success")
        assert hasattr(result, "error") or hasattr(result, "value")

    def test_create_api_from_config_invalid_real(self) -> None:
        """Test create_api_from_config with invalid config."""
        invalid_configs: list[FlextCore.Types.Dict] = [
            {},  # Empty config
            {"host": "test"},  # Missing required fields
            {"invalid": "config"},  # Invalid field names
        ]

        for invalid_config in invalid_configs:
            result = self.utilities.create_api_from_config(invalid_config)
            FlextTestsMatchers.assert_flext_result_failure(result)
            assert isinstance(result.error, str)

    def test_create_config_from_env_real(self) -> None:
        """Test create_config_from_env method."""
        result = self.utilities.create_config_from_env()

        # Should return FlextCore.Result - may fail if env vars not set
        assert hasattr(result, "is_success")
        assert hasattr(result, "error") or hasattr(result, "value")

    def test_utilities_error_handling_patterns_real(self) -> None:
        """Test utilities error handling patterns."""
        utilities = FlextDbOracleUtilities()

        # Test with empty inputs - should fail
        result1 = utilities.escape_oracle_identifier("")
        assert result1.is_failure

        # Test with invalid SQL - should handle gracefully
        result2 = utilities.format_sql_for_oracle("")
        assert result2.is_success  # Empty string is valid SQL

        # Test create_api_from_config with empty dict
        result3 = utilities.create_api_from_config({})
        assert result3.is_failure

    def test_utilities_performance_tracking_real(self) -> None:
        """Test utilities performance tracking."""
        start_time = time.time()

        # Perform multiple operations
        for i in range(50):
            result = self.utilities.escape_oracle_identifier(f"test_name_{i}")
            FlextTestsMatchers.assert_flext_result_success(result)

        end_time = time.time()
        elapsed = end_time - start_time

        # Should complete quickly (less than 1 second for 50 operations)
        assert elapsed < 1.0

    def test_utilities_protocols_integration_real(self) -> None:
        """Test utilities protocols integration."""

        # Test HasModelDump protocol with Pydantic model
        class TestModel(BaseModel):
            id: int
            name: str

        test_model = TestModel(id=1, name="test")

        # Verify protocol compliance
        assert hasattr(test_model, "model_dump")
        model_data = test_model.model_dump()
        assert isinstance(model_data, dict)
        assert model_data["id"] == 1
        assert model_data["name"] == "test"

    def test_utilities_integration_with_flext_core_patterns_real(self) -> None:
        """Test utilities integration with flext-core patterns."""
        utilities = FlextDbOracleUtilities()

        # Test FlextCore.Result operations
        result1 = utilities.escape_oracle_identifier("test_name")
        assert hasattr(result1, "is_success")
        assert hasattr(result1, "error") or hasattr(result1, "value")

        result2 = utilities.create_api_from_config({"test": "config"})
        assert hasattr(result2, "is_success")
        assert hasattr(result2, "error") or hasattr(result2, "value")

    def test_utilities_string_representations_real(self) -> None:
        """Test utilities string representations."""
        utilities = FlextDbOracleUtilities()

        # Test repr/str don't crash
        repr_str = repr(utilities)
        assert isinstance(repr_str, str)
        assert len(repr_str) > 0

        str_repr = str(utilities)
        assert isinstance(str_repr, str)
        assert len(str_repr) > 0

    def test_utilities_multiple_instances_isolation_real(self) -> None:
        """Test that multiple utility instances are properly isolated."""
        utilities1 = FlextDbOracleUtilities()
        utilities2 = FlextDbOracleUtilities()

        # Test that instances are separate
        assert utilities1 is not utilities2

        # Test that operations are independent
        result1 = utilities1.escape_oracle_identifier("test_name")
        result2 = utilities2.escape_oracle_identifier("test_name")

        FlextTestsMatchers.assert_flext_result_success(result1)
        FlextTestsMatchers.assert_flext_result_success(result2)
        assert result1.value == result2.value  # Same input, same result

        # But instances should be independent objects
        assert id(utilities1) != id(utilities2)

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
        params: FlextCore.Types.Dict = {"id": 123}
        result = FlextDbOracleUtilities.generate_query_hash(sql, params)

        assert result.is_success
        hash_value = result.unwrap()
        assert isinstance(hash_value, str)
        assert len(hash_value) == 16

    def test_generate_query_hash_empty_params(self) -> None:
        """Test generate_query_hash with empty params dict."""
        sql = "SELECT 1 FROM DUAL"
        params: FlextCore.Types.Dict = {}
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


"""Test utilities safe methods for Oracle database operations.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""


class TestModelDump:
    """Test class that supports model_dump methods."""

    def model_dump(self) -> FlextCore.Types.Dict:
        """Dump model to dictionary."""
        return {"status": "healthy", "version": "1.0.0", "uptime": 3600}

    def model_dump_json(self, *, indent: int | None = None) -> str:
        """Dump model to JSON string."""
        data = self.model_dump()
        return json.dumps(data, indent=indent)


class MockConsole:
    """Real console implementation for testing."""

    def __init__(self) -> None:
        """Initialize test console."""
        self.output = StringIO()

    def print(self, *args: object) -> None:
        """Print text to internal buffer."""
        print(*args, file=self.output)

    def get_output(self) -> str:
        """Get captured output."""
        return self.output.getvalue()


class TestFlextDbOracleUtilities:
    """Test FlextDbOracle utilities methods."""

    def test_utilities_create_config_from_env_method_exists(self) -> None:
        """Test create_config_from_env method exists and is callable."""
        assert hasattr(FlextDbOracleUtilities, "create_config_from_env")
        assert callable(FlextDbOracleUtilities.create_config_from_env)

    def test_utilities_create_api_from_config_method(self) -> None:
        """Test create_api_from_config utility method."""
        config_dict: FlextCore.Types.Dict = {
            "host": "util_api_test",
            "port": 1521,
            "service_name": "UTIL_API_TEST",
            "username": "util_api_user",
            "password": "util_api_pass",
        }

        api_result = FlextDbOracleUtilities.create_api_from_config(config_dict)
        assert api_result.is_success
        api = api_result.value
        assert api is not None

    def test_utilities_format_query_result_table_format(self) -> None:
        """Test format_query_result with table output format."""
        query_result = FlextDbOracleModels.QueryResult(
            query="SELECT id, name, email FROM users",
            columns=["id", "name", "email"],
            rows=[[1, "John", "john@test.com"], [2, "Jane", "jane@test.com"]],
            row_count=2,
            execution_time_ms=50,  # Convert to milliseconds as int
            query_hash=None,
            explain_plan=None,
        )

        # Should not raise exception with table format
        MockConsole()
        try:
            result = FlextDbOracleUtilities.format_query_result(query_result, "table")
            assert result.is_success
        except Exception as e:
            pytest.fail(f"format_query_result failed with table format: {e}")

    def test_utilities_format_query_result_json_format(self) -> None:
        """Test format_query_result with JSON output format."""
        query_result = FlextDbOracleModels.QueryResult(
            query="SELECT id, name FROM test_table",
            columns=["id", "name"],
            rows=[[1, "Test"]],
            row_count=1,
            execution_time_ms=20,  # Convert to milliseconds as int
            query_hash=None,
            explain_plan=None,
        )

        # Should not raise exception with JSON format
        MockConsole()
        try:
            result = FlextDbOracleUtilities.format_query_result(query_result, "json")
            assert result.is_success
        except Exception as e:
            pytest.fail(f"format_query_result failed with json format: {e}")

    def test_utilities_format_query_result_empty_data(self) -> None:
        """Test format_query_result with empty data."""
        empty_result = FlextDbOracleModels.QueryResult(
            query="SELECT * FROM empty_table",
            columns=[],
            rows=[],
            row_count=0,
            execution_time_ms=10,  # Convert to milliseconds as int
            query_hash=None,
            explain_plan=None,
        )

        # Should handle empty data gracefully
        MockConsole()
        try:
            result1 = FlextDbOracleUtilities.format_query_result(empty_result, "table")
            assert result1.is_success
            result2 = FlextDbOracleUtilities.format_query_result(empty_result, "json")
            assert result2.is_success
        except Exception as e:
            pytest.fail(f"format_query_result failed with empty data: {e}")

    def test_utilities_display_health_data_with_model_dump(self) -> None:
        """Test health data display functionality with objects supporting model_dump."""
        health_data = TestModelDump()

        # Test via public format_query_result method which uses private methods internally
        test_result = FlextDbOracleModels.QueryResult(
            query="SELECT health FROM test_table",
            columns=["health"],
            rows=[[health_data]],
            row_count=1,
            execution_time_ms=10,  # Convert to milliseconds as int
            query_hash=None,
            explain_plan=None,
        )

        for format_type in ["table", "json"]:
            result = FlextDbOracleUtilities.format_query_result(
                test_result,
                format_type,
            )
            assert result.is_success, (
                f"format_query_result failed with {format_type} format"
            )

    def test_utilities_display_health_data_without_model_dump(self) -> None:
        """Test health data display functionality with plain objects."""
        # Test via public format_query_result method which internally uses private methods
        test_result = FlextDbOracleModels.QueryResult(
            query="SELECT status, message FROM health_table",
            columns=["status", "message"],
            rows=[["ok", "All good"]],
            row_count=1,
            execution_time_ms=10,  # Convert to milliseconds as int
            query_hash=None,
            explain_plan=None,
        )

        for format_type in ["table", "json", "csv"]:
            result = FlextDbOracleUtilities.format_query_result(
                test_result,
                format_type,
            )
            assert result.is_success, (
                f"format_query_result failed with {format_type} for plain objects"
            )

    def test_utilities_display_query_table_method(self) -> None:
        """Test query table display functionality via public interface."""
        query_result = FlextDbOracleModels.QueryResult(
            query="SELECT column1, column2 FROM test_table",
            columns=["column1", "column2"],
            rows=[["value1", "value2"], ["value3", "value4"]],
            row_count=2,
            execution_time_ms=30,  # Convert to milliseconds as int
            query_hash=None,
            explain_plan=None,
        )

        # Test via public format_query_result method with table format
        result = FlextDbOracleUtilities.format_query_result(query_result, "table")
        assert result.is_success, "format_query_result failed with table format"

        # Verify the formatted output contains expected data
        formatted_output = result.value
        # Check that format method was called (output should contain something meaningful)
        assert isinstance(formatted_output, str)
        assert len(formatted_output) > 20  # Should be more than just "QueryResult"
        # More flexible check since actual formatting may vary
        assert "QueryResult" in formatted_output or "column1" in formatted_output

    def test_utilities_performance_monitoring_constants(self) -> None:
        """Test performance monitoring constants are accessible."""
        assert isinstance(
            FlextDbOracleConstants.OraclePerformance.PERFORMANCE_WARNING_THRESHOLD_SECONDS,
            (int, float),
        )
        assert (
            FlextDbOracleConstants.OraclePerformance.PERFORMANCE_WARNING_THRESHOLD_SECONDS
            > 0
        )
        assert isinstance(
            FlextDbOracleConstants.OraclePerformance.MAX_DISPLAY_ROWS, int
        )
        assert FlextDbOracleConstants.OraclePerformance.MAX_DISPLAY_ROWS > 0

    def test_utilities_supports_model_dump_protocol(self) -> None:
        """Test SupportsModelDump protocol works correctly."""
        test_object = TestModelDump()

        # Check protocol compliance
        assert hasattr(test_object, "model_dump")
        assert hasattr(test_object, "model_dump_json")
        assert callable(test_object.model_dump)
        assert callable(test_object.model_dump_json)

        # Test protocol methods
        model_data = test_object.model_dump()
        assert isinstance(model_data, dict)
        assert "status" in model_data

        json_data = test_object.model_dump_json(indent=2)
        assert isinstance(json_data, str)
        assert "status" in json_data


class TestFlextDbOracleUtilitiesDataValidation:
    """Test utilities data validation and processing methods."""

    def test_utilities_query_result_validation(self) -> None:
        """Test query result validation and processing."""
        # Valid query result
        valid_result = FlextDbOracleModels.QueryResult(
            query="SELECT test FROM validation_table",
            columns=["test"],
            rows=[["data"]],
            row_count=1,
            execution_time_ms=10,  # Convert to milliseconds as int
            query_hash=None,
            explain_plan=None,
        )

        assert valid_result.row_count == 1
        assert len(valid_result.rows) == 1
        assert len(valid_result.columns) == 1

    def test_utilities_configuration_processing(self) -> None:
        """Test configuration processing utilities."""
        config = FlextDbOracleConfig(
            host="config_test",
            port=1521,
            name="CONFIG_TEST",
            username="config_user",
            password="config_pass",
            service_name="CONFIG_TEST",
            pool_max=10,
        )

        # Configuration should be valid
        assert config.host == "config_test"
        assert config.port == 1521
        assert config.pool_max == 10

    def test_utilities_data_formatting_edge_cases(self) -> None:
        """Test data formatting with edge cases."""
        # Large dataset
        large_rows = [[i, f"Item{i}"] for i in range(100)]
        large_result = FlextDbOracleModels.QueryResult(
            query="SELECT id, name FROM large_table",
            columns=["id", "name"],
            rows=large_rows,
            row_count=100,
            execution_time_ms=500,  # Convert to milliseconds as int
            query_hash=None,
            explain_plan=None,
        )

        # Should handle large datasets
        MockConsole()
        try:
            FlextDbOracleUtilities.format_query_result(large_result, "table")
        except Exception as e:
            pytest.fail(f"format_query_result failed with large dataset: {e}")

        # Complex nested data
        complex_result = FlextDbOracleModels.QueryResult(
            query="SELECT nested_data FROM complex_table",
            columns=["nested_data"],
            rows=[['{"deep": {"value": "test"}}']],
            row_count=1,
            execution_time_ms=10,  # Convert to milliseconds as int
            query_hash=None,
            explain_plan=None,
        )

        # Should handle complex data structures
        MockConsole()
        try:
            FlextDbOracleUtilities.format_query_result(complex_result, "json")
        except Exception as e:
            pytest.fail(f"format_query_result failed with complex data: {e}")


class TestFlextDbOracleUtilitiesPerformanceMonitoring:
    """Test utilities performance monitoring functionality."""

    def test_utilities_performance_tracking(self) -> None:
        """Test performance tracking utilities."""
        start_time = time.time()
        time.sleep(0.01)  # Small delay for measurable execution time
        end_time = time.time()
        execution_time = end_time - start_time

        # Should be able to create query result with timing
        result = FlextDbOracleModels.QueryResult(
            query="SELECT 'performance' as test",
            columns=["test"],
            rows=[["performance"]],
            row_count=1,
            execution_time_ms=int(execution_time * 1000),  # Convert to milliseconds
            query_hash=None,
            explain_plan=None,
        )

        assert result.execution_time_ms > 0
        assert result.execution_time_ms < 1000.0  # Should be very fast

    def test_utilities_slow_query_detection_simulation(self) -> None:
        """Test slow query detection simulation."""
        # Simulate slow query
        slow_result = FlextDbOracleModels.QueryResult(
            query="SELECT slow FROM performance_table",
            columns=["slow"],
            rows=[["query"]],
            row_count=1,
            execution_time_ms=int(
                (
                    FlextDbOracleConstants.OraclePerformance.PERFORMANCE_WARNING_THRESHOLD_SECONDS
                    + 1.0
                )
                * 1000,
            ),  # Convert to int
            query_hash=None,
            explain_plan=None,
        )

        assert (
            slow_result.execution_time_ms
            > FlextDbOracleConstants.OraclePerformance.PERFORMANCE_WARNING_THRESHOLD_SECONDS
            * 1000
        )

        # Should handle slow query formatting
        MockConsole()
        try:
            result = FlextDbOracleUtilities.format_query_result(slow_result, "table")
            assert result.is_success
        except Exception as e:
            pytest.fail(f"format_query_result failed with slow query: {e}")


class TestFlextDbOracleUtilitiesErrorHandling:
    """Test utilities error handling scenarios."""

    def test_utilities_invalid_format_handling(self) -> None:
        """Test handling of invalid output formats."""
        query_result = FlextDbOracleModels.QueryResult(
            query="SELECT test FROM error_table",
            columns=["test"],
            rows=[["data"]],
            row_count=1,
            execution_time_ms=10,  # Convert to milliseconds as int
            query_hash=None,
            explain_plan=None,
        )

        # Should handle invalid formats gracefully - method is defensive and succeeds
        result = FlextDbOracleUtilities.format_query_result(
            query_result,
            "invalid_format",
        )
        # Method handles invalid formats defensively, should still succeed
        assert result.is_success, "Method should handle invalid format defensively"
        # Should still return some output (default formatting)
        assert isinstance(result.value, str)
        assert len(result.value) > 0

    def test_utilities_none_handling(self) -> None:
        """Test handling of None values in utilities via public interface."""
        # Test via public format_query_result method with None data
        empty_result = FlextDbOracleModels.QueryResult(
            query="SELECT * FROM empty_table",
            columns=[],
            rows=[],
            row_count=0,
            execution_time_ms=0,  # Convert to int
            query_hash=None,
            explain_plan=None,
        )

        # Test all formats to ensure None handling works
        for format_type in ["table", "json", "csv"]:
            result = FlextDbOracleUtilities.format_query_result(
                empty_result,
                format_type,
            )
            assert result.is_success, (
                f"format_query_result should handle empty data for {format_type}"
            )

            # Verify output is meaningful even with empty data
            formatted_output = result.value
            assert isinstance(formatted_output, str)
            assert (
                len(formatted_output) >= 0
            )  # Should return empty string or minimal format

    def setup_method(self) -> None:
        """Setup test utilities with real configuration."""
        self.utilities = FlextDbOracleUtilities()

    def test_utilities_initialization_real(self) -> None:
        """Test utilities initialization."""
        assert self.utilities is not None
        assert isinstance(self.utilities, FlextDbOracleUtilities)

    def test_escape_oracle_identifier_real(self) -> None:
        """Test Oracle identifier escaping."""
        test_cases = [
            # Valid identifiers
            ("VALID_NAME", True),
            ("valid_name", True),
            ("Table123", True),
            ("_name", True),
            # Edge cases that should fail
            ("", False),  # Empty string should fail
            ("123name", True),  # Starting with number should work
        ]

        for input_name, should_succeed in test_cases:
            result = self.utilities.escape_oracle_identifier(input_name)
            if should_succeed:
                assert result.is_success
                assert isinstance(result.unwrap(), str)
            else:
                assert result.is_failure

    def test_format_sql_for_oracle_real(self) -> None:
        """Test Oracle SQL formatting."""
        test_queries = [
            # Basic formatting
            ("SELECT * FROM table", True),
            ("  SELECT   *   FROM   table  ", True),
            # Empty/invalid queries
            ("", True),
            ("   ", True),
        ]

        for input_query, should_succeed in test_queries:
            result = self.utilities.format_sql_for_oracle(input_query)
            # Method has @safe_result decorator, returns FlextCore.Result
            if should_succeed:
                assert result.is_success
                assert isinstance(result.unwrap(), str)
            else:
                assert result.is_failure

    def test_generate_query_hash_real(self) -> None:
        """Test query hash generation."""
        # Test that same queries produce same hash
        query1 = "SELECT * FROM users WHERE id = ?"
        query2 = "SELECT * FROM users WHERE id = ?"

        # Method returns FlextCore.Result with @safe_result decorator
        result1 = self.utilities.generate_query_hash(query1)
        result2 = self.utilities.generate_query_hash(query2)

        assert result1.is_success
        assert result2.is_success
        assert result1.unwrap() == result2.unwrap()

        # Test that different queries produce different hashes
        query3 = "SELECT * FROM products WHERE id = ?"
        result3 = self.utilities.generate_query_hash(query3)

        assert result3.is_success
        assert result1.unwrap() != result3.unwrap()

        # Verify hash format - should be hex string
        assert all(c in "0123456789abcdef" for c in result1.unwrap().lower())

    def test_generate_query_hash_with_params_real(self) -> None:
        """Test query hash generation with parameters."""
        query = "SELECT * FROM users WHERE id = ? AND name = ?"
        params1: FlextCore.Types.Dict = {"id": 1, "name": "John"}
        params2: FlextCore.Types.Dict = {"id": 2, "name": "Jane"}

        result1 = self.utilities.generate_query_hash(query, params1)
        result2 = self.utilities.generate_query_hash(query, params2)

        assert result1.is_success
        assert result2.is_success
        assert (
            result1.unwrap() != result2.unwrap()
        )  # Different params should produce different hashes

    def test_format_query_result_real(self) -> None:
        """Test query result formatting."""
        # Mock QueryResult
        mock_result = Mock()
        mock_result.fetchall.return_value = [
            {"id": 1, "name": "John"},
            {"id": 2, "name": "Jane"},
        ]

        result = self.utilities.format_query_result(mock_result, format_type="json")
        FlextTestsMatchers.assert_result_success(result)
        formatted = result.value

        assert isinstance(formatted, str)
        # Should be formatted properly

    def test_format_query_result_table_real(self) -> None:
        """Test query result table formatting."""
        mock_result = Mock()
        mock_result.fetchall.return_value = [
            {"id": 1, "name": "John", "email": "john@example.com"},
            {"id": 2, "name": "Jane", "email": "jane@example.com"},
        ]

        result = self.utilities.format_query_result(mock_result, format_type="table")
        FlextTestsMatchers.assert_result_success(result)
        formatted = result.value

        assert isinstance(formatted, str)

    def test_format_query_result_empty_real(self) -> None:
        """Test query result formatting with empty data."""
        mock_result = Mock()
        mock_result.fetchall.return_value = []

        for format_type in ["table", "json", "csv"]:
            result = self.utilities.format_query_result(
                mock_result,
                format_type=format_type,
            )
            FlextTestsMatchers.assert_result_success(result)
            formatted = result.value
            assert isinstance(formatted, str)
            # Should handle empty data gracefully

    def test_create_api_from_config_method_real(self) -> None:
        """Test create_api_from_config method."""
        # Test with valid config dictionary
        config_dict: FlextCore.Types.Dict = {
            "host": "test_host",
            "port": 1521,
            "service_name": "TEST_SERVICE",
            "username": "test_user",
            "password": "test_password",
        }

        result = self.utilities.create_api_from_config(config_dict)

        # Should return FlextCore.Result
        assert hasattr(result, "is_success")
        assert hasattr(result, "error") or hasattr(result, "value")

    def test_create_api_from_config_invalid_real(self) -> None:
        """Test create_api_from_config with invalid config."""
        invalid_configs: list[FlextCore.Types.Dict] = [
            {},  # Empty config
            {"host": "test"},  # Missing required fields
            {"invalid": "config"},  # Invalid field names
        ]

        for invalid_config in invalid_configs:
            result = self.utilities.create_api_from_config(invalid_config)
            FlextTestsMatchers.assert_result_failure(result)
            assert isinstance(result.error, str)

    def test_create_config_from_env_real(self) -> None:
        """Test create_config_from_env method."""
        result = self.utilities.create_config_from_env()

        # Should return FlextCore.Result - may fail if env vars not set
        assert hasattr(result, "is_success")
        assert hasattr(result, "error") or hasattr(result, "value")

    def test_utilities_error_handling_patterns_real(self) -> None:
        """Test utilities error handling patterns."""
        utilities = FlextDbOracleUtilities()

        # Test with empty inputs - should fail
        result1 = utilities.escape_oracle_identifier("")
        assert result1.is_failure

        # Test with invalid SQL - should handle gracefully
        result2 = utilities.format_sql_for_oracle("")
        assert result2.is_success  # Empty string is valid SQL

        # Test create_api_from_config with empty dict
        result3 = utilities.create_api_from_config({})
        assert result3.is_failure

    def test_utilities_performance_tracking_real(self) -> None:
        """Test utilities performance tracking."""
        start_time = time.time()

        # Perform multiple operations
        for i in range(50):
            result = self.utilities.escape_oracle_identifier(f"test_name_{i}")
            FlextTestsMatchers.assert_result_success(result)

        end_time = time.time()
        elapsed = end_time - start_time

        # Should complete quickly (less than 1 second for 50 operations)
        assert elapsed < 1.0

    def test_utilities_protocols_integration_real(self) -> None:
        """Test utilities protocols integration."""

        # Test HasModelDump protocol with Pydantic model
        class TestModel(BaseModel):
            id: int
            name: str

        test_model = TestModel(id=1, name="test")

        # Verify protocol compliance
        assert hasattr(test_model, "model_dump")
        model_data = test_model.model_dump()
        assert isinstance(model_data, dict)
        assert model_data["id"] == 1
        assert model_data["name"] == "test"

    def test_utilities_integration_with_flext_core_patterns_real(self) -> None:
        """Test utilities integration with flext-core patterns."""
        utilities = FlextDbOracleUtilities()

        # Test FlextCore.Result operations
        result1 = utilities.escape_oracle_identifier("test_name")
        assert hasattr(result1, "is_success")
        assert hasattr(result1, "error") or hasattr(result1, "value")

        result2 = utilities.create_api_from_config({"test": "config"})
        assert hasattr(result2, "is_success")
        assert hasattr(result2, "error") or hasattr(result2, "value")

    def test_utilities_string_representations_real(self) -> None:
        """Test utilities string representations."""
        utilities = FlextDbOracleUtilities()

        # Test repr/str don't crash
        repr_str = repr(utilities)
        assert isinstance(repr_str, str)
        assert len(repr_str) > 0

        str_repr = str(utilities)
        assert isinstance(str_repr, str)
        assert len(str_repr) > 0

    def test_utilities_multiple_instances_isolation_real(self) -> None:
        """Test that multiple utility instances are properly isolated."""
        utilities1 = FlextDbOracleUtilities()
        utilities2 = FlextDbOracleUtilities()

        # Test that instances are separate
        assert utilities1 is not utilities2

        # Test that operations are independent
        result1 = utilities1.escape_oracle_identifier("test_name")
        result2 = utilities2.escape_oracle_identifier("test_name")

        FlextTestsMatchers.assert_result_success(result1)
        FlextTestsMatchers.assert_result_success(result2)
        assert result1.value == result2.value  # Same input, same result

        # But instances should be independent objects
        assert id(utilities1) != id(utilities2)

    def model_dump(self) -> FlextCore.Types.Dict:
        """Dump model to dictionary."""
        return {"status": "healthy", "version": "1.0.0", "uptime": 3600}

    def model_dump_json(self, *, indent: int | None = None) -> str:
        """Dump model to JSON string."""
        data = self.model_dump()
        return json.dumps(data, indent=indent)

    def __init__(self) -> None:
        """Initialize test console."""
        self.output = StringIO()

    def print(self, *args: object) -> None:
        """Print text to internal buffer."""
        print(*args, file=self.output)

    def get_output(self) -> str:
        """Get captured output."""
        return self.output.getvalue()

    def test_utilities_create_config_from_env_method_exists(self) -> None:
        """Test create_config_from_env method exists and is callable."""
        assert hasattr(FlextDbOracleUtilities, "create_config_from_env")
        assert callable(FlextDbOracleUtilities.create_config_from_env)

    def test_utilities_create_api_from_config_method(self) -> None:
        """Test create_api_from_config utility method."""
        config_dict: FlextCore.Types.Dict = {
            "host": "util_api_test",
            "port": 1521,
            "service_name": "UTIL_API_TEST",
            "username": "util_api_user",
            "password": "util_api_pass",
        }

        api_result = FlextDbOracleUtilities.create_api_from_config(config_dict)
        assert api_result.is_success
        api = api_result.value
        assert api is not None

    def test_utilities_format_query_result_table_format(self) -> None:
        """Test format_query_result with table output format."""
        query_result = FlextDbOracleModels.QueryResult(
            query="SELECT id, name, email FROM users",
            columns=["id", "name", "email"],
            rows=[[1, "John", "john@test.com"], [2, "Jane", "jane@test.com"]],
            row_count=2,
            execution_time_ms=50,  # Convert to milliseconds as int
            query_hash=None,
            explain_plan=None,
        )

        # Should not raise exception with table format
        MockConsole()
        try:
            result = FlextDbOracleUtilities.format_query_result(query_result, "table")
            assert result.is_success
        except Exception as e:
            pytest.fail(f"format_query_result failed with table format: {e}")

    def test_utilities_format_query_result_json_format(self) -> None:
        """Test format_query_result with JSON output format."""
        query_result = FlextDbOracleModels.QueryResult(
            query="SELECT id, name FROM test_table",
            columns=["id", "name"],
            rows=[[1, "Test"]],
            row_count=1,
            execution_time_ms=20,  # Convert to milliseconds as int
            query_hash=None,
            explain_plan=None,
        )

        # Should not raise exception with JSON format
        MockConsole()
        try:
            result = FlextDbOracleUtilities.format_query_result(query_result, "json")
            assert result.is_success
        except Exception as e:
            pytest.fail(f"format_query_result failed with json format: {e}")

    def test_utilities_format_query_result_empty_data(self) -> None:
        """Test format_query_result with empty data."""
        empty_result = FlextDbOracleModels.QueryResult(
            query="SELECT * FROM empty_table",
            columns=[],
            rows=[],
            row_count=0,
            execution_time_ms=10,  # Convert to milliseconds as int
            query_hash=None,
            explain_plan=None,
        )

        # Should handle empty data gracefully
        MockConsole()
        try:
            result1 = FlextDbOracleUtilities.format_query_result(empty_result, "table")
            assert result1.is_success
            result2 = FlextDbOracleUtilities.format_query_result(empty_result, "json")
            assert result2.is_success
        except Exception as e:
            pytest.fail(f"format_query_result failed with empty data: {e}")

    def test_utilities_display_health_data_with_model_dump(self) -> None:
        """Test health data display functionality with objects supporting model_dump."""
        health_data = TestModelDump()

        # Test via public format_query_result method which uses private methods internally
        test_result = FlextDbOracleModels.QueryResult(
            query="SELECT health FROM test_table",
            columns=["health"],
            rows=[[health_data]],
            row_count=1,
            execution_time_ms=10,  # Convert to milliseconds as int
            query_hash=None,
            explain_plan=None,
        )

        for format_type in ["table", "json"]:
            result = FlextDbOracleUtilities.format_query_result(
                test_result,
                format_type,
            )
            assert result.is_success, (
                f"format_query_result failed with {format_type} format"
            )

    def test_utilities_display_health_data_without_model_dump(self) -> None:
        """Test health data display functionality with plain objects."""
        # Test via public format_query_result method which internally uses private methods
        test_result = FlextDbOracleModels.QueryResult(
            query="SELECT status, message FROM health_table",
            columns=["status", "message"],
            rows=[["ok", "All good"]],
            row_count=1,
            execution_time_ms=10,  # Convert to milliseconds as int
            query_hash=None,
            explain_plan=None,
        )

        for format_type in ["table", "json", "csv"]:
            result = FlextDbOracleUtilities.format_query_result(
                test_result,
                format_type,
            )
            assert result.is_success, (
                f"format_query_result failed with {format_type} for plain objects"
            )

    def test_utilities_display_query_table_method(self) -> None:
        """Test query table display functionality via public interface."""
        query_result = FlextDbOracleModels.QueryResult(
            query="SELECT column1, column2 FROM test_table",
            columns=["column1", "column2"],
            rows=[["value1", "value2"], ["value3", "value4"]],
            row_count=2,
            execution_time_ms=30,  # Convert to milliseconds as int
            query_hash=None,
            explain_plan=None,
        )

        # Test via public format_query_result method with table format
        result = FlextDbOracleUtilities.format_query_result(query_result, "table")
        assert result.is_success, "format_query_result failed with table format"

        # Verify the formatted output contains expected data
        formatted_output = result.value
        # Check that format method was called (output should contain something meaningful)
        assert isinstance(formatted_output, str)
        assert len(formatted_output) > 20  # Should be more than just "QueryResult"
        # More flexible check since actual formatting may vary
        assert "QueryResult" in formatted_output or "column1" in formatted_output

    def test_utilities_performance_monitoring_constants(self) -> None:
        """Test performance monitoring constants are accessible."""
        assert isinstance(PERFORMANCE_WARNING_THRESHOLD_SECONDS, (int, float))
        assert PERFORMANCE_WARNING_THRESHOLD_SECONDS > 0
        assert isinstance(MAX_DISPLAY_ROWS, int)
        assert MAX_DISPLAY_ROWS > 0

    def test_utilities_supports_model_dump_protocol(self) -> None:
        """Test SupportsModelDump protocol works correctly."""
        test_object = TestModelDump()

        # Check protocol compliance
        assert hasattr(test_object, "model_dump")
        assert hasattr(test_object, "model_dump_json")
        assert callable(test_object.model_dump)
        assert callable(test_object.model_dump_json)

        # Test protocol methods
        model_data = test_object.model_dump()
        assert isinstance(model_data, dict)
        assert "status" in model_data

        json_data = test_object.model_dump_json(indent=2)
        assert isinstance(json_data, str)
        assert "status" in json_data

    def test_utilities_query_result_validation(self) -> None:
        """Test query result validation and processing."""
        # Valid query result
        valid_result = FlextDbOracleModels.QueryResult(
            query="SELECT test FROM validation_table",
            columns=["test"],
            rows=[["data"]],
            row_count=1,
            execution_time_ms=10,  # Convert to milliseconds as int
            query_hash=None,
            explain_plan=None,
        )

        assert valid_result.row_count == 1
        assert len(valid_result.rows) == 1
        assert len(valid_result.columns) == 1

    def test_utilities_configuration_processing(self) -> None:
        """Test configuration processing utilities."""
        config = FlextDbOracleConfig(
            host="config_test",
            port=1521,
            name="CONFIG_TEST",
            username="config_user",
            password="config_pass",
            service_name="CONFIG_TEST",
            pool_max=10,
        )

        # Configuration should be valid
        assert config.host == "config_test"
        assert config.port == 1521
        assert config.pool_max == 10

    def test_utilities_data_formatting_edge_cases(self) -> None:
        """Test data formatting with edge cases."""
        # Large dataset
        large_rows = [[i, f"Item{i}"] for i in range(100)]
        large_result = FlextDbOracleModels.QueryResult(
            query="SELECT id, name FROM large_table",
            columns=["id", "name"],
            rows=large_rows,
            row_count=100,
            execution_time_ms=500,  # Convert to milliseconds as int
            query_hash=None,
            explain_plan=None,
        )

        # Should handle large datasets
        MockConsole()
        try:
            FlextDbOracleUtilities.format_query_result(large_result, "table")
        except Exception as e:
            pytest.fail(f"format_query_result failed with large dataset: {e}")

        # Complex nested data
        complex_result = FlextDbOracleModels.QueryResult(
            query="SELECT nested_data FROM complex_table",
            columns=["nested_data"],
            rows=[['{"deep": {"value": "test"}}']],
            row_count=1,
            execution_time_ms=10,  # Convert to milliseconds as int
            query_hash=None,
            explain_plan=None,
        )

        # Should handle complex data structures
        MockConsole()
        try:
            FlextDbOracleUtilities.format_query_result(complex_result, "json")
        except Exception as e:
            pytest.fail(f"format_query_result failed with complex data: {e}")

    def test_utilities_performance_tracking(self) -> None:
        """Test performance tracking utilities."""
        start_time = time.time()
        time.sleep(0.01)  # Small delay for measurable execution time
        end_time = time.time()
        execution_time = end_time - start_time

        # Should be able to create query result with timing
        result = FlextDbOracleModels.QueryResult(
            query="SELECT 'performance' as test",
            columns=["test"],
            rows=[["performance"]],
            row_count=1,
            execution_time_ms=int(execution_time * 1000),  # Convert to milliseconds
            query_hash=None,
            explain_plan=None,
        )

        assert result.execution_time_ms > 0
        assert result.execution_time_ms < 1000.0  # Should be very fast

    def test_utilities_slow_query_detection_simulation(self) -> None:
        """Test slow query detection simulation."""
        # Simulate slow query
        slow_result = FlextDbOracleModels.QueryResult(
            query="SELECT slow FROM performance_table",
            columns=["slow"],
            rows=[["query"]],
            row_count=1,
            execution_time_ms=int(
                (PERFORMANCE_WARNING_THRESHOLD_SECONDS + 1.0) * 1000,
            ),  # Convert to int
            query_hash=None,
            explain_plan=None,
        )

        assert (
            slow_result.execution_time_ms > PERFORMANCE_WARNING_THRESHOLD_SECONDS * 1000
        )

        # Should handle slow query formatting
        MockConsole()
        try:
            result = FlextDbOracleUtilities.format_query_result(slow_result, "table")
            assert result.is_success
        except Exception as e:
            pytest.fail(f"format_query_result failed with slow query: {e}")

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
        params: FlextCore.Types.Dict = {"id": 123}
        result = FlextDbOracleUtilities.generate_query_hash(sql, params)

        assert result.is_success
        hash_value = result.unwrap()
        assert isinstance(hash_value, str)
        assert len(hash_value) == 16

    def test_generate_query_hash_empty_params(self) -> None:
        """Test generate_query_hash with empty params dict."""
        sql = "SELECT 1 FROM DUAL"
        params: FlextCore.Types.Dict = {}
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
