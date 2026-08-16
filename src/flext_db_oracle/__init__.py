# AUTO-GENERATED FILE — Regenerate with: make gen
"""Flext Db Oracle package."""

from __future__ import annotations

from typing import TYPE_CHECKING

from types import MappingProxyType

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
    from flext_core import d, e, h, r, x

    from ._config import FlextDbOracleConfig, config
    from ._settings import DbOracleSettings, FlextDbOracleSettings, settings
    from .api import FlextDbOracleApi, db_oracle
    from .base import FlextDbOracleServiceBase, FlextDbOracleServiceBase as s
    from .constants import FlextDbOracleConstants, FlextDbOracleConstants as c
    from .dispatcher import FlextDbOracleDispatcher
    from .exceptions import FlextDbOracleExceptions
    from .models import FlextDbOracleModels, FlextDbOracleModels as m
    from .protocols import FlextDbOracleProtocols, FlextDbOracleProtocols as p
    from .typings import FlextDbOracleTypes, FlextDbOracleTypes as t
    from .utilities import FlextDbOracleUtilities, FlextDbOracleUtilities as u
__all__: tuple[str, ...] = (
    "DbOracleSettings",
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

install_lazy_exports(
    __name__,
    globals(),
    MappingProxyType(
        build_lazy_import_map(
            MappingProxyType({
                "._config": ("FlextDbOracleConfig", "config"),
                "._settings": ("DbOracleSettings", "FlextDbOracleSettings", "settings"),
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
            }),
            alias_groups=MappingProxyType({}),
            sort_keys=False,
        )
    ),
    public_exports=__all__,
)
