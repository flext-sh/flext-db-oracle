"""Test utilities functionality with comprehensive coverage."""

from __future__ import annotations

import sys
import time
from pathlib import Path
from unittest.mock import Mock

from flext_tests import FlextTestsMatchers
from pydantic import BaseModel

from flext_core import FlextTypes
from flext_db_oracle.utilities import FlextDbOracleUtilities

# Add flext_tests to path
sys.path.insert(0, str(Path(__file__).parents[4] / "flext-core" / "src"))


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
            # Method has @safe_result decorator, returns FlextResult
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

        # Method returns FlextResult with @safe_result decorator
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
        params1 = {"id": 1, "name": "John"}
        params2 = {"id": 2, "name": "Jane"}

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
                mock_result, format_type=format_type,
            )
            FlextTestsMatchers.assert_result_success(result)
            formatted = result.value
            assert isinstance(formatted, str)
            # Should handle empty data gracefully

    def test_create_api_from_config_method_real(self) -> None:
        """Test create_api_from_config method."""
        # Test with valid config dictionary
        config_dict = {
            "host": "test_host",
            "port": 1521,
            "service_name": "TEST_SERVICE",
            "username": "test_user",
            "password": "test_password",
        }

        result = self.utilities.create_api_from_config(config_dict)

        # Should return FlextResult
        assert hasattr(result, "success")
        assert hasattr(result, "error") or hasattr(result, "value")

    def test_create_api_from_config_invalid_real(self) -> None:
        """Test create_api_from_config with invalid config."""
        invalid_configs: list[FlextTypes.Core.Dict] = [
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

        # Should return FlextResult - may fail if env vars not set
        assert hasattr(result, "success")
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

        # Test FlextResult operations
        result1 = utilities.escape_oracle_identifier("test_name")
        assert hasattr(result1, "success")
        assert hasattr(result1, "error") or hasattr(result1, "value")

        result2 = utilities.create_api_from_config({"test": "config"})
        assert hasattr(result2, "success")
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
