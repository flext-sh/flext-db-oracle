# AUTO-GENERATED FILE — Regenerate with: make gen
"""Tests package."""

from __future__ import annotations

import typing as _t

from flext_core.lazy import (
    build_lazy_import_map,
    install_lazy_exports,
    merge_lazy_imports,
)

if _t.TYPE_CHECKING:
    from flext_tests import td, tf, tk, tm, tv

    from flext_db_oracle import d, e, h, r, s, x
    from tests.constants import TestsFlextDbOracleConstants, c
    from tests.e2e.test_oracle import OperationTestErrorE2E, TestsFlextDbOracleEOracle
    from tests.integration.test_oracle import TestsFlextDbOracleOracle
    from tests.models import TestsFlextDbOracleModels, m
    from tests.protocols import TestsFlextDbOracleProtocols, p
    from tests.typings import TestsFlextDbOracleTypes, t
    from tests.unit.exceptions import FlextDbOracleTestExceptions
    from tests.unit.test_api import TestsFlextDbOracleApi
    from tests.unit.test_cli import TestsFlextDbOracleCli
    from tests.unit.test_client import TestsFlextDbOracleClient
    from tests.unit.test_config import TestsFlextDbOracleConfig
    from tests.unit.test_constants import TestsFlextDbOracleConstantsUnit
    from tests.unit.test_coverage_baseline import TestsFlextDbOracleCoverageBaseline
    from tests.unit.test_dispatcher import TestsFlextDbOracleDispatcher
    from tests.unit.test_exceptions import TestsFlextDbOracleExceptions
    from tests.unit.test_fields import TestsFlextDbOracleFields
    from tests.unit.test_metadata import TestsFlextDbOracleMetadata
    from tests.unit.test_models import TestsFlextDbOracleModelsUnit
    from tests.unit.test_oracle_example import TestsFlextDbOracleOracleExample
    from tests.unit.test_oracle_exceptions import TestsFlextDbOracleOracleExceptions
    from tests.unit.test_protocols import TestsFlextDbOracleProtocolsUnit
    from tests.unit.test_services import TestsFlextDbOracleServices
    from tests.unit.test_typings import TestsFlextDbOracleTypingsUnit
    from tests.unit.test_utilities import TestsFlextDbOracleUtilitiesUnit
    from tests.utilities import TestsFlextDbOracleUtilities, u
_LAZY_IMPORTS = merge_lazy_imports(
    (
        ".e2e",
        ".integration",
        ".unit",
    ),
    build_lazy_import_map(
        {
            ".constants": (
                "TestsFlextDbOracleConstants",
                "c",
            ),
            ".e2e.test_oracle": (
                "OperationTestErrorE2E",
                "TestsFlextDbOracleEOracle",
            ),
            ".integration.test_oracle": ("TestsFlextDbOracleOracle",),
            ".models": (
                "TestsFlextDbOracleModels",
                "m",
            ),
            ".protocols": (
                "TestsFlextDbOracleProtocols",
                "p",
            ),
            ".typings": (
                "TestsFlextDbOracleTypes",
                "t",
            ),
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
            "flext_db_oracle": (
                "d",
                "e",
                "h",
                "r",
                "s",
                "x",
            ),
            "flext_tests": (
                "td",
                "tf",
                "tk",
                "tm",
                "tv",
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


install_lazy_exports(__name__, globals(), _LAZY_IMPORTS)

__all__: list[str] = [
    "FlextDbOracleTestExceptions",
    "OperationTestErrorE2E",
    "TestsFlextDbOracleApi",
    "TestsFlextDbOracleCli",
    "TestsFlextDbOracleClient",
    "TestsFlextDbOracleConfig",
    "TestsFlextDbOracleConstants",
    "TestsFlextDbOracleConstantsUnit",
    "TestsFlextDbOracleCoverageBaseline",
    "TestsFlextDbOracleDispatcher",
    "TestsFlextDbOracleEOracle",
    "TestsFlextDbOracleExceptions",
    "TestsFlextDbOracleFields",
    "TestsFlextDbOracleMetadata",
    "TestsFlextDbOracleModels",
    "TestsFlextDbOracleModelsUnit",
    "TestsFlextDbOracleOracle",
    "TestsFlextDbOracleOracleExample",
    "TestsFlextDbOracleOracleExceptions",
    "TestsFlextDbOracleProtocols",
    "TestsFlextDbOracleProtocolsUnit",
    "TestsFlextDbOracleServices",
    "TestsFlextDbOracleTypes",
    "TestsFlextDbOracleTypingsUnit",
    "TestsFlextDbOracleUtilities",
    "TestsFlextDbOracleUtilitiesUnit",
    "c",
    "d",
    "e",
    "h",
    "m",
    "p",
    "r",
    "s",
    "t",
    "td",
    "tf",
    "tk",
    "tm",
    "tv",
    "u",
    "x",
]
