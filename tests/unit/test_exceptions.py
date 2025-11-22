"""Test FlextDbOracleExceptions functionality.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_db_oracle import FlextDbOracleExceptions


class TestFlextDbOracleExceptions:
    """Test FlextDbOracleExceptions functionality."""

    def test_exceptions_has_error_class(self) -> None:
        """Test exceptions has Error class."""
        assert hasattr(FlextDbOracleExceptions, "Error")

    def test_exceptions_has_connection_error_class(self) -> None:
        """Test exceptions has OracleConnectionError class."""
        assert hasattr(FlextDbOracleExceptions, "OracleConnectionError")

    def test_error_creation(self) -> None:
        """Test Error can be created."""
        error = FlextDbOracleExceptions.Error("Test error")
        assert error is not None
        assert "Test error" in str(error)

    def test_error_with_oracle_code(self) -> None:
        """Test Error with oracle error code."""
        error = FlextDbOracleExceptions.Error(
            "Test error", oracle_error_code="ORA-12345"
        )
        assert error is not None
        assert error.oracle_error_code == "ORA-12345"

    def test_connection_error_creation(self) -> None:
        """Test OracleConnectionError can be created."""
        error = FlextDbOracleExceptions.OracleConnectionError("Connection failed")
        assert error is not None
        assert "Connection failed" in str(error)
