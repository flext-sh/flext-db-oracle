# AUTO-GENERATED FILE — Regenerate with: make gen
"""Lazy export map part."""

from __future__ import annotations

from flext_core.lazy import build_lazy_import_map

FLEXT_DB_ORACLE_LAZY_IMPORTS_PART_01 = build_lazy_import_map(
    {
        "._models": ("_models",),
        "._utilities": ("_utilities",),
        ".api": (
            "FlextDbOracleApi",
            "db_oracle",
        ),
        ".base": (
            "FlextDbOracleServiceBase",
            "s",
        ),
        ".constants": (
            "FlextDbOracleConstants",
            "c",
        ),
        ".dispatcher": ("FlextDbOracleDispatcher",),
        ".exceptions": ("FlextDbOracleExceptions",),
        ".models": (
            "FlextDbOracleModels",
            "m",
        ),
        ".protocols": (
            "FlextDbOracleProtocols",
            "p",
        ),
        ".services": ("services",),
        ".services.api_runtime": ("FlextDbOracleApiRuntime",),
        ".services.connection": ("FlextDbOracleServiceConnection",),
        ".services.facade": ("FlextDbOracleServices",),
        ".services.plugin": ("FlextDbOracleServicePlugin",),
        ".services.query": ("FlextDbOracleServiceQuery",),
        ".services.schema": ("FlextDbOracleServiceSchema",),
        ".services.singer": ("FlextDbOracleServiceSinger",),
        ".services.sql_builder": ("FlextDbOracleServiceSqlBuilder",),
        ".settings": ("FlextDbOracleSettings",),
        ".typings": (
            "FlextDbOracleTypes",
            "t",
        ),
        ".utilities": (
            "FlextDbOracleUtilities",
            "u",
        ),
        "flext_core": (
            "d",
            "e",
            "h",
            "r",
        ),
    },
)

__all__: list[str] = ["FLEXT_DB_ORACLE_LAZY_IMPORTS_PART_01"]
