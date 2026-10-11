"""Canonical service facade for flext-db-oracle.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import override

from flext_db_oracle import (
    FlextDbOracleServiceBase,
    FlextDbOracleServiceConnection,
    FlextDbOracleServicePlugin,
    FlextDbOracleServiceQuery,
    FlextDbOracleServiceSchema,
    FlextDbOracleServiceSinger,
    FlextDbOracleServiceSqlBuilder,
    FlextDbOracleSettings,
    p,
    r,
)


class FlextDbOracleServices(
    FlextDbOracleServicePlugin,
    FlextDbOracleServiceSchema,
    FlextDbOracleServiceSinger,
    FlextDbOracleServiceSqlBuilder,
    FlextDbOracleServiceQuery,
    FlextDbOracleServiceConnection,
):
    """Primary service facade composed from the canonical Oracle mixins."""

    @override
    def __init__(self, settings: FlextDbOracleSettings) -> None:
        """Initialize the composed Oracle services facade."""
        FlextDbOracleServiceBase.__init__(self, settings)

    @property
    @override
    def settings(self) -> FlextDbOracleSettings:
        """The typed Oracle settings bound to this services facade."""
        return self.db_config

    @override
    def execute(self) -> p.Result[p.Base]:
        """Return the active Oracle configuration."""
        return r[p.Base].ok(self.db_config)


__all__: list[str] = ["FlextDbOracleServices"]
