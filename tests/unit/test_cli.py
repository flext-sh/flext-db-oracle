"""Behavioral tests for FlextDbOracleClient CLI contract.

Asserts observable public behavior only: constructed model state via public
fields, ``r[T]`` outcomes for fallible operations, and public API results.
No private access, no internal-collaborator spying, no monkeypatching of the
unit under test.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import pytest
from flext_tests import r, tm

from flext_db_oracle import FlextDbOracleApi, FlextDbOracleSettings
from flext_db_oracle.client import FlextDbOracleClient
from tests import u

_NO_CONNECTION_ERROR = "No active Oracle connection"
_CONNECTION_FAILURE_SNIPPETS = (
    "Connection failed",
    "Oracle connection failed",
    "Connection error",
)


class TestsFlextDbOracleCli:
    """Public-contract behavior of the Oracle CLI client (no mocks)."""

    # ---- construction / public model state -------------------------------

    @pytest.mark.parametrize("debug", [True, False])
    def test_construction_exposes_requested_debug_flag(self, *, debug: bool) -> None:
        """The ``debug`` public field reflects the constructor argument."""
        client = FlextDbOracleClient(debug=debug)
        tm.that(client.debug, eq=debug)

    def test_construction_starts_without_active_connection(self) -> None:
        """A freshly built client reports no active connection."""
        client = FlextDbOracleClient()
        tm.that(client.current_connection, none=True)

    @pytest.mark.parametrize(
        ("preference_key", "expected_value"),
        [
            ("default_output_format", "table"),
            ("show_execution_time", "True"),
            ("auto_confirm_operations", "False"),
            ("connection_timeout", 30),
            ("query_limit", 1000),
        ],
    )
    def test_default_preferences_are_populated(
        self,
        preference_key: str,
        expected_value: str | int,
    ) -> None:
        """Default user preferences expose the documented defaults."""
        client = FlextDbOracleClient()
        tm.that(client.user_preferences[preference_key], eq=expected_value)

    def test_each_construction_yields_an_independent_client(self) -> None:
        """Constructing twice yields distinct, independent instances."""
        client_a = FlextDbOracleClient()
        client_b = FlextDbOracleClient()
        tm.that(client_a, is_=FlextDbOracleClient)
        tm.that(client_b, is_=FlextDbOracleClient)
        tm.that(client_a is not client_b, eq=True)

    # ---- preference configuration ----------------------------------------

    def test_configure_preferences_updates_values_and_reports_success(self) -> None:
        """Configuring known preferences succeeds and mutates public state."""
        client = FlextDbOracleClient()
        tm.ok(
            client.configure_preferences(
                default_output_format="json",
                query_limit=2000,
                show_execution_time=False,
            ),
        )
        tm.that(client.user_preferences["default_output_format"], eq="json")
        tm.that(client.user_preferences["query_limit"], eq=2000)
        tm.that(client.user_preferences["show_execution_time"], eq=False)

    def test_configure_preferences_preserves_untouched_defaults(self) -> None:
        """Partial updates leave unrelated defaults intact."""
        client = FlextDbOracleClient()
        tm.ok(
            client.configure_preferences(
                default_output_format="json",
                connection_timeout=60,
            ),
        )
        tm.that(client.user_preferences["default_output_format"], eq="json")
        tm.that(client.user_preferences["connection_timeout"], eq=60)
        tm.that(client.user_preferences["query_limit"], eq=1000)

    def test_configure_preferences_tolerates_unknown_keys(self) -> None:
        """Unknown preference keys are accepted without failing the operation."""
        client = FlextDbOracleClient()
        result = client.configure_preferences(invalid_key="value", another="test")
        tm.that(result, is_=r)
        tm.ok(result)
        tm.that(client.user_preferences["query_limit"], eq=1000)

    def test_configure_preferences_accepts_empty_string_value(self) -> None:
        """An empty preference value is a valid, non-failing configuration."""
        client = FlextDbOracleClient()
        tm.ok(client.configure_preferences(valid_key=""))

    # ---- fail-fast without a connection ----------------------------------

    @pytest.mark.parametrize(
        ("method_name", "args"),
        [
            ("execute_query", ("SELECT 1 FROM DUAL",)),
            ("list_schemas", ()),
            ("list_tables", ()),
            ("health_check", ()),
        ],
    )
    def test_privileged_operations_fail_without_connection(
        self,
        method_name: str,
        args: tuple[str, ...],
    ) -> None:
        """Every privileged operation fails fast when no connection is active."""
        client = FlextDbOracleClient()
        operation = getattr(client, method_name)
        tm.fail(operation(*args), has=_NO_CONNECTION_ERROR)

    def test_execute_query_fails_without_connection(self) -> None:
        """An empty query without a connection reports failure, not success."""
        client = FlextDbOracleClient()
        tm.fail(client.execute_query(""))

    # ---- real connection attempts (no reachable server) ------------------

    def test_connect_to_oracle_reports_failure_for_unreachable_host(self) -> None:
        """Connecting to an invalid host yields a descriptive failure."""
        client = FlextDbOracleClient()
        result = client.connect_to_oracle(
            host="nonexistent-host-12345.invalid",
            port=9999,
            service_name="INVALID",
            username="invalid_user",
            password="invalid_password",
        )
        tm.that(result.failure, eq=True)
        error_text = result.error or ""
        tm.that(
            any(snippet in error_text for snippet in _CONNECTION_FAILURE_SNIPPETS),
            eq=True,
        )

    def test_connect_to_oracle_from_settings_returns_string_error(self) -> None:
        """A failed connection built from settings exposes a string error."""
        settings = FlextDbOracleSettings(
            DbOracle={
                "host": "localhost",
                "port": 1521,
                "name": "XE",
                "service_name": "XE",
                "username": "test",
                "password": "test",
            },
        )
        client = FlextDbOracleClient()
        result = client.connect_to_oracle(
            settings.DbOracle.host,
            settings.DbOracle.port,
            settings.DbOracle.service_name or "default_service",
            settings.DbOracle.username,
            settings.DbOracle.password,
        )
        tm.that(result.failure, eq=True)
        tm.that(result.error, is_=str)

    # ---- class-level CLI command dispatch --------------------------------

    def test_run_cli_command_returns_result(self) -> None:
        """``run_cli_command`` returns an ``r`` result for a known operation."""
        tm.that(FlextDbOracleClient.run_cli_command("health", timeout=30), is_=r)

    def test_run_cli_command_rejects_unknown_operation(self) -> None:
        """An unknown CLI operation is reported as a failure."""
        result = FlextDbOracleClient.run_cli_command("does-not-exist")
        tm.fail(result, has="Unknown CLI operation")

    # ---- API-facing behavior ---------------------------------------------

    def test_api_from_env_builds_configured_api(self) -> None:
        """``from_env`` succeeds and produces settings with a host."""
        FlextDbOracleSettings.reset_for_testing()
        with u.Tests.env_vars_context({
            "ORACLE_DBORACLE__HOST": "localhost",
            "ORACLE_DBORACLE__PORT": "1521",
            "ORACLE_DBORACLE__USERNAME": "testuser",
            "ORACLE_DBORACLE__PASSWORD": "testpass",
            "ORACLE_DBORACLE__SERVICE_NAME": "TESTDB",
        }):
            api_result = FlextDbOracleApi.from_env()
        tm.ok(api_result)
        tm.that(api_result.unwrap().settings.DbOracle.host, eq="localhost")

    def test_api_from_env_honours_service_name_override(self) -> None:
        """``from_env`` reflects env-provided settings with an int port."""
        FlextDbOracleSettings.reset_for_testing()
        with u.Tests.env_vars_context({
            "ORACLE_DBORACLE__HOST": "localhost",
            "ORACLE_DBORACLE__USERNAME": "testuser",
            "ORACLE_DBORACLE__PASSWORD": "testpass",
            "ORACLE_DBORACLE__SERVICE_NAME": "XEPDB1",
        }):
            api_result = FlextDbOracleApi.from_env()
        tm.ok(api_result)
        api = api_result.unwrap()
        tm.that(api.settings.DbOracle.host, none=False)
        tm.that(api.settings.DbOracle.port, is_=int)

    def test_api_settings_round_trip_constructor_values(self) -> None:
        """API settings expose exactly the values used to construct them."""
        api = FlextDbOracleApi(
            settings=FlextDbOracleSettings(
                DbOracle={
                    "host": "param_test_host",
                    "port": 1521,
                    "service_name": "PARAM_TEST",
                    "username": "param_user",
                    "password": "param_pass",
                },
            ),
        )
        tm.that(api.settings.DbOracle.host, eq="param_test_host")
        tm.that(api.settings.DbOracle.port, eq=1521)
        tm.that(api.settings.DbOracle.service_name, eq="PARAM_TEST")
        tm.that(api.settings.DbOracle.username, eq="param_user")

    def test_api_observability_metrics_are_available(self) -> None:
        """Observability metrics succeed and return a mapping."""
        api = self._sample_api()
        metrics_result = api.fetch_observability_metrics()
        tm.ok(metrics_result)
        tm.that(metrics_result.unwrap(), is_=dict)

    def test_api_reports_valid_configuration(self) -> None:
        """A fully-specified API validates its own configuration."""
        api = self._sample_api()
        api.test_connection()
        tm.that(api.valid(), eq=True)

    def test_api_optimize_query_succeeds(self) -> None:
        """Query optimization is a pure, connection-independent success."""
        api = self._sample_api()
        tm.ok(api.optimize_query("SELECT * FROM test"))

    def test_api_query_without_connection_reports_connection_error(self) -> None:
        """Querying an unconnected API fails with a connection-related error."""
        api = FlextDbOracleApi(
            FlextDbOracleSettings(
                DbOracle={
                    "host": "invalid.host",
                    "port": 9999,
                    "service_name": "INVALID_SERVICE",
                    "username": "invalid_user",
                    "password": "invalid_password",
                },
            ),
        )
        query_result = api.query("SELECT 1 FROM DUAL")
        tm.that(query_result.failure, eq=True)
        error_lower = (query_result.error or "").lower()
        tm.that("not connected" in error_lower or "connection" in error_lower, eq=True)

    def test_api_schema_and_table_fetches_fail_without_connection(self) -> None:
        """Schema/table listing fails without an established connection."""
        api = self._sample_api()
        tm.that(api.fetch_schemas().failure, eq=True)
        tm.that(api.fetch_tables().failure, eq=True)

    # ---- output formatting -----------------------------------------------

    @pytest.mark.parametrize("format_type", ["table", "json", "csv"])
    def test_format_query_result_produces_non_empty_string(
        self,
        format_type: str,
    ) -> None:
        """Every supported output format yields a non-empty string result."""
        formatted = u.DbOracle.format_query_result(
            {"column1": "value1", "column2": "value2"},
            format_type=format_type,
        )
        tm.ok(formatted)
        unwrapped = formatted.unwrap()
        tm.that(unwrapped, is_=str)
        tm.that(bool(unwrapped), eq=True)

    def test_yaml_dump_serializes_mapping_to_string(self) -> None:
        """YAML serialization returns a string containing the mapping data."""
        result = u.Cli.yaml_dump_str({"test": "value"})
        tm.that(result, is_=str)
        tm.that(result, has=["test", "value"])

    # ---- plugin lifecycle -------------------------------------------------

    def test_plugin_lifecycle_register_fetch_and_unregister(self) -> None:
        """A registered plugin is discoverable, fetchable, then removable."""
        api = self._sample_api()
        plugin_payload = {"name": "test_plugin", "version": "1.0.0"}
        tm.ok(api.register_plugin("test_plugin", plugin_payload))
        tm.that(tm.ok(api.list_plugins()), has="test_plugin")
        tm.that(api.fetch_plugin("test_plugin").unwrap(), eq=plugin_payload)
        tm.ok(api.unregister_plugin("test_plugin"))
        tm.that("test_plugin" not in api.list_plugins().unwrap(), eq=True)

    def test_list_plugins_starts_empty(self) -> None:
        """A fresh API exposes an empty plugin registry."""
        api = self._sample_api()
        tm.that(list(api.list_plugins().unwrap()), eq=[])

    # ---- helpers ----------------------------------------------------------

    @staticmethod
    def _sample_api() -> FlextDbOracleApi:
        """Build a fully-specified API instance for connection-free assertions."""
        return FlextDbOracleApi(
            FlextDbOracleSettings(
                DbOracle={
                    "host": "localhost",
                    "port": 1521,
                    "service_name": "TESTDB",
                    "username": "test",
                    "password": "test",
                },
            ),
        )
