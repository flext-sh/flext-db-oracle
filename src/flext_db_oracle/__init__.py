# AUTO-GENERATED FILE — Regenerate with: make gen
"""Flext Db Oracle package."""

from __future__ import annotations

from typing import TYPE_CHECKING

from flext_core.lazy import build_lazy_import_map, install_lazy_exports
from flext_db_oracle.__version__ import (
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
    from flext_core import d, e, h, r, x

    from ._config import FlextDbOracleConfig, config
    from ._models.password import FlextDbOraclePassword
    from ._settings import FlextDbOracleSettings, settings
    from ._utilities.db_oracle import FlextDbOracleUtilitiesDbOracle
    from .api import FlextDbOracleApi, db_oracle
    from .base import FlextDbOracleServiceBase, s
    from .client import FlextDbOracleClient, client
    from .constants import FlextDbOracleConstants, FlextDbOracleConstants as c
    from .dispatcher import FlextDbOracleDispatcher
    from .exceptions import FlextDbOracleExceptions
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
        FlextDbOracleConfig,
        config,
        FlextDbOraclePassword,
        FlextDbOracleSettings,
        settings,
        FlextDbOracleUtilitiesDbOracle,
        FlextDbOracleApi,
        db_oracle,
        FlextDbOracleClient,
        client,
        FlextDbOracleDispatcher,
        FlextDbOracleExceptions,
        FlextDbOracleApiRuntime,
        FlextDbOracleServiceConnection,
        FlextDbOracleServices,
        FlextDbOracleServicePlugin,
        FlextDbOracleServiceQuery,
        FlextDbOracleServiceSchema,
        FlextDbOracleServiceSinger,
        FlextDbOracleServiceSqlBuilder,
    )


_LAZY_MODULES: dict[str, tuple[str, ...]] = {
    "._config": ("FlextDbOracleConfig", "config"),
    "._models.password": ("FlextDbOraclePassword",),
    "._settings": ("FlextDbOracleSettings", "settings"),
    "._utilities.db_oracle": ("FlextDbOracleUtilitiesDbOracle",),
    ".api": ("FlextDbOracleApi", "db_oracle"),
    ".base": ("FlextDbOracleServiceBase", "s"),
    ".client": ("FlextDbOracleClient", "client"),
    ".constants": ("FlextDbOracleConstants", "c"),
    ".dispatcher": ("FlextDbOracleDispatcher",),
    ".exceptions": ("FlextDbOracleExceptions",),
    ".models": ("FlextDbOracleModels", "m"),
    ".protocols": ("FlextDbOracleProtocols", "p"),
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
    "flext_core": ("d", "e", "h", "r", "x"),
}


_LAZY_ALIAS_GROUPS: dict[str, tuple[tuple[str, str], ...]] = {}


_LAZY_IMPORTS = build_lazy_import_map(
    _LAZY_MODULES, alias_groups=_LAZY_ALIAS_GROUPS, sort_keys=False
)

_DIRECT_IMPORTS: tuple[str, ...] = (
    "FlextDbOracleApi",
    "FlextDbOracleApiRuntime",
    "FlextDbOracleClient",
    "FlextDbOracleConfig",
    "FlextDbOracleConstants",
    "FlextDbOracleDispatcher",
    "FlextDbOracleExceptions",
    "FlextDbOracleModels",
    "FlextDbOraclePassword",
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
    "FlextDbOracleUtilitiesDbOracle",
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
    "client",
    "config",
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
    "FlextDbOracleApiRuntime",
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


install_lazy_exports(__name__, globals(), _LAZY_IMPORTS, public_exports=__all__)
