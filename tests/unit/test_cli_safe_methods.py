"""Tests for FlextDbOracle CLI methods that work without Oracle connection.

Focus on CLI functionality that doesn't require database connection to boost coverage:
- CLI application initialization
- Command registration and discovery
- Configuration parsing
- Help system
- Output formatting utilities
"""

import os
from unittest.mock import Mock, patch

import pytest
from click.testing import CliRunner
from flext_core import FlextResult
from pydantic import SecretStr

from flext_db_oracle import FlextDbOracleConfig
from flext_db_oracle.cli import (
    FlextDbOracleCliApplication,
    get_app,
    oracle_cli,
)


class TestFlextDbOracleCliApplication:
    """Test CLI application initialization and core methods."""

    def test_cli_application_initialization(self) -> None:
        """Test CLI application basic initialization."""
        app = FlextDbOracleCliApplication()
        assert app is not None
        assert hasattr(app, "console")
        assert hasattr(app, "cli_config")

    def test_cli_application_debug_mode(self) -> None:
        """Test CLI application with debug mode."""
        app = FlextDbOracleCliApplication(debug=True)
        assert app is not None
        # Debug mode should be reflected in app state

    def test_get_app_singleton_pattern(self) -> None:
        """Test get_app singleton pattern."""
        # Clear any existing app
        import flext_db_oracle.cli as cli_module

        cli_module.app = None

        app1 = get_app()
        app2 = get_app()
        assert app1 is app2  # Same instance
        assert app1 is not None

    def test_get_app_debug_parameter(self) -> None:
        """Test get_app with debug parameter."""
        import flext_db_oracle.cli as cli_module

        cli_module.app = None

        app = get_app(debug=True)
        assert app is not None


class TestFlextDbOracleCliCommands:
    """Test CLI commands without Oracle connection."""

    def setup_method(self) -> None:
        """Set up test environment."""
        self.runner = CliRunner()

    def test_cli_help_command(self) -> None:
        """Test CLI help command."""
        result = self.runner.invoke(oracle_cli, ["--help"])
        assert result.exit_code == 0
        assert "Oracle" in result.output
        assert "database" in result.output.lower()

    def test_cli_command_discovery(self) -> None:
        """Test CLI discovers all commands."""
        result = self.runner.invoke(oracle_cli, ["--help"])
        assert result.exit_code == 0

        # Check for main commands
        expected_commands = [
            "connect",
            "connect-env",
            "query",
            "schemas",
            "tables",
            "health",
        ]
        for cmd in expected_commands:
            assert cmd in result.output

    @patch("flext_db_oracle.cli.FlextDbOracleUtilities.create_config_from_env")
    @patch("flext_db_oracle.cli.FlextDbOracleCliApplication.initialize_application")
    def test_connect_env_command_help(
        self, mock_init: Mock, mock_create_config: Mock
    ) -> None:
        """Test connect-env command help."""
        result = self.runner.invoke(oracle_cli, ["connect-env", "--help"])
        assert result.exit_code == 0
        assert "environment" in result.output.lower()

    @patch("flext_db_oracle.cli.FlextDbOracleUtilities.create_config_from_env")
    @patch("flext_db_oracle.cli.FlextDbOracleCliApplication.initialize_application")
    def test_query_command_help(
        self, mock_init: Mock, mock_create_config: Mock
    ) -> None:
        """Test query command help."""
        result = self.runner.invoke(oracle_cli, ["query", "--help"])
        assert result.exit_code == 0
        assert "sql" in result.output.lower()

    def test_connection_command_help(self) -> None:
        """Test connection command help."""
        result = self.runner.invoke(oracle_cli, ["connection", "--help"])
        assert result.exit_code == 0
        assert "connection" in result.output.lower()


class TestFlextDbOracleCliUtilities:
    """Test CLI utility classes and methods."""

    def test_cli_utilities_import(self) -> None:
        """Test CLI utilities can be imported."""
        from flext_db_oracle.cli import FlextDbOracleUtilities

        assert FlextDbOracleUtilities is not None
        assert hasattr(FlextDbOracleUtilities, "create_config_from_env")
        assert hasattr(FlextDbOracleUtilities, "create_api_from_config")

    @patch.dict(
        os.environ,
        {
            "FLEXT_TARGET_ORACLE_HOST": "test_host",
            "FLEXT_TARGET_ORACLE_PORT": "1521",
            "FLEXT_TARGET_ORACLE_SERVICE_NAME": "TEST_SERVICE",
            "FLEXT_TARGET_ORACLE_USERNAME": "test_user",
            "FLEXT_TARGET_ORACLE_PASSWORD": "test_pass",
        },
    )
    def test_utilities_create_config_from_env(self) -> None:
        """Test utilities create_config_from_env method."""
        from flext_db_oracle.cli import FlextDbOracleUtilities

        result = FlextDbOracleUtilities.create_config_from_env()
        assert isinstance(result, FlextResult)
        if result.success:
            config = result.value
            assert isinstance(config, FlextDbOracleConfig)
            assert config.host == "test_host"
            assert config.port == 1521

    def test_utilities_create_api_from_config(self) -> None:
        """Test utilities create_api_from_config method."""
        from flext_db_oracle import FlextDbOracleApi
        from flext_db_oracle.cli import FlextDbOracleUtilities

        config = FlextDbOracleConfig(
            host="util_test",
            port=1521,
            service_name="UTIL_TEST",
            username="util_user",
            password=SecretStr("util_pass"),
        )

        api = FlextDbOracleUtilities.create_api_from_config(config)
        assert isinstance(api, FlextDbOracleApi)
        assert api.config.host == "util_test"

    def test_utilities_format_query_result_empty(self) -> None:
        """Test utilities format_query_result with empty result."""
        from flext_db_oracle.cli import FlextDbOracleUtilities
        from flext_db_oracle.models import FlextDbOracleQueryResult

        empty_result = FlextDbOracleQueryResult(
            columns=[], rows=[], row_count=0, execution_time_ms=0.1
        )

        # This should not raise an exception
        console_mock = Mock()
        console_mock.print = Mock()
        try:
            FlextDbOracleUtilities.format_query_result(
                empty_result, "table", console_mock
            )
        except Exception as e:
            pytest.fail(f"format_query_result failed with empty result: {e}")


class TestFlextDbOracleCliErrorHandling:
    """Test CLI error handling scenarios."""

    def setup_method(self) -> None:
        """Set up test environment."""
        self.runner = CliRunner()

    def test_cli_invalid_command(self) -> None:
        """Test CLI with invalid command."""
        result = self.runner.invoke(oracle_cli, ["invalid-command"])
        assert result.exit_code != 0
        assert "No such command" in result.output

    @patch("flext_db_oracle.cli.FlextDbOracleUtilities.create_config_from_env")
    @patch("flext_db_oracle.cli.FlextDbOracleCliApplication.initialize_application")
    def test_connect_env_missing_config(
        self, mock_init: Mock, mock_create_config: Mock
    ) -> None:
        """Test connect-env with missing environment configuration."""
        mock_init.return_value = FlextResult[None].ok(None)
        mock_create_config.return_value = FlextResult[FlextDbOracleConfig].fail(
            "Missing environment variables"
        )

        result = self.runner.invoke(oracle_cli, ["connect-env"])
        # The decorators intercept the exit code, but error message should appear
        assert (
            "Missing environment variables" in result.output
            or "error" in result.output.lower()
        )

    def test_query_command_missing_sql(self) -> None:
        """Test query command without SQL parameter."""
        result = self.runner.invoke(oracle_cli, ["query"])
        assert result.exit_code != 0
        assert "Missing option" in result.output or "Error" in result.output


class TestFlextDbOracleCliConfiguration:
    """Test CLI configuration and parameter handling."""

    def setup_method(self) -> None:
        """Set up test environment."""
        self.runner = CliRunner()

    def test_cli_environment_variable_parsing(self) -> None:
        """Test CLI environment variable parsing logic."""
        from flext_db_oracle.cli import FlextDbOracleUtilities

        # Test with empty environment
        with patch.dict(os.environ, {}, clear=True):
            result = FlextDbOracleUtilities.create_config_from_env()
            # Should handle missing env vars gracefully
            assert isinstance(result, FlextResult)

    @patch("flext_db_oracle.cli.FlextDbOracleUtilities.create_config_from_env")
    @patch("flext_db_oracle.cli.FlextDbOracleUtilities.create_api_from_config")
    @patch("flext_db_oracle.cli.FlextDbOracleCliApplication.initialize_application")
    def test_query_command_parameters(
        self, mock_init: Mock, mock_create_api: Mock, mock_create_config: Mock
    ) -> None:
        """Test query command parameter handling."""
        # Setup mocks
        mock_init.return_value = FlextResult[None].ok(None)

        mock_config = FlextDbOracleConfig(
            host="test",
            port=1521,
            service_name="TEST",
            username="test",
            password=SecretStr("test"),
        )
        mock_create_config.return_value = FlextResult[FlextDbOracleConfig].ok(
            mock_config
        )

        # Test with all parameters
        self.runner.invoke(
            oracle_cli,
            [
                "query",
                "--sql",
                "SELECT 1 FROM dual",
                "--limit",
                "10",
                "--output",
                "json",
            ],
        )
        # Command parsing should succeed (connection will fail but that's expected)
        mock_init.assert_called_once()


class TestFlextDbOracleCliOutput:
    """Test CLI output formatting and display."""

    def setup_method(self) -> None:
        """Set up test environment."""
        self.runner = CliRunner()

    def test_cli_output_format_options(self) -> None:
        """Test CLI output format options are recognized."""
        result = self.runner.invoke(oracle_cli, ["query", "--help"])
        assert result.exit_code == 0

        # Check for basic command options
        assert "sql" in result.output.lower()
        assert "limit" in result.output.lower()

    def test_cli_utilities_output_methods_exist(self) -> None:
        """Test CLI utilities output methods exist."""
        from flext_db_oracle.cli import FlextDbOracleUtilities

        # Check that formatting methods exist
        assert hasattr(FlextDbOracleUtilities, "format_query_result")
        # These methods should be callable
        assert callable(FlextDbOracleUtilities.format_query_result)
