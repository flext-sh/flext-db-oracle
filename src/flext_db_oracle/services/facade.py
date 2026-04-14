"""Canonical service facade for flext-db-oracle."""

from __future__ import annotations

from typing import override

from flext_db_oracle import m, p, r, t
from flext_db_oracle.base import FlextDbOracleServiceBase
from flext_db_oracle.services.connection import FlextDbOracleServiceConnection
from flext_db_oracle.services.plugin import FlextDbOracleServicePlugin
from flext_db_oracle.services.query import FlextDbOracleServiceQuery
from flext_db_oracle.services.schema import FlextDbOracleServiceSchema
from flext_db_oracle.services.singer import FlextDbOracleServiceSinger
from flext_db_oracle.services.sql_builder import FlextDbOracleServiceSqlBuilder
from flext_db_oracle.settings import FlextDbOracleSettings


class FlextDbOracleServices(
    FlextDbOracleServicePlugin,
    FlextDbOracleServiceSchema,
    FlextDbOracleServiceSinger,
    FlextDbOracleServiceSqlBuilder,
    FlextDbOracleServiceQuery,
    FlextDbOracleServiceConnection,
    FlextDbOracleServiceBase,
):
    """Primary service facade composed from the canonical Oracle mixins."""

    @override
    def __init__(self, settings: FlextDbOracleSettings) -> None:
        """Initialize the composed Oracle services facade."""
        super(FlextDbOracleServiceBase, self).__init__()
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
