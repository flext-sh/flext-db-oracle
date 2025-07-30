"""Unit tests for FlextDbOracleConnection - comprehensive validation."""

from __future__ import annotations

from typing import TYPE_CHECKING
from unittest.mock import MagicMock, patch

import pytest
from flext_core import FlextResult
from sqlalchemy.engine import Engine

from flext_db_oracle import FlextDbOracleConfig, FlextDbOracleConnection

if TYPE_CHECKING:
    from unittest.mock import Mock


class TestFlextDbOracleConnection:
    """Comprehensive tests for Oracle connection."""

    def test_connection_initialization(self, valid_config: FlextDbOracleConfig) -> None:
        """Test connection initialization."""
        connection = FlextDbOracleConnection(valid_config)

        assert connection.config == valid_config
        assert connection._engine is None
        assert connection._session_factory is None
        assert not connection.is_connected()

    @patch("flext_db_oracle.connection.create_engine")
    def test_connect_success(
        self,
        mock_create_engine: Mock,
        valid_config: FlextDbOracleConfig,
    ) -> None:
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

    @patch("flext_db_oracle.connection.create_engine")
    def test_connect_failure(
        self,
        mock_create_engine: Mock,
        valid_config: FlextDbOracleConfig,
    ) -> None:
        """Test connection failure."""
        mock_create_engine.side_effect = OSError("Connection failed")

        connection = FlextDbOracleConnection(valid_config)
        result = connection.connect()

        assert result.is_failure
        assert "Connection failed" in result.error
        assert not connection.is_connected()

    def test_connect_with_invalid_config(
        self,
        invalid_config: FlextDbOracleConfig,
    ) -> None:
        """Test connection with invalid host (network failure)."""
        connection = FlextDbOracleConnection(invalid_config)
        result = connection.connect()

        assert result.is_failure
        assert "Failed to connect" in result.error

    @patch("flext_db_oracle.connection.create_engine")
    def test_disconnect_success(
        self,
        mock_create_engine: Mock,
        valid_config: FlextDbOracleConfig,
    ) -> None:
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

    def test_disconnect_when_not_connected(
        self,
        valid_config: FlextDbOracleConfig,
    ) -> None:
        """Test disconnect when not connected."""
        connection = FlextDbOracleConnection(valid_config)
        result = connection.disconnect()

        assert result.is_success
        assert result.data is True

    @patch("flext_db_oracle.connection.create_engine")
    def test_execute_select_success(
        self,
        mock_create_engine: Mock,
        valid_config: FlextDbOracleConfig,
    ) -> None:
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

    @patch("flext_db_oracle.connection.create_engine")
    def test_execute_dml_success(
        self,
        mock_create_engine: Mock,
        valid_config: FlextDbOracleConfig,
    ) -> None:
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

        result = connection.execute(
            "INSERT INTO test_table VALUES (:1)",
            {"1": "value"},
        )

        assert result.is_success
        assert result.data == [5]
        mock_connection.commit.assert_called_once()

    def test_execute_not_connected(self, valid_config: FlextDbOracleConfig) -> None:
        """Test execute when not connected."""
        connection = FlextDbOracleConnection(valid_config)
        result = connection.execute("SELECT 1 FROM DUAL")

        assert result.is_failure
        assert "Not connected to database" in result.error

    @patch("flext_db_oracle.connection.create_engine")
    def test_execute_sql_error(
        self,
        mock_create_engine: Mock,
        valid_config: FlextDbOracleConfig,
    ) -> None:
        """Test execute with SQL error."""
        # Setup mocks
        mock_engine = MagicMock(spec=Engine)
        mock_connection = MagicMock()

        # Configure mock to succeed on connection test but fail on actual execute

        def mock_execute(query: object, params: object = None) -> MagicMock:
            if "SELECT 1 FROM DUAL" in str(query):
                return MagicMock()  # Success for connection test
            error_msg = "SQL Error"
            raise ValueError(error_msg)  # Fail for actual test query

        mock_connection.execute = mock_execute
        mock_engine.connect.return_value.__enter__.return_value = mock_connection
        mock_create_engine.return_value = mock_engine

        connection = FlextDbOracleConnection(valid_config)
        connection.connect()

        result = connection.execute("INVALID SQL")

        assert result.is_failure
        assert "SQL execution failed" in result.error

    @patch("flext_db_oracle.connection.create_engine")
    def test_execute_many_success(
        self,
        mock_create_engine: Mock,
        valid_config: FlextDbOracleConfig,
    ) -> None:
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

    @patch("flext_db_oracle.connection.create_engine")
    def test_fetch_one_success(
        self,
        mock_create_engine: Mock,
        valid_config: FlextDbOracleConfig,
    ) -> None:
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

    @patch("flext_db_oracle.connection.create_engine")
    def test_session_context_manager(
        self,
        mock_create_engine: Mock,
        valid_config: FlextDbOracleConfig,
    ) -> None:
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

    @patch("flext_db_oracle.connection.create_engine")
    def test_session_rollback_on_error(
        self,
        mock_create_engine: Mock,
        valid_config: FlextDbOracleConfig,
    ) -> None:
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

        def _raise_error() -> None:
            msg = "Test error"
            raise ValueError(msg)

        try:
            with connection.session():
                _raise_error()
        except ValueError:
            pass

        mock_session.rollback.assert_called_once()
        mock_session.close.assert_called_once()

    @patch("flext_db_oracle.connection.create_engine")
    def test_transaction_context_manager(
        self,
        mock_create_engine: Mock,
        valid_config: FlextDbOracleConfig,
    ) -> None:
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

    @patch("flext_db_oracle.connection.create_engine")
    def test_transaction_rollback_on_error(
        self,
        mock_create_engine: Mock,
        valid_config: FlextDbOracleConfig,
    ) -> None:
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

        def _raise_error() -> None:
            msg = "Test error"
            raise ValueError(msg)

        try:
            with connection.transaction():
                _raise_error()
        except ValueError:
            pass

        mock_transaction.rollback.assert_called_once()

    @patch("flext_db_oracle.connection.create_engine")
    def test_get_table_names_success(
        self,
        mock_create_engine: Mock,
        valid_config: FlextDbOracleConfig,
    ) -> None:
        """Test getting table names successfully."""
        # Setup mocks
        mock_engine = MagicMock(spec=Engine)
        mock_connection = MagicMock()
        mock_result = MagicMock()
        mock_result.fetchall.return_value = [("TABLE1",), ("TABLE2",), ("TABLE3",)]
        mock_connection.execute.return_value = mock_result
        mock_engine.connect.return_value.__enter__.return_value = mock_connection
        mock_create_engine.return_value = mock_engine

        connection = FlextDbOracleConnection(valid_config)
        connection.connect()

        result = connection.get_table_names()

        assert result.is_success
        assert result.data == ["TABLE1", "TABLE2", "TABLE3"]

    @patch("flext_db_oracle.connection.create_engine")
    def test_get_table_names_with_schema(
        self,
        mock_create_engine: Mock,
        valid_config: FlextDbOracleConfig,
    ) -> None:
        """Test getting table names with specific schema."""
        # Setup mocks
        mock_engine = MagicMock(spec=Engine)
        mock_connection = MagicMock()
        mock_result = MagicMock()
        mock_result.fetchall.return_value = [("HR_TABLE1",), ("HR_TABLE2",)]
        mock_connection.execute.return_value = mock_result
        mock_engine.connect.return_value.__enter__.return_value = mock_connection
        mock_create_engine.return_value = mock_engine

        connection = FlextDbOracleConnection(valid_config)
        connection.connect()

        result = connection.get_table_names("HR")

        assert result.is_success
        assert result.data == ["HR_TABLE1", "HR_TABLE2"]

    @patch("flext_db_oracle.connection.create_engine")
    def test_get_schemas_success(
        self,
        mock_create_engine: Mock,
        valid_config: FlextDbOracleConfig,
    ) -> None:
        """Test getting schema names successfully."""
        # Setup mocks
        mock_engine = MagicMock(spec=Engine)
        mock_connection = MagicMock()
        mock_result = MagicMock()
        mock_result.fetchall.return_value = [("HR",), ("FINANCE",), ("SALES",)]
        mock_connection.execute.return_value = mock_result
        mock_engine.connect.return_value.__enter__.return_value = mock_connection
        mock_create_engine.return_value = mock_engine

        connection = FlextDbOracleConnection(valid_config)
        connection.connect()

        result = connection.get_schemas()

        assert result.is_success
        assert result.data == ["HR", "FINANCE", "SALES"]

    @patch("flext_db_oracle.connection.create_engine")
    def test_get_column_info_success(
        self,
        mock_create_engine: Mock,
        valid_config: FlextDbOracleConfig,
    ) -> None:
        """Test getting column info successfully."""
        # Setup mocks
        mock_engine = MagicMock(spec=Engine)
        mock_connection = MagicMock()
        mock_result = MagicMock()
        mock_result.fetchall.return_value = [
            ("ID", "NUMBER", "N", None, 10, 0, 1),
            ("NAME", "VARCHAR2", "Y", 100, None, None, 2),
        ]
        mock_connection.execute.return_value = mock_result
        mock_engine.connect.return_value.__enter__.return_value = mock_connection
        mock_create_engine.return_value = mock_engine

        connection = FlextDbOracleConnection(valid_config)
        connection.connect()

        result = connection.get_column_info("EMPLOYEES", "HR")

        assert result.is_success
        assert len(result.data) == 2
        assert result.data[0]["column_name"] == "ID"
        assert result.data[0]["data_type"] == "NUMBER"
        assert not result.data[0]["nullable"]
        assert result.data[1]["column_name"] == "NAME"
        assert result.data[1]["nullable"]

    @patch("flext_db_oracle.connection.create_engine")
    def test_get_primary_key_columns_success(
        self,
        mock_create_engine: Mock,
        valid_config: FlextDbOracleConfig,
    ) -> None:
        """Test getting primary key columns successfully."""
        # Setup mocks
        mock_engine = MagicMock(spec=Engine)
        mock_connection = MagicMock()
        mock_result = MagicMock()
        mock_result.fetchall.return_value = [("ID",), ("CODE",)]
        mock_connection.execute.return_value = mock_result
        mock_engine.connect.return_value.__enter__.return_value = mock_connection
        mock_create_engine.return_value = mock_engine

        connection = FlextDbOracleConnection(valid_config)
        connection.connect()

        result = connection.get_primary_key_columns("EMPLOYEES", "HR")

        assert result.is_success
        assert result.data == ["ID", "CODE"]

    @patch("flext_db_oracle.connection.create_engine")
    def test_get_table_metadata_success(
        self,
        mock_create_engine: Mock,
        valid_config: FlextDbOracleConfig,
    ) -> None:
        """Test getting complete table metadata successfully."""
        # Setup mocks
        mock_engine = MagicMock(spec=Engine)
        mock_connection = MagicMock()

        # Mock column info response - need to match the exact structure expected by get_column_info
        mock_column_result = MagicMock()
        mock_column_result.fetchall.return_value = [
            ("ID", "NUMBER", "N", None, 10, 0, 1),
            ("NAME", "VARCHAR2", "Y", 100, None, None, 2),
        ]

        # Mock primary key response
        mock_pk_result = MagicMock()
        mock_pk_result.fetchall.return_value = [("ID",)]

        # The execute method needs to handle both connection test and actual queries
        def mock_execute(query: object, params: object = None) -> MagicMock:
            if "SELECT 1 FROM DUAL" in str(query):
                return MagicMock()  # Connection test query
            if "all_tab_columns" in str(query) or "user_tab_columns" in str(query):
                return mock_column_result  # Column info query
            if "all_cons_columns" in str(query) or "user_cons_columns" in str(query):
                return mock_pk_result  # Primary key query
            return MagicMock()

        mock_connection.execute = mock_execute
        mock_engine.connect.return_value.__enter__.return_value = mock_connection
        mock_create_engine.return_value = mock_engine

        connection = FlextDbOracleConnection(valid_config)
        connection.connect()

        result = connection.get_table_metadata("EMPLOYEES", "HR")

        assert result.is_success
        assert result.data["table_name"] == "EMPLOYEES"
        assert result.data["schema_name"] == "HR"
        assert len(result.data["columns"]) == 2
        assert result.data["primary_keys"] == ["ID"]

    @patch("flext_db_oracle.connection.create_engine")
    def test_build_select_basic(
        self,
        mock_create_engine: Mock,
        valid_config: FlextDbOracleConfig,
    ) -> None:
        """Test building basic SELECT query."""
        # Setup mocks (minimal setup since we're testing query building logic)
        mock_engine = MagicMock(spec=Engine)
        mock_connection = MagicMock()
        mock_engine.connect.return_value.__enter__.return_value = mock_connection
        mock_create_engine.return_value = mock_engine

        connection = FlextDbOracleConnection(valid_config)
        connection.connect()

        result = connection.build_select("EMPLOYEES")

        assert result.is_success
        assert "SELECT * FROM EMPLOYEES" in result.data

    @patch("flext_db_oracle.connection.create_engine")
    def test_build_select_with_columns(
        self,
        mock_create_engine: Mock,
        valid_config: FlextDbOracleConfig,
    ) -> None:
        """Test building SELECT query with specific columns."""
        # Setup mocks
        mock_engine = MagicMock(spec=Engine)
        mock_connection = MagicMock()
        mock_engine.connect.return_value.__enter__.return_value = mock_connection
        mock_create_engine.return_value = mock_engine

        connection = FlextDbOracleConnection(valid_config)
        connection.connect()

        result = connection.build_select("EMPLOYEES", ["ID", "NAME", "EMAIL"])

        assert result.is_success
        assert "SELECT ID, NAME, EMAIL FROM EMPLOYEES" in result.data

    @patch("flext_db_oracle.connection.create_engine")
    def test_build_select_with_conditions(
        self,
        mock_create_engine: Mock,
        valid_config: FlextDbOracleConfig,
    ) -> None:
        """Test building SELECT query with WHERE conditions."""
        # Setup mocks
        mock_engine = MagicMock(spec=Engine)
        mock_connection = MagicMock()
        mock_engine.connect.return_value.__enter__.return_value = mock_connection
        mock_create_engine.return_value = mock_engine

        connection = FlextDbOracleConnection(valid_config)
        connection.connect()

        conditions = {"status": "active", "department_id": 10}
        result = connection.build_select("EMPLOYEES", None, conditions)

        assert result.is_success
        assert "SELECT * FROM EMPLOYEES WHERE" in result.data
        assert "status = 'active'" in result.data
        assert "department_id = 10" in result.data

    @patch("flext_db_oracle.connection.create_engine")
    def test_build_select_with_schema(
        self,
        mock_create_engine: Mock,
        valid_config: FlextDbOracleConfig,
    ) -> None:
        """Test building SELECT query with schema."""
        # Setup mocks
        mock_engine = MagicMock(spec=Engine)
        mock_connection = MagicMock()
        mock_engine.connect.return_value.__enter__.return_value = mock_connection
        mock_create_engine.return_value = mock_engine

        connection = FlextDbOracleConnection(valid_config)
        connection.connect()

        result = connection.build_select("EMPLOYEES", ["ID", "NAME"], None, "HR")

        assert result.is_success
        assert "SELECT ID, NAME FROM HR.EMPLOYEES" in result.data

    @patch("flext_db_oracle.connection.create_engine")
    def test_create_table_ddl_success(
        self,
        mock_create_engine: Mock,
        valid_config: FlextDbOracleConfig,
    ) -> None:
        """Test creating table DDL successfully."""
        # Setup mocks
        mock_engine = MagicMock(spec=Engine)
        mock_connection = MagicMock()
        mock_engine.connect.return_value.__enter__.return_value = mock_connection
        mock_create_engine.return_value = mock_engine

        connection = FlextDbOracleConnection(valid_config)
        connection.connect()

        columns = [
            {
                "name": "ID",
                "data_type": "NUMBER(10)",
                "nullable": False,
                "default_value": None,
            },
            {
                "name": "NAME",
                "data_type": "VARCHAR2(100)",
                "nullable": True,
                "default_value": "'UNKNOWN'",
            },
        ]

        result = connection.create_table_ddl("TEST_TABLE", columns, "HR")

        assert result.is_success
        assert "CREATE TABLE HR.TEST_TABLE" in result.data
        assert "ID NUMBER(10) NOT NULL" in result.data
        assert "NAME VARCHAR2(100) DEFAULT 'UNKNOWN'" in result.data

    @patch("flext_db_oracle.connection.create_engine")
    def test_drop_table_ddl_success(
        self,
        mock_create_engine: Mock,
        valid_config: FlextDbOracleConfig,
    ) -> None:
        """Test creating DROP table DDL successfully."""
        # Setup mocks
        mock_engine = MagicMock(spec=Engine)
        mock_connection = MagicMock()
        mock_engine.connect.return_value.__enter__.return_value = mock_connection
        mock_create_engine.return_value = mock_engine

        connection = FlextDbOracleConnection(valid_config)
        connection.connect()

        result = connection.drop_table_ddl("TEST_TABLE", "HR")

        assert result.is_success
        assert result.data == "DROP TABLE HR.TEST_TABLE"

    @patch("flext_db_oracle.connection.create_engine")
    def test_execute_ddl_success(
        self,
        mock_create_engine: Mock,
        valid_config: FlextDbOracleConfig,
    ) -> None:
        """Test executing DDL successfully."""
        # Setup mocks
        mock_engine = MagicMock(spec=Engine)
        mock_connection = MagicMock()
        mock_result = MagicMock()
        mock_result.rowcount = 1
        mock_connection.execute.return_value = mock_result
        mock_engine.connect.return_value.__enter__.return_value = mock_connection
        mock_create_engine.return_value = mock_engine

        connection = FlextDbOracleConnection(valid_config)
        connection.connect()

        result = connection.execute_ddl("CREATE TABLE TEST (ID NUMBER)")

        assert result.is_success
        assert result.data is True

    @patch("flext_db_oracle.connection.create_engine")
    def test_convert_singer_type_basic_types(
        self,
        mock_create_engine: Mock,
        valid_config: FlextDbOracleConfig,
    ) -> None:
        """Test converting basic Singer types to Oracle types."""
        # Setup mocks
        mock_engine = MagicMock(spec=Engine)
        mock_connection = MagicMock()
        mock_engine.connect.return_value.__enter__.return_value = mock_connection
        mock_create_engine.return_value = mock_engine

        connection = FlextDbOracleConnection(valid_config)
        connection.connect()

        # Test string type
        result = connection.convert_singer_type("string")
        assert result.is_success
        assert result.data == "VARCHAR2(4000)"

        # Test integer type
        result = connection.convert_singer_type("integer")
        assert result.is_success
        assert result.data == "NUMBER(38)"

        # Test number type
        result = connection.convert_singer_type("number")
        assert result.is_success
        assert result.data == "NUMBER"

        # Test boolean type
        result = connection.convert_singer_type("boolean")
        assert result.is_success
        assert result.data == "NUMBER(1)"

    @patch("flext_db_oracle.connection.create_engine")
    def test_convert_singer_type_with_format(
        self,
        mock_create_engine: Mock,
        valid_config: FlextDbOracleConfig,
    ) -> None:
        """Test converting Singer types with format hints."""
        # Setup mocks
        mock_engine = MagicMock(spec=Engine)
        mock_connection = MagicMock()
        mock_engine.connect.return_value.__enter__.return_value = mock_connection
        mock_create_engine.return_value = mock_engine

        connection = FlextDbOracleConnection(valid_config)
        connection.connect()

        # Test date format
        result = connection.convert_singer_type("string", "date-time")
        assert result.is_success
        assert result.data == "DATE"

        # Test time format
        result = connection.convert_singer_type("string", "time")
        assert result.is_success
        assert result.data == "TIMESTAMP"

    @patch("flext_db_oracle.connection.create_engine")
    def test_convert_singer_type_array_with_null(
        self,
        mock_create_engine: Mock,
        valid_config: FlextDbOracleConfig,
    ) -> None:
        """Test converting Singer array types with null."""
        # Setup mocks
        mock_engine = MagicMock(spec=Engine)
        mock_connection = MagicMock()
        mock_engine.connect.return_value.__enter__.return_value = mock_connection
        mock_create_engine.return_value = mock_engine

        connection = FlextDbOracleConnection(valid_config)
        connection.connect()

        # Test array with null
        result = connection.convert_singer_type(["string", "null"])
        assert result.is_success
        assert result.data == "VARCHAR2(4000)"

        # Test array without null
        result = connection.convert_singer_type(["integer"])
        assert result.is_success
        assert result.data == "NUMBER(38)"

    @patch("flext_db_oracle.connection.create_engine")
    def test_map_singer_schema_success(
        self,
        mock_create_engine: Mock,
        valid_config: FlextDbOracleConfig,
    ) -> None:
        """Test mapping Singer schema to Oracle column definitions."""
        # Setup mocks
        mock_engine = MagicMock(spec=Engine)
        mock_connection = MagicMock()
        mock_engine.connect.return_value.__enter__.return_value = mock_connection
        mock_create_engine.return_value = mock_engine

        connection = FlextDbOracleConnection(valid_config)
        connection.connect()

        singer_schema = {
            "properties": {
                "id": {"type": "integer"},
                "name": {"type": "string"},
                "email": {"type": "string"},
                "created_at": {"type": "string", "format": "date-time"},
                "is_active": {"type": "boolean"},
                "metadata": {"type": "object"},
            },
        }

        result = connection.map_singer_schema(singer_schema)

        assert result.is_success
        assert result.data["id"] == "NUMBER(38)"
        assert result.data["name"] == "VARCHAR2(4000)"
        assert result.data["email"] == "VARCHAR2(4000)"
        assert result.data["created_at"] == "DATE"
        assert result.data["is_active"] == "NUMBER(1)"
        assert result.data["metadata"] == "CLOB"

    def test_build_connection_url_service_name(
        self,
        valid_config: FlextDbOracleConfig,
    ) -> None:
        """Test building connection URL with service name."""
        connection = FlextDbOracleConnection(valid_config)

        result = connection._build_connection_url()

        assert result.is_success
        assert "service_name=" in result.data
        assert valid_config.service_name in result.data

    def test_build_connection_url_sid(self) -> None:
        """Test building connection URL with SID."""
        from pydantic import SecretStr

        from flext_db_oracle import FlextDbOracleConfig

        config = FlextDbOracleConfig(
            host="localhost",
            port=1521,
            username="testuser",
            password=SecretStr("testpass"),
            sid="ORCL",  # Using SID instead of service_name
        )

        connection = FlextDbOracleConnection(config)

        result = connection._build_connection_url()

        assert result.is_success
        assert "/ORCL" in result.data
        assert "service_name=" not in result.data

    def test_build_connection_url_no_identifier(
        self,
        valid_config: FlextDbOracleConfig,
    ) -> None:
        """Test building connection URL without SID or service name."""
        # Create a mock config that has neither service_name nor sid
        mock_config = MagicMock()
        mock_config.service_name = None
        mock_config.sid = None
        mock_config.username = "testuser"
        mock_config.password.get_secret_value.return_value = "testpass"
        mock_config.host = "localhost"
        mock_config.port = 1521

        connection = FlextDbOracleConnection(mock_config)
        result = connection._build_connection_url()

        assert result.is_failure
        assert "Must provide either service_name or sid" in result.error

    def test_connect_with_url_building_failure(
        self,
        valid_config: FlextDbOracleConfig,
    ) -> None:
        """Test connection with URL building failure."""
        # Patch _build_connection_url to return failure
        connection = FlextDbOracleConnection(valid_config)

        with patch.object(
            connection,
            "_build_connection_url",
            return_value=FlextResult.fail("URL build failed"),
        ):
            result = connection.connect()

        assert result.is_failure
        assert "URL build failed" in result.error

    @patch("flext_db_oracle.connection.create_engine")
    def test_test_connection_success(
        self,
        mock_create_engine: Mock,
        valid_config: FlextDbOracleConfig,
    ) -> None:
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

    def test_test_connection_not_connected(
        self,
        valid_config: FlextDbOracleConfig,
    ) -> None:
        """Test connection test when not connected."""
        connection = FlextDbOracleConnection(valid_config)
        result = connection.test_connection()

        assert result.is_failure
        assert "Not connected" in result.error

    @patch("flext_db_oracle.connection.create_engine")
    def test_disconnect_failure(
        self,
        mock_create_engine: Mock,
        valid_config: FlextDbOracleConfig,
    ) -> None:
        """Test disconnect failure handling."""
        # Setup mocks
        mock_engine = MagicMock(spec=Engine)
        mock_engine.dispose.side_effect = OSError("Dispose failed")
        mock_connection = MagicMock()
        mock_engine.connect.return_value.__enter__.return_value = mock_connection
        mock_create_engine.return_value = mock_engine

        connection = FlextDbOracleConnection(valid_config)
        connection.connect()

        result = connection.disconnect()

        assert result.is_failure
        assert "Disconnect failed" in result.error

    @patch("flext_db_oracle.connection.create_engine")
    def test_execute_many_not_connected(
        self,
        mock_create_engine: Mock,
        valid_config: FlextDbOracleConfig,
    ) -> None:
        """Test execute_many when not connected."""
        connection = FlextDbOracleConnection(valid_config)

        params_list = [{"id": 1}, {"id": 2}]
        result = connection.execute_many("INSERT INTO test VALUES (:id)", params_list)

        assert result.is_failure
        assert "Not connected to database" in result.error

    @patch("flext_db_oracle.connection.create_engine")
    def test_execute_many_no_engine(
        self,
        mock_create_engine: Mock,
        valid_config: FlextDbOracleConfig,
    ) -> None:
        """Test execute_many when is_connected but engine is None (edge case)."""
        connection = FlextDbOracleConnection(valid_config)
        # Set up mocks for connection
        mock_engine = MagicMock()
        mock_connection = MagicMock()
        mock_engine.connect.return_value.__enter__.return_value = mock_connection
        mock_create_engine.return_value = mock_engine

        connection.connect()

        # Patch is_connected to return True but _engine is None to test the edge case
        with patch.object(connection, "is_connected", return_value=True):
            connection._engine = None  # Engine is None but is_connected returns True
            params_list = [{"id": 1}, {"id": 2}]
            result = connection.execute_many(
                "INSERT INTO test VALUES (:id)",
                params_list,
            )

            assert result.is_failure
            assert "Database engine not initialized" in result.error

    @patch("flext_db_oracle.connection.create_engine")
    def test_execute_many_sql_error(
        self,
        mock_create_engine: Mock,
        valid_config: FlextDbOracleConfig,
    ) -> None:
        """Test execute_many with SQL error."""
        # Setup mocks
        mock_engine = MagicMock(spec=Engine)
        mock_connection = MagicMock()

        # Configure mock to succeed on connection test but fail on actual execute_many

        def mock_execute(query: object, params: object = None) -> MagicMock:
            if "SELECT 1 FROM DUAL" in str(query):
                return MagicMock()  # Success for connection test
            error_msg = "SQL Error in batch"
            raise ValueError(error_msg)  # Fail for actual test query

        mock_connection.execute = mock_execute
        mock_engine.connect.return_value.__enter__.return_value = mock_connection
        mock_create_engine.return_value = mock_engine

        connection = FlextDbOracleConnection(valid_config)
        connection.connect()

        params_list = [{"id": 1}, {"id": 2}]
        result = connection.execute_many("INSERT INTO test VALUES (:id)", params_list)

        assert result.is_failure
        assert "Batch execution failed" in result.error

    @patch("flext_db_oracle.connection.create_engine")
    def test_fetch_one_not_connected(
        self,
        mock_create_engine: Mock,
        valid_config: FlextDbOracleConfig,
    ) -> None:
        """Test fetch_one when not connected."""
        connection = FlextDbOracleConnection(valid_config)
        result = connection.fetch_one("SELECT 1 FROM DUAL")

        assert result.is_failure
        assert "Not connected to database" in result.error

    @patch("flext_db_oracle.connection.create_engine")
    def test_fetch_one_no_engine(
        self,
        mock_create_engine: Mock,
        valid_config: FlextDbOracleConfig,
    ) -> None:
        """Test fetch_one when is_connected but engine is None (edge case)."""
        connection = FlextDbOracleConnection(valid_config)
        # Set up mocks for connection
        mock_engine = MagicMock()
        mock_connection = MagicMock()
        mock_engine.connect.return_value.__enter__.return_value = mock_connection
        mock_create_engine.return_value = mock_engine

        connection.connect()

        # Patch is_connected to return True but _engine is None to test the edge case
        with patch.object(connection, "is_connected", return_value=True):
            connection._engine = None  # Engine is None but is_connected returns True
            result = connection.fetch_one("SELECT 1 FROM DUAL")

            assert result.is_failure
            assert "Database engine not initialized" in result.error

    @patch("flext_db_oracle.connection.create_engine")
    def test_fetch_one_sql_error(
        self,
        mock_create_engine: Mock,
        valid_config: FlextDbOracleConfig,
    ) -> None:
        """Test fetch_one with SQL error."""
        # Setup mocks
        mock_engine = MagicMock(spec=Engine)
        mock_connection = MagicMock()

        # Configure mock to succeed on connection test but fail on actual fetch_one

        def mock_execute(query: object, params: object = None) -> MagicMock:
            if "SELECT 1 FROM DUAL" in str(query):
                return MagicMock()  # Success for connection test
            error_msg = "SQL Error in fetch_one"
            raise ValueError(error_msg)  # Fail for actual test query

        mock_connection.execute = mock_execute
        mock_engine.connect.return_value.__enter__.return_value = mock_connection
        mock_create_engine.return_value = mock_engine

        connection = FlextDbOracleConnection(valid_config)
        connection.connect()

        result = connection.fetch_one("SELECT COUNT(*) FROM test_table")

        assert result.is_failure
        assert "Fetch one failed" in result.error

    @patch("flext_db_oracle.connection.create_engine")
    def test_session_not_connected(
        self,
        mock_create_engine: Mock,
        valid_config: FlextDbOracleConfig,
    ) -> None:
        """Test session context manager when not connected."""
        connection = FlextDbOracleConnection(valid_config)

        with (
            pytest.raises(ValueError, match="Not connected to database"),
            connection.session(),
        ):
            pass

    @patch("flext_db_oracle.connection.create_engine")
    def test_transaction_not_connected(
        self,
        mock_create_engine: Mock,
        valid_config: FlextDbOracleConfig,
    ) -> None:
        """Test transaction context manager when not connected."""
        connection = FlextDbOracleConnection(valid_config)

        with (
            pytest.raises(ValueError, match="Not connected to database"),
            connection.transaction(),
        ):
            pass

    @patch("flext_db_oracle.connection.create_engine")
    def test_transaction_no_engine(
        self,
        mock_create_engine: Mock,
        valid_config: FlextDbOracleConfig,
    ) -> None:
        """Test transaction context manager when is_connected but engine is None (edge case)."""
        connection = FlextDbOracleConnection(valid_config)
        # Set up mocks for connection
        mock_engine = MagicMock()
        mock_connection = MagicMock()
        mock_engine.connect.return_value.__enter__.return_value = mock_connection
        mock_create_engine.return_value = mock_engine

        connection.connect()

        # Patch is_connected to return True but _engine is None to test the edge case
        with patch.object(connection, "is_connected", return_value=True):
            connection._engine = None  # Engine is None but is_connected returns True

            with (
                pytest.raises(ValueError, match="Database engine not initialized"),
                connection.transaction(),
            ):
                pass
