# AUTO-GENERATED FILE — Regenerate with: make gen
"""Examples package."""

from __future__ import annotations

from types import MappingProxyType
from typing import TYPE_CHECKING

from flext_core.lazy import build_lazy_import_map, install_lazy_exports

if TYPE_CHECKING:
    from flext_core import (
        FlextDbOracleConstants,
        FlextDbOracleConstants as c,
        d,
        e,
        h,
        m,
        p,
        r,
        s,
        t,
        u,
        x,
    )

    from .constants import ExamplesFlextDbOracleConstants
    from .models import ExamplesFlextDbOracleModels
    from .protocols import ExamplesFlextDbOracleProtocols
    from .typings import ExamplesFlextDbOracleTypes
    from .utilities import ExamplesFlextDbOracleUtilities
__all__: tuple[str, ...] = (
    "ExamplesFlextDbOracleConstants",
    "ExamplesFlextDbOracleModels",
    "ExamplesFlextDbOracleProtocols",
    "ExamplesFlextDbOracleTypes",
    "ExamplesFlextDbOracleUtilities",
    "FlextDbOracleConstants",
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
)

_LAZY_IMPORTS = MappingProxyType(
    build_lazy_import_map(
        MappingProxyType({
            ".constants": ("ExamplesFlextDbOracleConstants",),
            ".models": ("ExamplesFlextDbOracleModels",),
            ".protocols": ("ExamplesFlextDbOracleProtocols",),
            ".typings": ("ExamplesFlextDbOracleTypes",),
            ".utilities": ("ExamplesFlextDbOracleUtilities",),
            "flext_core": (
                "FlextDbOracleConstants",
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
            ),
        }),
        alias_groups=MappingProxyType({}),
        sort_keys=False,
    )
)

install_lazy_exports(__name__, globals(), _LAZY_IMPORTS, public_exports=__all__)
