# AUTO-GENERATED FILE — DO NOT EDIT MANUALLY.
# Regenerate with: make gen
#
"""Services package."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import TYPE_CHECKING as _TYPE_CHECKING

from flext_core.lazy import install_lazy_exports

if _TYPE_CHECKING:
    from flext_core import FlextTypes
    from flext_core.constants import FlextConstants as c
    from flext_core.decorators import FlextDecorators as d
    from flext_core.exceptions import FlextExceptions as e
    from flext_core.handlers import FlextHandlers as h
    from flext_core.mixins import FlextMixins as x
    from flext_core.models import FlextModels as m
    from flext_core.protocols import FlextProtocols as p
    from flext_core.result import FlextResult as r
    from flext_core.service import FlextService as s
    from flext_core.typings import FlextTypes as t
    from flext_core.utilities import FlextUtilities as u
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
    "s": ("flext_core.service", "FlextService"),
    "schema": "flext_db_oracle.services.schema",
    "singer": "flext_db_oracle.services.singer",
    "sql_builder": "flext_db_oracle.services.sql_builder",
    "t": ("flext_core.typings", "FlextTypes"),
    "u": ("flext_core.utilities", "FlextUtilities"),
    "x": ("flext_core.mixins", "FlextMixins"),
}


install_lazy_exports(__name__, globals(), _LAZY_IMPORTS)
