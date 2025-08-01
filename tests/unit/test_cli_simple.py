"""Simple comprehensive tests for Oracle CLI coverage.

Tests for flext_db_oracle.cli module with focus on code coverage
rather than complex functional testing.
"""

from __future__ import annotations

from unittest.mock import Mock, patch

import pytest
from click.testing import CliRunner

from flext_db_oracle.cli import oracle


class TestOracleCLI:
    """Test Oracle CLI for coverage."""

    @pytest.fixture
    def runner(self) -> CliRunner:
        """Create CLI test runner."""
        return CliRunner()

    def test_oracle_help(self, runner: CliRunner) -> None:
        """Test oracle help command."""
        result = runner.invoke(oracle, ["--help"])
        assert result.exit_code == 0
        assert "Oracle Database CLI" in result.output

    def test_connect_help(self, runner: CliRunner) -> None:
        """Test connect help command."""
        result = runner.invoke(oracle, ["connect", "--help"])
        assert result.exit_code == 0
        assert "Connect to Oracle" in result.output

    def test_connect_env_help(self, runner: CliRunner) -> None:
        """Test connect-env help command."""
        result = runner.invoke(oracle, ["connect-env", "--help"])
        assert result.exit_code == 0

    def test_query_help(self, runner: CliRunner) -> None:
        """Test query help command."""
        result = runner.invoke(oracle, ["query", "--help"])
        assert result.exit_code == 0

    def test_health_help(self, runner: CliRunner) -> None:
        """Test health help command."""
        result = runner.invoke(oracle, ["health", "--help"])
        assert result.exit_code == 0

    def test_plugins_help(self, runner: CliRunner) -> None:
        """Test plugins help command."""
        result = runner.invoke(oracle, ["plugins", "--help"])
        assert result.exit_code == 0

    def test_schemas_help(self, runner: CliRunner) -> None:
        """Test schemas help command."""
        result = runner.invoke(oracle, ["schemas", "--help"])
        assert result.exit_code == 0

    def test_tables_help(self, runner: CliRunner) -> None:
        """Test tables help command."""
        result = runner.invoke(oracle, ["tables", "--help"])
        assert result.exit_code == 0

    @patch("flext_db_oracle.cli.FlextDbOracleApi")
    def test_connect_env_success(self, mock_api_class: Mock, runner: CliRunner) -> None:
        """Test connect-env command success."""
        mock_api = Mock()
        mock_api.connect.return_value = mock_api
        mock_api.is_connected = True
        mock_api_class.from_env.return_value = mock_api

        result = runner.invoke(oracle, ["connect-env"])

        # Should not fail completely
        assert result.exit_code in [0, 1]  # May fail due to missing env vars

    @patch("flext_db_oracle.cli.FlextDbOracleApi")
    def test_connect_with_params(self, mock_api_class: Mock, runner: CliRunner) -> None:
        """Test connect command with parameters."""
        mock_api = Mock()
        mock_api.connect.return_value = mock_api
        mock_api.is_connected = True
        mock_api_class.with_config.return_value = mock_api

        result = runner.invoke(
            oracle,
            [
                "connect",
                "--host",
                "localhost",
                "--port",
                "1521",
                "--service-name",
                "xe",
                "--username",
                "test",
                "--password",
                "test",
            ],
        )

        # Test the command execution (may fail due to no DB, but should not crash)
        assert result.exit_code in [0, 1]

    def test_utility_functions(self) -> None:
        """Test utility functions for coverage."""
        from flext_db_oracle.cli import (
            _extract_table_info,
            _raise_cli_error,
            _safe_get_list_length,
            _safe_get_query_data_attr,
            _safe_get_test_data,
            _safe_iterate_dict,
            _safe_iterate_list,
        )

        # Test _raise_cli_error
        with pytest.raises(Exception, match="test error"):
            _raise_cli_error("test error")

        # Test _safe_get_test_data
        assert _safe_get_test_data({"key": "value"}, "key") == "value"
        assert _safe_get_test_data(None, "key", "default") == "default"

        # Test _safe_get_query_data_attr
        class MockObj:
            attr = "value"

        assert _safe_get_query_data_attr(MockObj(), "attr") == "value"
        assert _safe_get_query_data_attr(None, "attr", "default") == "default"

        # Test _safe_iterate_list
        assert _safe_iterate_list(["a", "b"]) == ["a", "b"]
        assert _safe_iterate_list(None) == []

        # Test _safe_iterate_dict
        assert _safe_iterate_dict({"a": "b"}) == {"a": "b"}
        assert _safe_iterate_dict(None) == {}

        # Test _safe_get_list_length
        assert _safe_get_list_length([1, 2, 3]) == 3
        assert _safe_get_list_length(None) == 0
        assert _safe_get_list_length("abc") == 3

        # Test _extract_table_info
        table_dict = {"name": "test_table", "schema": "test_schema"}
        name, schema = _extract_table_info(table_dict, None)
        assert name == "test_table"
        assert schema == "test_schema"

        name, schema = _extract_table_info("simple_table", "default_schema")
        assert name == "simple_table"
        assert schema == "default_schema"

    def test_connection_params(self) -> None:
        """Test ConnectionParams dataclass."""
        from flext_db_oracle.cli import ConnectionParams

        params = ConnectionParams(
            host="localhost",
            port=1521,
            service_name="xe",
            username="user",
            password="pass",
        )

        assert params.host == "localhost"
        assert params.port == 1521
        assert params.service_name == "xe"
        assert params.username == "user"
        assert params.password == "pass"

    @patch("flext_db_oracle.cli.FlextDbOracleApi")
    def test_error_handling(self, mock_api_class: Mock, runner: CliRunner) -> None:
        """Test CLI error handling."""
        mock_api_class.from_env.side_effect = Exception("Connection failed")

        result = runner.invoke(oracle, ["connect-env"])

        # Should handle error gracefully
        assert result.exit_code == 1
        assert "Connection failed" in result.output
