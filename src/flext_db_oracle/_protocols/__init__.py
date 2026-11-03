# AUTO-GENERATED FILE — Regenerate with: make gen
"""Flext Db Oracle. Protocols package.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from flext_core.lazy import install_lazy_exports

if TYPE_CHECKING:
    from flext_db_oracle._protocols.base import FlextDbOracleProtocolsBase
    from flext_db_oracle._protocols.command_models import (
        FlextDbOracleProtocolsCommandModels,
    )
    from flext_db_oracle._protocols.connection_models import (
        FlextDbOracleProtocolsConnectionModels,
    )
    from flext_db_oracle._protocols.connection_protocols import (
        FlextDbOracleProtocolsConnection,
    )
    from flext_db_oracle._protocols.credential import FlextDbOracleProtocolsCredential
    from flext_db_oracle._protocols.query_models import (
        FlextDbOracleProtocolsQueryModels,
    )
    from flext_db_oracle._protocols.query_protocols import FlextDbOracleProtocolsQuery
    from flext_db_oracle._protocols.schema_models import (
        FlextDbOracleProtocolsSchemaModels,
    )


__all__: tuple[str, ...] = (
    "FlextDbOracleProtocolsBase",
    "FlextDbOracleProtocolsCommandModels",
    "FlextDbOracleProtocolsConnection",
    "FlextDbOracleProtocolsConnectionModels",
    "FlextDbOracleProtocolsCredential",
    "FlextDbOracleProtocolsQuery",
    "FlextDbOracleProtocolsQueryModels",
    "FlextDbOracleProtocolsSchemaModels",
)

install_lazy_exports(
    __name__,
    globals(),
    {
        "FlextDbOracleProtocolsBase": ".base",
        "FlextDbOracleProtocolsCommandModels": ".command_models",
        "FlextDbOracleProtocolsConnection": ".connection_protocols",
        "FlextDbOracleProtocolsConnectionModels": ".connection_models",
        "FlextDbOracleProtocolsCredential": ".credential",
        "FlextDbOracleProtocolsQuery": ".query_protocols",
        "FlextDbOracleProtocolsQueryModels": ".query_models",
        "FlextDbOracleProtocolsSchemaModels": ".schema_models",
    },
    public_exports=__all__,
)
