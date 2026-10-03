# AUTO-GENERATED FILE — Regenerate with: make gen
"""Flext Db Oracle.services package.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from types import MappingProxyType
from typing import TYPE_CHECKING

from flext_core import build_lazy_import_map, install_lazy_exports

if TYPE_CHECKING:
    from flext_db_oracle.services.api_runtime import FlextDbOracleApiRuntime
    from flext_db_oracle.services.connection import FlextDbOracleServiceConnection
    from flext_db_oracle.services.facade import FlextDbOracleServices
    from flext_db_oracle.services.plugin import FlextDbOracleServicePlugin
    from flext_db_oracle.services.query import FlextDbOracleServiceQuery
    from flext_db_oracle.services.schema import FlextDbOracleServiceSchema
    from flext_db_oracle.services.singer import FlextDbOracleServiceSinger
    from flext_db_oracle.services.sql_builder import FlextDbOracleServiceSqlBuilder


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
    ),
)

install_lazy_exports(__name__, globals(), _LAZY_IMPORTS, public_exports=__all__)
