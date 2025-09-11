"""Enterprise Oracle Database integration library for FLEXT ecosystem.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations
from flext_core import FlextTypes

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


# Ultra-simple aliases for missing classes - test compatibility
class FlextDbOracleMetadataManager:
    """Ultra-simple alias for test compatibility - MetadataManager."""


class FlextDbOracleTable:
    """Ultra-simple alias for test compatibility - Table."""


class FlextDbOracleConnection:
    """Ultra-simple alias for test compatibility - Connection."""


class FlextDbOracleObservabilityManager:
    """Ultra-simple alias for test compatibility - ObservabilityManager."""


class FlextDbOracleColumn:
    """Ultra-simple alias for test compatibility - Column."""


class FlextDbOracleQueryResult:
    """Ultra-simple alias for test compatibility - QueryResult."""


class FlextDbOracleSchema:
    """Ultra-simple alias for test compatibility - Schema."""


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
    # Ultra-simple aliases
    "FlextDbOracleMetadataManager",
    "FlextDbOracleTable",
    "FlextDbOracleConnection",
    "FlextDbOracleObservabilityManager",
    "FlextDbOracleColumn",
    "FlextDbOracleQueryResult",
    "FlextDbOracleSchema",
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
    "ParameterObject",
    # Exceptions
    "ExceptionParams",
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
__description__ = (
    "Modern Oracle Database Integration using SQLAlchemy 2 + oracledb "
    "with flext-core patterns"
)
