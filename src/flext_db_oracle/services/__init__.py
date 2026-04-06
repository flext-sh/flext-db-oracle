# AUTO-GENERATED FILE — DO NOT EDIT MANUALLY.
# Regenerate with: make gen
#
"""Services package."""

from __future__ import annotations

import typing as _t

from flext_core.lazy import install_lazy_exports

if _t.TYPE_CHECKING:
    import flext_db_oracle.services.base as _flext_db_oracle_services_base

    base = _flext_db_oracle_services_base
    import flext_db_oracle.services.connection as _flext_db_oracle_services_connection
    from flext_db_oracle.services.base import (
        FlextDbOracleServiceBase,
        FlextDbOracleServiceBase as s,
    )

    connection = _flext_db_oracle_services_connection
    import flext_db_oracle.services.plugin as _flext_db_oracle_services_plugin
    from flext_db_oracle.services.connection import FlextDbOracleServiceConnection

    plugin = _flext_db_oracle_services_plugin
    import flext_db_oracle.services.query as _flext_db_oracle_services_query
    from flext_db_oracle.services.plugin import FlextDbOracleServicePlugin

    query = _flext_db_oracle_services_query
    import flext_db_oracle.services.schema as _flext_db_oracle_services_schema
    from flext_db_oracle.services.query import FlextDbOracleServiceQuery

    schema = _flext_db_oracle_services_schema
    import flext_db_oracle.services.singer as _flext_db_oracle_services_singer
    from flext_db_oracle.services.schema import FlextDbOracleServiceSchema

    singer = _flext_db_oracle_services_singer
    import flext_db_oracle.services.sql_builder as _flext_db_oracle_services_sql_builder
    from flext_db_oracle.services.singer import FlextDbOracleServiceSinger

    sql_builder = _flext_db_oracle_services_sql_builder
    from flext_core.constants import FlextConstants as c
    from flext_core.decorators import FlextDecorators as d
    from flext_core.exceptions import FlextExceptions as e
    from flext_core.handlers import FlextHandlers as h
    from flext_core.mixins import FlextMixins as x
    from flext_core.models import FlextModels as m
    from flext_core.protocols import FlextProtocols as p
    from flext_core.result import FlextResult as r
    from flext_core.typings import FlextTypes as t
    from flext_core.utilities import FlextUtilities as u
    from flext_db_oracle.services.sql_builder import FlextDbOracleServiceSqlBuilder
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

__all__ = [
    "FlextDbOracleServiceBase",
    "FlextDbOracleServiceConnection",
    "FlextDbOracleServicePlugin",
    "FlextDbOracleServiceQuery",
    "FlextDbOracleServiceSchema",
    "FlextDbOracleServiceSinger",
    "FlextDbOracleServiceSqlBuilder",
    "base",
    "c",
    "connection",
    "d",
    "e",
    "h",
    "m",
    "p",
    "plugin",
    "query",
    "r",
    "s",
    "schema",
    "singer",
    "sql_builder",
    "t",
    "u",
    "x",
]


install_lazy_exports(__name__, globals(), _LAZY_IMPORTS)
