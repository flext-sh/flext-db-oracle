"""Oracle Database API with complete FLEXT ecosystem integration.

This API provides a unified interface to Oracle database operations
following FLEXT patterns with complete flext-core integration.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from flext_db_oracle._settings import FlextDbOracleSettings
from flext_db_oracle.services.api_runtime import FlextDbOracleApiRuntime
from flext_db_oracle.services.api_runtime_lifecycle import (
    FlextDbOracleApiRuntimeLifecycle,
)


class FlextDbOracleApi(FlextDbOracleApiRuntime):
    """Unified DB Oracle service facade via MRO composition."""

    def __init__(
        self,
        settings: FlextDbOracleSettings | None = None,
        context_name: str | None = None,
    ) -> None:
        """Initialize facade with explicit settings or the global singleton."""
        resolved = (
            settings if settings is not None else FlextDbOracleSettings.fetch_global()
        )
        # Direct lifecycle-init call: the pydantic-synthesized __init__ on the
        # composite shadows the custom lifecycle signature for the checker,
        # while the MRO binds to it at runtime — name it explicitly so both
        # worlds resolve the same constructor.
        FlextDbOracleApiRuntimeLifecycle.__init__(self, resolved, context_name)


db_oracle: FlextDbOracleApi = FlextDbOracleApi.fetch_global()
"""Process-wide Oracle API facade singleton resolved from the global container."""

__all__: list[str] = ["FlextDbOracleApi", "db_oracle"]
