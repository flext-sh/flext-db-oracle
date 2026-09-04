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
    from . import services as services
    from enum import StrEnum, unique
    from flext_core import d, h, r, x
    from typing import ClassVar, Final, TYPE_CHECKING

    from ._config import FlextDbOracleConfig, config
    from ._settings import DbOracleSettings, FlextDbOracleSettings, settings
    from .api import FlextDbOracleApi, db_oracle
    from .base import FlextDbOracleServiceBase, FlextDbOracleServiceBase as s
    from .client import FlextDbOracleClient, client
    from .constants import FlextDbOracleConstants, FlextDbOracleConstants as c
    from .dispatcher import FlextDbOracleDispatcher
    from .exceptions import FlextDbOracleExceptions, e
    from .models import FlextDbOracleModels, FlextDbOracleModels as m
    from .protocols import FlextDbOracleProtocols, FlextDbOracleProtocols as p
    from .services.api_runtime import FlextDbOracleApiRuntime
    from .services.connection import FlextDbOracleServiceConnection
    from .services.facade import FlextDbOracleServices
    from .services.plugin import FlextDbOracleServicePlugin
    from .services.query import FlextDbOracleServiceQuery
    from .services.schema import FlextDbOracleServiceSchema
    from .services.singer import FlextDbOracleServiceSinger
    from .services.sql_builder import FlextDbOracleServiceSqlBuilder
    from .typings import FlextDbOracleTypes, FlextDbOracleTypes as t
    from .utilities import FlextDbOracleUtilities, FlextDbOracleUtilities as u
__all__: tuple[str, ...] = (
    "TYPE_CHECKING",
    "ClassVar",
    "DbOracleSettings",
    "Final",
    "FlextDbOracleApi",
    "FlextDbOracleApiRuntime",
    "FlextDbOracleClient",
    "FlextDbOracleConfig",
    "FlextDbOracleConstants",
    "FlextDbOracleDispatcher",
    "FlextDbOracleExceptions",
    "FlextDbOracleModels",
    "FlextDbOracleProtocols",
    "FlextDbOracleServiceBase",
    "FlextDbOracleServiceConnection",
    "FlextDbOracleServicePlugin",
    "FlextDbOracleServiceQuery",
    "FlextDbOracleServiceSchema",
    "FlextDbOracleServiceSinger",
    "FlextDbOracleServiceSqlBuilder",
    "FlextDbOracleServices",
    "FlextDbOracleSettings",
    "FlextDbOracleTypes",
    "FlextDbOracleUtilities",
    "MappingProxyType",
    "StrEnum",
    "__author__",
    "__author_email__",
    "__description__",
    "__license__",
    "__title__",
    "__url__",
    "__version__",
    "__version_info__",
    "c",
    "client",
    "config",
    "d",
    "db_oracle",
    "e",
    "h",
    "m",
    "p",
    "r",
    "s",
    "services",
    "settings",
    "t",
    "u",
    "unique",
    "x",
)

_LAZY_IMPORTS = MappingProxyType(
    build_lazy_import_map(
        MappingProxyType({
            "._config": ("FlextDbOracleConfig", "config"),
            "._settings": ("DbOracleSettings", "FlextDbOracleSettings", "settings"),
            ".api": ("FlextDbOracleApi", "db_oracle"),
            ".base": ("FlextDbOracleServiceBase", "s"),
            ".client": ("FlextDbOracleClient", "client"),
            ".constants": ("FlextDbOracleConstants", "c"),
            ".dispatcher": ("FlextDbOracleDispatcher",),
            ".exceptions": ("FlextDbOracleExceptions", "e"),
            ".models": ("FlextDbOracleModels", "m"),
            ".protocols": ("FlextDbOracleProtocols", "p"),
            ".services": ("services",),
            ".services.api_runtime": ("FlextDbOracleApiRuntime",),
            ".services.connection": ("FlextDbOracleServiceConnection",),
            ".services.facade": ("FlextDbOracleServices",),
            ".services.plugin": ("FlextDbOracleServicePlugin",),
            ".services.query": ("FlextDbOracleServiceQuery",),
            ".services.schema": ("FlextDbOracleServiceSchema",),
            ".services.singer": ("FlextDbOracleServiceSinger",),
            ".services.sql_builder": ("FlextDbOracleServiceSqlBuilder",),
            ".typings": ("FlextDbOracleTypes", "t"),
            ".utilities": ("FlextDbOracleUtilities", "u"),
            "enum": ("StrEnum", "unique"),
            "flext_core": ("d", "h", "r", "x"),
            "types": ("MappingProxyType",),
            "typing": ("ClassVar", "Final", "TYPE_CHECKING"),
        }),
        alias_groups=MappingProxyType({}),
        sort_keys=False,
    )
)

install_lazy_exports(__name__, globals(), _LAZY_IMPORTS, public_exports=__all__)
