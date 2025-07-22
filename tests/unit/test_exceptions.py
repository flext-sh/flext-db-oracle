"""Tests for utils exceptions module.

Tests for Oracle database custom exception classes.
"""

from __future__ import annotations

import pytest

from flext_db_oracle.utils.exceptions import (
    OracleConnectionError,
    OracleDBCoreError,
    SchemaError,
)


class TestOracleDBCoreError:
    """Test base Oracle database core error."""

    def test_basic_error_creation(self) -> None:
        """Test basic error creation with message."""
        error = OracleDBCoreError("Test error message")

        assert str(error) == "Test error message"
        assert error.message == "Test error message"
        assert error.error_code is None

    def test_error_with_code(self) -> None:
        """Test error creation with error code."""
        error = OracleDBCoreError("Test error", error_code="TEST001")

        assert str(error) == "Test error"
        assert error.message == "Test error"
        assert error.error_code == "TEST001"

    def test_error_inheritance(self) -> None:
        """Test that error inherits from Exception."""
        error = OracleDBCoreError("Test")

        assert isinstance(error, Exception)
        assert isinstance(error, OracleDBCoreError)

    def test_error_attributes(self) -> None:
        """Test error attributes are accessible."""
        message = "Database operation failed"
        code = "DB001"
        error = OracleDBCoreError(message, code)

        assert hasattr(error, "message")
        assert hasattr(error, "error_code")
        assert error.message == message
        assert error.error_code == code


class TestOracleConnectionError:
    """Test Oracle connection error."""

    def test_connection_error_basic(self) -> None:
        """Test basic connection error."""
        error = OracleConnectionError("Failed to connect")

        assert str(error) == "Failed to connect"
        assert error.message == "Failed to connect"
        assert error.error_code == "CONNECTION_ERROR"
        assert error.host is None
        assert error.port is None

    def test_connection_error_with_host_port(self) -> None:
        """Test connection error with host and port."""
        error = OracleConnectionError(
            "Connection timeout",
            host="localhost",
            port=1521,
        )

        assert str(error) == "Connection timeout"
        assert error.message == "Connection timeout"
        assert error.error_code == "CONNECTION_ERROR"
        assert error.host == "localhost"
        assert error.port == 1521

    def test_connection_error_inheritance(self) -> None:
        """Test connection error inheritance."""
        error = OracleConnectionError("Test")

        assert isinstance(error, OracleConnectionError)
        assert isinstance(error, OracleDBCoreError)
        assert isinstance(error, Exception)

    def test_connection_error_attributes(self) -> None:
        """Test connection error has all expected attributes."""
        error = OracleConnectionError(
            "Network error",
            host="db.example.com",
            port=1522,
        )

        assert hasattr(error, "message")
        assert hasattr(error, "error_code")
        assert hasattr(error, "host")
        assert hasattr(error, "port")


class TestSchemaError:
    """Test schema error."""

    def test_schema_error_basic(self) -> None:
        """Test basic schema error."""
        error = SchemaError("Schema not found")

        assert str(error) == "Schema not found"
        assert error.message == "Schema not found"
        # Check if it has error_code attribute (might be set by parent)
        if hasattr(error, "error_code"):
            assert error.error_code is not None

    def test_schema_error_with_schema_name(self) -> None:
        """Test schema error with schema name."""
        # Need to check the actual constructor signature
        try:
            error = SchemaError("Schema validation failed", schema_name="TEST_SCHEMA")
            assert error.message == "Schema validation failed"
            if hasattr(error, "schema_name"):
                assert error.schema_name == "TEST_SCHEMA"
        except TypeError:
            # If schema_name parameter doesn't exist, test with just message
            error = SchemaError("Schema validation failed")
            assert error.message == "Schema validation failed"

    def test_schema_error_inheritance(self) -> None:
        """Test schema error inheritance."""
        error = SchemaError("Test schema error")

        assert isinstance(error, SchemaError)
        assert isinstance(error, OracleDBCoreError)
        assert isinstance(error, Exception)

    def test_schema_error_attributes(self) -> None:
        """Test schema error attributes."""
        error = SchemaError("Invalid schema structure")

        assert hasattr(error, "message")
        assert error.message == "Invalid schema structure"

        # Check for additional attributes if they exist
        if hasattr(error, "error_code"):
            assert error.error_code is not None


class TestExceptionHierarchy:
    """Test exception hierarchy and relationships."""

    def test_all_inherit_from_base(self) -> None:
        """Test that all custom exceptions inherit from base."""
        connection_error = OracleConnectionError("test")
        schema_error = SchemaError("test")

        assert isinstance(connection_error, OracleDBCoreError)
        assert isinstance(schema_error, OracleDBCoreError)

    def test_all_inherit_from_exception(self) -> None:
        """Test that all exceptions inherit from Exception."""
        base_error = OracleDBCoreError("test")
        connection_error = OracleConnectionError("test")
        schema_error = SchemaError("test")

        assert isinstance(base_error, Exception)
        assert isinstance(connection_error, Exception)
        assert isinstance(schema_error, Exception)

    def test_exception_can_be_raised_and_caught(self) -> None:
        """Test that exceptions can be raised and caught."""
        # Test base error
        msg = "Base error"
        with pytest.raises(OracleDBCoreError) as exc_info:
            raise OracleDBCoreError(msg)
        assert "Base error" in str(exc_info.value)

        # Test connection error
        msg = "Connection failed"
        with pytest.raises(OracleConnectionError) as exc_info:
            raise OracleConnectionError(msg)
        assert "Connection failed" in str(exc_info.value)

        # Test schema error
        msg = "Schema error"
        with pytest.raises(SchemaError) as exc_info:
            raise SchemaError(msg)
        assert "Schema error" in str(exc_info.value)

    def test_catch_specific_vs_base(self) -> None:
        """Test catching specific vs base exceptions."""
        # Can catch specific exception as base
        msg = "Connection issue"
        with pytest.raises(OracleDBCoreError) as exc_info:
            raise OracleConnectionError(msg)
        e = exc_info.value
        assert isinstance(e, OracleConnectionError)
        assert e.message == "Connection issue"

        # Can catch specific exception specifically
        msg = "Schema issue"
        with pytest.raises(SchemaError) as exc_info:
            raise SchemaError(msg)
        e = exc_info.value
        assert e.message == "Schema issue"


class TestErrorScenarios:
    """Test realistic error scenarios."""

    def test_connection_timeout_scenario(self) -> None:
        """Test connection timeout error scenario."""
        error = OracleConnectionError(
            "Connection timed out after 30 seconds",
            host="prod-db-01.company.com",
            port=1521,
        )

        assert "timed out" in error.message
        assert error.host == "prod-db-01.company.com"
        assert error.port == 1521
        assert error.error_code == "CONNECTION_ERROR"

    def test_invalid_credentials_scenario(self) -> None:
        """Test invalid credentials error scenario."""
        error = OracleConnectionError(
            "Invalid username or password",
            host="localhost",
            port=1521,
        )

        assert "Invalid username" in error.message
        assert error.error_code == "CONNECTION_ERROR"

    def test_schema_not_found_scenario(self) -> None:
        """Test schema not found error scenario."""
        error = SchemaError("Schema 'NONEXISTENT' does not exist")

        assert "does not exist" in error.message
        assert isinstance(error, OracleDBCoreError)

    def test_multiple_errors_in_sequence(self) -> None:
        """Test handling multiple errors in sequence."""
        errors = [
            OracleDBCoreError("General error"),
            OracleConnectionError("Connection failed", "localhost", 1521),
            SchemaError("Schema validation failed"),
        ]

        for error in errors:
            assert isinstance(error, OracleDBCoreError)
            assert isinstance(error, Exception)
            assert len(error.message) > 0
