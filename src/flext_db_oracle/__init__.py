# AUTO-GENERATED FILE — DO NOT EDIT MANUALLY.
# Regenerate with: make gen
#
"""Flext db oracle package."""

from __future__ import annotations

import typing as _t

from flext_core.lazy import install_lazy_exports, merge_lazy_imports
from flext_db_oracle.__version__ import *

if _t.TYPE_CHECKING:
    import flext_db_oracle._utilities as _flext_db_oracle__utilities

    _utilities = _flext_db_oracle__utilities
    import flext_db_oracle.api as _flext_db_oracle_api
    from flext_db_oracle._utilities import FlextDbOracleUtilitiesDbOracle

    api = _flext_db_oracle_api
    import flext_db_oracle.cli as _flext_db_oracle_cli
    from flext_db_oracle.api import FlextDbOracleApi

    cli = _flext_db_oracle_cli
    import flext_db_oracle.client as _flext_db_oracle_client
    from flext_db_oracle.cli import FlextDbOracleCli

    client = _flext_db_oracle_client
    import flext_db_oracle.constants as _flext_db_oracle_constants
    from flext_db_oracle.client import FlextDbOracleClient

    constants = _flext_db_oracle_constants
    import flext_db_oracle.dispatcher as _flext_db_oracle_dispatcher
    from flext_db_oracle.constants import (
        FlextDbOracleConstants,
        FlextDbOracleConstants as c,
    )

    dispatcher = _flext_db_oracle_dispatcher
    import flext_db_oracle.exceptions as _flext_db_oracle_exceptions
    from flext_db_oracle.dispatcher import FlextDbOracleDispatcher

    exceptions = _flext_db_oracle_exceptions
    import flext_db_oracle.models as _flext_db_oracle_models
    from flext_db_oracle.exceptions import (
        FlextDbOracleExceptions,
        FlextDbOracleExceptions as e,
    )

    models = _flext_db_oracle_models
    import flext_db_oracle.protocols as _flext_db_oracle_protocols
    from flext_db_oracle.models import FlextDbOracleModels, FlextDbOracleModels as m

    protocols = _flext_db_oracle_protocols
    import flext_db_oracle.service as _flext_db_oracle_service
    from flext_db_oracle.protocols import (
        FlextDbOracleProtocols,
        FlextDbOracleProtocols as p,
    )

    service = _flext_db_oracle_service
    import flext_db_oracle.settings as _flext_db_oracle_settings
    from flext_db_oracle.service import FlextDbOracleServices, s
    from flext_db_oracle.services.base import FlextDbOracleServiceBase
    from flext_db_oracle.services.connection import FlextDbOracleServiceConnection
    from flext_db_oracle.services.plugin import FlextDbOracleServicePlugin
    from flext_db_oracle.services.query import FlextDbOracleServiceQuery
    from flext_db_oracle.services.schema import FlextDbOracleServiceSchema
    from flext_db_oracle.services.singer import FlextDbOracleServiceSinger
    from flext_db_oracle.services.sql_builder import FlextDbOracleServiceSqlBuilder

    settings = _flext_db_oracle_settings
    import flext_db_oracle.typings as _flext_db_oracle_typings
    from flext_db_oracle.settings import (
        FlextDbOraclePassword,
        FlextDbOracleSettings,
        OracleIdentifier,
    )

    typings = _flext_db_oracle_typings
    import flext_db_oracle.utilities as _flext_db_oracle_utilities
    from flext_db_oracle.typings import FlextDbOracleTypes, FlextDbOracleTypes as t

    utilities = _flext_db_oracle_utilities
    from flext_core.decorators import FlextDecorators as d
    from flext_core.handlers import FlextHandlers as h
    from flext_core.mixins import FlextMixins as x
    from flext_core.result import FlextResult as r
    from flext_db_oracle.utilities import (
        FlextDbOracleUtilities,
        FlextDbOracleUtilities as u,
    )
_LAZY_IMPORTS = merge_lazy_imports(
    ("flext_db_oracle._utilities",),
    {
        "FlextDbOracleApi": ("flext_db_oracle.api", "FlextDbOracleApi"),
        "FlextDbOracleCli": ("flext_db_oracle.cli", "FlextDbOracleCli"),
        "FlextDbOracleClient": ("flext_db_oracle.client", "FlextDbOracleClient"),
        "FlextDbOracleConstants": (
            "flext_db_oracle.constants",
            "FlextDbOracleConstants",
        ),
        "FlextDbOracleDispatcher": (
            "flext_db_oracle.dispatcher",
            "FlextDbOracleDispatcher",
        ),
        "FlextDbOracleExceptions": (
            "flext_db_oracle.exceptions",
            "FlextDbOracleExceptions",
        ),
        "FlextDbOracleModels": ("flext_db_oracle.models", "FlextDbOracleModels"),
        "FlextDbOraclePassword": ("flext_db_oracle.settings", "FlextDbOraclePassword"),
        "FlextDbOracleProtocols": (
            "flext_db_oracle.protocols",
            "FlextDbOracleProtocols",
        ),
        "FlextDbOracleServiceBase": (
            "flext_db_oracle.services.base",
            "FlextDbOracleServiceBase",
        ),
        "FlextDbOracleServiceConnection": (
            "flext_db_oracle.services.connection",
            "FlextDbOracleServiceConnection",
        ),
        "FlextDbOracleServicePlugin": (
            "flext_db_oracle.services.plugin",
            "FlextDbOracleServicePlugin",
        ),
        "FlextDbOracleServiceQuery": (
            "flext_db_oracle.services.query",
            "FlextDbOracleServiceQuery",
        ),
        "FlextDbOracleServiceSchema": (
            "flext_db_oracle.services.schema",
            "FlextDbOracleServiceSchema",
        ),
        "FlextDbOracleServiceSinger": (
            "flext_db_oracle.services.singer",
            "FlextDbOracleServiceSinger",
        ),
        "FlextDbOracleServiceSqlBuilder": (
            "flext_db_oracle.services.sql_builder",
            "FlextDbOracleServiceSqlBuilder",
        ),
        "FlextDbOracleServices": ("flext_db_oracle.service", "FlextDbOracleServices"),
        "FlextDbOracleSettings": ("flext_db_oracle.settings", "FlextDbOracleSettings"),
        "FlextDbOracleTypes": ("flext_db_oracle.typings", "FlextDbOracleTypes"),
        "FlextDbOracleUtilities": (
            "flext_db_oracle.utilities",
            "FlextDbOracleUtilities",
        ),
        "OracleIdentifier": ("flext_db_oracle.settings", "OracleIdentifier"),
        "__author__": ("flext_db_oracle.__version__", "__author__"),
        "__author_email__": ("flext_db_oracle.__version__", "__author_email__"),
        "__description__": ("flext_db_oracle.__version__", "__description__"),
        "__license__": ("flext_db_oracle.__version__", "__license__"),
        "__title__": ("flext_db_oracle.__version__", "__title__"),
        "__url__": ("flext_db_oracle.__version__", "__url__"),
        "__version__": ("flext_db_oracle.__version__", "__version__"),
        "__version_info__": ("flext_db_oracle.__version__", "__version_info__"),
        "_utilities": "flext_db_oracle._utilities",
        "api": "flext_db_oracle.api",
        "c": ("flext_db_oracle.constants", "FlextDbOracleConstants"),
        "cli": "flext_db_oracle.cli",
        "client": "flext_db_oracle.client",
        "constants": "flext_db_oracle.constants",
        "d": ("flext_core.decorators", "FlextDecorators"),
        "dispatcher": "flext_db_oracle.dispatcher",
        "e": ("flext_db_oracle.exceptions", "FlextDbOracleExceptions"),
        "exceptions": "flext_db_oracle.exceptions",
        "h": ("flext_core.handlers", "FlextHandlers"),
        "m": ("flext_db_oracle.models", "FlextDbOracleModels"),
        "models": "flext_db_oracle.models",
        "p": ("flext_db_oracle.protocols", "FlextDbOracleProtocols"),
        "protocols": "flext_db_oracle.protocols",
        "r": ("flext_core.result", "FlextResult"),
        "s": ("flext_db_oracle.service", "s"),
        "service": "flext_db_oracle.service",
        "settings": "flext_db_oracle.settings",
        "t": ("flext_db_oracle.typings", "FlextDbOracleTypes"),
        "typings": "flext_db_oracle.typings",
        "u": ("flext_db_oracle.utilities", "FlextDbOracleUtilities"),
        "utilities": "flext_db_oracle.utilities",
        "x": ("flext_core.mixins", "FlextMixins"),
    },
)
_ = _LAZY_IMPORTS.pop("cleanup_submodule_namespace", None)
_ = _LAZY_IMPORTS.pop("install_lazy_exports", None)
_ = _LAZY_IMPORTS.pop("lazy_getattr", None)
_ = _LAZY_IMPORTS.pop("merge_lazy_imports", None)
_ = _LAZY_IMPORTS.pop("output", None)
_ = _LAZY_IMPORTS.pop("output_reporting", None)

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
    "OracleIdentifier",
    "__author__",
    "__author_email__",
    "__description__",
    "__license__",
    "__title__",
    "__url__",
    "__version__",
    "__version_info__",
    "_utilities",
    "api",
    "c",
    "cli",
    "client",
    "constants",
    "d",
    "dispatcher",
    "e",
    "exceptions",
    "h",
    "m",
    "models",
    "p",
    "protocols",
    "r",
    "s",
    "service",
    "settings",
    "t",
    "typings",
    "u",
    "utilities",
    "x",
]


install_lazy_exports(__name__, globals(), _LAZY_IMPORTS)
