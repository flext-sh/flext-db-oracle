# AUTO-GENERATED FILE — Regenerate with: make gen
"""Tests package."""

from __future__ import annotations

from typing import TYPE_CHECKING

from types import MappingProxyType

from flext_core.lazy import build_lazy_import_map, install_lazy_exports

if TYPE_CHECKING:
    from . import e2e as e2e
    from . import integration as integration
    from . import unit as unit
    from flext_tests import FlextTestsConstants, d, h, r, td, tf, tk, tm, tv, x

    from .base import TestsFlextDbOracleServiceBase, TestsFlextDbOracleServiceBase as s
    from .constants import TestsFlextDbOracleConstants, TestsFlextDbOracleConstants as c
    from .models import TestsFlextDbOracleModels, TestsFlextDbOracleModels as m
    from .protocols import TestsFlextDbOracleProtocols, TestsFlextDbOracleProtocols as p
    from .settings import TestsFlextDbOracleSettings
    from .typings import TestsFlextDbOracleTypes, TestsFlextDbOracleTypes as t
    from .unit.exceptions import FlextDbOracleTestExceptions, e
    from .utilities import TestsFlextDbOracleUtilities, TestsFlextDbOracleUtilities as u
__all__: tuple[str, ...] = (
    "FlextDbOracleTestExceptions",
    "FlextTestsConstants",
    "TestsFlextDbOracleConstants",
    "TestsFlextDbOracleModels",
    "TestsFlextDbOracleProtocols",
    "TestsFlextDbOracleServiceBase",
    "TestsFlextDbOracleSettings",
    "TestsFlextDbOracleTypes",
    "TestsFlextDbOracleUtilities",
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
    "tv",
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
            ".unit.exceptions": ("FlextDbOracleTestExceptions", "e"),
            ".utilities": ("TestsFlextDbOracleUtilities", "u"),
            "flext_tests": (
                "FlextTestsConstants",
                "d",
                "h",
                "r",
                "td",
                "tf",
                "tk",
                "tm",
                "tv",
                "x",
            ),
        }),
        alias_groups=MappingProxyType({}),
        sort_keys=False,
    )
)

install_lazy_exports(__name__, globals(), _LAZY_IMPORTS, public_exports=__all__)
