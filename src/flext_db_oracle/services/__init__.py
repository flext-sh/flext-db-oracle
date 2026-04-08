# AUTO-GENERATED FILE — DO NOT EDIT MANUALLY.
# Regenerate with: make gen
#
"""Services package."""

from __future__ import annotations

from flext_core.lazy import install_lazy_exports

_LAZY_IMPORTS = {
    "FlextDbOracleServiceBase": (
        "flext_db_oracle.services.base",
        "FlextDbOracleServiceBase",
    ),
    "FlextDbOracleServiceConnection": (
        "flext_db_oracle.services.connection",
        "FlextDbOracleServiceConnection",
    ),
    "FlextDbOracleServicePlugin": (
        "flext_db_oracle.services.plugin",
        "FlextDbOracleServicePlugin",
    ),
    "FlextDbOracleServiceQuery": (
        "flext_db_oracle.services.query",
        "FlextDbOracleServiceQuery",
    ),
    "FlextDbOracleServiceSchema": (
        "flext_db_oracle.services.schema",
        "FlextDbOracleServiceSchema",
    ),
    "FlextDbOracleServiceSinger": (
        "flext_db_oracle.services.singer",
        "FlextDbOracleServiceSinger",
    ),
    "FlextDbOracleServiceSqlBuilder": (
        "flext_db_oracle.services.sql_builder",
        "FlextDbOracleServiceSqlBuilder",
    ),
    "base": "flext_db_oracle.services.base",
    "connection": "flext_db_oracle.services.connection",
    "plugin": "flext_db_oracle.services.plugin",
    "query": "flext_db_oracle.services.query",
    "schema": "flext_db_oracle.services.schema",
    "singer": "flext_db_oracle.services.singer",
    "sql_builder": "flext_db_oracle.services.sql_builder",
}


install_lazy_exports(__name__, globals(), _LAZY_IMPORTS, publish_all=False)
