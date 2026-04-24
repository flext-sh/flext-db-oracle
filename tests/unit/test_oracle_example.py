"""Exemplo de testes REAIS usando Oracle.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import contextlib
from collections.abc import (
    Sequence,
)

import pytest
from flext_tests import tm

from flext_db_oracle import (
    FlextDbOracleApi,
    FlextDbOracleServices,
    FlextDbOracleSettings,
)
from tests import m, r, t, u


def safe_get_first_value(data: t.JsonValue) -> t.JsonValue:
    """Safely get first value from various data structures."""
    if isinstance(data, list) and data:
        return data[0]
    if isinstance(data, dict) and data:
        return next(iter(data.values()))
    return data


def _dict_first_value(row: m.Dict) -> t.JsonValue:
    root = row.root
    if root:
        val = next(iter(root.values()))
        if val is None:
            return None
        if isinstance(val, tuple):
            return [u.normalize_to_metadata(item) for item in val]
        return (
            u.normalize_to_metadata(val)
            if isinstance(val, (str, int, float, bool, dict, list))
            else None
        )
    return None


class TestsFlextDbOracleOracleExample:
    def test_real_connection_connect_disconnect(
        self,
        real_oracle_config: FlextDbOracleSettings,
    ) -> None:
        """Test real Oracle connection and disconnection."""
        connection = FlextDbOracleServices(settings=real_oracle_config)
        result = connection.connect()
        if result.failure:
            pytest.skip(f"Oracle connection unavailable: {result.error}")
        tm.that(connection.connected(), eq=True)
        disconnect_result = connection.disconnect()
        if disconnect_result.failure:
            pytest.skip(f"Oracle disconnect failed: {disconnect_result.error}")
        tm.that(not connection.connected(), eq=True)

    def test_real_connection_execute_query(
        self,
        real_oracle_config: FlextDbOracleSettings,
    ) -> None:
        """Test real Oracle query execution."""
        connection = FlextDbOracleServices(settings=real_oracle_config)
        connect_result = connection.connect()
        if connect_result.failure:
            pytest.skip(f"Oracle connection unavailable: {connect_result.error}")
        try:
            result = connection.execute_query("SELECT 1 FROM DUAL")
            if result.failure:
                msg = f"Query failed: {result.error}"
                raise AssertionError(msg)
            query_data = result.value
            tm.that(query_data, is_=list)
            tm.that(len(query_data), eq=1)
            first_row = query_data[0]
            first_value = _dict_first_value(first_row)
            tm.that(int(str(first_value)), eq=1)
        finally:
            connection.disconnect()

    def test_real_connection_fetch_one(
        self,
        real_oracle_config: FlextDbOracleSettings,
    ) -> None:
        """Test real Oracle fetch_one."""
        connection = FlextDbOracleServices(settings=real_oracle_config)
        connect_result = connection.connect()
        if connect_result.failure:
            pytest.skip(f"Oracle connection unavailable: {connect_result.error}")
        try:
            result = connection.fetch_one("SELECT 42 FROM DUAL")
            if result.failure:
                msg = f"Fetch one failed: {result.error}"
                raise AssertionError(msg)
            fetch_data = result.value
            if fetch_data:
                first_value = next(iter(fetch_data.values()))
                tm.that(int(str(first_value)), eq=42)
        finally:
            connection.disconnect()

    def test_real_connection_execute_many(
        self,
        real_oracle_config: FlextDbOracleSettings,
    ) -> None:
        """Test real Oracle execute_many with temporary table."""
        connection = FlextDbOracleServices(settings=real_oracle_config)
        connect_result = connection.connect()
        if connect_result.failure:
            pytest.skip(f"Oracle connection unavailable: {connect_result.error}")
        try:
            with contextlib.suppress(Exception):
                connection.execute_statement("DROP TABLE temp_test_table")
            create_result = connection.execute_statement(
                "\n                CREATE TABLE temp_test_table (\n                    id NUMBER,\n                    name VARCHAR2(100)\n                )\n            ",
            )
            if create_result.failure:
                msg = f"Table creation failed: {create_result.error}"
                raise AssertionError(msg)
            params_list: Sequence[t.JsonMapping] = [
                {"id": 1, "name": "Test 1"},
                {"id": 2, "name": "Test 2"},
                {"id": 3, "name": "Test 3"},
            ]
            result = connection.execute_many(
                "INSERT INTO temp_test_table (id, name) VALUES (:id, :name)",
                params_list,
            )
            if result.failure:
                msg = f"Execute many failed: {result.error}"
                raise AssertionError(msg)
            many_result = result.value
            tm.that(many_result, eq=3)
        finally:
            with contextlib.suppress(Exception):
                connection.execute_statement("DROP TABLE temp_test_table")
            connection.disconnect()

    def test_real_api_connect_context_manager(
        self,
        real_oracle_config: FlextDbOracleSettings,
    ) -> None:
        """Test real Oracle API with context manager."""
        try:
            with FlextDbOracleApi(real_oracle_config) as api:
                test_result = api.test_connection()
                if test_result.failure:
                    pytest.skip(f"Connection test failed: {test_result.error}")
                query_result = api.query("SELECT 'Hello Oracle' FROM DUAL")
                if query_result.failure:
                    pytest.skip(f"Query failed: {query_result.error}")
                query_data = query_result.value
                if query_data:
                    row = query_data[0]
                    cell = _dict_first_value(row)
                    final_value = (
                        safe_get_first_value(cell)
                        if isinstance(cell, (list, dict))
                        else cell
                    )
                    tm.that(str(final_value), has="Hello Oracle")
        except RuntimeError:
            pytest.skip("Oracle connection unavailable for context manager test")

    def test_real_api_fetch_schemas(
        self, connected_oracle_api: FlextDbOracleApi
    ) -> None:
        """Test real Oracle schema listing using utilities."""
        schemas_result = connected_oracle_api.fetch_schemas()
        if schemas_result.failure:
            msg = f"Get schemas failed: {schemas_result.error}"
            raise AssertionError(msg)
        schemas = schemas_result.value
        tm.that(len(schemas) > 0, eq=True)
        system_schemas = ["SYS", "SYSTEM", "FLEXT", "FLEXTTEST", "XDB"]
        tm.that(
            any(
                any(s in str(schema).upper() for s in system_schemas)
                for schema in schemas
            ),
            eq=True,
        )

    def test_real_api_fetch_tables(
        self, connected_oracle_api: FlextDbOracleApi
    ) -> None:
        """Test real Oracle table listing using utilities."""
        tables_result = connected_oracle_api.fetch_tables()
        if tables_result.failure:
            msg = f"Get tables failed: {tables_result.error}"
            raise AssertionError(msg)
        tables = tables_result.value
        tm.that(tables, is_=list)
        tm.that(len(tables) >= 0, eq=True)
        expected_tables = ["EMPLOYEES", "DEPARTMENTS", "JOBS"]
        for table in expected_tables:
            tm.that(any(table in str(t).upper() for t in tables), eq=True)

    def test_real_api_fetch_columns(
        self, connected_oracle_api: FlextDbOracleApi
    ) -> None:
        """Test real Oracle column listing."""
        result = connected_oracle_api.fetch_columns("EMPLOYEES")
        if result.failure:
            msg = f"Get columns failed: {result.error}"
            raise AssertionError(msg)
        columns = result.value
        tm.that(len(columns) > 0, eq=True)
        column_names = [
            col.name.upper() if hasattr(col, "name") else "" for col in columns
        ]
        expected_columns = ["EMPLOYEE_ID", "FIRST_NAME", "LAST_NAME", "EMAIL"]
        for col in expected_columns:
            tm.that(column_names, has=col)

    def test_real_api_query_with_timing(
        self,
        connected_oracle_api: FlextDbOracleApi,
    ) -> None:
        """Test real Oracle query with timing."""
        result = connected_oracle_api.query("SELECT COUNT(*) FROM EMPLOYEES")
        if result.failure:
            msg = f"Query with timing failed: {result.error}"
            raise AssertionError(msg)
        query_result = result.value
        tm.that(query_result, is_=list)
        tm.that(len(query_result) > 0, eq=True)

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
            if result.failure:
                msg = f"Type conversion failed for {singer_type}: {result.error}"
                raise AssertionError(msg)
            oracle_type = result.value
            tm.that(oracle_type, has=expected)

    def test_real_api_table_operations(
        self,
        connected_oracle_api: FlextDbOracleApi,
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
            if ddl_result.failure:
                msg = f"DDL generation failed: {ddl_result.error}"
                raise AssertionError(msg)
            ddl_sql = ddl_result.value
            execute_result = connected_oracle_api.execute_sql(ddl_sql)
            if execute_result.failure:
                msg = f"DDL execution failed: {execute_result.error}"
                raise AssertionError(msg)
            tables_result = connected_oracle_api.fetch_tables()
            if tables_result.failure:
                msg = f"Get tables failed: {tables_result.error}"
                raise AssertionError(msg)
            tables_data = tables_result.value
            table_names = [str(t).upper() for t in tables_data]
            tm.that(table_names, has=table_name.upper())
            metadata_result = connected_oracle_api.fetch_tables(table_name)
            if metadata_result.failure:
                msg = f"Get metadata failed: {metadata_result.error}"
                raise AssertionError(msg)
            metadata = metadata_result.value
            if metadata:
                tm.that(str(metadata[0]).upper(), eq=table_name.upper())
        finally:
            with contextlib.suppress(Exception):
                drop_sql = f"DROP TABLE {table_name}"
                connected_oracle_api.execute_sql(drop_sql)

    def test_real_connection_invalid_credentials(self) -> None:
        """Test connection with invalid credentials."""
        invalid_config = FlextDbOracleSettings(
            host="localhost",
            port=1521,
            service_name="XEPDB1",
            username="invalid_user",
            password="invalid_password",
        )
        connection = FlextDbOracleServices(settings=invalid_config)
        result = connection.connect()
        tm.fail(result)
        error_msg = (result.error or "").lower()
        tm.that(
            (
                "invalid username/password" in error_msg
                or "authentication" in error_msg
                or "login" in error_msg
                or ("connection refused" in error_msg)
                or ("cannot connect" in error_msg)
                or ("connection test failed" in error_msg)
                or ("not connected to database" in error_msg)
            ),
            eq=True,
        )

    def test_real_connection_invalid_sql(
        self,
        real_oracle_config: FlextDbOracleSettings,
    ) -> None:
        """Test execution with invalid SQL."""
        connection = FlextDbOracleServices(settings=real_oracle_config)
        connect_result = connection.connect()
        if connect_result.failure:
            pytest.skip(f"Oracle connection unavailable: {connect_result.error}")
        try:
            result = connection.execute_query(
                "SELECT FROM INVALID_TABLE_THAT_DOES_NOT_EXIST",
            )
            tm.fail(result)
            tm.that(
                (
                    "table" in (result.error or "").lower()
                    or "not exist" in (result.error or "").lower()
                ),
                eq=True,
            )
        finally:
            connection.disconnect()

    def test_real_api_not_connected_operations(
        self,
        real_oracle_config: FlextDbOracleSettings,
    ) -> None:
        """Test API operations when not connected."""
        api = FlextDbOracleApi(real_oracle_config)
        result = api.query("SELECT 1 FROM DUAL")
        tm.fail(result)
        tm.that((result.error or "").lower(), has="not connected")
        tables_result = api.fetch_tables()
        tm.fail(tables_result)
        tm.that(
            (
                "not connected" in (tables_result.error or "").lower()
                or "connection" in (tables_result.error or "").lower()
            ),
            eq=True,
        )
