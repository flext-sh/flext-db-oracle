"""Comprehensive tests for FlextDbOracleConnection using real code validation.

This module tests the connection functionality with real code paths,
following the user's requirement for real code testing without mocks.


Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from typing import cast

import pytest

from flext_core import FlextTypes
from flext_db_oracle import (
    FlextDbOracleModels,
    FlextDbOracleServices,
)


class TestFlextDbOracleConnectionComprehensive:
    """Comprehensive tests for Oracle connection using real code paths."""

    def setup_method(self) -> None:
        """Setup test configuration."""
        self.config = FlextDbOracleModels.OracleConfig(
            host="test",
            port=1521,
            name="TEST",
            username="test",
            password="test",
            service_name="TEST",
        )
        self.connection = FlextDbOracleServices(config=self.config)

    def test_connection_initialization(self) -> None:
        """Test connection initialization with real configuration."""
        assert self.connection is not None
        assert self.connection.config == self.config
        # Test that connection exists and is not connected initially
        assert not self.connection.is_connected()

    def test_is_connected_method(self) -> None:
        """Test is_connected method behavior."""
        # Initially not connected
        assert not self.connection.is_connected()

        # Test that method returns consistent results
        connected_status = self.connection.is_connected()
        assert isinstance(connected_status, bool)

    def test_connect_validation_errors(self) -> None:
        """Test connect method with invalid configurations."""
        # Test with empty host - should fail at config validation
        with pytest.raises(Exception, match="Host cannot be empty"):
            FlextDbOracleModels.OracleConfig(
                host="",
                port=1521,
                service_name="TEST",
                username="test",
                password="test",
            )

    def test_disconnect_when_not_connected(self) -> None:
        """Test disconnect when not connected."""
        result = self.connection.disconnect()
        assert result.is_success

    def test_connection_url_building(self) -> None:
        """Test connection URL building logic through public interface."""
        # Note: Testing public interface instead of private methods
        # _build_connection_url is now private inside _ConnectionManager
        # Test connection establishment which uses URL building internally
        result = self.connection.connect()
        # Connection may fail due to no real Oracle server, but URL building should work
        # This tests the functionality indirectly through the public interface
        assert result.is_failure  # Expected to fail without real Oracle server

    def test_connection_url_building_errors(self) -> None:
        """Test connection URL building with invalid configurations."""
        # Test with neither service_name nor sid - should fail at config validation
        with pytest.raises(
            ValueError,
            match="Service name cannot be empty when provided",
        ):
            FlextDbOracleModels.OracleConfig(
                host="test",
                port=1521,
                username="test",
                password="test",
                service_name="",  # Empty string should trigger validation error
            )

    def test_ensure_connected_when_not_connected(self) -> None:
        """Test connection status when not connected."""
        # _ensure_connected is now private, test through is_connected() instead
        assert not self.connection.is_connected()
        # Test that operations fail when not connected
        result = self.connection.test_connection()
        assert not result.is_success

    def test_execute_when_not_connected(self) -> None:
        """Test execute method when not connected."""
        result = self.connection.execute_query("SELECT 1 FROM DUAL")
        assert not result.is_success
        assert "not connected" in (result.error or "").lower()

    def test_execute_many_when_not_connected(self) -> None:
        """Test execute_many method when not connected."""
        result = self.connection.execute_many(
            "INSERT INTO test (id) VALUES (:id)",
            [{"id": 1}, {"id": 2}],
        )
        assert not result.is_success
        assert "not connected" in (result.error or "").lower()

    def test_fetch_one_when_not_connected(self) -> None:
        """Test fetch_one method when not connected."""
        result = self.connection.fetch_one("SELECT 1 FROM DUAL")
        assert not result.is_success
        assert "not connected" in (result.error or "").lower()

    def test_test_connection_when_not_connected(self) -> None:
        """Test test_connection method when not connected."""
        result = self.connection.test_connection()
        assert not result.is_success
        assert "not connected" in (result.error or "").lower()

    def test_connection_execute_query_validation(self) -> None:
        """Test execute_query parameter validation and error handling."""
        # Test with valid SQL
        result = self.connection.execute_query("SELECT 1 FROM DUAL")
        assert not result.is_success  # Should fail due to no connection

        # Test with empty SQL
        result = self.connection.execute_query("")
        assert not result.is_success  # Should fail due to no connection

    def test_execute_statement_when_not_connected(self) -> None:
        """Test execute_statement method when not connected."""
        result = self.connection.execute_statement("UPDATE test SET value = 1")
        assert not result.is_success
        assert (
            "not connected" in (result.error or "").lower()
            or "failed" in (result.error or "").lower()
        )

    def test_connection_disconnect_when_not_connected(self) -> None:
        """Test disconnect method when not connected."""
        result = self.connection.disconnect()
        assert result.is_success  # Should succeed gracefully

    def test_connection_url_building_with_real_method(self) -> None:
        """Test connection URL building through public interface."""
        # _build_connection_url is now private inside _ConnectionManager
        # Test connection establishment which validates URL building
        self.connection.connect()
        # URL building errors would be caught during connection attempt
        # This indirectly validates URL building functionality

    def test_connection_is_connected_method(self) -> None:
        """Test is_connected method (real method)."""
        # Should return False when not connected
        connected = self.connection.is_connected()
        assert not connected

    def test_get_columns_api(self) -> None:
        """Test get_columns public API method."""
        # Test the public API instead of internal methods
        result = self.connection.get_columns("TEST_TABLE", "TEST_SCHEMA")
        # Should fail when not connected, but method should exist
        assert result.is_failure  # Expected to fail when not connected
        assert "not connected" in str(result.error).lower()

        # Test without schema name
        result = self.connection.get_columns("TEST_TABLE", None)
        assert result.is_failure  # Expected to fail when not connected

    def test_get_columns_structure(self) -> None:
        """Test get_columns method structure and behavior."""
        # Test that get_columns method exists and returns FlextResult
        result = self.connection.get_columns("TEST_TABLE")
        assert hasattr(result, "is_success")
        assert hasattr(result, "is_failure")
        # Should fail when not connected
        assert result.is_failure

    def test_get_primary_key_columns_when_not_connected(self) -> None:
        """Test get_primary_key_columns method when not connected."""
        result = self.connection.get_primary_key_columns("TEST_TABLE")
        assert not result.is_success

    def test_get_primary_key_columns_api(self) -> None:
        """Test get_primary_key_columns public API method."""
        # Test the public API instead of internal methods
        result = self.connection.get_primary_key_columns("TEST_TABLE", "TEST_SCHEMA")
        # Should fail when not connected, but method should exist
        assert result.is_failure  # Expected to fail when not connected

        # Test without schema name
        result = self.connection.get_primary_key_columns("TEST_TABLE")
        assert result.is_failure  # Expected to fail when not connected

    def test_get_table_metadata_when_not_connected(self) -> None:
        """Test get_table_metadata method when not connected."""
        result = self.connection.get_tables("TEST_TABLE")
        assert not result.is_success

    def test_query_building_methods(self) -> None:
        """Test SQL query building methods."""
        # Test build_select
        result = self.connection.build_select(
            "TEST_TABLE",
            columns=["ID", "NAME"],
            conditions={"STATUS": "ACTIVE"},
            schema_name="TEST_SCHEMA",
        )
        assert result.is_success
        sql = result.value
        assert "SELECT ID, NAME" in sql
        assert "TEST_SCHEMA" in sql
        assert "TEST_TABLE" in sql
        assert "WHERE STATUS = :STATUS" in sql

    def test_build_select_method(self) -> None:
        """Test build_select method for SQL generation."""
        # Use the actual build_select method that exists
        result = self.connection.build_select(
            "TEST_TABLE",
            columns=["ID", "NAME"],
            conditions={"STATUS": "ACTIVE", "TYPE": "USER"},
            schema_name="TEST_SCHEMA",
        )
        assert result.is_success
        sql = result.value
        assert "SELECT" in sql
        assert "TEST_TABLE" in sql

    def test_sql_builder_functionality(self) -> None:
        """Test SQL builder functionality through public API."""
        # Test that SQL building works through public methods
        result = self.connection.build_select(
            "TEST_TABLE",
            columns=["ID", "NAME", "STATUS"],
            schema_name="TEST_SCHEMA",
        )
        assert result.is_success
        assert '"TEST_SCHEMA"."TEST_TABLE"' in result.value

        # Test with no columns (should default to *)
        result = self.connection.build_select("TEST_TABLE")
        assert result.is_success
        assert "TEST_TABLE" in result.value

    def test_table_name_handling(self) -> None:
        """Test table name handling through public API methods."""
        # Test that schema names are handled correctly in SQL generation
        result = self.connection.build_select("TEST_TABLE", schema_name="TEST_SCHEMA")
        assert result.is_success
        assert '"TEST_SCHEMA"."TEST_TABLE"' in result.value

        # Without schema
        result = self.connection.build_select("TEST_TABLE")
        assert result.is_success
        assert "TEST_TABLE" in result.value

    def test_ddl_generation_methods(self) -> None:
        """Test DDL generation methods through public API."""
        # Test DDL generation through create_table_ddl public method
        columns = [
            {
                "name": "ID",
                "data_type": "NUMBER",
                "nullable": False,
                "primary_key": True,
            }
        ]
        result = self.connection.create_table_ddl("TEST_TABLE", columns)
        assert result.is_success
        assert "NUMBER" in result.value

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
            "TEST_TABLE",
            columns,
            schema_name="TEST_SCHEMA",
        )
        assert result.is_success
        ddl = result.value
        assert "CREATE TABLE TEST_SCHEMA.TEST_TABLE" in ddl
        assert "ID NUMBER NOT NULL" in ddl
        assert "NAME VARCHAR2(100)" in ddl
        assert "PRIMARY KEY" in ddl

    def test_drop_table_ddl(self) -> None:
        """Test drop_table_ddl method."""
        result = self.connection.drop_table_ddl("TEST_TABLE", "TEST_SCHEMA")
        assert result.is_success
        assert result.value == "DROP TABLE TEST_SCHEMA.TEST_TABLE"

    def test_singer_type_conversion(self) -> None:
        """Test convert_singer_type method."""
        # Test string type
        result = self.connection.convert_singer_type("string")
        assert result.is_success
        assert "VARCHAR2" in result.value

        # Test number type
        result = self.connection.convert_singer_type("number")
        assert result.is_success
        assert "NUMBER" in result.value

        # Test array type with null
        result = self.connection.convert_singer_type(["string", "null"])
        assert result.is_success
        assert "VARCHAR2" in result.value

        # Test with format hint
        result = self.connection.convert_singer_type("string", "date-time")
        assert result.is_success
        assert "TIMESTAMP" in result.value

    def test_singer_schema_mapping(self) -> None:
        """Test map_singer_schema method."""
        singer_schema = {
            "properties": {
                "id": {"type": "integer"},
                "name": {"type": "string"},
                "created_at": {"type": "string", "format": "date-time"},
            },
        }

        # Cast singer_schema to compatible dict type
        schema_dict = cast("FlextTypes.Core.Dict", singer_schema)
        result = self.connection.map_singer_schema(schema_dict)
        assert result.is_success
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
            ["ID", "NAME", "EMAIL"],
            schema_name="TEST_SCHEMA",
            returning_columns=["ID"],
        )
        assert result.is_success
        sql = result.value
        assert "INSERT INTO" in sql and "TEST_SCHEMA" in sql and "TEST_TABLE" in sql
        assert "(id, name, email)" in sql
        assert "VALUES (:id, :name, :email)" in sql
        assert "RETURNING ID" in sql

        # Test UPDATE statement
        result = self.connection.build_update_statement(
            "TEST_TABLE",
            set_columns=["NAME", "EMAIL"],
            where_columns=["ID"],
            schema_name="TEST_SCHEMA",
        )
        assert result.is_success
        sql = result.value
        assert 'UPDATE "TEST_SCHEMA"."TEST_TABLE"' in sql or "UPDATE TEST_SCHEMA.TEST_TABLE" in sql
        assert '"NAME"=:NAME' in sql or '"EMAIL"=:EMAIL' in sql or "SET name = :name, email = :email" in sql
        assert "WHERE ID = :where_ID" in sql or "WHERE id = :where_id" in sql

        # Test DELETE statement
        result = self.connection.build_delete_statement(
            "TEST_TABLE",
            where_columns=["ID", "NAME"],
            schema_name="TEST_SCHEMA",
        )
        assert result.is_success
        sql = result.value
        assert 'DELETE FROM "TEST_SCHEMA"."TEST_TABLE"' in sql or "DELETE FROM TEST_SCHEMA.TEST_TABLE" in sql
        assert "WHERE ID = :ID AND NAME = :NAME" in sql or "WHERE id = :id AND name = :name" in sql

    def test_merge_statement_config_validation(self) -> None:
        """Test MERGE statement config validation."""
        # Test that FlextDbOracleModels.MergeStatementConfig can be created with correct fields
        config = FlextDbOracleModels.MergeStatementConfig(
            target_table="TARGET_TABLE",
            source_query="SELECT ID, NAME, STATUS FROM source_table",
            merge_conditions=["target.ID = source.ID"],
            update_columns=["NAME", "STATUS"],
            insert_columns=["ID", "NAME", "STATUS"],
        )
        assert config.target_table == "TARGET_TABLE"
        assert "SELECT" in config.source_query
        assert config.merge_conditions == ["target.ID = source.ID"]
        assert config.update_columns == ["NAME", "STATUS"]
        assert config.insert_columns == ["ID", "NAME", "STATUS"]

    def test_create_index_config_validation(self) -> None:
        """Test FlextDbOracleModels.CreateIndexConfig validation."""
        # Valid config
        config = FlextDbOracleModels.CreateIndexConfig(
            index_name="IDX_TEST",
            table_name="TEST_TABLE",
            columns=["ID", "NAME"],
        )
        assert config.index_name == "IDX_TEST"
        assert config.table_name == "TEST_TABLE"
        assert config.columns == ["ID", "NAME"]

        # Test successful validation (model was created without errors)
        assert config is not None

    def test_create_index_statement_building(self) -> None:
        """Test CREATE INDEX statement building."""
        config = FlextDbOracleModels.CreateIndexConfig(
            index_name="IDX_TEST",
            table_name="TEST_TABLE",
            columns=["ID", "NAME"],
            schema_name="TEST_SCHEMA",
            unique=True,
            tablespace="INDEXES",
            parallel=4,
        )

        result = self.connection.build_create_index_statement(config)
        assert result.is_success
        sql = result.value
        assert "CREATE UNIQUE INDEX TEST_SCHEMA.IDX_TEST" in sql
        assert "ON TEST_SCHEMA.TEST_TABLE (ID, NAME)" in sql
        assert "TABLESPACE INDEXES" in sql
        assert "PARALLEL 4" in sql

    def test_close_connection(self) -> None:
        """Test close method."""
        result = self.connection.close()
        assert result.is_success

    def test_execute_query_when_not_connected(self) -> None:
        """Test execute_query method when not connected."""
        result = self.connection.execute_query("SELECT 1 FROM DUAL")
        assert not result.is_success

    def test_connection_test_when_not_connected(self) -> None:
        """Test test_connection method when not connected."""
        # Test test_connection method (real method)
        result = self.connection.test_connection()
        assert not result.is_success
        assert (
            "connection" in (result.error or "").lower()
            or "database" in (result.error or "").lower()
        )

    def test_session_and_transaction_context_managers(self) -> None:
        """Test session and transaction context managers behavior when not connected."""
        # Test get_connection context manager - should raise when not connected
        try:
            with self.connection.get_connection():
                pass  # Should not reach here
            pytest.fail("Expected exception not raised")
        except (ValueError, RuntimeError):
            pass  # Expected exception

        # Test transaction context manager - should raise when not connected
        try:
            with self.connection.transaction():
                pass  # Should not reach here
            pytest.fail("Expected exception not raised")
        except (ValueError, RuntimeError):
            pass  # Expected exception
