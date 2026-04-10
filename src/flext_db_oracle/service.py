"""Service facade for flext-db-oracle.

Public MRO composition over all DB Oracle service mixins.
Composition lives at the package boundary, not inside ``services/``.
"""

from __future__ import annotations

from flext_db_oracle import (
    FlextDbOracleServiceBase,
    FlextDbOracleServiceConnection,
    FlextDbOracleServicePlugin,
    FlextDbOracleServiceQuery,
    FlextDbOracleServiceSchema,
    FlextDbOracleServiceSinger,
    FlextDbOracleServiceSqlBuilder,
    FlextDbOracleSettings,
)


class FlextDbOracleServices(
    FlextDbOracleServicePlugin,
    FlextDbOracleServiceSchema,
    FlextDbOracleServiceSinger,
    FlextDbOracleServiceSqlBuilder,
    FlextDbOracleServiceQuery,
    FlextDbOracleServiceConnection,
    FlextDbOracleServiceBase,
):
    """Unified DB Oracle service facade via MRO composition."""

    def __init__(self, config: FlextDbOracleSettings) -> None:
        """Initialize the composed DB Oracle service facade."""
        FlextDbOracleServiceBase.__init__(self, config)
