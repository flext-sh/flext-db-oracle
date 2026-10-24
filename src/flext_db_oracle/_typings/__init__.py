# AUTO-GENERATED FILE — Regenerate with: make gen
"""Flext Db Oracle. Typings package.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from types import MappingProxyType
from typing import TYPE_CHECKING

from flext_core.lazy import install_lazy_exports

if TYPE_CHECKING:
    from flext_db_oracle._typings.base import FlextDbOracleTypingsBase
    from flext_db_oracle._typings.db_oracle import (
        CliScalar,
        OracleDatabaseError,
        OracleInterfaceError,
        QueryParameters,
        Settings,
    )


__all__: tuple[str, ...] = (
    "CliScalar",
    "FlextDbOracleTypingsBase",
    "OracleDatabaseError",
    "OracleInterfaceError",
    "QueryParameters",
    "Settings",
)

install_lazy_exports(
    __name__,
    globals(),
    MappingProxyType({
        "CliScalar": ".db_oracle",
        "FlextDbOracleTypingsBase": ".base",
        "OracleDatabaseError": ".db_oracle",
        "OracleInterfaceError": ".db_oracle",
        "QueryParameters": ".db_oracle",
        "Settings": ".db_oracle",
    }),
    public_exports=__all__,
)
