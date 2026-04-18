# AUTO-GENERATED FILE — Regenerate with: make gen
"""Unit package."""

from __future__ import annotations

from flext_core.lazy import build_lazy_import_map, install_lazy_exports

_LAZY_IMPORTS = build_lazy_import_map(
    {
        ".conftest": ("conftest",),
        ".exceptions": (
            "FlextDbOracleTestExceptions",
            "e",
        ),
        ".test_api": (
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
        ".test_cli": (
            "TestCLIRealFunctionality",
            "TestCliServiceOperations",
            "TestFlextDbOracleCli",
            "TestFlextDbOracleClientIntegration",
            "TestFlextDbOracleClientReal",
            "TestOracleConnectionHelper",
            "TestOutputFormatter",
            "TestYamlModule",
        ),
        ".test_client": ("TestFlextDbOracleClientRealFunctionality",),
        ".test_config": ("TestFlextDbOracleSettings",),
        ".test_constants": ("Testc",),
        ".test_coverage_baseline": (
            "TestBasicModelCreation",
            "TestConstants",
            "TestExceptions",
            "TestFlextDbOracleServices",
            "TestModuleImports",
            "TestUtilities",
        ),
        ".test_dispatcher": ("TestDispatcherSurgical",),
        ".test_exceptions": ("Teste",),
        ".test_fields": ("TestFlextDbOracleFields",),
        ".test_metadata": ("TestFlextDbOracleMetadataManagerComprehensive",),
        ".test_models": (
            "TestFlextDbOracleSettingsModels",
            "Testm",
        ),
        ".test_oracle_example": (
            "TestRealOracleApi",
            "TestRealOracleConnection",
            "TestRealOracleErrorHandling",
        ),
        ".test_oracle_exceptions": (
            "TestRealOracleExceptionHierarchy",
            "TestRealOracleExceptionsAdvanced",
            "TestRealOracleExceptionsCore",
        ),
        ".test_protocols": ("TestFlextDbOracleProtocols",),
        ".test_services": (
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
        ".test_typings": ("TestFlextDbOracleTypes",),
        ".test_utilities": ("Testu",),
    },
)


install_lazy_exports(__name__, globals(), _LAZY_IMPORTS, publish_all=False)
