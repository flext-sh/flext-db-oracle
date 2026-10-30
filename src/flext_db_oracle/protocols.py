# AUTO-GENERATED FILE — Regenerate with: make gen
"""Oracle Database protocols for FLEXT ecosystem.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_cli import p

from flext_db_oracle._protocols import (
    FlextDbOracleProtocolsConnection,
    FlextDbOracleProtocolsQuery,
)


class FlextDbOracleProtocols(p):
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

    class DbOracle(FlextDbOracleProtocolsConnection, FlextDbOracleProtocolsQuery):
        """Oracle database domain-specific protocols."""


p = FlextDbOracleProtocols
__all__: list[str] = ["FlextDbOracleProtocols", "p"]
