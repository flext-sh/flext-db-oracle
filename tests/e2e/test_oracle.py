"""End-to-end behavioral tests for the flext-db-oracle public API.

These tests assert the OBSERVABLE CONTRACT of ``FlextDbOracleApi`` and
``FlextDbOracleSettings``: return values, ``r[T]`` success/failure outcomes,
error messages, and public model state. Pure-logic and error-path behaviors run
offline; the full CRUD lifecycle exercises a real Oracle container.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
from flext_tests import tm

from flext_db_oracle import FlextDbOracleSettings
from flext_db_oracle.api import FlextDbOracleApi
from tests import p, t, u

if TYPE_CHECKING:
    from collections.abc import Mapping

_NOT_CONNECTED = "not connected to database"


class TestsFlextDbOracleOracle:
    """Behavioral end-to-end tests for the Oracle API public contract."""

    @pytest.fixture
    def offline_settings(self) -> FlextDbOracleSettings:
        """Return settings pointing at an unreachable host for offline contract tests."""
        return FlextDbOracleSettings(
            DbOracle={
                "host": "nonexistent-host.invalid",
                "port": 9999,
                "service_name": "INVALID_DB",
                "username": "invalid_user",
                "password": "invalid_password",
            },
        )

    @pytest.fixture
    def offline_api(
        self,
        offline_settings: FlextDbOracleSettings,
    ) -> FlextDbOracleApi:
        """Unconnected API instance for pure-logic and error-path behavior."""
        return FlextDbOracleApi(offline_settings)

    # -- Configuration contract ------------------------------------------

    def test_env_vars_populate_settings_namespace(self) -> None:
        """ORACLE_DBORACLE__* env vars populate the public settings namespace."""
        FlextDbOracleSettings.reset_for_testing()
        env = {
            "ORACLE_DBORACLE__HOST": "e2e-test-host",
            "ORACLE_DBORACLE__PORT": "1521",
            "ORACLE_DBORACLE__SERVICE_NAME": "E2EDB",
            "ORACLE_DBORACLE__USERNAME": "e2e_user",
            "ORACLE_DBORACLE__PASSWORD": "e2e_password",
            "ORACLE_DBORACLE__POOL_MIN": "2",
            "ORACLE_DBORACLE__POOL_MAX": "20",
            "ORACLE_DBORACLE__TIMEOUT": "60",
        }
        with u.Tests.env_vars_context(env):
            settings = FlextDbOracleSettings()

        tm.that(settings.DbOracle.host, eq="e2e-test-host")
        tm.that(settings.DbOracle.port, eq=1521)
        tm.that(settings.DbOracle.service_name, eq="E2EDB")
        tm.that(settings.DbOracle.username, eq="e2e_user")
        tm.that(settings.DbOracle.password, eq="e2e_password")
        tm.that(settings.DbOracle.pool_min, eq=2)
        tm.that(settings.DbOracle.pool_max, eq=20)

    # -- Error-path contract (no connection) -----------------------------

    def test_query_without_connection_fails_with_not_connected_error(
        self,
        offline_api: FlextDbOracleApi,
    ) -> None:
        """Query returns a failure naming the missing connection."""
        result = offline_api.query("SELECT 1 FROM DUAL")

        tm.fail(result)
        tm.that((result.error or "").lower(), has=_NOT_CONNECTED)

    def test_fetch_tables_without_connection_fails_with_not_connected_error(
        self,
        offline_api: FlextDbOracleApi,
    ) -> None:
        """fetch_tables returns a failure naming the missing connection."""
        result = offline_api.fetch_tables()

        tm.fail(result)
        tm.that((result.error or "").lower(), has=_NOT_CONNECTED)

    def test_transaction_reports_disconnected_status_when_offline(
        self,
        offline_api: FlextDbOracleApi,
    ) -> None:
        """Transaction succeeds and reports the current (disconnected) state."""
        result = offline_api.transaction()

        tm.ok(result)
        status = result.value
        tm.that(status["connected"], eq=False)
        tm.that(status["transaction_available"], eq=True)

    # -- Singer type-conversion contract ---------------------------------

    @pytest.mark.parametrize(
        ("singer_type", "expected_oracle_type"),
        [
            ("string", "VARCHAR2(4000)"),
            ("integer", "NUMBER(38)"),
            ("number", "NUMBER"),
            ("boolean", "NUMBER(1)"),
            ("array", "VARCHAR2(255)"),
        ],
    )
    def test_convert_singer_type_returns_expected_oracle_type(
        self,
        offline_api: FlextDbOracleApi,
        singer_type: str,
        expected_oracle_type: str,
    ) -> None:
        """convert_singer_type maps each Singer type to its Oracle SQL type."""
        result = offline_api.convert_singer_type(singer_type)

        tm.ok(result)
        tm.that(result.value, has=expected_oracle_type)

    def test_map_singer_schema_maps_properties_to_oracle_column_types(
        self,
        offline_api: FlextDbOracleApi,
    ) -> None:
        """map_singer_schema converts each JSON-Schema property to an Oracle type."""
        singer_schema: t.JsonMapping = {
            "properties": {
                "id": {"type": "integer"},
                "name": {"type": "string"},
                "is_active": {"type": "boolean"},
            },
        }

        result = offline_api.map_singer_schema(singer_schema)

        tm.ok(result)
        mapped = result.value
        tm.that(mapped["id"], has="NUMBER")
        tm.that(mapped["name"], has="VARCHAR2")
        tm.that(mapped["is_active"], has="NUMBER(1)")

    # -- Full CRUD lifecycle against a real Oracle container -------------

    @staticmethod
    def _row_mapping(row: p.Dict) -> Mapping[str, object]:
        """Expose a query row's public mapping regardless of case handling."""
        return {key.upper(): value for key, value in row.root.items()}

    def _concurrent_source_rows(
        self,
        api1: FlextDbOracleApi,
        api2: FlextDbOracleApi,
    ) -> tuple[Mapping[str, object], Mapping[str, object]]:
        """Return one query row from each concurrent API context."""
        with api1, api2:
            result1 = api1.query("SELECT 'API1' AS SOURCE FROM DUAL")
            result2 = api2.query("SELECT 'API2' AS SOURCE FROM DUAL")
            tm.ok(result1)
            tm.ok(result2)
            return self._row_mapping(result1.value[0]), self._row_mapping(
                result2.value[0],
            )

    @pytest.mark.e2e
    def test_complete_crud_workflow_returns_expected_results(
        self,
        real_oracle_config: FlextDbOracleSettings,
    ) -> None:
        """A connect->create->insert->query->update->drop lifecycle behaves per contract."""
        table = "E2E_TEST_TABLE"
        with FlextDbOracleApi(settings=real_oracle_config) as api:
            tm.ok(api.test_connection())

            schemas = api.fetch_schemas()
            tm.ok(schemas)
            assert schemas.value

            create = api.execute_sql(
                f"CREATE TABLE {table} ("
                " ID NUMBER(10) NOT NULL PRIMARY KEY,"
                " NAME VARCHAR2(100) NOT NULL,"
                " EMAIL VARCHAR2(255))",
            )
            tm.ok(create)
            try:
                rows = [
                    (1, "John Doe", "'john@example.com'"),
                    (2, "Jane Smith", "'jane@example.com'"),
                    (3, "Bob Wilson", "NULL"),
                ]
                for row_id, name, email in rows:
                    inserted = api.execute_statement(
                        f"INSERT INTO {table} (ID, NAME, EMAIL) "
                        f"VALUES ({row_id}, '{name}', {email})",
                    )
                    tm.ok(inserted)

                selected = api.query(f"SELECT * FROM {table} ORDER BY ID")
                tm.ok(selected)
                tm.that(len(selected.value), eq=3)

                counted = api.query(
                    f"SELECT COUNT(*) AS ROW_COUNT FROM {table}",
                )
                tm.ok(counted)
                count_row = self._row_mapping(counted.value[0])
                tm.that(int(str(count_row["ROW_COUNT"])), eq=3)

                metadata = api.fetch_table_metadata(table)
                tm.ok(metadata)
                tm.that(metadata.value.table_name, eq=table)

                columns = api.fetch_columns(table)
                tm.ok(columns)
                assert len(columns.value) >= 3

                primary_keys = api.fetch_primary_keys(table)
                tm.ok(primary_keys)
                tm.that(primary_keys.value, has="ID")

                updated = api.execute_statement(
                    f"UPDATE {table} SET EMAIL = 'bob@example.com' WHERE ID = 3",
                )
                tm.ok(updated)

                verify = api.query(f"SELECT EMAIL FROM {table} WHERE ID = 3")
                tm.ok(verify)
                tm.that(len(verify.value), eq=1)
                verified_row = self._row_mapping(verify.value[0])
                tm.that(verified_row["EMAIL"], eq="bob@example.com")
            finally:
                api.execute_sql(f"DROP TABLE {table}")

    @pytest.mark.e2e
    def test_concurrent_apis_return_independent_query_results(
        self,
        real_oracle_config: FlextDbOracleSettings,
    ) -> None:
        """Two concurrent API contexts each return their own query result."""
        api1 = FlextDbOracleApi(real_oracle_config, context_name="connection1")
        api2 = FlextDbOracleApi(real_oracle_config, context_name="connection2")
        row1, row2 = self._concurrent_source_rows(api1, api2)
        tm.that(row1["SOURCE"], eq="API1")
        tm.that(row2["SOURCE"], eq="API2")

    @pytest.mark.e2e
    @pytest.mark.benchmark
    def test_benchmark_query_returns_single_row(
        self,
        real_oracle_config: FlextDbOracleSettings,
    ) -> None:
        """A trivial benchmark query returns exactly one row from the database."""
        with FlextDbOracleApi(settings=real_oracle_config) as api:
            result = api.query("SELECT 1 AS ONE FROM DUAL")
            tm.ok(result)
            tm.that(len(result.value), eq=1)
