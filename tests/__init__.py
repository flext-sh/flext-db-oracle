# AUTO-GENERATED FILE — Regenerate with: make gen
"""Tests package."""

from __future__ import annotations

import typing as _t

from flext_core.lazy import install_lazy_exports

if _t.TYPE_CHECKING:
    from flext_core.decorators import FlextDecorators as d
    from flext_core.exceptions import FlextExceptions as e
    from flext_core.handlers import FlextHandlers as h
    from flext_core.mixins import FlextMixins as x
    from flext_core.result import FlextResult as r
    from flext_core.service import FlextService as s
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
_LAZY_IMPORTS = {
    "TestsFlextDbOracleConstants": ".constants",
    "TestsFlextDbOracleModels": ".models",
    "TestsFlextDbOracleProtocols": ".protocols",
    "TestsFlextDbOracleTypes": ".typings",
    "TestsFlextDbOracleUtilities": ".utilities",
    "c": (".constants", "TestsFlextDbOracleConstants"),
    "d": ("flext_core.decorators", "FlextDecorators"),
    "e": ("flext_core.exceptions", "FlextExceptions"),
    "h": ("flext_core.handlers", "FlextHandlers"),
    "m": (".models", "TestsFlextDbOracleModels"),
    "p": (".protocols", "TestsFlextDbOracleProtocols"),
    "r": ("flext_core.result", "FlextResult"),
    "s": ("flext_core.service", "FlextService"),
    "t": (".typings", "TestsFlextDbOracleTypes"),
    "u": (".utilities", "TestsFlextDbOracleUtilities"),
    "x": ("flext_core.mixins", "FlextMixins"),
}

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
