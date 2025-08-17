"""Legacy shim: centralized definitions moved to `typings.py`."""

from __future__ import annotations

from .connection import CreateIndexConfig
from .typings import (
    FlextDbOracleColumn,
    FlextDbOracleConnectionStatus,
    FlextDbOracleQueryResult,
    FlextDbOracleSchema,
    FlextDbOracleTable,
    TDbOracleColumn,
    TDbOracleConnectionStatus,
    TDbOracleQueryResult,
    TDbOracleSchema,
    TDbOracleTable,
)

__all__: list[str] = [
    "CreateIndexConfig",
    "FlextDbOracleColumn",
    "FlextDbOracleConnectionStatus",
    "FlextDbOracleQueryResult",
    "FlextDbOracleSchema",
    "FlextDbOracleTable",
    "TDbOracleColumn",
    "TDbOracleConnectionStatus",
    "TDbOracleQueryResult",
    "TDbOracleSchema",
    "TDbOracleTable",
]
