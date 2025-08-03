"""Comprehensive tests for Oracle CLI to achieve 90%+ coverage.

Tests for flext_db_oracle.cli module with comprehensive coverage
of all CLI commands and utility functions.
"""

from __future__ import annotations

from unittest.mock import Mock, patch

import pytest
from click.testing import CliRunner
from flext_core import FlextResult

from flext_db_oracle.cli import (
    ConnectionParams,
    _extract_table_info,
    _safe_get_list_length,
    oracle,
)


def make_context_manager_mock() -> Mock:
    """Create a mock that supports context manager protocol."""
    mock_api = Mock()
    mock_api.__enter__ = Mock(return_value=mock_api)
    mock_api.__exit__ = Mock(return_value=False)
    return mock_api


class TestOracleCLIComprehensive:
    """Comprehensive test Oracle CLI commands for coverage."""

    @pytest.fixture
    def runner(self) -> CliRunner:
        """Create CLI test runner."""
        return CliRunner()

    @pytest.fixture
    def mock_config(self) -> Mock:
        """Create mock config."""
        config = Mock()
        config.profile = "test"
        config.output_format = "table"
        config.debug = False
        return config

    def test_oracle_group_basic(self, runner: CliRunner) -> None:
        """Test oracle group command basic functionality."""
        result = runner.invoke(oracle, ["--help"])
        assert result.exit_code == 0
        assert "Oracle Database CLI" in result.output

    def test_oracle_group_with_options(self, runner: CliRunner) -> None:
        """Test oracle group with all options."""
        with patch("flext_db_oracle.cli.get_config") as mock_get_config:
            mock_config = Mock()
            mock_get_config.return_value = mock_config

            # Test with a subcommand to actually trigger the group function
            # Since --help shortcuts out before calling the function
            result = runner.invoke(
                oracle,
                [
                    "--profile",
                    "test",
                    "--output",
                    "json",
                    "--debug",
                    "schemas",
                    "--help",
                ],
            )
            assert result.exit_code == 0
            # get_config should be called when the group function executes
            mock_get_config.assert_called_once()

    @patch("flext_db_oracle.cli._execute_connection_test")
    def test_connect_command_success(
        self,
        mock_execute: Mock,
        runner: CliRunner,
    ) -> None:
        """Test connect command with valid parameters."""
        result = runner.invoke(
            oracle,
            [
                "connect",
                "--host",
                "localhost",
                "--port",
                "1521",
                "--service-name",
                "XE",
                "--username",
                "test",
                "--password",
                "test",
            ],
        )
        assert result.exit_code == 0
        mock_execute.assert_called_once()

        # Verify ConnectionParams was created correctly
        args, _ = mock_execute.call_args
        params = args[1]  # Second argument is params
        assert isinstance(params, ConnectionParams)
        assert params.host == "localhost"
        assert params.port == 1521
        assert params.service_name == "XE"
        assert params.username == "test"
        assert params.password == "test"

    def test_connect_command_missing_required(self, runner: CliRunner) -> None:
        """Test connect command with missing required parameters."""
        result = runner.invoke(oracle, ["connect"])
        assert result.exit_code != 0
        assert "Missing option" in result.output

    @patch("flext_db_oracle.cli.FlextDbOracleApi.from_env")
    def test_connect_env_command_success(
        self,
        mock_from_env: Mock,
        runner: CliRunner,
    ) -> None:
        """Test connect-env command success."""
        # Mock successful API creation and connection
        mock_api = Mock()
        mock_api.test_connection_with_observability.return_value = FlextResult.ok(
            {
                "status": "healthy",
                "connected": True,
            },
        )
        mock_from_env.return_value = mock_api

        result = runner.invoke(oracle, ["connect-env"])
        assert result.exit_code == 0
        mock_from_env.assert_called_once()

    @patch("flext_db_oracle.cli.FlextDbOracleApi.from_env")
    def test_query_command_basic(self, mock_from_env: Mock, runner: CliRunner) -> None:
        """Test query command basic functionality."""
        # Mock API instance and successful query
        mock_api = make_context_manager_mock()

        from flext_db_oracle.types import TDbOracleQueryResult

        query_result = TDbOracleQueryResult(
            rows=[("result",)],
            columns=["col1"],
            row_count=1,
            execution_time_ms=10.0,
        )
        mock_api.query_with_timing.return_value = FlextResult.ok(query_result)
        mock_from_env.return_value = mock_api

        result = runner.invoke(
            oracle,
            [
                "query",
                "--sql",
                "SELECT 1 FROM DUAL",
            ],
        )
        assert result.exit_code == 0

    def test_query_command_help(self, runner: CliRunner) -> None:
        """Test query command help."""
        result = runner.invoke(oracle, ["query", "--help"])
        assert result.exit_code == 0
        assert "Execute SQL query" in result.output

    @patch("flext_db_oracle.cli.FlextDbOracleApi.from_env")
    def test_schemas_command_success(
        self,
        mock_from_env: Mock,
        runner: CliRunner,
    ) -> None:
        """Test schemas command success."""
        # Mock API and successful schema retrieval
        mock_api = make_context_manager_mock()
        mock_api.get_schemas.return_value = FlextResult.ok(["HR", "SCOTT", "SYS"])
        mock_from_env.return_value = mock_api

        result = runner.invoke(oracle, ["schemas"])
        assert result.exit_code == 0

    @patch("flext_db_oracle.cli.FlextDbOracleApi.from_env")
    def test_tables_command_success(
        self,
        mock_from_env: Mock,
        runner: CliRunner,
    ) -> None:
        """Test tables command success."""
        # Mock API and successful table retrieval
        mock_api = make_context_manager_mock()
        mock_api.get_tables.return_value = FlextResult.ok(["EMPLOYEES", "DEPARTMENTS"])
        mock_from_env.return_value = mock_api

        result = runner.invoke(oracle, ["tables"])
        assert result.exit_code == 0

    @patch("flext_db_oracle.cli.FlextDbOracleApi.from_env")
    def test_tables_command_with_schema(
        self,
        mock_from_env: Mock,
        runner: CliRunner,
    ) -> None:
        """Test tables command with schema filter."""
        # Mock API and successful table retrieval with schema
        mock_api = make_context_manager_mock()
        mock_api.get_tables.return_value = FlextResult.ok(["EMPLOYEES", "DEPARTMENTS"])
        mock_from_env.return_value = mock_api

        result = runner.invoke(oracle, ["tables", "--schema", "HR"])
        assert result.exit_code == 0
        # Verify schema was passed to get_tables
        mock_api.get_tables.assert_called_with("HR")

    @patch("flext_db_oracle.cli.register_all_oracle_plugins")
    @patch("flext_db_oracle.cli.FlextDbOracleApi.from_env")
    def test_plugins_command_success(
        self,
        mock_from_env: Mock,
        mock_register: Mock,
        runner: CliRunner,
    ) -> None:
        """Test plugins command success."""
        # Mock successful plugin registration
        mock_api = make_context_manager_mock()
        mock_register.return_value = FlextResult.ok(
            {"plugin1": "success", "plugin2": "success"},
        )
        mock_api.list_plugins.return_value = FlextResult.ok(
            [
                Mock(name="plugin1", version="1.0"),
                Mock(name="plugin2", version="2.0"),
            ],
        )
        mock_from_env.return_value = mock_api

        result = runner.invoke(oracle, ["plugins"])
        assert result.exit_code == 0
        mock_register.assert_called_once()

    @patch("flext_db_oracle.cli.FlextDbOracleApi.from_env")
    def test_health_command_success(
        self,
        mock_from_env: Mock,
        runner: CliRunner,
    ) -> None:
        """Test health command success."""
        # Mock API and successful health check
        mock_api = make_context_manager_mock()

        # Create proper health data mock
        mock_health_data = Mock()
        mock_health_data.status = "healthy"
        mock_health_data.component = "oracle-db"
        mock_health_data.message = "Database is healthy"
        mock_health_data.timestamp = Mock()
        mock_health_data.timestamp.isoformat.return_value = "2025-01-01T12:00:00"
        mock_health_data.metrics = {"connections": 5, "queries_per_sec": 10.5}

        mock_api.get_health_status.return_value = FlextResult.ok(mock_health_data)
        mock_from_env.return_value = mock_api

        result = runner.invoke(oracle, ["health"])
        assert result.exit_code == 0

    def test_connection_params_creation(self) -> None:
        """Test ConnectionParams dataclass creation."""
        params = ConnectionParams(
            host="localhost",
            port=1521,
            service_name="XE",
            username="test",
            password="secret",
        )

        assert params.host == "localhost"
        assert params.port == 1521
        assert params.service_name == "XE"
        assert params.username == "test"
        assert params.password == "secret"

    def test_safe_get_list_length_with_list(self) -> None:
        """Test _safe_get_list_length utility with list."""
        items = ["a", "b", "c"]
        count = _safe_get_list_length(items)
        assert count == 3

    def test_safe_get_list_length_with_dict(self) -> None:
        """Test _safe_get_list_length utility with dict."""
        items = {"a": 1, "b": 2}
        count = _safe_get_list_length(items)
        assert count == 2

    def test_safe_get_list_length_with_none(self) -> None:
        """Test _safe_get_list_length utility with None."""
        count = _safe_get_list_length(None)
        assert count == 0

    def test_safe_get_list_length_with_string(self) -> None:
        """Test _safe_get_list_length utility with string."""
        count = _safe_get_list_length("hello")
        assert count == 5

    def test_safe_get_list_length_with_invalid_type(self) -> None:
        """Test _safe_get_list_length utility with invalid type."""
        count = _safe_get_list_length(123)
        assert count == 0

    def test_extract_table_info_with_dict(self) -> None:
        """Test _extract_table_info with dict-like object."""
        table_info = {"name": "employees", "schema": "hr"}
        name, schema = _extract_table_info(table_info, None)
        assert name == "employees"
        assert schema == "hr"

    def test_extract_table_info_with_dict_missing_name(self) -> None:
        """Test _extract_table_info with dict missing name."""
        table_info = {"schema": "hr"}
        name, schema = _extract_table_info(table_info, None)
        assert name == str(table_info)
        assert schema == "hr"

    def test_extract_table_info_with_string(self) -> None:
        """Test _extract_table_info with string."""
        table_info = "employees"
        name, schema = _extract_table_info(table_info, "hr")
        assert name == "employees"
        assert schema == "hr"

    def test_extract_table_info_with_none_schema(self) -> None:
        """Test _extract_table_info with None schema."""
        table_info = "employees"
        name, schema = _extract_table_info(table_info, None)
        assert name == "employees"
        assert schema == ""


class TestCLIUtilityFunctions:
    """Test CLI utility functions."""

    def test_connection_params_with_defaults(self) -> None:
        """Test ConnectionParams with default values."""
        params = ConnectionParams(
            host="localhost",
            port=1521,
            service_name="XE",
            username="test",
            password="test",
        )

        # Test all attributes are set correctly
        assert params.host == "localhost"
        assert params.port == 1521
        assert params.service_name == "XE"
        assert params.username == "test"
        assert params.password == "test"

    def test_safe_get_list_length_edge_cases(self) -> None:
        """Test _safe_get_list_length with edge cases."""
        # Empty containers
        assert _safe_get_list_length([]) == 0
        assert _safe_get_list_length({}) == 0
        assert _safe_get_list_length("") == 0

        # Object without len
        class NoLen:
            pass

        assert _safe_get_list_length(NoLen()) == 0

    def test_extract_table_info_edge_cases(self) -> None:
        """Test _extract_table_info with edge cases."""
        # Dict with empty values
        table_info = {"name": "", "schema": ""}
        name, schema = _extract_table_info(table_info, "default")
        assert name == str(table_info)  # Falls back to str representation
        assert schema == ""

        # Dict with None values - when schema key exists but is None
        table_info = {"name": None, "schema": None}
        name, schema = _extract_table_info(table_info, "default")
        assert name == str(table_info)
        # When table_info["schema"] is None, get() returns None (key exists)
        # The default in get("schema", schema or "") is only used if key missing
        # Since key exists with None value, schema_name becomes None
        assert schema is None
