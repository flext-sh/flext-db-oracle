# AUTO-GENERATED FILE — DO NOT EDIT MANUALLY.
# Regenerate with: make codegen
#
"""Enterprise Oracle Database integration library for FLEXT ecosystem.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from typing import TYPE_CHECKING

from flext_core.lazy import cleanup_submodule_namespace, lazy_getattr

if TYPE_CHECKING:
    from flext_core import d, h, r, s, x
    from flext_core.typings import FlextTypes

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
    from flext_db_oracle.services import FlextDbOracleServices
    from flext_db_oracle.settings import (
        FlextDbOracleSettings,
        OracleIdentifier,
        OraclePassword,
    )
    from flext_db_oracle.typings import FlextDbOracleTypes, FlextDbOracleTypes as t
    from flext_db_oracle.utilities import (
        FlextDbOracleUtilities,
        FlextDbOracleUtilities as u,
    )

_LAZY_IMPORTS: dict[str, tuple[str, str]] = {
    "FlextDbOracleApi": ("flext_db_oracle.api", "FlextDbOracleApi"),
    "FlextDbOracleCli": ("flext_db_oracle.cli", "FlextDbOracleCli"),
    "FlextDbOracleClient": ("flext_db_oracle.client", "FlextDbOracleClient"),
    "FlextDbOracleConstants": ("flext_db_oracle.constants", "FlextDbOracleConstants"),
    "FlextDbOracleDispatcher": (
        "flext_db_oracle.dispatcher",
        "FlextDbOracleDispatcher",
    ),
    "FlextDbOracleExceptions": (
        "flext_db_oracle.exceptions",
        "FlextDbOracleExceptions",
    ),
    "FlextDbOracleModels": ("flext_db_oracle.models", "FlextDbOracleModels"),
    "FlextDbOracleProtocols": ("flext_db_oracle.protocols", "FlextDbOracleProtocols"),
    "FlextDbOracleServices": ("flext_db_oracle.services", "FlextDbOracleServices"),
    "FlextDbOracleSettings": ("flext_db_oracle.settings", "FlextDbOracleSettings"),
    "FlextDbOracleTypes": ("flext_db_oracle.typings", "FlextDbOracleTypes"),
    "FlextDbOracleUtilities": ("flext_db_oracle.utilities", "FlextDbOracleUtilities"),
    "OracleDatabaseError": ("flext_db_oracle.client", "OracleDatabaseError"),
    "OracleIdentifier": ("flext_db_oracle.settings", "OracleIdentifier"),
    "OracleInterfaceError": ("flext_db_oracle.client", "OracleInterfaceError"),
    "OraclePassword": ("flext_db_oracle.settings", "OraclePassword"),
    "__all__": ("flext_db_oracle.__version__", "__all__"),
    "__author__": ("flext_db_oracle.__version__", "__author__"),
    "__author_email__": ("flext_db_oracle.__version__", "__author_email__"),
    "__description__": ("flext_db_oracle.__version__", "__description__"),
    "__license__": ("flext_db_oracle.__version__", "__license__"),
    "__title__": ("flext_db_oracle.__version__", "__title__"),
    "__url__": ("flext_db_oracle.__version__", "__url__"),
    "__version__": ("flext_db_oracle.__version__", "__version__"),
    "__version_info__": ("flext_db_oracle.__version__", "__version_info__"),
    "c": ("flext_db_oracle.constants", "FlextDbOracleConstants"),
    "d": ("flext_core", "d"),
    "e": ("flext_db_oracle.exceptions", "FlextDbOracleExceptions"),
    "h": ("flext_core", "h"),
    "m": ("flext_db_oracle.models", "FlextDbOracleModels"),
    "p": ("flext_db_oracle.protocols", "FlextDbOracleProtocols"),
    "r": ("flext_core", "r"),
    "s": ("flext_core", "s"),
    "t": ("flext_db_oracle.typings", "FlextDbOracleTypes"),
    "u": ("flext_db_oracle.utilities", "FlextDbOracleUtilities"),
    "x": ("flext_core", "x"),
}

__all__ = [
    "FlextDbOracleApi",
    "FlextDbOracleCli",
    "FlextDbOracleClient",
    "FlextDbOracleConstants",
    "FlextDbOracleDispatcher",
    "FlextDbOracleExceptions",
    "FlextDbOracleModels",
    "FlextDbOracleProtocols",
    "FlextDbOracleServices",
    "FlextDbOracleSettings",
    "FlextDbOracleTypes",
    "FlextDbOracleUtilities",
    "OracleDatabaseError",
    "OracleIdentifier",
    "OracleInterfaceError",
    "OraclePassword",
    "__all__",
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


_LAZY_CACHE: dict[str, FlextTypes.ModuleExport] = {}


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


def __dir__() -> list[str]:
    """Return list of available attributes for dir() and autocomplete.

    Returns:
        List of public names from module exports.

    """
    return sorted(__all__)


cleanup_submodule_namespace(__name__, _LAZY_IMPORTS)
