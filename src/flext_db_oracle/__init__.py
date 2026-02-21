"""Enterprise Oracle Database integration library for FLEXT ecosystem.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from flext_db_oracle.__version__ import __version__, __version_info__
from flext_db_oracle.api import FlextDbOracleApi
from flext_db_oracle.cli import FlextDbOracleCli
from flext_db_oracle.client import FlextDbOracleClient
from flext_db_oracle.constants import FlextDbOracleConstants
from flext_db_oracle.dispatcher import FlextDbOracleDispatcher
from flext_db_oracle.exceptions import FlextDbOracleExceptions
from flext_db_oracle.models import FlextDbOracleModels, m
from flext_db_oracle.protocols import FlextDbOracleProtocols, p
from flext_db_oracle.services import FlextDbOracleServices
from flext_db_oracle.settings import FlextDbOracleSettings
from flext_db_oracle.typings import FlextDbOracleTypes, t
from flext_db_oracle.utilities import FlextDbOracleUtilities

# NO ALIASES - STRICT RULE: only use direct imports from respective modules
# All usage must be: from flext_db_oracle.api import FlextDbOracleApi
# NOT: from flext_db_oracle import FlextDbOracle

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
    "m",
    "p",
    "t",
]
