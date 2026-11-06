# AUTO-GENERATED FILE — Regenerate with: make gen
"""Flext Db Oracle. Typings package.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from flext_core.lazy import install_lazy_exports

if TYPE_CHECKING:
    from flext_db_oracle._typings.base import FlextDbOracleTypingsBase
    from flext_db_oracle._typings.db_oracle import FlextDbOracleTypesDbOracle


__all__: tuple[str, ...] = ("FlextDbOracleTypesDbOracle", "FlextDbOracleTypingsBase")

install_lazy_exports(
    __name__,
    globals(),
    {"FlextDbOracleTypesDbOracle": ".db_oracle", "FlextDbOracleTypingsBase": ".base"},
    public_exports=__all__,
)
