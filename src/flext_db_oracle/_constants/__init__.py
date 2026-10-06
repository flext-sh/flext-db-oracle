# AUTO-GENERATED FILE — Regenerate with: make gen
"""Flext Db Oracle. Constants package.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from types import MappingProxyType
from typing import TYPE_CHECKING

from flext_core import install_lazy_exports

if TYPE_CHECKING:
    from flext_db_oracle._constants.base import FlextDbOracleConstantsBase
    from flext_db_oracle._constants.exceptions import FlextDbOracleConstantsExceptions
    from flext_db_oracle._constants.values import FlextDbOracleConstantsValues


__all__: tuple[str, ...] = (
    "FlextDbOracleConstantsBase",
    "FlextDbOracleConstantsExceptions",
    "FlextDbOracleConstantsValues",
)

install_lazy_exports(
    __name__,
    globals(),
    MappingProxyType({
        "FlextDbOracleConstantsBase": ".base",
        "FlextDbOracleConstantsExceptions": ".exceptions",
        "FlextDbOracleConstantsValues": ".values",
    }),
    public_exports=__all__,
)
