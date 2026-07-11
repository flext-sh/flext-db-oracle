"""Behavioral contract tests for the public FlextDbOracleApi facade.

Every test exercises OBSERVABLE public behavior only: return values, the
``r[T]`` success/failure outcome, public model state, raised exceptions, and
documented error messages. No private attributes, internal-collaborator
spying, monkeypatching of the unit under test, or line-coverage pokes.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from collections.abc import Callable, Mapping

import pytest
from flext_tests import tm

from flext_db_oracle import FlextDbOracleApi, FlextDbOracleSettings, p
from flext_db_oracle.services.facade import FlextDbOracleServices
from tests.typings import t


class TestsFlextDbOracleApi:
    """Public-contract behavior of the Oracle API facade (no mocks, no internals)."""

    @staticmethod
    def _settings(
        host: str = "127.0.0.1",
        service_name: str = "TEST",
    ) -> FlextDbOracleSettings:
        """Build an unreachable-but-valid settings value for offline behavior."""
        return FlextDbOracleSettings(
            DbOracle={
                "host": host,
                "port": 19999,
                "service_name": service_name,
                "username": "test_user",
                "password": "test_password",
                "timeout": 1,
            },
        )

    @pytest.fixture
    def settings(self) -> FlextDbOracleSettings:
        """Typed Oracle settings pointing at an unreachable local endpoint."""
        return self._settings()

    @pytest.fixture
    def api(self, settings: FlextDbOracleSettings) -> FlextDbOracleApi:
        """A fresh, disconnected API instance under test."""
        return FlextDbOracleApi(settings)

    # ----- construction & configuration contract -------------------------

    def test_construction_exposes_settings_and_starts_disconnected(
        self,
        settings: FlextDbOracleSettings,
    ) -> None:
        """A new API returns its settings unchanged and reports disconnected."""
        api = FlextDbOracleApi(settings)
        tm.that(api.settings, eq=settings)
        tm.that(api.connected(), eq=False)
        tm.that(api.connection, none=True)

    def test_settings_fields_are_readable_through_public_property(
        self,
        api: FlextDbOracleApi,
    ) -> None:
        """Public settings expose the exact configured field values."""
        tm.that(api.settings.DbOracle.host, eq="127.0.0.1")
        tm.that(api.settings.DbOracle.port, eq=19999)
        tm.that(api.settings.DbOracle.service_name, eq="TEST")
        tm.that(api.settings.DbOracle.username, eq="test_user")

    def test_from_config_returns_configured_instance(
        self,
        settings: FlextDbOracleSettings,
    ) -> None:
        """from_config builds an independent API bound to the given settings."""
        api = FlextDbOracleApi.from_config(settings)
        tm.that(api, is_=FlextDbOracleApi)
        tm.that(api.settings, eq=settings)

    def test_valid_true_for_well_formed_settings(
        self,
        api: FlextDbOracleApi,
    ) -> None:
        """valid() is True when port and service name satisfy the contract."""
        tm.that(api.valid(), eq=True)

    def test_url_derived_service_name_is_uppercased(self) -> None:
        """from_url normalizes the parsed service name to upper case."""
        result = FlextDbOracleApi.from_url("oracle://user:pass@host:1521/service")
        tm.ok(result)
        api = result.value
        tm.that(api.settings.DbOracle.host, eq="host")
        tm.that(api.settings.DbOracle.port, eq=1521)
        tm.that(api.settings.DbOracle.service_name, eq="SERVICE")
        tm.that(api.settings.DbOracle.username, eq="user")

    @pytest.mark.parametrize("bad_url", ["invalid://not-oracle", "://x", "oracle://"])
    def test_from_url_rejects_malformed_urls(self, bad_url: str) -> None:
        """from_url yields a failure carrying an explanatory error for bad input."""
        result = FlextDbOracleApi.from_url(bad_url)
        tm.fail(result)
        tm.that(result.error, none=False)

    def test_from_env_missing_credentials_reports_required_password(self) -> None:
        """from_env fails clearly when no password is configured in the env."""
        result = FlextDbOracleApi.from_env("NONEXISTENT_PREFIX_")
        tm.fail(result)
        assert result.error is not None
        tm.that("password is required" in result.error, eq=True)

    # ----- serialization contract ----------------------------------------

    def test_to_dict_exposes_state_and_hides_password(
        self,
        api: FlextDbOracleApi,
    ) -> None:
        """to_dict reports settings/connected/plugin_count and never the password."""
        result = api.to_dict()
        tm.that("settings" in result, eq=True)
        tm.that("connected" in result, eq=True)
        tm.that("plugin_count" in result, eq=True)
        settings_dump = result["settings"]
        assert isinstance(settings_dump, dict)
        db_dump = settings_dump["DbOracle"]
        assert isinstance(db_dump, dict)
        tm.that("password" not in db_dump, eq=True)
        tm.that(db_dump["host"], eq="127.0.0.1")
        tm.that(result["connected"], eq=False)
        tm.that(result["plugin_count"], eq=0)

    def test_to_dict_plugin_count_tracks_registrations(
        self,
        api: FlextDbOracleApi,
    ) -> None:
        """plugin_count in to_dict reflects the number of registered plugins."""
        api.register_plugin("one", {"name": "one"})
        api.register_plugin("two", {"name": "two"})
        tm.that(api.to_dict()["plugin_count"], eq=2)

    def test_repr_reports_host_and_disconnected_status(
        self,
        api: FlextDbOracleApi,
    ) -> None:
        """Rendered repr shows the host and the current disconnected status."""
        tm.that(
            repr(api),
            eq="FlextDbOracleApi(host=127.0.0.1, status=disconnected)",
        )

    # ----- offline operation contract (no live database) -----------------

    @pytest.mark.parametrize(
        "operation",
        [
            "query",
            "query_one",
            "execute_sql",
            "fetch_schemas",
            "fetch_tables",
            "fetch_columns",
            "test_connection",
        ],
    )
    def test_operations_fail_gracefully_when_not_connected(
        self,
        api: FlextDbOracleApi,
        operation: str,
    ) -> None:
        """Every data operation returns a failure mentioning the missing connection."""

        def discard(_value: object) -> None:
            return None

        calls: Mapping[str, Callable[[], p.Result[None]]] = {
            "query": lambda: api.query("SELECT 1 FROM DUAL").map(discard),
            "query_one": lambda: api.query_one("SELECT 1 FROM DUAL").map(discard),
            "execute_sql": lambda: api.execute_sql(
                "CREATE TABLE t (id NUMBER)",
            ).map(discard),
            "fetch_schemas": lambda: api.fetch_schemas().map(discard),
            "fetch_tables": lambda: api.fetch_tables().map(discard),
            "fetch_columns": lambda: api.fetch_columns("test_table").map(discard),
            "test_connection": lambda: api.test_connection().map(discard),
        }
        result = calls[operation]()
        tm.fail(result)
        assert result.error is not None
        tm.that("connect" in result.error.lower(), eq=True)

    def test_disconnect_is_idempotent_when_never_connected(
        self,
        api: FlextDbOracleApi,
    ) -> None:
        """Disconnect on a fresh instance succeeds (no error) and is safe to repeat."""
        tm.ok(api.disconnect())
        tm.ok(api.disconnect())

    def test_transaction_reports_status_without_connection(
        self,
        api: FlextDbOracleApi,
    ) -> None:
        """transaction() succeeds and reports the disconnected transaction state."""
        result = api.transaction()
        tm.ok(result)
        tm.that(result.value["connected"], eq=False)
        tm.that(result.value["transaction_available"], eq=True)

    def test_context_manager_raises_when_connection_fails(
        self,
        api: FlextDbOracleApi,
    ) -> None:
        """Entering the context on an unreachable host raises RuntimeError."""
        with pytest.raises(RuntimeError):
            with api:
                pass

    def test_exit_without_enter_does_not_raise(
        self,
        api: FlextDbOracleApi,
    ) -> None:
        """__exit__ cleans up gracefully even if the connection was never opened."""
        api.__exit__(None, None, None)
        tm.that(api.connected(), eq=False)

    # ----- query optimization contract -----------------------------------

    @pytest.mark.parametrize(
        ("raw", "expected"),
        [
            ("  SELECT   *   FROM   test  ", "SELECT * FROM test"),
            ("SELECT\n\nid,\n\nname\n\nFROM\n\nusers", "SELECT id, name FROM users"),
            ("SELECT\t\t*\tFROM\t\temployees", "SELECT * FROM employees"),
            ("", ""),
            ("INVALID SQL SYNTAX HERE", "INVALID SQL SYNTAX HERE"),
        ],
    )
    def test_optimize_query_collapses_whitespace(
        self,
        api: FlextDbOracleApi,
        raw: str,
        expected: str,
    ) -> None:
        """optimize_query normalizes runs of whitespace to single spaces."""
        result = api.optimize_query(raw)
        tm.ok(result)
        tm.that(result.value, eq=expected)

    # ----- metrics contract ----------------------------------------------

    def test_observability_metrics_available_offline(
        self,
        api: FlextDbOracleApi,
    ) -> None:
        """fetch_observability_metrics returns a metrics mapping without a connection."""
        result = api.fetch_observability_metrics()
        tm.ok(result)
        tm.that(result.value, none=False)

    # ----- Singer mapping contract ---------------------------------------

    @pytest.mark.parametrize(
        "singer_type",
        ["string", "integer", "number", "boolean", "date-time"],
    )
    def test_convert_singer_type_yields_oracle_type(
        self,
        api: FlextDbOracleApi,
        singer_type: str,
    ) -> None:
        """convert_singer_type maps each Singer type to a non-empty Oracle type."""
        result = api.convert_singer_type(singer_type)
        tm.ok(result)
        tm.that(result.value, is_=str)
        tm.that(len(result.value) > 0, eq=True)

    def test_map_singer_schema_returns_mapping_for_valid_schema(
        self,
        api: FlextDbOracleApi,
    ) -> None:
        """map_singer_schema returns an Oracle column mapping for a valid schema."""
        schema: t.JsonMapping = {
            "type": "object",
            "properties": {
                "id": {"type": "integer"},
                "name": {"type": "string", "maxLength": 100},
            },
            "required": ["id", "name"],
        }
        result = api.map_singer_schema(schema)
        tm.ok(result)
        tm.that(result.value, is_=dict)

    # ----- plugin registry contract --------------------------------------

    def test_list_plugins_empty_by_default(self, api: FlextDbOracleApi) -> None:
        """A fresh API lists no plugins."""
        result = api.list_plugins()
        tm.ok(result)
        tm.that(result.value, empty=True)

    def test_plugin_register_fetch_list_unregister_roundtrip(
        self,
        api: FlextDbOracleApi,
    ) -> None:
        """Registering a plugin makes it fetchable and listed until unregistered."""
        plugin = {"name": "perf", "version": "1.0.0"}
        tm.ok(api.register_plugin("perf", plugin))

        fetched = api.fetch_plugin("perf")
        tm.ok(fetched)
        tm.that(fetched.value, eq=plugin)

        listed = api.list_plugins()
        tm.ok(listed)
        tm.that("perf" in listed.value, eq=True)

        tm.ok(api.unregister_plugin("perf"))
        tm.fail(api.fetch_plugin("perf"))

    def test_register_plugin_rejects_empty_name(
        self,
        api: FlextDbOracleApi,
    ) -> None:
        """register_plugin fails when the plugin name is blank."""
        result = api.register_plugin("", {"x": 1})
        tm.fail(result)
        assert result.error is not None
        tm.that("name is required" in result.error.lower(), eq=True)

    def test_fetch_missing_plugin_reports_not_found(
        self,
        api: FlextDbOracleApi,
    ) -> None:
        """fetch_plugin fails with a not-found error for an unknown plugin."""
        result = api.fetch_plugin("nonexistent_plugin")
        tm.fail(result)
        assert result.error is not None
        tm.that("not found" in result.error.lower(), eq=True)

    def test_unregister_missing_plugin_reports_not_found(
        self,
        api: FlextDbOracleApi,
    ) -> None:
        """unregister_plugin fails with a not-found error for an unknown plugin."""
        result = api.unregister_plugin("nonexistent_plugin")
        tm.fail(result)
        assert result.error is not None
        tm.that("not found" in result.error.lower(), eq=True)

    def test_instances_have_isolated_plugin_registries(self) -> None:
        """Plugins registered on one API instance never leak into another."""
        api_a = FlextDbOracleApi(self._settings("a", "A"))
        api_b = FlextDbOracleApi(self._settings("b", "B"))
        api_a.register_plugin("only_a", {"name": "only_a"})

        listed_a = api_a.list_plugins()
        listed_b = api_b.list_plugins()
        tm.ok(listed_a)
        tm.ok(listed_b)
        tm.that("only_a" in listed_a.value, eq=True)
        tm.that(listed_b.value, empty=True)

    # ----- services SQL builder contract (public collaborator) -----------

    @pytest.mark.parametrize(
        ("table_name", "columns"),
        [
            ("valid_table", ["col1"]),
            ("VALID_TABLE", ["col1", "col2"]),
            ("table123", ["a", "b", "c"]),
        ],
    )
    def test_build_select_emits_select_over_named_table_and_columns(
        self,
        settings: FlextDbOracleSettings,
        table_name: str,
        columns: list[str],
    ) -> None:
        """build_select produces a SELECT that references the table and columns."""
        services = FlextDbOracleServices(settings=settings)
        result = services.build_select(table_name, columns)
        tm.ok(result)
        sql_upper = result.value.upper()
        tm.that("SELECT" in sql_upper, eq=True)
        tm.that(table_name.upper() in sql_upper, eq=True)
        for column_name in columns:
            tm.that(column_name.lower() in result.value.lower(), eq=True)

    def test_build_select_qualifies_with_schema_when_provided(
        self,
        settings: FlextDbOracleSettings,
    ) -> None:
        """A schema-qualified build_select references both schema and table."""
        services = FlextDbOracleServices(settings=settings)
        result = services.build_select(
            "test_table",
            ["col1"],
            schema_name="test_schema",
        )
        tm.ok(result)
        sql_upper = result.value.upper()
        tm.that("TEST_SCHEMA" in sql_upper, eq=True)
        tm.that("TEST_TABLE" in sql_upper, eq=True)
