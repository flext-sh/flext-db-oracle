"""LEGACY FILE - Use models directly from flext_db_oracle.models."""  # DEPRECATION WARNING

from __future__ import annotations

from .connection import CreateIndexConfig

# LEGACY IMPORTS REMOVED - Use flext_db_oracle.models directly
# from flext_db_oracle.models import FlextDbOracleColumn, FlextDbOracleTable, etc.

__all__: list[str] = [
    "CreateIndexConfig",  # Only non-legacy export
    # ALL LEGACY EXPORTS REMOVED
    # Use models directly: from flext_db_oracle.models import FlextDbOracle*
]
