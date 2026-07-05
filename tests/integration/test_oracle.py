"""Behavioral tests for the flext-db-oracle public API contract.

Container-gated tests exercise REAL Oracle connectivity and skip cleanly when
no container is available. Container-free tests assert observable contract of
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
        host="mock-host",
        port=1521,
        service_name="mock-service",
        username="mock-user",
        password="mock-pass",
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

    # -------------------------------------------- container-free: settings API
    def test_settings_expose_supplied_connection_values(
        self,
        mock_oracle_config: FlextDbOracleSettings,
    ) -> None:
        """Valid settings expose the supplied connection fields (service upper-cased)."""
        assert mock_oracle_config.host == "mock-host"
        assert mock_oracle_config.port == 1521
        assert mock_oracle_config.service_name == "MOCK-SERVICE"
        assert mock_oracle_config.username == "mock-user"

    @pytest.mark.parametrize(
        ("overrides", "reason"),
        [
            ({"host": "   "}, "blank host is rejected"),
            ({"username": ""}, "empty username is rejected"),
            ({"service_name": "", "sid": None}, "missing service and sid rejected"),
            ({"port": 70000}, "port above the valid range is rejected"),
            ({"port": 0}, "port below the valid range is rejected"),
        ],
    )
    def test_invalid_settings_raise_validation_error(
        self,
        overrides: t.StrMapping,
        reason: str,
    ) -> None:
        """Business-rule violations fail construction (pydantic ValidationError)."""
        base = {
            "host": "db-host",
            "port": 1521,
            "service_name": "svc",
            "username": "user",
            "password": "pw",
        }
        base.update(overrides)
        with pytest.raises(ValueError):
            FlextDbOracleSettings(**base)

    def test_from_url_rejects_non_oracle_scheme(self) -> None:
        """``from_url`` returns a failure result for a non-Oracle scheme."""
        result = FlextDbOracleSettings.from_url("postgres://u:p@host:5432/db")
        assert result.failure
        assert result.error is not None
        assert "scheme" in result.error.lower()

    def test_from_url_parses_valid_oracle_url_into_settings(self) -> None:
        """``from_url`` maps a valid Oracle URL to the corresponding fields."""
        result = FlextDbOracleSettings.from_url("oracle://scott:tiger@dbhost:1600/ORCL")
        assert result.success
        settings = result.unwrap()
        assert settings.host == "dbhost"
        assert settings.port == 1600
        assert settings.username == "scott"
        assert settings.service_name == "ORCL"

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
        real_oracle_config: FlextDbOracleSettings | None,
    ) -> None:
        """Connecting and querying DUAL returns exactly one row on success."""
        if real_oracle_config is None:
            pytest.skip("Oracle container not available")
        api = FlextDbOracleApi(settings=oracle_config)
        connect_result = api.connect()
        if connect_result.failure:
            pytest.skip(f"Oracle container not available: {connect_result.error}")
        connected_api = connect_result.unwrap()
        assert connected_api.connected() is True
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
        real_oracle_config: FlextDbOracleSettings | None,
    ) -> None:
        """Schema/table/column lookups return string sequences on success."""
        if real_oracle_config is None:
            pytest.skip("Oracle container not available")
        api = FlextDbOracleApi(settings=oracle_config)
        connect_result = api.connect()
        if connect_result.failure:
            pytest.skip(f"Oracle container not available: {connect_result.error}")
        connected_api = connect_result.unwrap()

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
        real_oracle_config: FlextDbOracleSettings | None,
        invalid_sql: str,
    ) -> None:
        """Malformed or unresolvable SQL surfaces as a failure result."""
        if real_oracle_config is None:
            pytest.skip("Oracle container not available")
        api = FlextDbOracleApi(settings=oracle_config)
        connect_result = api.connect()
        if connect_result.failure:
            pytest.skip(f"Oracle container not available: {connect_result.error}")
        connected_api = connect_result.unwrap()

        result = connected_api.query(invalid_sql)
        assert result.failure
        assert result.error

        connected_api.disconnect()

    @pytest.mark.oracle
    def test_context_manager_connects_for_the_block_and_disconnects_after(
        self,
        oracle_config: FlextDbOracleSettings,
        real_oracle_config: FlextDbOracleSettings | None,
    ) -> None:
        """``with api`` yields a connected session and disconnects on exit."""
        if real_oracle_config is None:
            pytest.skip("Oracle container not available")
        api = FlextDbOracleApi(settings=oracle_config)
        try:
            with api as session:
                assert session.connected() is True
                assert session.query("SELECT 1 FROM DUAL").success
        except RuntimeError:
            pytest.skip("Oracle container not available")
        assert api.connected() is False

    @pytest.mark.oracle
    def test_insert_update_delete_roundtrip_is_observable_via_queries(
        self,
        connected_oracle_api: FlextDbOracleApi | None,
        test_database_setup: t.StrMapping | None,
    ) -> None:
        """DML mutations are observable through subsequent SELECT results."""
        if connected_oracle_api is None or test_database_setup is None:
            pytest.skip("Oracle container not available")
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
        connected_oracle_api: FlextDbOracleApi | None,
        test_database_setup: t.StrMapping | None,
    ) -> None:
        """A committed insert is readable and cleanup removes it again."""
        if connected_oracle_api is None or test_database_setup is None:
            pytest.skip("Oracle container not available")
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
        connected_oracle_api: FlextDbOracleApi | None,
    ) -> None:
        """A connected instance always reports at least one named schema."""
        if connected_oracle_api is None:
            pytest.skip("Oracle container not available")
        result = connected_oracle_api.fetch_schemas()
        assert result.success, result.error
        schemas = result.unwrap()
        assert schemas
        assert all(isinstance(name, str) for name in schemas)

    @pytest.mark.oracle
    @pytest.mark.xfail(
        reason=(
            "Pre-existing src defect: ConnectionStatus is not fully defined "
            "(missing datetime forward-ref / model_rebuild) so fetch_health_status "
            "raises PydanticUserError at services/connection.py:125. The behavioral "
            "contract below (connected/healthy/status_description/age) is asserted and "
            "will XPASS once the src model is fixed."
        ),
        strict=True,
        raises=Exception,
    )
    def test_health_status_reports_connected_and_healthy(
        self,
        real_oracle_config: FlextDbOracleSettings | None,
    ) -> None:
        """Health status of a live connection is connected, healthy, aged >= 0."""
        if real_oracle_config is None:
            pytest.skip("Oracle container not available")
        api = FlextDbOracleApi(settings=real_oracle_config)
        connect_result = api.connect()
        if connect_result.failure:
            pytest.skip(f"Oracle container not available: {connect_result.error}")
        connected_api = connect_result.unwrap()

        health_result = connected_api.fetch_health_status()
        assert health_result.success, health_result.error
        status = health_result.unwrap()
        assert status.connected is True
        assert status.healthy is True
        assert status.status_description == "Connected"
        assert status.connection_age_seconds >= 0

        assert connected_api.disconnect().success
