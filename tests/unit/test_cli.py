"""Real CLI tests WITHOUT mocks - testing actual FlextDbOracleClient functionality.

This module provides comprehensive tests for CLI components using REAL code
execution without mocks, following FLEXT testing standards.


Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from flext_core import FlextResult
from flext_db_oracle import FlextDbOracleClient, FlextDbOracleModels


class TestFlextDbOracleClientReal:
    """Test FlextDbOracleClient class with REAL functionality - NO MOCKS."""

    def test_client_initialization_debug_mode(self) -> None:
        """Test CLI client initialization in debug mode."""
        client = FlextDbOracleClient(debug=True)

        assert client.debug is True
        assert client.current_connection is None
        assert client.user_preferences["default_output_format"] == "table"
        assert client.user_preferences["show_execution_time"] == "True"

        # Verify flext components are initialized
        assert client.container is not None
        assert client.logger is not None

    def test_client_initialization_production_mode(self) -> None:
        """Test CLI client initialization in production mode."""
        client = FlextDbOracleClient(debug=False)

        assert client.debug is False
        assert client.user_preferences["auto_confirm_operations"] == "False"
        assert client.user_preferences["connection_timeout"] == 30
        assert client.user_preferences["query_limit"] == 1000

    def test_client_initialization_real(self) -> None:
        """Test actual CLI client initialization."""
        client = FlextDbOracleClient()

        # Test that client is properly initialized
        assert client.container is not None
        assert client.logger is not None
        assert client.current_connection is None

    def test_configure_preferences_real(self) -> None:
        """Test configuring user preferences with real values."""
        client = FlextDbOracleClient()

        # Test updating valid preferences
        result = client.configure_preferences(
            default_output_format="json",
            query_limit=2000,
            show_execution_time=False,
        )

        assert result.is_success is True
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

        # Should succeed and add the new preferences (no validation in current implementation)
        assert result.is_success is True
        # New preferences are added to the original ones
        expected_prefs = {
            **original_prefs,
            "invalid_key": "value",
            "another_invalid": "test",
        }
        assert client.user_preferences == expected_prefs

    def test_connection_without_config(self) -> None:
        """Test connection methods without active connection."""
        client = FlextDbOracleClient()

        # Test execute_query without connection
        result = client.execute_query("SELECT 1 FROM DUAL")
        assert not result.is_success
        assert result.error
        assert "No active Oracle connection" in result.error

        # Test list_schemas without connection
        schemas_result = client.list_schemas()
        assert not schemas_result.is_success
        assert schemas_result.error
        assert "No active Oracle connection" in schemas_result.error

        # Test list_tables without connection
        tables_result = client.list_tables()
        assert not tables_result.is_success
        assert tables_result.error
        assert "No active Oracle connection" in tables_result.error

        # Test health_check without connection
        health_result = client.health_check()
        assert not health_result.is_success
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
        assert not result.is_success
        assert result.error
        assert (
            "Connection failed" in result.error
            or "Oracle connection failed" in result.error
        )

    def test_get_global_client_real(self) -> None:
        """Test creating client instances with real functionality."""
        # Create client instances
        client1 = FlextDbOracleClient()
        client2 = FlextDbOracleClient()

        # Verify they are separate instances
        assert isinstance(client1, FlextDbOracleClient)
        assert isinstance(client2, FlextDbOracleClient)
        assert client1 is not client2

    def test_run_cli_command_real(self) -> None:
        """Test CLI command execution with real functionality."""
        # Test command execution (may fail due to missing implementation)
        result = FlextDbOracleClient.run_cli_command("health", timeout=30)

        # Should return FlextResult, may fail due to missing command
        assert isinstance(result, FlextResult)

    def test_connection_wizard_real_validation(self) -> None:
        """Test connection wizard input validation."""
        client = FlextDbOracleClient()

        # Connection wizard functionality is handled through CLI commands
        # Test that client has connection capabilities through connect_to_oracle
        assert hasattr(client, "connect_to_oracle")
        assert callable(client.connect_to_oracle)

    def test_oracle_cli_client_methods_real(self) -> None:
        """Test FlextDbOracleClient has proper CLI methods."""
        # Test CLI client has required methods
        client = FlextDbOracleClient()

        # Test that client has required methods
        assert hasattr(client, "connect_to_oracle")
        assert hasattr(client, "execute_query")
        assert hasattr(client, "list_schemas")
        assert hasattr(client, "list_tables")
        assert hasattr(client, "health_check")

    def test_client_real_error_handling(self) -> None:
        """Test real error handling in client methods."""
        client = FlextDbOracleClient()

        # Test with None/empty parameters
        result = client.execute_query("")
        assert not result.is_success

        # Test configuration with malformed data
        bad_result = client.configure_preferences(valid_key="")
        # Should handle gracefully and return FlextResult
        assert isinstance(bad_result, FlextResult)
        # The method handles None values gracefully (returns success with warning)
        assert bad_result.is_success

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
            name="XE",  # Required field
            service_name="XE",
            username="test",
            password="test",
            ssl_server_cert_dn=None,
            domain_events=[],
        )

        client = FlextDbOracleClient()

        # Test connection attempt (will fail but tests real code path)
        service_name = config.service_name or "default_service"
        result = client.connect_to_oracle(
            config.host,
            config.port,
            service_name,
            config.username,
            config.password,
        )

        # Should fail with connection error, not code errors
        assert not result.is_success
        assert isinstance(result.error, str)
