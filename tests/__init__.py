# AUTO-GENERATED FILE — DO NOT EDIT MANUALLY.
# Regenerate with: make codegen
#
"""Tests package."""

from __future__ import annotations

from collections.abc import Mapping, MutableMapping, Sequence
from typing import TYPE_CHECKING

from flext_core.lazy import cleanup_submodule_namespace, lazy_getattr


if TYPE_CHECKING:
    from flext_core import FlextTypes
    from flext_tests import d, e, h, r, s, x

    from tests.conftest import (
        flext_domains,
        pytest_configure,
        pytest_runtest_makereport,
        pytest_sessionstart,
        test_database_setup,
    )
    from tests.constants import (
        FlextDbOracleTestConstants,
        FlextDbOracleTestConstants as c,
    )
    import tests.e2e as e2e
    from tests.e2e.test_oracle import OperationTestError, TestOracleE2E
    import tests.integration as integration
    from tests.integration.test_oracle import TestOracleIntegration
    from tests.models import FlextDbOracleTestModels, FlextDbOracleTestModels as m
    from tests.protocols import (
        FlextDbOracleTestProtocols,
        FlextDbOracleTestProtocols as p,
    )
    from tests.typings import FlextDbOracleTestTypes, FlextDbOracleTestTypes as t
    import tests.unit as unit
    from tests.unit.conftest import (
        connected_oracle_api,
        docker_control,
        ensure_shared_docker_container,
        logger,
        mock_oracle_config,
        oracle_api,
        oracle_available,
        oracle_config,
        oracle_container,
        real_oracle_config,
        shared_oracle_container,
        test_cleanup,
    )
    from tests.unit.test_api import (
        TestApiModule,
        TestApiSurgicalSimple,
        TestFlextDbOracleApiRealFunctionality,
        TestFlextDbOracleApiSafeMethods,
        TestFlextDbOracleApiWorking,
    )
    from tests.unit.test_cli import (
        HealthCheckReport,
        NamedItem,
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
    from tests.unit.test_constants import TestFlextDbOracleConstants
    from tests.unit.test_coverage_baseline import (
        TestBasicModelCreation,
        TestConstants,
        TestExceptions,
        TestFlextDbOracleServices,
        TestModuleImports,
        TestUtilities,
    )
    from tests.unit.test_dispatcher import TestDispatcherSurgical
    from tests.unit.test_exceptions import TestFlextDbOracleExceptions
    from tests.unit.test_fields import TestFlextDbOracleFields
    from tests.unit.test_models import (
        TestFlextDbOracleModels,
        TestFlextDbOracleSettings,
    )
    from tests.unit.test_oracle_example import (
        TestRealOracleApi,
        TestRealOracleConnection,
        TestRealOracleErrorHandling,
        safe_get_first_value,
    )
    from tests.unit.test_oracle_exceptions import (
        TestRealOracleExceptionHierarchy,
        TestRealOracleExceptionsAdvanced,
        TestRealOracleExceptionsCore,
    )
    from tests.unit.test_protocols import TestFlextDbOracleProtocols
    from tests.unit.test_services import (
        TestDirectCoverageBoostAPI,
        TestDirectCoverageBoostConfig,
        TestDirectCoverageBoostConnection,
        TestDirectCoverageBoostObservability,
        TestDirectCoverageBoostServices,
        TestDirectCoverageBoostTypes,
        TestFlextDbOracleConnectionSimple,
        TestFlextDbOracleMetadataManagerComprehensive,
        TestFlextDbOracleServicesBasic,
        TestFlextDbOracleServicesPlaceholderRemovals,
        TestServiceErrorHandling,
    )
    from tests.unit.test_typings import TestFlextDbOracleTypes
    from tests.unit.test_utilities import TestFlextDbOracleUtilities
    from tests.utilities import (
        FlextDbOracleTestUtilities,
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
    "TestBasicModelCreation": ["tests.unit.test_coverage_baseline", "TestBasicModelCreation"],
    "TestCLIRealFunctionality": ["tests.unit.test_cli", "TestCLIRealFunctionality"],
    "TestCliServiceOperations": ["tests.unit.test_cli", "TestCliServiceOperations"],
    "TestConstants": ["tests.unit.test_coverage_baseline", "TestConstants"],
    "TestDirectCoverageBoostAPI": ["tests.unit.test_services", "TestDirectCoverageBoostAPI"],
    "TestDirectCoverageBoostConfig": ["tests.unit.test_services", "TestDirectCoverageBoostConfig"],
    "TestDirectCoverageBoostConnection": ["tests.unit.test_services", "TestDirectCoverageBoostConnection"],
    "TestDirectCoverageBoostObservability": ["tests.unit.test_services", "TestDirectCoverageBoostObservability"],
    "TestDirectCoverageBoostServices": ["tests.unit.test_services", "TestDirectCoverageBoostServices"],
    "TestDirectCoverageBoostTypes": ["tests.unit.test_services", "TestDirectCoverageBoostTypes"],
    "TestDispatcherSurgical": ["tests.unit.test_dispatcher", "TestDispatcherSurgical"],
    "TestExceptions": ["tests.unit.test_coverage_baseline", "TestExceptions"],
    "TestFlextDbOracleApiRealFunctionality": ["tests.unit.test_api", "TestFlextDbOracleApiRealFunctionality"],
    "TestFlextDbOracleApiSafeMethods": ["tests.unit.test_api", "TestFlextDbOracleApiSafeMethods"],
    "TestFlextDbOracleApiWorking": ["tests.unit.test_api", "TestFlextDbOracleApiWorking"],
    "TestFlextDbOracleCli": ["tests.unit.test_cli", "TestFlextDbOracleCli"],
    "TestFlextDbOracleClientIntegration": ["tests.unit.test_cli", "TestFlextDbOracleClientIntegration"],
    "TestFlextDbOracleClientReal": ["tests.unit.test_cli", "TestFlextDbOracleClientReal"],
    "TestFlextDbOracleClientRealFunctionality": ["tests.unit.test_client", "TestFlextDbOracleClientRealFunctionality"],
    "TestFlextDbOracleConnectionSimple": ["tests.unit.test_services", "TestFlextDbOracleConnectionSimple"],
    "TestFlextDbOracleConstants": ["tests.unit.test_constants", "TestFlextDbOracleConstants"],
    "TestFlextDbOracleExceptions": ["tests.unit.test_exceptions", "TestFlextDbOracleExceptions"],
    "TestFlextDbOracleFields": ["tests.unit.test_fields", "TestFlextDbOracleFields"],
    "TestFlextDbOracleMetadataManagerComprehensive": ["tests.unit.test_services", "TestFlextDbOracleMetadataManagerComprehensive"],
    "TestFlextDbOracleModels": ["tests.unit.test_models", "TestFlextDbOracleModels"],
    "TestFlextDbOracleProtocols": ["tests.unit.test_protocols", "TestFlextDbOracleProtocols"],
    "TestFlextDbOracleServices": ["tests.unit.test_coverage_baseline", "TestFlextDbOracleServices"],
    "TestFlextDbOracleServicesBasic": ["tests.unit.test_services", "TestFlextDbOracleServicesBasic"],
    "TestFlextDbOracleServicesPlaceholderRemovals": ["tests.unit.test_services", "TestFlextDbOracleServicesPlaceholderRemovals"],
    "TestFlextDbOracleSettings": ["tests.unit.test_models", "TestFlextDbOracleSettings"],
    "TestFlextDbOracleTypes": ["tests.unit.test_typings", "TestFlextDbOracleTypes"],
    "TestFlextDbOracleUtilities": ["tests.unit.test_utilities", "TestFlextDbOracleUtilities"],
    "TestModuleImports": ["tests.unit.test_coverage_baseline", "TestModuleImports"],
    "TestOracleConnectionHelper": ["tests.unit.test_cli", "TestOracleConnectionHelper"],
    "TestOracleE2E": ["tests.e2e.test_oracle", "TestOracleE2E"],
    "TestOracleIntegration": ["tests.integration.test_oracle", "TestOracleIntegration"],
    "TestOutputFormatter": ["tests.unit.test_cli", "TestOutputFormatter"],
    "TestRealOracleApi": ["tests.unit.test_oracle_example", "TestRealOracleApi"],
    "TestRealOracleConnection": ["tests.unit.test_oracle_example", "TestRealOracleConnection"],
    "TestRealOracleErrorHandling": ["tests.unit.test_oracle_example", "TestRealOracleErrorHandling"],
    "TestRealOracleExceptionHierarchy": ["tests.unit.test_oracle_exceptions", "TestRealOracleExceptionHierarchy"],
    "TestRealOracleExceptionsAdvanced": ["tests.unit.test_oracle_exceptions", "TestRealOracleExceptionsAdvanced"],
    "TestRealOracleExceptionsCore": ["tests.unit.test_oracle_exceptions", "TestRealOracleExceptionsCore"],
    "TestServiceErrorHandling": ["tests.unit.test_services", "TestServiceErrorHandling"],
    "TestUtilities": ["tests.unit.test_coverage_baseline", "TestUtilities"],
    "TestYamlModule": ["tests.unit.test_cli", "TestYamlModule"],
    "c": ["tests.constants", "FlextDbOracleTestConstants"],
    "connected_oracle_api": ["tests.unit.conftest", "connected_oracle_api"],
    "d": ["flext_tests", "d"],
    "docker_control": ["tests.unit.conftest", "docker_control"],
    "e": ["flext_tests", "e"],
    "e2e": ["tests.e2e", ""],
    "ensure_shared_docker_container": ["tests.unit.conftest", "ensure_shared_docker_container"],
    "flext_domains": ["tests.conftest", "flext_domains"],
    "h": ["flext_tests", "h"],
    "integration": ["tests.integration", ""],
    "logger": ["tests.unit.conftest", "logger"],
    "m": ["tests.models", "FlextDbOracleTestModels"],
    "mock_oracle_config": ["tests.unit.conftest", "mock_oracle_config"],
    "oracle_api": ["tests.unit.conftest", "oracle_api"],
    "oracle_available": ["tests.unit.conftest", "oracle_available"],
    "oracle_config": ["tests.unit.conftest", "oracle_config"],
    "oracle_container": ["tests.unit.conftest", "oracle_container"],
    "p": ["tests.protocols", "FlextDbOracleTestProtocols"],
    "pytest_configure": ["tests.conftest", "pytest_configure"],
    "pytest_runtest_makereport": ["tests.conftest", "pytest_runtest_makereport"],
    "pytest_sessionstart": ["tests.conftest", "pytest_sessionstart"],
    "r": ["flext_tests", "r"],
    "real_oracle_config": ["tests.unit.conftest", "real_oracle_config"],
    "s": ["flext_tests", "s"],
    "safe_get_first_value": ["tests.unit.test_oracle_example", "safe_get_first_value"],
    "shared_oracle_container": ["tests.unit.conftest", "shared_oracle_container"],
    "t": ["tests.typings", "FlextDbOracleTestTypes"],
    "test_cleanup": ["tests.unit.conftest", "test_cleanup"],
    "test_database_setup": ["tests.conftest", "test_database_setup"],
    "u": ["tests.utilities", "FlextDbOracleTestUtilities"],
    "unit": ["tests.unit", ""],
    "x": ["flext_tests", "x"],
}

__all__ = [
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
    "connected_oracle_api",
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
    "oracle_api",
    "oracle_available",
    "oracle_config",
    "oracle_container",
    "p",
    "pytest_configure",
    "pytest_runtest_makereport",
    "pytest_sessionstart",
    "r",
    "real_oracle_config",
    "s",
    "safe_get_first_value",
    "shared_oracle_container",
    "t",
    "test_cleanup",
    "test_database_setup",
    "u",
    "unit",
    "x",
]


_LAZY_CACHE: MutableMapping[str, FlextTypes.ModuleExport] = {}


def __getattr__(name: str) -> FlextTypes.ModuleExport:
    """Lazy-load module attributes on first access (PEP 562).

    A local cache ``_LAZY_CACHE`` persists resolved objects across repeated
    accesses during process lifetime.

    Args:
        name: Attribute name requested by dir()/import.

    Returns:
        Lazy-loaded module export type.

    Raises:
        AttributeError: If attribute not registered.
    """
    if name in _LAZY_CACHE:
        return _LAZY_CACHE[name]

    value = lazy_getattr(name, _LAZY_IMPORTS, globals(), __name__)
    _LAZY_CACHE[name] = value
    return value


def __dir__() -> Sequence[str]:
    """Return list of available attributes for dir() and autocomplete.

    Returns:
        List of public names from module exports.
    """
    return sorted(__all__)


cleanup_submodule_namespace(__name__, _LAZY_IMPORTS)