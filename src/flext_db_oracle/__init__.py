"""flext-db-oracle - Oracle Database Integration using SQLAlchemy 2 + oracledb.

Modern Oracle database library with comprehensive functionality built on flext-core patterns.
All classes use FlextDbOracle prefix to supplement (not replace) flext-core functionality.

Example Usage:
    from flext_db_oracle import (
        FlextDbOracleApi,
        FlextDbOracleConfig,
        FlextDbOracleConnection,
    )

    # Basic usage
    config = FlextDbOracleConfig.from_env()
    api = FlextDbOracleApi(config).connect()
    result = api.query("SELECT * FROM employees")
"""

# Core components using SQLAlchemy 2 and flext-core
from .api import FlextDbOracleApi
from .config import FlextDbOracleConfig
from .connection import FlextDbOracleConnection

# Additional components
from .metadata import (
    FlextDbOracleColumn,
    FlextDbOracleMetadataManager,
    FlextDbOracleSchema,
    FlextDbOracleTable,
)
from .types import (
    TDbOracleColumn,
    TDbOracleConnectionStatus,
    TDbOracleQueryResult,
    TDbOracleSchema,
    TDbOracleTable,
)

__all__ = [
    # Core API
    "FlextDbOracleApi",
    # Metadata
    "FlextDbOracleColumn",
    "FlextDbOracleConfig",
    "FlextDbOracleConnection",
    "FlextDbOracleMetadataManager",
    "FlextDbOracleSchema",
    "FlextDbOracleTable",
    # Types
    "TDbOracleColumn",
    "TDbOracleConnectionStatus",
    "TDbOracleQueryResult",
    "TDbOracleSchema",
    "TDbOracleTable",
]

__version__ = "2.0.0"
__author__ = "flext-team"
__description__ = "Modern Oracle Database Integration using SQLAlchemy 2 + oracledb with flext-core patterns"
