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
    from flext_tests import api, d, h, r, td, tf, tk, tm, x

    from flext_db_oracle import config, db_oracle, e, main, settings
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
    "config",
    "d",
    "db_oracle",
    "e",
    "h",
    "m",
    "main",
    "p",
    "r",
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
        "c": ".constants",
        "config": "flext_db_oracle",
        "d": "flext_tests",
        "db_oracle": "flext_db_oracle",
        "e": "flext_db_oracle",
        "h": "flext_tests",
        "m": ".models",
        "main": "flext_db_oracle",
        "p": ".protocols",
        "r": "flext_tests",
        "s": ".base",
        "settings": "flext_db_oracle",
        "t": ".typings",
        "td": "flext_tests",
        "tf": "flext_tests",
        "tk": "flext_tests",
        "tm": "flext_tests",
        "u": ".utilities",
        "x": "flext_tests",
    }),
    public_exports=__all__,
)
