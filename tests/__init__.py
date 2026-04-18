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
    from tests.conftest import OperationTestError
    from tests.constants import TestsFlextDbOracleConstants, c
    from tests.e2e.test_oracle import OperationTestErrorE2E, TestOracleE2E
    from tests.integration.test_oracle import TestOracleIntegration
    from tests.models import TestsFlextDbOracleModels, m
    from tests.protocols import TestsFlextDbOracleProtocols, p
    from tests.typings import TestsFlextDbOracleTypes, t
    from tests.unit.exceptions import FlextDbOracleTestExceptions
    from tests.unit.test_api import (
        TestApiModule,
        TestApiSurgicalSimple,
        TestDirectCoverageBoostAPI,
        TestDirectCoverageBoostConfig,
        TestDirectCoverageBoostConnection,
        TestDirectCoverageBoostObservability,
        TestDirectCoverageBoostServices,
        TestDirectCoverageBoostTypes,
        TestFlextDbOracleApiRealFunctionality,
        TestFlextDbOracleApiSafeMethods,
        TestFlextDbOracleApiWorking,
    )
    from tests.unit.test_cli import (
        TestCLIRealFunctionality,
        TestCliServiceOperations,
        TestFlextDbOracleCli,
        TestFlextDbOracleClientIntegration,
        TestFlextDbOracleClientReal,
        TestOracleConnectionHelper,
        TestOutputFormatter,
        TestYamlModule,
    )
    from tests.unit.test_client import TestFlextDbOracleClientRealFunctionality
    from tests.unit.test_config import TestFlextDbOracleSettings
    from tests.unit.test_constants import Testc
    from tests.unit.test_coverage_baseline import (
        TestBasicModelCreation,
        TestConstants,
        TestExceptions,
        TestFlextDbOracleServices,
        TestModuleImports,
        TestUtilities,
    )
    from tests.unit.test_dispatcher import TestDispatcherSurgical
    from tests.unit.test_exceptions import Teste
    from tests.unit.test_fields import TestFlextDbOracleFields
    from tests.unit.test_metadata import TestFlextDbOracleMetadataManagerComprehensive
    from tests.unit.test_models import TestFlextDbOracleSettingsModels, Testm
    from tests.unit.test_oracle_example import (
        TestRealOracleApi,
        TestRealOracleConnection,
        TestRealOracleErrorHandling,
    )
    from tests.unit.test_oracle_exceptions import (
        TestRealOracleExceptionHierarchy,
        TestRealOracleExceptionsAdvanced,
        TestRealOracleExceptionsCore,
    )
    from tests.unit.test_protocols import TestFlextDbOracleProtocols
    from tests.unit.test_services import (
        TestDirectCoverageBoostAPIServices,
        TestDirectCoverageBoostConfigServices,
        TestDirectCoverageBoostConnectionServices,
        TestDirectCoverageBoostObservabilityServices,
        TestDirectCoverageBoostServicesServices,
        TestDirectCoverageBoostTypesServices,
        TestFlextDbOracleConnectionSimple,
        TestFlextDbOracleMetadataManagerComprehensiveServices,
        TestFlextDbOracleServicesBasic,
        TestFlextDbOracleServicesPlaceholderRemovals,
        TestServiceErrorHandling,
    )
    from tests.unit.test_typings import TestFlextDbOracleTypes
    from tests.unit.test_utilities import Testu
    from tests.utilities import TestsFlextDbOracleUtilities, u
_LAZY_IMPORTS = merge_lazy_imports(
    (
        ".e2e",
        ".integration",
        ".unit",
    ),
    build_lazy_import_map(
        {
            ".conftest": ("OperationTestError",),
            ".constants": (
                "TestsFlextDbOracleConstants",
                "c",
            ),
            ".e2e.test_oracle": (
                "OperationTestErrorE2E",
                "TestOracleE2E",
            ),
            ".integration.test_oracle": ("TestOracleIntegration",),
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
            ".unit.test_api": (
                "TestApiModule",
                "TestApiSurgicalSimple",
                "TestDirectCoverageBoostAPI",
                "TestDirectCoverageBoostConfig",
                "TestDirectCoverageBoostConnection",
                "TestDirectCoverageBoostObservability",
                "TestDirectCoverageBoostServices",
                "TestDirectCoverageBoostTypes",
                "TestFlextDbOracleApiRealFunctionality",
                "TestFlextDbOracleApiSafeMethods",
                "TestFlextDbOracleApiWorking",
            ),
            ".unit.test_cli": (
                "TestCLIRealFunctionality",
                "TestCliServiceOperations",
                "TestFlextDbOracleCli",
                "TestFlextDbOracleClientIntegration",
                "TestFlextDbOracleClientReal",
                "TestOracleConnectionHelper",
                "TestOutputFormatter",
                "TestYamlModule",
            ),
            ".unit.test_client": ("TestFlextDbOracleClientRealFunctionality",),
            ".unit.test_config": ("TestFlextDbOracleSettings",),
            ".unit.test_constants": ("Testc",),
            ".unit.test_coverage_baseline": (
                "TestBasicModelCreation",
                "TestConstants",
                "TestExceptions",
                "TestFlextDbOracleServices",
                "TestModuleImports",
                "TestUtilities",
            ),
            ".unit.test_dispatcher": ("TestDispatcherSurgical",),
            ".unit.test_exceptions": ("Teste",),
            ".unit.test_fields": ("TestFlextDbOracleFields",),
            ".unit.test_metadata": ("TestFlextDbOracleMetadataManagerComprehensive",),
            ".unit.test_models": (
                "TestFlextDbOracleSettingsModels",
                "Testm",
            ),
            ".unit.test_oracle_example": (
                "TestRealOracleApi",
                "TestRealOracleConnection",
                "TestRealOracleErrorHandling",
            ),
            ".unit.test_oracle_exceptions": (
                "TestRealOracleExceptionHierarchy",
                "TestRealOracleExceptionsAdvanced",
                "TestRealOracleExceptionsCore",
            ),
            ".unit.test_protocols": ("TestFlextDbOracleProtocols",),
            ".unit.test_services": (
                "TestDirectCoverageBoostAPIServices",
                "TestDirectCoverageBoostConfigServices",
                "TestDirectCoverageBoostConnectionServices",
                "TestDirectCoverageBoostObservabilityServices",
                "TestDirectCoverageBoostServicesServices",
                "TestDirectCoverageBoostTypesServices",
                "TestFlextDbOracleConnectionSimple",
                "TestFlextDbOracleMetadataManagerComprehensiveServices",
                "TestFlextDbOracleServicesBasic",
                "TestFlextDbOracleServicesPlaceholderRemovals",
                "TestServiceErrorHandling",
            ),
            ".unit.test_typings": ("TestFlextDbOracleTypes",),
            ".unit.test_utilities": ("Testu",),
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
    ),
    module_name=__name__,
)


install_lazy_exports(__name__, globals(), _LAZY_IMPORTS)

__all__: list[str] = [
    "FlextDbOracleTestExceptions",
    "OperationTestError",
    "OperationTestErrorE2E",
    "TestApiModule",
    "TestApiSurgicalSimple",
    "TestBasicModelCreation",
    "TestCLIRealFunctionality",
    "TestCliServiceOperations",
    "TestConstants",
    "TestDirectCoverageBoostAPI",
    "TestDirectCoverageBoostAPIServices",
    "TestDirectCoverageBoostConfig",
    "TestDirectCoverageBoostConfigServices",
    "TestDirectCoverageBoostConnection",
    "TestDirectCoverageBoostConnectionServices",
    "TestDirectCoverageBoostObservability",
    "TestDirectCoverageBoostObservabilityServices",
    "TestDirectCoverageBoostServices",
    "TestDirectCoverageBoostServicesServices",
    "TestDirectCoverageBoostTypes",
    "TestDirectCoverageBoostTypesServices",
    "TestDispatcherSurgical",
    "TestExceptions",
    "TestFlextDbOracleApiRealFunctionality",
    "TestFlextDbOracleApiSafeMethods",
    "TestFlextDbOracleApiWorking",
    "TestFlextDbOracleCli",
    "TestFlextDbOracleClientIntegration",
    "TestFlextDbOracleClientReal",
    "TestFlextDbOracleClientRealFunctionality",
    "TestFlextDbOracleConnectionSimple",
    "TestFlextDbOracleFields",
    "TestFlextDbOracleMetadataManagerComprehensive",
    "TestFlextDbOracleMetadataManagerComprehensiveServices",
    "TestFlextDbOracleProtocols",
    "TestFlextDbOracleServices",
    "TestFlextDbOracleServicesBasic",
    "TestFlextDbOracleServicesPlaceholderRemovals",
    "TestFlextDbOracleSettings",
    "TestFlextDbOracleSettingsModels",
    "TestFlextDbOracleTypes",
    "TestModuleImports",
    "TestOracleConnectionHelper",
    "TestOracleE2E",
    "TestOracleIntegration",
    "TestOutputFormatter",
    "TestRealOracleApi",
    "TestRealOracleConnection",
    "TestRealOracleErrorHandling",
    "TestRealOracleExceptionHierarchy",
    "TestRealOracleExceptionsAdvanced",
    "TestRealOracleExceptionsCore",
    "TestServiceErrorHandling",
    "TestUtilities",
    "TestYamlModule",
    "Testc",
    "Teste",
    "Testm",
    "TestsFlextDbOracleConstants",
    "TestsFlextDbOracleModels",
    "TestsFlextDbOracleProtocols",
    "TestsFlextDbOracleTypes",
    "TestsFlextDbOracleUtilities",
    "Testu",
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
