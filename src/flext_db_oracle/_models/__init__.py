# AUTO-GENERATED FILE — Regenerate with: make gen
"""Flext Db Oracle. Models package.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from types import MappingProxyType
from typing import TYPE_CHECKING

from flext_core import install_lazy_exports

if TYPE_CHECKING:
    from flext_db_oracle._models.base import FlextDbOracleModelsBase
    from flext_db_oracle._models.password import FlextDbOraclePassword


__all__: tuple[str, ...] = ("FlextDbOracleModelsBase", "FlextDbOraclePassword")

install_lazy_exports(
    __name__,
    globals(),
    MappingProxyType({
        "FlextDbOracleModelsBase": ".base",
        "FlextDbOraclePassword": ".password",
    }),
    public_exports=__all__,
)
