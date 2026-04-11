# AUTO-GENERATED FILE — Regenerate with: make gen
"""Tests package."""

from __future__ import annotations

import typing as _t

from flext_core.lazy import (
    build_lazy_import_map,
    install_lazy_exports,
    merge_lazy_imports,
)

if _t.TYPE_CHECKING:
    from flext_tests import d, e, h, r, s, td, tf, tk, tm, tv, x

    from tests.constants import TestsFlextDbOracleConstants, c
    from tests.models import TestsFlextDbOracleModels, m
    from tests.protocols import TestsFlextDbOracleProtocols, p
    from tests.typings import TestsFlextDbOracleTypes, t
    from tests.utilities import TestsFlextDbOracleUtilities, u
_LAZY_IMPORTS = merge_lazy_imports(
    (
        ".e2e",
        ".integration",
        ".unit",
    ),
    build_lazy_import_map(
        {
            ".constants": (
                "TestsFlextDbOracleConstants",
                "c",
            ),
            ".models": (
                "TestsFlextDbOracleModels",
                "m",
            ),
            ".protocols": (
                "TestsFlextDbOracleProtocols",
                "p",
            ),
            ".typings": (
                "TestsFlextDbOracleTypes",
                "t",
            ),
            ".utilities": (
                "TestsFlextDbOracleUtilities",
                "u",
            ),
            "flext_tests": (
                "d",
                "e",
                "h",
                "r",
                "s",
                "td",
                "tf",
                "tk",
                "tm",
                "tv",
                "x",
            ),
        },
    ),
    exclude_names=(
        "cleanup_submodule_namespace",
        "install_lazy_exports",
        "lazy_getattr",
        "logger",
        "merge_lazy_imports",
        "output",
        "output_reporting",
    ),
    module_name=__name__,
)


install_lazy_exports(__name__, globals(), _LAZY_IMPORTS)

__all__ = [
    "TestsFlextDbOracleConstants",
    "TestsFlextDbOracleModels",
    "TestsFlextDbOracleProtocols",
    "TestsFlextDbOracleTypes",
    "TestsFlextDbOracleUtilities",
    "c",
    "d",
    "e",
    "h",
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
    "x",
]
