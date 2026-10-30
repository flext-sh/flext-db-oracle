# AUTO-GENERATED FILE — Regenerate with: make gen
"""Examples package.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from types import MappingProxyType
from typing import TYPE_CHECKING

from flext_core.lazy import install_lazy_exports

if TYPE_CHECKING:
    from flext_core import d, h, r, x

    from flext_db_oracle import (
        build_lazy_import_map,
        c,
        cleanup_submodule_namespace,
        config,
        core,
        db_oracle,
        e,
        install_lazy_exports,
        lazy,
        lazy_getattr,
        lazy_member,
        m,
        main,
        merge_lazy_imports,
        normalize_lazy_imports,
        p,
        resolve_lazy_members,
        s,
        settings,
        t,
        u,
    )


__all__: tuple[str, ...] = (
    "build_lazy_import_map",
    "c",
    "cleanup_submodule_namespace",
    "config",
    "core",
    "d",
    "db_oracle",
    "e",
    "h",
    "install_lazy_exports",
    "lazy",
    "lazy_getattr",
    "lazy_member",
    "m",
    "main",
    "merge_lazy_imports",
    "normalize_lazy_imports",
    "p",
    "r",
    "resolve_lazy_members",
    "s",
    "settings",
    "t",
    "u",
    "x",
)

install_lazy_exports(
    __name__,
    globals(),
    MappingProxyType({
        "build_lazy_import_map": "flext_db_oracle",
        "c": "flext_db_oracle",
        "cleanup_submodule_namespace": "flext_db_oracle",
        "config": "flext_db_oracle",
        "core": "flext_db_oracle",
        "d": "flext_core",
        "db_oracle": "flext_db_oracle",
        "e": "flext_db_oracle",
        "h": "flext_core",
        "install_lazy_exports": "flext_db_oracle",
        "lazy": "flext_db_oracle",
        "lazy_getattr": "flext_db_oracle",
        "lazy_member": "flext_db_oracle",
        "m": "flext_db_oracle",
        "main": "flext_db_oracle",
        "merge_lazy_imports": "flext_db_oracle",
        "normalize_lazy_imports": "flext_db_oracle",
        "p": "flext_db_oracle",
        "r": "flext_core",
        "resolve_lazy_members": "flext_db_oracle",
        "s": "flext_db_oracle",
        "settings": "flext_db_oracle",
        "t": "flext_db_oracle",
        "u": "flext_db_oracle",
        "x": "flext_core",
    }),
    public_exports=__all__,
)
