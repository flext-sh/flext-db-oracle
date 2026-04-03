# AUTO-GENERATED FILE — DO NOT EDIT MANUALLY.
# Regenerate with: make gen
#
"""Flext db oracle package."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import TYPE_CHECKING as _TYPE_CHECKING

from flext_core.lazy import install_lazy_exports, merge_lazy_imports
from flext_db_oracle.__version__ import *

if _TYPE_CHECKING:
    from flext_core import FlextTypes
    from flext_core.decorators import FlextDecorators as d
    from flext_core.handlers import FlextHandlers as h
    from flext_core.mixins import FlextMixins as x
    from flext_core.result import FlextResult as r
    from flext_db_oracle import (
        _utilities,
        api,
        cli,
        client,
        constants,
        dispatcher,
        exceptions,
        models,
        protocols,
        service,
        services,
        settings,
        typings,
        utilities,
    )
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
    from flext_db_oracle._utilities import FlextDbOracleUtilitiesDbOracle, db_oracle
    from flext_db_oracle.api import FlextDbOracleApi
    from flext_db_oracle.cli import (
        FlextDbOracleCli,
        OracleDatabaseError,
        OracleInterfaceError,
    )
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
    from flext_db_oracle.protocols import (
        FlextDbOracleProtocols,
        FlextDbOracleProtocols as p,
    )
    from flext_db_oracle.service import FlextDbOracleServices, s
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
    from flext_db_oracle.settings import (
        FlextDbOraclePassword,
        FlextDbOracleSettings,
        OracleIdentifier,
    )
    from flext_db_oracle.typings import FlextDbOracleTypes, FlextDbOracleTypes as t
    from flext_db_oracle.utilities import (
        FlextDbOracleUtilities,
        FlextDbOracleUtilities as u,
    )

_LAZY_IMPORTS: FlextTypes.LazyImportIndex = merge_lazy_imports(
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


install_lazy_exports(__name__, globals(), _LAZY_IMPORTS)
