# AUTO-GENERATED FILE — Regenerate with: make gen
"""Flext Db Oracle package.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from types import MappingProxyType
from typing import TYPE_CHECKING

from flext_core import build_lazy_import_map, install_lazy_exports
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
    from flext_core import d, h, r, x
    from flext_db_oracle import services
    from flext_db_oracle._config import FlextDbOracleConfig, config
    from flext_db_oracle._settings import (
        DbOracleSettings,
        FlextDbOracleSettings,
        settings,
    )
    from flext_db_oracle.api import FlextDbOracleApi, db_oracle
    from flext_db_oracle.base import FlextDbOracleServiceBase, s
    from flext_db_oracle.cli import main
    from flext_db_oracle.client import FlextDbOracleClient
    from flext_db_oracle.constants import FlextDbOracleConstants, c
    from flext_db_oracle.dispatcher import FlextDbOracleDispatcher
    from flext_db_oracle.exceptions import FlextDbOracleExceptions, e
    from flext_db_oracle.models import FlextDbOracleModels, m
    from flext_db_oracle.protocols import FlextDbOracleProtocols, p
    from flext_db_oracle.services.api_runtime import FlextDbOracleApiRuntime
    from flext_db_oracle.services.connection import FlextDbOracleServiceConnection
    from flext_db_oracle.services.facade import FlextDbOracleServices
    from flext_db_oracle.services.plugin import FlextDbOracleServicePlugin
    from flext_db_oracle.services.query import FlextDbOracleServiceQuery
    from flext_db_oracle.services.schema import FlextDbOracleServiceSchema
    from flext_db_oracle.services.singer import FlextDbOracleServiceSinger
    from flext_db_oracle.services.sql_builder import FlextDbOracleServiceSqlBuilder
    from flext_db_oracle.typings import FlextDbOracleTypes, t
    from flext_db_oracle.utilities import FlextDbOracleUtilities, u


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
    "d",
    "db_oracle",
    "e",
    "h",
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
            "flext_core": ("d", "h", "r", "x"),
        }),
        alias_groups=MappingProxyType({}),
        sort_keys=False,
    ),
)

install_lazy_exports(__name__, globals(), _LAZY_IMPORTS, public_exports=__all__)
