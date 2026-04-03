# AUTO-GENERATED FILE — DO NOT EDIT MANUALLY.
# Regenerate with: make gen
#
"""Tests package."""

from __future__ import annotations

import typing as _t

from flext_core.lazy import install_lazy_exports, merge_lazy_imports

if _t.TYPE_CHECKING:
    import tests.conftest as _tests_conftest

    conftest = _tests_conftest
    import tests.constants as _tests_constants
    from tests.conftest import (
        flext_domains,
        pytest_configure,
        pytest_runtest_makereport,
        pytest_sessionstart,
        test_database_setup,
    )

    constants = _tests_constants
    import tests.e2e as _tests_e2e
    from tests.constants import (
        FlextDbOracleTestConstants,
        FlextDbOracleTestConstants as c,
    )

    e2e = _tests_e2e
    import tests.e2e.test_oracle as _tests_e2e_test_oracle

    test_oracle = _tests_e2e_test_oracle
    import tests.exceptions as _tests_exceptions
    from tests.e2e.test_oracle import OperationTestError, TestOracleE2E

    exceptions = _tests_exceptions
    import tests.integration as _tests_integration
    from tests.exceptions import (
        FlextDbOracleTestExceptions,
        FlextDbOracleTestExceptions as e,
    )

    integration = _tests_integration
    import tests.models as _tests_models
    from tests.integration.test_oracle import TestOracleIntegration

    models = _tests_models
    import tests.protocols as _tests_protocols
    from tests.models import FlextDbOracleTestModels, FlextDbOracleTestModels as m

    protocols = _tests_protocols
    import tests.typings as _tests_typings
    from tests.protocols import (
        FlextDbOracleTestProtocols,
        FlextDbOracleTestProtocols as p,
    )

    typings = _tests_typings
    import tests.unit as _tests_unit
    from tests.typings import FlextDbOracleTestTypes, FlextDbOracleTestTypes as t

    unit = _tests_unit
    import tests.unit.test_api as _tests_unit_test_api
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

    test_api = _tests_unit_test_api
    import tests.unit.test_cli as _tests_unit_test_cli
    from tests.unit.test_api import (
        TestApiModule,
        TestApiSurgicalSimple,
        TestFlextDbOracleApiRealFunctionality,
        TestFlextDbOracleApiSafeMethods,
        TestFlextDbOracleApiWorking,
    )

    test_cli = _tests_unit_test_cli
    import tests.unit.test_client as _tests_unit_test_client
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

    test_client = _tests_unit_test_client
    import tests.unit.test_config as _tests_unit_test_config
    from tests.unit.test_client import TestFlextDbOracleClientRealFunctionality

    test_config = _tests_unit_test_config
    import tests.unit.test_constants as _tests_unit_test_constants

    test_constants = _tests_unit_test_constants
    import tests.unit.test_coverage_baseline as _tests_unit_test_coverage_baseline
    from tests.unit.test_constants import Testc

    test_coverage_baseline = _tests_unit_test_coverage_baseline
    import tests.unit.test_dispatcher as _tests_unit_test_dispatcher
    from tests.unit.test_coverage_baseline import (
        TestBasicModelCreation,
        TestConstants,
        TestExceptions,
        TestFlextDbOracleServices,
        TestModuleImports,
        TestUtilities,
    )

    test_dispatcher = _tests_unit_test_dispatcher
    import tests.unit.test_exceptions as _tests_unit_test_exceptions
    from tests.unit.test_dispatcher import TestDispatcherSurgical

    test_exceptions = _tests_unit_test_exceptions
    import tests.unit.test_fields as _tests_unit_test_fields
    from tests.unit.test_exceptions import Teste

    test_fields = _tests_unit_test_fields
    import tests.unit.test_metadata as _tests_unit_test_metadata
    from tests.unit.test_fields import TestFlextDbOracleFields

    test_metadata = _tests_unit_test_metadata
    import tests.unit.test_models as _tests_unit_test_models

    test_models = _tests_unit_test_models
    import tests.unit.test_oracle_example as _tests_unit_test_oracle_example
    from tests.unit.test_models import TestFlextDbOracleSettings, Testm

    test_oracle_example = _tests_unit_test_oracle_example
    import tests.unit.test_oracle_exceptions as _tests_unit_test_oracle_exceptions
    from tests.unit.test_oracle_example import (
        TestRealOracleApi,
        TestRealOracleConnection,
        TestRealOracleErrorHandling,
        safe_get_first_value,
    )

    test_oracle_exceptions = _tests_unit_test_oracle_exceptions
    import tests.unit.test_protocols as _tests_unit_test_protocols
    from tests.unit.test_oracle_exceptions import (
        TestRealOracleExceptionHierarchy,
        TestRealOracleExceptionsAdvanced,
        TestRealOracleExceptionsCore,
    )

    test_protocols = _tests_unit_test_protocols
    import tests.unit.test_services as _tests_unit_test_services
    from tests.unit.test_protocols import TestFlextDbOracleProtocols

    test_services = _tests_unit_test_services
    import tests.unit.test_typings as _tests_unit_test_typings
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

    test_typings = _tests_unit_test_typings
    import tests.unit.test_utilities as _tests_unit_test_utilities
    from tests.unit.test_typings import TestFlextDbOracleTypes

    test_utilities = _tests_unit_test_utilities
    import tests.utilities as _tests_utilities
    from tests.unit.test_utilities import Testu

    utilities = _tests_utilities
    from flext_core.decorators import FlextDecorators as d
    from flext_core.handlers import FlextHandlers as h
    from flext_core.mixins import FlextMixins as x
    from flext_core.result import FlextResult as r
    from flext_core.service import FlextService as s
    from tests.utilities import (
        FlextDbOracleTestUtilities,
        FlextDbOracleTestUtilities as u,
    )
_LAZY_IMPORTS = merge_lazy_imports(
    (
        "tests.e2e",
        "tests.integration",
        "tests.unit",
    ),
    {
        "FlextDbOracleTestConstants": "tests.constants",
        "FlextDbOracleTestExceptions": "tests.exceptions",
        "FlextDbOracleTestModels": "tests.models",
        "FlextDbOracleTestProtocols": "tests.protocols",
        "FlextDbOracleTestTypes": "tests.typings",
        "FlextDbOracleTestUtilities": "tests.utilities",
        "c": ("tests.constants", "FlextDbOracleTestConstants"),
        "conftest": "tests.conftest",
        "constants": "tests.constants",
        "d": ("flext_core.decorators", "FlextDecorators"),
        "e": ("tests.exceptions", "FlextDbOracleTestExceptions"),
        "e2e": "tests.e2e",
        "exceptions": "tests.exceptions",
        "flext_domains": "tests.conftest",
        "h": ("flext_core.handlers", "FlextHandlers"),
        "integration": "tests.integration",
        "m": ("tests.models", "FlextDbOracleTestModels"),
        "models": "tests.models",
        "p": ("tests.protocols", "FlextDbOracleTestProtocols"),
        "protocols": "tests.protocols",
        "pytest_configure": "tests.conftest",
        "pytest_runtest_makereport": "tests.conftest",
        "pytest_sessionstart": "tests.conftest",
        "r": ("flext_core.result", "FlextResult"),
        "s": ("flext_core.service", "FlextService"),
        "t": ("tests.typings", "FlextDbOracleTestTypes"),
        "test_database_setup": "tests.conftest",
        "typings": "tests.typings",
        "u": ("tests.utilities", "FlextDbOracleTestUtilities"),
        "unit": "tests.unit",
        "utilities": "tests.utilities",
        "x": ("flext_core.mixins", "FlextMixins"),
    },
)

__all__ = [
    "FlextDbOracleTestConstants",
    "FlextDbOracleTestExceptions",
    "FlextDbOracleTestModels",
    "FlextDbOracleTestProtocols",
    "FlextDbOracleTestTypes",
    "FlextDbOracleTestUtilities",
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
    "TestFlextDbOracleFields",
    "TestFlextDbOracleMetadataManagerComprehensive",
    "TestFlextDbOracleProtocols",
    "TestFlextDbOracleServices",
    "TestFlextDbOracleServicesBasic",
    "TestFlextDbOracleServicesPlaceholderRemovals",
    "TestFlextDbOracleSettings",
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
    "Testu",
    "c",
    "conftest",
    "connected_oracle_api",
    "constants",
    "d",
    "docker_control",
    "e",
    "e2e",
    "ensure_shared_docker_container",
    "exceptions",
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


install_lazy_exports(__name__, globals(), _LAZY_IMPORTS)
