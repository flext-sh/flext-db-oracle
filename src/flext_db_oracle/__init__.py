"""Enterprise Oracle Database integration library for FLEXT ecosystem.

Clean, production-ready Oracle database integration following FLEXT architectural patterns.

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
    FlextDbOracleExceptions,
    OracleConnectionError,
    OracleQueryError,
    OracleValidationError,
)
from flext_db_oracle.mixins import (
    ConnectionParameters,
    ErrorContextTransformer,
    OracleIdentifierValidation,
    OracleValidationFactory,
    ParameterObject,
)
from flext_db_oracle.models import (
    FlextDbOracleModels,
    Column,
    ConnectionStatus,
    CreateIndexConfig,
    MergeStatementConfig,
    OracleConfig,
    QueryResult,
    Schema,
    Table,
)
from flext_db_oracle.plugins import FlextDbOraclePlugins
from flext_db_oracle.services import FlextDbOracleServices
from flext_db_oracle.utilities import FlextDbOracleUtilities

# Main aliases for backward compatibility
FlextDbOracleConfig = OracleConfig

__all__ = [
    # Main classes
    "FlextDbOracleApi",
    "FlextDbOracleClient",
    "FlextDbOracleConstants",
    "FlextDbOracleExceptions",
    "FlextDbOracleModels",
    "FlextDbOraclePlugins",
    "FlextDbOracleServices",
    "FlextDbOracleUtilities",
    # Configuration
    "OracleConfig",
    "FlextDbOracleConfig",
    # Models
    "Column",
    "Table",
    "Schema",
    "QueryResult",
    "ConnectionStatus",
    "CreateIndexConfig",
    "MergeStatementConfig",
    # Mixins
    "ConnectionParameters",
    "ErrorContextTransformer",
    "OracleIdentifierValidation",
    "OracleValidationFactory",
    "ParameterObject",
    # Exceptions
    "OracleConnectionError",
    "OracleQueryError",
    "OracleValidationError",
    # CLI Functions
    "create_oracle_cli_commands",
    "oracle_cli",
]

__version__ = "0.9.0"
__version_info__ = (0, 9, 0)
__author__ = "flext-team"
__description__ = "Modern Oracle Database Integration using SQLAlchemy 2 + oracledb with flext-core patterns"
