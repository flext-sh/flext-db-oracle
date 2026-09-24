# AUTO-GENERATED FILE — Regenerate with: make gen
"""Examples package."""

from __future__ import annotations

from types import MappingProxyType
from typing import TYPE_CHECKING

from flext_core.lazy import build_lazy_import_map, install_lazy_exports

if TYPE_CHECKING:
<<<<<<< HEAD
    from flext_core import (
        core,
        d,
        h,
        lazy,
        lazy_attribute,
        normalize_lazy_imports,
        r,
        x,
    )
    from flext_db_oracle import c, config, db_oracle, e, m, main, p, s, settings, t, u


__all__: tuple[str, ...] = (
    "c",
    "config",
    "core",
    "d",
    "db_oracle",
    "e",
    "h",
    "lazy",
    "lazy_attribute",
    "m",
    "main",
    "normalize_lazy_imports",
    "p",
    "r",
    "s",
    "settings",
    "t",
    "u",
    "x",
)
=======
    from flext_db_oracle import c, d, e, h, m, p, r, s, t, u, x


__all__: tuple[str, ...] = ("c", "d", "e", "h", "m", "p", "r", "s", "t", "u", "x")
>>>>>>> recovery/rope-automation-20260921

_LAZY_IMPORTS = MappingProxyType(
    build_lazy_import_map(
        MappingProxyType({
<<<<<<< HEAD
            "flext_core": (
                "core",
                "d",
                "h",
                "lazy",
                "lazy_attribute",
                "normalize_lazy_imports",
                "r",
                "x",
            ),
            "flext_db_oracle": (
                "c",
                "config",
                "db_oracle",
                "e",
                "m",
                "main",
                "p",
                "s",
                "settings",
                "t",
                "u",
            ),
=======
            "flext_db_oracle": ("c", "d", "e", "h", "m", "p", "r", "s", "t", "u", "x")
>>>>>>> recovery/rope-automation-20260921
        }),
        alias_groups=MappingProxyType({}),
        sort_keys=False,
    )
)

install_lazy_exports(__name__, globals(), _LAZY_IMPORTS, public_exports=__all__)
