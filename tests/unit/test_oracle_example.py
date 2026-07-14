"""Behavioral tests for the real Oracle API and services facade.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

These tests exercise the public contract of :class:`FlextDbOracleApi` and
:class:`FlextDbOracleServices`. Integration paths that require a live Oracle
instance fail loudly when the shared test database is unreachable; the
connection-error and not-connected paths are exercised without a server.

"""

from __future__ import annotations

import contextlib

import pytest
from flext_tests import tm

from flext_db_oracle import FlextDbOracleSettings
from flext_db_oracle.api import FlextDbOracleApi
from flext_db_oracle.services.facade import FlextDbOracleServices
from tests import m, t, u


class TestsFlextDbOracleOracleExample:
    """Public-contract behavior for the Oracle API and services facade."""

    @staticmethod
    def _first_cell(row: m.Dict) -> t.JsonValue:
        """Return the first cell of a query row via its public ``root`` mapping."""
        root = row.root
        if not root:
            return None
        val = next(iter(root.values()))
        if val is None:
            return None
        if isinstance(val, tuple):
            return [u.normalize_to_metadata(item) for item in val]
        if isinstance(val, (str, int, float, bool, dict, list)):
            return u.normalize_to_metadata(val)
        return None

    @classmethod
    def _api_context_first_cell(
        cls,
        real_oracle_config: FlextDbOracleSettings,
    ) -> t.JsonValue:
        """Query a scalar value through the public API context manager."""
        with FlextDbOracleApi(real_oracle_config) as api:
            connection_result = api.test_connection()
            tm.ok(connection_result)
            query_result = api.query("SELECT 'Hello Oracle' FROM DUAL")
            tm.ok(query_result)
            return cls._first_cell(query_result.value[0])

    @staticmethod
    def _connect_services(
        real_oracle_config: FlextDbOracleSettings,
    ) -> FlextDbOracleServices:
        """Connect the services facade or fail the real-Oracle contract."""
        connection = FlextDbOracleServices(settings=real_oracle_config)
        connect_result = connection.connect()
        tm.ok(connect_result)
        tm.that(connection.connected(), eq=True)
        return connection

    # ------------------------------------------------------------------
    # Services facade: connection lifecycle
    # ------------------------------------------------------------------

    def test_connect_reports_connected_then_disconnect_clears_it(
        self,
        real_oracle_config: FlextDbOracleSettings,
    ) -> None:
        """After a successful connect ``connected()`` is True, False after disconnect."""
        connection = self._connect_services(real_oracle_config)

        tm.that(connection.connected(), eq=True)

        disconnect_result = connection.disconnect()
        tm.ok(disconnect_result)
        tm.that(connection.connected(), eq=False)

    def test_execute_query_returns_single_row_result(
        self,
        real_oracle_config: FlextDbOracleSettings,
    ) -> None:
        """``execute_query`` succeeds and yields exactly one row for ``SELECT 1``."""
        connection = self._connect_services(real_oracle_config)
        try:
            result = connection.execute_query("SELECT 1 FROM DUAL")
            tm.ok(result)
            query_data = result.value
            tm.that(len(query_data), eq=1)
            tm.that(int(str(self._first_cell(query_data[0]))), eq=1)
        finally:
            connection.disconnect()

    def test_fetch_one_returns_scalar_mapping(
        self,
        real_oracle_config: FlextDbOracleSettings,
    ) -> None:
        """``fetch_one`` succeeds and the returned mapping carries the scalar value."""
        connection = self._connect_services(real_oracle_config)
        try:
            result = connection.fetch_one("SELECT 42 FROM DUAL")
            tm.ok(result)
            fetch_data = result.value
            if fetch_data is None:
                msg = "fetch_one returned success with no row"
                raise AssertionError(msg)
            first_value = next(iter(fetch_data.values()))
            tm.that(int(str(first_value)), eq=42)
        finally:
            connection.disconnect()

    def test_execute_many_returns_affected_row_count(
        self,
        real_oracle_config: FlextDbOracleSettings,
    ) -> None:
        """``execute_many`` reports the number of rows inserted."""
        connection = self._connect_services(real_oracle_config)
        try:
            with contextlib.suppress(Exception):
                connection.execute_statement("DROP TABLE temp_test_table")
            create_result = connection.execute_statement(
                "CREATE TABLE temp_test_table (id NUMBER, name VARCHAR2(100))",
            )
            tm.ok(create_result)
            params_list: t.SequenceOf[t.JsonMapping] = [
                {"id": 1, "name": "Test 1"},
                {"id": 2, "name": "Test 2"},
                {"id": 3, "name": "Test 3"},
            ]
            result = connection.execute_many(
                "INSERT INTO temp_test_table (id, name) VALUES (:id, :name)",
                params_list,
            )
            tm.ok(result)
            tm.that(result.value, eq=3)
        finally:
            with contextlib.suppress(Exception):
                connection.execute_statement("DROP TABLE temp_test_table")
            connection.disconnect()

    # ------------------------------------------------------------------
    # API facade: context manager and metadata queries
    # ------------------------------------------------------------------

    def test_api_context_manager_executes_query(
        self,
        real_oracle_config: FlextDbOracleSettings,
    ) -> None:
        """The API context manager yields a usable, connected client."""
        cell = self._api_context_first_cell(real_oracle_config)
        tm.that(str(cell), has="Hello Oracle")

    def test_fetch_schemas_includes_a_system_schema(
        self,
        connected_oracle_api: FlextDbOracleApi,
    ) -> None:
        """``fetch_schemas`` returns a non-empty list containing a known system schema."""
        schemas_result = connected_oracle_api.fetch_schemas()
        tm.ok(schemas_result)
        schemas = schemas_result.value
        tm.that(len(schemas) > 0, eq=True)
        system_schemas = ("SYS", "SYSTEM", "FLEXT", "FLEXTTEST", "XDB")
        tm.that(
            any(
                known in schema.upper()
                for schema in schemas
                for known in system_schemas
            ),
            eq=True,
        )

    def test_fetch_tables_lists_seed_tables(
        self,
        connected_oracle_api: FlextDbOracleApi,
    ) -> None:
        """``fetch_tables`` returns the seeded HR-style tables."""
        tables_result = connected_oracle_api.fetch_tables()
        tm.ok(tables_result)
        tables_upper = [name.upper() for name in tables_result.value]
        for expected in ("EMPLOYEES", "DEPARTMENTS", "JOBS"):
            tm.that(any(expected in name for name in tables_upper), eq=True)

    def test_fetch_columns_exposes_named_columns(
        self,
        connected_oracle_api: FlextDbOracleApi,
    ) -> None:
        """``fetch_columns`` returns Column models whose ``name`` field is public."""
        result = connected_oracle_api.fetch_columns("EMPLOYEES")
        tm.ok(result)
        columns = result.value
        tm.that(len(columns) > 0, eq=True)
        column_names = [col.name.upper() for col in columns]
        for expected in ("EMPLOYEE_ID", "FIRST_NAME", "LAST_NAME", "EMAIL"):
            tm.that(column_names, has=expected)

    def test_query_returns_rows_for_aggregate(
        self,
        connected_oracle_api: FlextDbOracleApi,
    ) -> None:
        """``query`` succeeds and returns at least one row for a COUNT aggregate."""
        result = connected_oracle_api.query("SELECT COUNT(*) FROM EMPLOYEES")
        tm.ok(result)
        tm.that(len(result.value) > 0, eq=True)

    @pytest.mark.parametrize(
        ("singer_type", "format_hint", "expected_fragment"),
        [
            ("string", None, "VARCHAR2(4000)"),
            ("integer", None, "NUMBER(38)"),
            ("number", None, "NUMBER"),
            ("boolean", None, "NUMBER(1)"),
            ("string", "date-time", "TIMESTAMP"),
        ],
    )
    def test_convert_singer_type_maps_to_oracle_type(
        self,
        connected_oracle_api: FlextDbOracleApi,
        singer_type: str,
        format_hint: str | None,
        expected_fragment: str,
    ) -> None:
        """``convert_singer_type`` maps each Singer type to the Oracle type fragment."""
        result = (
            connected_oracle_api.convert_singer_type(singer_type)
            if format_hint is None
            else connected_oracle_api.convert_singer_type(singer_type, format_hint)
        )
        tm.ok(result)
        tm.that(result.value, has=expected_fragment)

    def test_execute_sql_creates_table_visible_to_fetch_tables(
        self,
        connected_oracle_api: FlextDbOracleApi,
    ) -> None:
        """A table created via ``execute_sql`` appears in ``fetch_tables``."""
        table_name = "TEST_TEMP_TABLE"
        try:
            ddl_sql = (
                f"CREATE TABLE {table_name} ("
                "id NUMBER NOT NULL, "
                "name VARCHAR2(100), "
                "created_at TIMESTAMP DEFAULT SYSDATE)"
            )
            execute_result = connected_oracle_api.execute_sql(ddl_sql)
            tm.ok(execute_result)

            tables_result = connected_oracle_api.fetch_tables()
            tm.ok(tables_result)
            table_names = [name.upper() for name in tables_result.value]
            tm.that(table_names, has=table_name.upper())

            filtered_result = connected_oracle_api.fetch_tables(table_name)
            tm.ok(filtered_result)
            filtered = filtered_result.value
            if filtered:
                tm.that(filtered[0].upper(), eq=table_name.upper())
        finally:
            with contextlib.suppress(Exception):
                connected_oracle_api.execute_sql(f"DROP TABLE {table_name}")

    # ------------------------------------------------------------------
    # Error paths (exercised without a live server)
    # ------------------------------------------------------------------

    def test_connect_with_invalid_credentials_fails_with_reason(self) -> None:
        """Connecting with bad credentials yields a failure carrying a diagnostic reason."""
        invalid_config = FlextDbOracleSettings(
            DbOracle={
                "host": "localhost",
                "port": 1521,
                "service_name": "XEPDB1",
                "username": "invalid_user",
                "password": "invalid_password",
            },
        )
        connection = FlextDbOracleServices(settings=invalid_config)
        result = connection.connect()
        tm.fail(result)
        error_msg = (result.error or "").lower()
        reasons = (
            "invalid username/password",
            "authentication",
            "login",
            "connection refused",
            "cannot connect",
            "connection test failed",
            "not connected to database",
        )
        tm.that(any(reason in error_msg for reason in reasons), eq=True)

    def test_invalid_sql_returns_failure(
        self,
        real_oracle_config: FlextDbOracleSettings,
    ) -> None:
        """Executing malformed SQL against a real connection returns a failure."""
        connection = self._connect_services(real_oracle_config)
        try:
            result = connection.execute_query(
                "SELECT FROM INVALID_TABLE_THAT_DOES_NOT_EXIST",
            )
            tm.fail(result)
            error_msg = (result.error or "").lower()
            tm.that("table" in error_msg or "not exist" in error_msg, eq=True)
        finally:
            connection.disconnect()

    def test_api_operations_fail_when_not_connected(
        self,
        real_oracle_config: FlextDbOracleSettings,
    ) -> None:
        """API queries and metadata fetches fail cleanly before ``connect``."""
        api = FlextDbOracleApi(real_oracle_config)

        query_result = api.query("SELECT 1 FROM DUAL")
        tm.fail(query_result)
        tm.that((query_result.error or "").lower(), has="not connected")

        tables_result = api.fetch_tables()
        tm.fail(tables_result)
        tables_error = (tables_result.error or "").lower()
        tm.that(
            "not connected" in tables_error or "connection" in tables_error,
            eq=True,
        )
