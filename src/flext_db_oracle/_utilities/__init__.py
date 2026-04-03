# AUTO-GENERATED FILE — DO NOT EDIT MANUALLY.
# Regenerate with: make gen
#
"""Utilities package."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import TYPE_CHECKING as _TYPE_CHECKING

from flext_core.lazy import install_lazy_exports

if _TYPE_CHECKING:
    from flext_core import FlextTypes
    from flext_db_oracle._utilities import db_oracle
    from flext_db_oracle._utilities.db_oracle import FlextDbOracleUtilitiesDbOracle

_LAZY_IMPORTS: FlextTypes.LazyImportIndex = {
    "FlextDbOracleUtilitiesDbOracle": "flext_db_oracle._utilities.db_oracle",
    "db_oracle": "flext_db_oracle._utilities.db_oracle",
}


install_lazy_exports(__name__, globals(), _LAZY_IMPORTS)
