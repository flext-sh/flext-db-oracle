# AUTO-GENERATED FILE — Regenerate with: make gen
"""Oracle Database models using FLEXT ecosystem patterns.

This module provides Oracle-specific models extending flext-core patterns
for data structures and domain objects.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from typing import ClassVar

from flext_cli import FlextCliModels

from flext_db_oracle._models.command_models import FlextDbOracleModelsCommand
from flext_db_oracle._models.connection_models import FlextDbOracleModelsConnection
from flext_db_oracle._models.credential import FlextDbOracleCredentialModel
from flext_db_oracle._models.query_models import FlextDbOracleModelsQuery
from flext_db_oracle._models.schema_models import FlextDbOracleModelsSchema


class FlextDbOracleModels(FlextCliModels):
    """Oracle database models using flext-core exclusively.

    Contains ONLY pure domain models (Entity, Value, AggregateRoot, etc.).
    All settings-like classes moved to settings.py.
    All constants moved to constants.py.
    All types moved to typings.py.
    """

    class DbOracle(
        FlextDbOracleModelsCommand,
        FlextDbOracleModelsConnection,
        FlextDbOracleModelsQuery,
        FlextDbOracleModelsSchema,
    ):
        """DbOracle domain namespace."""

        Password: ClassVar[type[FlextDbOracleCredentialModel]] = (
            FlextDbOracleCredentialModel
        )


m = FlextDbOracleModels

__all__: list[str] = ["FlextDbOracleModels", "m"]
