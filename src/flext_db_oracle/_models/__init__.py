# AUTO-GENERATED FILE — Regenerate with: make gen
"""Flext Db Oracle. Models package.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from types import MappingProxyType
from typing import TYPE_CHECKING

from flext_core.lazy import install_lazy_exports

if TYPE_CHECKING:
    from flext_db_oracle._models.base import FlextDbOracleModelsBase
    from flext_db_oracle._models.command_models import FlextDbOracleModelsCommand
    from flext_db_oracle._models.connection_models import FlextDbOracleModelsConnection
    from flext_db_oracle._models.credential import FlextDbOracleCredentialModel
    from flext_db_oracle._models.query_models import FlextDbOracleModelsQuery
    from flext_db_oracle._models.schema_models import FlextDbOracleModelsSchema


__all__: tuple[str, ...] = (
    "FlextDbOracleCredentialModel",
    "FlextDbOracleModelsBase",
    "FlextDbOracleModelsCommand",
    "FlextDbOracleModelsConnection",
    "FlextDbOracleModelsQuery",
    "FlextDbOracleModelsSchema",
)

install_lazy_exports(
    __name__,
    globals(),
    MappingProxyType({
        "FlextDbOracleCredentialModel": ".credential",
        "FlextDbOracleModelsBase": ".base",
        "FlextDbOracleModelsCommand": ".command_models",
        "FlextDbOracleModelsConnection": ".connection_models",
        "FlextDbOracleModelsQuery": ".query_models",
        "FlextDbOracleModelsSchema": ".schema_models",
    }),
    public_exports=__all__,
)
