"""Oracle Database Domain Layer.

Following flext-core DDD patterns.
"""

from flext_db_oracle.domain.models import (
    FlextDbOracleColumnInfo,
    FlextDbOracleConnectionInfo,
    FlextDbOracleConnectionStatus,
    FlextDbOracleQueryResult,
    FlextDbOracleSchemaInfo,
    FlextDbOracleTableMetadata,
)

__all__ = [
    "FlextDbOracleColumnInfo",
    "FlextDbOracleConnectionInfo",
    "FlextDbOracleConnectionStatus",
    "FlextDbOracleQueryResult",
    "FlextDbOracleSchemaInfo",
    "FlextDbOracleTableMetadata",
]
