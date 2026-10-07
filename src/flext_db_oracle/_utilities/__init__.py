# AUTO-GENERATED FILE — Regenerate with: make gen
"""Flext Db Oracle. Utilities package.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from types import MappingProxyType
from typing import TYPE_CHECKING

from flext_core import install_lazy_exports

if TYPE_CHECKING:
    from flext_db_oracle._utilities.base import FlextDbOracleUtilitiesBase
    from flext_db_oracle._utilities.db_oracle import FlextDbOracleUtilitiesDbOracle


__all__: tuple[str, ...] = (
    "FlextDbOracleUtilitiesBase",
    "FlextDbOracleUtilitiesDbOracle",
)

install_lazy_exports(
    __name__,
    globals(),
    MappingProxyType({
        "FlextDbOracleUtilitiesBase": ".base",
        "FlextDbOracleUtilitiesDbOracle": ".db_oracle",
    }),
    public_exports=__all__,
)
