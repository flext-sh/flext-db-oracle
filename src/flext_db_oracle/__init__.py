"""Enterprise Oracle Database integration library for FLEXT ecosystem.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from typing import TYPE_CHECKING

from flext_core.lazy import cleanup_submodule_namespace, lazy_getattr

if TYPE_CHECKING:
    from flext_db_oracle.__version__ import __version__, __version_info__
    from flext_db_oracle.api import FlextDbOracleApi
    from flext_db_oracle.cli import FlextDbOracleCli
    from flext_db_oracle.client import FlextDbOracleClient
    from flext_db_oracle.constants import (
        FlextDbOracleConstants,
        FlextDbOracleConstants as c,
    )
    from flext_db_oracle.dispatcher import FlextDbOracleDispatcher
    from flext_db_oracle.exceptions import FlextDbOracleExceptions
    from flext_db_oracle.models import FlextDbOracleModels, FlextDbOracleModels as m
    from flext_db_oracle.protocols import (
        FlextDbOracleProtocols,
        FlextDbOracleProtocols as p,
    )
    from flext_db_oracle.services import FlextDbOracleServices
    from flext_db_oracle.settings import FlextDbOracleSettings
    from flext_db_oracle.typings import FlextDbOracleTypes, FlextDbOracleTypes as t
    from flext_db_oracle.utilities import (
        FlextDbOracleUtilities,
        FlextDbOracleUtilities as u,
    )

# Lazy import mapping: export_name -> (module_path, attr_name)
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
    "__version__": ("flext_db_oracle.__version__", "__version__"),
    "__version_info__": ("flext_db_oracle.__version__", "__version_info__"),
    "c": ("flext_db_oracle.constants", "FlextDbOracleConstants"),
    "m": ("flext_db_oracle.models", "FlextDbOracleModels"),
    "p": ("flext_db_oracle.protocols", "FlextDbOracleProtocols"),
    "t": ("flext_db_oracle.typings", "FlextDbOracleTypes"),
    "u": ("flext_db_oracle.utilities", "FlextDbOracleUtilities"),
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
    "__version__",
    "__version_info__",
    "c",
    "m",
    "p",
    "t",
    "u",
]


def __getattr__(name: str) -> object:
    """Lazy-load module attributes on first access (PEP 562)."""
    return lazy_getattr(name, _LAZY_IMPORTS, globals(), __name__)


def __dir__() -> list[str]:
    """Return list of available attributes for dir() and autocomplete."""
    return sorted(__all__)


cleanup_submodule_namespace(__name__, _LAZY_IMPORTS)
