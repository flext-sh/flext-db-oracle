"""Canonical service facade for flext-db-oracle."""

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
    t,
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
        """Return the typed Oracle settings bound to this services facade."""
        return self.db_config

    @override
    def execute(self, **_kwargs: t.Scalar) -> p.Result[FlextDbOracleSettings]:
        """Return the active Oracle configuration as the default service result."""
        return r[FlextDbOracleSettings].ok(self.db_config)


__all__: list[str] = ["FlextDbOracleServices"]
