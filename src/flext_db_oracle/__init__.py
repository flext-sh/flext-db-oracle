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
    from _utilities.db_oracle import FlextDbOracleUtilitiesDbOracle
    from flext_cli.base import s

    from flext_core.decorators import d
    from flext_core.handlers import h
    from flext_core.mixins import x
    from flext_core.result import r
    from flext_db_oracle.api import FlextDbOracleApi
    from flext_db_oracle.base import FlextDbOracleServiceBase
    from flext_db_oracle.cli import FlextDbOracleCli
    from flext_db_oracle.client import FlextDbOracleClient
    from flext_db_oracle.connection import FlextDbOracleServiceConnection
    from flext_db_oracle.constants import FlextDbOracleConstants, c
    from flext_db_oracle.dispatcher import FlextDbOracleDispatcher
    from flext_db_oracle.exceptions import FlextDbOracleExceptions, e
    from flext_db_oracle.models import FlextDbOracleModels, m
    from flext_db_oracle.password import FlextDbOraclePassword
    from flext_db_oracle.plugin import FlextDbOracleServicePlugin
    from flext_db_oracle.protocols import FlextDbOracleProtocols, p
    from flext_db_oracle.query import FlextDbOracleServiceQuery
    from flext_db_oracle.schema import FlextDbOracleServiceSchema
    from flext_db_oracle.service import FlextDbOracleServices
    from flext_db_oracle.settings import FlextDbOracleSettings
    from flext_db_oracle.singer import FlextDbOracleServiceSinger
    from flext_db_oracle.sql_builder import FlextDbOracleServiceSqlBuilder
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
            ".api": ("FlextDbOracleApi",),
            ".base": ("FlextDbOracleServiceBase",),
            ".cli": ("FlextDbOracleCli",),
            ".client": ("FlextDbOracleClient",),
            ".connection": ("FlextDbOracleServiceConnection",),
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
            ".plugin": ("FlextDbOracleServicePlugin",),
            ".protocols": (
                "FlextDbOracleProtocols",
                "p",
            ),
            ".query": ("FlextDbOracleServiceQuery",),
            ".schema": ("FlextDbOracleServiceSchema",),
            ".service": ("FlextDbOracleServices",),
            ".settings": ("FlextDbOracleSettings",),
            ".singer": ("FlextDbOracleServiceSinger",),
            ".sql_builder": ("FlextDbOracleServiceSqlBuilder",),
            ".typings": (
                "FlextDbOracleTypes",
                "t",
            ),
            ".utilities": (
                "FlextDbOracleUtilities",
                "u",
            ),
            "_utilities.db_oracle": ("FlextDbOracleUtilitiesDbOracle",),
            "flext_cli.base": ("s",),
            "flext_core.decorators": ("d",),
            "flext_core.handlers": ("h",),
            "flext_core.mixins": ("x",),
            "flext_core.result": ("r",),
        },
    ),
    exclude_names=(
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

__all__ = [
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
