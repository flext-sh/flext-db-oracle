"""FlextDbOracleConfig — frozen config singleton for flext-db-oracle (ADR-005 §7).

Model-less: business rules live in ``config/*.yaml`` under the ``DbOracle:`` key and
are exposed through the open ``config.DbOracle`` namespace (``extra="allow"``), with
no per-domain model. Access is ``config.DbOracle.<domain>[<key>...]``.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import Annotated

from flext_cli import FlextCliConfig, m

from flext_db_oracle._models.base import FlextDbOracleModelsBase


class FlextDbOracleConfig(FlextCliConfig):
    """DbOracle config auto-loaded model-less from ``config/*.yaml``.

    The fleet-converged config inherits only the declared frozen config
    capability base (``config_bases`` precedence: meltano -> cli -> core); the
    adjustable runtime settings keep their own independent ``_settings.py``
    lifecycle.
    """

    DbOracle: Annotated[
        FlextDbOracleModelsBase.ConfigNamespace,
        m.Field(
            description="Open namespace exposing ``config/*.yaml`` under ``DbOracle``.",
        ),
    ] = FlextDbOracleModelsBase.ConfigNamespace()


config: FlextDbOracleConfig = FlextDbOracleConfig.fetch_global()
"""Pre-instantiated frozen config singleton — ``from flext_db_oracle import config``."""

__all__: list[str] = ["FlextDbOracleConfig", "config"]
