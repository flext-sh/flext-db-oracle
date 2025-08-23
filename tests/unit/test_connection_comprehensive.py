"""Comprehensive tests for FlextDbOracleConnection using real code validation.

This module tests the connection functionality with real code paths,
following the user's requirement for real code testing without mocks.
"""

import pytest
from pydantic import SecretStr

from flext_db_oracle import FlextDbOracleConfig, FlextDbOracleConnection
from flext_db_oracle.config_types import MergeStatementConfig
from flext_db_oracle.connection import CreateIndexConfig


class TestFlextDbOracleConnectionComprehensive:
    """Comprehensive tests for Oracle connection using real code paths."""

    def setup_method(self) -> None:
        """Setup test configuration."""
        self.config = FlextDbOracleConfig(
            host="test",
            port=1521,
            service_name="TEST",
            username="test",
            password=SecretStr("test"),
        )
        self.connection = FlextDbOracleConnection(self.config)

    def test_connection_initialization(self) -> None:
        """Test connection initialization with real configuration."""
        assert self.connection is not None
        assert self.connection.config == self.config
        assert self.connection._engine is None
        assert self.connection._session_factory is None

    def test_is_connected_method(self) -> None:
        """Test is_connected method behavior."""
        # Initially not connected
        assert not self.connection.is_connected()

        # After setting _engine to None explicitly
        self.connection._engine = None
        assert not self.connection.is_connected()

    def test_connect_validation_errors(self) -> None:
        """Test connect method with invalid configurations."""
        # Test with empty host - should fail at config validation
        with pytest.raises(ValueError, match="Host cannot be empty"):
            FlextDbOracleConfig(
                host="",
                port=1521,
                service_name="TEST",
                username="test",
                password=SecretStr("test"),
            )

    def test_disconnect_when_not_connected(self) -> None:
        """Test disconnect when not connected."""
        result = self.connection.disconnect()
        assert result.success
        assert result.value is True

    def test_connection_url_building(self) -> None:
        """Test connection URL building logic."""
        # Test with service name
        result = self.connection._build_connection_url()
        assert result.success
        url = result.value
        assert "oracle+oracledb://" in url
        assert "test:" in url
        assert "@test:1521" in url
        assert "service_name=TEST" in url

        # Test with SID instead of service_name
        sid_config = FlextDbOracleConfig(
            host="test",
            port=1521,
            sid="TESTSID",
            username="test",
            password=SecretStr("test"),
        )
        sid_connection = FlextDbOracleConnection(sid_config)
        sid_result = sid_connection._build_connection_url()
        assert sid_result.success
        assert "/TESTSID" in sid_result.value

    def test_connection_url_building_errors(self) -> None:
        """Test connection URL building with invalid configurations."""
        # Test with neither service_name nor sid - should fail at config validation
        with pytest.raises(
            ValueError, match="Either SID or service_name must be provided"
        ):
            FlextDbOracleConfig(
                host="test",
                port=1521,
                username="test",
                password=SecretStr("test"),
                # Neither service_name nor sid provided
            )

    def test_ensure_connected_when_not_connected(self) -> None:
        """Test _ensure_connected when not connected."""
        result = self.connection._ensure_connected()
        assert not result.success
        assert "not connected" in result.error.lower()

    def test_execute_when_not_connected(self) -> None:
        """Test execute method when not connected."""
        result = self.connection.execute("SELECT 1 FROM DUAL")
        assert not result.success
        assert "not connected" in result.error.lower()

    def test_execute_many_when_not_connected(self) -> None:
        """Test execute_many method when not connected."""
        result = self.connection.execute_many(
            "INSERT INTO test (id) VALUES (:id)", [{"id": 1}, {"id": 2}]
        )
        assert not result.success
        assert "not connected" in result.error.lower()

    def test_fetch_one_when_not_connected(self) -> None:
        """Test fetch_one method when not connected."""
        result = self.connection.fetch_one("SELECT 1 FROM DUAL")
        assert not result.success
        assert "not connected" in result.error.lower()

    def test_test_connection_when_not_connected(self) -> None:
        """Test test_connection method when not connected."""
        result = self.connection.test_connection()
        assert not result.success
        assert "not connected" in result.error.lower()

    def test_get_table_names_validation(self) -> None:
        """Test get_table_names parameter validation and error handling."""
        # Test with valid schema name
        result = self.connection.get_table_names("VALID_SCHEMA")
        assert not result.success  # Should fail due to no connection

        # Test with current user schema (no schema_name)
        result = self.connection.get_table_names()
        assert not result.success  # Should fail due to no connection

    def test_get_schemas_when_not_connected(self) -> None:
        """Test get_schemas method when not connected."""
        result = self.connection.get_schemas()
        assert not result.success
        assert (
            "not connected" in result.error.lower() or "failed" in result.error.lower()
        )

    def test_get_current_schema_when_not_connected(self) -> None:
        """Test get_current_schema method when not connected."""
        result = self.connection.get_current_schema()
        assert not result.success

    def test_build_table_names_query(self) -> None:
        """Test _build_table_names_query helper method."""
        # Test with schema name
        sql, params = self.connection._build_table_names_query("TEST_SCHEMA")
        assert "all_tables" in sql
        assert "owner = UPPER(:schema_name)" in sql
        assert params["schema_name"] == "TEST_SCHEMA"

        # Test without schema name
        sql, params = self.connection._build_table_names_query(None)
        assert "user_tables" in sql
        assert "schema_name" not in params
        assert params == {}

    def test_get_column_info_when_not_connected(self) -> None:
        """Test get_column_info method when not connected."""
        result = self.connection.get_column_info("TEST_TABLE")
        assert not result.success

    def test_build_column_info_query(self) -> None:
        """Test _build_column_info_query helper method."""
        # Test with schema name
        sql, params = self.connection._build_column_info_query(
            "TEST_TABLE", "TEST_SCHEMA"
        )
        assert "all_tab_columns" in sql
        assert "owner = UPPER(:schema_name)" in sql
        assert params["table_name"] == "TEST_TABLE"
        assert params["schema_name"] == "TEST_SCHEMA"

        # Test without schema name
        sql, params = self.connection._build_column_info_query("TEST_TABLE", None)
        assert "user_tab_columns" in sql
        assert "table_name = UPPER(:table_name)" in sql
        assert params["table_name"] == "TEST_TABLE"
        assert "schema_name" not in params

    def test_convert_column_row_to_dict(self) -> None:
        """Test _convert_column_row_to_dict helper method."""
        # Mock row data
        row_data = ["COLUMN_NAME", "VARCHAR2", "Y", 100, None, None, 1]

        result = self.connection._convert_column_row_to_dict(row_data)
        assert result["column_name"] == "COLUMN_NAME"
        assert result["data_type"] == "VARCHAR2"
        assert result["nullable"] is True
        assert result["data_length"] == 100
        assert result["column_id"] == 1

    def test_get_primary_key_columns_when_not_connected(self) -> None:
        """Test get_primary_key_columns method when not connected."""
        result = self.connection.get_primary_key_columns("TEST_TABLE")
        assert not result.success

    def test_build_primary_key_query(self) -> None:
        """Test _build_primary_key_query helper method."""
        # Test with schema name
        sql, params = self.connection._build_primary_key_query(
            "TEST_TABLE", "TEST_SCHEMA"
        )
        assert "all_cons_columns" in sql
        assert "all_constraints" in sql
        assert "owner = UPPER(:schema_name)" in sql
        assert params["table_name"] == "TEST_TABLE"
        assert params["schema_name"] == "TEST_SCHEMA"

        # Test without schema name
        sql, params = self.connection._build_primary_key_query("TEST_TABLE", None)
        assert "user_cons_columns" in sql
        assert "user_constraints" in sql
        assert params["table_name"] == "TEST_TABLE"

    def test_get_table_metadata_when_not_connected(self) -> None:
        """Test get_table_metadata method when not connected."""
        result = self.connection.get_table_metadata("TEST_TABLE")
        assert not result.success

    def test_query_building_methods(self) -> None:
        """Test SQL query building methods."""
        # Test build_select
        result = self.connection.build_select(
            "TEST_TABLE",
            columns=["ID", "NAME"],
            conditions={"STATUS": "ACTIVE"},
            schema_name="TEST_SCHEMA",
        )
        assert result.success
        sql = result.value
        assert "SELECT ID, NAME FROM TEST_SCHEMA.TEST_TABLE" in sql
        assert "WHERE STATUS = 'ACTIVE'" in sql

    def test_build_select_safe(self) -> None:
        """Test build_select_safe method for parameterized queries."""
        result = self.connection.build_select_safe(
            "TEST_TABLE",
            columns=["ID", "NAME"],
            conditions={"STATUS": "ACTIVE", "TYPE": "USER"},
            schema_name="TEST_SCHEMA",
        )
        assert result.success
        sql, params = result.value
        assert "SELECT ID, NAME FROM TEST_SCHEMA.TEST_TABLE" in sql
        assert ":param_STATUS" in sql
        assert ":param_TYPE" in sql
        assert params["param_STATUS"] == "ACTIVE"
        assert params["param_TYPE"] == "USER"

    def test_build_select_base(self) -> None:
        """Test _build_select_base helper method."""
        column_list, full_table_name = self.connection._build_select_base(
            "TEST_TABLE", columns=["ID", "NAME", "STATUS"], schema_name="TEST_SCHEMA"
        )
        assert column_list == "ID, NAME, STATUS"
        assert full_table_name == "TEST_SCHEMA.TEST_TABLE"

        # Test with no columns (should default to *)
        column_list, full_table_name = self.connection._build_select_base(
            "TEST_TABLE", columns=None, schema_name=None
        )
        assert column_list == "*"
        assert full_table_name == "TEST_TABLE"

    def test_build_table_name(self) -> None:
        """Test _build_table_name helper method."""
        # With schema
        result = self.connection._build_table_name("TEST_TABLE", "TEST_SCHEMA")
        assert result == "TEST_SCHEMA.TEST_TABLE"

        # Without schema
        result = self.connection._build_table_name("TEST_TABLE", None)
        assert result == "TEST_TABLE"

    def test_ddl_generation_methods(self) -> None:
        """Test DDL generation methods."""
        # Test column definition building
        column_def = {
            "name": "ID",
            "data_type": "NUMBER",
            "nullable": False,
            "primary_key": True,
        }
        result = self.connection._build_column_definition(column_def)
        assert result.success
        assert "ID NUMBER" in result.value
        assert "NOT NULL" in result.value

    def test_create_table_ddl(self) -> None:
        """Test create_table_ddl method."""
        columns = [
            {
                "name": "ID",
                "data_type": "NUMBER",
                "nullable": False,
                "primary_key": True,
            },
            {"name": "NAME", "data_type": "VARCHAR2(100)", "nullable": True},
        ]

        result = self.connection.create_table_ddl(
            "TEST_TABLE", columns, schema_name="TEST_SCHEMA"
        )
        assert result.success
        ddl = result.value
        assert "CREATE TABLE TEST_SCHEMA.TEST_TABLE" in ddl
        assert "ID NUMBER NOT NULL" in ddl
        assert "NAME VARCHAR2(100)" in ddl
        assert "PRIMARY KEY" in ddl

    def test_drop_table_ddl(self) -> None:
        """Test drop_table_ddl method."""
        result = self.connection.drop_table_ddl("TEST_TABLE", "TEST_SCHEMA")
        assert result.success
        assert result.value == "DROP TABLE TEST_SCHEMA.TEST_TABLE"

    def test_singer_type_conversion(self) -> None:
        """Test convert_singer_type method."""
        # Test string type
        result = self.connection.convert_singer_type("string")
        assert result.success
        assert "VARCHAR2" in result.value

        # Test number type
        result = self.connection.convert_singer_type("number")
        assert result.success
        assert "NUMBER" in result.value

        # Test array type with null
        result = self.connection.convert_singer_type(["string", "null"])
        assert result.success
        assert "VARCHAR2" in result.value

        # Test with format hint
        result = self.connection.convert_singer_type("string", "date-time")
        assert result.success
        assert "TIMESTAMP" in result.value

    def test_singer_schema_mapping(self) -> None:
        """Test map_singer_schema method."""
        singer_schema = {
            "properties": {
                "id": {"type": "integer"},
                "name": {"type": "string"},
                "created_at": {"type": "string", "format": "date-time"},
            }
        }

        result = self.connection.map_singer_schema(singer_schema)
        assert result.success
        mapping = result.value
        assert "id" in mapping
        assert "name" in mapping
        assert "created_at" in mapping
        assert "NUMBER" in mapping["id"]
        assert "VARCHAR2" in mapping["name"]
        assert "TIMESTAMP" in mapping["created_at"]

    def test_dml_statement_building(self) -> None:
        """Test DML statement building methods."""
        # Test INSERT statement
        result = self.connection.build_insert_statement(
            "TEST_TABLE",
            ["ID", "NAME", "STATUS"],
            schema_name="TEST_SCHEMA",
            returning_columns=["ID"],
        )
        assert result.success
        sql = result.value
        assert "INSERT INTO TEST_SCHEMA.TEST_TABLE" in sql
        assert "(ID, NAME, STATUS)" in sql
        assert "VALUES (:ID, :NAME, :STATUS)" in sql
        assert "RETURNING ID" in sql

        # Test UPDATE statement
        result = self.connection.build_update_statement(
            "TEST_TABLE",
            set_columns=["NAME", "STATUS"],
            where_columns=["ID"],
            schema_name="TEST_SCHEMA",
        )
        assert result.success
        sql = result.value
        assert "UPDATE TEST_SCHEMA.TEST_TABLE" in sql
        assert "SET NAME = :NAME, STATUS = :STATUS" in sql
        assert "WHERE ID = :where_ID" in sql

        # Test DELETE statement
        result = self.connection.build_delete_statement(
            "TEST_TABLE", where_columns=["ID", "STATUS"], schema_name="TEST_SCHEMA"
        )
        assert result.success
        sql = result.value
        assert "DELETE FROM TEST_SCHEMA.TEST_TABLE" in sql
        assert "WHERE ID = :ID AND STATUS = :STATUS" in sql

    def test_merge_statement_building(self) -> None:
        """Test MERGE statement building."""
        config = MergeStatementConfig(
            target_table="TARGET_TABLE",
            source_columns=["ID", "NAME", "STATUS"],
            merge_keys=["ID"],
            schema_name="TEST_SCHEMA",
        )

        result = self.connection.build_merge_statement(config)
        assert result.success
        sql = result.value
        assert "MERGE" in sql
        assert "INTO TEST_SCHEMA.TARGET_TABLE" in sql
        assert "USING (SELECT" in sql
        assert "ON (tgt.ID = src.ID)" in sql
        assert "WHEN MATCHED" in sql
        assert "WHEN NOT MATCHED" in sql

    def test_create_index_config_validation(self) -> None:
        """Test CreateIndexConfig validation."""
        # Valid config
        config = CreateIndexConfig(
            index_name="IDX_TEST", table_name="TEST_TABLE", columns=["ID", "NAME"]
        )
        assert config.index_name == "IDX_TEST"
        assert config.table_name == "TEST_TABLE"
        assert config.columns == ["ID", "NAME"]

        # Test validation
        result = config.validate_business_rules()
        assert result.success

    def test_create_index_statement_building(self) -> None:
        """Test CREATE INDEX statement building."""
        config = CreateIndexConfig(
            index_name="IDX_TEST",
            table_name="TEST_TABLE",
            columns=["ID", "NAME"],
            schema_name="TEST_SCHEMA",
            unique=True,
            tablespace="INDEXES",
            parallel=4,
        )

        result = self.connection.build_create_index_statement(config)
        assert result.success
        sql = result.value
        assert "CREATE UNIQUE INDEX TEST_SCHEMA.IDX_TEST" in sql
        assert "ON TEST_SCHEMA.TEST_TABLE (ID, NAME)" in sql
        assert "TABLESPACE INDEXES" in sql
        assert "PARALLEL 4" in sql

    def test_close_connection(self) -> None:
        """Test close method."""
        result = self.connection.close()
        assert result.success

    def test_execute_query_when_not_connected(self) -> None:
        """Test execute_query method when not connected."""
        result = self.connection.execute_query("SELECT 1 FROM DUAL")
        assert not result.success

    def test_error_handling_methods(self) -> None:
        """Test error handling helper methods."""
        # Test database error handling
        test_exception = Exception("Test database error")
        result = self.connection._handle_database_error_with_logging(
            "Test operation", test_exception
        )
        assert not result.success
        assert "Test operation: Test database error" in result.error

    def test_session_and_transaction_context_managers(self) -> None:
        """Test session and transaction context managers behavior when not connected."""
        # Test session context manager - should raise when not connected
        with pytest.raises(ValueError, match="Not connected"):
            with self.connection.session():
                pass

        # Test transaction context manager - should raise when not connected
        with pytest.raises(ValueError, match="Not connected to database"):
            with self.connection.transaction():
                pass
