"""Comprehensive tests for Oracle plugins with full coverage.

Tests for flext_db_oracle.plugins module covering all plugin functions
and business logic with complete code coverage.
"""

from __future__ import annotations

from unittest.mock import Mock, patch

from flext_core import FlextResult
from flext_plugin import FlextPlugin

from flext_db_oracle.plugins import (
    ORACLE_PLUGINS,
    OraclePluginHandler,
    _validate_business_rules,
    _validate_data_types,
    _validate_table_structure,
    create_data_validation_plugin,
    create_performance_monitor_plugin,
    create_security_audit_plugin,
    data_validation_plugin_handler,
    performance_monitor_plugin_handler,
    register_all_oracle_plugins,
    security_audit_plugin_handler,
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


class TestBusinessRulesMissingCoverage:
    """Test business rule validation missing coverage."""

    def test_validate_business_rules_email_edge_cases(self) -> None:
        """Test email validation edge cases."""
        # Test email missing @ symbol - line 51-55
        data = {"email": "invalid-email"}
        errors = _validate_business_rules(data)
        assert len(errors) == 1
        assert "Invalid email format" in errors[0]

    def test_validate_business_rules_age_exceptions(self) -> None:
        """Test age validation exception handling - lines 64-65."""
        # Test ValueError in age conversion
        data = {"age": "not-a-number"}
        errors = _validate_business_rules(data)
        assert len(errors) == 1
        assert "valid number" in errors[0]

        # Test None age - should be skipped, no error
        data = {"age": None}
        errors = _validate_business_rules(data)
        assert len(errors) == 0  # None values are skipped

    def test_validate_business_rules_table_name_checks(self) -> None:
        """Test table name validation - lines 67-72."""
        # Test table_name exists and not None
        data = {"table_name": "x" * 151}  # Over 150 char limit
        errors = _validate_business_rules(data)
        assert len(errors) == 1
        assert "too long" in errors[0]

        # Test table_name is None - should be skipped (line 67)
        data = {"table_name": None}
        errors = _validate_business_rules(data)
        assert len(errors) == 0

        # Test table_name not in data - should be skipped
        data = {"other_field": "value"}
        errors = _validate_business_rules(data)
        assert len(errors) == 0


class TestTableStructureMissingCoverage:
    """Test table structure validation missing coverage."""

    def test_validate_table_structure_exception_handling(self) -> None:
        """Test exception handling in table validation - lines 100-105."""
        mock_api = Mock()

        # Mock exception during get_tables call
        mock_api.get_tables.side_effect = Exception("Database connection failed")

        # Should not raise exception, just return empty errors
        errors = _validate_table_structure("test_table", mock_api)
        assert errors == []

    def test_validate_table_structure_mixed_objects(self) -> None:
        """Test table structure with mixed object types - lines 94-98."""
        mock_api = Mock()

        # Mock tables with mixed types
        mock_table_obj = Mock()
        mock_table_obj.name = "TABLE_WITH_NAME"

        # Mix of objects with .name and plain strings
        mock_api.get_tables.return_value = FlextResult.ok(
            [
                mock_table_obj,  # Has .name attribute
                "PLAIN_STRING_TABLE",  # Plain string
                42,  # Number (will be converted to string)
            ],
        )

        # Test finding table with .name attribute
        errors = _validate_table_structure("table_with_name", mock_api)
        assert errors == []

        # Test finding plain string table
        errors = _validate_table_structure("plain_string_table", mock_api)
        assert errors == []

        # Test finding number table
        errors = _validate_table_structure("42", mock_api)
        assert errors == []

    def test_validate_table_structure_edge_cases(self) -> None:
        """Test table structure validation edge cases."""
        mock_api = Mock()

        # Test with None table_name - should return empty errors (line 82-83)
        errors = _validate_table_structure(None, mock_api)
        assert errors == []

        # Test with empty string table_name
        errors = _validate_table_structure("", mock_api)
        assert errors == []

        # Test with very long table name (line 85-88)
        long_name = "x" * 151  # Over MAX_TABLE_NAME_LENGTH (150)
        errors = _validate_table_structure(long_name, mock_api)
        assert len(errors) == 1
        assert "exceeds maximum length" in errors[0]

        # Test table not found case (line 98-99)
        mock_api.get_tables.return_value = FlextResult.ok(["OTHER_TABLE"])
        errors = _validate_table_structure("MISSING_TABLE", mock_api)
        assert len(errors) == 1
        assert "does not exist" in errors[0]


class TestPluginHandlersMissingCoverage:
    """Test missing coverage in plugin handlers."""

    def test_performance_monitor_slow_query_detection(self) -> None:
        """Test slow query detection logic - lines 250-270."""
        mock_api = Mock()
        mock_api._observability.get_current_timestamp.return_value = (
            "2025-01-01T12:00:00"
        )

        # Test slow query detection
        result = performance_monitor_plugin_handler(
            mock_api,
            sql="SELECT * FROM large_table",
            execution_time_ms=2000.0,
            threshold_ms=1000,
        )

        assert result.is_success
        data = result.data
        assert data["is_slow_query"] is True
        assert "database indexes" in str(data["recommendations"]) or "Add index" in str(
            data["recommendations"],
        )
        assert len(data["recommendations"]) > 0

    def test_data_validation_handler_all_paths(self) -> None:
        """Test data validation handler all execution paths - lines 290-320."""
        mock_api = Mock()
        mock_api._observability.get_current_timestamp.return_value = (
            "2025-01-01T12:00:00"
        )

        # Test with data that has both errors and warnings
        test_data = {
            "email": "invalid-email",  # Will cause error
            "name": "x" * 4001,  # Will cause warning (over VARCHAR limit)
            "age": -5,  # Will cause error
            "user_id": ["invalid"],  # Will cause error
        }

        result = data_validation_plugin_handler(mock_api, data=test_data)

        assert result.is_success
        data = result.data
        assert data["validation_status"] == "invalid"
        assert len(data["validation_errors"]) >= 3  # email, age, user_id errors
        assert len(data["validation_warnings"]) >= 1  # name warning

    def test_data_validation_handler_branch_coverage(self) -> None:
        """Test data validation handler branch coverage - lines 380-397."""
        mock_api = Mock()
        mock_api._observability.get_current_timestamp.return_value = (
            "2025-01-01T12:00:00"
        )

        # Test with validate_data_types=False (line 380)
        result = data_validation_plugin_handler(
            mock_api,
            data={"test": "data"},
            validate_data_types=False,
        )
        assert result.is_success

        # Test with enforce_business_rules=False (line 385)
        result = data_validation_plugin_handler(
            mock_api,
            data={"test": "data"},
            enforce_business_rules=False,
        )
        assert result.is_success

        # Test with no data provided (line 380-385)
        result = data_validation_plugin_handler(mock_api, data=None)
        assert result.is_success
        assert result.data["validation_status"] == "valid"

        # Test validation_status = "warning" path (line 396-397)
        result = data_validation_plugin_handler(
            mock_api,
            data={"name": "x" * 4001},  # Only warning, no errors
        )
        assert result.is_success
        assert result.data["validation_status"] == "warning"

    def test_security_audit_handler_basic_functionality(self) -> None:
        """Test security audit handler basic functionality - lines 283-320."""
        mock_api = Mock()
        mock_api._observability.get_current_timestamp.return_value = (
            "2025-01-01T12:00:00"
        )

        # Test basic security audit
        result = security_audit_plugin_handler(
            mock_api,
            sql="SELECT * FROM users",
            operation_type="SELECT",
        )
        assert result.is_success
        assert result.data["plugin_name"] == "oracle_security_audit"
        assert result.data["sql"] == "SELECT * FROM users"
        assert result.data["operation_type"] == "SELECT"
        assert "security_warnings" in result.data
        assert "compliance_status" in result.data

    def test_security_audit_handler_sql_injection_detection(self) -> None:
        """Test security audit SQL injection detection."""
        mock_api = Mock()
        mock_api._observability.get_current_timestamp.return_value = (
            "2025-01-01T12:00:00"
        )

        # Test with potentially dangerous SQL
        dangerous_sql = "SELECT * FROM users WHERE id = 1; DROP TABLE users;"
        result = security_audit_plugin_handler(
            mock_api,
            sql=dangerous_sql,
            check_sql_injection=True,
        )
        assert result.is_success
        # Should detect security warnings
        assert len(result.data["security_warnings"]) >= 1
        assert "DROP TABLE" in str(result.data["security_warnings"])

    def test_plugin_handler_exception_coverage(self) -> None:
        """Test plugin handler exception handling - lines 274-275, 346-347, 401-402."""
        mock_api = Mock()
        # Force TypeError in performance monitor by making _observability raise exception
        mock_api._observability.get_current_timestamp.side_effect = TypeError(
            "Timestamp error",
        )

        # Test performance monitor exception
        result = performance_monitor_plugin_handler(mock_api, sql="SELECT 1")
        assert result.is_failure
        assert "Performance monitor plugin failed" in result.error

        # Test security audit exception
        result = security_audit_plugin_handler(mock_api, sql="SELECT 1")
        assert result.is_failure
        assert "Security audit plugin failed" in result.error

        # Test data validation exception
        result = data_validation_plugin_handler(mock_api, data={"test": "data"})
        assert result.is_failure
        assert "Data validation plugin failed" in result.error

    def test_registration_edge_cases(self) -> None:
        """Test plugin registration edge cases - lines 430-432."""
        from flext_db_oracle.plugins import register_all_oracle_plugins

        mock_api = Mock()

        # Test case where plugin creation succeeds but plugin is None
        def mock_creator_none() -> FlextResult[None]:
            return FlextResult.ok(None)

        # Patch ORACLE_PLUGINS to include our test creator
        with patch(
            "flext_db_oracle.plugins.ORACLE_PLUGINS",
            {"test_plugin": mock_creator_none},
        ):
            result = register_all_oracle_plugins(mock_api)
            assert result.is_success
            assert "failed: plugin is None" in result.data["test_plugin"]


class TestOraclePluginHandlerMethods:
    """Test OraclePluginHandler methods missing coverage."""

    def test_create_base_result_data_basic(self) -> None:
        """Test basic result data creation."""
        mock_api = Mock()
        mock_api._observability.get_current_timestamp.return_value = (
            "2025-01-01T12:00:00"
        )

        result = OraclePluginHandler.create_base_result_data("test_plugin", mock_api)

        assert result["plugin_name"] == "test_plugin"
        assert result["timestamp"] == "2025-01-01T12:00:00"

    def test_create_base_result_data_with_additional_fields(self) -> None:
        """Test result data creation with additional fields."""
        mock_api = Mock()
        mock_api._observability.get_current_timestamp.return_value = (
            "2025-01-01T12:00:00"
        )

        additional = {"status": "success", "count": 42}
        result = OraclePluginHandler.create_base_result_data(
            "test_plugin",
            mock_api,
            additional,
        )

        assert result["plugin_name"] == "test_plugin"
        assert result["timestamp"] == "2025-01-01T12:00:00"
        assert result["status"] == "success"
        assert result["count"] == 42

    def test_handle_plugin_exception(self) -> None:
        """Test plugin exception handling."""
        test_exception = ValueError("Test error message")
        result = OraclePluginHandler.handle_plugin_exception(
            test_exception,
            "test_plugin",
        )

        assert result.is_failure
        assert "test_plugin plugin failed: Test error message" in result.error


class TestFactoryMethodsMissingCoverage:
    """Test factory methods missing coverage."""

    def test_plugin_creation_functions(self) -> None:
        """Test plugin creation functions that actually exist."""
        # Test all plugin creation functions work
        data_validation = create_data_validation_plugin()
        assert data_validation.is_success

        performance_monitor = create_performance_monitor_plugin()
        assert performance_monitor.is_success

        security_audit = create_security_audit_plugin()
        assert security_audit.is_success

    def test_oracle_plugin_factory_edge_cases(self) -> None:
        """Test OraclePluginFactory edge cases for missing coverage."""
        from flext_db_oracle.plugins import OraclePluginFactory

        # Test direct factory methods
        factory = OraclePluginFactory()

        # Test create_plugin_template with different configurations
        result = factory._create_plugin_template(
            name="test_plugin",
            description="Test plugin description",
            plugin_type="test",
            specific_config={"custom_param": "custom_value"},
        )
        assert result.is_success
        plugin = result.data
        assert plugin.name == "test_plugin"
        assert plugin.plugin_version == "0.9.0"

    def test_oracle_plugin_handler_edge_cases(self) -> None:
        """Test OraclePluginHandler edge cases for missing coverage."""
        from flext_db_oracle.plugins import OraclePluginHandler

        # Test create_base_result_data with None additional_fields
        mock_api = Mock()
        mock_api._observability.get_current_timestamp.return_value = (
            "2025-01-01T12:00:00"
        )

        result = OraclePluginHandler.create_base_result_data(
            "test_plugin",
            mock_api,
            None,
        )
        assert result["plugin_name"] == "test_plugin"
        assert result["timestamp"] == "2025-01-01T12:00:00"

        # Test various exception types
        test_exceptions = [
            ValueError("Value error"),
            TypeError("Type error"),
            AttributeError("Attribute error"),
            Exception("Generic error"),
        ]

        for exc in test_exceptions:
            result = OraclePluginHandler.handle_plugin_exception(exc, "test_plugin")
            assert result.is_failure
            assert "test_plugin plugin failed:" in result.error
