"""Oracle Database API with complete FLEXT ecosystem integration.

This API provides a unified interface to Oracle database operations
following FLEXT patterns with complete flext-core integration.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from typing import TYPE_CHECKING

from flext_db_oracle.services.api_runtime import FlextDbOracleApiRuntime

if TYPE_CHECKING:
    from flext_db_oracle import FlextDbOracleSettings


class FlextDbOracleApi(FlextDbOracleApiRuntime):
    """Unified DB Oracle service facade via MRO composition."""

    def __init__(
        self, settings: FlextDbOracleSettings, context_name: str | None = None
    ) -> None:
        """Initialize facade with explicit runtime constructor contract."""
        super().__init__(settings=settings, context_name=context_name)


db_oracle = FlextDbOracleApi

__all__: list[str] = ["FlextDbOracleApi", "db_oracle"]
