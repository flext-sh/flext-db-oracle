# AUTO-GENERATED FILE — Regenerate with: make gen
"""Examples package."""

from __future__ import annotations

from types import MappingProxyType
from typing import TYPE_CHECKING

from flext_core.lazy import build_lazy_import_map, install_lazy_exports

if TYPE_CHECKING:
    from flext_core import d, h, r, x
    from flext_db_oracle import c, e, m, p, s, t, u


__all__: tuple[str, ...] = ("c", "d", "e", "h", "m", "p", "r", "s", "t", "u", "x")

_LAZY_IMPORTS = MappingProxyType(
    build_lazy_import_map(
        MappingProxyType({
            "flext_core": ("d", "h", "r", "x"),
            "flext_db_oracle": ("c", "e", "m", "p", "s", "t", "u"),
        }),
        alias_groups=MappingProxyType({}),
        sort_keys=False,
    )
)

install_lazy_exports(__name__, globals(), _LAZY_IMPORTS, public_exports=__all__)
