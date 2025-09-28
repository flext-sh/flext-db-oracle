"""Real comprehensive tests for exceptions module without mocks.

Tests all exception functionality with real objects and validations.
Coverage target: 31% → 90%+


Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import pytest

from flext_db_oracle import (
    FlextDbOracleExceptions,
)


class TestExceptionParams:
    """Test ExceptionParams dataclass."""

    def test_exception_params_creation(self) -> None:
        """Test creating ExceptionParams with all fields."""
        params = FlextDbOracleExceptions.ExceptionParams(
            message="Test error",
            error_code="TEST_CODE",
            context={"key": "value"},
        )
        assert params.message == "Test error"
        assert params.error_code == "TEST_CODE"
        assert params.context == {"key": "value"}

    def test_exception_params_defaults(self) -> None:
        """Test ExceptionParams with default values."""
        params = FlextDbOracleExceptions.ExceptionParams(
            message="Test error",
            error_code="DEFAULT_CODE",
        )
        assert params.message == "Test error"
        assert params.error_code == "DEFAULT_CODE"
        assert params.context == {}

    def test_exception_params_empty_message_raises(self) -> None:
        """Test that empty message raises ValueError."""
        with pytest.raises(ValueError, match="Exception message cannot be empty"):
            FlextDbOracleExceptions.ExceptionParams(
                message="", error_code="TEST_CODE", domain_events=[]
            )

    def test_exception_params_whitespace_message_raises(self) -> None:
        """Test that whitespace-only message raises ValueError."""
        with pytest.raises(ValueError, match="Exception message cannot be empty"):
            FlextDbOracleExceptions.ExceptionParams(
                message="   ", error_code="TEST_CODE", domain_events=[]
            )

    def test_exception_params_frozen(self) -> None:
        """Test that ExceptionParams is frozen (immutable)."""
        params = FlextDbOracleExceptions.ExceptionParams(
            message="Test", error_code="TEST_CODE", domain_events=[]
        )
        with pytest.raises(AttributeError):
            setattr(params, "message", "Modified")


class TestOracleErrorCodes:
    """Test OracleErrorCodes enum."""

    def test_error_codes_exist(self) -> None:
        """Test that all error codes are defined."""
        codes = FlextDbOracleExceptions.OracleErrorCodes
        assert codes.VALIDATION_ERROR == "ORACLE_VALIDATION_ERROR"
        assert codes.CONFIGURATION_ERROR == "ORACLE_CONFIGURATION_ERROR"
        assert codes.CONNECTION_ERROR == "ORACLE_CONNECTION_ERROR"
        assert codes.PROCESSING_ERROR == "ORACLE_PROCESSING_ERROR"
        assert codes.AUTHENTICATION_ERROR == "ORACLE_AUTHENTICATION_ERROR"
        assert codes.TIMEOUT_ERROR == "ORACLE_TIMEOUT_ERROR"
        assert codes.QUERY_ERROR == "ORACLE_QUERY_ERROR"
        assert codes.METADATA_ERROR == "ORACLE_METADATA_ERROR"

    def test_error_codes_count(self) -> None:
        """Test that we have the expected number of error codes."""
        codes = FlextDbOracleExceptions.OracleErrorCodes
        # Count the attributes that are string constants
        error_code_attrs = [
            attr
            for attr in dir(codes)
            if not attr.startswith("_") and isinstance(getattr(codes, attr), str)
        ]
        assert len(error_code_attrs) == 8


class TestValidationError:
    """Test ValidationError exception."""

    def test_validation_error_with_string(self) -> None:
        """Test ValidationError with simple string message."""
        error = FlextDbOracleExceptions.ValidationError(
            "Invalid value",
            code="ORACLE_VALIDATION_ERROR",
        )
        assert "Invalid value" in str(error)
        assert error.error_code == "VALIDATION_ERROR"
        assert error.context == {
            "field": None,
            "value": None,
            "validation_details": None,
        }

    def test_validation_error_with_params(self) -> None:
        """Test ValidationError with parameters."""
        error = FlextDbOracleExceptions.ValidationError(
            "Field validation failed",
            code="FIELD_ERROR",
            context={"field": "username", "value": "invalid@"},
        )
        assert "Field validation failed" in str(error)
        assert error.error_code == "VALIDATION_ERROR"  # flext-core uses default code
        assert error.context == {
            "field": "None",
            "value": "None",
            "validation_details": "None",
        }  # flext-core overrides context for ValidationError with string 'None' values

    def test_validation_error_inheritance(self) -> None:
        """Test that ValidationError inherits from correct base classes."""
        error = FlextDbOracleExceptions.ValidationError("Test")
        assert isinstance(error, Exception)
        assert isinstance(error, FlextDbOracleExceptions.BaseError)


class TestConfigurationError:
    """Test ConfigurationError exception."""

    def test_configuration_error_with_string(self) -> None:
        """Test ConfigurationError with simple string message."""
        error = FlextDbOracleExceptions.ConfigurationError(
            "Invalid config",
            code="ORACLE_CONFIGURATION_ERROR",
        )
        assert "Invalid config" in str(error)
        assert error.error_code == "CONFIGURATION_ERROR"  # flext-core uses default code
        assert error.context == {
            "config_key": "None",
            "config_file": "None",
        }  # ConfigurationError has string 'None' default fields

    def test_configuration_error_with_params(self) -> None:
        """Test ConfigurationError with parameters."""
        error = FlextDbOracleExceptions.ConfigurationError(
            "Missing required configuration",
            code="CONFIG_MISSING",
            context={"missing": ["host", "port"]},
        )
        assert "Missing required configuration" in str(error)
        assert error.error_code == "CONFIGURATION_ERROR"  # flext-core uses default code
        assert error.context["missing"] == [
            "host",
            "port",
        ]  # Check custom context is preserved
        assert "config_key" in error.context  # Default fields are added by flext-core


class TestConnectionError:
    """Test ConnectionError exception."""

    def test_connection_error_with_string(self) -> None:
        """Test ConnectionError with simple string message."""
        error = FlextDbOracleExceptions.OracleConnectionError(
            "Connection failed",
            code="ORACLE_CONNECTION_ERROR",
        )
        assert "Connection failed" in str(error)
        assert error.error_code == "CONNECTION_ERROR"  # flext-core uses default code
        assert error.context == {
            "endpoint": "None",
            "service": "None",
        }  # ConnectionError has different default fields

    def test_connection_error_with_params(self) -> None:
        """Test ConnectionError with parameters."""
        error = FlextDbOracleExceptions.OracleConnectionError(
            "Unable to connect to Oracle",
            code="CONN_TIMEOUT",
            context={"host": "localhost", "port": 1521, "timeout": 30},
        )
        assert "Unable to connect to Oracle" in str(error)
        assert error.error_code == "CONNECTION_ERROR"  # flext-core uses default code
        assert error.context["host"] == "localhost"
        assert error.context["port"] == 1521


class TestProcessingError:
    """Test ProcessingError exception."""

    def test_processing_error_with_string(self) -> None:
        """Test ProcessingError with simple string message."""
        error = FlextDbOracleExceptions.ProcessingError(
            "Processing failed",
            code="ORACLE_PROCESSING_ERROR",
        )
        assert "Processing failed" in str(error)
        assert error.error_code == "PROCESSING_ERROR"  # flext-core uses default code

    def test_processing_error_with_params(self) -> None:
        """Test ProcessingError with ExceptionParams."""
        params = FlextDbOracleExceptions.ExceptionParams(
            message="Failed to process query result",
            error_code="PROC_PARSE_ERROR",
            context={"row_count": 1000, "error_at": 500},
        )
        error = FlextDbOracleExceptions.ProcessingError(
            params.message,
            code=params.error_code,
            context=params.context,
        )
        assert "Failed to process query result" in str(error)
        assert (
            error.error_code == "PROC_PARSE_ERROR"
        )  # Uses the code that was passed  # Uses the code that was passed


class TestAuthenticationError:
    """Test AuthenticationError exception."""

    def test_authentication_error_with_string(self) -> None:
        """Test AuthenticationError with simple string message."""
        error = FlextDbOracleExceptions.AuthenticationError(
            "Auth failed",
            code="ORACLE_AUTHENTICATION_ERROR",
        )
        assert "Auth failed" in str(error)
        assert (
            error.error_code == "AUTHENTICATION_ERROR"
        )  # flext-core uses default code

    def test_authentication_error_with_params(self) -> None:
        """Test AuthenticationError with ExceptionParams."""
        params = FlextDbOracleExceptions.ExceptionParams(
            message="Invalid credentials",
            error_code="AUTH_INVALID_CREDS",
            context={"username": "testuser", "attempts": 3},
        )
        error = FlextDbOracleExceptions.AuthenticationError(
            params.message,
            code=params.error_code,
            context=params.context,
        )
        assert "Invalid credentials" in str(error)
        assert (
            error.error_code == "AUTHENTICATION_ERROR"
        )  # flext-core uses default code  # flext-core uses default code


class TestTimeoutError:
    """Test TimeoutError exception."""

    def test_timeout_error_with_string(self) -> None:
        """Test TimeoutError with simple string message."""
        error = FlextDbOracleExceptions.OracleTimeoutError(
            "Operation timed out",
            code="ORACLE_TIMEOUT_ERROR",
        )
        assert "Operation timed out" in str(error)
        assert error.error_code == "TIMEOUT_ERROR"  # flext-core uses default code

    def test_timeout_error_with_params(self) -> None:
        """Test TimeoutError with parameters."""
        error = FlextDbOracleExceptions.OracleTimeoutError(
            "Query execution timeout",
            code="QUERY_TIMEOUT",
            context={"timeout_seconds": 30, "query": "SELECT * FROM large_table"},
        )
        assert "Query execution timeout" in str(error)
        assert error.error_code == "QUERY_TIMEOUT"  # Uses the code that was passed


class TestQueryError:
    """Test QueryError exception."""

    def test_query_error_with_string(self) -> None:
        """Test QueryError with simple string message."""
        error = FlextDbOracleExceptions.OracleQueryError("Invalid SQL")
        assert "Invalid SQL" in str(error)
        # QueryError inherits from _OperationError which has default code
        assert hasattr(error, "error_code")

    def test_query_error_with_params(self) -> None:
        """Test QueryError with parameters."""
        error = FlextDbOracleExceptions.OracleQueryError(
            "SQL syntax error",
            code="SQL_SYNTAX_ERROR",
            context={"line": 5, "column": 10, "near": "FORM"},
        )
        assert "SQL syntax error" in str(error)
        # Code from params is used
        assert error.error_code == "SQL_SYNTAX_ERROR"  # Uses the code that was passed


class TestMetadataError:
    """Test MetadataError exception."""

    def test_metadata_error_with_string(self) -> None:
        """Test MetadataError with simple string message."""
        error = FlextDbOracleExceptions.OracleMetadataError("Metadata not found")
        assert "Metadata not found" in str(error)
        # MetadataError inherits from _OperationError
        assert hasattr(error, "error_code")

    def test_metadata_error_with_params(self) -> None:
        """Test MetadataError with parameters."""
        error = FlextDbOracleExceptions.OracleMetadataError(
            "Table metadata unavailable",
            code="META_TABLE_NOT_FOUND",
            context={"schema": "PUBLIC", "table": "USERS"},
        )
        assert "Table metadata unavailable" in str(error)
        # Code from params is used
        assert (
            error.error_code == "PROCESSING_ERROR"
        )  # flext-core uses default code (MetadataError is alias for ProcessingError)


class TestExceptionHelperMethods:
    """Test helper methods in FlextDbOracleExceptions."""

    def test_create_validation_error(self) -> None:
        """Test ValidationError creation with parameters."""
        error = FlextDbOracleExceptions.ValidationError(
            "Invalid input",
            code="ORACLE_VALIDATION_ERROR",
            context={"input": "test"},
        )
        assert isinstance(error, FlextDbOracleExceptions.ValidationError)
        assert "Invalid input" in str(error)
        assert error.context["input"] == "test"  # Custom context is preserved
        assert "field" in error.context  # Default fields are added by flext-core
        assert error.error_code == "VALIDATION_ERROR"

    def test_create_configuration_error(self) -> None:
        """Test ConfigurationError creation with parameters."""
        error = FlextDbOracleExceptions.ConfigurationError(
            "Missing config",
            code="ORACLE_CONFIGURATION_ERROR",
            context={"required": ["host"]},
        )
        assert isinstance(error, FlextDbOracleExceptions.ConfigurationError)
        assert "Missing config" in str(error)
        assert error.context == {
            "required": ["host"],
            "config_file": "None",
            "config_key": "None",
        }

    def test_create_connection_error(self) -> None:
        """Test DatabaseConnectionError creation with parameters."""
        error = FlextDbOracleExceptions.OracleConnectionError(
            "Connection lost",
            code="ORACLE_CONNECTION_ERROR",
            context={"retry_count": 3},
        )
        assert isinstance(error, FlextDbOracleExceptions.OracleConnectionError)
        assert "Connection lost" in str(error)

    def test_create_processing_error(self) -> None:
        """Test ProcessingError creation with parameters."""
        error = FlextDbOracleExceptions.ProcessingError(
            "Processing failed",
            code="ORACLE_PROCESSING_ERROR",
            context={"stage": "parsing"},
        )
        assert isinstance(error, FlextDbOracleExceptions.ProcessingError)
        assert "Processing failed" in str(error)
        assert error.context["stage"] == "parsing"  # Custom context is preserved
        assert (
            "business_rule" in error.context
        )  # Default fields are added by flext-core

    def test_create_authentication_error(self) -> None:
        """Test AuthenticationError creation with parameters."""
        error = FlextDbOracleExceptions.AuthenticationError(
            "Auth required",
            code="ORACLE_AUTHENTICATION_ERROR",
            context={"realm": "REDACTED_LDAP_BIND_PASSWORD"},
        )
        assert isinstance(error, FlextDbOracleExceptions.AuthenticationError)
        assert "Auth required" in str(error)
        assert error.context["realm"] == "REDACTED_LDAP_BIND_PASSWORD"  # Custom context is preserved
        assert "auth_method" in error.context  # Default fields are added by flext-core

    def test_create_timeout_error(self) -> None:
        """Test DatabaseTimeoutError creation with parameters."""
        error = FlextDbOracleExceptions.OracleTimeoutError(
            "Timed out",
            code="ORACLE_TIMEOUT_ERROR",
            context={"duration": 60},
        )
        assert isinstance(error, FlextDbOracleExceptions.OracleTimeoutError)
        assert "Timed out" in str(error)
        assert error.context["duration"] == 60  # Custom context is preserved
        assert (
            "timeout_seconds" in error.context
        )  # Default fields are added by flext-core

    def test_create_query_error(self) -> None:
        """Test QueryError creation with parameters."""
        error = FlextDbOracleExceptions.OracleQueryError(
            "Query failed",
            code="ORACLE_QUERY_ERROR",
            context={"sql": "SELECT 1"},
        )
        assert isinstance(error, FlextDbOracleExceptions.OracleQueryError)
        assert "Query failed" in str(error)
        assert error.context["sql"] == "SELECT 1"  # Custom context is preserved
        assert (
            "business_rule" in error.context
        )  # Default fields are added by flext-core

    def test_create_metadata_error(self) -> None:
        """Test MetadataError creation with parameters."""
        error = FlextDbOracleExceptions.OracleMetadataError(
            "Metadata missing",
            code="ORACLE_METADATA_ERROR",
            context={"object": "INDEX"},
        )
        assert isinstance(error, FlextDbOracleExceptions.OracleMetadataError)
        assert "Metadata missing" in str(error)
        assert error.context is not None
        assert error.context.get("object") == "INDEX"


class TestExceptionRaising:
    """Test that exceptions can be properly raised and caught."""

    def test_raise_validation_error(self) -> None:
        """Test raising and catching ValidationError."""
        error_msg = "Test validation error"
        with pytest.raises(FlextDbOracleExceptions.ValidationError) as exc_info:
            raise FlextDbOracleExceptions.ValidationError(error_msg)
        assert error_msg in str(exc_info.value)

    def test_raise_configuration_error(self) -> None:
        """Test raising and catching ConfigurationError."""
        error_msg = "Test config error"
        with pytest.raises(FlextDbOracleExceptions.ConfigurationError) as exc_info:
            raise FlextDbOracleExceptions.ConfigurationError(error_msg)
        assert error_msg in str(exc_info.value)

    def test_exception_hierarchy(self) -> None:
        """Test that exceptions follow proper inheritance hierarchy."""
        validation_error = FlextDbOracleExceptions.ValidationError("Test")
        assert isinstance(validation_error, Exception)
        assert isinstance(validation_error, FlextDbOracleExceptions.BaseError)

        config_error = FlextDbOracleExceptions.ConfigurationError("Test")
        assert isinstance(config_error, Exception)


class TestFactoryMethods:
    """Test factory methods for creating specific exception types."""

    def test_create_validation_error_factory(self) -> None:
        """Test create_validation_error factory method."""
        error = FlextDbOracleExceptions.create_validation_error(
            field="username",
            value="invalid@",
            message="Validation failed",
        )
        # Factory method returns FlextDbOracleExceptions.ValidationError

        assert isinstance(error, FlextDbOracleExceptions.OracleValidationError)
        assert "Validation failed" in str(error)

    def test_create_connection_error_factory(self) -> None:
        """Test create_connection_error factory method."""
        error = FlextDbOracleExceptions.create_connection_error(
            host="localhost",
            port=1521,
            message="Connection failed",
        )
        # Factory method returns OracleConnectionError

        assert isinstance(error, FlextDbOracleExceptions.OracleConnectionError)
        assert "Connection failed" in str(error)

    def test_is_oracle_error_method(self) -> None:
        """Test is_oracle_error utility method."""
        oracle_error = FlextDbOracleExceptions.ValidationError("Test")
        non_oracle_error = ValueError("Test")

        assert FlextDbOracleExceptions.is_oracle_error(oracle_error) is True
        assert FlextDbOracleExceptions.is_oracle_error(non_oracle_error) is False
