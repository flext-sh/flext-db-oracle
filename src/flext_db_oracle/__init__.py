# AUTO-GENERATED FILE — Regenerate with: make gen
"""Flext Db Oracle package."""

from __future__ import annotations

from typing import TYPE_CHECKING

from flext_core.lazy import build_lazy_import_map, install_lazy_exports
from flext_db_oracle.__version__ import (
    __author__,
    __author_email__,
    __description__,
    __license__,
    __title__,
    __url__,
    __version__,
    __version_info__,
)

if TYPE_CHECKING:
    from flext_core import d, e, h, r, x

    from ._settings import FlextDbOracleSettings, settings
    from .api import FlextDbOracleApi, db_oracle
    from .base import FlextDbOracleServiceBase, s
    from .constants import FlextDbOracleConstants, FlextDbOracleConstants as c
    from .dispatcher import FlextDbOracleDispatcher
    from .exceptions import FlextDbOracleExceptions
    from .models import FlextDbOracleModels, FlextDbOracleModels as m
    from .protocols import FlextDbOracleProtocols, FlextDbOracleProtocols as p
    from .typings import FlextDbOracleTypes, FlextDbOracleTypes as t
    from .utilities import FlextDbOracleUtilities, FlextDbOracleUtilities as u

    _ = (
        c,
        FlextDbOracleConstants,
        t,
        FlextDbOracleTypes,
        p,
        FlextDbOracleProtocols,
        m,
        FlextDbOracleModels,
        u,
        FlextDbOracleUtilities,
        d,
        e,
        h,
        r,
        x,
        s,
        FlextDbOracleServiceBase,
        FlextDbOracleSettings,
        settings,
        FlextDbOracleApi,
        db_oracle,
        FlextDbOracleDispatcher,
        FlextDbOracleExceptions,
    )


_LAZY_MODULES: dict[str, tuple[str, ...]] = {
    "._settings": (
        "FlextDbOracleSettings",
        "settings",
    ),
    ".api": (
        "FlextDbOracleApi",
        "db_oracle",
    ),
    ".base": (
        "FlextDbOracleServiceBase",
        "s",
    ),
    ".constants": (
        "FlextDbOracleConstants",
        "c",
    ),
    ".dispatcher": ("FlextDbOracleDispatcher",),
    ".exceptions": ("FlextDbOracleExceptions",),
    ".models": (
        "FlextDbOracleModels",
        "m",
    ),
    ".protocols": (
        "FlextDbOracleProtocols",
        "p",
    ),
    ".typings": (
        "FlextDbOracleTypes",
        "t",
    ),
    ".utilities": (
        "FlextDbOracleUtilities",
        "u",
    ),
    "flext_core": (
        "d",
        "e",
        "h",
        "r",
        "x",
    ),
}


_LAZY_ALIAS_GROUPS: dict[str, tuple[tuple[str, str], ...]] = {}


_LAZY_IMPORTS = build_lazy_import_map(
    _LAZY_MODULES,
    alias_groups=_LAZY_ALIAS_GROUPS,
    sort_keys=False,
)

_DIRECT_IMPORTS: tuple[str, ...] = (
    "FlextDbOracleApi",
    "FlextDbOracleConstants",
    "FlextDbOracleDispatcher",
    "FlextDbOracleExceptions",
    "FlextDbOracleModels",
    "FlextDbOracleProtocols",
    "FlextDbOracleServiceBase",
    "FlextDbOracleSettings",
    "FlextDbOracleTypes",
    "FlextDbOracleUtilities",
    "__author__",
    "__author_email__",
    "__description__",
    "__license__",
    "__title__",
    "__url__",
    "__version__",
    "__version_info__",
    "build_lazy_import_map",
    "c",
    "d",
    "db_oracle",
    "e",
    "h",
    "install_lazy_exports",
    "m",
    "p",
    "r",
    "s",
    "settings",
    "t",
    "u",
    "x",
)

__all__: tuple[str, ...] = (
    "FlextDbOracleApi",
    "FlextDbOracleConstants",
    "FlextDbOracleDispatcher",
    "FlextDbOracleExceptions",
    "FlextDbOracleModels",
    "FlextDbOracleProtocols",
    "FlextDbOracleServiceBase",
    "FlextDbOracleSettings",
    "FlextDbOracleTypes",
    "FlextDbOracleUtilities",
    "__author__",
    "__author_email__",
    "__description__",
    "__license__",
    "__title__",
    "__url__",
    "__version__",
    "__version_info__",
    "c",
    "d",
    "db_oracle",
    "e",
    "h",
    "m",
    "p",
    "r",
    "s",
    "settings",
    "t",
    "u",
    "x",
)


install_lazy_exports(
    __name__,
    globals(),
    _LAZY_IMPORTS,
    public_exports=__all__,
)
