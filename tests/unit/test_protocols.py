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

from typing import TYPE_CHECKING

from flext_db_oracle import FlextDbOracleSettings
from flext_db_oracle.services import FlextDbOracleServices
from tests import p, tm

if TYPE_CHECKING:
    from tests import t

# (public name, protocol class, promised method surface) — the contract each
# Oracle domain protocol advertises to implementers.
_DB_ORACLE_CONTRACTS: t.VariadicTuple[t.Tests.ProtocolContract] = (
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


class TestsFlextDbOracleProtocols:
    """Contract behavior of the FlextDbOracleProtocols.DbOracle namespace."""

    @staticmethod
    def test_db_oracle_namespace_exposes_every_documented_protocol() -> None:
        """The public DbOracle namespace exposes exactly the promised protocols."""
        exposed = {name for name in dir(p.DbOracle) if not name.startswith("_")}
        promised = {name for name, _proto, _methods in _DB_ORACLE_CONTRACTS}

        tm.ok(promised <= exposed)

    @staticmethod
    def test_real_services_satisfy_connection_contract() -> None:
        """The actual services expose disconnected connection behavior."""
        services = FlextDbOracleServices(FlextDbOracleSettings())
        tm.that(services, is_=p.DbOracle.Connection)
        tm.ok(services.connected() is False)
        tm.ok(services.disconnect())
        tm.ok(services.connected() is False)

    @staticmethod
    def test_real_services_satisfy_sql_builder_contract() -> None:
        """The actual SQL builder produces the requested identifiers."""
        services = FlextDbOracleServices(FlextDbOracleSettings())
        tm.that(services, is_=p.DbOracle.SqlBuilder)
        result = services.build_select("customers", ["customer_id"])
        tm.ok(result)
        tm.that(result.value.upper(), has="SELECT")
        tm.that(result.value.lower(), has="customers")
        tm.that(result.value.lower(), has="customer_id")

    @staticmethod
    def test_foundation_result_protocol_inherited_from_flext_cli() -> None:
        """FlextDbOracleProtocols inherits foundation protocols from flext_cli."""
        tm.ok(hasattr(p, "Result"))
