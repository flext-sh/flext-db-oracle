"""Behavioral tests for FlextDbOracleClient public contract.

These tests assert observable behavior of the client's public API only:
return values, r[T] success/failure outcomes, error messages, and public
model state. No private attributes, internal collaborators, or line-coverage
pokes are exercised.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from collections.abc import Mapping

import pytest
from flext_tests import tm

from flext_db_oracle import c, m, u
from flext_db_oracle.client import FlextDbOracleClient


class TestsFlextDbOracleClient:
    """Behavioral contract tests for the Oracle client public surface."""

    @staticmethod
    @pytest.fixture
    def client() -> FlextDbOracleClient:
        """Provide a default, unconnected client instance.

        Returns:
            The resulting ``FlextDbOracleClient``.
        """
        return FlextDbOracleClient()

    # -- construction ------------------------------------------------------

    @staticmethod
    def test_default_client_reports_debug_disabled() -> None:
        """A client built without arguments exposes debug=False."""
        client = FlextDbOracleClient()
        tm.that(client.debug, eq=False)

    @staticmethod
    def test_client_honors_debug_flag() -> None:
        """The debug flag passed at construction is reflected publicly."""
        client = FlextDbOracleClient(debug=True)
        tm.that(client.debug, eq=True)

    @staticmethod
    def test_new_client_is_not_connected(client: FlextDbOracleClient) -> None:
        """A freshly built client has no active engine."""
        tm.that(client.connected(), eq=False)

    @staticmethod
    def test_default_preferences_are_populated(
        client: FlextDbOracleClient,
    ) -> None:
        """Default user preferences expose the documented output format key."""
        tm.that(client.user_preferences.root["default_output_format"], eq="table")

    # -- escape_oracle_identifier -----------------------------------------

    @staticmethod
    @pytest.mark.parametrize(
        ("identifier", "expected"),
        [("valid_name", "valid_name"), ("Table1", "Table1"), ("COL_A_1", "COL_A_1")],
    )
    def test_escape_identifier_accepts_valid_names(
        identifier: str,
        expected: str,
    ) -> None:
        """Valid identifiers are returned unchanged in a success result."""
        result = u.DbOracle.escape_oracle_identifier(identifier)
        tm.that(result.success, eq=True)
        tm.that(result.unwrap(), eq=expected)

    @staticmethod
    @pytest.mark.parametrize(
        ("identifier", "error"),
        [
            ("", "Empty Oracle identifier"),
            ("   ", "Empty Oracle identifier"),
            ("a b", "Invalid Oracle identifier"),
            ("bad!", "Invalid Oracle identifier"),
            ("dash-name", "Invalid Oracle identifier"),
        ],
    )
    def test_escape_identifier_rejects_bad_names(
        identifier: str,
        error: str,
    ) -> None:
        """Blank or non-alphanumeric identifiers fail with a specific error."""
        result = u.DbOracle.escape_oracle_identifier(identifier)
        tm.that(result.success, eq=False)
        tm.that(result.error, eq=error)

    @staticmethod
    def test_escape_identifier_truncates_to_max_length() -> None:
        """Over-long identifiers are truncated to the Oracle maximum length."""
        long_identifier = "a" * (c.DbOracle.MAX_IDENTIFIER_LENGTH + 50)
        result = u.DbOracle.escape_oracle_identifier(long_identifier)
        tm.that(result.success, eq=True)
        tm.that(len(result.unwrap()), eq=c.DbOracle.MAX_IDENTIFIER_LENGTH)

    # -- validate_identifier ----------------------------------------------

    @staticmethod
    @pytest.mark.parametrize("identifier", ["my_col", "employees", "T1"])
    def test_validate_identifier_accepts_normal_names(identifier: str) -> None:
        """Ordinary identifiers validate successfully to True."""
        result = u.DbOracle.validate_identifier(identifier)
        tm.that(result.success, eq=True)
        tm.that(result.unwrap(), eq=True)

    @staticmethod
    @pytest.mark.parametrize(
        ("identifier", "error"),
        [
            ("", "Empty Oracle identifier"),
            ("SELECT", "Oracle identifier is reserved word"),
            ("from", "Oracle identifier is reserved word"),
        ],
    )
    def test_validate_identifier_rejects_empty_and_reserved(
        identifier: str,
        error: str,
    ) -> None:
        """Empty or reserved-word identifiers fail with the matching error."""
        result = u.DbOracle.validate_identifier(identifier)
        tm.that(result.success, eq=False)
        tm.that(result.error, eq=error)

    @staticmethod
    def test_validate_identifier_rejects_too_long() -> None:
        """Identifiers exceeding the maximum length are rejected."""
        too_long = "x" * (c.DbOracle.MAX_IDENTIFIER_LENGTH + 1)
        result = u.DbOracle.validate_identifier(too_long)
        tm.that(result.success, eq=False)
        tm.that(result.error, eq="Oracle identifier too long")

    # -- format_sql_for_oracle --------------------------------------------

    @staticmethod
    @pytest.mark.parametrize(
        ("raw", "expected"),
        [
            ("SELECT   1  FROM dual", "SELECT 1 FROM dual"),
            ("  SELECT *\n  FROM t ", "SELECT * FROM t"),
            ("A\tB", "A B"),
        ],
    )
    def test_format_sql_collapses_whitespace(raw: str, expected: str) -> None:
        """SQL formatting normalizes all runs of whitespace to single spaces."""
        result = u.DbOracle.format_sql_for_oracle(raw)
        tm.that(result.success, eq=True)
        tm.that(result.unwrap(), eq=expected)

    # -- generate_query_hash ----------------------------------------------

    @staticmethod
    def test_query_hash_is_short_hex_digest() -> None:
        """A generated hash is a 16-character hexadecimal string."""
        result = u.DbOracle.generate_query_hash("SELECT 1", None)
        digest = result.unwrap()
        tm.that(result.success, eq=True)
        tm.that(len(digest), eq=16)
        assert int(digest, 16) >= 0

    @staticmethod
    def test_query_hash_is_deterministic() -> None:
        """The same query and params always produce the same hash."""
        first = u.DbOracle.generate_query_hash("SELECT 1", None)
        second = u.DbOracle.generate_query_hash("SELECT 1", None)
        tm.that(first.unwrap(), eq=second.unwrap())

    @staticmethod
    def test_query_hash_varies_with_query() -> None:
        """Different queries produce different hashes."""
        a = u.DbOracle.generate_query_hash("SELECT 1", None)
        b = u.DbOracle.generate_query_hash("SELECT 2", None)
        tm.that(a.unwrap(), ne=b.unwrap())

    @staticmethod
    def test_query_hash_is_order_independent_for_params() -> None:
        """Parameter ordering does not change the resulting hash."""
        a = u.DbOracle.generate_query_hash("Q", {"a": 1, "b": 2})
        b = u.DbOracle.generate_query_hash("Q", {"b": 2, "a": 1})
        tm.that(a.unwrap(), eq=b.unwrap())

    # -- format_query_result ----------------------------------------------

    @staticmethod
    def test_format_result_json_emits_json_text() -> None:
        """JSON formatting yields parseable JSON for the payload."""
        result = u.DbOracle.format_query_result({"a": 1}, "json")
        tm.that(result.success, eq=True)
        tm.that(result.unwrap(), eq='{"a":1}')

    @staticmethod
    def test_format_result_table_emits_string_repr() -> None:
        """Default (table) formatting yields the string form of the payload."""
        payload: Mapping[str, int] = {"a": 1}
        result = u.DbOracle.format_query_result(payload)
        tm.that(result.success, eq=True)
        tm.that(result.unwrap(), eq=str(payload))

    # -- normalize_params -------------------------------------------------

    @staticmethod
    def test_normalize_params_returns_empty_map_for_none() -> None:
        """None params normalize to an empty ConfigMap."""
        normalized = u.DbOracle.normalize_params(None)
        tm.that(normalized.root, eq={})

    @staticmethod
    def test_normalize_params_passes_through_existing_map() -> None:
        """A provided ConfigMap is returned unchanged."""
        provided = m.ConfigMap(root={"query_limit": "10"})
        normalized = u.DbOracle.normalize_params(provided)
        tm.that(normalized.root, eq={"query_limit": "10"})

    # -- configure_preferences --------------------------------------------

    @staticmethod
    def test_configure_preferences_records_new_keys(
        client: FlextDbOracleClient,
    ) -> None:
        """Configuring preferences succeeds and updates public state."""
        result = client.configure_preferences(theme="dark", page_size=50)
        tm.that(result.success, eq=True)
        tm.that(result.unwrap(), eq=True)
        tm.that(client.user_preferences.root["theme"], eq="dark")
        tm.that(client.user_preferences.root["page_size"], eq=50)

    @staticmethod
    def test_configure_preferences_preserves_defaults(
        client: FlextDbOracleClient,
    ) -> None:
        """Updating preferences leaves untouched default keys intact."""
        client.configure_preferences(theme="light")
        tm.that(client.user_preferences.root["default_output_format"], eq="table")

    # -- run_cli_command --------------------------------------------------

    @staticmethod
    def test_run_cli_command_rejects_unknown_operation(
        client: FlextDbOracleClient,
    ) -> None:
        """An unknown CLI operation fails with a descriptive error."""
        result = client.run_cli_command("bogus")
        tm.that(result.success, eq=False)
        tm.that(result.error, eq="Unknown CLI operation: bogus")
