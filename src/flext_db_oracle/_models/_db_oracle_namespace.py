"""Db oracle namespace module.

Copyright (c) 2026 FLEXT Team. All rights reserved.
src/flext_db_oracle/_models/_db_oracle_namespace
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_db_oracle import m
from flext_db_oracle._config import FlextDbOracleConfig, config, __all__


class _DbOracleNamespace(m.BaseModel):
    """Open, frozen namespace exposing every ``config/*.yaml`` domain model-less."""

    model_config = m.ConfigDict(extra="allow", frozen=True)


class _DbOracleNamespace(m.BaseModel):
    """Open, frozen namespace exposing every ``config/*.yaml`` domain model-less."""

    model_config = m.ConfigDict(extra="allow", frozen=True)
