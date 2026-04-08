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
    "c": ("flext_core.constants", "FlextConstants"),
    "connection": "flext_db_oracle.services.connection",
    "d": ("flext_core.decorators", "FlextDecorators"),
    "e": ("flext_core.exceptions", "FlextExceptions"),
    "h": ("flext_core.handlers", "FlextHandlers"),
    "m": ("flext_core.models", "FlextModels"),
    "p": ("flext_core.protocols", "FlextProtocols"),
    "plugin": "flext_db_oracle.services.plugin",
    "query": "flext_db_oracle.services.query",
    "r": ("flext_core.result", "FlextResult"),
    "s": ("flext_db_oracle.services.base", "FlextDbOracleServiceBase"),
    "schema": "flext_db_oracle.services.schema",
    "singer": "flext_db_oracle.services.singer",
    "sql_builder": "flext_db_oracle.services.sql_builder",
    "t": ("flext_core.typings", "FlextTypes"),
    "u": ("flext_core.utilities", "FlextUtilities"),
    "x": ("flext_core.mixins", "FlextMixins"),
}


install_lazy_exports(__name__, globals(), _LAZY_IMPORTS, publish_all=False)
