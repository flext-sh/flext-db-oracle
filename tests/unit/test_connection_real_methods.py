"""Targeted coverage tests for FlextDbOracleConnection - focusing on REAL methods.

Based on analysis of actual code in connection.py, this focuses on the 35+ real methods
that exist to systematically eliminate the 589 missing statements.
"""

from unittest.mock import Mock, patch

import pytest
from flext_core import FlextResult
from pydantic import SecretStr

from flext_db_oracle import FlextDbOracleConfig, FlextDbOracleConnection


class TestFlextDbOracleConnectionRealMethods:
    """Test ALL real methods in FlextDbOracleConnection."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.config = FlextDbOracleConfig(
            host="test_host",
            port=1521,
            service_name="TEST_SERVICE",
            username="test_user",
            password=SecretStr("test_password")
        )
        self.connection = FlextDbOracleConnection(self.config)

    # =================================================================
    # CORE CONNECTION METHODS
    # =================================================================

    def test_initialization(self) -> None:
        """Test connection initialization."""
        conn = FlextDbOracleConnection(self.config)
        assert conn.config == self.config
        assert conn._engine is None
        assert conn._session_factory is None
        assert not conn.is_connected()

    @patch("sqlalchemy.create_engine")
    @patch("sqlalchemy.orm.sessionmaker")
    def test_connect_success(self, mock_sessionmaker: Mock, mock_create_engine: Mock) -> None:
        """Test successful connection."""
        # Setup mocks
        mock_engine = Mock()
        mock_connection_context = Mock()
        mock_connection_context.__enter__ = Mock(return_value=Mock())
        mock_connection_context.__exit__ = Mock(return_value=None)
        mock_engine.connect.return_value = mock_connection_context
        mock_create_engine.return_value = mock_engine
        mock_sessionmaker.return_value = Mock()

        # Mock config validation using FlextDbOracleConfig from flext_db_oracle
        from flext_db_oracle.config import FlextDbOracleConfig
        with patch.object(FlextDbOracleConfig, "validate_business_rules", return_value=FlextResult[None].ok(None)):

            with patch.object(self.connection, "_build_connection_url") as mock_build_url:
                mock_build_url.return_value = FlextResult[str].ok("oracle+oracledb://test:test@test:1521/TEST")

                result = self.connection.connect()

                assert result.success
                assert self.connection.is_connected()
                assert self.connection._engine is mock_engine
                assert self.connection._session_factory is not None

    def test_disconnect_success(self) -> None:
        """Test successful disconnection."""
        # Setup connected state
        mock_engine = Mock()
        self.connection._engine = mock_engine
        self.connection._session_factory = Mock()

        result = self.connection.disconnect()

        assert result.success
        assert result.value is True
        assert self.connection._engine is None
        assert self.connection._session_factory is None
        mock_engine.dispose.assert_called_once()

    def test_disconnect_not_connected(self) -> None:
        """Test disconnect when not connected."""
        result = self.connection.disconnect()
        assert result.success
        assert result.value is True

    def test_is_connected_states(self) -> None:
        """Test is_connected() in different states."""
        # Not connected
        assert not self.connection.is_connected()

        # Connected
        self.connection._engine = Mock()
        assert self.connection.is_connected()

        # Disconnected again
        self.connection._engine = None
        assert not self.connection.is_connected()

    def test_ensure_connected_when_connected(self) -> None:
        """Test _ensure_connected when already connected."""
        self.connection._engine = Mock()

        result = self.connection._ensure_connected()
        assert result.success

    def test_ensure_connected_when_not_connected(self) -> None:
        """Test _ensure_connected when not connected."""
        result = self.connection._ensure_connected()

        assert not result.success
        assert "Not connected" in result.error

    # =================================================================
    # DATABASE OPERATION METHODS
    # =================================================================

    def test_execute_not_connected(self) -> None:
        """Test execute when not connected."""
        result = self.connection.execute("SELECT 1 FROM dual")

        assert not result.success
        assert "Not connected" in result.error

    def test_execute_many_not_connected(self) -> None:
        """Test execute_many when not connected."""
        result = self.connection.execute_many("INSERT INTO test VALUES (:val)", [{"val": 1}])

        assert not result.success
        assert "Not connected" in result.error

    def test_fetch_one_not_connected(self) -> None:
        """Test fetch_one when not connected."""
        result = self.connection.fetch_one("SELECT name FROM users WHERE id = 1")

        assert not result.success
        assert "Not connected" in result.error

    def test_session_no_engine(self) -> None:
        """Test session when no engine available."""
        with pytest.raises(RuntimeError, match="No engine available"):
            with self.connection.session():
                pass

    def test_transaction_no_engine(self) -> None:
        """Test transaction when no engine available."""
        with pytest.raises(RuntimeError, match="No engine available"):
            with self.connection.transaction():
                pass

    def test_close(self) -> None:
        """Test close method."""
        # When not connected
        result = self.connection.close()
        assert result.success

        # When connected
        mock_engine = Mock()
        self.connection._engine = mock_engine

        result = self.connection.close()
        assert result.success
        assert self.connection._engine is None
        mock_engine.dispose.assert_called_once()

    def test_execute_query_not_connected(self) -> None:
        """Test execute_query when not connected."""
        result = self.connection.execute_query("SELECT * FROM test")

        assert not result.success
        assert "Not connected" in result.error

    def test_test_connection_not_connected(self) -> None:
        """Test test_connection method when not connected."""
        result = self.connection.test_connection()

        assert not result.success
        assert "No engine available" in result.error

    # =================================================================
    # SCHEMA INTROSPECTION METHODS
    # =================================================================

    def test_get_table_names_not_connected(self) -> None:
        """Test get_table_names when not connected."""
        result = self.connection.get_table_names()

        assert not result.success
        assert "Not connected" in result.error

    def test_get_schemas_not_connected(self) -> None:
        """Test get_schemas when not connected."""
        result = self.connection.get_schemas()

        assert not result.success
        assert "Not connected" in result.error

    def test_get_current_schema_not_connected(self) -> None:
        """Test get_current_schema when not connected."""
        result = self.connection.get_current_schema()

        assert not result.success
        assert "Not connected" in result.error

    def test_get_column_info_not_connected(self) -> None:
        """Test get_column_info when not connected."""
        result = self.connection.get_column_info("test_table")

        assert not result.success
        assert "Not connected" in result.error

    def test_get_primary_key_columns_not_connected(self) -> None:
        """Test get_primary_key_columns when not connected."""
        result = self.connection.get_primary_key_columns("test_table")

        assert not result.success
        assert "Not connected" in result.error

    def test_get_table_metadata_not_connected(self) -> None:
        """Test get_table_metadata when not connected."""
        result = self.connection.get_table_metadata("test_table")

        assert not result.success
        assert "Not connected" in result.error

    # =================================================================
    # QUERY BUILDING METHODS - Test logic without connection
    # =================================================================

    def test_build_select_basic(self) -> None:
        """Test build_select method basic functionality."""
        result = self.connection.build_select(
            table_name="users",
            columns=["id", "name", "email"],
            where_clause="id > 100",
            limit=50
        )

        assert result.success
        assert "SELECT" in result.value
        assert "users" in result.value
        assert "id, name, email" in result.value
        assert "WHERE id > 100" in result.value
        assert "ROWNUM <= 50" in result.value

    def test_build_select_minimal(self) -> None:
        """Test build_select with minimal parameters."""
        result = self.connection.build_select(table_name="simple_table")

        assert result.success
        assert "SELECT * FROM simple_table" in result.value

    def test_build_select_safe_basic(self) -> None:
        """Test build_select_safe method."""
        result = self.connection.build_select_safe(
            table_name="safe_table",
            columns=["col1", "col2"],
            limit=10
        )

        assert result.success
        assert "SELECT" in result.value
        assert "safe_table" in result.value
        assert "col1, col2" in result.value

    def test_build_table_name_with_schema(self) -> None:
        """Test _build_table_name method."""
        # Test with schema
        result = self.connection._build_table_name("users", "hr")
        assert result == "hr.users"

        # Test without schema
        result = self.connection._build_table_name("users")
        assert result == "users"

    def test_build_column_definition_success(self) -> None:
        """Test _build_column_definition method."""
        col_info = {
            "name": "user_id",
            "data_type": "NUMBER(10)",
            "nullable": False,
            "default_value": "1"
        }

        result = self.connection._build_column_definition(col_info)

        assert result.success
        assert "user_id NUMBER(10)" in result.value
        assert "NOT NULL" in result.value
        assert "DEFAULT 1" in result.value

    def test_build_column_definition_minimal(self) -> None:
        """Test _build_column_definition with minimal info."""
        col_info = {
            "name": "simple_col",
            "data_type": "VARCHAR2(50)"
        }

        result = self.connection._build_column_definition(col_info)

        assert result.success
        assert result.value == "simple_col VARCHAR2(50)"

    # =================================================================
    # DDL BUILDING METHODS
    # =================================================================

    def test_create_table_ddl_basic(self) -> None:
        """Test create_table_ddl method."""
        columns = [
            {"name": "id", "data_type": "NUMBER(10)", "nullable": False},
            {"name": "name", "data_type": "VARCHAR2(100)", "nullable": True}
        ]

        result = self.connection.create_table_ddl("test_table", columns)

        assert result.success
        assert "CREATE TABLE test_table" in result.value
        assert "id NUMBER(10) NOT NULL" in result.value
        assert "name VARCHAR2(100)" in result.value

    def test_create_table_ddl_with_primary_key(self) -> None:
        """Test create_table_ddl with primary key."""
        columns = [
            {"name": "id", "data_type": "NUMBER(10)", "nullable": False},
            {"name": "name", "data_type": "VARCHAR2(100)"}
        ]
        primary_keys = ["id"]

        result = self.connection.create_table_ddl("pk_table", columns, primary_keys)

        assert result.success
        assert "CREATE TABLE pk_table" in result.value
        assert "PRIMARY KEY (id)" in result.value

    def test_drop_table_ddl(self) -> None:
        """Test drop_table_ddl method."""
        result = self.connection.drop_table_ddl("drop_me")

        assert result.success
        assert result.value == "DROP TABLE drop_me"

    def test_execute_ddl_not_connected(self) -> None:
        """Test execute_ddl when not connected."""
        result = self.connection.execute_ddl("CREATE TABLE test (id NUMBER)")

        assert not result.success
        assert "Not connected" in result.error

    # =================================================================
    # SINGER SCHEMA METHODS
    # =================================================================

    def test_convert_singer_type_string(self) -> None:
        """Test convert_singer_type for string types."""
        result = self.connection.convert_singer_type("string", max_length=100)

        assert result.success
        assert "VARCHAR2(100)" in result.value

    def test_convert_singer_type_integer(self) -> None:
        """Test convert_singer_type for integer types."""
        result = self.connection.convert_singer_type("integer")

        assert result.success
        assert "NUMBER(38)" in result.value

    def test_convert_singer_type_number(self) -> None:
        """Test convert_singer_type for number types."""
        result = self.connection.convert_singer_type("number")

        assert result.success
        assert "NUMBER" in result.value

    def test_convert_singer_type_boolean(self) -> None:
        """Test convert_singer_type for boolean types."""
        result = self.connection.convert_singer_type("boolean")

        assert result.success
        assert "NUMBER(1)" in result.value

    def test_convert_singer_type_date_time(self) -> None:
        """Test convert_singer_type for date-time types."""
        result = self.connection.convert_singer_type("string", format_hint="date-time")

        assert result.success
        assert "TIMESTAMP" in result.value

    def test_convert_singer_type_unsupported(self) -> None:
        """Test convert_singer_type for unsupported types."""
        result = self.connection.convert_singer_type("unknown_type")

        assert not result.success
        assert "Unsupported Singer type" in result.error

    def test_map_singer_schema_basic(self) -> None:
        """Test map_singer_schema method."""
        singer_schema = {
            "properties": {
                "id": {"type": "integer"},
                "name": {"type": "string", "maxLength": 50},
                "active": {"type": "boolean"}
            }
        }

        result = self.connection.map_singer_schema(singer_schema)

        assert result.success
        assert len(result.value) == 3

        # Check mapped columns
        columns = result.value
        id_col = next(col for col in columns if col["name"] == "id")
        assert "NUMBER(38)" in id_col["data_type"]

        name_col = next(col for col in columns if col["name"] == "name")
        assert "VARCHAR2(50)" in name_col["data_type"]

        active_col = next(col for col in columns if col["name"] == "active")
        assert "NUMBER(1)" in active_col["data_type"]

    # =================================================================
    # CONNECTION URL BUILDING
    # =================================================================

    def test_build_connection_url_service_name(self) -> None:
        """Test _build_connection_url with service_name."""
        result = self.connection._build_connection_url()

        assert result.success
        url = result.value
        assert url.startswith("oracle+oracledb://")
        assert "test_user" in url
        assert "test_host:1521" in url
        assert "TEST_SERVICE" in url

    def test_build_connection_url_with_sid(self) -> None:
        """Test _build_connection_url with SID."""
        config = FlextDbOracleConfig(
            host="sid_host",
            port=1522,
            sid="TESTSID",
            username="sid_user",
            password=SecretStr("sid_pass")
        )
        connection = FlextDbOracleConnection(config)

        result = connection._build_connection_url()

        assert result.success
        url = result.value
        assert "sid_host:1522" in url
        assert "TESTSID" in url
        assert "sid_user" in url

    # =================================================================
    # SQL STATEMENT BUILDING METHODS
    # =================================================================

    def test_build_insert_statement(self) -> None:
        """Test build_insert_statement method."""
        columns = ["id", "name", "email"]

        result = self.connection.build_insert_statement("users", columns)

        assert result.success
        assert "INSERT INTO users" in result.value
        assert "(id, name, email)" in result.value
        assert "VALUES (:id, :name, :email)" in result.value

    def test_build_update_statement(self) -> None:
        """Test build_update_statement method."""
        set_columns = ["name", "email"]
        where_columns = ["id"]

        result = self.connection.build_update_statement("users", set_columns, where_columns)

        assert result.success
        assert "UPDATE users SET" in result.value
        assert "name = :name" in result.value
        assert "email = :email" in result.value
        assert "WHERE id = :id" in result.value

    def test_build_merge_statement(self) -> None:
        """Test build_merge_statement method."""
        key_columns = ["id"]
        data_columns = ["name", "email"]

        result = self.connection.build_merge_statement("users", key_columns, data_columns)

        assert result.success
        assert "MERGE INTO users" in result.value
        assert "ON (target.id = source.id)" in result.value
        assert "UPDATE SET" in result.value
        assert "INSERT (" in result.value

    def test_build_delete_statement(self) -> None:
        """Test build_delete_statement method."""
        where_columns = ["id", "status"]

        result = self.connection.build_delete_statement("users", where_columns)

        assert result.success
        assert "DELETE FROM users" in result.value
        assert "WHERE id = :id AND status = :status" in result.value

    def test_build_create_index_statement(self) -> None:
        """Test build_create_index_statement method."""
        from flext_db_oracle.connection import CreateIndexConfig

        config = CreateIndexConfig(
            index_name="idx_users_email",
            table_name="users",
            columns=["email"],
            unique=True
        )

        result = self.connection.build_create_index_statement(config)

        assert result.success
        assert "CREATE UNIQUE INDEX idx_users_email" in result.value
        assert "ON users (email)" in result.value

    # =================================================================
    # ERROR HANDLING METHOD
    # =================================================================

    def test_handle_database_error_with_logging(self) -> None:
        """Test _handle_database_error_with_logging method."""
        from sqlalchemy.exc import SQLAlchemyError

        error = SQLAlchemyError("Test database error")
        result = self.connection._handle_database_error_with_logging(error, "test_operation")

        assert not result.success
        assert "test_operation" in result.error
        assert "Test database error" in result.error
