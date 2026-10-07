"""Shared state contract for the Oracle API facade runtime mixins.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_db_oracle import FlextDbOracleServiceBase, FlextDbOracleSettings, p, u
from flext_db_oracle.services.facade import FlextDbOracleServices


class FlextDbOracleApiRuntimeState(FlextDbOracleServiceBase):
    """Shared API facade state consumed by the focused runtime mixins."""

    _oracle_config: FlextDbOracleSettings = u.PrivateAttr()
    _services: FlextDbOracleServices = u.PrivateAttr()
    _context_name: str = u.PrivateAttr(default_factory=lambda: "oracle-api")
    _dispatcher: p.Dispatcher = u.PrivateAttr()


__all__: list[str] = ["FlextDbOracleApiRuntimeState"]
