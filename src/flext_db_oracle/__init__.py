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

# Main facade alias following FLEXT pattern
FlextDbOracle = FlextDbOracleApi

# Export nested model classes for convenience
FlextDbOracleColumn = FlextDbOracleModels.Column
FlextDbOracleQueryResult = FlextDbOracleModels.QueryResult
FlextDbOracleSchema = FlextDbOracleModels.Schema
FlextDbOracleTable = FlextDbOracleModels.Table

# Export type aliases for tap-oracle compatibility
FlextDbOracleConnection = FlextDbOracleTypes.Connection
FlextDbOracleMetadataManager = FlextDbOracleApi  # Metadata operations in API
FlextDbOracleObservabilityManager = FlextDbOracleApi  # Observability operations in API

__all__ = [
    "FlextDbOracle",  # Main facade
    "FlextDbOracleApi",  # Implementation
    "FlextDbOracleCliService",
    "FlextDbOracleClient",
    "FlextDbOracleColumn",
    "FlextDbOracleConfig",
    "FlextDbOracleConnection",
    "FlextDbOracleConstants",
    "FlextDbOracleDispatcher",
    "FlextDbOracleExceptions",
    "FlextDbOracleMetadataManager",
    "FlextDbOracleMixins",
    "FlextDbOracleModels",
    "FlextDbOracleObservabilityManager",
    "FlextDbOraclePlugins",
    "FlextDbOracleProtocols",
    "FlextDbOracleQueryResult",
    "FlextDbOracleSchema",
    "FlextDbOracleServices",
    "FlextDbOracleTable",
    "FlextDbOracleTypes",
    "FlextDbOracleUtilities",
    "FlextTypes",  # Re-export for convenience
]
