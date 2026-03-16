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
    from flext_db_oracle.cli import (
        FlextDbOracleCli,
        HealthCheckReport,
        NamedItem,
        OutputPayload,
    )
    from flext_db_oracle.client import FlextDbOracleClient
    from flext_db_oracle.dispatcher import FlextDbOracleDispatcher
    from flext_db_oracle.exceptions import (
        FlextDbOracleExceptions,
        FlextDbOracleExceptions as e,
    )
    from flext_db_oracle.models import FlextDbOracleModels, m
    from flext_db_oracle.protocols import FlextDbOracleProtocols, p
    from flext_db_oracle.services import FlextDbOracleServices
    from flext_db_oracle.settings import (
        FlextDbOracleSettings,
        OracleDatabaseError,
        OracleIdentifier,
        OracleInterfaceError,
        OraclePassword,
    )
    from flext_db_oracle.typings import FlextDbOracleTypes, t
    from flext_db_oracle.utilities import FlextDbOracleUtilities, u

_LAZY_IMPORTS: dict[str, tuple[str, str]] = {
    "FlextDbOracleApi": ("flext_db_oracle.api", "FlextDbOracleApi"),
    "FlextDbOracleCli": ("flext_db_oracle.cli", "FlextDbOracleCli"),
    "FlextDbOracleClient": ("flext_db_oracle.client", "FlextDbOracleClient"),
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
    "HealthCheckReport": ("flext_db_oracle.cli", "HealthCheckReport"),
    "NamedItem": ("flext_db_oracle.cli", "NamedItem"),
    "OracleDatabaseError": ("flext_db_oracle.settings", "OracleDatabaseError"),
    "OracleIdentifier": ("flext_db_oracle.settings", "OracleIdentifier"),
    "OracleInterfaceError": ("flext_db_oracle.settings", "OracleInterfaceError"),
    "OraclePassword": ("flext_db_oracle.settings", "OraclePassword"),
    "OutputPayload": ("flext_db_oracle.cli", "OutputPayload"),
    "__all__": ("flext_db_oracle.__version__", "__all__"),
    "__author__": ("flext_db_oracle.__version__", "__author__"),
    "__author_email__": ("flext_db_oracle.__version__", "__author_email__"),
    "__description__": ("flext_db_oracle.__version__", "__description__"),
    "__license__": ("flext_db_oracle.__version__", "__license__"),
    "__title__": ("flext_db_oracle.__version__", "__title__"),
    "__url__": ("flext_db_oracle.__version__", "__url__"),
    "__version__": ("flext_db_oracle.__version__", "__version__"),
    "__version_info__": ("flext_db_oracle.__version__", "__version_info__"),
    "e": ("flext_db_oracle.exceptions", "FlextDbOracleExceptions"),
    "m": ("flext_db_oracle.models", "m"),
    "p": ("flext_db_oracle.protocols", "p"),
    "t": ("flext_db_oracle.typings", "t"),
    "u": ("flext_db_oracle.utilities", "u"),
}

__all__ = [
    "FlextDbOracleApi",
    "FlextDbOracleCli",
    "FlextDbOracleClient",
    "FlextDbOracleDispatcher",
    "FlextDbOracleExceptions",
    "FlextDbOracleModels",
    "FlextDbOracleProtocols",
    "FlextDbOracleServices",
    "FlextDbOracleSettings",
    "FlextDbOracleTypes",
    "FlextDbOracleUtilities",
    "HealthCheckReport",
    "NamedItem",
    "OracleDatabaseError",
    "OracleIdentifier",
    "OracleInterfaceError",
    "OraclePassword",
    "OutputPayload",
    "__all__",
    "__author__",
    "__author_email__",
    "__description__",
    "__license__",
    "__title__",
    "__url__",
    "__version__",
    "__version_info__",
    "e",
    "m",
    "p",
    "t",
    "u",
]


def __getattr__(name: str) -> FlextTypes.ModuleExport:
    """Lazy-load module attributes on first access (PEP 562)."""
    return lazy_getattr(name, _LAZY_IMPORTS, globals(), __name__)


def __dir__() -> list[str]:
    """Return list of available attributes for dir() and autocomplete."""
    return sorted(__all__)


cleanup_submodule_namespace(__name__, _LAZY_IMPORTS)
