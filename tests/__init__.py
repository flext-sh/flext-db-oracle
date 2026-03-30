# AUTO-GENERATED FILE — DO NOT EDIT MANUALLY.
# Regenerate with: make gen
#
"""Tests package."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import TYPE_CHECKING

from flext_core.lazy import install_lazy_exports

if TYPE_CHECKING:
    from flext_tests import *

    from tests import conftest, constants, models, protocols, typings, utilities
    from tests.conftest import *
    from tests.constants import *
    from tests.e2e import *
    from tests.integration import *
    from tests.models import *
    from tests.protocols import *
    from tests.typings import *
    from tests.unit import *
    from tests.utilities import *

_LAZY_IMPORTS: Mapping[str, str | Sequence[str]] = {
    "FlextDbOracleTestConstants": "tests.constants",
    "FlextDbOracleTestModels": "tests.models",
    "FlextDbOracleTestProtocols": "tests.protocols",
    "FlextDbOracleTestTypes": "tests.typings",
    "FlextDbOracleTestUtilities": "tests.utilities",
    "HealthCheckReport": "tests.unit.test_cli",
    "NamedItem": "tests.unit.test_cli",
    "OperationTestError": "tests.e2e.test_oracle",
    "TestApiModule": "tests.unit.test_api",
    "TestApiSurgicalSimple": "tests.unit.test_api",
    "TestBasicModelCreation": "tests.unit.test_coverage_baseline",
    "TestCLIRealFunctionality": "tests.unit.test_cli",
    "TestCliServiceOperations": "tests.unit.test_cli",
    "TestConstants": "tests.unit.test_coverage_baseline",
    "TestDirectCoverageBoostAPI": "tests.unit.test_services",
    "TestDirectCoverageBoostConfig": "tests.unit.test_services",
    "TestDirectCoverageBoostConnection": "tests.unit.test_services",
    "TestDirectCoverageBoostObservability": "tests.unit.test_services",
    "TestDirectCoverageBoostServices": "tests.unit.test_services",
    "TestDirectCoverageBoostTypes": "tests.unit.test_services",
    "TestDispatcherSurgical": "tests.unit.test_dispatcher",
    "TestExceptions": "tests.unit.test_coverage_baseline",
    "TestFlextDbOracleApiRealFunctionality": "tests.unit.test_api",
    "TestFlextDbOracleApiSafeMethods": "tests.unit.test_api",
    "TestFlextDbOracleApiWorking": "tests.unit.test_api",
    "TestFlextDbOracleCli": "tests.unit.test_cli",
    "TestFlextDbOracleClientIntegration": "tests.unit.test_cli",
    "TestFlextDbOracleClientReal": "tests.unit.test_cli",
    "TestFlextDbOracleClientRealFunctionality": "tests.unit.test_client",
    "TestFlextDbOracleConnectionSimple": "tests.unit.test_services",
    "TestFlextDbOracleConstants": "tests.unit.test_constants",
    "TestFlextDbOracleExceptions": "tests.unit.test_exceptions",
    "TestFlextDbOracleFields": "tests.unit.test_fields",
    "TestFlextDbOracleMetadataManagerComprehensive": "tests.unit.test_services",
    "TestFlextDbOracleModels": "tests.unit.test_models",
    "TestFlextDbOracleProtocols": "tests.unit.test_protocols",
    "TestFlextDbOracleServices": "tests.unit.test_coverage_baseline",
    "TestFlextDbOracleServicesBasic": "tests.unit.test_services",
    "TestFlextDbOracleServicesPlaceholderRemovals": "tests.unit.test_services",
    "TestFlextDbOracleSettings": "tests.unit.test_models",
    "TestFlextDbOracleTypes": "tests.unit.test_typings",
    "TestFlextDbOracleUtilities": "tests.unit.test_utilities",
    "TestModuleImports": "tests.unit.test_coverage_baseline",
    "TestOracleConnectionHelper": "tests.unit.test_cli",
    "TestOracleE2E": "tests.e2e.test_oracle",
    "TestOracleIntegration": "tests.integration.test_oracle",
    "TestOutputFormatter": "tests.unit.test_cli",
    "TestRealOracleApi": "tests.unit.test_oracle_example",
    "TestRealOracleConnection": "tests.unit.test_oracle_example",
    "TestRealOracleErrorHandling": "tests.unit.test_oracle_example",
    "TestRealOracleExceptionHierarchy": "tests.unit.test_oracle_exceptions",
    "TestRealOracleExceptionsAdvanced": "tests.unit.test_oracle_exceptions",
    "TestRealOracleExceptionsCore": "tests.unit.test_oracle_exceptions",
    "TestServiceErrorHandling": "tests.unit.test_services",
    "TestUtilities": "tests.unit.test_coverage_baseline",
    "TestYamlModule": "tests.unit.test_cli",
    "c": ["tests.constants", "FlextDbOracleTestConstants"],
    "conftest": "tests.conftest",
    "connected_oracle_api": "tests.unit.conftest",
    "constants": "tests.constants",
    "d": "flext_tests",
    "docker_control": "tests.unit.conftest",
    "e": "flext_tests",
    "e2e": "tests.e2e",
    "ensure_shared_docker_container": "tests.unit.conftest",
    "flext_domains": "tests.conftest",
    "h": "flext_tests",
    "integration": "tests.integration",
    "logger": "tests.unit.conftest",
    "m": ["tests.models", "FlextDbOracleTestModels"],
    "mock_oracle_config": "tests.unit.conftest",
    "models": "tests.models",
    "oracle_api": "tests.unit.conftest",
    "oracle_available": "tests.unit.conftest",
    "oracle_config": "tests.unit.conftest",
    "oracle_container": "tests.unit.conftest",
    "p": ["tests.protocols", "FlextDbOracleTestProtocols"],
    "protocols": "tests.protocols",
    "pytest_configure": "tests.conftest",
    "pytest_runtest_makereport": "tests.conftest",
    "pytest_sessionstart": "tests.conftest",
    "r": "flext_tests",
    "real_oracle_config": "tests.unit.conftest",
    "s": "flext_tests",
    "safe_get_first_value": "tests.unit.test_oracle_example",
    "shared_oracle_container": "tests.unit.conftest",
    "t": ["tests.typings", "FlextDbOracleTestTypes"],
    "test_api": "tests.unit.test_api",
    "test_cleanup": "tests.unit.conftest",
    "test_cli": "tests.unit.test_cli",
    "test_client": "tests.unit.test_client",
    "test_config": "tests.unit.test_config",
    "test_constants": "tests.unit.test_constants",
    "test_coverage_baseline": "tests.unit.test_coverage_baseline",
    "test_database_setup": "tests.conftest",
    "test_dispatcher": "tests.unit.test_dispatcher",
    "test_exceptions": "tests.unit.test_exceptions",
    "test_fields": "tests.unit.test_fields",
    "test_metadata": "tests.unit.test_metadata",
    "test_models": "tests.unit.test_models",
    "test_oracle": "tests.e2e.test_oracle",
    "test_oracle_example": "tests.unit.test_oracle_example",
    "test_oracle_exceptions": "tests.unit.test_oracle_exceptions",
    "test_protocols": "tests.unit.test_protocols",
    "test_services": "tests.unit.test_services",
    "test_typings": "tests.unit.test_typings",
    "test_utilities": "tests.unit.test_utilities",
    "typings": "tests.typings",
    "u": ["tests.utilities", "FlextDbOracleTestUtilities"],
    "unit": "tests.unit",
    "utilities": "tests.utilities",
    "x": "flext_tests",
}


install_lazy_exports(__name__, globals(), _LAZY_IMPORTS, sorted(_LAZY_IMPORTS))
