"""Oracle Database Domain Layer.

Following flext-core DDD patterns.
"""

from flext_db_oracle.domain.models import (
    OracleColumnInfo,
    OracleConnectionInfo,
    OracleConnectionStatus,
    OracleQueryResult,
    OracleSchemaInfo,
    OracleTableMetadata,
)

__all__ = [
    "OracleColumnInfo",
    "OracleConnectionInfo",
    "OracleConnectionStatus",
    "OracleQueryResult",
    "OracleSchemaInfo",
    "OracleTableMetadata",
]
