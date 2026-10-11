"""Runtime mixin used by the public DB Oracle API facade.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_db_oracle import (
    FlextDbOracleApiRuntimeExecution,
    FlextDbOracleApiRuntimeIntrospection,
    FlextDbOracleApiRuntimeLifecycle,
)


class FlextDbOracleApiRuntime(
    FlextDbOracleApiRuntimeLifecycle,
    FlextDbOracleApiRuntimeIntrospection,
    FlextDbOracleApiRuntimeExecution,
):
    """Runtime behavior composed by the public Oracle API facade via MRO."""


__all__: list[str] = ["FlextDbOracleApiRuntime"]
