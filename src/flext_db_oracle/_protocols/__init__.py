# AUTO-GENERATED FILE — Regenerate with: make gen
"""Flext Db Oracle. Protocols package.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from types import MappingProxyType
from typing import TYPE_CHECKING

from flext_core import install_lazy_exports

if TYPE_CHECKING:
    from flext_db_oracle._protocols.base import FlextDbOracleProtocolsBase


__all__: tuple[str, ...] = ("FlextDbOracleProtocolsBase",)

install_lazy_exports(
    __name__,
    globals(),
    MappingProxyType({"FlextDbOracleProtocolsBase": ".base"}),
    public_exports=__all__,
)
