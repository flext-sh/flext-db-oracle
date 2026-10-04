# AUTO-GENERATED FILE — Regenerate with: make gen
"""Tests package.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from types import MappingProxyType
from typing import TYPE_CHECKING

from flext_core import build_lazy_import_map, install_lazy_exports

if TYPE_CHECKING:
    from flext_tests import api, td, tf, tk, tm

    from flext_core import d, h, r, x
    from flext_db_oracle import e
    from tests import e2e, integration, unit
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
    "c",
    "d",
    "e",
    "e2e",
    "h",
    "integration",
    "m",
    "p",
    "r",
    "s",
    "t",
    "td",
    "tf",
    "tk",
    "tm",
    "u",
    "unit",
    "x",
)

_LAZY_IMPORTS = MappingProxyType(
    build_lazy_import_map(
        MappingProxyType({
            ".base": ("TestsFlextDbOracleServiceBase", "s"),
            ".constants": ("TestsFlextDbOracleConstants", "c"),
            ".e2e": ("e2e",),
            ".integration": ("integration",),
            ".models": ("TestsFlextDbOracleModels", "m"),
            ".protocols": ("TestsFlextDbOracleProtocols", "p"),
            ".settings": ("TestsFlextDbOracleSettings",),
            ".typings": ("TestsFlextDbOracleTypes", "t"),
            ".unit": ("unit",),
            ".utilities": ("TestsFlextDbOracleUtilities", "u"),
            "flext_core": ("d", "h", "r", "x"),
            "flext_db_oracle": ("e",),
            "flext_tests": ("api", "td", "tf", "tk", "tm"),
        }),
        alias_groups=MappingProxyType({}),
        sort_keys=False,
    ),
)

install_lazy_exports(__name__, globals(), _LAZY_IMPORTS, public_exports=__all__)
