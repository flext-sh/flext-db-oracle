"""Canonical service facade for flext-db-oracle."""

from __future__ import annotations

from typing import override

from flext_db_oracle import FlextDbOracleServiceBase, FlextDbOracleSettings
from flext_db_oracle.services.connection import FlextDbOracleServiceConnection
from flext_db_oracle.services.plugin import FlextDbOracleServicePlugin
from flext_db_oracle.services.query import FlextDbOracleServiceQuery
from flext_db_oracle.services.schema import FlextDbOracleServiceSchema
from flext_db_oracle.services.singer import FlextDbOracleServiceSinger
from flext_db_oracle.services.sql_builder import FlextDbOracleServiceSqlBuilder


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


__all__: list[str] = ["FlextDbOracleServices"]
