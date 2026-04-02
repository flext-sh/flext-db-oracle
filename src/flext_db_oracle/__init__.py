# AUTO-GENERATED FILE — DO NOT EDIT MANUALLY.
# Regenerate with: make gen
#
"""Enterprise Oracle Database integration library for FLEXT ecosystem.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import TYPE_CHECKING as _TYPE_CHECKING

from flext_core.lazy import install_lazy_exports, merge_lazy_imports

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

if _TYPE_CHECKING:
    from flext_core import FlextTypes, d, h, r, x

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
    from flext_db_oracle._utilities import FlextDbOracleUtilitiesDbOracle, db_oracle
    from flext_db_oracle.api import FlextDbOracleApi
    from flext_db_oracle.cli import FlextDbOracleCli
    from flext_db_oracle.client import (
        FlextDbOracleClient,
        OracleDatabaseError,
        OracleInterfaceError,
    )
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

_LAZY_IMPORTS: Mapping[str, str | Sequence[str]] = merge_lazy_imports(
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
        "OracleDatabaseError": "flext_db_oracle.client",
        "OracleIdentifier": "flext_db_oracle.settings",
        "OracleInterfaceError": "flext_db_oracle.client",
        "_utilities": "flext_db_oracle._utilities",
        "api": "flext_db_oracle.api",
        "c": ("flext_db_oracle.constants", "FlextDbOracleConstants"),
        "cli": "flext_db_oracle.cli",
        "client": "flext_db_oracle.client",
        "constants": "flext_db_oracle.constants",
        "d": "flext_core",
        "dispatcher": "flext_db_oracle.dispatcher",
        "e": ("flext_db_oracle.exceptions", "FlextDbOracleExceptions"),
        "exceptions": "flext_db_oracle.exceptions",
        "h": "flext_core",
        "m": ("flext_db_oracle.models", "FlextDbOracleModels"),
        "models": "flext_db_oracle.models",
        "p": ("flext_db_oracle.protocols", "FlextDbOracleProtocols"),
        "protocols": "flext_db_oracle.protocols",
        "r": "flext_core",
        "s": "flext_db_oracle.service",
        "service": "flext_db_oracle.service",
        "services": "flext_db_oracle.services",
        "settings": "flext_db_oracle.settings",
        "t": ("flext_db_oracle.typings", "FlextDbOracleTypes"),
        "typings": "flext_db_oracle.typings",
        "u": ("flext_db_oracle.utilities", "FlextDbOracleUtilities"),
        "utilities": "flext_db_oracle.utilities",
        "x": "flext_core",
    },
)


install_lazy_exports(
    __name__,
    globals(),
    _LAZY_IMPORTS,
    [
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
