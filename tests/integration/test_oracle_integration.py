"""Integration tests for flext-db-oracle with real Oracle connectivity patterns.

These tests use mock Oracle connections to simulate real integration scenarios
without requiring actual Oracle database instances.
"""

from __future__ import annotations

import os
from typing import TYPE_CHECKING, Any
from unittest.mock import MagicMock, patch

if TYPE_CHECKING:
    from collections.abc import Generator

import pytest
from flext_core import FlextResult

from flext_db_oracle import (
    FlextDbOracleApi,
    FlextDbOracleConfig,
)


class TestOracleIntegration:
    """Integration tests for Oracle database operations."""

    @pytest.fixture
    def mock_oracle_config(self) -> FlextDbOracleConfig:
        """Create a test Oracle configuration."""
        return FlextDbOracleConfig(
            host="internal.invalid",
            port=1521,
            service_name="TESTDB",
            username="testuser",
            password="testpass",
        )

    @pytest.fixture
    def mock_connection(self, mock_oracle_config: FlextDbOracleConfig) -> MagicMock:
        """Create a mocked Oracle connection."""
        from contextlib import contextmanager

        mock_conn = MagicMock()
        mock_conn.connect.return_value = FlextResult.ok(data=True)
        mock_conn.disconnect.return_value = FlextResult.ok(data=True)
        mock_conn.execute.return_value = FlextResult.ok([("result",)])
        mock_conn.fetch_one.return_value = FlextResult.ok(("single_result",))
        mock_conn.get_table_names.return_value = FlextResult.ok(["TEST_TABLE"])
        mock_conn.get_column_info.return_value = FlextResult.ok(
            [
                {
                    "column_name": "ID",
                    "data_type": "NUMBER",
                    "nullable": False,
                    "default_value": None,
                    "data_length": None,
                    "data_precision": 10,
                    "data_scale": 0,
                    "column_id": 1,
                    "comments": "Primary key",
                },
            ],
        )
        mock_conn.create_table_ddl.return_value = FlextResult.ok(
            "CREATE TABLE new_table (id NUMBER NOT NULL, name VARCHAR2(100))",
        )
        mock_conn.drop_table_ddl.return_value = FlextResult.ok("DROP TABLE test_table")

        # Mock transaction context manager
        @contextmanager
        def mock_transaction() -> Generator[Any]:
            yield mock_conn

        mock_conn.transaction = mock_transaction
        mock_conn.begin_transaction.return_value = FlextResult.ok(data=True)
        mock_conn.commit_transaction.return_value = FlextResult.ok(data=True)
        mock_conn.rollback_transaction.return_value = FlextResult.ok(data=True)
        return mock_conn

    def test_api_full_workflow(
        self,
        mock_oracle_config: FlextDbOracleConfig,
        mock_connection: MagicMock,
    ) -> None:
        """Test complete API workflow from configuration to query execution."""
        # Mock DDL generation result
        mock_connection.create_table_ddl.return_value = FlextResult.ok(
            "CREATE TABLE new_table (id NUMBER NOT NULL, name VARCHAR2(100))",
        )

        with patch(
            "flext_db_oracle.api.FlextDbOracleConnection", return_value=mock_connection,
        ):
            # Initialize API
            api = FlextDbOracleApi(mock_oracle_config)

            # Connect
            connected_api = api.connect()
            assert connected_api is api

            # Execute query
            result = api.query("SELECT * FROM test_table")
            assert result.is_success
            assert result.data == [("result",)]

            # Test single query
            single_result = api.query_one("SELECT COUNT(*) FROM test_table")
            assert single_result.is_success
            assert single_result.data == ("single_result",)

            # Test DDL generation
            ddl_result = api.create_table_ddl(
                "new_table",
                [
                    {"name": "id", "type": "number", "nullable": False},
                    {"name": "name", "type": "varchar2(100)", "nullable": True},
                ],
            )
            assert ddl_result.is_success
            assert "CREATE TABLE" in ddl_result.data

            # Disconnect
            api.disconnect()

    def test_connection_error_handling(
        self, mock_oracle_config: FlextDbOracleConfig,
    ) -> None:
        """Test connection error handling."""
        with patch("flext_db_oracle.api.FlextDbOracleConnection") as mock_conn_class:
            mock_conn = MagicMock()
            mock_conn.connect.return_value = FlextResult.fail("Connection failed")
            mock_conn_class.return_value = mock_conn

            api = FlextDbOracleApi(mock_oracle_config)

            with pytest.raises(ConnectionError, match="Failed to connect"):
                api.connect()

    def test_transaction_context_manager(
        self,
        mock_oracle_config: FlextDbOracleConfig,
        mock_connection: MagicMock,
    ) -> None:
        """Test transaction context manager functionality."""
        with patch(
            "flext_db_oracle.api.FlextDbOracleConnection", return_value=mock_connection,
        ):
            api = FlextDbOracleApi(mock_oracle_config).connect()

            # Test successful transaction
            with api.transaction() as tx_api:
                result = tx_api.query("SELECT 1 FROM DUAL")
                assert result.is_success
                assert tx_api is api  # Should return the same API instance

    def test_batch_operations(
        self,
        mock_oracle_config: FlextDbOracleConfig,
        mock_connection: MagicMock,
    ) -> None:
        """Test batch operation execution."""
        mock_connection.execute.side_effect = [
            FlextResult.ok("Result 1"),
            FlextResult.ok("Result 2"),
            FlextResult.ok("Result 3"),
        ]

        with patch(
            "flext_db_oracle.api.FlextDbOracleConnection", return_value=mock_connection,
        ):
            api = FlextDbOracleApi(mock_oracle_config).connect()

            operations = [
                ("INSERT INTO table1 VALUES (?)", {"value": 1}),
                ("INSERT INTO table2 VALUES (?)", {"value": 2}),
                ("UPDATE table3 SET col = ?", {"col": "updated"}),
            ]

            result = api.execute_batch(operations)
            assert result.is_success
            assert result.data == ["Result 1", "Result 2", "Result 3"]

    def test_metadata_operations(
        self,
        mock_oracle_config: FlextDbOracleConfig,
        mock_connection: MagicMock,
    ) -> None:
        """Test metadata retrieval operations."""
        with patch(
            "flext_db_oracle.api.FlextDbOracleConnection", return_value=mock_connection,
        ):
            api = FlextDbOracleApi(mock_oracle_config).connect()

            # Test table metadata
            table_meta_result = api.get_table_metadata("TEST_TABLE")
            assert table_meta_result.is_success

            # Test schema listing
            tables_result = api.get_tables()
            assert tables_result.is_success
            assert tables_result.data == ["TEST_TABLE"]

            # Test column information
            columns_result = api.get_columns("TEST_TABLE")
            assert columns_result.is_success
            assert len(columns_result.data) > 0

    def test_configuration_from_environment(self) -> None:
        """Test configuration creation from environment variables."""
        env_vars = {
            "FLEXT_TARGET_ORACLE_HOST": "internal.invalid",
            "FLEXT_TARGET_ORACLE_PORT": "1522",
            "FLEXT_TARGET_ORACLE_SERVICE_NAME": "ENVDB",
            "FLEXT_TARGET_ORACLE_USERNAME": "envuser",
            "FLEXT_TARGET_ORACLE_PASSWORD": "envpass",
        }

        with patch.dict(os.environ, env_vars):
            result = FlextDbOracleConfig.from_env()
            assert result.is_success

            config = result.data
            assert config.host == "internal.invalid"
            assert config.port == 1522
            assert config.service_name == "ENVDB"
            assert config.username == "envuser"
            assert config.password.get_secret_value() == "envpass"

    def test_api_factory_methods(self) -> None:
        """Test API factory method creation."""
        # Test from_env factory
        env_vars = {
            "FLEXT_TARGET_ORACLE_HOST": "internal.invalid",
            "FLEXT_TARGET_ORACLE_SERVICE_NAME": "FACTORYDB",
            "FLEXT_TARGET_ORACLE_USERNAME": "factoryuser",
            "FLEXT_TARGET_ORACLE_PASSWORD": "factorypass",
        }

        with patch.dict(os.environ, env_vars):
            api = FlextDbOracleApi.from_env()
            assert isinstance(api, FlextDbOracleApi)

        # Test with_config factory
        api2 = FlextDbOracleApi.with_config(
            host="internal.invalid",
            service_name="CONFIGDB",
            username="configuser",
            password="configpass",
        )
        assert isinstance(api2, FlextDbOracleApi)

    def test_connection_retry_mechanism(
        self, mock_oracle_config: FlextDbOracleConfig,
    ) -> None:
        """Test connection retry mechanism."""
        with patch("flext_db_oracle.api.FlextDbOracleConnection") as mock_conn_class:
            mock_conn = MagicMock()
            # First two attempts fail, third succeeds
            mock_conn.connect.side_effect = [
                FlextResult.fail("Connection timeout"),
                FlextResult.fail("Network error"),
                FlextResult.ok(data=True),
            ]
            mock_conn_class.return_value = mock_conn

            api = FlextDbOracleApi(mock_oracle_config)
            connected_api = api.connect()

            assert connected_api is api
            # Verify connect was called 3 times (2 retries + 1 success)
            assert mock_conn.connect.call_count == 3

    def test_context_manager_integration(
        self,
        mock_oracle_config: FlextDbOracleConfig,
        mock_connection: MagicMock,
    ) -> None:
        """Test API as context manager."""
        with patch(
            "flext_db_oracle.api.FlextDbOracleConnection", return_value=mock_connection,
        ):
            with FlextDbOracleApi(mock_oracle_config) as api:
                result = api.query("SELECT 1 FROM DUAL")
                assert result.is_success

            # Verify connection was established and closed
            mock_connection.connect.assert_called()
            mock_connection.disconnect.assert_called()

    def test_singer_type_conversion_integration(
        self,
        mock_oracle_config: FlextDbOracleConfig,
        mock_connection: MagicMock,
    ) -> None:
        """Test Singer type conversion functionality."""

        # Mock the convert_singer_type method
        def mock_convert_type(
            singer_type: str, format_hint: str | None = None,
        ) -> FlextResult[str]:
            type_map = {
                "string": "VARCHAR2(4000)",
                "integer": "NUMBER(38)",
                "number": "NUMBER",
                "boolean": "NUMBER(1)",
                "array": "CLOB",
                "object": "CLOB",
            }
            return FlextResult.ok(type_map.get(singer_type, "VARCHAR2(4000)"))

        mock_connection.convert_singer_type.side_effect = mock_convert_type

        with patch(
            "flext_db_oracle.api.FlextDbOracleConnection", return_value=mock_connection,
        ):
            api = FlextDbOracleApi(mock_oracle_config).connect()

            # Test various Singer type conversions
            conversions = [
                ("string", "VARCHAR2(4000)"),
                ("integer", "NUMBER(38)"),
                ("number", "NUMBER"),
                ("boolean", "NUMBER(1)"),
                ("array", "CLOB"),
                ("object", "CLOB"),
            ]

            for singer_type, expected_oracle_type in conversions:
                result = api.convert_singer_type(singer_type)
                assert result.is_success
                assert result.data == expected_oracle_type

    def test_ddl_generation_integration(
        self,
        mock_oracle_config: FlextDbOracleConfig,
        mock_connection: MagicMock,
    ) -> None:
        """Test DDL generation with various scenarios."""
        # Mock DDL generation methods
        mock_connection.create_table_ddl.return_value = FlextResult.ok(
            "CREATE TABLE test_schema.users ("
            "id number(10) NOT NULL, "
            "name varchar2(100) NOT NULL, "
            "email varchar2(255), "
            "created_at timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP"
            ")",
        )
        mock_connection.drop_table_ddl.return_value = FlextResult.ok(
            "DROP TABLE test_schema.users",
        )

        with patch(
            "flext_db_oracle.api.FlextDbOracleConnection", return_value=mock_connection,
        ):
            api = FlextDbOracleApi(mock_oracle_config).connect()

            # Test CREATE TABLE DDL
            columns = [
                {
                    "name": "id",
                    "type": "number(10)",
                    "nullable": False,
                    "primary_key": True,
                },
                {"name": "name", "type": "varchar2(100)", "nullable": False},
                {"name": "email", "type": "varchar2(255)", "nullable": True},
                {
                    "name": "created_at",
                    "type": "timestamp",
                    "nullable": False,
                    "default_value": "CURRENT_TIMESTAMP",
                },
            ]

            create_result = api.create_table_ddl("users", columns, schema="test_schema")
            assert create_result.is_success
            ddl = create_result.data
            assert "CREATE TABLE test_schema.users" in ddl
            assert "id number(10) NOT NULL" in ddl
            assert "name varchar2(100) NOT NULL" in ddl
            assert "email varchar2(255)" in ddl
            assert "created_at timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP" in ddl

            # Test DROP TABLE DDL
            drop_result = api.drop_table_ddl("users", schema="test_schema")
            assert drop_result.is_success
            assert drop_result.data == "DROP TABLE test_schema.users"
