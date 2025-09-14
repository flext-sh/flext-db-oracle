"""Enterprise Oracle Database integration library for FLEXT ecosystem.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_db_oracle.api import FlextDbOracleApi
from flext_db_oracle.cli import FlextDbOracleCliService
from flext_db_oracle.client import (
    FlextDbOracleClient,
    create_oracle_cli_commands,
    get_client,
    oracle_cli,
)
from flext_db_oracle.constants import FlextDbOracleConstants
from flext_db_oracle.exceptions import (
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

FlextDbOracleConfig = FlextDbOracleModels.OracleConfig

__all__ = [
    "Column",
    "ConnectionParameters",
    "ConnectionStatus",
    "CreateIndexConfig",
    "ErrorContextTransformer",
    "FlextDbOracleApi",
    "FlextDbOracleCliService",
    "FlextDbOracleClient",
    "FlextDbOracleConfig",
    "FlextDbOracleConstants",
    "FlextDbOracleExceptions",
    "FlextDbOracleModels",
    "FlextDbOraclePlugins",
    "FlextDbOracleServices",
    "FlextDbOracleUtilities",
    "MergeStatementConfig",
    "OracleConfig",
    "OracleConnectionError",
    "OracleIdentifierValidation",
    "OracleQueryError",
    "OracleValidationError",
    "ParameterObject",
    "QueryResult",
    "Schema",
    "Table",
    "create_oracle_cli_commands",
    "get_client",
    "oracle_cli",
]
