"""Oracle Database protocols for FLEXT ecosystem.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from flext_cli import FlextCliProtocols

from flext_db_oracle._protocols import (
    connection_protocols as _connection_protocols,
    query_protocols as _query_protocols,
)


class FlextDbOracleProtocols(FlextCliProtocols):
    """Oracle database protocols extending FlextProtocols.

    Extends FlextProtocols to inherit all foundation protocols (Result, Service, etc.)
    and adds Oracle-specific protocols in the DbOracle namespace.

    Architecture:
    - EXTENDS: FlextProtocols (inherits Foundation, Domain, Application, etc.)
    - ADDS: Oracle-specific protocols in DbOracle namespace

    Usage:
    from flext_db_oracle import FlextDbOracleProtocols

    # Foundation protocols (inherited)
    result: FlextDbOracleProtocols.Result[str]
    service: FlextDbOracleProtocols.Service[str]

    # Oracle-specific protocols
    connection: FlextDbOracleProtocols.Database.Connection
    query: FlextDbOracleProtocols.Database.QueryExecutor
    """

    @runtime_checkable
    class DbOracle(Protocol):
        """Oracle database domain-specific protocols."""

        Connection = _connection_protocols.Connection
        OraclePlugin = _connection_protocols.OraclePlugin
        QueryExecutor = _query_protocols.QueryExecutor
        SchemaIntrospector = _query_protocols.SchemaIntrospector
        SqlBuilder = _query_protocols.SqlBuilder
        DdlGenerator = _query_protocols.DdlGenerator
        MetricsCollector = _query_protocols.MetricsCollector
        PluginRegistry = _connection_protocols.PluginRegistry
        HealthCheck = _connection_protocols.HealthCheck
        Runtime = _connection_protocols.Runtime


p = FlextDbOracleProtocols

__all__: list[str] = ["FlextDbOracleProtocols", "p"]
