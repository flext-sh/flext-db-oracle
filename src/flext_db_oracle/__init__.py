# AUTO-GENERATED FILE — DO NOT EDIT MANUALLY.
# Regenerate with: make gen
#
"""Flext db oracle package."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import TYPE_CHECKING as _TYPE_CHECKING

from flext_core.lazy import install_lazy_exports, merge_lazy_imports
from flext_db_oracle.__version__ import (
    __all__,
    __author__,
    __author_email__,
    __description__,
    __license__,
    __title__,
    __url__,
    __version__,
    __version_info__,
)

if _TYPE_CHECKING:
    from flext_core import FlextTypes
    from flext_core.decorators import FlextDecorators as d
    from flext_core.handlers import FlextHandlers as h
    from flext_core.mixins import FlextMixins as x
    from flext_core.result import FlextResult as r
    from flext_db_oracle import (
        _utilities,
        api,
        base,
        cli,
        client,
        connection,
        constants,
        db_oracle,
        dispatcher,
        exceptions,
        models,
        plugin,
        protocols,
        query,
        schema,
        service,
        services,
        settings,
        singer,
        sql_builder,
        typings,
        utilities,
    )
    from flext_db_oracle._utilities import FlextDbOracleUtilitiesDbOracle
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
    )
    from flext_db_oracle.settings import (
        FlextDbOraclePassword,
        FlextDbOracleSettings,
        OracleDatabaseError,
        OracleIdentifier,
        OracleInterfaceError,
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
        "FlextDbOracleSettings": "flext_db_oracle.settings",
        "FlextDbOracleProtocols": "flext_db_oracle.protocols",
        "FlextDbOracleServices": "flext_db_oracle.service",
        "FlextDbOracleTypes": "flext_db_oracle.typings",
        "FlextDbOracleUtilities": "flext_db_oracle.utilities",
        "OracleDatabaseError": "flext_db_oracle.settings",
        "OracleIdentifier": "flext_db_oracle.settings",
        "OracleInterfaceError": "flext_db_oracle.settings",
        "_utilities": "flext_db_oracle._utilities",
        "api": "flext_db_oracle.api",
        "base": "flext_db_oracle.base",
        "c": ("flext_db_oracle.constants", "FlextDbOracleConstants"),
        "cli": "flext_db_oracle.cli",
        "client": "flext_db_oracle.client",
        "connection": "flext_db_oracle.connection",
        "constants": "flext_db_oracle.constants",
        "d": ("flext_core.decorators", "FlextDecorators"),
        "db_oracle": "flext_db_oracle.db_oracle",
        "dispatcher": "flext_db_oracle.dispatcher",
        "e": ("flext_db_oracle.exceptions", "FlextDbOracleExceptions"),
        "exceptions": "flext_db_oracle.exceptions",
        "h": ("flext_core.handlers", "FlextHandlers"),
        "m": ("flext_db_oracle.models", "FlextDbOracleModels"),
        "models": "flext_db_oracle.models",
        "p": ("flext_db_oracle.protocols", "FlextDbOracleProtocols"),
        "plugin": "flext_db_oracle.plugin",
        "protocols": "flext_db_oracle.protocols",
        "query": "flext_db_oracle.query",
        "r": ("flext_core.result", "FlextResult"),
        "s": "flext_db_oracle.service",
        "schema": "flext_db_oracle.schema",
        "service": "flext_db_oracle.service",
        "services": "flext_db_oracle.services",
        "settings": "flext_db_oracle.settings",
        "singer": "flext_db_oracle.singer",
        "sql_builder": "flext_db_oracle.sql_builder",
        "t": ("flext_db_oracle.typings", "FlextDbOracleTypes"),
        "typings": "flext_db_oracle.typings",
        "u": ("flext_db_oracle.utilities", "FlextDbOracleUtilities"),
        "utilities": "flext_db_oracle.utilities",
        "x": ("flext_core.mixins", "FlextMixins"),
    },
)


install_lazy_exports(
    __name__,
    globals(),
    _LAZY_IMPORTS,
    [
        "__all__",
        "__author__",
        "__author_email__",
        "__description__",
        "__license__",
        "__title__",
        "__url__",
        "__version__",
        "__version_info__",
    ],
)
