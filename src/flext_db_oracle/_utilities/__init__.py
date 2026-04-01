# AUTO-GENERATED FILE — DO NOT EDIT MANUALLY.
# Regenerate with: make gen
#
"""FLEXT DB Oracle utilities submodules."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import TYPE_CHECKING as _TYPE_CHECKING

from flext_core.lazy import install_lazy_exports

if _TYPE_CHECKING:
    from flext_db_oracle.cli import FlextDbOracleCli
    from flext_db_oracle.client import (
        FlextDbOracleClient,
        OracleDatabaseError,
        OracleInterfaceError,
    )
    from flext_db_oracle.services import FlextDbOracleServices, s

_LAZY_IMPORTS: Mapping[str, Sequence[str]] = {
    "FlextDbOracleCli": ["flext_db_oracle.cli", "FlextDbOracleCli"],
    "FlextDbOracleClient": ["flext_db_oracle.client", "FlextDbOracleClient"],
    "FlextDbOracleServices": [
        "flext_db_oracle.services",
        "FlextDbOracleServices",
    ],
    "OracleDatabaseError": ["flext_db_oracle.client", "OracleDatabaseError"],
    "OracleInterfaceError": [
        "flext_db_oracle.client",
        "OracleInterfaceError",
    ],
    "s": ["flext_db_oracle.services", "s"],
}


install_lazy_exports(__name__, globals(), _LAZY_IMPORTS)
