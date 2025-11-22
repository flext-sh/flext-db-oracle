"""Test FlextDbOracleUtilities functionality.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_db_oracle import FlextDbOracleUtilities


class TestFlextDbOracleUtilities:
    """Test FlextDbOracleUtilities functionality."""

    def test_utilities_creation(self) -> None:
        """Test utilities can be created."""
        utilities = FlextDbOracleUtilities()
        assert utilities is not None

    def test_utilities_has_generate_query_hash(self) -> None:
        """Test utilities has generate_query_hash method."""
        assert hasattr(FlextDbOracleUtilities, "generate_query_hash")

    def test_generate_query_hash_basic(self) -> None:
        """Test basic query hash generation."""
        result = FlextDbOracleUtilities.generate_query_hash("SELECT 1", None)
        assert result.is_success
        hash_value = result.unwrap()
        assert isinstance(hash_value, str)
        assert len(hash_value) > 0

    def test_generate_query_hash_with_params(self) -> None:
        """Test query hash generation with parameters."""
        params = {"id": 1, "name": "test"}
        result = FlextDbOracleUtilities.generate_query_hash(
            "SELECT * FROM table", params
        )
        assert result.is_success
        hash_value = result.unwrap()
        assert isinstance(hash_value, str)

    def test_format_query_result_basic(self) -> None:
        """Test basic query result formatting."""
        utilities = FlextDbOracleUtilities()
        data = [{"id": 1, "name": "John"}]
        result = utilities.format_query_result(data, "json")
        assert result.is_success
        formatted = result.unwrap()
        assert isinstance(formatted, str)
        assert "John" in formatted

    def test_format_query_result_empty(self) -> None:
        """Test empty query result formatting."""
        utilities = FlextDbOracleUtilities()
        data = []
        result = utilities.format_query_result(data, "table")
        assert result.is_success
        formatted = result.unwrap()
        assert isinstance(formatted, str)
