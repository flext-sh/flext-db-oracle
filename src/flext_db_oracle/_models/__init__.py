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
    from flext_db_oracle._models.base import FlextModelsDbOracleBase
    from flext_db_oracle._models.command_models import FlextModelsDbOracleCommand
    from flext_db_oracle._models.connection_models import FlextModelsDbOracleConnection
    from flext_db_oracle._models.credential import FlextDbOracleCredentialModel
    from flext_db_oracle._models.query_models import FlextModelsDbOracleQuery
    from flext_db_oracle._models.schema_models import FlextModelsDbOracleSchema


__all__: tuple[str, ...] = (
    "FlextDbOracleCredentialModel",
    "FlextModelsDbOracleBase",
    "FlextModelsDbOracleCommand",
    "FlextModelsDbOracleConnection",
    "FlextModelsDbOracleQuery",
    "FlextModelsDbOracleSchema",
)

install_lazy_exports(
    __name__,
    globals(),
    MappingProxyType({
        "FlextDbOracleCredentialModel": ".credential",
        "FlextModelsDbOracleBase": ".base",
        "FlextModelsDbOracleCommand": ".command_models",
        "FlextModelsDbOracleConnection": ".connection_models",
        "FlextModelsDbOracleQuery": ".query_models",
        "FlextModelsDbOracleSchema": ".schema_models",
    }),
    public_exports=__all__,
)
