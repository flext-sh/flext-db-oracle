# AUTO-GENERATED FILE — Regenerate with: make gen
"""Flext Db Oracle package."""

from __future__ import annotations

from types import MappingProxyType
from typing import TYPE_CHECKING

from flext_core.lazy import build_lazy_import_map, install_lazy_exports

from .__version__ import (
    __author__ as __author__,
    __author_email__ as __author_email__,
    __description__ as __description__,
    __license__ as __license__,
    __title__ as __title__,
    __url__ as __url__,
    __version__ as __version__,
    __version_info__ as __version_info__,
)

if TYPE_CHECKING:
    from flext_core import core, d, h, lazy_attribute, r, x

    from . import services
    from ._config import FlextDbOracleConfig, config
    from ._settings import DbOracleSettings, FlextDbOracleSettings, settings
    from .api import FlextDbOracleApi, db_oracle
    from .base import FlextDbOracleServiceBase, s
    from .cli import main
    from .client import FlextDbOracleClient
    from .constants import FlextDbOracleConstants, c
    from .dispatcher import FlextDbOracleDispatcher
    from .exceptions import FlextDbOracleExceptions, e
    from .models import FlextDbOracleModels, m
    from .protocols import FlextDbOracleProtocols, p
    from .services.api_runtime import FlextDbOracleApiRuntime
    from .services.connection import FlextDbOracleServiceConnection
    from .services.facade import FlextDbOracleServices
    from .services.plugin import FlextDbOracleServicePlugin
    from .services.query import FlextDbOracleServiceQuery
    from .services.schema import FlextDbOracleServiceSchema
    from .services.singer import FlextDbOracleServiceSinger
    from .services.sql_builder import FlextDbOracleServiceSqlBuilder
    from .typings import FlextDbOracleTypes, t
    from .utilities import FlextDbOracleUtilities, u


__all__: tuple[str, ...] = (
    "DbOracleSettings",
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
    "core",
    "d",
    "db_oracle",
    "e",
    "h",
    "lazy_attribute",
    "m",
    "main",
    "p",
    "r",
    "s",
    "services",
    "settings",
    "t",
    "u",
    "x",
)

_LAZY_IMPORTS = MappingProxyType(
    build_lazy_import_map(
        MappingProxyType({
            "._config": ("FlextDbOracleConfig", "config"),
            "._settings": ("DbOracleSettings", "FlextDbOracleSettings", "settings"),
            ".api": ("FlextDbOracleApi", "db_oracle"),
            ".base": ("FlextDbOracleServiceBase", "s"),
            ".cli": ("main",),
            ".client": ("FlextDbOracleClient",),
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
            "flext_core": ("core", "d", "h", "lazy_attribute", "r", "x"),
        }),
        alias_groups=MappingProxyType({}),
        sort_keys=False,
    )
)

install_lazy_exports(__name__, globals(), _LAZY_IMPORTS, public_exports=__all__)
