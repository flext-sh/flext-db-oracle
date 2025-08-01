"""Comprehensive tests for Oracle plugins with full coverage.

Tests for flext_db_oracle.plugins module covering all plugin functions
and business logic with complete code coverage.
"""

from __future__ import annotations

from unittest.mock import Mock

from flext_core import FlextResult
from flext_plugin import FlextPlugin

from flext_db_oracle.plugins import (
    ORACLE_PLUGINS,
    _validate_business_rules,
    _validate_data_types,
    create_data_validation_plugin,
    create_performance_monitor_plugin,
    create_security_audit_plugin,
    register_all_oracle_plugins,
)


class TestDataTypeValidation:
    """Test data type validation functions."""

    def test_validate_data_types_empty_data(self) -> None:
        """Test validation with empty data."""
        errors, warnings = _validate_data_types({})
        assert errors == []
        assert warnings == []

    def test_validate_data_types_varchar_length_warning(self) -> None:
        """Test VARCHAR length validation warnings."""
        data = {"name": "x" * 4001}  # Over 4000 char limit
        errors, warnings = _validate_data_types(data)
        assert errors == []
        assert len(warnings) == 1
        assert "exceeds VARCHAR2(4000) limit" in warnings[0]

    def test_validate_data_types_id_field_validation(self) -> None:
        """Test ID field type validation."""
        data = {
            "user_id": 123,  # Valid integer
            "account_id": "abc123",  # Valid string
            "invalid_id": ["list"],  # Invalid type
        }
        errors, warnings = _validate_data_types(data)
        assert len(errors) == 1
        assert "invalid_id should be numeric or string" in errors[0]
        assert warnings == []

    def test_validate_data_types_mixed_validations(self) -> None:
        """Test mixed validation scenarios."""
        data = {
            "name": "x" * 4001,  # Warning
            "description": "normal text",  # OK
            "user_id": 123,  # OK
            "bad_id": {"dict": "value"},  # Error
        }
        errors, warnings = _validate_data_types(data)
        assert len(errors) == 1
        assert len(warnings) == 1


class TestBusinessRulesValidation:
    """Test business rules validation functions."""

    def test_validate_business_rules_empty_data(self) -> None:
        """Test validation with empty data."""
        errors = _validate_business_rules({})
        assert errors == []

    def test_validate_business_rules_invalid_email(self) -> None:
        """Test email validation."""
        test_cases = [
            {"email": "invalid"},
            {"email": "no-at-sign.com"},
            {"email": "no-dot@domain"},
            {"email": ""},
        ]

        for data in test_cases:
            errors = _validate_business_rules(data)
            assert len(errors) == 1
            assert "Invalid email format" in errors[0]

    def test_validate_business_rules_valid_email(self) -> None:
        """Test valid email validation."""
        data = {"email": "user@example.com"}
        errors = _validate_business_rules(data)
        assert errors == []

    def test_validate_business_rules_age_validation(self) -> None:
        """Test age validation."""
        test_cases = [
            {"age": -1},  # Negative age
            {"age": 0},  # Zero age
            {"age": 151},  # Over 150 limit
        ]

        for data in test_cases:
            errors = _validate_business_rules(data)
            assert len(errors) == 1
            assert "Age must be between" in errors[0]

    def test_validate_business_rules_valid_age(self) -> None:
        """Test valid age validation."""
        data = {"age": 25}
        errors = _validate_business_rules(data)
        assert errors == []

    def test_validate_business_rules_table_name_length(self) -> None:
        """Test table name length validation."""
        data = {"table_name": "x" * 151}  # Over 150 char limit
        errors = _validate_business_rules(data)
        assert len(errors) == 1
        assert "Table name too long" in errors[0]

    def test_validate_business_rules_multiple_errors(self) -> None:
        """Test multiple business rule errors."""
        data = {
            "email": "invalid",
            "age": -1,
            "table_name": "x" * 151,
        }
        errors = _validate_business_rules(data)
        assert len(errors) == 3


class TestPluginCreation:
    """Test plugin creation functions."""

    def test_create_data_validation_plugin(self) -> None:
        """Test data validation plugin creation."""
        plugin_result = create_data_validation_plugin()

        assert plugin_result.is_success
        assert plugin_result.data is not None
        plugin = plugin_result.data
        assert isinstance(plugin, FlextPlugin)
        assert plugin.name == "oracle_data_validator"
        assert plugin.plugin_version == "0.9.0"

    def test_create_performance_monitor_plugin(self) -> None:
        """Test performance monitor plugin creation."""
        plugin_result = create_performance_monitor_plugin()

        assert plugin_result.is_success
        assert plugin_result.data is not None
        plugin = plugin_result.data
        assert isinstance(plugin, FlextPlugin)
        assert plugin.name == "oracle_performance_monitor"
        assert plugin.plugin_version == "0.9.0"

    def test_create_security_audit_plugin(self) -> None:
        """Test security audit plugin creation."""
        plugin_result = create_security_audit_plugin()

        assert plugin_result.is_success
        assert plugin_result.data is not None
        plugin = plugin_result.data
        assert isinstance(plugin, FlextPlugin)
        assert plugin.name == "oracle_security_audit"
        assert plugin.plugin_version == "0.9.0"


class TestPluginRegistration:
    """Test plugin registration functions."""

    def test_register_all_oracle_plugins_success(self) -> None:
        """Test successful registration of all Oracle plugins."""
        mock_api = Mock()
        mock_api.register_plugin.return_value = FlextResult.ok(None)

        result = register_all_oracle_plugins(mock_api)

        assert result.is_success
        assert mock_api.register_plugin.call_count == 3  # 3 plugins

    def test_register_all_oracle_plugins_failure(self) -> None:
        """Test failure in plugin registration."""
        mock_api = Mock()
        mock_api.register_plugin.return_value = FlextResult.fail("Registration failed")

        result = register_all_oracle_plugins(mock_api)

        assert result.is_success  # Function doesn't fail, just records errors
        # Check that plugins failed
        assert any("failed:" in status for status in result.data.values())

    def test_register_all_oracle_plugins_exception(self) -> None:
        """Test exception handling in plugin registration."""
        # Create a mock API that will cause registration to fail
        mock_api = Mock()
        mock_api.register_plugin.side_effect = Exception("Registration error")

        result = register_all_oracle_plugins(mock_api)

        assert result.is_success  # Function doesn't fail, just records errors
        # Check that at least one plugin failed
        assert any("error:" in status for status in result.data.values())


class TestOraclePluginsConstant:
    """Test ORACLE_PLUGINS constant."""

    def test_oracle_plugins_list_structure(self) -> None:
        """Test ORACLE_PLUGINS dictionary structure."""
        assert isinstance(ORACLE_PLUGINS, dict)
        assert len(ORACLE_PLUGINS) == 3

        # Check that all items are factory functions
        for factory_func in ORACLE_PLUGINS.values():
            assert callable(factory_func)
            # Test that calling the factory returns a FlextResult
            result = factory_func()
            assert result.is_success
            assert result.data is not None
            assert isinstance(result.data, FlextPlugin)

    def test_oracle_plugins_names(self) -> None:
        """Test that all expected plugin names are present."""
        expected_factory_keys = [
            "performance_monitor",
            "security_audit",
            "data_validator",
        ]

        for key in expected_factory_keys:
            assert key in ORACLE_PLUGINS

    def test_oracle_plugins_versions(self) -> None:
        """Test that all plugins have correct version."""
        for factory_func in ORACLE_PLUGINS.values():
            result = factory_func()
            assert result.is_success
            assert result.data is not None
            assert result.data.plugin_version == "0.9.0"


class TestPluginFunctionality:
    """Test plugin functional behavior."""

    def test_data_validation_plugin_execution(self) -> None:
        """Test data validation plugin creation and properties."""
        plugin_result = create_data_validation_plugin()
        assert plugin_result.is_success
        plugin = plugin_result.data

        # Test basic plugin properties
        assert plugin.name == "oracle_data_validator"
        assert plugin.plugin_version == "0.9.0"
        assert (
            plugin.description
            == "Validate data integrity and business rules for Oracle operations"
        )

    def test_performance_monitor_plugin_execution(self) -> None:
        """Test performance monitor plugin creation and properties."""
        plugin_result = create_performance_monitor_plugin()
        assert plugin_result.is_success
        plugin = plugin_result.data

        # Test basic plugin properties
        assert plugin.name == "oracle_performance_monitor"
        assert plugin.plugin_version == "0.9.0"
        assert (
            plugin.description
            == "Monitor Oracle database performance and identify slow queries"
        )

    def test_security_audit_plugin_execution(self) -> None:
        """Test security audit plugin creation and properties."""
        plugin_result = create_security_audit_plugin()
        assert plugin_result.is_success
        plugin = plugin_result.data

        # Test basic plugin properties
        assert plugin.name == "oracle_security_audit"
        assert plugin.plugin_version == "0.9.0"
        assert (
            plugin.description
            == "Security audit and compliance monitoring for Oracle operations"
        )

    def test_plugin_error_handling(self) -> None:
        """Test plugin creation doesn't fail."""
        plugin_result = create_data_validation_plugin()
        assert plugin_result.is_success
        plugin = plugin_result.data

        # Test basic plugin properties
        assert plugin.name == "oracle_data_validator"
        assert plugin.plugin_version == "0.9.0"
        assert (
            plugin.description
            == "Validate data integrity and business rules for Oracle operations"
        )


class TestEdgeCases:
    """Test edge cases and error conditions."""

    def test_validate_data_types_with_none_values(self) -> None:
        """Test validation with None values."""
        data = {"name": None, "user_id": None}
        errors, warnings = _validate_data_types(data)
        # None values should not cause errors for regular fields
        # but ID fields should be validated
        assert len(errors) == 1  # user_id should be numeric or string
        assert warnings == []

    def test_validate_business_rules_with_none_values(self) -> None:
        """Test business rules with None values."""
        data = {"email": None, "age": None}
        errors = _validate_business_rules(data)
        # None values should be handled gracefully
        assert len(errors) >= 1  # None email is invalid

    def test_validate_data_types_case_insensitive_id_fields(self) -> None:
        """Test that ID field validation is case insensitive."""
        data = {
            "USER_ID": 123,  # Uppercase
            "account_Id": "abc",  # Mixed case
            "bad_ID": ["invalid"],  # Invalid type
        }
        errors, warnings = _validate_data_types(data)
        assert len(errors) == 1  # Only bad_ID should error
        assert warnings == []
