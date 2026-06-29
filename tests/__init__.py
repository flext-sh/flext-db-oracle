# AUTO-GENERATED FILE — Regenerate with: make gen
"""Tests package."""

from __future__ import annotations

from flext_core.lazy import (
    build_lazy_import_map,
    install_lazy_exports,
    merge_lazy_imports,
)

_LAZY_IMPORTS = merge_lazy_imports(
    (
        ".e2e",
        ".integration",
        ".unit",
    ),
    build_lazy_import_map(
        {
            ".base": (
                "TestsFlextDbOracleServiceBase",
                "s",
            ),
            ".conftest": ("conftest",),
            ".constants": (
                "TestsFlextDbOracleConstants",
                "c",
            ),
            ".e2e": ("e2e",),
            ".e2e.test_oracle": (
                "OperationTestErrorE2E",
                "TestsFlextDbOracleEOracle",
            ),
            ".integration": ("integration",),
            ".integration.test_oracle": ("TestsFlextDbOracleOracle",),
            ".models": (
                "TestsFlextDbOracleModels",
                "m",
            ),
            ".protocols": (
                "TestsFlextDbOracleProtocols",
                "p",
            ),
            ".settings": ("TestsFlextDbOracleSettings",),
            ".typings": (
                "TestsFlextDbOracleTypes",
                "t",
            ),
            ".unit": ("unit",),
            ".unit.exceptions": ("FlextDbOracleTestExceptions",),
            ".unit.test_api": ("TestsFlextDbOracleApi",),
            ".unit.test_cli": ("TestsFlextDbOracleCli",),
            ".unit.test_client": ("TestsFlextDbOracleClient",),
            ".unit.test_config": ("TestsFlextDbOracleConfig",),
            ".unit.test_constants": ("TestsFlextDbOracleConstantsUnit",),
            ".unit.test_coverage_baseline": ("TestsFlextDbOracleCoverageBaseline",),
            ".unit.test_dispatcher": ("TestsFlextDbOracleDispatcher",),
            ".unit.test_exceptions": ("TestsFlextDbOracleExceptions",),
            ".unit.test_fields": ("TestsFlextDbOracleFields",),
            ".unit.test_metadata": ("TestsFlextDbOracleMetadata",),
            ".unit.test_models": ("TestsFlextDbOracleModelsUnit",),
            ".unit.test_oracle_example": ("TestsFlextDbOracleOracleExample",),
            ".unit.test_oracle_exceptions": ("TestsFlextDbOracleOracleExceptions",),
            ".unit.test_protocols": ("TestsFlextDbOracleProtocolsUnit",),
            ".unit.test_services": ("TestsFlextDbOracleServices",),
            ".unit.test_typings": ("TestsFlextDbOracleTypingsUnit",),
            ".unit.test_utilities": ("TestsFlextDbOracleUtilitiesUnit",),
            ".utilities": (
                "TestsFlextDbOracleUtilities",
                "u",
            ),
            "flext_tests": (
                "d",
                "e",
                "h",
                "r",
                "td",
                "tf",
                "tk",
                "tm",
                "tv",
                "x",
            ),
        },
    ),
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
    module_name=__name__,
)


install_lazy_exports(
    __name__,
    globals(),
    _LAZY_IMPORTS,
    publish_all=False,
)
