# AUTO-GENERATED FILE — Regenerate with: make gen
"""Tests package.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from types import MappingProxyType
from typing import TYPE_CHECKING

from flext_core.lazy import install_lazy_exports

if TYPE_CHECKING:
    from flext_core import d, h, r, x
    from flext_tests import (
        api,
        config,
        install_local_packages,
        settings,
        td,
        tf,
        tk,
        tm,
    )

    from flext_db_oracle import (
        build_lazy_import_map,
        cleanup_submodule_namespace,
        core,
        db_oracle,
        e,
        install_lazy_exports,
        lazy,
        lazy_getattr,
        lazy_member,
        main,
        merge_lazy_imports,
        normalize_lazy_imports,
        resolve_lazy_members,
    )
    from tests.base import TestsFlextDbOracleServiceBase, s
    from tests.constants import TestsFlextDbOracleConstants, c
    from tests.models import TestsFlextDbOracleModels, m
    from tests.protocols import TestsFlextDbOracleProtocols, p
    from tests.settings import TestsFlextDbOracleSettings
    from tests.typings import TestsFlextDbOracleTypes, t
    from tests.utilities import TestsFlextDbOracleUtilities, u


__all__: tuple[str, ...] = (
    "TestsFlextDbOracleConstants",
    "TestsFlextDbOracleModels",
    "TestsFlextDbOracleProtocols",
    "TestsFlextDbOracleServiceBase",
    "TestsFlextDbOracleSettings",
    "TestsFlextDbOracleTypes",
    "TestsFlextDbOracleUtilities",
    "api",
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
    "install_local_packages",
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
    "td",
    "tf",
    "tk",
    "tm",
    "u",
    "x",
)

install_lazy_exports(
    __name__,
    globals(),
    MappingProxyType({
        "TestsFlextDbOracleConstants": ".constants",
        "TestsFlextDbOracleModels": ".models",
        "TestsFlextDbOracleProtocols": ".protocols",
        "TestsFlextDbOracleServiceBase": ".base",
        "TestsFlextDbOracleSettings": ".settings",
        "TestsFlextDbOracleTypes": ".typings",
        "TestsFlextDbOracleUtilities": ".utilities",
        "api": "flext_tests",
        "build_lazy_import_map": "flext_db_oracle",
        "c": ".constants",
        "cleanup_submodule_namespace": "flext_db_oracle",
        "config": "flext_tests",
        "core": "flext_db_oracle",
        "d": "flext_core",
        "db_oracle": "flext_db_oracle",
        "e": "flext_db_oracle",
        "h": "flext_core",
        "install_lazy_exports": "flext_db_oracle",
        "install_local_packages": "flext_tests",
        "lazy": "flext_db_oracle",
        "lazy_getattr": "flext_db_oracle",
        "lazy_member": "flext_db_oracle",
        "m": ".models",
        "main": "flext_db_oracle",
        "merge_lazy_imports": "flext_db_oracle",
        "normalize_lazy_imports": "flext_db_oracle",
        "p": ".protocols",
        "r": "flext_core",
        "resolve_lazy_members": "flext_db_oracle",
        "s": ".base",
        "settings": "flext_tests",
        "t": ".typings",
        "td": "flext_tests",
        "tf": "flext_tests",
        "tk": "flext_tests",
        "tm": "flext_tests",
        "u": ".utilities",
        "x": "flext_core",
    }),
    public_exports=__all__,
)
