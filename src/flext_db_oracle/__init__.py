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

from flext_core.lazy import install_lazy_exports

if _TYPE_CHECKING:
    from flext_core import d, h, r, x

    from flext_db_oracle.__version__ import *
    from flext_db_oracle.api import *
    from flext_db_oracle.cli import *
    from flext_db_oracle.client import *
    from flext_db_oracle.constants import *
    from flext_db_oracle.dispatcher import *
    from flext_db_oracle.exceptions import *
    from flext_db_oracle.models import *
    from flext_db_oracle.protocols import *
    from flext_db_oracle.services import *
    from flext_db_oracle.settings import *
    from flext_db_oracle.typings import *
    from flext_db_oracle.utilities import *

_LAZY_IMPORTS: Mapping[str, str | Sequence[str]] = {
    "FlextDbOracleApi": "flext_db_oracle.api",
    "FlextDbOracleCli": "flext_db_oracle.cli",
    "FlextDbOracleClient": "flext_db_oracle.client",
    "FlextDbOracleConstants": "flext_db_oracle.constants",
    "FlextDbOracleDispatcher": "flext_db_oracle.dispatcher",
    "FlextDbOracleExceptions": "flext_db_oracle.exceptions",
    "FlextDbOracleModels": "flext_db_oracle.models",
    "FlextDbOraclePassword": "flext_db_oracle.settings",
    "FlextDbOracleProtocols": "flext_db_oracle.protocols",
    "FlextDbOracleServices": "flext_db_oracle.services",
    "FlextDbOracleSettings": "flext_db_oracle.settings",
    "FlextDbOracleTypes": "flext_db_oracle.typings",
    "FlextDbOracleUtilities": "flext_db_oracle.utilities",
    "OracleDatabaseError": "flext_db_oracle.client",
    "OracleIdentifier": "flext_db_oracle.settings",
    "OracleInterfaceError": "flext_db_oracle.client",
    "__author__": "flext_db_oracle.__version__",
    "__author_email__": "flext_db_oracle.__version__",
    "__description__": "flext_db_oracle.__version__",
    "__license__": "flext_db_oracle.__version__",
    "__title__": "flext_db_oracle.__version__",
    "__url__": "flext_db_oracle.__version__",
    "__version__": "flext_db_oracle.__version__",
    "__version_info__": "flext_db_oracle.__version__",
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
    "s": "flext_db_oracle.services",
    "services": "flext_db_oracle.services",
    "settings": "flext_db_oracle.settings",
    "t": ("flext_db_oracle.typings", "FlextDbOracleTypes"),
    "typings": "flext_db_oracle.typings",
    "u": ("flext_db_oracle.utilities", "FlextDbOracleUtilities"),
    "utilities": "flext_db_oracle.utilities",
    "x": "flext_core",
}


install_lazy_exports(__name__, globals(), _LAZY_IMPORTS)
