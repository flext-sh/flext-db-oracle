"""Behavioral unit tests for flext_db_oracle.protocols module.

These tests assert the OBSERVABLE public contract of the Oracle protocol
namespace: every ``FlextDbOracleProtocols.DbOracle.*`` member is a
``@runtime_checkable`` structural protocol, so an object is recognised as an
implementer iff it exposes the promised method surface. Contract is exercised
purely through ``isinstance`` (the public runtime-checkable behavior), never
through private attributes or implementation details.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from collections.abc import Mapping

import pytest

from flext_db_oracle import p
from flext_tests import tm
from tests import t

# (public name, protocol class, promised method surface) — the contract each
# Oracle domain protocol advertises to implementers.
_DB_ORACLE_CONTRACTS: tuple[t.Tests.ProtocolContract, ...] = (
    ("Connection", p.DbOracle.Connection, ("connect", "disconnect", "connected")),
    (
        "OraclePlugin",
        p.DbOracle.OraclePlugin,
        ("fetch_connection", "initialize", "shutdown", "test_connection"),
    ),
    (
        "QueryExecutor",
        p.DbOracle.QueryExecutor,
        ("execute_many", "execute_query", "execute_statement", "fetch_one"),
    ),
    (
        "SchemaIntrospector",
        p.DbOracle.SchemaIntrospector,
        (
            "fetch_columns",
            "fetch_primary_keys",
            "fetch_schemas",
            "fetch_table_metadata",
            "fetch_tables",
        ),
    ),
    (
        "SqlBuilder",
        p.DbOracle.SqlBuilder,
        (
            "build_delete_statement",
            "build_insert_statement",
            "build_select",
            "build_update_statement",
        ),
    ),
    (
        "DdlGenerator",
        p.DbOracle.DdlGenerator,
        ("build_create_index_statement", "create_table_ddl", "drop_table_ddl"),
    ),
    (
        "MetricsCollector",
        p.DbOracle.MetricsCollector,
        ("fetch_metrics", "record_metric", "track_operation"),
    ),
    (
        "PluginRegistry",
        p.DbOracle.PluginRegistry,
        ("fetch_plugin", "list_plugins", "register_plugin", "unregister_plugin"),
    ),
    (
        "HealthCheck",
        p.DbOracle.HealthCheck,
        ("fetch_connection_status", "health_check"),
    ),
)


def _stub(_self: object) -> None:
    """Method-surface stub used to synthesise protocol implementers."""


def _implementer(methods: tuple[str, ...]) -> object:
    """Build an object exposing exactly ``methods`` as callables."""
    namespace: Mapping[str, object] = dict.fromkeys(methods, _stub)
    cls = type("SyntheticImplementer", (), dict(namespace))
    return cls()


class TestsFlextDbOracleProtocols:
    """Contract behavior of the FlextDbOracleProtocols.DbOracle namespace."""

    def test_db_oracle_namespace_exposes_every_documented_protocol(self) -> None:
        """The public DbOracle namespace exposes exactly the promised protocols."""
        exposed = {name for name in dir(p.DbOracle) if not name.startswith("_")}
        promised = {name for name, _proto, _methods in _DB_ORACLE_CONTRACTS}

        assert promised <= exposed

    @pytest.mark.parametrize(
        ("name", "protocol", "methods"),
        _DB_ORACLE_CONTRACTS,
        ids=[name for name, _proto, _methods in _DB_ORACLE_CONTRACTS],
    )
    def test_protocol_is_runtime_checkable(
        self, name: str, protocol: type, methods: tuple[str, ...]
    ) -> None:
        """Each protocol supports isinstance() — its public runtime-check contract."""
        implementer = _implementer(methods)

        # A runtime-checkable protocol answers isinstance without raising.
        tm.that(implementer, is_=protocol)

    @pytest.mark.parametrize(
        ("name", "protocol", "methods"),
        _DB_ORACLE_CONTRACTS,
        ids=[name for name, _proto, _methods in _DB_ORACLE_CONTRACTS],
    )
    def test_full_method_surface_satisfies_protocol(
        self, name: str, protocol: type, methods: tuple[str, ...]
    ) -> None:
        """An object with the full promised surface is recognised as implementer."""
        implementer = _implementer(methods)

        tm.that(implementer, is_=protocol)

    @pytest.mark.parametrize(
        ("name", "protocol", "methods"),
        _DB_ORACLE_CONTRACTS,
        ids=[name for name, _proto, _methods in _DB_ORACLE_CONTRACTS],
    )
    def test_missing_any_single_method_breaks_conformance(
        self, name: str, protocol: type, methods: tuple[str, ...]
    ) -> None:
        """Dropping any one promised method makes the object a non-implementer."""
        for dropped in methods:
            partial = tuple(m for m in methods if m != dropped)
            implementer = _implementer(partial)

            assert not isinstance(implementer, protocol), f"{name}:{dropped}"

    def test_empty_object_conforms_to_no_db_oracle_protocol(self) -> None:
        """A bare object satisfies none of the Oracle protocols (structural gate)."""
        bare = object()

        for name, protocol, _methods in _DB_ORACLE_CONTRACTS:
            assert not isinstance(bare, protocol), name

    def test_foundation_result_protocol_inherited_from_flext_cli(self) -> None:
        """FlextDbOracleProtocols inherits foundation protocols (Result) from flext_cli."""
        assert hasattr(p, "Result")
