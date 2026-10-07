# AUTO-GENERATED FILE — Regenerate with: make gen
"""Examples package.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from types import MappingProxyType
from typing import TYPE_CHECKING

from flext_core import install_lazy_exports

if TYPE_CHECKING:
    from flext_core import d, h, r, x
    from flext_db_oracle import c, e, m, p, s, t, u


__all__: tuple[str, ...] = ("c", "d", "e", "h", "m", "p", "r", "s", "t", "u", "x")

install_lazy_exports(
    __name__,
    globals(),
    MappingProxyType({
        "c": "flext_db_oracle",
        "d": "flext_core",
        "e": "flext_db_oracle",
        "h": "flext_core",
        "m": "flext_db_oracle",
        "p": "flext_db_oracle",
        "r": "flext_core",
        "s": "flext_db_oracle",
        "t": "flext_db_oracle",
        "u": "flext_db_oracle",
        "x": "flext_core",
    }),
    public_exports=__all__,
)
