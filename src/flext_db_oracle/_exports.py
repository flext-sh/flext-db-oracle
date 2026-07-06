# AUTO-GENERATED FILE — Regenerate with: make gen
"""Lazy export registry."""

from __future__ import annotations

from flext_core.lazy import build_lazy_import_map, merge_lazy_imports

_LOCAL_LAZY_IMPORTS = build_lazy_import_map(
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
        "flext_core._root_typing_parts.facades": (
            "d",
            "e",
            "h",
            "r",
            "x",
        ),
    },
)

FLEXT_DB_ORACLE_LAZY_IMPORTS = merge_lazy_imports(
    (".services",),
    _LOCAL_LAZY_IMPORTS,
    exclude_names=(
        "cleanup_submodule_namespace",
        "install_lazy_exports",
        "lazy_getattr",
        "logger",
        "merge_lazy_imports",
        "output",
        "output_reporting",
        "pytest_addoption",
        "pytest_collect_file",
        "pytest_collection_modifyitems",
        "pytest_configure",
        "pytest_runtest_setup",
        "pytest_runtest_teardown",
        "pytest_sessionfinish",
        "pytest_sessionstart",
        "pytest_terminal_summary",
        "pytest_warning_recorded",
    ),
    module_name="flext_db_oracle",
)

__all__: list[str] = ["FLEXT_DB_ORACLE_LAZY_IMPORTS"]
