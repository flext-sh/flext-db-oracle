"""Exemplo de testes REAIS usando Oracle.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import contextlib

from flext_core import r

from flext_db_oracle import (
    FlextDbOracleApi,
    FlextDbOracleServices,
    FlextDbOracleSettings,
    t,
)


def safe_get_first_value(data: object) -> object:
    """Safely get first value from various data structures."""
    if hasattr(data, "root"):
        data = data.root
    if isinstance(data, (tuple, list)) and len(data) > 0:
        return data[0]
    if isinstance(data, dict) and data:
        return next(iter(data.values()))
    return data


class TestRealOracleConnection:
    """Testes reais de conexão Oracle - SEM MOCKS."""

    def test_real_connection_connect_disconnect(
        self, real_oracle_config: FlextDbOracleSettings
    ) -> None:
        """Test real Oracle connection and disconnection."""
        connection = FlextDbOracleServices(config=real_oracle_config)
        result = connection.connect()
        if result.is_failure:
            msg = f"Connection failed: {result.error}"
            raise AssertionError(msg)
        assert connection.is_connected()
        disconnect_result = connection.disconnect()
        if disconnect_result.is_failure:
            msg = f"Disconnect failed: {disconnect_result.error}"
            raise AssertionError(msg)
        assert not connection.is_connected()

    def test_real_connection_execute_query(
        self, real_oracle_config: FlextDbOracleSettings
    ) -> None:
        """Test real Oracle query execution."""
        connection = FlextDbOracleServices(config=real_oracle_config)
        connect_result = connection.connect()
        if connect_result.is_failure:
            msg = f"Connection failed: {connect_result.error}"
            raise AssertionError(msg)
        try:
            result = connection.execute_query("SELECT 1 FROM DUAL")
            if result.is_failure:
                msg = f"Query failed: {result.error}"
                raise AssertionError(msg)
            query_data = result.value
            assert isinstance(query_data, list)
            assert len(query_data) == 1
            first_row = safe_get_first_value(query_data)
            first_value = safe_get_first_value(first_row)
            assert first_value == 1
        finally:
            connection.disconnect()

    def test_real_connection_fetch_one(
        self, real_oracle_config: FlextDbOracleSettings
    ) -> None:
        """Test real Oracle fetch_one."""
        connection = FlextDbOracleServices(config=real_oracle_config)
        connect_result = connection.connect()
        if connect_result.is_failure:
            msg = f"Connection failed: {connect_result.error}"
            raise AssertionError(msg)
        try:
            result = connection.fetch_one("SELECT 42 FROM DUAL")
            if result.is_failure:
                msg = f"Fetch one failed: {result.error}"
                raise AssertionError(msg)
            fetch_data = result.value
            if fetch_data:
                assert hasattr(fetch_data, "__getitem__"), (
                    f"Expected dict-like, got {type(fetch_data)}"
                )
                first_value = next(iter(fetch_data.values()))
                assert first_value == 42
        finally:
            connection.disconnect()

    def test_real_connection_execute_many(
        self, real_oracle_config: FlextDbOracleSettings
    ) -> None:
        """Test real Oracle execute_many with temporary table."""
        connection = FlextDbOracleServices(config=real_oracle_config)
        connect_result = connection.connect()
        if connect_result.is_failure:
            msg = f"Connection failed: {connect_result.error}"
            raise AssertionError(msg)
        try:
            with contextlib.suppress(Exception):
                connection.execute_statement("DROP TABLE temp_test_table")
            create_result = connection.execute_statement(
                "\n                CREATE TABLE temp_test_table (\n                    id NUMBER,\n                    name VARCHAR2(100)\n                )\n            "
            )
            if create_result.is_failure:
                msg = f"Table creation failed: {create_result.error}"
                raise AssertionError(msg)
            params_list: list[dict[str, t.ContainerValue]] = [
                {"id": 1, "name": "Test 1"},
                {"id": 2, "name": "Test 2"},
                {"id": 3, "name": "Test 3"},
            ]
            result = connection.execute_many(
                "INSERT INTO temp_test_table (id, name) VALUES (:id, :name)",
                params_list,
            )
            if result.is_failure:
                msg = f"Execute many failed: {result.error}"
                raise AssertionError(msg)
            many_result = result.value
            assert many_result == 3
        finally:
            with contextlib.suppress(Exception):
                connection.execute_statement("DROP TABLE temp_test_table")
            connection.disconnect()


class TestRealOracleApi:
    """Testes reais da API Oracle - SEM MOCKS."""

    def test_real_api_connect_context_manager(
        self, real_oracle_config: FlextDbOracleSettings
    ) -> None:
        """Test real Oracle API with context manager."""
        with FlextDbOracleApi(real_oracle_config) as api:
            test_result = api.test_connection()
            if test_result.is_failure:
                msg = f"Connection test failed: {test_result.error}"
                raise AssertionError(msg)
            query_result = api.query("SELECT 'Hello Oracle' FROM DUAL")
            if query_result.is_failure:
                msg = f"Query failed: {query_result.error}"
                raise AssertionError(msg)
            query_data = query_result.value
            if len(query_data) > 0:
                row = query_data[0]
                if (
                    hasattr(row, "__getitem__")
                    and hasattr(row, "__len__")
                    and (len(row) > 0)
                ):
                    cell = safe_get_first_value(row)
                    final_value = (
                        safe_get_first_value(cell) if hasattr(cell, "__len__") else cell
                    )
                    assert "Hello Oracle" in str(final_value)

    def test_real_api_get_schemas(self, connected_oracle_api: FlextDbOracleApi) -> None:
        """Test real Oracle schema listing using utilities."""
        schemas_result = connected_oracle_api.get_schemas()
        if schemas_result.is_failure:
            msg = f"Get schemas failed: {schemas_result.error}"
            raise AssertionError(msg)
        schemas = schemas_result.value
        assert len(schemas) > 0
        system_schemas = ["SYS", "SYSTEM", "FLEXT", "FLEXTTEST", "XDB"]
        assert any(
            any(s in str(schema).upper() for s in system_schemas) for schema in schemas
        ), f"No expected schemas found in {schemas}"

    def test_real_api_get_tables(self, connected_oracle_api: FlextDbOracleApi) -> None:
        """Test real Oracle table listing using utilities."""
        tables_result = connected_oracle_api.get_tables()
        if tables_result.is_failure:
            msg = f"Get tables failed: {tables_result.error}"
            raise AssertionError(msg)
        tables = tables_result.value
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
            msg = f"Get columns failed: {result.error}"
            raise AssertionError(msg)
        columns = result.value
        assert len(columns) > 0
        column_names = [
            str(col["column_name"]).upper() if "column_name" in col else ""
            for col in columns
        ]
        expected_columns = ["EMPLOYEE_ID", "FIRST_NAME", "LAST_NAME", "EMAIL"]
        for col in expected_columns:
            assert col in column_names, f"Column {col} not found"

    def test_real_api_query_with_timing(
        self, connected_oracle_api: FlextDbOracleApi
    ) -> None:
        """Test real Oracle query with timing."""
        result = connected_oracle_api.query("SELECT COUNT(*) FROM EMPLOYEES")
        if result.is_failure:
            msg = f"Query with timing failed: {result.error}"
            raise AssertionError(msg)
        query_result = result.value
        assert isinstance(query_result, list), (
            f"Expected list, got {type(query_result)}"
        )
        assert len(query_result) > 0, "Expected at least one row in result"

    def test_real_api_singer_type_conversion(
        self, connected_oracle_api: FlextDbOracleApi
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
                    singer_type, format_hint
                )
            if result.is_failure:
                msg = f"Type conversion failed for {singer_type}: {result.error}"
                raise AssertionError(msg)
            oracle_type = result.value
            assert expected in oracle_type, f"Expected {expected} in {oracle_type}"

    def test_real_api_table_operations(
        self, connected_oracle_api: FlextDbOracleApi
    ) -> None:
        """Test real Oracle table operations."""
        table_name = "TEST_TEMP_TABLE"
        try:
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
            ddl_parts = [f"CREATE TABLE {table_name} ("]
            column_parts: list[str] = []
            for col in columns:
                col_def = f"{col['name']} {col['type']}"
                if not col.get("nullable", True):
                    col_def += " NOT NULL"
                if "default_value" in col:
                    col_def += f" DEFAULT {col['default_value']}"
                column_parts.append(col_def)
            ddl_parts.extend((", ".join(column_parts), ")"))
            ddl_sql = " ".join(ddl_parts)
            ddl_result = r[str].ok(ddl_sql)
            if ddl_result.is_failure:
                msg = f"DDL generation failed: {ddl_result.error}"
                raise AssertionError(msg)
            ddl_sql = ddl_result.value
            execute_result = connected_oracle_api.execute_sql(ddl_sql)
            if execute_result.is_failure:
                msg = f"DDL execution failed: {execute_result.error}"
                raise AssertionError(msg)
            tables_result = connected_oracle_api.get_tables()
            if tables_result.is_failure:
                msg = f"Get tables failed: {tables_result.error}"
                raise AssertionError(msg)
            tables_data = tables_result.value
            table_names = [str(t).upper() for t in tables_data]
            assert table_name.upper() in table_names
            metadata_result = connected_oracle_api.get_tables(table_name)
            if metadata_result.is_failure:
                msg = f"Get metadata failed: {metadata_result.error}"
                raise AssertionError(msg)
            metadata = metadata_result.value
            if len(metadata) > 0:
                assert str(metadata[0]).upper() == table_name.upper()
        finally:
            with contextlib.suppress(Exception):
                drop_sql = f"DROP TABLE {table_name}"
                connected_oracle_api.execute_sql(drop_sql)


class TestRealOracleErrorHandling:
    """Test real Oracle error handling scenarios."""

    def test_real_connection_invalid_credentials(self) -> None:
        """Test connection with invalid credentials."""
        invalid_config = FlextDbOracleSettings(
            host="localhost",
            port=1521,
            service_name="XEPDB1",
            username="invalid_user",
            password="invalid_password",
        )
        connection = FlextDbOracleServices(config=invalid_config)
        result = connection.connect()
        assert result.is_failure
        error_msg = (result.error or "").lower()
        assert (
            "invalid username/password" in error_msg
            or "authentication" in error_msg
            or "login" in error_msg
            or ("connection refused" in error_msg)
            or ("cannot connect" in error_msg)
            or ("connection test failed" in error_msg)
            or ("not connected to database" in error_msg)
        )

    def test_real_connection_invalid_sql(
        self, real_oracle_config: FlextDbOracleSettings
    ) -> None:
        """Test execution with invalid SQL."""
        connection = FlextDbOracleServices(config=real_oracle_config)
        connect_result = connection.connect()
        if connect_result.is_failure:
            msg = f"Connection failed: {connect_result.error}"
            raise AssertionError(msg)
        try:
            result = connection.execute_query(
                "SELECT FROM INVALID_TABLE_THAT_DOES_NOT_EXIST"
            )
            assert result.is_failure
            assert (
                "table" in (result.error or "").lower()
                or "not exist" in (result.error or "").lower()
            )
        finally:
            connection.disconnect()

    def test_real_api_not_connected_operations(
        self, real_oracle_config: FlextDbOracleSettings
    ) -> None:
        """Test API operations when not connected."""
        api = FlextDbOracleApi(real_oracle_config)
        result = api.query("SELECT 1 FROM DUAL")
        assert result.is_failure
        assert "not connected" in (result.error or "").lower()
        tables_result = api.get_tables()
        assert tables_result.is_failure
        assert (
            "not connected" in (tables_result.error or "").lower()
            or "connection" in (tables_result.error or "").lower()
        )
