"""Unit tests for FlextDbOracleConnection - comprehensive validation."""

from typing import Never
from unittest.mock import MagicMock, patch

import pytest
from sqlalchemy.engine import Engine
from src.flext_db_oracle import FlextDbOracleConfig, FlextDbOracleConnection


class TestFlextDbOracleConnection:
    """Comprehensive tests for Oracle connection."""

    def test_connection_initialization(self, valid_config) -> None:
        """Test connection initialization."""
        connection = FlextDbOracleConnection(valid_config)

        assert connection.config == valid_config
        assert connection._engine is None
        assert connection._session_factory is None
        assert not connection.is_connected()

    @patch("src.flext_db_oracle.connection.create_engine")
    def test_connect_success(self, mock_create_engine, valid_config) -> None:
        """Test successful database connection."""
        # Mock engine and connection
        mock_engine = MagicMock(spec=Engine)
        mock_connection = MagicMock()
        mock_engine.connect.return_value.__enter__.return_value = mock_connection
        mock_create_engine.return_value = mock_engine

        connection = FlextDbOracleConnection(valid_config)
        result = connection.connect()

        assert result.is_success
        assert result.data is True
        assert connection.is_connected()
        mock_create_engine.assert_called_once()

    @patch("src.flext_db_oracle.connection.create_engine")
    def test_connect_failure(self, mock_create_engine, valid_config) -> None:
        """Test connection failure."""
        mock_create_engine.side_effect = Exception("Connection failed")

        connection = FlextDbOracleConnection(valid_config)
        result = connection.connect()

        assert result.is_failure
        assert "Connection failed" in result.error
        assert not connection.is_connected()

    def test_connect_with_invalid_config(self, invalid_config) -> None:
        """Test connection with invalid configuration."""
        connection = FlextDbOracleConnection(invalid_config)
        result = connection.connect()

        assert result.is_failure
        assert "Configuration invalid" in result.error

    @patch("src.flext_db_oracle.connection.create_engine")
    def test_disconnect_success(self, mock_create_engine, valid_config) -> None:
        """Test successful disconnection."""
        mock_engine = MagicMock(spec=Engine)
        mock_connection = MagicMock()
        mock_engine.connect.return_value.__enter__.return_value = mock_connection
        mock_create_engine.return_value = mock_engine

        connection = FlextDbOracleConnection(valid_config)
        connection.connect()

        result = connection.disconnect()

        assert result.is_success
        assert result.data is True
        assert not connection.is_connected()
        mock_engine.dispose.assert_called_once()

    def test_disconnect_when_not_connected(self, valid_config) -> None:
        """Test disconnect when not connected."""
        connection = FlextDbOracleConnection(valid_config)
        result = connection.disconnect()

        assert result.is_success
        assert result.data is True

    @patch("src.flext_db_oracle.connection.create_engine")
    def test_execute_select_success(self, mock_create_engine, valid_config) -> None:
        """Test successful SELECT execution."""
        # Setup mocks
        mock_engine = MagicMock(spec=Engine)
        mock_connection = MagicMock()
        mock_result = MagicMock()
        mock_result.fetchall.return_value = [("row1",), ("row2",)]
        mock_connection.execute.return_value = mock_result
        mock_engine.connect.return_value.__enter__.return_value = mock_connection
        mock_create_engine.return_value = mock_engine

        connection = FlextDbOracleConnection(valid_config)
        connection.connect()

        result = connection.execute("SELECT * FROM test_table")

        assert result.is_success
        assert result.data == [("row1",), ("row2",)]

    @patch("src.flext_db_oracle.connection.create_engine")
    def test_execute_dml_success(self, mock_create_engine, valid_config) -> None:
        """Test successful DML execution."""
        # Setup mocks
        mock_engine = MagicMock(spec=Engine)
        mock_connection = MagicMock()
        mock_result = MagicMock()
        mock_result.rowcount = 5
        mock_connection.execute.return_value = mock_result
        mock_engine.connect.return_value.__enter__.return_value = mock_connection
        mock_create_engine.return_value = mock_engine

        connection = FlextDbOracleConnection(valid_config)
        connection.connect()

        result = connection.execute("INSERT INTO test_table VALUES (:1)", {"1": "value"})

        assert result.is_success
        assert result.data == [5]
        mock_connection.commit.assert_called_once()

    def test_execute_not_connected(self, valid_config) -> None:
        """Test execute when not connected."""
        connection = FlextDbOracleConnection(valid_config)
        result = connection.execute("SELECT 1 FROM DUAL")

        assert result.is_failure
        assert "Not connected to database" in result.error

    @patch("src.flext_db_oracle.connection.create_engine")
    def test_execute_sql_error(self, mock_create_engine, valid_config) -> None:
        """Test execute with SQL error."""
        # Setup mocks
        mock_engine = MagicMock(spec=Engine)
        mock_connection = MagicMock()
        mock_connection.execute.side_effect = Exception("SQL Error")
        mock_engine.connect.return_value.__enter__.return_value = mock_connection
        mock_create_engine.return_value = mock_engine

        connection = FlextDbOracleConnection(valid_config)
        connection.connect()

        result = connection.execute("INVALID SQL")

        assert result.is_failure
        assert "SQL execution failed" in result.error

    @patch("src.flext_db_oracle.connection.create_engine")
    def test_execute_many_success(self, mock_create_engine, valid_config) -> None:
        """Test successful batch execution."""
        # Setup mocks
        mock_engine = MagicMock(spec=Engine)
        mock_connection = MagicMock()
        mock_result = MagicMock()
        mock_result.rowcount = 3
        mock_connection.execute.return_value = mock_result
        mock_engine.connect.return_value.__enter__.return_value = mock_connection
        mock_create_engine.return_value = mock_engine

        connection = FlextDbOracleConnection(valid_config)
        connection.connect()

        params_list = [{"id": 1}, {"id": 2}, {"id": 3}]
        result = connection.execute_many("INSERT INTO test VALUES (:id)", params_list)

        assert result.is_success
        assert result.data == 3

    @patch("src.flext_db_oracle.connection.create_engine")
    def test_fetch_one_success(self, mock_create_engine, valid_config) -> None:
        """Test successful single row fetch."""
        # Setup mocks
        mock_engine = MagicMock(spec=Engine)
        mock_connection = MagicMock()
        mock_result = MagicMock()
        mock_result.fetchone.return_value = ("single_row",)
        mock_connection.execute.return_value = mock_result
        mock_engine.connect.return_value.__enter__.return_value = mock_connection
        mock_create_engine.return_value = mock_engine

        connection = FlextDbOracleConnection(valid_config)
        connection.connect()

        result = connection.fetch_one("SELECT COUNT(*) FROM test_table")

        assert result.is_success
        assert result.data == ("single_row",)

    @patch("src.flext_db_oracle.connection.create_engine")
    def test_session_context_manager(self, mock_create_engine, valid_config) -> None:
        """Test session context manager."""
        # Setup mocks
        mock_engine = MagicMock(spec=Engine)
        mock_session = MagicMock()
        mock_session_factory = MagicMock(return_value=mock_session)
        mock_connection = MagicMock()
        mock_engine.connect.return_value.__enter__.return_value = mock_connection
        mock_create_engine.return_value = mock_engine

        connection = FlextDbOracleConnection(valid_config)
        connection.connect()
        connection._session_factory = mock_session_factory

        with connection.session() as session:
            assert session == mock_session

        mock_session.commit.assert_called_once()
        mock_session.close.assert_called_once()

    @patch("src.flext_db_oracle.connection.create_engine")
    def test_session_rollback_on_error(self, mock_create_engine, valid_config) -> Never:
        """Test session rollback on error."""
        # Setup mocks
        mock_engine = MagicMock(spec=Engine)
        mock_session = MagicMock()
        mock_session_factory = MagicMock(return_value=mock_session)
        mock_connection = MagicMock()
        mock_engine.connect.return_value.__enter__.return_value = mock_connection
        mock_create_engine.return_value = mock_engine

        connection = FlextDbOracleConnection(valid_config)
        connection.connect()
        connection._session_factory = mock_session_factory

        with pytest.raises(Exception, match="Test error"), connection.session():
            msg = "Test error"
            raise Exception(msg)

        mock_session.rollback.assert_called_once()
        mock_session.close.assert_called_once()

    @patch("src.flext_db_oracle.connection.create_engine")
    def test_transaction_context_manager(self, mock_create_engine, valid_config) -> None:
        """Test transaction context manager."""
        # Setup mocks
        mock_engine = MagicMock(spec=Engine)
        mock_connection = MagicMock()
        mock_transaction = MagicMock()
        mock_connection.begin.return_value = mock_transaction
        mock_engine.connect.return_value.__enter__.return_value = mock_connection
        mock_create_engine.return_value = mock_engine

        connection = FlextDbOracleConnection(valid_config)
        connection.connect()

        with connection.transaction() as conn:
            assert conn == mock_connection

        mock_transaction.commit.assert_called_once()

    @patch("src.flext_db_oracle.connection.create_engine")
    def test_transaction_rollback_on_error(self, mock_create_engine, valid_config) -> Never:
        """Test transaction rollback on error."""
        # Setup mocks
        mock_engine = MagicMock(spec=Engine)
        mock_connection = MagicMock()
        mock_transaction = MagicMock()
        mock_connection.begin.return_value = mock_transaction
        mock_engine.connect.return_value.__enter__.return_value = mock_connection
        mock_create_engine.return_value = mock_engine

        connection = FlextDbOracleConnection(valid_config)
        connection.connect()

        with pytest.raises(Exception, match="Test error"):
            with connection.transaction():
                msg = "Test error"
                raise Exception(msg)

        mock_transaction.rollback.assert_called_once()

    @patch("src.flext_db_oracle.connection.create_engine")
    def test_test_connection_success(self, mock_create_engine, valid_config) -> None:
        """Test successful connection test."""
        # Setup mocks
        mock_engine = MagicMock(spec=Engine)
        mock_connection = MagicMock()
        mock_result = MagicMock()
        mock_result.fetchall.return_value = [("1",)]
        mock_connection.execute.return_value = mock_result
        mock_engine.connect.return_value.__enter__.return_value = mock_connection
        mock_create_engine.return_value = mock_engine

        connection = FlextDbOracleConnection(valid_config)
        connection.connect()

        result = connection.test_connection()

        assert result.is_success
        assert result.data is True

    def test_test_connection_not_connected(self, valid_config) -> None:
        """Test connection test when not connected."""
        connection = FlextDbOracleConnection(valid_config)
        result = connection.test_connection()

        assert result.is_failure
        assert "Not connected" in result.error

    @patch("src.flext_db_oracle.connection.create_engine")
    def test_get_table_names_success(self, mock_create_engine, valid_config) -> None:
        """Test successful table names retrieval."""
        # Setup mocks
        mock_engine = MagicMock(spec=Engine)
        mock_connection = MagicMock()
        mock_result = MagicMock()
        mock_result.fetchall.return_value = [("TABLE1",), ("TABLE2",)]
        mock_connection.execute.return_value = mock_result
        mock_engine.connect.return_value.__enter__.return_value = mock_connection
        mock_create_engine.return_value = mock_engine

        connection = FlextDbOracleConnection(valid_config)
        connection.connect()

        result = connection.get_table_names()

        assert result.is_success
        assert result.data == ["TABLE1", "TABLE2"]

    @patch("src.flext_db_oracle.connection.create_engine")
    def test_get_table_names_with_schema(self, mock_create_engine, valid_config) -> None:
        """Test table names retrieval with specific schema."""
        # Setup mocks
        mock_engine = MagicMock(spec=Engine)
        mock_connection = MagicMock()
        mock_result = MagicMock()
        mock_result.fetchall.return_value = [("SCHEMA_TABLE1",), ("SCHEMA_TABLE2",)]
        mock_connection.execute.return_value = mock_result
        mock_engine.connect.return_value.__enter__.return_value = mock_connection
        mock_create_engine.return_value = mock_engine

        connection = FlextDbOracleConnection(valid_config)
        connection.connect()

        result = connection.get_table_names("TEST_SCHEMA")

        assert result.is_success
        assert result.data == ["SCHEMA_TABLE1", "SCHEMA_TABLE2"]

    @patch("src.flext_db_oracle.connection.create_engine")
    def test_get_schemas_success(self, mock_create_engine, valid_config) -> None:
        """Test successful schemas retrieval."""
        # Setup mocks
        mock_engine = MagicMock(spec=Engine)
        mock_connection = MagicMock()
        mock_result = MagicMock()
        mock_result.fetchall.return_value = [("SCHEMA1",), ("SCHEMA2",)]
        mock_connection.execute.return_value = mock_result
        mock_engine.connect.return_value.__enter__.return_value = mock_connection
        mock_create_engine.return_value = mock_engine

        connection = FlextDbOracleConnection(valid_config)
        connection.connect()

        result = connection.get_schemas()

        assert result.is_success
        assert result.data == ["SCHEMA1", "SCHEMA2"]

    @patch("src.flext_db_oracle.connection.create_engine")
    def test_get_column_info_success(self, mock_create_engine, valid_config) -> None:
        """Test successful column info retrieval."""
        # Setup mocks
        mock_engine = MagicMock(spec=Engine)
        mock_connection = MagicMock()
        mock_result = MagicMock()
        mock_result.fetchall.return_value = [
            ("ID", "NUMBER", "N", None, 10, 0, 1),
            ("NAME", "VARCHAR2", "Y", 50, None, None, 2),
        ]
        mock_connection.execute.return_value = mock_result
        mock_engine.connect.return_value.__enter__.return_value = mock_connection
        mock_create_engine.return_value = mock_engine

        connection = FlextDbOracleConnection(valid_config)
        connection.connect()

        result = connection.get_column_info("TEST_TABLE")

        assert result.is_success
        assert len(result.data) == 2
        assert result.data[0]["column_name"] == "ID"
        assert result.data[0]["nullable"] is False
        assert result.data[1]["column_name"] == "NAME"
        assert result.data[1]["nullable"] is True

    def test_build_connection_url_service_name(self, valid_config) -> None:
        """Test connection URL building with service name."""
        connection = FlextDbOracleConnection(valid_config)
        result = connection._build_connection_url()

        assert result.is_success
        expected_url = "oracle+oracledb://testuser:testpass@localhost:1521/?service_name=ORCLCDB"
        assert result.data == expected_url

    def test_build_connection_url_sid(self) -> None:
        """Test connection URL building with SID."""
        config = FlextDbOracleConfig(
            host="localhost",
            port=1521,
            username="testuser",
            password="testpass",
            sid="ORCL",
        )

        connection = FlextDbOracleConnection(config)
        result = connection._build_connection_url()

        assert result.is_success
        expected_url = "oracle+oracledb://testuser:testpass@localhost:1521/ORCL"
        assert result.data == expected_url

    def test_build_connection_url_no_identifier(self) -> None:
        """Test connection URL building without service name or SID."""
        config = FlextDbOracleConfig(
            host="localhost",
            port=1521,
            username="testuser",
            password="testpass",
        )

        connection = FlextDbOracleConnection(config)
        result = connection._build_connection_url()

        assert result.is_failure
        assert "Must provide either service_name or sid" in result.error
