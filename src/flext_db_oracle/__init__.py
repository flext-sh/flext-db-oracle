# AUTO-GENERATED FILE — DO NOT EDIT MANUALLY.
# Regenerate with: make gen
#
"""Enterprise Oracle Database integration library for FLEXT ecosystem.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import TYPE_CHECKING

from flext_core.lazy import install_lazy_exports

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
    from flext_db_oracle import (
        api as api,
        cli as cli,
        client as client,
        constants as constants,
        dispatcher as dispatcher,
        exceptions as exceptions,
        models as models,
        protocols as protocols,
        services as services,
        settings as settings,
        typings as typings,
        utilities as utilities,
    )
    from flext_db_oracle.api import FlextDbOracleApi as FlextDbOracleApi
    from flext_db_oracle.cli import FlextDbOracleCli as FlextDbOracleCli
    from flext_db_oracle.client import (
        FlextDbOracleClient as FlextDbOracleClient,
        OracleDatabaseError as OracleDatabaseError,
        OracleInterfaceError as OracleInterfaceError,
    )
    from flext_db_oracle.constants import (
        FlextDbOracleConstants as FlextDbOracleConstants,
        FlextDbOracleConstants as c,
    )
    from flext_db_oracle.dispatcher import (
        FlextDbOracleDispatcher as FlextDbOracleDispatcher,
    )
    from flext_db_oracle.exceptions import (
        FlextDbOracleExceptions as FlextDbOracleExceptions,
        FlextDbOracleExceptions as e,
    )
    from flext_db_oracle.models import (
        FlextDbOracleModels as FlextDbOracleModels,
        FlextDbOracleModels as m,
    )
    from flext_db_oracle.protocols import (
        FlextDbOracleProtocols as FlextDbOracleProtocols,
        FlextDbOracleProtocols as p,
    )
    from flext_db_oracle.services import (
        FlextDbOracleServices as FlextDbOracleServices,
        s as s,
    )
    from flext_db_oracle.settings import (
        FlextDbOraclePassword as FlextDbOraclePassword,
        FlextDbOracleSettings as FlextDbOracleSettings,
        OracleIdentifier as OracleIdentifier,
    )
    from flext_db_oracle.typings import (
        FlextDbOracleTypes as FlextDbOracleTypes,
        FlextDbOracleTypes as t,
    )
    from flext_db_oracle.utilities import (
        FlextDbOracleUtilities as FlextDbOracleUtilities,
        FlextDbOracleUtilities as u,
    )

_LAZY_IMPORTS: Mapping[str, Sequence[str]] = {
    "FlextDbOracleApi": ["flext_db_oracle.api", "FlextDbOracleApi"],
    "FlextDbOracleCli": ["flext_db_oracle.cli", "FlextDbOracleCli"],
    "FlextDbOracleClient": ["flext_db_oracle.client", "FlextDbOracleClient"],
    "FlextDbOracleConstants": ["flext_db_oracle.constants", "FlextDbOracleConstants"],
    "FlextDbOracleDispatcher": [
        "flext_db_oracle.dispatcher",
        "FlextDbOracleDispatcher",
    ],
    "FlextDbOracleExceptions": [
        "flext_db_oracle.exceptions",
        "FlextDbOracleExceptions",
    ],
    "FlextDbOracleModels": ["flext_db_oracle.models", "FlextDbOracleModels"],
    "FlextDbOraclePassword": ["flext_db_oracle.settings", "FlextDbOraclePassword"],
    "FlextDbOracleProtocols": ["flext_db_oracle.protocols", "FlextDbOracleProtocols"],
    "FlextDbOracleServices": ["flext_db_oracle.services", "FlextDbOracleServices"],
    "FlextDbOracleSettings": ["flext_db_oracle.settings", "FlextDbOracleSettings"],
    "FlextDbOracleTypes": ["flext_db_oracle.typings", "FlextDbOracleTypes"],
    "FlextDbOracleUtilities": ["flext_db_oracle.utilities", "FlextDbOracleUtilities"],
    "OracleDatabaseError": ["flext_db_oracle.client", "OracleDatabaseError"],
    "OracleIdentifier": ["flext_db_oracle.settings", "OracleIdentifier"],
    "OracleInterfaceError": ["flext_db_oracle.client", "OracleInterfaceError"],
    "api": ["flext_db_oracle.api", ""],
    "c": ["flext_db_oracle.constants", "FlextDbOracleConstants"],
    "cli": ["flext_db_oracle.cli", ""],
    "client": ["flext_db_oracle.client", ""],
    "constants": ["flext_db_oracle.constants", ""],
    "d": ["flext_core", "d"],
    "dispatcher": ["flext_db_oracle.dispatcher", ""],
    "e": ["flext_db_oracle.exceptions", "FlextDbOracleExceptions"],
    "exceptions": ["flext_db_oracle.exceptions", ""],
    "h": ["flext_core", "h"],
    "m": ["flext_db_oracle.models", "FlextDbOracleModels"],
    "models": ["flext_db_oracle.models", ""],
    "p": ["flext_db_oracle.protocols", "FlextDbOracleProtocols"],
    "protocols": ["flext_db_oracle.protocols", ""],
    "r": ["flext_core", "r"],
    "s": ["flext_db_oracle.services", "s"],
    "services": ["flext_db_oracle.services", ""],
    "settings": ["flext_db_oracle.settings", ""],
    "t": ["flext_db_oracle.typings", "FlextDbOracleTypes"],
    "typings": ["flext_db_oracle.typings", ""],
    "u": ["flext_db_oracle.utilities", "FlextDbOracleUtilities"],
    "utilities": ["flext_db_oracle.utilities", ""],
    "x": ["flext_core", "x"],
}

_EXPORTS: Sequence[str] = [
    "FlextDbOracleApi",
    "FlextDbOracleCli",
    "FlextDbOracleClient",
    "FlextDbOracleConstants",
    "FlextDbOracleDispatcher",
    "FlextDbOracleExceptions",
    "FlextDbOracleModels",
    "FlextDbOraclePassword",
    "FlextDbOracleProtocols",
    "FlextDbOracleServices",
    "FlextDbOracleSettings",
    "FlextDbOracleTypes",
    "FlextDbOracleUtilities",
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
    "services",
    "settings",
    "t",
    "typings",
    "u",
    "utilities",
    "x",
]


install_lazy_exports(__name__, globals(), _LAZY_IMPORTS, _EXPORTS)
