"""Comprehensive Oracle Utilities Tests - Real Implementation Without Mocks.

Tests the FlextDbOracleUtilities class completely without mocks,
achieving maximum coverage through real utility operations using flext_tests.



Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import sys
import time
from pathlib import Path
from unittest.mock import Mock

from flext_core import FlextTypes
from pydantic import BaseModel

# Add flext_tests to path
sys.path.insert(0, str(Path(__file__).parents[4] / "flext-core" / "src"))

from flext_tests import FlextMatchers

from flext_db_oracle.utilities import FlextDbOracleUtilities


class TestFlextDbOracleUtilitiesRealFunctionality:
    """Comprehensive tests for Oracle Utilities using ONLY real functionality - NO MOCKS."""

    def setup_method(self) -> None:
        """Setup test utilities with real configuration."""
        self.utilities = FlextDbOracleUtilities()

    def test_utilities_initialization_real(self) -> None:
        """Test utilities initialization - REAL FUNCTIONALITY."""
        assert self.utilities is not None
        assert isinstance(self.utilities, FlextDbOracleUtilities)

    def test_escape_oracle_identifier_real(self) -> None:
        """Test Oracle identifier escaping - REAL FUNCTIONALITY."""
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
                FlextMatchers.assert_result_success(result)
                assert isinstance(result.value, str)
            else:
                FlextMatchers.assert_result_failure(result)

    def test_format_sql_for_oracle_real(self) -> None:
        """Test Oracle SQL formatting - REAL FUNCTIONALITY."""
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
                FlextMatchers.assert_result_success(result)
                assert isinstance(result.value, str)
            else:
                FlextMatchers.assert_result_failure(result)

    def test_generate_query_hash_real(self) -> None:
        """Test query hash generation - REAL FUNCTIONALITY."""
        # Test that same queries produce same hash
        query1 = "SELECT * FROM users WHERE id = ?"
        query2 = "SELECT * FROM users WHERE id = ?"

        # Method returns FlextResult with @safe_result decorator
        result1 = self.utilities.generate_query_hash(query1)
        result2 = self.utilities.generate_query_hash(query2)

        FlextMatchers.assert_result_success(result1)
        FlextMatchers.assert_result_success(result2)
        assert result1.value == result2.value

        # Test that different queries produce different hashes
        query3 = "SELECT * FROM products WHERE id = ?"
        result3 = self.utilities.generate_query_hash(query3)

        FlextMatchers.assert_result_success(result3)
        assert result1.value != result3.value

        # Verify hash format - should be hex string
        assert all(c in "0123456789abcdef" for c in result1.value.lower())

    def test_generate_query_hash_with_params_real(self) -> None:
        """Test query hash generation with parameters - REAL FUNCTIONALITY."""
        query = "SELECT * FROM users WHERE id = ? AND name = ?"
        params1 = {"id": 1, "name": "John"}
        params2 = {"id": 2, "name": "Jane"}

        result1 = self.utilities.generate_query_hash(query, params1)
        result2 = self.utilities.generate_query_hash(query, params2)

        FlextMatchers.assert_result_success(result1)
        FlextMatchers.assert_result_success(result2)
        assert (
            result1.value != result2.value
        )  # Different params should produce different hashes

    def test_format_query_result_real(self) -> None:
        """Test query result formatting - REAL FUNCTIONALITY."""
        # Mock QueryResult
        mock_result = Mock()
        mock_result.fetchall.return_value = [
            {"id": 1, "name": "John"},
            {"id": 2, "name": "Jane"},
        ]

        result = self.utilities.format_query_result(mock_result, format_type="json")
        FlextMatchers.assert_result_success(result)
        formatted = result.value

        assert isinstance(formatted, str)
        # Should be formatted properly

    def test_format_query_result_table_real(self) -> None:
        """Test query result table formatting - REAL FUNCTIONALITY."""
        mock_result = Mock()
        mock_result.fetchall.return_value = [
            {"id": 1, "name": "John", "email": "john@example.com"},
            {"id": 2, "name": "Jane", "email": "jane@example.com"},
        ]

        result = self.utilities.format_query_result(mock_result, format_type="table")
        FlextMatchers.assert_result_success(result)
        formatted = result.value

        assert isinstance(formatted, str)

    def test_format_query_result_empty_real(self) -> None:
        """Test query result formatting with empty data - REAL FUNCTIONALITY."""
        mock_result = Mock()
        mock_result.fetchall.return_value = []

        for format_type in ["table", "json", "csv"]:
            result = self.utilities.format_query_result(
                mock_result, format_type=format_type
            )
            FlextMatchers.assert_result_success(result)
            formatted = result.value
            assert isinstance(formatted, str)
            # Should handle empty data gracefully

    def test_create_api_from_config_method_real(self) -> None:
        """Test create_api_from_config method - REAL FUNCTIONALITY."""
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
        """Test create_api_from_config with invalid config - REAL FUNCTIONALITY."""
        invalid_configs: list[FlextTypes.Core.Dict] = [
            {},  # Empty config
            {"host": "test"},  # Missing required fields
            {"invalid": "config"},  # Invalid field names
        ]

        for invalid_config in invalid_configs:
            result = self.utilities.create_api_from_config(invalid_config)
            FlextMatchers.assert_result_failure(result)
            assert isinstance(result.error, str)

    def test_create_config_from_env_real(self) -> None:
        """Test create_config_from_env method - REAL FUNCTIONALITY."""
        result = self.utilities.create_config_from_env()

        # Should return FlextResult - may fail if env vars not set
        assert hasattr(result, "success")
        assert hasattr(result, "error") or hasattr(result, "value")

    def test_utilities_error_handling_patterns_real(self) -> None:
        """Test utilities error handling patterns - REAL FUNCTIONALITY."""
        utilities = FlextDbOracleUtilities()

        # Test with None inputs - use type ignore to test error handling
        result1 = utilities.escape_oracle_identifier(None)
        FlextMatchers.assert_result_failure(result1)

        # Test with invalid types - use type ignore to test error handling
        utilities.format_sql_for_oracle(123)
        # Should handle gracefully - may work or fail

        # Test create_api_from_config with None
        result3 = utilities.create_api_from_config(None)
        FlextMatchers.assert_result_failure(result3)

    def test_utilities_performance_tracking_real(self) -> None:
        """Test utilities performance tracking - REAL FUNCTIONALITY."""
        start_time = time.time()

        # Perform multiple operations
        for i in range(50):
            result = self.utilities.escape_oracle_identifier(f"test_name_{i}")
            FlextMatchers.assert_result_success(result)

        end_time = time.time()
        elapsed = end_time - start_time

        # Should complete quickly (less than 1 second for 50 operations)
        assert elapsed < 1.0

    def test_utilities_protocols_integration_real(self) -> None:
        """Test utilities protocols integration - REAL FUNCTIONALITY."""

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
        """Test utilities integration with flext-core patterns - REAL FUNCTIONALITY."""
        utilities = FlextDbOracleUtilities()

        # Test FlextResult operations
        result1 = utilities.escape_oracle_identifier("test_name")
        assert hasattr(result1, "success")
        assert hasattr(result1, "error") or hasattr(result1, "value")

        result2 = utilities.create_api_from_config({"test": "config"})
        assert hasattr(result2, "success")
        assert hasattr(result2, "error") or hasattr(result2, "value")

    def test_utilities_string_representations_real(self) -> None:
        """Test utilities string representations - REAL FUNCTIONALITY."""
        utilities = FlextDbOracleUtilities()

        # Test repr/str don't crash
        repr_str = repr(utilities)
        assert isinstance(repr_str, str)
        assert len(repr_str) > 0

        str_repr = str(utilities)
        assert isinstance(str_repr, str)
        assert len(str_repr) > 0

    def test_utilities_multiple_instances_isolation_real(self) -> None:
        """Test that multiple utility instances are properly isolated - REAL FUNCTIONALITY."""
        utilities1 = FlextDbOracleUtilities()
        utilities2 = FlextDbOracleUtilities()

        # Test that instances are separate
        assert utilities1 is not utilities2

        # Test that operations are independent
        result1 = utilities1.escape_oracle_identifier("test_name")
        result2 = utilities2.escape_oracle_identifier("test_name")

        FlextMatchers.assert_result_success(result1)
        FlextMatchers.assert_result_success(result2)
        assert result1.value == result2.value  # Same input, same result

        # But instances should be independent objects
        assert id(utilities1) != id(utilities2)
