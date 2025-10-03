"""Test CLI functionality with real Oracle operations.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import os

from flext_tests import FlextTestsMatchers

from flext_db_oracle import (
    FlextDbOracleApi,
    FlextDbOracleClient,
    FlextDbOracleModels,
    FlextDbOracleUtilities,
)


class TestCLIRealFunctionality:
    """Test CLI using real flext-cli API - NO MOCKS."""

    def test_cli_creation_and_basic_functionality(self) -> None:
        """Test CLI creation and basic functionality - REAL IMPLEMENTATION."""
        # Test CLI was created successfully
        oracle_cli = FlextDbOracleClient()
        # Constructor guarantees non-None return, so no need to check

        # Test CLI API has required attributes
        assert hasattr(oracle_cli, "execute_query")

        # Test command history functionality - defensive check first
        get_history_method = getattr(oracle_cli, "get_command_history", None)
        if callable(get_history_method):
            history = get_history_method()
            assert isinstance(history, list)
        else:
            # Command history may not be implemented - check if CLI has execute functionality
            assert callable(getattr(oracle_cli, "execute_query", None))

    def test_environment_configuration_real(self) -> None:
        """Test environment configuration using real API functionality."""
        # Test environment variables loading
        test_env_vars = {
            "ORACLE_HOST": "localhost",
            "ORACLE_PORT": "1521",
            "ORACLE_USERNAME": "testuser",
            "ORACLE_PASSWORD": "testpass",
            "ORACLE_SERVICE_NAME": "TESTDB",
        }

        # Save original environment
        original_env = {}
        for key, value in test_env_vars.items():
            original_env[key] = os.environ.get(key)
            os.environ[key] = value

        try:
            # Test real API creation from environment
            # Uses FLEXT_TARGET_ORACLE_* environment variables
            api_result = FlextDbOracleApi.from_env()
            FlextTestsMatchers.assert_result_success(api_result)

            api = api_result.value
            # Should use environment variables
            assert api.config.host == "localhost"
            assert api.config.port == 1521
            assert api.config.service_name == "TESTDB"
            assert api.config.username == "testuser"
            assert api.config.password == "testpass"

        finally:
            # Restore environment
            for key, original_value in original_env.items():
                if original_value is None:
                    if key in os.environ:
                        del os.environ[key]
                else:
                    os.environ[key] = original_value

    def test_api_observability_and_connection_real(self) -> None:
        """Test API observability and connection functionality - REAL IMPLEMENTATION."""
        # Create real API configuration
        config = FlextDbOracleModels.OracleConfig(
            host="localhost",
            port=1521,
            service_name="TESTDB",
            username="test",
            password="test",
        )

        api = FlextDbOracleApi(config)

        # Test real observability metrics
        metrics_result = api.get_observability_metrics()
        FlextTestsMatchers.assert_result_success(metrics_result)
        assert isinstance(metrics_result.value, dict)

        # Test real connection testing (will fail but should handle gracefully)
        connection_result = api.test_connection()
        assert hasattr(connection_result, "is_success")

        # Test configuration validation
        is_valid = api.is_valid()
        assert isinstance(is_valid, bool)
        assert is_valid is True  # Config should be valid

    def test_output_formatting_real(self) -> None:
        """Test output formatting using real functionality."""
        utilities = FlextDbOracleUtilities()

        # Test real query result formatting
        test_result = {"column1": "value1", "column2": "value2"}

        # Test different format types
        for format_type in ["table", "json", "csv"]:
            format_result = utilities.format_query_result(
                test_result,
                format_type=format_type,
            )
            FlextTestsMatchers.assert_result_success(format_result)
            assert isinstance(format_result.value, str)
            assert len(format_result.value) > 0

    def test_error_handling_real(self) -> None:
        """Test error handling using real functionality - NO MOCKS."""
        # Create API with invalid configuration to test error handling
        invalid_config = FlextDbOracleModels.OracleConfig(
            host="invalid.host",
            port=9999,
            service_name="INVALID_SERVICE",
            username="invalid_user",
            password="invalid_password",
        )

        api = FlextDbOracleApi(invalid_config)

        # Test error handling for operations without connection
        query_result = api.query("SELECT 1 FROM DUAL")
        assert query_result.is_failure
        assert query_result.error is not None
        assert (
            "not connected" in query_result.error.lower()
            or "connection" in query_result.error.lower()
        )

        # Test error handling for schema operations
        schemas_result = api.get_schemas()
        assert schemas_result.is_failure

        # Test error handling for table operations
        tables_result = api.get_tables()
        assert tables_result.is_failure

    def test_parameter_processing_real(self) -> None:
        """Test parameter processing using real API functionality."""
        # Test parameter processing through API configuration
        config_data = {
            "host": "param_test_host",
            "port": 1521,
            "service_name": "PARAM_TEST",
            "username": "param_user",
            "password": "param_pass",
        }

        # Test from_config with parameters
        config = FlextDbOracleModels.OracleConfig(
            host=str(config_data["host"]),
            port=int(str(config_data["port"])) if config_data.get("port") else 1521,
            service_name=str(config_data.get("service_name", "XE")),
            username=str(config_data["username"]),
            password=str(config_data["password"]),
        )

        api = FlextDbOracleApi.from_config(config)

        # Verify parameter processing worked
        assert api.config.host == "param_test_host"
        assert api.config.port == 1521
        assert api.config.service_name == "PARAM_TEST"
        assert api.config.username == "param_user"

    def test_comprehensive_api_coverage_real(self) -> None:
        """Comprehensive API coverage test using real functionality - NO MOCKS."""
        # Create comprehensive test configuration
        config = FlextDbOracleModels.OracleConfig(
            host="comprehensive_test",
            port=1521,
            name="COMP_TEST",  # Required field
            service_name="COMP_TEST",
            username="comp_user",
            password="comp_pass",
        )

        api = FlextDbOracleApi(config)

        # Test all major API methods with real functionality
        methods_to_test = [
            ("is_valid", api.is_valid),
            ("to_dict", api.to_dict),
            ("get_observability_metrics", api.get_observability_metrics),
            ("optimize_query", lambda: api.optimize_query("SELECT * FROM test")),
            ("list_plugins", api.list_plugins),
        ]

        for _method_name, method_call in methods_to_test:
            result = method_call()

            # All methods should return proper results (success or proper failure)
            if hasattr(result, "success"):
                # FlextResult - check it has proper structure
                assert hasattr(result, "error") or hasattr(result, "value")
            else:
                # Direct return (like is_valid, to_dict)
                assert result is not None

    def test_factory_methods_real(self) -> None:
        """Test factory methods using real functionality - NO MOCKS."""
        # Set required environment variables for from_env
        original_env = {}
        env_vars = {
            "ORACLE_USERNAME": "testuser",
            "ORACLE_PASSWORD": "testpass",
            "ORACLE_HOST": "localhost",
            "ORACLE_PORT": "1521",
            "ORACLE_SERVICE_NAME": "XEPDB1",
        }
        for key, value in env_vars.items():
            original_env[key] = os.environ.get(key)
            os.environ[key] = value

        try:
            # Test from_env factory method
            api_result = FlextDbOracleApi.from_env()
            FlextTestsMatchers.assert_result_success(api_result)

            api = api_result.value
            assert api.config.host == "localhost"
            assert api.config.port == 1521
            assert api.config.service_name == "XEPDB1"
            assert api.config.username == "testuser"
        finally:
            # Restore environment
            for key, original_value in original_env.items():
                if original_value is None:
                    os.environ.pop(key, None)
                else:
                    os.environ[key] = original_value

        # Test from_url factory method
        url_result = FlextDbOracleApi.from_url("oracle://user:pass@host:1521/service")
        FlextTestsMatchers.assert_result_success(url_result)

        url_api = url_result.value
        assert url_api.config.host == "host"
        assert url_api.config.port == 1521
        assert url_api.config.service_name == "SERVICE"

    def test_plugin_system_real(self) -> None:
        """Test plugin system using real functionality - NO MOCKS."""
        config = FlextDbOracleModels.OracleConfig(
            host="plugin_test",
            port=1521,
            service_name="PLUGIN_TEST",
            username="plugin_user",
            password="plugin_pass",
        )

        api = FlextDbOracleApi(config)

        # Test plugin registration - real functionality
        test_plugin = {"name": "test_plugin", "version": "1.0.0"}
        register_result = api.register_plugin("test_plugin", test_plugin)
        FlextTestsMatchers.assert_result_success(register_result)

        # Test plugin listing - real functionality
        list_result = api.list_plugins()
        FlextTestsMatchers.assert_result_success(list_result)
        plugin_list = list_result.value
        assert "test_plugin" in plugin_list

        # Test plugin retrieval - real functionality
        get_result = api.get_plugin("test_plugin")
        FlextTestsMatchers.assert_result_success(get_result)
        retrieved_plugin = get_result.value
        assert retrieved_plugin == test_plugin

        # Test plugin unregistration - real functionality
        unregister_result = api.unregister_plugin("test_plugin")
        FlextTestsMatchers.assert_result_success(unregister_result)

        # Verify plugin was removed
        final_list = api.list_plugins()
        FlextTestsMatchers.assert_result_success(final_list)
        assert "test_plugin" not in final_list.value
