"""Canonical service facade for flext-db-oracle."""

from __future__ import annotations

from typing import TYPE_CHECKING

from flext_db_oracle.base import FlextDbOracleServiceBase
from flext_db_oracle.services.connection import FlextDbOracleServiceConnection
from flext_db_oracle.services.plugin import FlextDbOracleServicePlugin
from flext_db_oracle.services.query import FlextDbOracleServiceQuery
from flext_db_oracle.services.schema import FlextDbOracleServiceSchema
from flext_db_oracle.services.singer import FlextDbOracleServiceSinger
from flext_db_oracle.services.sql_builder import FlextDbOracleServiceSqlBuilder

if TYPE_CHECKING:
    from flext_db_oracle import FlextDbOracleSettings


class FlextDbOracleServices(
    FlextDbOracleServicePlugin,
    FlextDbOracleServiceSchema,
    FlextDbOracleServiceSinger,
    FlextDbOracleServiceSqlBuilder,
    FlextDbOracleServiceQuery,
    FlextDbOracleServiceConnection,
):
    """Primary service facade composed from the canonical Oracle mixins."""

    def __init__(self, settings: FlextDbOracleSettings) -> None:
        """Initialize the composed service facade with Oracle settings."""
        FlextDbOracleServiceBase.__init__(self, settings)


__all__: list[str] = ["FlextDbOracleServices"]
