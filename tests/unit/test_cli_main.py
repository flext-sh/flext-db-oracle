"""Tests for CLI main module.

Tests for the command line interface functionality.
"""

from __future__ import annotations

from argparse import Namespace
from unittest.mock import Mock, patch

import pytest

from flext_db_oracle.cli.main import (
    describe_table,
    list_tables,
    main,
    setup_parser,
    test_connection,
)


class TestTestConnection:
    """Test connection testing functionality."""

    @patch("flext_db_oracle.connection.connection.OracleConnection")
    @patch("flext_db_oracle.connection.config.ConnectionConfig")
    def test_connection_success_with_args(
        self,
        mock_config_class: Mock,
        mock_conn_class: Mock,
    ) -> None:
        """Test successful connection with individual args."""
        # Setup mocks
        mock_config = Mock()
        mock_config_class.return_value = mock_config

        mock_conn = Mock()
        mock_conn.test_connection.return_value = True
        mock_conn_class.return_value = mock_conn

        # Create args
        args = Namespace(
            url=None,
            host="localhost",
            port=1521,
            sid=None,
            service_name="testdb",
            username="testuser",
            password="testpass",
        )

        result = test_connection(args)

        assert result == 0
        mock_config_class.assert_called_once()
        mock_conn_class.assert_called_once_with(mock_config)

    @patch("flext_db_oracle.connection.connection.OracleConnection")
    @patch("flext_db_oracle.connection.config.ConnectionConfig.from_url")
    def test_connection_success_with_url(
        self,
        mock_from_url: Mock,
        mock_conn_class: Mock,
    ) -> None:
        """Test successful connection with URL."""
        # Setup mocks
        mock_config = Mock()
        mock_from_url.return_value = mock_config

        mock_conn = Mock()
        mock_conn.test_connection.return_value = True
        mock_conn_class.return_value = mock_conn

        # Create args with URL
        args = Namespace(
            url="oracle://user:pass@host:1521/service",
            host=None,
            port=None,
            sid=None,
            service_name=None,
            username=None,
            password=None,
        )

        result = test_connection(args)

        assert result == 0
        mock_from_url.assert_called_once_with("oracle://user:pass@host:1521/service")

    @patch("flext_db_oracle.connection.connection.OracleConnection")
    @patch("flext_db_oracle.connection.config.ConnectionConfig")
    def test_connection_failure(
        self,
        mock_config_class: Mock,
        mock_conn_class: Mock,
    ) -> None:
        """Test connection failure."""
        # Setup mocks
        mock_config = Mock()
        mock_config_class.return_value = mock_config

        mock_conn = Mock()
        mock_conn.test_connection.side_effect = Exception("Connection failed")
        mock_conn_class.return_value = mock_conn

        # Create args
        args = Namespace(
            url=None,
            host="localhost",
            port=1521,
            sid=None,
            service_name="testdb",
            username="testuser",
            password="testpass",
        )

        result = test_connection(args)

        assert result == 1


class TestListTables:
    """Test table listing functionality."""

    @patch("flext_db_oracle.connection.connection.OracleConnection")
    @patch("flext_db_oracle.connection.config.ConnectionConfig")
    def test_list_tables_success(
        self,
        mock_config_class: Mock,
        mock_conn_class: Mock,
    ) -> None:
        """Test successful table listing."""
        # Setup mocks
        mock_config = Mock()
        mock_config_class.return_value = mock_config

        mock_conn = Mock()
        mock_conn.list_tables.return_value = ["table1", "table2", "table3"]
        mock_conn_class.return_value = mock_conn

        # Create args
        args = Namespace(
            schema="testschema",
            host="localhost",
            port=1521,
            service_name="testdb",
            username="testuser",
            password="testpass",
            url=None,
            sid=None,
        )

        result = list_tables(args)

        assert result == 0
        mock_conn.list_tables.assert_called_once_with("testschema")

    @patch("flext_db_oracle.connection.connection.OracleConnection")
    @patch("flext_db_oracle.connection.config.ConnectionConfig")
    def test_list_tables_failure(
        self,
        mock_config_class: Mock,
        mock_conn_class: Mock,
    ) -> None:
        """Test table listing failure."""
        # Setup mocks
        mock_config = Mock()
        mock_config_class.return_value = mock_config

        mock_conn = Mock()
        mock_conn.list_tables.side_effect = Exception("List tables failed")
        mock_conn_class.return_value = mock_conn

        # Create args
        args = Namespace(
            schema="testschema",
            host="localhost",
            port=1521,
            service_name="testdb",
            username="testuser",
            password="testpass",
            url=None,
            sid=None,
        )

        result = list_tables(args)

        assert result == 1


class TestDescribeTable:
    """Test table description functionality."""

    @patch("flext_db_oracle.connection.connection.OracleConnection")
    @patch("flext_db_oracle.connection.config.ConnectionConfig")
    def test_describe_table_success(
        self,
        mock_config_class: Mock,
        mock_conn_class: Mock,
    ) -> None:
        """Test successful table description."""
        # Setup mocks
        mock_config = Mock()
        mock_config_class.return_value = mock_config

        mock_conn = Mock()
        mock_conn.describe_table.return_value = {
            "columns": [
                {"name": "id", "type": "NUMBER", "nullable": False},
                {"name": "name", "type": "VARCHAR2", "nullable": True},
            ],
        }
        mock_conn_class.return_value = mock_conn

        # Create args
        args = Namespace(
            table="testtable",
            schema="testschema",
            host="localhost",
            port=1521,
            service_name="testdb",
            username="testuser",
            password="testpass",
            url=None,
            sid=None,
        )

        result = describe_table(args)

        assert result == 0
        mock_conn.describe_table.assert_called_once_with("testtable", "testschema")

    @patch("flext_db_oracle.connection.connection.OracleConnection")
    @patch("flext_db_oracle.connection.config.ConnectionConfig")
    def test_describe_table_failure(
        self,
        mock_config_class: Mock,
        mock_conn_class: Mock,
    ) -> None:
        """Test table description failure."""
        # Setup mocks
        mock_config = Mock()
        mock_config_class.return_value = mock_config

        mock_conn = Mock()
        mock_conn.describe_table.side_effect = Exception("Describe failed")
        mock_conn_class.return_value = mock_conn

        # Create args
        args = Namespace(
            table="testtable",
            schema="testschema",
            host="localhost",
            port=1521,
            service_name="testdb",
            username="testuser",
            password="testpass",
            url=None,
            sid=None,
        )

        result = describe_table(args)

        assert result == 1


class TestParser:
    """Test argument parser creation."""

    def test_setup_parser(self) -> None:
        """Test parser creation."""
        parser = setup_parser()

        assert parser is not None
        assert hasattr(parser, "parse_args")

        # Test parsing help doesn't raise
        with pytest.raises(SystemExit):
            parser.parse_args(["--help"])

    def test_parser_subcommands(self) -> None:
        """Test parser has expected subcommands."""
        parser = setup_parser()

        # Test that subcommands exist
        test_args = [
            [
                "test-connection",
                "--host",
                "localhost",
                "--username",
                "test",
                "--password",
                "pass",
            ],
            [
                "list-tables",
                "--schema",
                "test",
                "--host",
                "localhost",
                "--username",
                "test",
                "--password",
                "pass",
            ],
            [
                "describe-table",
                "--table",
                "test",
                "--schema",
                "test",
                "--host",
                "localhost",
                "--username",
                "test",
                "--password",
                "pass",
            ],
        ]

        for args in test_args:
            parsed = parser.parse_args(args)
            assert parsed is not None


class TestMain:
    """Test main function."""

    @patch("flext_db_oracle.cli.main.test_connection")
    @patch("flext_db_oracle.cli.main.setup_parser")
    def test_main_with_test_connection(
        self,
        mock_parser: Mock,
        mock_test_connection: Mock,
    ) -> None:
        """Test main function with test-connection command."""
        # Setup mocks
        mock_args = Mock()
        mock_args.command = "test-connection"
        mock_parser.return_value.parse_args.return_value = mock_args
        mock_test_connection.return_value = 0

        with patch("sys.argv", ["flext-db-oracle", "test-connection"]):
            result = main()

        assert result == 0
        mock_test_connection.assert_called_once_with(mock_args)

    @patch("flext_db_oracle.cli.main.list_tables")
    @patch("flext_db_oracle.cli.main.setup_parser")
    def test_main_with_list_tables(
        self,
        mock_parser: Mock,
        mock_list_tables: Mock,
    ) -> None:
        """Test main function with list-tables command."""
        # Setup mocks
        mock_args = Mock()
        mock_args.command = "list-tables"
        mock_parser.return_value.parse_args.return_value = mock_args
        mock_list_tables.return_value = 0

        with patch("sys.argv", ["flext-db-oracle", "list-tables"]):
            result = main()

        assert result == 0
        mock_list_tables.assert_called_once_with(mock_args)

    @patch("flext_db_oracle.cli.main.setup_parser")
    def test_main_no_command(self, mock_parser: Mock) -> None:
        """Test main function with no command."""
        # Setup mocks
        mock_args = Mock()
        mock_args.command = None
        mock_parser.return_value.parse_args.return_value = mock_args
        mock_parser.return_value.print_help = Mock()

        result = main()

        assert result == 1
        mock_parser.return_value.print_help.assert_called_once()

    @patch("flext_db_oracle.cli.main.test_connection")
    @patch("flext_db_oracle.cli.main.setup_parser")
    def test_main_command_failure(
        self,
        mock_parser: Mock,
        mock_test_connection: Mock,
    ) -> None:
        """Test main function when command fails."""
        # Setup mocks
        mock_args = Mock()
        mock_args.command = "test-connection"
        mock_parser.return_value.parse_args.return_value = mock_args
        mock_test_connection.return_value = 1

        result = main()

        assert result == 1

    @patch("flext_db_oracle.cli.main.setup_parser")
    def test_main_with_exception(self, mock_parser: Mock) -> None:
        """Test main function handles exceptions."""
        # Setup mocks to raise exception
        mock_parser.return_value.parse_args.side_effect = Exception("Parse error")

        result = main()

        assert result == 1


class TestIntegrationScenarios:
    """Test CLI integration scenarios."""

    @patch("flext_db_oracle.connection.connection.OracleConnection")
    @patch("flext_db_oracle.connection.config.ConnectionConfig")
    def test_full_cli_workflow(
        self,
        mock_config_class: Mock,
        mock_conn_class: Mock,
    ) -> None:
        """Test complete CLI workflow simulation."""
        # Setup mocks
        mock_config = Mock()
        mock_config_class.return_value = mock_config

        mock_conn = Mock()
        mock_conn.test_connection.return_value = True
        mock_conn.list_tables.return_value = ["table1", "table2"]
        mock_conn.describe_table.return_value = {"columns": []}
        mock_conn_class.return_value = mock_conn

        # Test connection
        args = Namespace(
            url=None,
            host="localhost",
            port=1521,
            sid=None,
            service_name="testdb",
            username="testuser",
            password="testpass",
        )

        # Test connection
        result = test_connection(args)
        assert result == 0

        # Test list tables
        args.schema = "testschema"
        result = list_tables(args)
        assert result == 0

        # Test describe table
        args.table = "testtable"
        result = describe_table(args)
        assert result == 0

    def test_help_output(self) -> None:
        """Test help output is generated."""
        parser = setup_parser()

        # Should not raise exception
        with pytest.raises(SystemExit):
            parser.parse_args(["--help"])
