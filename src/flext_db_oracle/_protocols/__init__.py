# AUTO-GENERATED FILE — Regenerate with: make gen
"""Flext Db Oracle. Protocols package.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from types import MappingProxyType
from typing import TYPE_CHECKING

from flext_core.lazy import install_lazy_exports

if TYPE_CHECKING:
    from flext_db_oracle._protocols.base import FlextDbOracleProtocolsBase
    from flext_db_oracle._protocols.connection_protocols import (
        Connection,
        FlextDbOracleProtocolsConnection,
        HealthCheck,
        OraclePlugin,
        PluginRegistry,
        Runtime,
    )
    from flext_db_oracle._protocols.query_protocols import (
        DdlGenerator,
        FlextDbOracleProtocolsQuery,
        MetricsCollector,
        QueryExecutor,
        SchemaIntrospector,
        SqlBuilder,
    )


__all__: tuple[str, ...] = (
    "Connection",
    "DdlGenerator",
    "FlextDbOracleProtocolsBase",
    "FlextDbOracleProtocolsConnection",
    "FlextDbOracleProtocolsQuery",
    "HealthCheck",
    "MetricsCollector",
    "OraclePlugin",
    "PluginRegistry",
    "QueryExecutor",
    "Runtime",
    "SchemaIntrospector",
    "SqlBuilder",
)

install_lazy_exports(
    __name__,
    globals(),
    MappingProxyType({
        "Connection": ".connection_protocols",
        "DdlGenerator": ".query_protocols",
        "FlextDbOracleProtocolsBase": ".base",
        "FlextDbOracleProtocolsConnection": ".connection_protocols",
        "FlextDbOracleProtocolsQuery": ".query_protocols",
        "HealthCheck": ".connection_protocols",
        "MetricsCollector": ".query_protocols",
        "OraclePlugin": ".connection_protocols",
        "PluginRegistry": ".connection_protocols",
        "QueryExecutor": ".query_protocols",
        "Runtime": ".connection_protocols",
        "SchemaIntrospector": ".query_protocols",
        "SqlBuilder": ".query_protocols",
    }),
    public_exports=__all__,
)
