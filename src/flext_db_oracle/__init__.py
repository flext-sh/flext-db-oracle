# AUTO-GENERATED FILE — DO NOT EDIT MANUALLY.
# Regenerate with: make gen
#
"""Enterprise Oracle Database integration library for FLEXT ecosystem.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from collections.abc import Mapping, MutableMapping, Sequence
from typing import TYPE_CHECKING

from flext_core.lazy import cleanup_submodule_namespace, lazy_getattr

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
    from flext_core import FlextTypes, d, h, r, x

    from flext_db_oracle import (
        api,
        cli,
        client,
        constants,
        dispatcher,
        exceptions,
        models,
        protocols,
        services,
        settings,
        typings,
        utilities,
    )
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
    from flext_db_oracle.services import FlextDbOracleServices, s
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


_LAZY_CACHE: MutableMapping[str, FlextTypes.ModuleExport] = {}


def __getattr__(name: str) -> FlextTypes.ModuleExport:
    """Lazy-load module attributes on first access (PEP 562).

    A local cache ``_LAZY_CACHE`` persists resolved objects across repeated
    accesses during process lifetime.

    Args:
        name: Attribute name requested by dir()/import.

    Returns:
        Lazy-loaded module export type.

    Raises:
        AttributeError: If attribute not registered.

    """
    if name in _LAZY_CACHE:
        return _LAZY_CACHE[name]

    value = lazy_getattr(name, _LAZY_IMPORTS, globals(), __name__)
    _LAZY_CACHE[name] = value
    return value


def __dir__() -> Sequence[str]:
    """Return list of available attributes for dir() and autocomplete.

    Returns:
        List of public names from module exports.

    """
    return sorted(__all__)


cleanup_submodule_namespace(__name__, _LAZY_IMPORTS)
