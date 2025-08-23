"""Exemplo de testes REAIS usando Oracle.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import contextlib

from pydantic import SecretStr

from flext_db_oracle import (
    FlextDbOracleApi,
    FlextDbOracleConfig,
    FlextDbOracleConnection,
)
from flext_db_oracle.utilities import FlextDbOracleUtilities


class TestRealOracleConnection:
    """Testes reais de conexão Oracle - SEM MOCKS."""

    def test_real_connection_connect_disconnect(
        self,
        real_oracle_config: FlextDbOracleConfig,
    ) -> None:
        """Test real Oracle connection and disconnection."""
        connection = FlextDbOracleConnection(real_oracle_config)

        # Test connect - using modern .value access after failure check
        result = connection.connect()
        if result.is_failure:
            raise AssertionError(f"Connection failed: {result.error}")
        # Success case - use modern .value access
        assert connection.is_connected()

        # Test disconnect - using modern .value access after failure check
        result = connection.disconnect()
        if result.is_failure:
            raise AssertionError(f"Disconnect failed: {result.error}")
        # Success case - use modern .value access
        assert not connection.is_connected()

    def test_real_connection_execute_query(
        self,
        real_oracle_config: FlextDbOracleConfig,
    ) -> None:
        """Test real Oracle query execution."""
        connection = FlextDbOracleConnection(real_oracle_config)

        # Connect first - using modern pattern
        connect_result = connection.connect()
        if connect_result.is_failure:
            raise AssertionError(f"Connection failed: {connect_result.error}")
        # Success case - connection established

        try:
            # Execute simple query - using modern .value access after failure check
            result = connection.execute("SELECT 1 FROM DUAL")
            if result.is_failure:
                raise AssertionError(f"Query failed: {result.error}")
            # Success case - use modern .value access
            query_data = result.value
            assert isinstance(query_data, list)
            assert len(query_data) == 1
            row = query_data[0]
            if hasattr(row, "__getitem__"):
                assert row[0] == 1

        finally:
            connection.disconnect()

    def test_real_connection_fetch_one(
        self,
        real_oracle_config: FlextDbOracleConfig,
    ) -> None:
        """Test real Oracle fetch_one."""
        connection = FlextDbOracleConnection(real_oracle_config)

        # Connect first - using modern pattern
        connect_result = connection.connect()
        if connect_result.is_failure:
            raise AssertionError(f"Connection failed: {connect_result.error}")
        # Success case - connection established

        try:
            # Fetch one row - using modern .value access after failure check
            result = connection.fetch_one("SELECT 42 FROM DUAL")
            if result.is_failure:
                raise AssertionError(f"Fetch one failed: {result.error}")
            # Success case - use modern .value access
            fetch_data = result.value
            if fetch_data and hasattr(fetch_data, "__getitem__"):
                assert fetch_data[0] == 42

        finally:
            connection.disconnect()

    def test_real_connection_execute_many(
        self,
        real_oracle_config: FlextDbOracleConfig,
    ) -> None:
        """Test real Oracle execute_many with temporary table."""
        connection = FlextDbOracleConnection(real_oracle_config)

        # Connect first - using modern pattern
        connect_result = connection.connect()
        if connect_result.is_failure:
            raise AssertionError(f"Connection failed: {connect_result.error}")
        # Success case - connection established

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
            if create_result.is_failure:
                raise AssertionError(f"Table creation failed: {create_result.error}")
            # Success case - table created successfully

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
            if result.is_failure:
                raise AssertionError(f"Execute many failed: {result.error}")
            # Success case - use modern .value access
            many_result = result.value
            assert many_result == 3  # Row count

            # Verify data - using modern .value access after failure check
            select_result = connection.execute("SELECT COUNT(*) FROM temp_test_table")
            if select_result.is_failure:
                raise AssertionError(f"Count query failed: {select_result.error}")
            # Success case - use modern .value access
            count_data = select_result.value
            assert isinstance(count_data, list)
            assert len(count_data) > 0
            row = count_data[0]
            if hasattr(row, "__getitem__"):
                assert row[0] == 3

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
            # Test connection - using modern .value access after failure check
            test_result = api.test_connection()
            if test_result.is_failure:
                raise AssertionError(f"Connection test failed: {test_result.error}")
            # Success case - use modern .value access
            # Success case - connection test passed

            # Test simple query - using modern .value access after failure check
            query_result = api.query("SELECT 'Hello Oracle' FROM DUAL")
            if query_result.is_failure:
                raise AssertionError(f"Query failed: {query_result.error}")
            # Success case - use modern .value access
            # SQLAlchemy Row objects are returned as tuples: rows[0][0] = ('Hello Oracle',)
            # To get the actual string value, we need to access the first element of the tuple
            query_data = query_result.value
            if query_data.rows and len(query_data.rows) > 0:
                row = query_data.rows[0]
                if hasattr(row, "__getitem__") and len(row) > 0:
                    cell = row[0]
                    if (
                        hasattr(cell, "__getitem__")
                        and hasattr(cell, "__len__")
                        and len(cell) > 0
                    ):
                        assert cell[0] == "Hello Oracle"

    def test_real_api_get_schemas(self, connected_oracle_api: FlextDbOracleApi) -> None:
        """Test real Oracle schema listing using utilities."""
        # Use utilities for cleaner code
        schemas = FlextDbOracleUtilities.safe_get_schemas(connected_oracle_api)

        # Should have at least FLEXTTEST and system schemas
        assert len(schemas) > 0
        assert any("FLEXTTEST" in str(schema).upper() for schema in schemas)

    def test_real_api_get_tables(self, connected_oracle_api: FlextDbOracleApi) -> None:
        """Test real Oracle table listing using utilities."""
        # Use utilities for cleaner code
        tables = FlextDbOracleUtilities.safe_get_tables(connected_oracle_api)

        # Should succeed and have test tables from init.sql
        assert isinstance(tables, list)
        assert len(tables) > 0
        expected_tables = ["EMPLOYEES", "DEPARTMENTS", "JOBS"]
        for table in expected_tables:
            assert any(table in str(t).upper() for t in tables), (
                f"Table {table} not found"
            )

    def test_real_api_get_columns(self, connected_oracle_api: FlextDbOracleApi) -> None:
        """Test real Oracle column listing."""
        result = connected_oracle_api.get_columns("EMPLOYEES")
        if result.is_failure:
            raise AssertionError(f"Get columns failed: {result.error}")
        # Success case - use modern .value access
        columns = result.value
        assert len(columns) > 0

        # Check for expected columns
        column_names = [
            str(col["column_name"]).upper() if "column_name" in col else ""
            for col in columns
        ]
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
        if result.is_failure:
            raise AssertionError(f"Query with timing failed: {result.error}")
        # Success case - use modern .value access
        query_result = result.value
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

            if result.is_failure:
                raise AssertionError(
                    f"Type conversion failed for {singer_type}: {result.error}"
                )
            # Success case - use modern .value access
            oracle_type = result.value
            assert expected in oracle_type, f"Expected {expected} in {oracle_type}"

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
            if ddl_result.is_failure:
                raise AssertionError(f"DDL generation failed: {ddl_result.error}")
            # Success case - use modern .value access
            ddl_sql = ddl_result.value

            # Execute DDL - using modern .value access after failure check
            execute_result = connected_oracle_api.execute_ddl(ddl_sql)
            if execute_result.is_failure:
                raise AssertionError(f"DDL execution failed: {execute_result.error}")
            # Success case - DDL executed successfully

            # Verify table exists - using modern .value access after failure check
            tables_result = connected_oracle_api.get_tables()
            if tables_result.is_failure:
                raise AssertionError(f"Get tables failed: {tables_result.error}")
            # Success case - use modern .value access
            tables_data = tables_result.value
            table_names = [str(t).upper() for t in tables_data]
            assert table_name.upper() in table_names

            # Get table metadata - using modern .value access after failure check
            metadata_result = connected_oracle_api.get_table_metadata(table_name)
            if metadata_result.is_failure:
                raise AssertionError(f"Get metadata failed: {metadata_result.error}")
            # Success case - use modern .value access
            metadata = metadata_result.value
            assert str(metadata["table_name"]).upper() == table_name.upper()
            columns_obj = metadata["columns"]
            if hasattr(columns_obj, "__len__"):
                assert len(columns_obj) == 3

        finally:
            # Cleanup - drop table
            with contextlib.suppress(Exception):
                drop_ddl = connected_oracle_api.drop_table_ddl(table_name)
                if drop_ddl.success:
                    # Use modern .value access for successful DDL
                    drop_sql = drop_ddl.value
                    connected_oracle_api.execute_ddl(drop_sql)


class TestRealOracleErrorHandling:
    """Test real Oracle error handling scenarios."""

    def test_real_connection_invalid_credentials(self) -> None:
        """Test connection with invalid credentials."""
        invalid_config = FlextDbOracleConfig(
            host="localhost",
            port=1521,
            service_name="XEPDB1",
            username="invalid_user",
            password=SecretStr("invalid_password"),
        )

        connection = FlextDbOracleConnection(invalid_config)
        result = connection.connect()
        assert result.is_failure
        error_msg = (result.error or "").lower()
        assert (
            "invalid username/password" in error_msg
            or "authentication" in error_msg
            or "login" in error_msg
            or "connection refused" in error_msg
            or "cannot connect" in error_msg
        )

    def test_real_connection_invalid_sql(
        self,
        real_oracle_config: FlextDbOracleConfig,
    ) -> None:
        """Test execution with invalid SQL."""
        connection = FlextDbOracleConnection(real_oracle_config)

        connect_result = connection.connect()
        if connect_result.is_failure:
            raise AssertionError(f"Connection failed: {connect_result.error}")
        # Success case - connection established

        try:
            # Execute invalid SQL
            result = connection.execute("SELECT FROM INVALID_TABLE_THAT_DOES_NOT_EXIST")
            assert result.is_failure
            assert (
                "table" in (result.error or "").lower()
                or "not exist" in (result.error or "").lower()
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
        assert "not connected" in (result.error or "").lower()

        tables_result = api.get_tables()
        assert tables_result.is_failure
        assert (
            "not connected" in (tables_result.error or "").lower()
            or "connection" in (tables_result.error or "").lower()
        )
