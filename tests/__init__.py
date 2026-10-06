# AUTO-GENERATED FILE — Regenerate with: make gen
"""Tests package.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from types import MappingProxyType
from typing import TYPE_CHECKING

from flext_core import install_lazy_exports

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
        "c": ".constants",
        "d": "flext_core",
        "e": "flext_db_oracle",
        "e2e": ".e2e",
        "h": "flext_core",
        "integration": ".integration",
        "m": ".models",
        "p": ".protocols",
        "r": "flext_core",
        "s": ".base",
        "t": ".typings",
        "td": "flext_tests",
        "tf": "flext_tests",
        "tk": "flext_tests",
        "tm": "flext_tests",
        "u": ".utilities",
        "unit": ".unit",
        "x": "flext_core",
    }),
    public_exports=__all__,
)
