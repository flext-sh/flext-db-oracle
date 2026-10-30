# AUTO-GENERATED FILE — Regenerate with: make gen
"""Oracle Database models using FLEXT ecosystem patterns.

This module provides Oracle-specific models extending flext-core patterns
for data structures and domain objects.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from flext_cli import m

from flext_db_oracle._models import (
    FlextDbOracleCredentialModel,
    FlextModelsDbOracleBase,
    FlextModelsDbOracleCommand,
    FlextModelsDbOracleConnection,
    FlextModelsDbOracleQuery,
    FlextModelsDbOracleSchema,
)


class FlextModelsDbOracle(m):
    """Oracle database models using flext-core exclusively.

    Contains ONLY pure domain models (Entity, Value, AggregateRoot, etc.).
    All settings-like classes moved to settings.py.
    All constants moved to constants.py.
    All types moved to typings.py.
    """

    class DbOracle(
        FlextModelsDbOracleBase,
        FlextModelsDbOracleCommand,
        FlextModelsDbOracleConnection,
        FlextDbOracleCredentialModel,
        FlextModelsDbOracleQuery,
        FlextModelsDbOracleSchema,
    ):
        """DbOracle domain namespace."""


m = FlextModelsDbOracle
__all__: list[str] = ["FlextModelsDbOracle", "m"]
