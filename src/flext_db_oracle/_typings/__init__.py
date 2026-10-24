# AUTO-GENERATED FILE — Regenerate with: make gen
"""Flext Db Oracle. Typings package.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from types import MappingProxyType
from typing import TYPE_CHECKING

from flext_core.lazy import install_lazy_exports

if TYPE_CHECKING:
    from flext_db_oracle._typings.base import FlextDbOracleTypingsBase
    from flext_db_oracle._typings.db_oracle import FlextDbOracleTypes, t


__all__: tuple[str, ...] = ("FlextDbOracleTypes", "FlextDbOracleTypingsBase", "t")

install_lazy_exports(
    __name__,
    globals(),
    MappingProxyType({
        "FlextDbOracleTypes": ".db_oracle",
        "FlextDbOracleTypingsBase": ".base",
        "t": ".db_oracle",
    }),
    public_exports=__all__,
)
