"""Enterprise Oracle Database integration library for FLEXT ecosystem.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_db_oracle.api import FlextDbOracleApi
from flext_db_oracle.client import (
    FlextDbOracleClient,
    create_oracle_cli_commands,
    oracle_cli,
)
from flext_db_oracle.constants import FlextDbOracleConstants
from flext_db_oracle.exceptions import (
    ExceptionParams,
    FlextDbOracleExceptions,
    OracleConnectionError,
    OracleQueryError,
    OracleValidationError,
)
from flext_db_oracle.mixins import (
    ConnectionParameters,
    ErrorContextTransformer,
    OracleIdentifierValidation,
    ParameterObject,
)
from flext_db_oracle.models import (
    Column,
    ConnectionStatus,
    CreateIndexConfig,
    FlextDbOracleModels,
    MergeStatementConfig,
    OracleConfig,
    QueryResult,
    Schema,
    Table,
)
from flext_db_oracle.plugins import FlextDbOraclePlugins
from flext_db_oracle.services import FlextDbOracleServices
from flext_db_oracle.utilities import FlextDbOracleUtilities

# CLI integration - oracle_cli is already imported from client module

__all__ = [
    "Column",
    "ConnectionParameters",
    "ConnectionStatus",
    "CreateIndexConfig",
    "ErrorContextTransformer",
    "ExceptionParams",
    # Main API components
    "FlextDbOracleApi",
    "FlextDbOracleClient",
    "FlextDbOracleColumn",
    "FlextDbOracleConfig",
    "FlextDbOracleConnection",
    # Exceptions
    "FlextDbOracleConnectionError",
    "FlextDbOracleConstants",
    "FlextDbOracleError",
    "FlextDbOracleExceptions",
    "FlextDbOracleMetadataManager",
    "FlextDbOracleModels",
    "FlextDbOracleObservabilityManager",
    "FlextDbOracleOperationTracker",
    "FlextDbOraclePlugins",
    "FlextDbOracleQueryResult",
    "FlextDbOracleSchema",
    "FlextDbOracleServices",
    "FlextDbOracleTable",
    "FlextDbOracleUtilities",
    "MergeStatementConfig",
    "OracleConfig",
    # Connection and models
    "OracleConnection",
    "OracleConnectionError",
    # Mixins
    "OracleConnectionMixin",
    "OracleIdentifierValidation",
    "OracleQueryError",
    "OracleQueryMixin",
    "OracleValidationError",
    "ParameterObject",
    "QueryResult",
    "Schema",
    "Table",
    "create_oracle_cli_commands",
    # CLI
    "main",
    "oracle_cli",
    # Compatibility functions
    "oracle_connect",
    "oracle_query",
]
