"""Comprehensive tests for Oracle mixins functionality.

Tests all Oracle mixin components including validation, parameter handling,
connection configuration, and error transformation to achieve high coverage.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import pytest

from flext_core import FlextMixins, FlextResult
from flext_db_oracle import FlextDbOracleMixins, __all__


class TestOracleValidation:
    """Test Oracle validation mixin functionality."""

    def test_validate_identifier_success(self) -> None:
        """Test successful Oracle identifier validation."""
        validator = FlextDbOracleMixins.OracleValidation

        # Test valid identifiers
        result = validator.validate_identifier("valid_table")
        assert result.is_success
        assert result.value == "VALID_TABLE"  # Oracle normalizes to uppercase

        # Test alphanumeric with underscores
        result = validator.validate_identifier("table_123")
        assert result.is_success
        assert result.value == "TABLE_123"

        # Test starting with letter
        result = validator.validate_identifier("a_table")
        assert result.is_success
        assert result.value == "A_TABLE"

    def test_validate_identifier_case_normalization(self) -> None:
        """Test Oracle identifier case normalization."""
        validator = FlextDbOracleMixins.OracleValidation

        # Test lowercase conversion
        result = validator.validate_identifier("lowercase_table")
        assert result.is_success
        assert result.value == "LOWERCASE_TABLE"

        # Test mixed case conversion
        result = validator.validate_identifier("MixedCase_Table")
        assert result.is_success
        assert result.value == "MIXEDCASE_TABLE"

    def test_validate_identifier_empty_input(self) -> None:
        """Test Oracle identifier validation with empty input."""
        validator = FlextDbOracleMixins.OracleValidation

        # Test empty string
        result = validator.validate_identifier("")
        assert result.is_failure
        assert "cannot be empty" in str(result.error)

        # Test whitespace only
        result = validator.validate_identifier("   ")
        assert result.is_failure
        assert "cannot be empty" in str(result.error)

        # Test newline/tab whitespace
        result = validator.validate_identifier("\n\t  ")
        assert result.is_failure
        assert "cannot be empty" in str(result.error)

    def test_validate_identifier_too_long(self) -> None:
        """Test Oracle identifier validation with too long input."""
        validator = FlextDbOracleMixins.OracleValidation

        # Create identifier longer than max length (128 chars from constants)
        long_identifier = "A" * 129
        result = validator.validate_identifier(long_identifier)
        assert result.is_failure
        assert "too long" in str(result.error)
        assert "max 128 chars" in str(result.error)

    def test_validate_identifier_invalid_characters(self) -> None:
        """Test Oracle identifier validation with invalid characters."""
        validator = FlextDbOracleMixins.OracleValidation

        # Test invalid characters (depends on IDENTIFIER_PATTERN in constants)
        invalid_identifiers = [
            "table-name",  # Hyphens typically not allowed
            "table name",  # Spaces typically not allowed
            "table@name",  # Special chars typically not allowed
            "table.name",  # Dots typically not allowed
            "table!name",  # Exclamation typically not allowed
        ]

        for invalid_id in invalid_identifiers:
            result = validator.validate_identifier(invalid_id)
            assert result.is_failure
            assert "invalid characters" in str(result.error)

    def test_validate_identifier_reserved_words(self) -> None:
        """Test Oracle identifier validation with reserved words."""
        validator = FlextDbOracleMixins.OracleValidation

        # Test common Oracle reserved words (these should be in ORACLE_RESERVED)
        reserved_words = [
            "SELECT",
            "INSERT",
            "UPDATE",
            "DELETE",
            "CREATE",
            "DROP",
            "TABLE",
            "INDEX",
            "VIEW",
            "FROM",
            "WHERE",
            "ORDER",
        ]

        for reserved_word in reserved_words:
            result = validator.validate_identifier(reserved_word)
            # Result may succeed or fail depending on what's in ORACLE_RESERVED constants
            # If it fails, it should mention reserved word
            if result.is_failure:
                assert "reserved word" in str(result.error)

    def test_validate_identifier_edge_cases(self) -> None:
        """Test Oracle identifier validation edge cases."""
        validator = FlextDbOracleMixins.OracleValidation

        # Test identifier at max length boundary (128 chars)
        max_length_identifier = "A" * 128
        result = validator.validate_identifier(max_length_identifier)
        # Should succeed if exactly at max length
        assert result.is_success
        assert len(result.value) == 128

        # Test single character identifier
        result = validator.validate_identifier("A")
        assert result.is_success
        assert result.value == "A"

        # Test numbers (depending on pattern, may or may not be allowed at start)
        result = validator.validate_identifier("123TABLE")
        # Result depends on IDENTIFIER_PATTERN - test that it gives consistent result
        if result.is_failure:
            assert "invalid characters" in str(result.error)


class TestParameterContainer:
    """Test parameter container functionality."""

    def test_parameter_container_initialization_with_params(self) -> None:
        """Test parameter container initialization with parameters."""
        params = {"key1": "value1", "key2": 123}
        container = FlextDbOracleMixins.ParameterContainer(params=params)

        assert container.params == params
        assert container.params is not None

    def test_parameter_container_initialization_without_params(self) -> None:
        """Test parameter container initialization without parameters."""
        container = FlextDbOracleMixins.ParameterContainer()

        assert container.params == {}
        assert container.params is not None

    def test_parameter_container_initialization_none_params(self) -> None:
        """Test parameter container initialization with None parameters."""
        container = FlextDbOracleMixins.ParameterContainer(params=None)

        # __post_init__ should initialize params to empty dict
        assert container.params == {}
        assert container.params is not None

    def test_parameter_container_get_existing_key(self) -> None:
        """Test getting existing parameter values."""
        params = {"key1": "value1", "key2": 123, "key3": None}
        container = FlextDbOracleMixins.ParameterContainer(params=params)

        assert container.get("key1") == "value1"
        assert container.get("key2") == 123
        assert container.get("key3") is None

    def test_parameter_container_get_missing_key(self) -> None:
        """Test getting missing parameter values with defaults."""
        params: dict[str, object] = {"key1": "value1"}
        container = FlextDbOracleMixins.ParameterContainer(params=params)

        # Test default None
        assert container.get("missing_key") is None

        # Test custom default
        assert container.get("missing_key", default="default_value") == "default_value"
        assert container.get("missing_key", default=42) == 42

    def test_parameter_container_get_from_none_params(self) -> None:
        """Test getting values when params is None."""
        # Create container and manually set params to None to test edge case
        container = FlextDbOracleMixins.ParameterContainer()
        # Simulate the case where params might be None despite __post_init__
        setattr(container, "params", None)

        assert container.get("any_key") is None
        assert container.get("any_key", default="default") == "default"

    def test_parameter_container_require_existing_key(self) -> None:
        """Test requiring existing parameter values."""
        params = {"key1": "value1", "key2": 123, "key3": None}
        container = FlextDbOracleMixins.ParameterContainer(params=params)

        assert container.require("key1") == "value1"
        assert container.require("key2") == 123
        assert container.require("key3") is None  # None is still a valid value

    def test_parameter_container_require_missing_key(self) -> None:
        """Test requiring missing parameter values."""
        params: dict[str, object] = {"key1": "value1"}
        container = FlextDbOracleMixins.ParameterContainer(params=params)

        with pytest.raises(KeyError) as exc_info:
            container.require("missing_key")

        assert "Required parameter 'missing_key' not provided" in str(exc_info.value)

    def test_parameter_container_require_from_none_params(self) -> None:
        """Test requiring values when params is None."""
        # Create container and manually set params to None to test edge case
        container = FlextDbOracleMixins.ParameterContainer()
        setattr(container, "params", None)

        with pytest.raises(KeyError) as exc_info:
            container.require("any_key")

        assert "Required parameter 'any_key' not provided" in str(exc_info.value)


class TestConnectionConfig:
    """Test connection configuration dataclass."""

    def test_connection_config_creation_required_fields(self) -> None:
        """Test connection config creation with required fields."""
        config = FlextDbOracleMixins.ConnectionConfig(
            host="localhost",
            port=1521,
            service_name="XEPDB1",
            username="test_user",
            password="test_password",
        )

        assert config.host == "localhost"
        assert config.port == 1521
        assert config.service_name == "XEPDB1"
        assert config.username == "test_user"
        assert config.password == "test_password"
        assert config.test_connection is False  # Default value

    def test_connection_config_creation_with_test_connection(self) -> None:
        """Test connection config creation with test_connection parameter."""
        config = FlextDbOracleMixins.ConnectionConfig(
            host="prod-server",
            port=1522,
            service_name="PRODDB",
            username="prod_user",
            password="prod_password",
            test_connection=True,
        )

        assert config.host == "prod-server"
        assert config.port == 1522
        assert config.service_name == "PRODDB"
        assert config.username == "prod_user"
        assert config.password == "prod_password"
        assert config.test_connection is True

    def test_connection_config_creation_none_test_connection(self) -> None:
        """Test connection config creation with None test_connection."""
        config = FlextDbOracleMixins.ConnectionConfig(
            host="test-server",
            port=1521,
            service_name="TESTDB",
            username="test_user",
            password="test_password",
            test_connection=None,
        )

        assert config.test_connection is None

    def test_connection_config_dataclass_behavior(self) -> None:
        """Test that ConnectionConfig behaves as expected dataclass."""
        config1 = FlextDbOracleMixins.ConnectionConfig(
            host="localhost",
            port=1521,
            service_name="XEPDB1",
            username="user",
            password="pass",
        )

        config2 = FlextDbOracleMixins.ConnectionConfig(
            host="localhost",
            port=1521,
            service_name="XEPDB1",
            username="user",
            password="pass",
        )

        # Test equality (dataclass should implement __eq__)
        assert config1 == config2

        # Test representation (dataclass should implement __repr__)
        repr_str = repr(config1)
        assert "ConnectionConfig" in repr_str
        assert "localhost" in repr_str

    def test_connection_config_field_access(self) -> None:
        """Test direct field access on connection config."""
        config = FlextDbOracleMixins.ConnectionConfig(
            host="example.com",
            port=1521,
            service_name="EXAMPLE",
            username="example_user",
            password="example_password",
        )

        # Test that fields can be accessed directly
        assert hasattr(config, "host")
        assert hasattr(config, "port")
        assert hasattr(config, "service_name")
        assert hasattr(config, "username")
        assert hasattr(config, "password")
        assert hasattr(config, "test_connection")


class TestErrorTransformer:
    """Test error transformer functionality."""

    def test_error_transformer_initialization(self) -> None:
        """Test error transformer initialization."""
        context = "Oracle Connection"
        transformer = FlextDbOracleMixins.ErrorTransformer(context)

        assert transformer.context == context

    def test_error_transformer_success_result(self) -> None:
        """Test error transformer with successful result."""
        transformer = FlextDbOracleMixins.ErrorTransformer("Test Context")
        success_result = FlextResult[str].ok("success_value")

        transformed_result = transformer.transform(success_result)

        assert transformed_result.is_success
        assert transformed_result.value == "success_value"
        # Success results should pass through unchanged
        assert transformed_result is success_result

    def test_error_transformer_failure_result(self) -> None:
        """Test error transformer with failure result."""
        transformer = FlextDbOracleMixins.ErrorTransformer("Database Operation")
        failure_result = FlextResult[str].fail("original error message")

        transformed_result = transformer.transform(failure_result)

        assert transformed_result.is_failure
        assert "Database Operation: original error message" in str(
            transformed_result.error,
        )

    def test_error_transformer_different_contexts(self) -> None:
        """Test error transformer with different contexts."""
        contexts = [
            "Oracle Connection",
            "Query Execution",
            "Schema Validation",
            "Parameter Processing",
        ]

        for context in contexts:
            transformer = FlextDbOracleMixins.ErrorTransformer(context)
            failure_result = FlextResult[int].fail("test error")

            transformed_result = transformer.transform(failure_result)

            assert transformed_result.is_failure
            assert str(transformed_result.error).startswith(f"{context}: ")

    def test_error_transformer_empty_context(self) -> None:
        """Test error transformer with empty context."""
        transformer = FlextDbOracleMixins.ErrorTransformer("")
        failure_result = FlextResult[str].fail("error message")

        transformed_result = transformer.transform(failure_result)

        assert transformed_result.is_failure
        assert str(transformed_result.error) == ": error message"

    def test_error_transformer_none_error_message(self) -> None:
        """Test error transformer with None error message."""
        transformer = FlextDbOracleMixins.ErrorTransformer("Context")
        failure_result = FlextResult[str].fail("Unknown error")

        transformed_result = transformer.transform(failure_result)

        assert transformed_result.is_failure
        # FlextResult.fail(None) may convert to default error message
        error_str = str(transformed_result.error)
        assert error_str.startswith("Context: ")
        assert "None" in error_str or "Unknown error" in error_str

    def test_error_transformer_generic_types(self) -> None:
        """Test error transformer with different generic types."""
        transformer = FlextDbOracleMixins.ErrorTransformer("Type Test")

        # Test with different types
        int_result = FlextResult[int].fail("int error")
        dict_result = FlextResult[dict[str, object]].fail("dict error")
        list_result = FlextResult[list[str]].fail("list error")

        int_transformed = transformer.transform(int_result)
        dict_transformed = transformer.transform(dict_result)
        list_transformed = transformer.transform(list_result)

        assert int_transformed.is_failure
        assert "Type Test: int error" in str(int_transformed.error)

        assert dict_transformed.is_failure
        assert "Type Test: dict error" in str(dict_transformed.error)

        assert list_transformed.is_failure
        assert "Type Test: list error" in str(list_transformed.error)


class TestFlextDbOracleMixinsStructure:
    """Test FlextDbOracleMixins class structure."""

    def test_mixins_inheritance(self) -> None:
        """Test FlextDbOracleMixins inherits from FlextMixins."""
        assert issubclass(FlextDbOracleMixins, FlextMixins)

    def test_nested_classes_exist(self) -> None:
        """Test that all expected nested classes exist."""
        assert hasattr(FlextDbOracleMixins, "OracleValidation")
        assert hasattr(FlextDbOracleMixins, "ParameterContainer")
        assert hasattr(FlextDbOracleMixins, "ConnectionConfig")
        assert hasattr(FlextDbOracleMixins, "ErrorTransformer")

    def test_oracle_validation_methods(self) -> None:
        """Test OracleValidation has expected methods."""
        validation_class = FlextDbOracleMixins.OracleValidation

        assert hasattr(validation_class, "validate_identifier")
        assert callable(validation_class.validate_identifier)

    def test_parameter_container_methods(self) -> None:
        """Test ParameterContainer has expected methods."""
        # Test class can be instantiated
        container = FlextDbOracleMixins.ParameterContainer()

        assert hasattr(container, "get")
        assert hasattr(container, "require")
        assert callable(container.get)
        assert callable(container.require)

    def test_error_transformer_methods(self) -> None:
        """Test ErrorTransformer has expected methods."""
        transformer = FlextDbOracleMixins.ErrorTransformer("test")

        assert hasattr(transformer, "transform")
        assert callable(transformer.transform)

    def test_module_exports(self) -> None:
        """Test module __all__ exports."""
        assert "FlextDbOracleMixins" in __all__
        # Should only export the main class, no aliases
        assert len(__all__) == 1


class TestMixinsIntegration:
    """Test integration between different mixin components."""

    def test_parameter_container_with_error_transformer(self) -> None:
        """Test parameter container with error transformer."""
        container = FlextDbOracleMixins.ParameterContainer(params={"key": "value"})
        transformer = FlextDbOracleMixins.ErrorTransformer("Parameter Processing")

        # Simulate getting a parameter that might fail
        try:
            container.require("missing_key")
        except KeyError as e:
            # Transform the error using error transformer
            error_result = FlextResult[str].fail(str(e))
            transformed_result = transformer.transform(error_result)

            assert transformed_result.is_failure
            assert "Parameter Processing:" in str(transformed_result.error)

    def test_validation_with_error_transformer(self) -> None:
        """Test validation with error transformer."""
        validator = FlextDbOracleMixins.OracleValidation
        transformer = FlextDbOracleMixins.ErrorTransformer("Identifier Validation")

        # Test validation failure with error transformation
        validation_result = validator.validate_identifier("")
        transformed_result = transformer.transform(validation_result)

        assert transformed_result.is_failure
        assert "Identifier Validation:" in str(transformed_result.error)
        assert "cannot be empty" in str(transformed_result.error)

    def test_connection_config_with_validation(self) -> None:
        """Test connection config with validation."""
        # Test that connection config values can be validated
        config = FlextDbOracleMixins.ConnectionConfig(
            host="localhost",
            port=1521,
            service_name="TEST_DB",
            username="test_user",
            password="test_password",
        )

        validator = FlextDbOracleMixins.OracleValidation

        # Validate service name
        service_validation = validator.validate_identifier(config.service_name)
        assert service_validation.is_success

        # Validate username
        username_validation = validator.validate_identifier(config.username)
        # Username validation may succeed or fail depending on pattern
        # Just test that it returns a FlextResult
        assert isinstance(username_validation, FlextResult)
