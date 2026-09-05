# AUTO-GENERATED FILE — Regenerate with: make gen
"""Flext Db Oracle.services package."""

from __future__ import annotations

from types import MappingProxyType
from typing import TYPE_CHECKING

from flext_core.lazy import build_lazy_import_map, install_lazy_exports

if TYPE_CHECKING:
    from .api_runtime import FlextDbOracleApiRuntime
    from .connection import FlextDbOracleServiceConnection
    from .facade import FlextDbOracleServices
    from .plugin import FlextDbOracleServicePlugin
    from .query import FlextDbOracleServiceQuery
    from .schema import FlextDbOracleServiceSchema
    from .singer import FlextDbOracleServiceSinger
    from .sql_builder import FlextDbOracleServiceSqlBuilder
__all__: tuple[str, ...] = (
    "FlextDbOracleApiRuntime",
    "FlextDbOracleServiceConnection",
    "FlextDbOracleServicePlugin",
    "FlextDbOracleServiceQuery",
    "FlextDbOracleServiceSchema",
    "FlextDbOracleServiceSinger",
    "FlextDbOracleServiceSqlBuilder",
    "FlextDbOracleServices",
)

_LAZY_IMPORTS = MappingProxyType(
    build_lazy_import_map(
        MappingProxyType({
            ".api_runtime": ("FlextDbOracleApiRuntime",),
            ".connection": ("FlextDbOracleServiceConnection",),
            ".facade": ("FlextDbOracleServices",),
            ".plugin": ("FlextDbOracleServicePlugin",),
            ".query": ("FlextDbOracleServiceQuery",),
            ".schema": ("FlextDbOracleServiceSchema",),
            ".singer": ("FlextDbOracleServiceSinger",),
            ".sql_builder": ("FlextDbOracleServiceSqlBuilder",),
        }),
        alias_groups=MappingProxyType({}),
        sort_keys=False,
    )
)

install_lazy_exports(__name__, globals(), _LAZY_IMPORTS, public_exports=__all__)
