# AUTO-GENERATED FILE — DO NOT EDIT MANUALLY.
# Regenerate with: make gen
#
"""Service facade for flext-db-oracle.

MRO composition of all service mixins into a single
FlextDbOracleServices class following AGENTS.md Service Facade Pattern.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import TYPE_CHECKING as _TYPE_CHECKING

from flext_core.lazy import install_lazy_exports

if _TYPE_CHECKING:
    from flext_core import FlextTypes
    from flext_db_oracle.services import (
        base,
        connection,
        plugin,
        query,
        schema,
        singer,
        sql_builder,
    )
    from flext_db_oracle.services.base import FlextDbOracleServiceBase
    from flext_db_oracle.services.connection import FlextDbOracleServiceConnection
    from flext_db_oracle.services.plugin import FlextDbOracleServicePlugin
    from flext_db_oracle.services.query import FlextDbOracleServiceQuery
    from flext_db_oracle.services.schema import FlextDbOracleServiceSchema
    from flext_db_oracle.services.singer import FlextDbOracleServiceSinger
    from flext_db_oracle.services.sql_builder import FlextDbOracleServiceSqlBuilder

_LAZY_IMPORTS: FlextTypes.LazyImportIndex = {
    "FlextDbOracleServiceBase": "flext_db_oracle.services.base",
    "FlextDbOracleServiceConnection": "flext_db_oracle.services.connection",
    "FlextDbOracleServicePlugin": "flext_db_oracle.services.plugin",
    "FlextDbOracleServiceQuery": "flext_db_oracle.services.query",
    "FlextDbOracleServiceSchema": "flext_db_oracle.services.schema",
    "FlextDbOracleServiceSinger": "flext_db_oracle.services.singer",
    "FlextDbOracleServiceSqlBuilder": "flext_db_oracle.services.sql_builder",
    "base": "flext_db_oracle.services.base",
    "connection": "flext_db_oracle.services.connection",
    "plugin": "flext_db_oracle.services.plugin",
    "query": "flext_db_oracle.services.query",
    "schema": "flext_db_oracle.services.schema",
    "singer": "flext_db_oracle.services.singer",
    "sql_builder": "flext_db_oracle.services.sql_builder",
}


install_lazy_exports(__name__, globals(), _LAZY_IMPORTS)
