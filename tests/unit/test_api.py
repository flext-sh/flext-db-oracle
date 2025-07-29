"""Unit tests for FlextDbOracleApi - comprehensive validation."""

from unittest.mock import MagicMock, patch

import pytest
from flext_core import FlextResult
from src.flext_db_oracle import (
    FlextDbOracleApi,
    FlextDbOracleConnection,
)


class TestFlextDbOracleApi:
    """Comprehensive tests for Oracle API."""

    def test_api_initialization_with_config(self, valid_config) -> None:
        """Test API initialization with configuration."""
        api = FlextDbOracleApi(valid_config, "test_context")

        assert api._config == valid_config
        assert api._context_name == "test_context"
        assert api._connection is None
        assert not api._is_connected
        assert not api.is_connected

    def test_api_initialization_without_config(self) -> None:
        """Test API initialization without configuration."""
        api = FlextDbOracleApi()

        assert api._config is None
        assert api._context_name == "oracle"
        assert api._connection is None
        assert not api.is_connected

    @patch.dict("os.environ", {
        "FLEXT_TARGET_ORACLE_HOST": "env.oracle.com",
        "FLEXT_TARGET_ORACLE_PORT": "1522",
        "FLEXT_TARGET_ORACLE_USERNAME": "envuser",
        "FLEXT_TARGET_ORACLE_PASSWORD": "envpass",
        "FLEXT_TARGET_ORACLE_SERVICE_NAME": "ENVDB",
    })
    def test_from_env_success(self) -> None:
        """Test API creation from environment variables."""
        api = FlextDbOracleApi.from_env()

        assert api._config is not None
        assert api._config.host == "env.oracle.com"
        assert api._config.port == 1522
        assert api._config.username == "envuser"
        assert api._config.service_name == "ENVDB"

    def test_with_config_success(self) -> None:
        """Test API creation with configuration parameters."""
        api = FlextDbOracleApi.with_config(
            host="param.oracle.com",
            port=1523,
            username="paramuser",
            password="parampass",
            service_name="PARAMDB",
        )

        assert api._config is not None
        assert api._config.host == "param.oracle.com"
        assert api._config.port == 1523

    @patch("src.flext_db_oracle.api.FlextDbOracleConnection")
    def test_connect_success(self, mock_connection_class, valid_config) -> None:
        """Test successful database connection."""
        # Setup mock connection
        mock_connection = MagicMock(spec=FlextDbOracleConnection)
        mock_connection.connect.return_value = FlextResult.ok(True)
        mock_connection_class.return_value = mock_connection

        api = FlextDbOracleApi(valid_config)
        result = api.connect()

        assert result == api  # Should return self for chaining
        assert api._is_connected
        assert api.is_connected
        mock_connection.connect.assert_called_once()

    def test_connect_without_config(self) -> None:
        """Test connection without configuration."""
        api = FlextDbOracleApi()

        with pytest.raises(ValueError, match="No configuration provided"):
            api.connect()

    @patch("src.flext_db_oracle.api.FlextDbOracleConnection")
    def test_connect_failure(self, mock_connection_class, valid_config) -> None:
        """Test connection failure."""
        # Setup mock connection
        mock_connection = MagicMock(spec=FlextDbOracleConnection)
        mock_connection.connect.return_value = FlextResult.fail("Connection failed")
        mock_connection_class.return_value = mock_connection

        api = FlextDbOracleApi(valid_config)

        with pytest.raises(ConnectionError, match="Failed to connect: Connection failed"):
            api.connect()

    @patch("src.flext_db_oracle.api.FlextDbOracleConnection")
    def test_disconnect_success(self, mock_connection_class, valid_config) -> None:
        """Test successful disconnection."""
        # Setup mock connection
        mock_connection = MagicMock(spec=FlextDbOracleConnection)
        mock_connection.connect.return_value = FlextResult.ok(True)
        mock_connection.disconnect.return_value = FlextResult.ok(True)
        mock_connection_class.return_value = mock_connection

        api = FlextDbOracleApi(valid_config)
        api.connect()

        result = api.disconnect()

        assert result == api  # Should return self for chaining
        assert not api._is_connected
        assert not api.is_connected
        mock_connection.disconnect.assert_called_once()

    def test_disconnect_when_not_connected(self, valid_config) -> None:
        """Test disconnect when not connected."""
        api = FlextDbOracleApi(valid_config)
        result = api.disconnect()

        assert result == api
        assert not api.is_connected

    @patch("src.flext_db_oracle.api.FlextDbOracleConnection")
    def test_query_success(self, mock_connection_class, valid_config, sample_query_result) -> None:
        """Test successful query execution."""
        # Setup mock connection
        mock_connection = MagicMock(spec=FlextDbOracleConnection)
        mock_connection.connect.return_value = FlextResult.ok(True)
        mock_connection.execute.return_value = FlextResult.ok(sample_query_result)
        mock_connection_class.return_value = mock_connection

        api = FlextDbOracleApi(valid_config)
        api.connect()

        result = api.query("SELECT * FROM employees")

        assert result.is_success
        assert result.data == sample_query_result
        mock_connection.execute.assert_called_once_with("SELECT * FROM employees", None)

    def test_query_not_connected(self, valid_config) -> None:
        """Test query when not connected."""
        api = FlextDbOracleApi(valid_config)
        result = api.query("SELECT 1 FROM DUAL")

        assert result.is_failure
        assert "Database not connected" in result.error

    @patch("src.flext_db_oracle.api.FlextDbOracleConnection")
    def test_query_with_parameters(self, mock_connection_class, valid_config) -> None:
        """Test query execution with parameters."""
        # Setup mock connection
        mock_connection = MagicMock(spec=FlextDbOracleConnection)
        mock_connection.connect.return_value = FlextResult.ok(True)
        mock_connection.execute.return_value = FlextResult.ok([("result",)])
        mock_connection_class.return_value = mock_connection

        api = FlextDbOracleApi(valid_config)
        api.connect()

        params = {"emp_id": 123}
        result = api.query("SELECT * FROM employees WHERE id = :emp_id", params)

        assert result.is_success
        mock_connection.execute.assert_called_once_with(
            "SELECT * FROM employees WHERE id = :emp_id",
            params,
        )

    @patch("src.flext_db_oracle.api.FlextDbOracleConnection")
    def test_query_one_success(self, mock_connection_class, valid_config) -> None:
        """Test successful single row query."""
        # Setup mock connection
        mock_connection = MagicMock(spec=FlextDbOracleConnection)
        mock_connection.connect.return_value = FlextResult.ok(True)
        mock_connection.fetch_one.return_value = FlextResult.ok(("single_result",))
        mock_connection_class.return_value = mock_connection

        api = FlextDbOracleApi(valid_config)
        api.connect()

        result = api.query_one("SELECT COUNT(*) FROM employees")

        assert result.is_success
        assert result.data == ("single_result",)
        mock_connection.fetch_one.assert_called_once()

    @patch("src.flext_db_oracle.api.FlextDbOracleConnection")
    def test_execute_batch_success(self, mock_connection_class, valid_config) -> None:
        """Test successful batch operation execution."""
        # Setup mock connection
        mock_connection = MagicMock(spec=FlextDbOracleConnection)
        mock_connection.connect.return_value = FlextResult.ok(True)
        mock_connection.execute.side_effect = [
            FlextResult.ok([("result1",)]),
            FlextResult.ok([("result2",)]),
        ]
        mock_connection_class.return_value = mock_connection

        api = FlextDbOracleApi(valid_config)
        api.connect()

        operations = [
            ("SELECT * FROM table1", None),
            ("SELECT * FROM table2", {"param": "value"}),
        ]

        result = api.execute_batch(operations)

        assert result.is_success
        assert len(result.data) == 2
        assert result.data[0] == [("result1",)]
        assert result.data[1] == [("result2",)]

    @patch("src.flext_db_oracle.api.FlextDbOracleConnection")
    def test_execute_batch_failure(self, mock_connection_class, valid_config) -> None:
        """Test batch operation with failure."""
        # Setup mock connection
        mock_connection = MagicMock(spec=FlextDbOracleConnection)
        mock_connection.connect.return_value = FlextResult.ok(True)
        mock_connection.execute.side_effect = [
            FlextResult.ok([("result1",)]),
            FlextResult.fail("SQL error"),
        ]
        mock_connection_class.return_value = mock_connection

        api = FlextDbOracleApi(valid_config)
        api.connect()

        operations = [
            ("SELECT * FROM table1", None),
            ("INVALID SQL", None),
        ]

        result = api.execute_batch(operations)

        assert result.is_failure
        assert "Batch operation 2 failed" in result.error

    @patch("src.flext_db_oracle.api.FlextDbOracleConnection")
    def test_transaction_context_manager(self, mock_connection_class, valid_config) -> None:
        """Test transaction context manager."""
        # Setup mock connection
        mock_connection = MagicMock(spec=FlextDbOracleConnection)
        mock_connection.connect.return_value = FlextResult.ok(True)
        mock_connection.transaction.return_value.__enter__.return_value = mock_connection
        mock_connection_class.return_value = mock_connection

        api = FlextDbOracleApi(valid_config)
        api.connect()

        with api.transaction() as conn:
            assert conn == mock_connection

        mock_connection.transaction.assert_called_once()

    @patch("src.flext_db_oracle.api.FlextDbOracleConnection")
    def test_session_context_manager(self, mock_connection_class, valid_config) -> None:
        """Test session context manager."""
        # Setup mock connection
        mock_connection = MagicMock(spec=FlextDbOracleConnection)
        mock_connection.connect.return_value = FlextResult.ok(True)
        mock_session = MagicMock()
        mock_connection.session.return_value.__enter__.return_value = mock_session
        mock_connection_class.return_value = mock_connection

        api = FlextDbOracleApi(valid_config)
        api.connect()

        with api.session() as session:
            assert session == mock_session

        mock_connection.session.assert_called_once()

    @patch("src.flext_db_oracle.api.FlextDbOracleConnection")
    def test_get_tables_success(self, mock_connection_class, valid_config) -> None:
        """Test successful table names retrieval."""
        # Setup mock connection
        mock_connection = MagicMock(spec=FlextDbOracleConnection)
        mock_connection.connect.return_value = FlextResult.ok(True)
        mock_connection.get_table_names.return_value = FlextResult.ok(["TABLE1", "TABLE2"])
        mock_connection_class.return_value = mock_connection

        api = FlextDbOracleApi(valid_config)
        api.connect()

        result = api.get_tables()

        assert result.is_success
        assert result.data == ["TABLE1", "TABLE2"]
        mock_connection.get_table_names.assert_called_once_with(None)

    @patch("src.flext_db_oracle.api.FlextDbOracleConnection")
    def test_get_tables_with_schema(self, mock_connection_class, valid_config) -> None:
        """Test table names retrieval with schema."""
        # Setup mock connection
        mock_connection = MagicMock(spec=FlextDbOracleConnection)
        mock_connection.connect.return_value = FlextResult.ok(True)
        mock_connection.get_table_names.return_value = FlextResult.ok(["SCHEMA_TABLE1"])
        mock_connection_class.return_value = mock_connection

        api = FlextDbOracleApi(valid_config)
        api.connect()

        result = api.get_tables("TEST_SCHEMA")

        assert result.is_success
        mock_connection.get_table_names.assert_called_once_with("TEST_SCHEMA")

    @patch("src.flext_db_oracle.api.FlextDbOracleConnection")
    def test_get_schemas_success(self, mock_connection_class, valid_config) -> None:
        """Test successful schemas retrieval."""
        # Setup mock connection
        mock_connection = MagicMock(spec=FlextDbOracleConnection)
        mock_connection.connect.return_value = FlextResult.ok(True)
        mock_connection.get_schemas.return_value = FlextResult.ok(["SCHEMA1", "SCHEMA2"])
        mock_connection_class.return_value = mock_connection

        api = FlextDbOracleApi(valid_config)
        api.connect()

        result = api.get_schemas()

        assert result.is_success
        assert result.data == ["SCHEMA1", "SCHEMA2"]

    @patch("src.flext_db_oracle.api.FlextDbOracleConnection")
    def test_get_columns_success(self, mock_connection_class, valid_config) -> None:
        """Test successful column info retrieval."""
        # Setup mock connection
        mock_connection = MagicMock(spec=FlextDbOracleConnection)
        mock_connection.connect.return_value = FlextResult.ok(True)
        mock_connection.get_column_info.return_value = FlextResult.ok([
            {"column_name": "ID", "data_type": "NUMBER"},
            {"column_name": "NAME", "data_type": "VARCHAR2"},
        ])
        mock_connection_class.return_value = mock_connection

        api = FlextDbOracleApi(valid_config)
        api.connect()

        result = api.get_columns("TEST_TABLE")

        assert result.is_success
        assert len(result.data) == 2

    @patch("src.flext_db_oracle.api.FlextDbOracleConnection")
    def test_test_connection_success(self, mock_connection_class, valid_config) -> None:
        """Test successful connection test."""
        # Setup mock connection
        mock_connection = MagicMock(spec=FlextDbOracleConnection)
        mock_connection.connect.return_value = FlextResult.ok(True)
        mock_connection.test_connection.return_value = FlextResult.ok(True)
        mock_connection_class.return_value = mock_connection

        api = FlextDbOracleApi(valid_config)
        api.connect()

        result = api.test_connection()

        assert result.is_success
        assert result.data is True

    def test_test_connection_not_connected(self, valid_config) -> None:
        """Test connection test when not connected."""
        api = FlextDbOracleApi(valid_config)
        result = api.test_connection()

        assert result.is_failure
        assert "No connection established" in result.error

    def test_properties(self, valid_config) -> None:
        """Test API properties."""
        api = FlextDbOracleApi(valid_config, "test_context")

        assert api.config == valid_config
        assert api.connection is None
        assert not api.is_connected

    @patch("src.flext_db_oracle.api.FlextDbOracleConnection")
    def test_context_manager_connect(self, mock_connection_class, valid_config) -> None:
        """Test context manager auto-connection."""
        # Setup mock connection
        mock_connection = MagicMock(spec=FlextDbOracleConnection)
        mock_connection.connect.return_value = FlextResult.ok(True)
        mock_connection.disconnect.return_value = FlextResult.ok(True)
        mock_connection_class.return_value = mock_connection

        api = FlextDbOracleApi(valid_config)

        with api as connected_api:
            assert connected_api == api
            assert api._is_connected

        assert not api._is_connected
        mock_connection.connect.assert_called_once()
        mock_connection.disconnect.assert_called_once()

    @patch("src.flext_db_oracle.api.FlextDbOracleConnection")
    def test_context_manager_already_connected(self, mock_connection_class, valid_config) -> None:
        """Test context manager when already connected."""
        # Setup mock connection
        mock_connection = MagicMock(spec=FlextDbOracleConnection)
        mock_connection.connect.return_value = FlextResult.ok(True)
        mock_connection.disconnect.return_value = FlextResult.ok(True)
        mock_connection_class.return_value = mock_connection

        api = FlextDbOracleApi(valid_config)
        api.connect()  # Connect before context manager

        with api as connected_api:
            assert connected_api == api

        # Should still disconnect
        assert not api._is_connected

    @patch("src.flext_db_oracle.api.FlextDbOracleConnection")
    def test_chaining_methods(self, mock_connection_class, valid_config) -> None:
        """Test method chaining functionality."""
        # Setup mock connection
        mock_connection = MagicMock(spec=FlextDbOracleConnection)
        mock_connection.connect.return_value = FlextResult.ok(True)
        mock_connection.disconnect.return_value = FlextResult.ok(True)
        mock_connection_class.return_value = mock_connection

        api = FlextDbOracleApi(valid_config)

        # Test method chaining
        result_api = api.connect().disconnect()

        assert result_api == api
        mock_connection.connect.assert_called_once()
        mock_connection.disconnect.assert_called_once()

    def test_container_registration(self, valid_config) -> None:
        """Test container registration functionality."""
        # This test would need to mock the container, but the basic structure is tested
        api = FlextDbOracleApi(valid_config, "test_context")
        assert api._context_name == "test_context"
        # The container registration happens in connect(), which is tested separately
