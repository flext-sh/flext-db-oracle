"""Oracle Database Connection Management."""

from flext_db_oracle.connection.config import ConnectionConfig
from flext_db_oracle.connection.connection import FlextDbOracleConnection
from flext_db_oracle.connection.pool import ConnectionPool, FlextDbOracleConnectionPool
from flext_db_oracle.connection.resilient_connection import (
    FlextDbOracleResilientConnection,
)

__all__ = [
    "ConnectionConfig",
    "ConnectionPool",  # Backward compatibility alias
    "FlextDbOracleConnection",
    "FlextDbOracleConnectionPool",
    "FlextDbOracleResilientConnection",
]
