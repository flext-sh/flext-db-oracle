"""FlextDbOracleConfig — frozen, validated config singleton for flext-db-oracle.

Every ``config/*.yaml`` file is auto-discovered and deep-merged at first
``fetch_global`` call (model-less, ``extra=allow`` at the FlextConfig base).
The flat YAML is then validated into the pure-Pydantic ``_models.config``
shapes and exposed as typed domain objects under ``config.DbOracle`` — never a
model-less dict subscript.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from functools import cached_property
from pathlib import Path
from typing import ClassVar

from flext_cli import FlextCliConfig
from flext_db_oracle._models.config import FlextDbOracleConfigModels


class FlextDbOracleConfig(FlextCliConfig):
    """DbOracle config auto-loaded from ``config/*.yaml`` and validated via models."""

    CONFIG_DIR: ClassVar[str] = str(Path(__file__).resolve().parent / "config")

    @cached_property
    def DbOracle(self) -> FlextDbOracleConfigModels.DbOracle:
        """Validated ``DbOracle`` business-rule config namespace."""
        root = FlextDbOracleConfigModels.Root.model_validate(
            dict(self.model_extra or {})
        )
        return root.DbOracle


config: FlextDbOracleConfig = FlextDbOracleConfig.fetch_global()
"""Pre-instantiated frozen config singleton — ``from flext_db_oracle import config``."""

__all__: list[str] = ["FlextDbOracleConfig", "config"]
