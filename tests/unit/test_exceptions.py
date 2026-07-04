"""Test e functionality.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_tests import tm

from flext_db_oracle import FlextDbOracleExceptions


class TestsFlextDbOracleExceptions:
    """Test e functionality."""

    def test_exceptions_has_error_class(self) -> None:
        """Test exceptions has Error class."""
        tm.that(hasattr(FlextDbOracleExceptions, "Error"), eq=True)

    def test_exceptions_has_connection_error_class(self) -> None:
        """Test exceptions has OracleConnectionError class."""
        tm.that(hasattr(FlextDbOracleExceptions, "OracleConnectionError"), eq=True)

    def test_error_creation(self) -> None:
        """Test Error can be created."""
        error = FlextDbOracleExceptions.Error("Test error")
        tm.that(error, none=False)
        tm.that(str(error), has="Test error")

    def test_error_with_oracle_code(self) -> None:
        """Test Error with oracle error code."""
        error = FlextDbOracleExceptions.Error(
            "Test error",
            oracle_error_code="ORA-12345",
        )
        tm.that(error, none=False)
        tm.that(error.oracle_error_code, eq="ORA-12345")

    def test_connection_error_creation(self) -> None:
        """Test OracleConnectionError can be created."""
        error = FlextDbOracleExceptions.OracleConnectionError("Connection failed")
        tm.that(error, none=False)
        tm.that(str(error), has="Connection failed")
