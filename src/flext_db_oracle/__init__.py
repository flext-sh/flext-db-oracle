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
    from flext_db_oracle._utilities import FlextDbOracleUtilitiesDbOracle, db_oracle

    api = _flext_db_oracle_api
    import flext_db_oracle.cli as _flext_db_oracle_cli
    from flext_db_oracle.api import FlextDbOracleApi

    cli = _flext_db_oracle_cli
    import flext_db_oracle.client as _flext_db_oracle_client
    from flext_db_oracle.cli import (
        FlextDbOracleCli,
        OracleDatabaseError,
        OracleInterfaceError,
    )

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
    import flext_db_oracle.services as _flext_db_oracle_services
    from flext_db_oracle.service import FlextDbOracleServices, s

    services = _flext_db_oracle_services
    import flext_db_oracle.settings as _flext_db_oracle_settings
    from flext_db_oracle.services import (
        FlextDbOracleServiceBase,
        FlextDbOracleServiceConnection,
        FlextDbOracleServicePlugin,
        FlextDbOracleServiceQuery,
        FlextDbOracleServiceSchema,
        FlextDbOracleServiceSinger,
        FlextDbOracleServiceSqlBuilder,
        base,
        connection,
        plugin,
        query,
        schema,
        singer,
        sql_builder,
    )

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
    (
        "flext_db_oracle._utilities",
        "flext_db_oracle.services",
    ),
    {
        "FlextDbOracleApi": "flext_db_oracle.api",
        "FlextDbOracleCli": "flext_db_oracle.cli",
        "FlextDbOracleClient": "flext_db_oracle.client",
        "FlextDbOracleConstants": "flext_db_oracle.constants",
        "FlextDbOracleDispatcher": "flext_db_oracle.dispatcher",
        "FlextDbOracleExceptions": "flext_db_oracle.exceptions",
        "FlextDbOracleModels": "flext_db_oracle.models",
        "FlextDbOraclePassword": "flext_db_oracle.settings",
        "FlextDbOracleProtocols": "flext_db_oracle.protocols",
        "FlextDbOracleServices": "flext_db_oracle.service",
        "FlextDbOracleSettings": "flext_db_oracle.settings",
        "FlextDbOracleTypes": "flext_db_oracle.typings",
        "FlextDbOracleUtilities": "flext_db_oracle.utilities",
        "OracleDatabaseError": "flext_db_oracle.cli",
        "OracleIdentifier": "flext_db_oracle.settings",
        "OracleInterfaceError": "flext_db_oracle.cli",
        "__author__": "flext_db_oracle.__version__",
        "__author_email__": "flext_db_oracle.__version__",
        "__description__": "flext_db_oracle.__version__",
        "__license__": "flext_db_oracle.__version__",
        "__title__": "flext_db_oracle.__version__",
        "__url__": "flext_db_oracle.__version__",
        "__version__": "flext_db_oracle.__version__",
        "__version_info__": "flext_db_oracle.__version__",
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
        "s": "flext_db_oracle.service",
        "service": "flext_db_oracle.service",
        "services": "flext_db_oracle.services",
        "settings": "flext_db_oracle.settings",
        "t": ("flext_db_oracle.typings", "FlextDbOracleTypes"),
        "typings": "flext_db_oracle.typings",
        "u": ("flext_db_oracle.utilities", "FlextDbOracleUtilities"),
        "utilities": "flext_db_oracle.utilities",
        "x": ("flext_core.mixins", "FlextMixins"),
    },
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
    "OracleDatabaseError",
    "OracleIdentifier",
    "OracleInterfaceError",
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
    "base",
    "c",
    "cli",
    "client",
    "connection",
    "constants",
    "d",
    "db_oracle",
    "dispatcher",
    "e",
    "exceptions",
    "h",
    "m",
    "models",
    "p",
    "plugin",
    "protocols",
    "query",
    "r",
    "s",
    "schema",
    "service",
    "services",
    "settings",
    "singer",
    "sql_builder",
    "t",
    "typings",
    "u",
    "utilities",
    "x",
]


install_lazy_exports(__name__, globals(), _LAZY_IMPORTS)
