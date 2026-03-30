# AUTO-GENERATED FILE — DO NOT EDIT MANUALLY.
# Regenerate with: make gen
#
"""Tests package."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import TYPE_CHECKING

from flext_core.lazy import install_lazy_exports

if TYPE_CHECKING:
    from tests import (
        conftest as conftest,
        constants as constants,
        e2e as e2e,
        integration as integration,
        models as models,
        protocols as protocols,
        typings as typings,
        unit as unit,
        utilities as utilities,
    )
    from tests.conftest import (
        flext_domains as flext_domains,
        pytest_configure as pytest_configure,
        pytest_runtest_makereport as pytest_runtest_makereport,
        pytest_sessionstart as pytest_sessionstart,
        test_database_setup as test_database_setup,
    )
    from tests.constants import (
        FlextDbOracleTestConstants as FlextDbOracleTestConstants,
        FlextDbOracleTestConstants as c,
    )
    from tests.e2e import test_oracle as test_oracle
    from tests.e2e.test_oracle import (
        OperationTestError as OperationTestError,
        TestOracleE2E as TestOracleE2E,
    )
    from tests.integration.test_oracle import (
        TestOracleIntegration as TestOracleIntegration,
    )
    from tests.models import (
        FlextDbOracleTestModels as FlextDbOracleTestModels,
        FlextDbOracleTestModels as m,
    )
    from tests.protocols import (
        FlextDbOracleTestProtocols as FlextDbOracleTestProtocols,
        FlextDbOracleTestProtocols as p,
    )
    from tests.typings import (
        FlextDbOracleTestTypes as FlextDbOracleTestTypes,
        FlextDbOracleTestTypes as t,
    )
    from tests.unit import (
        test_api as test_api,
        test_cli as test_cli,
        test_client as test_client,
        test_config as test_config,
        test_constants as test_constants,
        test_coverage_baseline as test_coverage_baseline,
        test_dispatcher as test_dispatcher,
        test_exceptions as test_exceptions,
        test_fields as test_fields,
        test_metadata as test_metadata,
        test_models as test_models,
        test_oracle_example as test_oracle_example,
        test_oracle_exceptions as test_oracle_exceptions,
        test_protocols as test_protocols,
        test_services as test_services,
        test_typings as test_typings,
        test_utilities as test_utilities,
    )
    from tests.unit.conftest import (
        connected_oracle_api as connected_oracle_api,
        docker_control as docker_control,
        ensure_shared_docker_container as ensure_shared_docker_container,
        logger as logger,
        mock_oracle_config as mock_oracle_config,
        oracle_api as oracle_api,
        oracle_available as oracle_available,
        oracle_config as oracle_config,
        oracle_container as oracle_container,
        real_oracle_config as real_oracle_config,
        shared_oracle_container as shared_oracle_container,
        test_cleanup as test_cleanup,
    )
    from tests.unit.test_api import (
        TestApiModule as TestApiModule,
        TestApiSurgicalSimple as TestApiSurgicalSimple,
        TestFlextDbOracleApiRealFunctionality as TestFlextDbOracleApiRealFunctionality,
        TestFlextDbOracleApiSafeMethods as TestFlextDbOracleApiSafeMethods,
        TestFlextDbOracleApiWorking as TestFlextDbOracleApiWorking,
    )
    from tests.unit.test_cli import (
        HealthCheckReport as HealthCheckReport,
        NamedItem as NamedItem,
        TestCLIRealFunctionality as TestCLIRealFunctionality,
        TestCliServiceOperations as TestCliServiceOperations,
        TestFlextDbOracleCli as TestFlextDbOracleCli,
        TestFlextDbOracleClientIntegration as TestFlextDbOracleClientIntegration,
        TestFlextDbOracleClientReal as TestFlextDbOracleClientReal,
        TestOracleConnectionHelper as TestOracleConnectionHelper,
        TestOutputFormatter as TestOutputFormatter,
        TestYamlModule as TestYamlModule,
    )
    from tests.unit.test_client import (
        TestFlextDbOracleClientRealFunctionality as TestFlextDbOracleClientRealFunctionality,
    )
    from tests.unit.test_constants import (
        TestFlextDbOracleConstants as TestFlextDbOracleConstants,
    )
    from tests.unit.test_coverage_baseline import (
        TestBasicModelCreation as TestBasicModelCreation,
        TestConstants as TestConstants,
        TestExceptions as TestExceptions,
        TestFlextDbOracleServices as TestFlextDbOracleServices,
        TestModuleImports as TestModuleImports,
        TestUtilities as TestUtilities,
    )
    from tests.unit.test_dispatcher import (
        TestDispatcherSurgical as TestDispatcherSurgical,
    )
    from tests.unit.test_exceptions import (
        TestFlextDbOracleExceptions as TestFlextDbOracleExceptions,
    )
    from tests.unit.test_fields import (
        TestFlextDbOracleFields as TestFlextDbOracleFields,
    )
    from tests.unit.test_models import (
        TestFlextDbOracleModels as TestFlextDbOracleModels,
        TestFlextDbOracleSettings as TestFlextDbOracleSettings,
    )
    from tests.unit.test_oracle_example import (
        TestRealOracleApi as TestRealOracleApi,
        TestRealOracleConnection as TestRealOracleConnection,
        TestRealOracleErrorHandling as TestRealOracleErrorHandling,
        safe_get_first_value as safe_get_first_value,
    )
    from tests.unit.test_oracle_exceptions import (
        TestRealOracleExceptionHierarchy as TestRealOracleExceptionHierarchy,
        TestRealOracleExceptionsAdvanced as TestRealOracleExceptionsAdvanced,
        TestRealOracleExceptionsCore as TestRealOracleExceptionsCore,
    )
    from tests.unit.test_protocols import (
        TestFlextDbOracleProtocols as TestFlextDbOracleProtocols,
    )
    from tests.unit.test_services import (
        TestDirectCoverageBoostAPI as TestDirectCoverageBoostAPI,
        TestDirectCoverageBoostConfig as TestDirectCoverageBoostConfig,
        TestDirectCoverageBoostConnection as TestDirectCoverageBoostConnection,
        TestDirectCoverageBoostObservability as TestDirectCoverageBoostObservability,
        TestDirectCoverageBoostServices as TestDirectCoverageBoostServices,
        TestDirectCoverageBoostTypes as TestDirectCoverageBoostTypes,
        TestFlextDbOracleConnectionSimple as TestFlextDbOracleConnectionSimple,
        TestFlextDbOracleMetadataManagerComprehensive as TestFlextDbOracleMetadataManagerComprehensive,
        TestFlextDbOracleServicesBasic as TestFlextDbOracleServicesBasic,
        TestFlextDbOracleServicesPlaceholderRemovals as TestFlextDbOracleServicesPlaceholderRemovals,
        TestServiceErrorHandling as TestServiceErrorHandling,
    )
    from tests.unit.test_typings import TestFlextDbOracleTypes as TestFlextDbOracleTypes
    from tests.unit.test_utilities import (
        TestFlextDbOracleUtilities as TestFlextDbOracleUtilities,
    )
    from tests.utilities import (
        FlextDbOracleTestUtilities as FlextDbOracleTestUtilities,
        FlextDbOracleTestUtilities as u,
    )

_LAZY_IMPORTS: Mapping[str, Sequence[str]] = {
    "FlextDbOracleTestConstants": ["tests.constants", "FlextDbOracleTestConstants"],
    "FlextDbOracleTestModels": ["tests.models", "FlextDbOracleTestModels"],
    "FlextDbOracleTestProtocols": ["tests.protocols", "FlextDbOracleTestProtocols"],
    "FlextDbOracleTestTypes": ["tests.typings", "FlextDbOracleTestTypes"],
    "FlextDbOracleTestUtilities": ["tests.utilities", "FlextDbOracleTestUtilities"],
    "HealthCheckReport": ["tests.unit.test_cli", "HealthCheckReport"],
    "NamedItem": ["tests.unit.test_cli", "NamedItem"],
    "OperationTestError": ["tests.e2e.test_oracle", "OperationTestError"],
    "TestApiModule": ["tests.unit.test_api", "TestApiModule"],
    "TestApiSurgicalSimple": ["tests.unit.test_api", "TestApiSurgicalSimple"],
    "TestBasicModelCreation": [
        "tests.unit.test_coverage_baseline",
        "TestBasicModelCreation",
    ],
    "TestCLIRealFunctionality": ["tests.unit.test_cli", "TestCLIRealFunctionality"],
    "TestCliServiceOperations": ["tests.unit.test_cli", "TestCliServiceOperations"],
    "TestConstants": ["tests.unit.test_coverage_baseline", "TestConstants"],
    "TestDirectCoverageBoostAPI": [
        "tests.unit.test_services",
        "TestDirectCoverageBoostAPI",
    ],
    "TestDirectCoverageBoostConfig": [
        "tests.unit.test_services",
        "TestDirectCoverageBoostConfig",
    ],
    "TestDirectCoverageBoostConnection": [
        "tests.unit.test_services",
        "TestDirectCoverageBoostConnection",
    ],
    "TestDirectCoverageBoostObservability": [
        "tests.unit.test_services",
        "TestDirectCoverageBoostObservability",
    ],
    "TestDirectCoverageBoostServices": [
        "tests.unit.test_services",
        "TestDirectCoverageBoostServices",
    ],
    "TestDirectCoverageBoostTypes": [
        "tests.unit.test_services",
        "TestDirectCoverageBoostTypes",
    ],
    "TestDispatcherSurgical": ["tests.unit.test_dispatcher", "TestDispatcherSurgical"],
    "TestExceptions": ["tests.unit.test_coverage_baseline", "TestExceptions"],
    "TestFlextDbOracleApiRealFunctionality": [
        "tests.unit.test_api",
        "TestFlextDbOracleApiRealFunctionality",
    ],
    "TestFlextDbOracleApiSafeMethods": [
        "tests.unit.test_api",
        "TestFlextDbOracleApiSafeMethods",
    ],
    "TestFlextDbOracleApiWorking": [
        "tests.unit.test_api",
        "TestFlextDbOracleApiWorking",
    ],
    "TestFlextDbOracleCli": ["tests.unit.test_cli", "TestFlextDbOracleCli"],
    "TestFlextDbOracleClientIntegration": [
        "tests.unit.test_cli",
        "TestFlextDbOracleClientIntegration",
    ],
    "TestFlextDbOracleClientReal": [
        "tests.unit.test_cli",
        "TestFlextDbOracleClientReal",
    ],
    "TestFlextDbOracleClientRealFunctionality": [
        "tests.unit.test_client",
        "TestFlextDbOracleClientRealFunctionality",
    ],
    "TestFlextDbOracleConnectionSimple": [
        "tests.unit.test_services",
        "TestFlextDbOracleConnectionSimple",
    ],
    "TestFlextDbOracleConstants": [
        "tests.unit.test_constants",
        "TestFlextDbOracleConstants",
    ],
    "TestFlextDbOracleExceptions": [
        "tests.unit.test_exceptions",
        "TestFlextDbOracleExceptions",
    ],
    "TestFlextDbOracleFields": ["tests.unit.test_fields", "TestFlextDbOracleFields"],
    "TestFlextDbOracleMetadataManagerComprehensive": [
        "tests.unit.test_services",
        "TestFlextDbOracleMetadataManagerComprehensive",
    ],
    "TestFlextDbOracleModels": ["tests.unit.test_models", "TestFlextDbOracleModels"],
    "TestFlextDbOracleProtocols": [
        "tests.unit.test_protocols",
        "TestFlextDbOracleProtocols",
    ],
    "TestFlextDbOracleServices": [
        "tests.unit.test_coverage_baseline",
        "TestFlextDbOracleServices",
    ],
    "TestFlextDbOracleServicesBasic": [
        "tests.unit.test_services",
        "TestFlextDbOracleServicesBasic",
    ],
    "TestFlextDbOracleServicesPlaceholderRemovals": [
        "tests.unit.test_services",
        "TestFlextDbOracleServicesPlaceholderRemovals",
    ],
    "TestFlextDbOracleSettings": [
        "tests.unit.test_models",
        "TestFlextDbOracleSettings",
    ],
    "TestFlextDbOracleTypes": ["tests.unit.test_typings", "TestFlextDbOracleTypes"],
    "TestFlextDbOracleUtilities": [
        "tests.unit.test_utilities",
        "TestFlextDbOracleUtilities",
    ],
    "TestModuleImports": ["tests.unit.test_coverage_baseline", "TestModuleImports"],
    "TestOracleConnectionHelper": ["tests.unit.test_cli", "TestOracleConnectionHelper"],
    "TestOracleE2E": ["tests.e2e.test_oracle", "TestOracleE2E"],
    "TestOracleIntegration": ["tests.integration.test_oracle", "TestOracleIntegration"],
    "TestOutputFormatter": ["tests.unit.test_cli", "TestOutputFormatter"],
    "TestRealOracleApi": ["tests.unit.test_oracle_example", "TestRealOracleApi"],
    "TestRealOracleConnection": [
        "tests.unit.test_oracle_example",
        "TestRealOracleConnection",
    ],
    "TestRealOracleErrorHandling": [
        "tests.unit.test_oracle_example",
        "TestRealOracleErrorHandling",
    ],
    "TestRealOracleExceptionHierarchy": [
        "tests.unit.test_oracle_exceptions",
        "TestRealOracleExceptionHierarchy",
    ],
    "TestRealOracleExceptionsAdvanced": [
        "tests.unit.test_oracle_exceptions",
        "TestRealOracleExceptionsAdvanced",
    ],
    "TestRealOracleExceptionsCore": [
        "tests.unit.test_oracle_exceptions",
        "TestRealOracleExceptionsCore",
    ],
    "TestServiceErrorHandling": [
        "tests.unit.test_services",
        "TestServiceErrorHandling",
    ],
    "TestUtilities": ["tests.unit.test_coverage_baseline", "TestUtilities"],
    "TestYamlModule": ["tests.unit.test_cli", "TestYamlModule"],
    "c": ["tests.constants", "FlextDbOracleTestConstants"],
    "conftest": ["tests.conftest", ""],
    "connected_oracle_api": ["tests.unit.conftest", "connected_oracle_api"],
    "constants": ["tests.constants", ""],
    "d": ["flext_tests", "d"],
    "docker_control": ["tests.unit.conftest", "docker_control"],
    "e": ["flext_tests", "e"],
    "e2e": ["tests.e2e", ""],
    "ensure_shared_docker_container": [
        "tests.unit.conftest",
        "ensure_shared_docker_container",
    ],
    "flext_domains": ["tests.conftest", "flext_domains"],
    "h": ["flext_tests", "h"],
    "integration": ["tests.integration", ""],
    "logger": ["tests.unit.conftest", "logger"],
    "m": ["tests.models", "FlextDbOracleTestModels"],
    "mock_oracle_config": ["tests.unit.conftest", "mock_oracle_config"],
    "models": ["tests.models", ""],
    "oracle_api": ["tests.unit.conftest", "oracle_api"],
    "oracle_available": ["tests.unit.conftest", "oracle_available"],
    "oracle_config": ["tests.unit.conftest", "oracle_config"],
    "oracle_container": ["tests.unit.conftest", "oracle_container"],
    "p": ["tests.protocols", "FlextDbOracleTestProtocols"],
    "protocols": ["tests.protocols", ""],
    "pytest_configure": ["tests.conftest", "pytest_configure"],
    "pytest_runtest_makereport": ["tests.conftest", "pytest_runtest_makereport"],
    "pytest_sessionstart": ["tests.conftest", "pytest_sessionstart"],
    "r": ["flext_tests", "r"],
    "real_oracle_config": ["tests.unit.conftest", "real_oracle_config"],
    "s": ["flext_tests", "s"],
    "safe_get_first_value": ["tests.unit.test_oracle_example", "safe_get_first_value"],
    "shared_oracle_container": ["tests.unit.conftest", "shared_oracle_container"],
    "t": ["tests.typings", "FlextDbOracleTestTypes"],
    "test_api": ["tests.unit.test_api", ""],
    "test_cleanup": ["tests.unit.conftest", "test_cleanup"],
    "test_cli": ["tests.unit.test_cli", ""],
    "test_client": ["tests.unit.test_client", ""],
    "test_config": ["tests.unit.test_config", ""],
    "test_constants": ["tests.unit.test_constants", ""],
    "test_coverage_baseline": ["tests.unit.test_coverage_baseline", ""],
    "test_database_setup": ["tests.conftest", "test_database_setup"],
    "test_dispatcher": ["tests.unit.test_dispatcher", ""],
    "test_exceptions": ["tests.unit.test_exceptions", ""],
    "test_fields": ["tests.unit.test_fields", ""],
    "test_metadata": ["tests.unit.test_metadata", ""],
    "test_models": ["tests.unit.test_models", ""],
    "test_oracle": ["tests.e2e.test_oracle", ""],
    "test_oracle_example": ["tests.unit.test_oracle_example", ""],
    "test_oracle_exceptions": ["tests.unit.test_oracle_exceptions", ""],
    "test_protocols": ["tests.unit.test_protocols", ""],
    "test_services": ["tests.unit.test_services", ""],
    "test_typings": ["tests.unit.test_typings", ""],
    "test_utilities": ["tests.unit.test_utilities", ""],
    "typings": ["tests.typings", ""],
    "u": ["tests.utilities", "FlextDbOracleTestUtilities"],
    "unit": ["tests.unit", ""],
    "utilities": ["tests.utilities", ""],
    "x": ["flext_tests", "x"],
}

_EXPORTS: Sequence[str] = [
    "FlextDbOracleTestConstants",
    "FlextDbOracleTestModels",
    "FlextDbOracleTestProtocols",
    "FlextDbOracleTestTypes",
    "FlextDbOracleTestUtilities",
    "HealthCheckReport",
    "NamedItem",
    "OperationTestError",
    "TestApiModule",
    "TestApiSurgicalSimple",
    "TestBasicModelCreation",
    "TestCLIRealFunctionality",
    "TestCliServiceOperations",
    "TestConstants",
    "TestDirectCoverageBoostAPI",
    "TestDirectCoverageBoostConfig",
    "TestDirectCoverageBoostConnection",
    "TestDirectCoverageBoostObservability",
    "TestDirectCoverageBoostServices",
    "TestDirectCoverageBoostTypes",
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
    "TestFlextDbOracleConstants",
    "TestFlextDbOracleExceptions",
    "TestFlextDbOracleFields",
    "TestFlextDbOracleMetadataManagerComprehensive",
    "TestFlextDbOracleModels",
    "TestFlextDbOracleProtocols",
    "TestFlextDbOracleServices",
    "TestFlextDbOracleServicesBasic",
    "TestFlextDbOracleServicesPlaceholderRemovals",
    "TestFlextDbOracleSettings",
    "TestFlextDbOracleTypes",
    "TestFlextDbOracleUtilities",
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
    "c",
    "conftest",
    "connected_oracle_api",
    "constants",
    "d",
    "docker_control",
    "e",
    "e2e",
    "ensure_shared_docker_container",
    "flext_domains",
    "h",
    "integration",
    "logger",
    "m",
    "mock_oracle_config",
    "models",
    "oracle_api",
    "oracle_available",
    "oracle_config",
    "oracle_container",
    "p",
    "protocols",
    "pytest_configure",
    "pytest_runtest_makereport",
    "pytest_sessionstart",
    "r",
    "real_oracle_config",
    "s",
    "safe_get_first_value",
    "shared_oracle_container",
    "t",
    "test_api",
    "test_cleanup",
    "test_cli",
    "test_client",
    "test_config",
    "test_constants",
    "test_coverage_baseline",
    "test_database_setup",
    "test_dispatcher",
    "test_exceptions",
    "test_fields",
    "test_metadata",
    "test_models",
    "test_oracle",
    "test_oracle_example",
    "test_oracle_exceptions",
    "test_protocols",
    "test_services",
    "test_typings",
    "test_utilities",
    "typings",
    "u",
    "unit",
    "utilities",
    "x",
]


install_lazy_exports(__name__, globals(), _LAZY_IMPORTS, _EXPORTS)
