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
    test_connection as cli_test_connection,
)


class TestTestConnection:
    """Test connection testing functionality."""

    @patch("flext_db_oracle.cli.main.FlextDbOracleConnection")
    @patch("flext_db_oracle.cli.main.FlextDbOracleConfig")
    def test_connection_success_with_args(
        self,
        mock_config_class: Mock,
        mock_conn_class: Mock,
    ) -> None:
        """Test successful connection with individual args."""
        # Setup config mock
        mock_config = Mock()
        mock_config.host = "localhost"
        mock_config.port = 1521
        mock_config.service_name = "testdb"
        mock_config.username = "testuser"
        mock_config.to_connection_config.return_value = Mock()
        mock_config_class.return_value = mock_config

        # Setup connection mock
        mock_conn = Mock()
        mock_conn.is_connected = True
        mock_conn.fetch_one.return_value = (1,)  # Return tuple for "SELECT 1 FROM DUAL"
        mock_conn.connect.return_value = None
        mock_conn.disconnect.return_value = None
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

        result = cli_test_connection(args)

        assert result == 0
        mock_config_class.assert_called_once()
        mock_conn.connect.assert_called_once()
        mock_conn.fetch_one.assert_called_once_with("SELECT 1 FROM DUAL")
        mock_conn.disconnect.assert_called_once()

    @patch("flext_db_oracle.cli.main.FlextDbOracleConnection")
    @patch("flext_db_oracle.cli.main.FlextDbOracleConfig")
    def test_connection_success_with_url(
        self,
        mock_config_class: Mock,
        mock_conn_class: Mock,
    ) -> None:
        """Test successful connection with URL."""
        # Setup config mock
        mock_config = Mock()
        mock_config.host = "host"
        mock_config.port = 1521
        mock_config.service_name = "service"
        mock_config.username = "user"
        mock_config.to_connection_config.return_value = Mock()
        mock_config_class.from_url.return_value = mock_config

        # Setup connection mock
        mock_conn = Mock()
        mock_conn.is_connected = True
        mock_conn.fetch_one.return_value = (1,)  # Return tuple for "SELECT 1 FROM DUAL"
        mock_conn.connect.return_value = None
        mock_conn.disconnect.return_value = None
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

        result = cli_test_connection(args)

        assert result == 0
        mock_config_class.from_url.assert_called_once_with(
            "oracle://user:pass@host:1521/service",
        )
        mock_conn.connect.assert_called_once()
        mock_conn.fetch_one.assert_called_once_with("SELECT 1 FROM DUAL")
        mock_conn.disconnect.assert_called_once()

    @patch("flext_db_oracle.cli.main.FlextDbOracleConnection")
    @patch("flext_db_oracle.cli.main.FlextDbOracleConfig")
    def test_connection_failure_not_connected(
        self,
        mock_config_class: Mock,
        mock_conn_class: Mock,
    ) -> None:
        """Test connection failure when connection cannot be established."""
        # Setup config mock
        mock_config = Mock()
        mock_config.to_connection_config.return_value = Mock()
        mock_config_class.return_value = mock_config

        # Setup connection mock to simulate connection failure
        mock_conn = Mock()
        mock_conn.is_connected = False  # Connection fails
        mock_conn.connect.return_value = None
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

        result = cli_test_connection(args)

        assert result == 1
        mock_conn.connect.assert_called_once()

    @patch("flext_db_oracle.cli.main.FlextDbOracleConnection")
    @patch("flext_db_oracle.cli.main.FlextDbOracleConfig")
    def test_connection_failure_no_query_result(
        self,
        mock_config_class: Mock,
        mock_conn_class: Mock,
    ) -> None:
        """Test connection failure when test query returns no result."""
        # Setup config mock
        mock_config = Mock()
        mock_config.to_connection_config.return_value = Mock()
        mock_config_class.return_value = mock_config

        # Setup connection mock
        mock_conn = Mock()
        mock_conn.is_connected = True
        mock_conn.fetch_one.return_value = None  # Query returns no result
        mock_conn.connect.return_value = None
        mock_conn.disconnect.return_value = None
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

        result = cli_test_connection(args)

        assert result == 1
        mock_conn.connect.assert_called_once()
        mock_conn.fetch_one.assert_called_once_with("SELECT 1 FROM DUAL")

    @patch("flext_db_oracle.cli.main.FlextDbOracleConnection")
    @patch("flext_db_oracle.cli.main.FlextDbOracleConfig")
    def test_connection_exception(
        self,
        mock_config_class: Mock,
        mock_conn_class: Mock,
    ) -> None:
        """Test connection failure due to exception."""
        # Setup config mock
        mock_config = Mock()
        mock_config.to_connection_config.return_value = Mock()
        mock_config_class.return_value = mock_config

        # Setup connection mock to raise exception
        mock_conn = Mock()
        mock_conn.connect.side_effect = Exception("Connection failed")
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

        result = cli_test_connection(args)

        assert result == 1


class TestListTables:
    """Test table listing functionality."""

    @patch("flext_db_oracle.cli.main.FlextDbOracleConnection")
    @patch("flext_db_oracle.cli.main.FlextDbOracleConfig")
    def test_list_tables_success(
        self,
        mock_config_class: Mock,
        mock_conn_class: Mock,
    ) -> None:
        """Test successful table listing."""
        # Setup config mock
        mock_config = Mock()
        mock_config.username = "testuser"
        mock_config.to_connection_config.return_value = Mock()
        mock_config_class.return_value = mock_config

        # Setup connection mock with fetch_all returning list of tuples
        mock_conn = Mock()
        mock_conn.connect.return_value = None
        mock_conn.disconnect.return_value = None
        mock_conn.fetch_all.return_value = [
            ("TABLE1", 100, "USERS"),
            ("TABLE2", 50, "USERS"),
            ("TABLE3", 200, "SYSTEM"),
        ]
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
        mock_conn.connect.assert_called_once()
        mock_conn.fetch_all.assert_called_once()
        mock_conn.disconnect.assert_called_once()

        # Verify the SQL query parameters
        call_args = mock_conn.fetch_all.call_args
        sql_query = call_args[0][0]
        parameters = call_args[0][1]

        assert "all_tables" in sql_query
        assert "owner = :schema" in sql_query
        assert parameters == {"schema": "testschema"}

    @patch("flext_db_oracle.cli.main.FlextDbOracleConnection")
    @patch("flext_db_oracle.cli.main.FlextDbOracleConfig")
    def test_list_tables_no_schema_uses_username(
        self,
        mock_config_class: Mock,
        mock_conn_class: Mock,
    ) -> None:
        """Test table listing when no schema provided uses username."""
        # Setup config mock
        mock_config = Mock()
        mock_config.username = "testuser"
        mock_config.to_connection_config.return_value = Mock()
        mock_config_class.return_value = mock_config

        # Setup connection mock
        mock_conn = Mock()
        mock_conn.connect.return_value = None
        mock_conn.disconnect.return_value = None
        mock_conn.fetch_all.return_value = [("TABLE1", 100, "USERS")]
        mock_conn_class.return_value = mock_conn

        # Create args without schema
        args = Namespace(
            schema=None,  # No schema provided
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

        # Verify the SQL query uses uppercase username as schema
        call_args = mock_conn.fetch_all.call_args
        parameters = call_args[0][1]
        assert parameters == {"schema": "TESTUSER"}  # Should be uppercase

    @patch("flext_db_oracle.cli.main.FlextDbOracleConnection")
    @patch("flext_db_oracle.cli.main.FlextDbOracleConfig")
    def test_list_tables_empty_results(
        self,
        mock_config_class: Mock,
        mock_conn_class: Mock,
    ) -> None:
        """Test table listing with no tables found."""
        # Setup config mock
        mock_config = Mock()
        mock_config.username = "testuser"
        mock_config.to_connection_config.return_value = Mock()
        mock_config_class.return_value = mock_config

        # Setup connection mock with empty results
        mock_conn = Mock()
        mock_conn.connect.return_value = None
        mock_conn.disconnect.return_value = None
        mock_conn.fetch_all.return_value = []  # No tables found
        mock_conn_class.return_value = mock_conn

        # Create args
        args = Namespace(
            schema="emptyschema",
            host="localhost",
            port=1521,
            service_name="testdb",
            username="testuser",
            password="testpass",
            url=None,
            sid=None,
        )

        result = list_tables(args)

        assert result == 0  # Should still return success with empty results
        mock_conn.connect.assert_called_once()
        mock_conn.fetch_all.assert_called_once()
        mock_conn.disconnect.assert_called_once()

    @patch("flext_db_oracle.cli.main.FlextDbOracleConnection")
    @patch("flext_db_oracle.cli.main.FlextDbOracleConfig")
    def test_list_tables_failure(
        self,
        mock_config_class: Mock,
        mock_conn_class: Mock,
    ) -> None:
        """Test table listing failure."""
        # Setup config mock
        mock_config = Mock()
        mock_config.username = "testuser"
        mock_config.to_connection_config.return_value = Mock()
        mock_config_class.return_value = mock_config

        # Setup connection mock to raise exception
        mock_conn = Mock()
        mock_conn.connect.side_effect = Exception("Connection failed")
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

    @patch("flext_db_oracle.cli.main.FlextDbOracleConnection")
    @patch("flext_db_oracle.cli.main.FlextDbOracleConfig")
    def test_describe_table_success(
        self,
        mock_config_class: Mock,
        mock_conn_class: Mock,
    ) -> None:
        """Test successful table description."""
        # Setup config mock
        mock_config = Mock()
        mock_config.username = "testuser"
        mock_config.to_connection_config.return_value = Mock()
        mock_config_class.return_value = mock_config

        # Setup connection mock with fetch_all returning column information
        mock_conn = Mock()
        mock_conn.connect.return_value = None
        mock_conn.disconnect.return_value = None
        mock_conn.fetch_all.return_value = [
            (
                "ID",
                "NUMBER",
                None,
                10,
                0,
                "N",
                None,
            ),  # column_name, data_type, data_length, data_precision, data_scale, nullable, data_default
            ("NAME", "VARCHAR2", 100, None, None, "Y", None),
            ("CREATED_DATE", "DATE", None, None, None, "N", "SYSDATE"),
        ]
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
        mock_conn.connect.assert_called_once()
        mock_conn.fetch_all.assert_called_once()
        mock_conn.disconnect.assert_called_once()

        # Verify the SQL query parameters
        call_args = mock_conn.fetch_all.call_args
        sql_query = call_args[0][0]
        parameters = call_args[0][1]

        assert "all_tab_columns" in sql_query
        assert "table_name = :table_name" in sql_query
        assert "owner = :schema" in sql_query
        assert parameters == {"table_name": "TESTTABLE", "schema": "testschema"}

    @patch("flext_db_oracle.cli.main.FlextDbOracleConnection")
    @patch("flext_db_oracle.cli.main.FlextDbOracleConfig")
    def test_describe_table_no_schema_uses_username(
        self,
        mock_config_class: Mock,
        mock_conn_class: Mock,
    ) -> None:
        """Test table description when no schema provided uses username."""
        # Setup config mock
        mock_config = Mock()
        mock_config.username = "testuser"
        mock_config.to_connection_config.return_value = Mock()
        mock_config_class.return_value = mock_config

        # Setup connection mock
        mock_conn = Mock()
        mock_conn.connect.return_value = None
        mock_conn.disconnect.return_value = None
        mock_conn.fetch_all.return_value = [
            ("ID", "NUMBER", None, 10, 0, "N", None),
        ]
        mock_conn_class.return_value = mock_conn

        # Create args without schema
        args = Namespace(
            table="testtable",
            schema=None,  # No schema provided
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

        # Verify the SQL query uses uppercase username as schema
        call_args = mock_conn.fetch_all.call_args
        parameters = call_args[0][1]
        assert parameters == {
            "table_name": "TESTTABLE",
            "schema": "TESTUSER",
        }  # Should be uppercase

    @patch("flext_db_oracle.cli.main.FlextDbOracleConnection")
    @patch("flext_db_oracle.cli.main.FlextDbOracleConfig")
    def test_describe_table_not_found(
        self,
        mock_config_class: Mock,
        mock_conn_class: Mock,
    ) -> None:
        """Test table description when table is not found."""
        # Setup config mock
        mock_config = Mock()
        mock_config.username = "testuser"
        mock_config.to_connection_config.return_value = Mock()
        mock_config_class.return_value = mock_config

        # Setup connection mock with empty results (table not found)
        mock_conn = Mock()
        mock_conn.connect.return_value = None
        mock_conn.disconnect.return_value = None
        mock_conn.fetch_all.return_value = []  # No columns found
        mock_conn_class.return_value = mock_conn

        # Create args
        args = Namespace(
            table="nonexistent",
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

        assert result == 1  # Should return error code for table not found
        mock_conn.connect.assert_called_once()
        mock_conn.fetch_all.assert_called_once()
        # disconnect() is NOT called when table is not found (returns early)

    @patch("flext_db_oracle.cli.main.FlextDbOracleConnection")
    @patch("flext_db_oracle.cli.main.FlextDbOracleConfig")
    def test_describe_table_failure(
        self,
        mock_config_class: Mock,
        mock_conn_class: Mock,
    ) -> None:
        """Test table description failure."""
        # Setup config mock
        mock_config = Mock()
        mock_config.username = "testuser"
        mock_config.to_connection_config.return_value = Mock()
        mock_config_class.return_value = mock_config

        # Setup connection mock to raise exception
        mock_conn = Mock()
        mock_conn.connect.side_effect = Exception("Connection failed")
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

        # Test that subcommands exist (using actual command names from CLI)
        # Note: Global arguments must come before the subcommand
        test_args = [
            [
                "--host",
                "localhost",
                "--service-name",
                "XE",
                "--username",
                "test",
                "--password",
                "pass",
                "test",
            ],
            [
                "--schema",
                "test",
                "--host",
                "localhost",
                "--service-name",
                "XE",
                "--username",
                "test",
                "--password",
                "pass",
                "tables",
            ],
            [
                "--schema",
                "test",
                "--host",
                "localhost",
                "--service-name",
                "XE",
                "--username",
                "test",
                "--password",
                "pass",
                "describe",
                "testtable",
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
        mock_args.command = "test"
        mock_args.func = mock_test_connection  # Set the function to be called
        mock_parser.return_value.parse_args.return_value = mock_args
        mock_test_connection.return_value = 0

        with patch("sys.argv", ["flext-db-oracle", "test"]):
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
        mock_args.command = "tables"
        mock_args.func = mock_list_tables  # Set the function to be called
        mock_parser.return_value.parse_args.return_value = mock_args
        mock_list_tables.return_value = 0

        with patch("sys.argv", ["flext-db-oracle", "tables"]):
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
        mock_args.command = "test"
        mock_args.func = mock_test_connection  # Set the function to be called
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

    @patch("flext_db_oracle.cli.main.FlextDbOracleConnection")
    @patch("flext_db_oracle.cli.main.FlextDbOracleConfig")
    def test_full_cli_workflow(
        self,
        mock_config_class: Mock,
        mock_conn_class: Mock,
    ) -> None:
        """Test complete CLI workflow simulation."""
        # Setup config mock
        mock_config = Mock()
        mock_config.host = "localhost"
        mock_config.port = 1521
        mock_config.service_name = "testdb"
        mock_config.username = "testuser"
        mock_config.to_connection_config.return_value = Mock()
        mock_config_class.return_value = mock_config

        # Setup connection mock that matches the actual CLI calls
        mock_conn = Mock()

        # Mock connection behavior
        mock_conn.connect.return_value = None
        mock_conn.disconnect.return_value = None
        mock_conn.is_connected = True

        # Mock for test_connection: fetch_one("SELECT 1 FROM DUAL")
        mock_conn.fetch_one.return_value = (1,)

        # Mock for list_tables: fetch_all with table data
        mock_conn.fetch_all.return_value = [
            ("TABLE1", 100, "USERS"),
            ("TABLE2", 50, "USERS"),
        ]

        mock_conn_class.return_value = mock_conn

        # Test connection workflow
        args = Namespace(
            url=None,
            host="localhost",
            port=1521,
            sid=None,
            service_name="testdb",
            username="testuser",
            password="testpass",
        )

        # Test connection command
        result = cli_test_connection(args)
        assert result == 0
        mock_conn.connect.assert_called()
        mock_conn.fetch_one.assert_called_with("SELECT 1 FROM DUAL")
        mock_conn.disconnect.assert_called()

        # Reset mock call counts for next test
        mock_conn.reset_mock()
        mock_conn.connect.return_value = None
        mock_conn.disconnect.return_value = None
        mock_conn.fetch_all.return_value = [
            ("TABLE1", 100, "USERS"),
            ("TABLE2", 50, "USERS"),
        ]

        # Test list tables workflow
        args.schema = "testschema"
        result = list_tables(args)
        assert result == 0
        mock_conn.connect.assert_called_once()
        mock_conn.fetch_all.assert_called_once()
        mock_conn.disconnect.assert_called_once()

        # Verify list_tables called with correct SQL
        call_args = mock_conn.fetch_all.call_args
        sql_query = call_args[0][0]
        parameters = call_args[0][1]
        assert "all_tables" in sql_query
        assert parameters == {"schema": "testschema"}

        # Reset mock call counts for describe table test
        mock_conn.reset_mock()
        mock_conn.connect.return_value = None
        mock_conn.disconnect.return_value = None
        mock_conn.fetch_all.return_value = [
            ("ID", "NUMBER", None, 10, 0, "N", None),
            ("NAME", "VARCHAR2", 100, None, None, "Y", None),
        ]

        # Test describe table workflow
        args.table = "testtable"
        result = describe_table(args)
        assert result == 0
        mock_conn.connect.assert_called_once()
        mock_conn.fetch_all.assert_called_once()
        mock_conn.disconnect.assert_called_once()

        # Verify describe_table called with correct SQL
        call_args = mock_conn.fetch_all.call_args
        sql_query = call_args[0][0]
        parameters = call_args[0][1]
        assert "all_tab_columns" in sql_query
        assert parameters == {"table_name": "TESTTABLE", "schema": "testschema"}

    def test_help_output(self) -> None:
        """Test help output is generated."""
        parser = setup_parser()

        # Should not raise exception
        with pytest.raises(SystemExit):
            parser.parse_args(["--help"])
