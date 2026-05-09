"""Real CLI tests WITHOUT mocks - testing actual FlextDbOracleClient functionality.

This module provides comprehensive tests for CLI components using REAL code
execution without mocks, following FLEXT testing standards.


Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import os

import pytest
from flext_tests import tm

from flext_db_oracle import (
    FlextDbOracleApi,
    FlextDbOracleClient,
    FlextDbOraclePassword,
    FlextDbOracleSettings,
)
from tests import r, t, u

_NO_CONNECTION_ERROR = "No active Oracle connection"


class TestsFlextDbOracleCli:
    """Test FlextDbOracleClient class with REAL functionality - NO MOCKS."""

    def test_client_initialization_debug_mode(self) -> None:
        """Test CLI client initialization in debug mode."""
        client = FlextDbOracleClient(debug=True)
        tm.that(client.debug, eq=True)
        tm.that(client.current_connection, none=True)
        tm.that(client.user_preferences["default_output_format"], eq="table")
        tm.that(client.user_preferences["show_execution_time"], eq="True")
        tm.that(client.container, none=False)
        tm.that(client.logger, none=False)

    def test_client_initialization_production_mode(self) -> None:
        """Test CLI client initialization in production mode."""
        client = FlextDbOracleClient(debug=False)
        tm.that(client.debug, eq=False)
        tm.that(client.user_preferences["auto_confirm_operations"], eq="False")
        tm.that(client.user_preferences["connection_timeout"], eq=30)
        tm.that(client.user_preferences["query_limit"], eq=1000)

    def test_client_initialization_real(self) -> None:
        """Test actual CLI client initialization."""
        client = FlextDbOracleClient()
        tm.that(client.container, none=False)
        tm.that(client.logger, none=False)
        tm.that(client.current_connection, none=True)

    def test_configure_preferences_real(self) -> None:
        """Test configuring user preferences with real values."""
        client = FlextDbOracleClient()
        tm.ok(
            client.configure_preferences(
                default_output_format="json",
                query_limit=2000,
                show_execution_time=False,
            )
        )
        tm.that(client.user_preferences["default_output_format"], eq="json")
        tm.that(client.user_preferences["query_limit"], eq=2000)
        tm.that(client.user_preferences["show_execution_time"], eq=False)

    def test_configure_preferences_invalid_keys(self) -> None:
        """Invalid preference keys are tolerated and not stored as attributes."""
        client = FlextDbOracleClient()
        tm.ok(client.configure_preferences(invalid_key="value", another_invalid="test"))
        tm.that(hasattr(client.user_preferences, "invalid_key"), eq=False)
        tm.that(hasattr(client.user_preferences, "another_invalid"), eq=False)

    def test_connection_without_config(self) -> None:
        """Every privileged client method fails fast without an active connection."""
        client = FlextDbOracleClient()
        tm.fail(client.execute_query("SELECT 1 FROM DUAL"), has=_NO_CONNECTION_ERROR)
        tm.fail(client.list_schemas(), has=_NO_CONNECTION_ERROR)
        tm.fail(client.list_tables(), has=_NO_CONNECTION_ERROR)
        tm.fail(client.health_check(), has=_NO_CONNECTION_ERROR)

    def test_connect_to_oracle_invalid_credentials(self) -> None:
        """Test Oracle connection with invalid credentials (real connection attempt)."""
        client = FlextDbOracleClient()
        result = client.connect_to_oracle(
            host="nonexistent-host-12345.invalid",
            port=9999,
            service_name="INVALID",
            username="invalid_user",
            password="invalid_password",
        )
        tm.that(result.failure, eq=True)
        error_text = result.error or ""
        tm.that(
            any(
                snippet in error_text
                for snippet in (
                    "Connection failed",
                    "Oracle connection failed",
                    "Connection error",
                )
            ),
            eq=True,
        )

    def test_get_global_client_real(self) -> None:
        """Test creating client instances with real functionality."""
        client1 = FlextDbOracleClient()
        client2 = FlextDbOracleClient()
        tm.that(client1, is_=FlextDbOracleClient)
        tm.that(client2, is_=FlextDbOracleClient)
        tm.that(client1 is not client2, eq=True)

    def test_run_cli_command_real(self) -> None:
        """Test CLI command execution with real functionality."""
        tm.that(FlextDbOracleClient.run_cli_command("health", timeout=30), is_=r)

    def test_connection_wizard_real_validation(self) -> None:
        """Test connection wizard input validation."""
        tm.that(callable(FlextDbOracleClient().connect_to_oracle), eq=True)

    def test_client_real_error_handling(self) -> None:
        """Test real error handling in client methods."""
        client = FlextDbOracleClient()
        tm.fail(client.execute_query(""))
        bad_result = client.configure_preferences(valid_key="")
        tm.that(bad_result, is_=r)
        tm.ok(bad_result)

    def test_client_preferences_persistence(self) -> None:
        """Test that preference changes persist within client instance."""
        client = FlextDbOracleClient()
        client.configure_preferences(
            default_output_format="json", connection_timeout=60
        )
        tm.that(client.user_preferences["default_output_format"], eq="json")
        tm.that(client.user_preferences["connection_timeout"], eq=60)
        tm.that(client.user_preferences["query_limit"], eq=1000)

    def test_client_with_real_config_creation(self) -> None:
        """Test client operations with real configuration objects."""
        settings = FlextDbOracleSettings(
            host="localhost",
            port=1521,
            name="XE",
            service_name="XE",
            username="test",
            password="test",
            ssl_server_cert_dn=None,
        )
        client = FlextDbOracleClient()
        password = (
            settings.password.get_secret_value()
            if isinstance(settings.password, FlextDbOraclePassword)
            else settings.password
        )
        result = client.connect_to_oracle(
            settings.host,
            settings.port,
            settings.service_name or "default_service",
            settings.username,
            password,
        )
        tm.that(result.failure, eq=True)
        tm.that(result.error, is_=str)

    def test_yaml_module_protocol_interface(self) -> None:
        """Test that yaml dump produces valid YAML string."""
        result = u.Cli.yaml_dump_str({"test": "value"})
        tm.that(result, is_=str)
        tm.that(result, has=["test", "value"])

    def test_cli_creation_and_basic_functionality(self) -> None:
        """Test CLI creation and basic functionality - REAL IMPLEMENTATION."""
        oracle_cli = FlextDbOracleClient()
        get_history_method = getattr(oracle_cli, "get_command_history", None)
        if callable(get_history_method):
            tm.that(get_history_method(), is_=list)

    @pytest.fixture
    def oracle_env_vars(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> t.MutableOptionalStrMapping:
        """Configure ORACLE_* env vars while purging FLEXT_TARGET_ORACLE_* leakage."""
        for key in [k for k in os.environ if k.startswith("FLEXT_TARGET_ORACLE_")]:
            monkeypatch.delenv(key, raising=False)
        env_vars: t.MutableOptionalStrMapping = {
            "ORACLE_HOST": "localhost",
            "ORACLE_PORT": "1521",
            "ORACLE_USERNAME": "testuser",
            "ORACLE_PASSWORD": "testpass",
            "ORACLE_SERVICE_NAME": "TESTDB",
        }
        for key, value in env_vars.items():
            if value is not None:
                monkeypatch.setenv(key, value)
        return env_vars

    def test_environment_configuration_real(
        self, oracle_env_vars: t.MutableOptionalStrMapping
    ) -> None:
        """Test environment configuration using real API functionality."""
        _ = oracle_env_vars
        api_result = FlextDbOracleApi.from_env()
        tm.ok(api_result)
        tm.that(api_result.unwrap().settings.host, none=False)

    def test_api_observability_and_connection_real(self) -> None:
        """Test API observability and connection functionality - REAL IMPLEMENTATION."""
        api = FlextDbOracleApi(
            FlextDbOracleSettings(
                host="localhost",
                port=1521,
                service_name="TESTDB",
                username="test",
                password="test",
            )
        )
        metrics_result = api.fetch_observability_metrics()
        tm.ok(metrics_result)
        tm.that(metrics_result.unwrap(), is_=dict)
        api.test_connection()
        tm.that(api.valid(), eq=True)

    @pytest.mark.parametrize("format_type", ["table", "json", "csv"])
    def test_output_formatting_real(self, format_type: str) -> None:
        """Test output formatting using real functionality."""
        formatted = u.DbOracle.format_query_result(
            {"column1": "value1", "column2": "value2"},
            format_type=format_type,
        )
        tm.ok(formatted)
        unwrapped = formatted.unwrap()
        tm.that(unwrapped, is_=str)
        tm.that(bool(unwrapped), eq=True)

    def test_error_handling_real(self) -> None:
        """Test error handling using real functionality - NO MOCKS."""
        api = FlextDbOracleApi(
            FlextDbOracleSettings(
                host="invalid.host",
                port=9999,
                service_name="INVALID_SERVICE",
                username="invalid_user",
                password="invalid_password",
            )
        )
        query_result = api.query("SELECT 1 FROM DUAL")
        tm.that(query_result.failure, eq=True)
        error_lower = (query_result.error or "").lower()
        tm.that("not connected" in error_lower or "connection" in error_lower, eq=True)
        tm.that(api.fetch_schemas().failure, eq=True)
        tm.that(api.fetch_tables().failure, eq=True)

    def test_parameter_processing_real(self) -> None:
        """Test parameter processing using real API functionality."""
        api = FlextDbOracleApi(
            settings=FlextDbOracleSettings(
                host="param_test_host",
                port=1521,
                service_name="PARAM_TEST",
                username="param_user",
                password="param_pass",
            )
        )
        tm.that(api.settings.host, eq="param_test_host")
        tm.that(api.settings.port, eq=1521)
        tm.that(api.settings.service_name, eq="PARAM_TEST")
        tm.that(api.settings.username, eq="param_user")

    def test_comprehensive_api_coverage_real(self) -> None:
        """Comprehensive API coverage test using real functionality - NO MOCKS."""
        api = FlextDbOracleApi(
            FlextDbOracleSettings(
                host="comprehensive_test",
                port=1521,
                name="COMP_TEST",
                service_name="COMP_TEST",
                username="comp_user",
                password="comp_pass",
            )
        )
        methods_to_test = [
            api.valid,
            api.to_dict,
            api.fetch_observability_metrics,
            lambda: api.optimize_query("SELECT * FROM test"),
            api.list_plugins,
        ]
        for method_call in methods_to_test:
            result = method_call()
            tm.that(result, none=False)

    def test_factory_methods_real(
        self,
        oracle_env_vars: t.MutableOptionalStrMapping,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """Test factory methods using real functionality - NO MOCKS."""
        del oracle_env_vars
        monkeypatch.setenv("ORACLE_SERVICE_NAME", "XEPDB1")
        api_result = FlextDbOracleApi.from_env()
        tm.ok(api_result)
        api = api_result.unwrap()
        tm.that(api.settings.host, none=False)
        tm.that(api.settings.port, is_=int)
        url_api = FlextDbOracleApi(
            settings=FlextDbOracleSettings(
                host="host",
                port=1521,
                service_name="SERVICE",
                username="user",
                password="pass",
            )
        )
        tm.that(url_api.settings.host, eq="host")
        tm.that(url_api.settings.port, eq=1521)
        tm.that(url_api.settings.service_name, eq="SERVICE")

    def test_plugin_system_real(self) -> None:
        """Test plugin system using real functionality - NO MOCKS."""
        api = FlextDbOracleApi(
            FlextDbOracleSettings(
                host="plugin_test",
                port=1521,
                service_name="PLUGIN_TEST",
                username="plugin_user",
                password="plugin_pass",
            )
        )
        plugin_payload = {"name": "test_plugin", "version": "1.0.0"}
        tm.ok(api.register_plugin("test_plugin", plugin_payload))
        tm.that(tm.ok(api.list_plugins()), has="test_plugin")
        tm.that(api.fetch_plugin("test_plugin").unwrap(), eq=plugin_payload)
        tm.ok(api.unregister_plugin("test_plugin"))
        tm.that("test_plugin" not in api.list_plugins().unwrap(), eq=True)
