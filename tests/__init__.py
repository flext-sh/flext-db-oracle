# AUTO-GENERATED FILE — Regenerate with: make gen
"""Tests package."""

from __future__ import annotations

import typing as _t

from flext_core.lazy import build_lazy_import_map, install_lazy_exports

if _t.TYPE_CHECKING:
    from flext_core.decorators import d
    from flext_core.exceptions import e
    from flext_core.handlers import h
    from flext_core.mixins import x
    from flext_core.result import r
    from flext_core.service import s
    from tests.constants import (
        TestsFlextDbOracleConstants,
        TestsFlextDbOracleConstants as c,
    )
    from tests.models import TestsFlextDbOracleModels, TestsFlextDbOracleModels as m
    from tests.protocols import (
        TestsFlextDbOracleProtocols,
        TestsFlextDbOracleProtocols as p,
    )
    from tests.typings import TestsFlextDbOracleTypes, TestsFlextDbOracleTypes as t
    from tests.utilities import (
        TestsFlextDbOracleUtilities,
        TestsFlextDbOracleUtilities as u,
    )
_LAZY_IMPORTS = build_lazy_import_map(
    {
        ".constants": ("TestsFlextDbOracleConstants",),
        ".models": ("TestsFlextDbOracleModels",),
        ".protocols": ("TestsFlextDbOracleProtocols",),
        ".typings": ("TestsFlextDbOracleTypes",),
        ".utilities": ("TestsFlextDbOracleUtilities",),
        "flext_core.decorators": ("d",),
        "flext_core.exceptions": ("e",),
        "flext_core.handlers": ("h",),
        "flext_core.mixins": ("x",),
        "flext_core.result": ("r",),
        "flext_core.service": ("s",),
    },
    alias_groups={
        ".constants": (("c", "TestsFlextDbOracleConstants"),),
        ".models": (("m", "TestsFlextDbOracleModels"),),
        ".protocols": (("p", "TestsFlextDbOracleProtocols"),),
        ".typings": (("t", "TestsFlextDbOracleTypes"),),
        ".utilities": (("u", "TestsFlextDbOracleUtilities"),),
    },
)

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
    "u",
    "x",
]


install_lazy_exports(__name__, globals(), _LAZY_IMPORTS)
