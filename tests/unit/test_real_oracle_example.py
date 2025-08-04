"""Exemplo de testes REAIS usando Oracle.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import contextlib

from flext_db_oracle import (
    FlextDbOracleApi,
    FlextDbOracleConfig,
    FlextDbOracleConnection,
)


class TestRealOracleConnection:
    """Testes reais de conexão Oracle - SEM MOCKS."""

    def test_real_connection_connect_disconnect(
        self,
        real_oracle_config: FlextDbOracleConfig,
    ) -> None:
        """Test real Oracle connection and disconnection."""
        connection = FlextDbOracleConnection(real_oracle_config)

        # Test connect
        result = connection.connect()
        assert result.success, f"Connection failed: {result.error}"
        assert connection.is_connected()

        # Test disconnect
        result = connection.disconnect()
        assert result.success, f"Disconnect failed: {result.error}"
        assert not connection.is_connected()

    def test_real_connection_execute_query(
        self,
        real_oracle_config: FlextDbOracleConfig,
    ) -> None:
        """Test real Oracle query execution."""
        connection = FlextDbOracleConnection(real_oracle_config)

        # Connect first
        connect_result = connection.connect()
        assert connect_result.success

        try:
            # Execute simple query
            result = connection.execute("SELECT 1 FROM DUAL")
            assert result.success, f"Query failed: {result.error}"
            assert len(result.data) == 1
            assert result.data[0][0] == 1

        finally:
            connection.disconnect()

    def test_real_connection_fetch_one(
        self,
        real_oracle_config: FlextDbOracleConfig,
    ) -> None:
        """Test real Oracle fetch_one."""
        connection = FlextDbOracleConnection(real_oracle_config)

        # Connect first
        connect_result = connection.connect()
        assert connect_result.success

        try:
            # Fetch one row
            result = connection.fetch_one("SELECT 42 FROM DUAL")
            assert result.success, f"Fetch one failed: {result.error}"
            assert result.data[0] == 42

        finally:
            connection.disconnect()

    def test_real_connection_execute_many(
        self,
        real_oracle_config: FlextDbOracleConfig,
    ) -> None:
        """Test real Oracle execute_many with temporary table."""
        connection = FlextDbOracleConnection(real_oracle_config)

        # Connect first
        connect_result = connection.connect()
        assert connect_result.success

        try:
            # Drop table if it already exists (cleanup from previous runs)
            connection.execute(
                "DROP TABLE temp_test_table",
            )  # Ignore errors - table might not exist

            # Create temporary table with PRESERVE ROWS to survive commit
            create_result = connection.execute("""
                CREATE GLOBAL TEMPORARY TABLE temp_test_table (
                    id NUMBER,
                    name VARCHAR2(100)
                ) ON COMMIT PRESERVE ROWS
            """)
            assert create_result.success, (
                f"Table creation failed: {create_result.error}"
            )

            # Execute many inserts
            params_list = [
                {"id": 1, "name": "Test 1"},
                {"id": 2, "name": "Test 2"},
                {"id": 3, "name": "Test 3"},
            ]

            result = connection.execute_many(
                "INSERT INTO temp_test_table (id, name) VALUES (:id, :name)",
                params_list,
            )
            assert result.success, f"Execute many failed: {result.error}"
            assert result.data == 3  # Row count

            # Verify data
            select_result = connection.execute("SELECT COUNT(*) FROM temp_test_table")
            assert select_result.success
            assert select_result.data[0][0] == 3

        finally:
            # Cleanup - drop temp table manually since PRESERVE ROWS keeps data
            with contextlib.suppress(Exception):
                connection.execute("DROP TABLE temp_test_table")
            connection.disconnect()


class TestRealOracleApi:
    """Testes reais da API Oracle - SEM MOCKS."""

    def test_real_api_connect_context_manager(
        self,
        real_oracle_config: FlextDbOracleConfig,
    ) -> None:
        """Test real Oracle API with context manager."""
        with FlextDbOracleApi(real_oracle_config) as api:
            # Test connection
            test_result = api.test_connection()
            assert test_result.success, f"Connection test failed: {test_result.error}"

            # Test simple query
            query_result = api.query("SELECT 'Hello Oracle' FROM DUAL")
            assert query_result.success, f"Query failed: {query_result.error}"
            # SQLAlchemy Row objects are returned as tuples: rows[0][0] = ('Hello Oracle',)
            # To get the actual string value, we need to access the first element of the tuple
            assert query_result.data.rows[0][0][0] == "Hello Oracle"

    def test_real_api_get_schemas(self, connected_oracle_api: FlextDbOracleApi) -> None:
        """Test real Oracle schema listing."""
        result = connected_oracle_api.get_schemas()
        assert result.success, f"Get schemas failed: {result.error}"

        # Should have at least FLEXTTEST and system schemas
        schemas = result.data
        assert len(schemas) > 0
        assert any("FLEXTTEST" in str(schema).upper() for schema in schemas)

    def test_real_api_get_tables(self, connected_oracle_api: FlextDbOracleApi) -> None:
        """Test real Oracle table listing."""
        result = connected_oracle_api.get_tables()
        assert result.success, f"Get tables failed: {result.error}"

        # Should have test tables from init.sql
        tables = result.data
        assert len(tables) > 0
        expected_tables = ["EMPLOYEES", "DEPARTMENTS", "JOBS"]
        for table in expected_tables:
            assert any(table in str(t).upper() for t in tables), (
                f"Table {table} not found"
            )

    def test_real_api_get_columns(self, connected_oracle_api: FlextDbOracleApi) -> None:
        """Test real Oracle column listing."""
        result = connected_oracle_api.get_columns("EMPLOYEES")
        assert result.success, f"Get columns failed: {result.error}"

        # Should have columns from EMPLOYEES table
        columns = result.data
        assert len(columns) > 0

        # Check for expected columns
        column_names = [col["column_name"].upper() for col in columns]
        expected_columns = ["EMPLOYEE_ID", "FIRST_NAME", "LAST_NAME", "EMAIL"]
        for col in expected_columns:
            assert col in column_names, f"Column {col} not found"

    def test_real_api_query_with_timing(
        self,
        connected_oracle_api: FlextDbOracleApi,
    ) -> None:
        """Test real Oracle query with timing."""
        result = connected_oracle_api.query_with_timing(
            "SELECT COUNT(*) FROM EMPLOYEES",
        )
        assert result.success, f"Query with timing failed: {result.error}"

        # Should have timing information
        query_result = result.data
        assert hasattr(query_result, "execution_time_ms")
        assert query_result.execution_time_ms >= 0
        assert query_result.row_count >= 0
        assert len(query_result.rows) > 0

    def test_real_api_singer_type_conversion(
        self,
        connected_oracle_api: FlextDbOracleApi,
    ) -> None:
        """Test real Singer type conversion."""
        test_cases = [
            ("string", "VARCHAR2(4000)"),
            ("integer", "NUMBER(38)"),
            ("number", "NUMBER"),
            ("boolean", "NUMBER(1)"),
            ("string", "date-time", "TIMESTAMP"),
        ]

        for args in test_cases:
            if len(args) == 2:
                singer_type, expected = args
                result = connected_oracle_api.convert_singer_type(singer_type)
            else:
                singer_type, format_hint, expected = args
                result = connected_oracle_api.convert_singer_type(
                    singer_type,
                    format_hint,
                )

            assert result.success, (
                f"Type conversion failed for {singer_type}: {result.error}"
            )
            assert expected in result.data, f"Expected {expected} in {result.data}"

    def test_real_api_table_operations(
        self,
        connected_oracle_api: FlextDbOracleApi,
    ) -> None:
        """Test real Oracle table operations."""
        table_name = "TEST_TEMP_TABLE"

        try:
            # Create table DDL
            columns = [
                {"name": "id", "type": "NUMBER", "nullable": False},
                {"name": "name", "type": "VARCHAR2(100)", "nullable": True},
                {
                    "name": "created_at",
                    "type": "TIMESTAMP",
                    "nullable": True,
                    "default_value": "SYSDATE",
                },
            ]

            ddl_result = connected_oracle_api.create_table_ddl(table_name, columns)
            assert ddl_result.success, f"DDL generation failed: {ddl_result.error}"

            # Execute DDL
            execute_result = connected_oracle_api.execute_ddl(ddl_result.data)
            assert execute_result.success, (
                f"DDL execution failed: {execute_result.error}"
            )

            # Verify table exists
            tables_result = connected_oracle_api.get_tables()
            assert tables_result.success
            table_names = [str(t).upper() for t in tables_result.data]
            assert table_name.upper() in table_names

            # Get table metadata
            metadata_result = connected_oracle_api.get_table_metadata(table_name)
            assert metadata_result.success, (
                f"Get metadata failed: {metadata_result.error}"
            )

            metadata = metadata_result.data
            assert metadata["table_name"].upper() == table_name.upper()
            assert len(metadata["columns"]) == 3

        finally:
            # Cleanup - drop table
            with contextlib.suppress(Exception):
                drop_ddl = connected_oracle_api.drop_table_ddl(table_name)
                if drop_ddl.success:
                    connected_oracle_api.execute_ddl(drop_ddl.data)


class TestRealOracleErrorHandling:
    """Test real Oracle error handling scenarios."""

    def test_real_connection_invalid_credentials(self) -> None:
        """Test connection with invalid credentials."""
        invalid_config = FlextDbOracleConfig(
            host="localhost",
            port=1521,
            service_name="XEPDB1",
            username="invalid_user",
            password="invalid_password",
        )

        connection = FlextDbOracleConnection(invalid_config)
        result = connection.connect()
        assert result.is_failure
        assert (
            "invalid username/password" in result.error.lower()
            or "authentication" in result.error.lower()
            or "login" in result.error.lower()
        )

    def test_real_connection_invalid_sql(
        self,
        real_oracle_config: FlextDbOracleConfig,
    ) -> None:
        """Test execution with invalid SQL."""
        connection = FlextDbOracleConnection(real_oracle_config)

        connect_result = connection.connect()
        assert connect_result.success

        try:
            # Execute invalid SQL
            result = connection.execute("SELECT FROM INVALID_TABLE_THAT_DOES_NOT_EXIST")
            assert result.is_failure
            assert (
                "table" in result.error.lower() or "not exist" in result.error.lower()
            )

        finally:
            connection.disconnect()

    def test_real_api_not_connected_operations(
        self,
        real_oracle_config: FlextDbOracleConfig,
    ) -> None:
        """Test API operations when not connected."""
        api = FlextDbOracleApi(real_oracle_config)
        # Don't connect

        # These should fail gracefully
        result = api.query("SELECT 1 FROM DUAL")
        assert result.is_failure
        assert "not connected" in result.error.lower()

        result = api.get_tables()
        assert result.is_failure
        assert (
            "not connected" in result.error.lower()
            or "connection" in result.error.lower()
        )
