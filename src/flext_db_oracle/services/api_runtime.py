"""Runtime mixin used by the public DB Oracle API facade.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_db_oracle.services.api_runtime_execution import (
    FlextDbOracleApiRuntimeExecution,
)
from flext_db_oracle.services.api_runtime_introspection import (
    FlextDbOracleApiRuntimeIntrospection,
)
from flext_db_oracle.services.api_runtime_lifecycle import (
    FlextDbOracleApiRuntimeLifecycle,
)


class FlextDbOracleApiRuntime(
    FlextDbOracleApiRuntimeLifecycle,
    FlextDbOracleApiRuntimeIntrospection,
    FlextDbOracleApiRuntimeExecution,
):
    """Runtime behavior composed by the public Oracle API facade via MRO."""


__all__: list[str] = ["FlextDbOracleApiRuntime"]
