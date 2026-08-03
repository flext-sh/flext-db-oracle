# @generated AUTO-GENERATED FILE — Regenerate with: make gen
"""Flext Db Oracle.services package."""

from __future__ import annotations

from typing import TYPE_CHECKING

from flext_core.lazy import build_lazy_import_map, install_lazy_exports

if TYPE_CHECKING:
    from .api_runtime import FlextDbOracleApiRuntime as FlextDbOracleApiRuntime
    from .connection import (
        FlextDbOracleServiceConnection as FlextDbOracleServiceConnection,
    )
    from .facade import FlextDbOracleServices as FlextDbOracleServices
    from .plugin import FlextDbOracleServicePlugin as FlextDbOracleServicePlugin
    from .query import FlextDbOracleServiceQuery as FlextDbOracleServiceQuery
    from .schema import FlextDbOracleServiceSchema as FlextDbOracleServiceSchema
    from .singer import FlextDbOracleServiceSinger as FlextDbOracleServiceSinger
    from .sql_builder import (
        FlextDbOracleServiceSqlBuilder as FlextDbOracleServiceSqlBuilder,
    )

_LAZY_MODULES: dict[str, tuple[str, ...]] = {
    ".api_runtime": ("FlextDbOracleApiRuntime",),
    ".connection": ("FlextDbOracleServiceConnection",),
    ".facade": ("FlextDbOracleServices",),
    ".plugin": ("FlextDbOracleServicePlugin",),
    ".query": ("FlextDbOracleServiceQuery",),
    ".schema": ("FlextDbOracleServiceSchema",),
    ".singer": ("FlextDbOracleServiceSinger",),
    ".sql_builder": ("FlextDbOracleServiceSqlBuilder",),
}


_LAZY_ALIAS_GROUPS: dict[str, tuple[tuple[str, str], ...]] = {}


_LAZY_IMPORTS = build_lazy_import_map(
    _LAZY_MODULES, alias_groups=_LAZY_ALIAS_GROUPS, sort_keys=False
)

_PUBLIC_EXPORTS: tuple[str, ...] = (
    "FlextDbOracleApiRuntime",
    "FlextDbOracleServiceConnection",
    "FlextDbOracleServicePlugin",
    "FlextDbOracleServiceQuery",
    "FlextDbOracleServiceSchema",
    "FlextDbOracleServiceSinger",
    "FlextDbOracleServiceSqlBuilder",
    "FlextDbOracleServices",
)

__all__: tuple[str, ...] = tuple(_PUBLIC_EXPORTS)

install_lazy_exports(__name__, globals(), _LAZY_IMPORTS, public_exports=__all__)
