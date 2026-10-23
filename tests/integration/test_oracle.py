"""Behavioral tests for the flext-db-oracle public API contract.

Container-gated tests exercise REAL Oracle connectivity when prerequisites are
available, skipping before fixtures otherwise. Container-free tests assert the contract of
``FlextDbOracleSettings`` and ``FlextDbOracleApi`` (validation, factories,
representation, connection state) without any external dependency.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from flext_db_oracle import FlextDbOracleApi, FlextDbOracleSettings
from tests import tm

if TYPE_CHECKING:
    from tests import m, t


@pytest.fixture
def offline_oracle_settings() -> FlextDbOracleSettings:
    """Return a well-formed offline Oracle settings value."""
    return FlextDbOracleSettings.model_validate({
        "DbOracle": {
            "host": "mock-host",
            "port": 1521,
            "service_name": "mock-service",
            "username": "mock-user",
            "password": "p" + "4" * 12,
        },
    })


@pytest.mark.integration
class TestsFlextDbOracleOracle:
    """Behavioral contract of the Oracle settings and API public surface."""

    # ----------------------------------------------------------------- helpers
    @staticmethod
    def _cell(row: m.Dict, *keys: str) -> str:
        """Read one column value from a query row via its public root mapping.

        Oracle returns column names in varying case; probe the requested keys
        (and their case variants) against the row's public mapping.

        Returns:
            The resulting ``str``.

        """
        values = row.root
        for key in keys:
            for candidate in (key, key.upper(), key.lower()):
                if candidate in values:
                    return str(values[candidate])
        return ""

    @staticmethod
    def _connect(settings: FlextDbOracleSettings) -> FlextDbOracleApi:
        """Connect a public API instance or fail the real-Oracle contract.

        Returns:
            The resulting ``FlextDbOracleApi``.

        """
        api = FlextDbOracleApi(settings=settings)
        connect_result = api.connect()
        tm.ok(connect_result)
        tm.ok(api.connected())
        return api

    # -------------------------------------------- container-free: settings API
    @staticmethod
    def test_settings_expose_supplied_connection_values(
        offline_oracle_settings: FlextDbOracleSettings,
    ) -> None:
        """Valid settings expose the supplied connection fields verbatim."""
        tm.that(offline_oracle_settings.DbOracle.host, eq="mock-host")
        tm.that(offline_oracle_settings.DbOracle.port, eq=1521)
        tm.that(offline_oracle_settings.DbOracle.service_name, eq="mock-service")
        tm.that(offline_oracle_settings.DbOracle.username, eq="mock-user")

    @staticmethod
    def test_namespace_overrides_are_stored_verbatim() -> None:
        """Layer-0 namespace stores caller values without business-rule rewriting."""
        settings = FlextDbOracleSettings.model_validate({
            "DbOracle": {"host": "db-host", "service_name": "svc"},
        })
        tm.that(settings.DbOracle.host, eq="db-host")
        tm.that(settings.DbOracle.service_name, eq="svc")

    @staticmethod
    def test_from_url_rejects_non_oracle_scheme() -> None:
        """``from_url`` returns a failure result for a non-Oracle scheme."""
        result = FlextDbOracleApi.from_url("postgres://u:p@host:5432/db")
        error = tm.fail(result)
        tm.that(error.lower(), has="scheme")

    @staticmethod
    def test_from_url_parses_valid_oracle_url_into_settings() -> None:
        """``from_url`` maps a valid Oracle URL to the corresponding fields."""
        result = FlextDbOracleApi.from_url("oracle://scott:tiger@dbhost:1600/ORCL")
        tm.ok(result)
        api = result.unwrap()
        tm.that(api.settings.DbOracle.host, eq="dbhost")
        tm.that(api.settings.DbOracle.port, eq=1600)
        tm.that(api.settings.DbOracle.username, eq="scott")
        tm.that(api.settings.DbOracle.service_name, eq="ORCL")

    # ------------------------------------------------- container-free: API API
    @staticmethod
    def test_api_starts_disconnected(
        offline_oracle_settings: FlextDbOracleSettings,
    ) -> None:
        """A freshly built API reports a disconnected connection state."""
        api = FlextDbOracleApi(settings=offline_oracle_settings)
        tm.fail(api.connected())
        tm.that(api.connection, none=True)

    @staticmethod
    def test_api_exposes_supplied_settings(
        offline_oracle_settings: FlextDbOracleSettings,
    ) -> None:
        """The API surfaces the same settings value it was constructed with."""
        api = FlextDbOracleApi(settings=offline_oracle_settings)
        tm.that(api.settings is offline_oracle_settings)
        tm.that(api.oracle_config is offline_oracle_settings)

    @staticmethod
    def test_from_config_builds_equivalent_api(
        offline_oracle_settings: FlextDbOracleSettings,
    ) -> None:
        """``from_config`` yields an API bound to the given settings."""
        api = FlextDbOracleApi.from_config(offline_oracle_settings)
        tm.that(api, is_=FlextDbOracleApi)
        tm.that(api.settings is offline_oracle_settings)
        tm.fail(api.connected())

    @staticmethod
    def test_repr_reflects_host_and_disconnected_state(
        offline_oracle_settings: FlextDbOracleSettings,
    ) -> None:
        """``repr`` advertises the host and the disconnected status."""
        api = FlextDbOracleApi(settings=offline_oracle_settings)
        rendered = repr(api)
        tm.that(rendered, has="mock-host")
        tm.that(rendered, has="disconnected")

    # ---------------------------------------------- container-gated: real flow
    def test_connect_then_query_dual_returns_single_row(
        self,
        oracle_config: FlextDbOracleSettings,
    ) -> None:
        """Connecting and querying DUAL returns exactly one row on success."""
        connected_api = self._connect(oracle_config)
        tm.ok(connected_api.test_connection().unwrap())

        query_result = connected_api.query("SELECT SYSDATE FROM DUAL")
        tm.ok(query_result)
        tm.that(len(query_result.unwrap()), eq=1)

        tm.ok(connected_api.disconnect().unwrap())
        tm.fail(connected_api.connected())

    def test_metadata_queries_return_string_sequences(
        self,
        oracle_config: FlextDbOracleSettings,
    ) -> None:
        """Schema/table/column lookups return string sequences on success."""
        connected_api = self._connect(oracle_config)

        schemas_result = connected_api.fetch_schemas()
        tm.ok(schemas_result)
        schemas = schemas_result.unwrap()
        tm.that(all(isinstance(name, str) for name in schemas))
        tm.that(
            schemas,
            where=bool,
            msg="A connected Oracle instance must expose at least one schema",
        )

        tables_result = connected_api.fetch_tables(schemas[0])
        tm.ok(tables_result)
        tables = tables_result.unwrap()
        tm.that(all(isinstance(name, str) for name in tables))

        if tables:
            columns_result = connected_api.fetch_columns(tables[0])
            tm.ok(columns_result)
            tm.that(all(isinstance(col, str) for col in columns_result.unwrap()))

        connected_api.disconnect()

    @pytest.mark.parametrize(
        "invalid_sql",
        ["INVALID SQL STATEMENT", "SELECT * FROM NONEXISTENT_TABLE_12345"],
    )
    def test_invalid_sql_yields_failure_result(
        self,
        oracle_config: FlextDbOracleSettings,
        invalid_sql: str,
    ) -> None:
        """Malformed or unresolvable SQL surfaces as a failure result."""
        connected_api = self._connect(oracle_config)

        result = connected_api.query(invalid_sql)
        tm.fail(result)
        tm.that(result.error, where=bool)

        connected_api.disconnect()

    @staticmethod
    def test_context_manager_connects_for_the_block_and_disconnects_after(
        oracle_config: FlextDbOracleSettings,
    ) -> None:
        """``with api`` yields a connected session and disconnects on exit."""
        api = FlextDbOracleApi(settings=oracle_config)
        with api as session:
            tm.ok(session.connected())
            tm.ok(session.query("SELECT 1 FROM DUAL"))
        tm.fail(api.connected())

    def test_insert_update_delete_roundtrip_is_observable_via_queries(
        self,
        connected_oracle_api: FlextDbOracleApi,
        oracle_test_database: t.StrMapping,
    ) -> None:
        """DML mutations are observable through subsequent SELECT results."""
        tm.that(oracle_test_database, has="test_table")

        insert = connected_oracle_api.execute_statement(
            "INSERT INTO test_table (id, name) VALUES (1, 'Test User')",
        )
        tm.ok(insert)

        after_insert = connected_oracle_api.query(
            "SELECT id, name FROM test_table WHERE id = 1",
        )
        tm.ok(after_insert)
        rows = after_insert.unwrap()
        tm.that(len(rows), eq=1)
        tm.that(self._cell(rows[0], "id"), eq="1")
        tm.that(self._cell(rows[0], "name"), eq="Test User")

        update = connected_oracle_api.execute_statement(
            "UPDATE test_table SET name = 'Updated User' WHERE id = 1",
        )
        tm.ok(update)
        after_update = connected_oracle_api.query(
            "SELECT name FROM test_table WHERE id = 1",
        )
        tm.that(self._cell(after_update.unwrap()[0], "name"), eq="Updated User")

        delete = connected_oracle_api.execute_statement(
            "DELETE FROM test_table WHERE id = 1",
        )
        tm.ok(delete)
        remaining = connected_oracle_api.query(
            "SELECT COUNT(*) AS count FROM test_table",
        )
        tm.that(self._cell(remaining.unwrap()[0], "count", "count(*)"), eq="0")

    @pytest.mark.usefixtures("oracle_test_database")
    def test_committed_row_is_visible_after_commit(
        self,
        connected_oracle_api: FlextDbOracleApi,
    ) -> None:
        """A committed insert is readable and cleanup removes it again."""
        insert = connected_oracle_api.execute_statement(
            "INSERT INTO test_table (id, name) VALUES (100, 'Transaction Test')",
        )
        tm.ok(insert)
        tm.ok(connected_oracle_api.execute_statement("COMMIT"))

        visible = connected_oracle_api.query(
            "SELECT name FROM test_table WHERE id = 100",
        )
        tm.ok(visible)
        rows = visible.unwrap()
        tm.that(len(rows), eq=1)
        tm.that(self._cell(rows[0], "name"), eq="Transaction Test")

        connected_oracle_api.execute_statement("DELETE FROM test_table WHERE id = 100")

    @staticmethod
    def test_fetch_schemas_returns_non_empty_string_sequence(
        connected_oracle_api: FlextDbOracleApi,
    ) -> None:
        """A connected instance always reports at least one named schema."""
        result = connected_oracle_api.fetch_schemas()
        tm.ok(result)
        schemas = result.unwrap()
        tm.that(schemas, where=bool)
        tm.that(all(isinstance(name, str) for name in schemas))

    def test_health_status_reports_connected_and_healthy(
        self,
        real_oracle_config: FlextDbOracleSettings,
    ) -> None:
        """Health status of a live connection is connected, healthy, aged >= 0."""
        connected_api = self._connect(real_oracle_config)

        health_result = connected_api.fetch_health_status()
        tm.ok(health_result)
        status = health_result.unwrap()
        tm.ok(status.connected)
        tm.ok(status.healthy)
        tm.that(status.status_description, eq="Connected")
        tm.that(status.connection_age_seconds >= 0)

        tm.ok(connected_api.disconnect())
