"""Real comprehensive tests for exceptions module without mocks.

Tests all exception functionality with real objects and validations.
Coverage target: 31% → 90%+
"""

from __future__ import annotations

import pytest

from flext_db_oracle import (
    ExceptionParams,
    FlextDbOracleExceptions,
    ParameterObject,
)


class TestExceptionParams:
    """Test ExceptionParams dataclass."""

    def test_exception_params_creation(self) -> None:
        """Test creating ExceptionParams with all fields."""
        params = ExceptionParams(
            message="Test error",
            code="TEST_CODE",
            context={"key": "value"},
        )
        assert params.message == "Test error"
        assert params.code == "TEST_CODE"
        assert params.context == {"key": "value"}

    def test_exception_params_defaults(self) -> None:
        """Test ExceptionParams with default values."""
        params = ExceptionParams(message="Test error")
        assert params.message == "Test error"
        assert params.code is None
        assert params.context == {}  # Auto-resolved in __post_init__

    def test_exception_params_empty_message_raises(self) -> None:
        """Test that empty message raises ValueError."""
        with pytest.raises(ValueError, match="Message cannot be empty"):
            ExceptionParams(message="")

    def test_exception_params_whitespace_message_raises(self) -> None:
        """Test that whitespace-only message raises ValueError."""
        with pytest.raises(ValueError, match="Message cannot be empty"):
            ExceptionParams(message="   ")

    def test_exception_params_frozen(self) -> None:
        """Test that ExceptionParams is frozen (immutable)."""
        params = ExceptionParams(message="Test")
        with pytest.raises(AttributeError):
            params.message = "Modified"


class TestOracleErrorCodes:
    """Test OracleErrorCodes enum."""

    def test_error_codes_exist(self) -> None:
        """Test that all error codes are defined."""
        codes = FlextDbOracleExceptions.OracleErrorCodes
        assert codes.ORACLE_ERROR.value == "ORACLE_ERROR"
        assert codes.ORACLE_VALIDATION_ERROR.value == "ORACLE_VALIDATION_ERROR"
        assert codes.ORACLE_CONFIGURATION_ERROR.value == "ORACLE_CONFIGURATION_ERROR"
        assert codes.ORACLE_CONNECTION_ERROR.value == "ORACLE_CONNECTION_ERROR"
        assert codes.ORACLE_PROCESSING_ERROR.value == "ORACLE_PROCESSING_ERROR"
        assert codes.ORACLE_AUTHENTICATION_ERROR.value == "ORACLE_AUTHENTICATION_ERROR"
        assert codes.ORACLE_TIMEOUT_ERROR.value == "ORACLE_TIMEOUT_ERROR"
        assert codes.ORACLE_QUERY_ERROR.value == "ORACLE_QUERY_ERROR"
        assert codes.ORACLE_METADATA_ERROR.value == "ORACLE_METADATA_ERROR"

    def test_error_codes_count(self) -> None:
        """Test that we have the expected number of error codes."""
        codes = list(FlextDbOracleExceptions.OracleErrorCodes)
        assert len(codes) == 9


class TestValidationError:
    """Test ValidationError exception."""

    def test_validation_error_with_string(self) -> None:
        """Test ValidationError with simple string message."""
        error = FlextDbOracleExceptions.ValidationError("Invalid value")
        assert str(error) == "Invalid value"
        assert error.error_code == "ORACLE_VALIDATION_ERROR"
        assert error.context == {}

    def test_validation_error_with_params(self) -> None:
        """Test ValidationError with ExceptionParams."""
        params = ExceptionParams(
            message="Field validation failed",
            code="FIELD_ERROR",
            context={"field": "username", "value": "invalid@"},
        )
        error = FlextDbOracleExceptions.ValidationError(params)
        assert str(error) == "Field validation failed"
        assert error.error_code == "FIELD_ERROR"
        assert error.context == {"field": "username", "value": "invalid@"}

    def test_validation_error_inheritance(self) -> None:
        """Test that ValidationError inherits from ValueError."""
        error = FlextDbOracleExceptions.ValidationError("Test")
        assert isinstance(error, ValueError)


class TestConfigurationError:
    """Test ConfigurationError exception."""

    def test_configuration_error_with_string(self) -> None:
        """Test ConfigurationError with simple string message."""
        error = FlextDbOracleExceptions.ConfigurationError("Invalid config")
        assert str(error) == "Invalid config"
        assert error.error_code == "ORACLE_CONFIGURATION_ERROR"
        assert error.context == {}

    def test_configuration_error_with_params(self) -> None:
        """Test ConfigurationError with ExceptionParams."""
        params = ExceptionParams(
            message="Missing required configuration",
            code="CONFIG_MISSING",
            context={"missing": ["host", "port"]},
        )
        error = FlextDbOracleExceptions.ConfigurationError(params)
        assert str(error) == "Missing required configuration"
        assert error.error_code == "CONFIG_MISSING"
        assert error.context == {"missing": ["host", "port"]}


class TestConnectionError:
    """Test ConnectionError exception."""

    def test_connection_error_with_string(self) -> None:
        """Test ConnectionError with simple string message."""
        error = FlextDbOracleExceptions.ConnectionError("Connection failed")
        assert str(error) == "Connection failed"
        assert error.error_code == "ORACLE_CONNECTION_ERROR"
        assert error.context == {}

    def test_connection_error_with_params(self) -> None:
        """Test ConnectionError with ExceptionParams."""
        params = ExceptionParams(
            message="Unable to connect to Oracle",
            code="CONN_TIMEOUT",
            context={"host": "localhost", "port": 1521, "timeout": 30},
        )
        error = FlextDbOracleExceptions.ConnectionError(params)
        assert str(error) == "Unable to connect to Oracle"
        assert error.error_code == "CONN_TIMEOUT"
        assert error.context["host"] == "localhost"
        assert error.context["port"] == 1521


class TestProcessingError:
    """Test ProcessingError exception."""

    def test_processing_error_with_string(self) -> None:
        """Test ProcessingError with simple string message."""
        error = FlextDbOracleExceptions.ProcessingError("Processing failed")
        assert str(error) == "Processing failed"
        assert error.error_code == "ORACLE_PROCESSING_ERROR"

    def test_processing_error_with_params(self) -> None:
        """Test ProcessingError with ExceptionParams."""
        params = ExceptionParams(
            message="Failed to process query result",
            code="PROC_PARSE_ERROR",
            context={"row_count": 1000, "error_at": 500},
        )
        error = FlextDbOracleExceptions.ProcessingError(params)
        assert str(error) == "Failed to process query result"
        assert error.error_code == "PROC_PARSE_ERROR"


class TestAuthenticationError:
    """Test AuthenticationError exception."""

    def test_authentication_error_with_string(self) -> None:
        """Test AuthenticationError with simple string message."""
        error = FlextDbOracleExceptions.AuthenticationError("Auth failed")
        assert "Auth failed" in str(error)
        assert error.error_code == "ORACLE_AUTHENTICATION_ERROR"

    def test_authentication_error_with_params(self) -> None:
        """Test AuthenticationError with ExceptionParams."""
        params = ExceptionParams(
            message="Invalid credentials",
            code="AUTH_INVALID_CREDS",
            context={"username": "testuser", "attempts": 3},
        )
        error = FlextDbOracleExceptions.AuthenticationError(params)
        assert "Invalid credentials" in str(error)
        assert error.error_code == "AUTH_INVALID_CREDS"


class TestTimeoutError:
    """Test TimeoutError exception."""

    def test_timeout_error_with_string(self) -> None:
        """Test TimeoutError with simple string message."""
        error = FlextDbOracleExceptions.TimeoutError("Operation timed out")
        assert "Operation timed out" in str(error)
        assert error.error_code == "ORACLE_TIMEOUT_ERROR"

    def test_timeout_error_with_params(self) -> None:
        """Test TimeoutError with ExceptionParams."""
        params = ExceptionParams(
            message="Query execution timeout",
            code="QUERY_TIMEOUT",
            context={"timeout_seconds": 30, "query": "SELECT * FROM large_table"},
        )
        error = FlextDbOracleExceptions.TimeoutError(params)
        assert "Query execution timeout" in str(error)
        assert error.error_code == "QUERY_TIMEOUT"


class TestQueryError:
    """Test QueryError exception."""

    def test_query_error_with_string(self) -> None:
        """Test QueryError with simple string message."""
        error = FlextDbOracleExceptions.QueryError("Invalid SQL")
        assert "Invalid SQL" in str(error)
        # QueryError inherits from _OperationError which has default code
        assert hasattr(error, "error_code")

    def test_query_error_with_params(self) -> None:
        """Test QueryError with ParameterObject."""
        params = ParameterObject(
            {
                "code": "SQL_SYNTAX_ERROR",
                "context": {"line": 5, "column": 10, "near": "FORM"},
            }
        )
        error = FlextDbOracleExceptions.QueryError("SQL syntax error", params=params)
        assert "SQL syntax error" in str(error)
        # Code from params is used
        assert error.error_code == "SQL_SYNTAX_ERROR"


class TestMetadataError:
    """Test MetadataError exception."""

    def test_metadata_error_with_string(self) -> None:
        """Test MetadataError with simple string message."""
        error = FlextDbOracleExceptions.MetadataError("Metadata not found")
        assert "Metadata not found" in str(error)
        # MetadataError inherits from _OperationError
        assert hasattr(error, "error_code")

    def test_metadata_error_with_params(self) -> None:
        """Test MetadataError with ParameterObject."""
        from flext_db_oracle.mixins import ParameterObject

        params = ParameterObject(
            {
                "code": "META_TABLE_NOT_FOUND",
                "context": {"schema": "PUBLIC", "table": "USERS"},
            }
        )
        error = FlextDbOracleExceptions.MetadataError(
            "Table metadata unavailable", params=params
        )
        assert "Table metadata unavailable" in str(error)
        # Code from params is used
        assert error.error_code == "META_TABLE_NOT_FOUND"


class TestExceptionHelperMethods:
    """Test helper methods in FlextDbOracleExceptions."""

    def test_create_validation_error(self) -> None:
        """Test create_validation_error helper method."""
        error = FlextDbOracleExceptions.create_validation_error(
            "Invalid input", {"input": "test"}
        )
        assert isinstance(error, FlextDbOracleExceptions.ValidationError)
        assert str(error) == "Invalid input"
        assert error.context == {"input": "test"}

    def test_create_configuration_error(self) -> None:
        """Test create_configuration_error helper method."""
        error = FlextDbOracleExceptions.create_configuration_error(
            "Missing config", {"required": ["host"]}
        )
        assert isinstance(error, FlextDbOracleExceptions.ConfigurationError)
        assert str(error) == "Missing config"
        assert error.context == {"required": ["host"]}

    def test_create_connection_error(self) -> None:
        """Test create_connection_error helper method."""
        error = FlextDbOracleExceptions.create_connection_error(
            "Connection lost", {"retry_count": 3}
        )
        assert isinstance(error, FlextDbOracleExceptions.ConnectionError)
        assert str(error) == "Connection lost"
        assert error.context == {"retry_count": 3}

    def test_create_processing_error(self) -> None:
        """Test create_processing_error helper method."""
        error = FlextDbOracleExceptions.create_processing_error(
            "Processing failed", {"stage": "parsing"}
        )
        assert isinstance(error, FlextDbOracleExceptions.ProcessingError)
        assert str(error) == "Processing failed"
        assert error.context == {"stage": "parsing"}

    def test_create_authentication_error(self) -> None:
        """Test create_authentication_error helper method."""
        error = FlextDbOracleExceptions.create_authentication_error(
            "Auth required", {"realm": "REDACTED_LDAP_BIND_PASSWORD"}
        )
        assert isinstance(error, FlextDbOracleExceptions.AuthenticationError)
        assert str(error) == "Auth required"
        assert error.context == {"realm": "REDACTED_LDAP_BIND_PASSWORD"}

    def test_create_timeout_error(self) -> None:
        """Test create_timeout_error helper method."""
        error = FlextDbOracleExceptions.create_timeout_error(
            "Timed out", {"duration": 60}
        )
        assert isinstance(error, FlextDbOracleExceptions.TimeoutError)
        assert str(error) == "Timed out"
        assert error.context == {"duration": 60}

    def test_create_query_error(self) -> None:
        """Test create_query_error helper method."""
        error = FlextDbOracleExceptions.create_query_error(
            "Query failed", {"sql": "SELECT 1"}
        )
        assert isinstance(error, FlextDbOracleExceptions.QueryError)
        assert str(error) == "Query failed"
        assert error.context == {"sql": "SELECT 1"}

    def test_create_metadata_error(self) -> None:
        """Test create_metadata_error helper method."""
        error = FlextDbOracleExceptions.create_metadata_error(
            "Metadata missing", {"object": "INDEX"}
        )
        assert isinstance(error, FlextDbOracleExceptions.MetadataError)
        assert str(error) == "Metadata missing"
        assert error.context == {"object": "INDEX"}


class TestExceptionRaising:
    """Test that exceptions can be properly raised and caught."""

    def test_raise_validation_error(self) -> None:
        """Test raising and catching ValidationError."""
        with pytest.raises(FlextDbOracleExceptions.ValidationError) as exc_info:
            msg = "Test validation error"
            raise FlextDbOracleExceptions.ValidationError(msg)
        assert "Test validation error" in str(exc_info.value)

    def test_raise_configuration_error(self) -> None:
        """Test raising and catching ConfigurationError."""
        with pytest.raises(FlextDbOracleExceptions.ConfigurationError) as exc_info:
            msg = "Test config error"
            raise FlextDbOracleExceptions.ConfigurationError(msg)
        assert "Test config error" in str(exc_info.value)

    def test_exception_hierarchy(self) -> None:
        """Test that exceptions follow proper inheritance hierarchy."""
        validation_error = FlextDbOracleExceptions.ValidationError("Test")
        assert isinstance(validation_error, ValueError)
        assert isinstance(validation_error, Exception)

        config_error = FlextDbOracleExceptions.ConfigurationError("Test")
        assert isinstance(config_error, Exception)
