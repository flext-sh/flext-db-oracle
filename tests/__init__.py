# AUTO-GENERATED FILE — Regenerate with: make gen
"""Tests package."""

from __future__ import annotations

from types import MappingProxyType
from typing import TYPE_CHECKING

from flext_core.lazy import build_lazy_import_map, install_lazy_exports

if TYPE_CHECKING:
    from flext_cli import cli
    from flext_tests import (
        active_rules,
        api,
        config,
        discover_repository_root,
        install_local_packages,
        load_infra_report,
        settings,
        split_csv,
        td,
        tf,
        tk,
        tm,
        tv,
    )

    from flext_core import core, d, h, lazy_attribute, r, x
    from flext_db_oracle import db_oracle, e, main

    from . import e2e, integration, unit
    from .base import TestsFlextDbOracleServiceBase, TestsFlextDbOracleServiceBase as s
    from .constants import TestsFlextDbOracleConstants, c
    from .models import TestsFlextDbOracleModels, m
    from .protocols import TestsFlextDbOracleProtocols, p
    from .settings import TestsFlextDbOracleSettings
    from .typings import TestsFlextDbOracleTypes, t
    from .utilities import TestsFlextDbOracleUtilities, u


__all__: tuple[str, ...] = (
    "TestsFlextDbOracleConstants",
    "TestsFlextDbOracleModels",
    "TestsFlextDbOracleProtocols",
    "TestsFlextDbOracleServiceBase",
    "TestsFlextDbOracleSettings",
    "TestsFlextDbOracleTypes",
    "TestsFlextDbOracleUtilities",
    "active_rules",
    "api",
    "c",
    "cli",
    "config",
    "core",
    "d",
    "db_oracle",
    "discover_repository_root",
    "e",
    "e2e",
    "h",
    "install_local_packages",
    "integration",
    "lazy_attribute",
    "load_infra_report",
    "m",
    "main",
    "p",
    "r",
    "s",
    "settings",
    "split_csv",
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
            ".utilities": ("TestsFlextDbOracleUtilities", "u"),
            "flext_cli": ("cli",),
            "flext_core": ("core", "d", "h", "lazy_attribute", "r", "x"),
            "flext_db_oracle": ("db_oracle", "e", "main"),
            "flext_tests": (
                "active_rules",
                "api",
                "config",
                "discover_repository_root",
                "install_local_packages",
                "load_infra_report",
                "settings",
                "split_csv",
                "td",
                "tf",
                "tk",
                "tm",
                "tv",
            ),
        }),
        alias_groups=MappingProxyType({}),
        sort_keys=False,
    )
)

install_lazy_exports(__name__, globals(), _LAZY_IMPORTS, public_exports=__all__)
