"""Shared state contract for the Oracle API facade runtime mixins.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_db_oracle import FlextDbOracleServiceBase, FlextDbOracleSettings, m, p
from flext_db_oracle.services import FlextDbOracleServices


class FlextDbOracleApiRuntimeState(FlextDbOracleServiceBase):
    """Shared API facade state consumed by the focused runtime mixins."""

    _oracle_config: FlextDbOracleSettings = m.PrivateAttr()
    _services: FlextDbOracleServices = m.PrivateAttr()
    _context_name: str = m.PrivateAttr(default_factory=lambda: "oracle-api")
    _dispatcher: p.Dispatcher = m.PrivateAttr()


__all__: list[str] = ["FlextDbOracleApiRuntimeState"]
