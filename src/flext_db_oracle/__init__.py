"""Enterprise Oracle Database integration library for FLEXT ecosystem.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_core import FlextTypes  # Import FlextTypes for type safety
from flext_db_oracle.api import FlextDbOracleApi
from flext_db_oracle.cli import FlextDbOracleCliService
from flext_db_oracle.client import FlextDbOracleClient
from flext_db_oracle.config import FlextDbOracleConfig
from flext_db_oracle.constants import FlextDbOracleConstants
from flext_db_oracle.dispatcher import FlextDbOracleDispatcher
from flext_db_oracle.exceptions import FlextDbOracleExceptions
from flext_db_oracle.mixins import FlextDbOracleMixins
from flext_db_oracle.models import FlextDbOracleModels
from flext_db_oracle.plugins import FlextDbOraclePlugins
from flext_db_oracle.protocols import FlextDbOracleProtocols
from flext_db_oracle.services import FlextDbOracleServices
from flext_db_oracle.typings import FlextDbOracleTypes
from flext_db_oracle.utilities import FlextDbOracleUtilities

__all__ = [
    "FlextDbOracleApi",
    "FlextDbOracleCliService",
    "FlextDbOracleClient",
    "FlextDbOracleConfig",
    "FlextDbOracleConstants",
    "FlextDbOracleDispatcher",
    "FlextDbOracleExceptions",
    "FlextDbOracleMixins",
    "FlextDbOracleModels",
    "FlextDbOraclePlugins",
    "FlextDbOracleProtocols",
    "FlextDbOracleServices",
    "FlextDbOracleTypes",
    "FlextDbOracleUtilities",
    "FlextTypes",  # Re-export for convenience
]
