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
    from flext_core.decorators import d
    from flext_core.handlers import h
    from flext_core.mixins import x
    from flext_core.result import r
    from flext_db_oracle._utilities.db_oracle import FlextDbOracleUtilitiesDbOracle
    from flext_db_oracle.api import FlextDbOracleApi
    from flext_db_oracle.cli import FlextDbOracleCli
    from flext_db_oracle.client import FlextDbOracleClient
    from flext_db_oracle.constants import (
        FlextDbOracleConstants,
        FlextDbOracleConstants as c,
    )
    from flext_db_oracle.dispatcher import FlextDbOracleDispatcher
    from flext_db_oracle.exceptions import (
        FlextDbOracleExceptions,
        FlextDbOracleExceptions as e,
    )
    from flext_db_oracle.models import FlextDbOracleModels, FlextDbOracleModels as m
    from flext_db_oracle.password import FlextDbOraclePassword
    from flext_db_oracle.protocols import (
        FlextDbOracleProtocols,
        FlextDbOracleProtocols as p,
    )
    from flext_db_oracle.service import FlextDbOracleServices
    from flext_db_oracle.services.base import (
        FlextDbOracleServiceBase,
        FlextDbOracleServiceBase as s,
    )
    from flext_db_oracle.services.connection import FlextDbOracleServiceConnection
    from flext_db_oracle.services.plugin import FlextDbOracleServicePlugin
    from flext_db_oracle.services.query import FlextDbOracleServiceQuery
    from flext_db_oracle.services.schema import FlextDbOracleServiceSchema
    from flext_db_oracle.services.singer import FlextDbOracleServiceSinger
    from flext_db_oracle.services.sql_builder import FlextDbOracleServiceSqlBuilder
    from flext_db_oracle.settings import FlextDbOracleSettings
    from flext_db_oracle.typings import FlextDbOracleTypes, FlextDbOracleTypes as t
    from flext_db_oracle.utilities import (
        FlextDbOracleUtilities,
        FlextDbOracleUtilities as u,
    )
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
            ".cli": ("FlextDbOracleCli",),
            ".client": ("FlextDbOracleClient",),
            ".constants": ("FlextDbOracleConstants",),
            ".dispatcher": ("FlextDbOracleDispatcher",),
            ".exceptions": ("FlextDbOracleExceptions",),
            ".models": ("FlextDbOracleModels",),
            ".password": ("FlextDbOraclePassword",),
            ".protocols": ("FlextDbOracleProtocols",),
            ".service": ("FlextDbOracleServices",),
            ".settings": ("FlextDbOracleSettings",),
            ".typings": ("FlextDbOracleTypes",),
            ".utilities": ("FlextDbOracleUtilities",),
            "flext_core.decorators": ("d",),
            "flext_core.handlers": ("h",),
            "flext_core.mixins": ("x",),
            "flext_core.result": ("r",),
        },
        alias_groups={
            ".constants": (("c", "FlextDbOracleConstants"),),
            ".exceptions": (("e", "FlextDbOracleExceptions"),),
            ".models": (("m", "FlextDbOracleModels"),),
            ".protocols": (("p", "FlextDbOracleProtocols"),),
            ".typings": (("t", "FlextDbOracleTypes"),),
            ".utilities": (("u", "FlextDbOracleUtilities"),),
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


install_lazy_exports(__name__, globals(), _LAZY_IMPORTS)
