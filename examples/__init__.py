# AUTO-GENERATED FILE — Regenerate with: make gen
"""Examples package."""

from __future__ import annotations

from types import MappingProxyType
from typing import TYPE_CHECKING

from flext_core.lazy import build_lazy_import_map, install_lazy_exports

if TYPE_CHECKING:
    from pydantic_core import from_json, to_json, to_jsonable_python

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
    from flext_db_oracle import c, config, db_oracle, e, m, p, s, settings, t, u
__all__: tuple[str, ...] = (
    "c",
    "config",
    "core",
    "d",
    "db_oracle",
    "e",
    "from_json",
    "h",
    "lazy",
    "lazy_attribute",
    "m",
    "normalize_lazy_imports",
    "p",
    "r",
    "s",
    "settings",
    "t",
    "to_json",
    "to_jsonable_python",
    "u",
    "x",
)

_LAZY_IMPORTS = MappingProxyType(
    build_lazy_import_map(
        MappingProxyType({
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
                "p",
                "s",
                "settings",
                "t",
                "u",
            ),
            "pydantic_core": ("from_json", "to_json", "to_jsonable_python"),
        }),
        alias_groups=MappingProxyType({}),
        sort_keys=False,
    )
)

install_lazy_exports(__name__, globals(), _LAZY_IMPORTS, public_exports=__all__)
