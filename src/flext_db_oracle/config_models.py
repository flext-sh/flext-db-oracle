"""Layer-zero schemas for YAML-owned Oracle configuration.

Copyright (c) 2026 FLEXT Team. All rights reserved.
src/flext_db_oracle/config_models
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class FlextDbOracleConfigModels:
    """Configuration declarations independent of the model facade."""

    class ConfigNamespace(BaseModel):
        """Open, frozen namespace exposing every ``config/*.yaml`` domain."""

        model_config = ConfigDict(extra="allow", frozen=True)


__all__: list[str] = ["FlextDbOracleConfigModels"]
