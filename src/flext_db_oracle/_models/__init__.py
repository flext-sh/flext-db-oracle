# AUTO-GENERATED FILE — Regenerate with: make gen
"""Flext Db Oracle. Models package.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from types import MappingProxyType
from typing import TYPE_CHECKING

from flext_core import install_lazy_exports

if TYPE_CHECKING:
    from flext_db_oracle._models._db_oracle_namespace import (
        FlextDbOracleModelsDbOracleNamespace,
    )
    from flext_db_oracle._models.base import FlextDbOracleModelsBase
    from flext_db_oracle._models.credential import FlextDbOracleCredentialModel


__all__: tuple[str, ...] = (
    "FlextDbOracleCredentialModel",
    "FlextDbOracleModelsBase",
    "FlextDbOracleModelsDbOracleNamespace",
)

install_lazy_exports(
    __name__,
    globals(),
    MappingProxyType({
        "FlextDbOracleCredentialModel": ".credential",
        "FlextDbOracleModelsBase": ".base",
        "FlextDbOracleModelsDbOracleNamespace": "._db_oracle_namespace",
    }),
    public_exports=__all__,
)
