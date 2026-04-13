# AUTO-GENERATED FILE — Regenerate with: make gen
"""Flext Db Oracle package."""

from __future__ import annotations

import typing as _t

from flext_core.lazy import (
    build_lazy_import_map,
    install_lazy_exports,
    merge_lazy_imports,
)
from flext_db_oracle.__version__ import *

if _t.TYPE_CHECKING:
    from flext_cli import d, h, r, s, x

    from flext_db_oracle._utilities.db_oracle import FlextDbOracleUtilitiesDbOracle
    from flext_db_oracle.api import FlextDbOracleApi, db_oracle
    from flext_db_oracle.base import FlextDbOracleServiceBase
    from flext_db_oracle.cli import FlextDbOracleCli, cli
    from flext_db_oracle.client import FlextDbOracleClient, client
    from flext_db_oracle.constants import FlextDbOracleConstants, c
    from flext_db_oracle.dispatcher import FlextDbOracleDispatcher
    from flext_db_oracle.exceptions import FlextDbOracleExceptions, e
    from flext_db_oracle.models import FlextDbOracleModels, m
    from flext_db_oracle.password import FlextDbOraclePassword
    from flext_db_oracle.protocols import FlextDbOracleProtocols, p
    from flext_db_oracle.services.connection import FlextDbOracleServiceConnection
    from flext_db_oracle.services.plugin import FlextDbOracleServicePlugin
    from flext_db_oracle.services.query import FlextDbOracleServiceQuery
    from flext_db_oracle.services.schema import FlextDbOracleServiceSchema
    from flext_db_oracle.services.singer import FlextDbOracleServiceSinger
    from flext_db_oracle.services.sql_builder import FlextDbOracleServiceSqlBuilder
    from flext_db_oracle.settings import FlextDbOracleSettings
    from flext_db_oracle.typings import FlextDbOracleTypes, t
    from flext_db_oracle.utilities import FlextDbOracleUtilities, u
_LAZY_IMPORTS = merge_lazy_imports(
    (
        "._utilities",
        ".services",
    ),
    build_lazy_import_map(
        {
            ".__version__": (
                "__author__",
                "__author_email__",
                "__description__",
                "__license__",
                "__title__",
                "__url__",
                "__version__",
                "__version_info__",
            ),
            ".api": (
                "FlextDbOracleApi",
                "db_oracle",
            ),
            ".base": ("FlextDbOracleServiceBase",),
            ".cli": (
                "FlextDbOracleCli",
                "cli",
            ),
            ".client": (
                "FlextDbOracleClient",
                "client",
            ),
            ".constants": (
                "FlextDbOracleConstants",
                "c",
            ),
            ".dispatcher": ("FlextDbOracleDispatcher",),
            ".exceptions": (
                "FlextDbOracleExceptions",
                "e",
            ),
            ".models": (
                "FlextDbOracleModels",
                "m",
            ),
            ".password": ("FlextDbOraclePassword",),
            ".protocols": (
                "FlextDbOracleProtocols",
                "p",
            ),
            ".settings": ("FlextDbOracleSettings",),
            ".typings": (
                "FlextDbOracleTypes",
                "t",
            ),
            ".utilities": (
                "FlextDbOracleUtilities",
                "u",
            ),
            "flext_cli": (
                "d",
                "h",
                "r",
                "s",
                "x",
            ),
        },
    ),
    exclude_names=(
        "FlextDispatcher",
        "FlextLogger",
        "FlextRegistry",
        "FlextRuntime",
        "cleanup_submodule_namespace",
        "install_lazy_exports",
        "lazy_getattr",
        "logger",
        "merge_lazy_imports",
        "output",
        "output_reporting",
    ),
    module_name=__name__,
)


install_lazy_exports(__name__, globals(), _LAZY_IMPORTS)

__all__: list[str] = [
    "FlextDbOracleApi",
    "FlextDbOracleCli",
    "FlextDbOracleClient",
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
    "c",
    "cli",
    "client",
    "d",
    "db_oracle",
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
