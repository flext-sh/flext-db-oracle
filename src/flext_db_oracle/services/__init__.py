# AUTO-GENERATED FILE — Regenerate with: make gen
"""Services package."""

from __future__ import annotations

from typing import TYPE_CHECKING

from flext_core.lazy import build_lazy_import_map, install_lazy_exports

if TYPE_CHECKING:
    from flext_db_oracle.services.api_runtime import FlextDbOracleApiRuntime
    from flext_db_oracle.services.connection import FlextDbOracleServiceConnection
    from flext_db_oracle.services.facade import FlextDbOracleServices
    from flext_db_oracle.services.plugin import FlextDbOracleServicePlugin
    from flext_db_oracle.services.query import FlextDbOracleServiceQuery
    from flext_db_oracle.services.schema import FlextDbOracleServiceSchema
    from flext_db_oracle.services.singer import FlextDbOracleServiceSinger
    from flext_db_oracle.services.sql_builder import FlextDbOracleServiceSqlBuilder
_LAZY_IMPORTS = build_lazy_import_map(
    {
        ".api_runtime": ("FlextDbOracleApiRuntime",),
        ".connection": ("FlextDbOracleServiceConnection",),
        ".facade": ("FlextDbOracleServices",),
        ".plugin": ("FlextDbOracleServicePlugin",),
        ".query": ("FlextDbOracleServiceQuery",),
        ".schema": ("FlextDbOracleServiceSchema",),
        ".singer": ("FlextDbOracleServiceSinger",),
        ".sql_builder": ("FlextDbOracleServiceSqlBuilder",),
    },
)


install_lazy_exports(
    __name__,
    globals(),
    _LAZY_IMPORTS,
    publish_all=False,
)
