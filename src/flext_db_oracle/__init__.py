# @generated AUTO-GENERATED FILE — Regenerate with: make gen
"""Flext Db Oracle package."""

from __future__ import annotations

from typing import TYPE_CHECKING

from flext_core.lazy import build_lazy_import_map, install_lazy_exports

from .__version__ import __author__ as __author__
from .__version__ import __author_email__ as __author_email__
from .__version__ import __description__ as __description__
from .__version__ import __license__ as __license__
from .__version__ import __title__ as __title__
from .__version__ import __url__ as __url__
from .__version__ import __version__ as __version__
from .__version__ import __version_info__ as __version_info__

if TYPE_CHECKING:
    from flext_core import d as d
    from flext_core import e as e
    from flext_core import h as h
    from flext_core import r as r
    from flext_core import x as x

    from ._config import FlextDbOracleConfig as FlextDbOracleConfig
    from ._config import config as config
    from ._settings import FlextDbOracleSettings as FlextDbOracleSettings
    from ._settings import settings as settings
    from .api import FlextDbOracleApi as FlextDbOracleApi
    from .api import db_oracle as db_oracle
    from .base import FlextDbOracleServiceBase as FlextDbOracleServiceBase

    s: type[FlextDbOracleServiceBase]
    from .constants import FlextDbOracleConstants as FlextDbOracleConstants

    c: type[FlextDbOracleConstants]
    from .dispatcher import FlextDbOracleDispatcher as FlextDbOracleDispatcher
    from .exceptions import FlextDbOracleExceptions as FlextDbOracleExceptions
    from .models import FlextDbOracleModels as FlextDbOracleModels

    m: type[FlextDbOracleModels]
    from .protocols import FlextDbOracleProtocols as FlextDbOracleProtocols

    p: type[FlextDbOracleProtocols]
    from .typings import FlextDbOracleTypes as FlextDbOracleTypes

    t: type[FlextDbOracleTypes]
    from .utilities import FlextDbOracleUtilities as FlextDbOracleUtilities

    u: type[FlextDbOracleUtilities]

_LAZY_MODULES: dict[str, tuple[str, ...]] = {
    "._config": ("FlextDbOracleConfig", "config"),
    "._settings": ("FlextDbOracleSettings", "settings"),
    ".api": ("FlextDbOracleApi", "db_oracle"),
    ".base": ("FlextDbOracleServiceBase", "s"),
    ".constants": ("FlextDbOracleConstants", "c"),
    ".dispatcher": ("FlextDbOracleDispatcher",),
    ".exceptions": ("FlextDbOracleExceptions",),
    ".models": ("FlextDbOracleModels", "m"),
    ".protocols": ("FlextDbOracleProtocols", "p"),
    ".typings": ("FlextDbOracleTypes", "t"),
    ".utilities": ("FlextDbOracleUtilities", "u"),
    "flext_core": ("d", "e", "h", "r", "x"),
}


_LAZY_ALIAS_GROUPS: dict[str, tuple[tuple[str, str], ...]] = {}


_LAZY_IMPORTS = build_lazy_import_map(
    _LAZY_MODULES, alias_groups=_LAZY_ALIAS_GROUPS, sort_keys=False
)

_PUBLIC_EXPORTS: tuple[str, ...] = (
    "FlextDbOracleApi",
    "FlextDbOracleConfig",
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
    "config",
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

__all__: tuple[str, ...] = tuple(_PUBLIC_EXPORTS)

install_lazy_exports(__name__, globals(), _LAZY_IMPORTS, public_exports=__all__)
