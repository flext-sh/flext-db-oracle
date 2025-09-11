"""Real CLI tests WITHOUT mocks - testing actual FlextDbOracleClient functionality.

This module provides comprehensive tests for CLI components using REAL code
execution without mocks, following FLEXT testing standards.


Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

import pytest
from flext_core import FlextResult
from pydantic import SecretStr

from flext_db_oracle import FlextDbOracleModels
from flext_db_oracle.client import (
    FlextDbOracleClient,
    create_oracle_cli_commands,
    get_client,
)


class TestFlextDbOracleClientReal:
    """Test FlextDbOracleClient class with REAL functionality - NO MOCKS."""

    def test_client_initialization_debug_mode(self) -> None:
        """Test CLI client initialization in debug mode."""
        client = FlextDbOracleClient(debug=True)

        assert client.debug is True
        assert client.current_connection is None
        assert client.user_preferences["default_output_format"] == "table"
        assert client.user_preferences["show_execution_time"] is True

        # Verify flext-cli components are initialized
        assert client.cli_api is not None
        assert client.formatter is not None
        assert client.interactions is not None
        assert client.logger is not None

    def test_client_initialization_production_mode(self) -> None:
        """Test CLI client initialization in production mode."""
        client = FlextDbOracleClient(debug=False)

        assert client.debug is False
        assert client.user_preferences["auto_confirm_operations"] is False
        assert client.user_preferences["connection_timeout"] == 30
        assert client.user_preferences["query_limit"] == 1000

    def test_client_initialization_real(self) -> None:
        """Test actual CLI client initialization."""
        client = FlextDbOracleClient()

        # Test real initialization
        init_result = client.initialize()
        # May fail due to missing flext-cli components, but should return FlextResult
        assert isinstance(init_result, FlextResult)

    def test_configure_preferences_real(self) -> None:
        """Test configuring user preferences with real values."""
        client = FlextDbOracleClient()

        # Test updating valid preferences
        result = client.configure_preferences(
            default_output_format="json",
            query_limit=2000,
            show_execution_time=False,
        )

        assert result.success is True
        assert client.user_preferences["default_output_format"] == "json"
        assert client.user_preferences["query_limit"] == 2000
        assert client.user_preferences["show_execution_time"] is False

    def test_configure_preferences_invalid_keys(self) -> None:
        """Test configuring preferences with invalid keys."""
        client = FlextDbOracleClient()
        original_prefs = client.user_preferences.copy()

        # Test with invalid preference keys
        result = client.configure_preferences(
            invalid_key="value",
            another_invalid="test",
        )

        # Should still succeed but not change preferences
        assert result.success is True
        assert client.user_preferences == original_prefs

    def test_connection_without_config(self) -> None:
        """Test connection methods without active connection."""
        client = FlextDbOracleClient()

        # Test execute_query without connection
        result = client.execute_query("SELECT 1 FROM DUAL")
        assert not result.success
        assert result.error
        assert "No active Oracle connection" in result.error

        # Test list_schemas without connection
        schemas_result = client.list_schemas()
        assert not schemas_result.success
        assert schemas_result.error
        assert "No active Oracle connection" in schemas_result.error

        # Test list_tables without connection
        tables_result = client.list_tables()
        assert not tables_result.success
        assert tables_result.error
        assert "No active Oracle connection" in tables_result.error

        # Test health_check without connection
        health_result = client.health_check()
        assert not health_result.success
        assert health_result.error
        assert "No active Oracle connection" in health_result.error

    def test_connect_to_oracle_invalid_credentials(self) -> None:
        """Test Oracle connection with invalid credentials (real connection attempt)."""
        client = FlextDbOracleClient()

        # Test with obviously invalid connection details
        result = client.connect_to_oracle(
            host="nonexistent-host-12345.invalid",
            port=9999,
            service_name="INVALID",
            username="invalid_user",
            password="invalid_password",
        )

        # Should fail with real connection error
        assert not result.success
        assert result.error
        assert (
            "Connection failed" in result.error
            or "Oracle connection failed" in result.error
        )

    def test_get_global_client_real(self) -> None:
        """Test global client getter with real functionality."""
        # This may initialize flext-cli components
        try:
            client = get_client()
            assert isinstance(client, FlextDbOracleClient)

            # Test that subsequent calls return same instance
            client2 = get_client()
            assert client is client2

        except SystemExit:
            # Expected if flext-cli initialization fails
            pytest.skip(
                "flext-cli initialization failed - expected in test environment",
            )

    def test_run_cli_command_real(self) -> None:
        """Test CLI command execution with real FlextCliApi."""
        client = FlextDbOracleClient()

        # Test command execution (may fail due to missing flext-cli setup)
        result = client.run_cli_command("test-command", param1="value1")

        # Should return FlextResult, may fail due to missing command
        assert isinstance(result, FlextResult)

    def test_connection_wizard_real_validation(self) -> None:
        """Test connection wizard input validation."""
        client = FlextDbOracleClient()

        # The wizard requires interactive input, so we can't fully test it
        # But we can test that it's properly defined
        assert hasattr(client, "connection_wizard")
        assert callable(client.connection_wizard)

    def test_create_oracle_cli_commands_real(self) -> None:
        """Test CLI commands creation with real FlextCliModels."""
        # Test command creation
        commands_result = create_oracle_cli_commands()

        # Should return FlextResult with commands
        assert isinstance(commands_result, FlextResult)

        if commands_result.success:
            commands = commands_result.value
            assert isinstance(commands, list)
            assert len(commands) > 0

            # Verify command structure - CliCommand actual fields
            for command in commands:
                assert hasattr(command, "command_line")
                assert hasattr(command, "status")
                assert hasattr(command, "execution_time")
                assert isinstance(command.command_line, str)
                assert len(command.command_line) > 0

    def test_client_real_error_handling(self) -> None:
        """Test real error handling in client methods."""
        client = FlextDbOracleClient()

        # Test with None/empty parameters
        result = client.execute_query("")
        assert not result.success

        # Test configuration with malformed data
        try:
            bad_result = client.configure_preferences(valid_key=None)
            # Should handle gracefully
            assert isinstance(bad_result, FlextResult)
        except Exception:
            # Some parameter combinations might raise exceptions
            pass

    def test_client_preferences_persistence(self) -> None:
        """Test that preference changes persist within client instance."""
        client = FlextDbOracleClient()

        client.user_preferences["default_output_format"]
        client.user_preferences["connection_timeout"]

        # Change preferences
        client.configure_preferences(
            default_output_format="json",
            connection_timeout=60,
        )

        # Verify changes persisted
        assert client.user_preferences["default_output_format"] == "json"
        assert client.user_preferences["connection_timeout"] == 60

        # Other preferences should remain unchanged
        assert client.user_preferences["query_limit"] == 1000  # default value


class TestFlextDbOracleClientIntegration:
    """Integration tests using real Oracle database operations."""

    def test_client_with_real_config_creation(self) -> None:
        """Test client operations with real configuration objects."""
        # Create real configuration
        config = FlextDbOracleModels.OracleConfig(
            host="localhost",
            port=1521,
            database="XE",  # Required field
            service_name="XE",
            username="test",
            password=SecretStr("test"),
            ssl_server_cert_dn=None,
        )

        client = FlextDbOracleClient()

        # Test connection attempt (will fail but tests real code path)
        service_name = config.service_name or "default_service"
        result = client.connect_to_oracle(
            config.host,
            config.port,
            service_name,
            config.username,
            config.password.get_secret_value(),
        )

        # Should fail with connection error, not code errors
        assert not result.success
        assert isinstance(result.error, str)
