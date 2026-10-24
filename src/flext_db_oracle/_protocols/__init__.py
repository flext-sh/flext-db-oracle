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
        FlextDbOracleProtocolsConnection,
    )
    from flext_db_oracle._protocols.query_protocols import FlextDbOracleProtocolsQuery


__all__: tuple[str, ...] = (
    "FlextDbOracleProtocolsBase",
    "FlextDbOracleProtocolsConnection",
    "FlextDbOracleProtocolsQuery",
)

install_lazy_exports(
    __name__,
    globals(),
    MappingProxyType({
        "FlextDbOracleProtocolsBase": ".base",
        "FlextDbOracleProtocolsConnection": ".connection_protocols",
        "FlextDbOracleProtocolsQuery": ".query_protocols",
    }),
    public_exports=__all__,
)
