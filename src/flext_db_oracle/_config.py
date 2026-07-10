"""FlextDbOracleConfig — frozen config singleton for flext-db-oracle (ADR-005 §7).

Model-less: business rules live in ``config/*.yaml`` under the ``DbOracle:`` key and
are exposed through the open ``config.DbOracle`` namespace (``extra="allow"``), with
no per-domain model. Access is ``config.DbOracle.<domain>[<key>...]``.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict

from flext_cli import FlextCliConfig


class _DbOracleNamespace(BaseModel):
    """Open, frozen namespace exposing every ``config/*.yaml`` domain model-less."""

    model_config = ConfigDict(extra="allow", frozen=True)


class FlextDbOracleConfig(FlextCliConfig):
    """DbOracle config auto-loaded model-less from ``config/*.yaml``."""

    DbOracle: _DbOracleNamespace = _DbOracleNamespace()


config: FlextDbOracleConfig = FlextDbOracleConfig.fetch_global()
"""Pre-instantiated frozen config singleton — ``from flext_db_oracle import config``."""

__all__: list[str] = ["FlextDbOracleConfig", "config"]
