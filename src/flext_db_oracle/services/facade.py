"""Canonical service facade for flext-db-oracle."""

from __future__ import annotations

from typing import override

from flext_db_oracle import (
    FlextDbOracleServiceConnection,
    FlextDbOracleServicePlugin,
    FlextDbOracleServiceQuery,
    FlextDbOracleServiceSchema,
    FlextDbOracleServiceSinger,
    FlextDbOracleServiceSqlBuilder,
    FlextDbOracleSettings,
    m,
    p,
    r,
    s,
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
        super(s, self).__init__()
        self._db_config = settings
        self._config = settings
        self._engine = None
        self._operations = list[m.DbOracle.OperationRecord]()
        self._plugins = dict[str, t.ContainerValue]()
        self._metrics = dict[str, t.ContainerValue]()

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
