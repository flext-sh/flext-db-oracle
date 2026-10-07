# AUTO-GENERATED FILE — Regenerate with: make gen
"""Flext Db Oracle. Typings package.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from types import MappingProxyType
from typing import TYPE_CHECKING

from flext_core import install_lazy_exports

if TYPE_CHECKING:
    from flext_db_oracle._typings.base import FlextDbOracleTypingsBase


__all__: tuple[str, ...] = ("FlextDbOracleTypingsBase",)

install_lazy_exports(
    __name__,
    globals(),
    MappingProxyType({"FlextDbOracleTypingsBase": ".base"}),
    public_exports=__all__,
)
