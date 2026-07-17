"""Behavioral tests for the flext-db-oracle public API contract.

Container-gated tests exercise REAL Oracle connectivity and fail loudly when
the shared container is unavailable. Container-free tests assert observable contract of
``FlextDbOracleSettings`` and ``FlextDbOracleApi`` (validation, factories,
representation, connection state) without any external dependency.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
from flext_tests import tm

from flext_db_oracle import FlextDbOracleApi, FlextDbOracleSettings

if TYPE_CHECKING:
    from tests import p, t


@pytest.fixture
def mock_oracle_config() -> FlextDbOracleSettings:
    """Return a well-formed offline Oracle settings value."""
    return FlextDbOracleSettings(
        DbOracle={
            "host": "mock-host",
            "port": 1521,
            "service_name": "mock-service",
            "username": "mock-user",
            "password": "mock-pass",
        },
    )


@pytest.mark.integration
class TestsFlextDbOracleOracle:
    """Behavioral contract of the Oracle settings and API public surface."""

    # ----------------------------------------------------------------- helpers
    @staticmethod
    def _cell(row: p.Dict, *keys: str) -> str:
        """Read one column value from a query row via its public model dump.

        Oracle returns column names in varying case; probe the requested keys
        (and their case variants) against the row's public mapping.
        """
        dumped = row.model_dump()
        for key in keys:
            for candidate in (key, key.upper(), key.lower()):
                if candidate in dumped:
                    return str(dumped[candidate])
        return ""

    @staticmethod
    def _connect(settings: FlextDbOracleSettings) -> FlextDbOracleApi:
        """Connect a public API instance or fail the real-Oracle contract."""
        api = FlextDbOracleApi(settings=settings)
        connect_result = api.connect()
        tm.ok(connect_result)
        tm.that(api.connected(), eq=True)
        return api

    # -------------------------------------------- container-free: settings API
    def test_settings_expose_supplied_connection_values(
        self,
        mock_oracle_config: FlextDbOracleSettings,
    ) -> None:
        """Valid settings expose the supplied connection fields verbatim."""
        tm.that(mock_oracle_config.DbOracle.host, eq="mock-host")
        tm.that(mock_oracle_config.DbOracle.port, eq=1521)
        tm.that(mock_oracle_config.DbOracle.service_name, eq="mock-service")
        tm.that(mock_oracle_config.DbOracle.username, eq="mock-user")

    def test_namespace_overrides_are_stored_verbatim(self) -> None:
        """Layer-0 namespace stores caller values without business-rule rewriting."""
        settings = FlextDbOracleSettings.model_validate(
            {"DbOracle": {"host": "db-host", "service_name": "svc"}},
        )
        tm.that(settings.DbOracle.host, eq="db-host")
        tm.that(settings.DbOracle.service_name, eq="svc")

    def test_from_url_rejects_non_oracle_scheme(self) -> None:
        """``from_url`` returns a failure result for a non-Oracle scheme."""
        result = FlextDbOracleApi.from_url("postgres://u:p@host:5432/db")
        tm.fail(result)
        tm.that(result.error, none=False)
        tm.that(result.error.lower(), has="scheme")

    def test_from_url_parses_valid_oracle_url_into_settings(self) -> None:
        """``from_url`` maps a valid Oracle URL to the corresponding fields."""
        result = FlextDbOracleApi.from_url("oracle://scott:tiger@dbhost:1600/ORCL")
        tm.ok(result)
        api = result.unwrap()
        tm.that(api.settings.DbOracle.host, eq="dbhost")
        tm.that(api.settings.DbOracle.port, eq=1600)
        tm.that(api.settings.DbOracle.username, eq="scott")
        tm.that(api.settings.DbOracle.service_name, eq="ORCL")

    # ------------------------------------------------- container-free: API API
    def test_api_starts_disconnected(
        self,
        mock_oracle_config: FlextDbOracleSettings,
    ) -> None:
        """A freshly built API reports a disconnected connection state."""
        api = FlextDbOracleApi(settings=mock_oracle_config)
        tm.that(api.connected(), eq=False)
        tm.that(api.connection, none=True)

    def test_api_exposes_supplied_settings(
        self,
        mock_oracle_config: FlextDbOracleSettings,
    ) -> None:
        """The API surfaces the same settings value it was constructed with."""
        api = FlextDbOracleApi(settings=mock_oracle_config)
        assert api.settings is mock_oracle_config
        assert api.oracle_config is mock_oracle_config

    def test_from_config_builds_equivalent_api(
        self,
        mock_oracle_config: FlextDbOracleSettings,
    ) -> None:
        """``from_config`` yields an API bound to the given settings."""
        api = FlextDbOracleApi.from_config(mock_oracle_config)
        tm.that(api, is_=FlextDbOracleApi)
        assert api.settings is mock_oracle_config
        tm.that(api.connected(), eq=False)

    def test_repr_reflects_host_and_disconnected_state(
        self,
        mock_oracle_config: FlextDbOracleSettings,
    ) -> None:
        """``repr`` advertises the host and the disconnected status."""
        api = FlextDbOracleApi(settings=mock_oracle_config)
        rendered = repr(api)
        tm.that(rendered, has="mock-host")
        tm.that(rendered, has="disconnected")

    # ---------------------------------------------- container-gated: real flow
    @pytest.mark.oracle
    def test_connect_then_query_dual_returns_single_row(
        self,
        oracle_config: FlextDbOracleSettings,
    ) -> None:
        """Connecting and querying DUAL returns exactly one row on success."""
        connected_api = self._connect(oracle_config)
        tm.that(connected_api.test_connection().unwrap(), eq=True)

        query_result = connected_api.query("SELECT SYSDATE FROM DUAL")
        tm.ok(query_result)
        tm.that(len(query_result.unwrap()), eq=1)

        tm.that(connected_api.disconnect().unwrap(), eq=True)
        tm.that(connected_api.connected(), eq=False)

    @pytest.mark.oracle
    def test_metadata_queries_return_string_sequences(
        self,
        oracle_config: FlextDbOracleSettings,
    ) -> None:
        """Schema/table/column lookups return string sequences on success."""
        connected_api = self._connect(oracle_config)

        schemas_result = connected_api.fetch_schemas()
        tm.ok(schemas_result)
        schemas = schemas_result.unwrap()
        assert all(isinstance(name, str) for name in schemas)
        assert schemas, "A connected Oracle instance must expose at least one schema"

        tables_result = connected_api.fetch_tables(schemas[0])
        tm.ok(tables_result)
        tables = tables_result.unwrap()
        assert all(isinstance(name, str) for name in tables)

        if tables:
            columns_result = connected_api.fetch_columns(tables[0])
            tm.ok(columns_result)
            assert all(isinstance(col, str) for col in columns_result.unwrap())

        connected_api.disconnect()

    @pytest.mark.oracle
    @pytest.mark.parametrize(
        "invalid_sql",
        [
            "INVALID SQL STATEMENT",
            "SELECT * FROM NONEXISTENT_TABLE_12345",
        ],
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
        assert result.error

        connected_api.disconnect()

    @pytest.mark.oracle
    def test_context_manager_connects_for_the_block_and_disconnects_after(
        self,
        oracle_config: FlextDbOracleSettings,
    ) -> None:
        """``with api`` yields a connected session and disconnects on exit."""
        api = FlextDbOracleApi(settings=oracle_config)
        with api as session:
            tm.that(session.connected(), eq=True)
            tm.ok(session.query("SELECT 1 FROM DUAL"))
        tm.that(api.connected(), eq=False)

    @pytest.mark.oracle
    def test_insert_update_delete_roundtrip_is_observable_via_queries(
        self,
        connected_oracle_api: FlextDbOracleApi,
        test_database_setup: t.StrMapping,
    ) -> None:
        """DML mutations are observable through subsequent SELECT results."""
        tm.that(test_database_setup, has="test_table")

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

    @pytest.mark.oracle
    def test_committed_row_is_visible_after_commit(
        self,
        connected_oracle_api: FlextDbOracleApi,
        test_database_setup: t.StrMapping,
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

    @pytest.mark.oracle
    def test_fetch_schemas_returns_non_empty_string_sequence(
        self,
        connected_oracle_api: FlextDbOracleApi,
    ) -> None:
        """A connected instance always reports at least one named schema."""
        result = connected_oracle_api.fetch_schemas()
        tm.ok(result)
        schemas = result.unwrap()
        assert schemas
        assert all(isinstance(name, str) for name in schemas)

    @pytest.mark.oracle
    def test_health_status_reports_connected_and_healthy(
        self,
        real_oracle_config: FlextDbOracleSettings,
    ) -> None:
        """Health status of a live connection is connected, healthy, aged >= 0."""
        connected_api = self._connect(real_oracle_config)

        health_result = connected_api.fetch_health_status()
        tm.ok(health_result)
        status = health_result.unwrap()
        tm.that(status.connected, eq=True)
        tm.that(status.healthy, eq=True)
        tm.that(status.status_description, eq="Connected")
        assert status.connection_age_seconds >= 0

        tm.ok(connected_api.disconnect())
