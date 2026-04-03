# AUTO-GENERATED FILE — DO NOT EDIT MANUALLY.
# Regenerate with: make gen
#
"""Utilities package."""

from __future__ import annotations

import typing as _t

from flext_core.lazy import install_lazy_exports
from flext_db_oracle._utilities.db_oracle import FlextDbOracleUtilitiesDbOracle

if _t.TYPE_CHECKING:
    import flext_db_oracle._utilities.db_oracle as _flext_db_oracle__utilities_db_oracle

    db_oracle = _flext_db_oracle__utilities_db_oracle

    _ = (
        FlextDbOracleUtilitiesDbOracle,
        db_oracle,
    )
_LAZY_IMPORTS = {
    "FlextDbOracleUtilitiesDbOracle": "flext_db_oracle._utilities.db_oracle",
    "db_oracle": "flext_db_oracle._utilities.db_oracle",
}

__all__ = [
    "FlextDbOracleUtilitiesDbOracle",
    "db_oracle",
]


install_lazy_exports(__name__, globals(), _LAZY_IMPORTS)
