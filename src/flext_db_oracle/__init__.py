"""Enterprise Oracle Database integration library for FLEXT ecosystem.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_db_oracle.api import FlextDbOracleApi
from flext_db_oracle.client import FlextDbOracleClient
from flext_db_oracle.constants import FlextDbOracleConstants
from flext_db_oracle.exceptions import FlextDbOracleExceptions
from flext_db_oracle.mixins import FlextDbOracleMixins
from flext_db_oracle.models import FlextDbOracleModels
from flext_db_oracle.plugins import FlextDbOraclePlugins
from flext_db_oracle.services import FlextDbOracleServices
from flext_db_oracle.utilities import FlextDbOracleUtilities

# ZERO TOLERANCE: No aliases - use unified classes directly

# Create alias for OracleConfig
OracleConfig = FlextDbOracleModels.OracleConfig

__all__ = [
    "FlextDbOracleApi",
    "FlextDbOracleClient",
    "FlextDbOracleConstants",
    "FlextDbOracleExceptions",
    "FlextDbOracleMixins",
    "FlextDbOracleModels",
    "FlextDbOraclePlugins",
    "FlextDbOracleServices",
    "FlextDbOracleUtilities",
    "OracleConfig",
]
