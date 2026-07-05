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

from flext_db_oracle.api import FlextDbOracleApi
from flext_db_oracle.settings import FlextDbOracleSettings

if TYPE_CHECKING:
    from collections.abc import Mapping

    from flext_db_oracle import m
    from tests.typings import t

_NOT_CONNECTED = "not connected to database"


class TestsFlextDbOracleOracle:
    """Behavioral end-to-end tests for the Oracle API public contract."""

    @pytest.fixture
    def offline_settings(self) -> FlextDbOracleSettings:
        """Settings pointing at an unreachable host for offline contract tests."""
        return FlextDbOracleSettings(
            host="nonexistent-host.invalid",
            port=9999,
            service_name="INVALID_DB",
            username="invalid_user",
            password="invalid_password",
        )

    @pytest.fixture
    def offline_api(
        self,
        offline_settings: FlextDbOracleSettings,
    ) -> FlextDbOracleApi:
        """Unconnected API instance for pure-logic and error-path behavior."""
        return FlextDbOracleApi(offline_settings)

    # -- Configuration contract ------------------------------------------

    def test_from_env_maps_environment_variables_to_settings_fields(
        self,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """from_env succeeds and exposes each env value on the public fields."""
        env = {
            "FLEXT_TARGET_ORACLE_HOST": "e2e-test-host",
            "FLEXT_TARGET_ORACLE_PORT": "1521",
            "FLEXT_TARGET_ORACLE_SERVICE_NAME": "E2EDB",
            "FLEXT_TARGET_ORACLE_USERNAME": "e2e_user",
            "FLEXT_TARGET_ORACLE_PASSWORD": "e2e_password",
            "FLEXT_TARGET_ORACLE_POOL_MIN": "2",
            "FLEXT_TARGET_ORACLE_POOL_MAX": "20",
            "FLEXT_TARGET_ORACLE_TIMEOUT": "60",
        }
        for key, value in env.items():
            monkeypatch.setenv(key, value)

        result = FlextDbOracleSettings.from_env()

        assert result.success, result.error
        settings = result.value
        assert settings.host == "e2e-test-host"
        assert settings.port == 1521
        assert settings.service_name == "E2EDB"
        assert settings.username == "e2e_user"
        assert settings.password == "e2e_password"
        assert settings.pool_min == 2
        assert settings.pool_max == 20

    # -- Error-path contract (no connection) -----------------------------

    def test_query_without_connection_fails_with_not_connected_error(
        self,
        offline_api: FlextDbOracleApi,
    ) -> None:
        """Query returns a failure naming the missing connection."""
        result = offline_api.query("SELECT 1 FROM DUAL")

        assert result.failure
        assert _NOT_CONNECTED in (result.error or "").lower()

    def test_fetch_tables_without_connection_fails_with_not_connected_error(
        self,
        offline_api: FlextDbOracleApi,
    ) -> None:
        """fetch_tables returns a failure naming the missing connection."""
        result = offline_api.fetch_tables()

        assert result.failure
        assert _NOT_CONNECTED in (result.error or "").lower()

    def test_transaction_reports_disconnected_status_when_offline(
        self,
        offline_api: FlextDbOracleApi,
    ) -> None:
        """Transaction succeeds and reports the current (disconnected) state."""
        result = offline_api.transaction()

        assert result.success
        status = result.value
        assert status["connected"] is False
        assert status["transaction_available"] is True

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

        assert result.success, result.error
        assert expected_oracle_type in result.value

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

        assert result.success, result.error
        mapped = result.value
        assert "NUMBER" in mapped["id"]
        assert "VARCHAR2" in mapped["name"]
        assert "NUMBER(1)" in mapped["is_active"]

    # -- Full CRUD lifecycle against a real Oracle container -------------

    @staticmethod
    def _row_mapping(row: m.Dict) -> Mapping[str, object]:
        """Expose a query row's public mapping regardless of case handling."""
        return {key.upper(): value for key, value in row.root.items()}

    @pytest.mark.e2e
    def test_complete_crud_workflow_returns_expected_results(
        self,
        real_oracle_config: FlextDbOracleSettings,
    ) -> None:
        """A connect->create->insert->query->update->drop lifecycle behaves per contract."""
        table = "E2E_TEST_TABLE"
        with FlextDbOracleApi(settings=real_oracle_config) as api:
            assert api.test_connection().success

            schemas = api.fetch_schemas()
            assert schemas.success, schemas.error
            assert schemas.value

            create = api.execute_sql(
                f"CREATE TABLE {table} ("
                " ID NUMBER(10) NOT NULL PRIMARY KEY,"
                " NAME VARCHAR2(100) NOT NULL,"
                " EMAIL VARCHAR2(255))",
            )
            assert create.success, create.error
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
                    assert inserted.success, inserted.error

                selected = api.query(f"SELECT * FROM {table} ORDER BY ID")
                assert selected.success, selected.error
                assert len(selected.value) == 3

                counted = api.query(
                    f"SELECT COUNT(*) AS ROW_COUNT FROM {table}",
                )
                assert counted.success, counted.error
                count_row = self._row_mapping(counted.value[0])
                assert int(str(count_row["ROW_COUNT"])) == 3

                metadata = api.fetch_table_metadata(table)
                assert metadata.success, metadata.error
                assert metadata.value.table_name == table

                columns = api.fetch_columns(table)
                assert columns.success, columns.error
                assert len(columns.value) >= 3

                primary_keys = api.fetch_primary_keys(table)
                assert primary_keys.success, primary_keys.error
                assert "ID" in primary_keys.value

                updated = api.execute_statement(
                    f"UPDATE {table} SET EMAIL = 'bob@example.com' WHERE ID = 3",
                )
                assert updated.success, updated.error

                verify = api.query(f"SELECT EMAIL FROM {table} WHERE ID = 3")
                assert verify.success, verify.error
                assert len(verify.value) == 1
                verified_row = self._row_mapping(verify.value[0])
                assert verified_row["EMAIL"] == "bob@example.com"
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
        try:
            with api1, api2:
                result1 = api1.query("SELECT 'API1' AS SOURCE FROM DUAL")
                result2 = api2.query("SELECT 'API2' AS SOURCE FROM DUAL")
                assert result1.success, result1.error
                assert result2.success, result2.error
                assert self._row_mapping(result1.value[0])["SOURCE"] == "API1"
                assert self._row_mapping(result2.value[0])["SOURCE"] == "API2"
        except ConnectionError:
            pytest.skip("Oracle database not available for concurrent testing")

    @pytest.mark.e2e
    @pytest.mark.benchmark
    def test_benchmark_query_returns_single_row(
        self,
        real_oracle_config: FlextDbOracleSettings,
    ) -> None:
        """A trivial benchmark query returns exactly one row from the database."""
        try:
            with FlextDbOracleApi(settings=real_oracle_config) as api:
                result = api.query("SELECT 1 AS ONE FROM DUAL")
                assert result.success, result.error
                assert len(result.value) == 1
        except ConnectionError:
            pytest.skip("Oracle database not available for performance testing")
