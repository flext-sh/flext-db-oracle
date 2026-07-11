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

from flext_db_oracle import FlextDbOracleApi, FlextDbOracleSettings

if TYPE_CHECKING:
    from flext_db_oracle import m
    from tests.typings import t


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
    def _cell(row: m.Dict, *keys: str) -> str:
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
        assert connect_result.success, connect_result.error
        assert api.connected() is True
        return api

    # -------------------------------------------- container-free: settings API
    def test_settings_expose_supplied_connection_values(
        self,
        mock_oracle_config: FlextDbOracleSettings,
    ) -> None:
        """Valid settings expose the supplied connection fields verbatim."""
        assert mock_oracle_config.DbOracle.host == "mock-host"
        assert mock_oracle_config.DbOracle.port == 1521
        assert mock_oracle_config.DbOracle.service_name == "mock-service"
        assert mock_oracle_config.DbOracle.username == "mock-user"

    def test_namespace_overrides_are_stored_verbatim(self) -> None:
        """Layer-0 namespace stores caller values without business-rule rewriting."""
        settings = FlextDbOracleSettings.model_validate(
            {"DbOracle": {"host": "db-host", "service_name": "svc"}},
        )
        assert settings.DbOracle.host == "db-host"
        assert settings.DbOracle.service_name == "svc"

    def test_from_url_rejects_non_oracle_scheme(self) -> None:
        """``from_url`` returns a failure result for a non-Oracle scheme."""
        result = FlextDbOracleApi.from_url("postgres://u:p@host:5432/db")
        assert result.failure
        assert result.error is not None
        assert "scheme" in result.error.lower()

    def test_from_url_parses_valid_oracle_url_into_settings(self) -> None:
        """``from_url`` maps a valid Oracle URL to the corresponding fields."""
        result = FlextDbOracleApi.from_url("oracle://scott:tiger@dbhost:1600/ORCL")
        assert result.success
        api = result.unwrap()
        assert api.settings.DbOracle.host == "dbhost"
        assert api.settings.DbOracle.port == 1600
        assert api.settings.DbOracle.username == "scott"
        assert api.settings.DbOracle.service_name == "ORCL"

    # ------------------------------------------------- container-free: API API
    def test_api_starts_disconnected(
        self,
        mock_oracle_config: FlextDbOracleSettings,
    ) -> None:
        """A freshly built API reports a disconnected connection state."""
        api = FlextDbOracleApi(settings=mock_oracle_config)
        assert api.connected() is False
        assert api.connection is None

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
        assert isinstance(api, FlextDbOracleApi)
        assert api.settings is mock_oracle_config
        assert api.connected() is False

    def test_repr_reflects_host_and_disconnected_state(
        self,
        mock_oracle_config: FlextDbOracleSettings,
    ) -> None:
        """``repr`` advertises the host and the disconnected status."""
        api = FlextDbOracleApi(settings=mock_oracle_config)
        rendered = repr(api)
        assert "mock-host" in rendered
        assert "disconnected" in rendered

    # ---------------------------------------------- container-gated: real flow
    @pytest.mark.oracle
    def test_connect_then_query_dual_returns_single_row(
        self,
        oracle_config: FlextDbOracleSettings,
    ) -> None:
        """Connecting and querying DUAL returns exactly one row on success."""
        connected_api = self._connect(oracle_config)
        assert connected_api.test_connection().unwrap() is True

        query_result = connected_api.query("SELECT SYSDATE FROM DUAL")
        assert query_result.success, query_result.error
        assert len(query_result.unwrap()) == 1

        assert connected_api.disconnect().unwrap() is True
        assert connected_api.connected() is False

    @pytest.mark.oracle
    def test_metadata_queries_return_string_sequences(
        self,
        oracle_config: FlextDbOracleSettings,
    ) -> None:
        """Schema/table/column lookups return string sequences on success."""
        connected_api = self._connect(oracle_config)

        schemas_result = connected_api.fetch_schemas()
        assert schemas_result.success, schemas_result.error
        schemas = schemas_result.unwrap()
        assert all(isinstance(name, str) for name in schemas)
        assert schemas, "A connected Oracle instance must expose at least one schema"

        tables_result = connected_api.fetch_tables(schemas[0])
        assert tables_result.success, tables_result.error
        tables = tables_result.unwrap()
        assert all(isinstance(name, str) for name in tables)

        if tables:
            columns_result = connected_api.fetch_columns(tables[0])
            assert columns_result.success, columns_result.error
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
        assert result.failure
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
            assert session.connected() is True
            assert session.query("SELECT 1 FROM DUAL").success
        assert api.connected() is False

    @pytest.mark.oracle
    def test_insert_update_delete_roundtrip_is_observable_via_queries(
        self,
        connected_oracle_api: FlextDbOracleApi,
        test_database_setup: t.StrMapping,
    ) -> None:
        """DML mutations are observable through subsequent SELECT results."""
        assert "test_table" in test_database_setup

        insert = connected_oracle_api.execute_statement(
            "INSERT INTO test_table (id, name) VALUES (1, 'Test User')",
        )
        assert insert.success, insert.error

        after_insert = connected_oracle_api.query(
            "SELECT id, name FROM test_table WHERE id = 1",
        )
        assert after_insert.success, after_insert.error
        rows = after_insert.unwrap()
        assert len(rows) == 1
        assert self._cell(rows[0], "id") == "1"
        assert self._cell(rows[0], "name") == "Test User"

        update = connected_oracle_api.execute_statement(
            "UPDATE test_table SET name = 'Updated User' WHERE id = 1",
        )
        assert update.success, update.error
        after_update = connected_oracle_api.query(
            "SELECT name FROM test_table WHERE id = 1",
        )
        assert self._cell(after_update.unwrap()[0], "name") == "Updated User"

        delete = connected_oracle_api.execute_statement(
            "DELETE FROM test_table WHERE id = 1",
        )
        assert delete.success, delete.error
        remaining = connected_oracle_api.query(
            "SELECT COUNT(*) AS count FROM test_table",
        )
        assert self._cell(remaining.unwrap()[0], "count", "count(*)") == "0"

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
        assert insert.success, insert.error
        assert connected_oracle_api.execute_statement("COMMIT").success

        visible = connected_oracle_api.query(
            "SELECT name FROM test_table WHERE id = 100",
        )
        assert visible.success, visible.error
        rows = visible.unwrap()
        assert len(rows) == 1
        assert self._cell(rows[0], "name") == "Transaction Test"

        connected_oracle_api.execute_statement("DELETE FROM test_table WHERE id = 100")

    @pytest.mark.oracle
    def test_fetch_schemas_returns_non_empty_string_sequence(
        self,
        connected_oracle_api: FlextDbOracleApi,
    ) -> None:
        """A connected instance always reports at least one named schema."""
        result = connected_oracle_api.fetch_schemas()
        assert result.success, result.error
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
        assert health_result.success, health_result.error
        status = health_result.unwrap()
        assert status.connected is True
        assert status.healthy is True
        assert status.status_description == "Connected"
        assert status.connection_age_seconds >= 0

        assert connected_api.disconnect().success
