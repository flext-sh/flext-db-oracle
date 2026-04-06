# AUTO-GENERATED FILE — DO NOT EDIT MANUALLY.
# Regenerate with: make gen
#
"""Unit package."""

from __future__ import annotations

import typing as _t

from flext_core.lazy import install_lazy_exports

if _t.TYPE_CHECKING:
    import tests.unit.conftest as _tests_unit_conftest

    conftest = _tests_unit_conftest
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
    from flext_core.constants import FlextConstants as c
    from flext_core.decorators import FlextDecorators as d
    from flext_core.exceptions import FlextExceptions as e
    from flext_core.handlers import FlextHandlers as h
    from flext_core.mixins import FlextMixins as x
    from flext_core.models import FlextModels as m
    from flext_core.protocols import FlextProtocols as p
    from flext_core.result import FlextResult as r
    from flext_core.service import FlextService as s
    from flext_core.typings import FlextTypes as t
    from flext_core.utilities import FlextUtilities as u
    from tests.unit.test_utilities import Testu
_LAZY_IMPORTS = {
    "TestApiModule": ("tests.unit.test_api", "TestApiModule"),
    "TestApiSurgicalSimple": ("tests.unit.test_api", "TestApiSurgicalSimple"),
    "TestBasicModelCreation": (
        "tests.unit.test_coverage_baseline",
        "TestBasicModelCreation",
    ),
    "TestCLIRealFunctionality": ("tests.unit.test_cli", "TestCLIRealFunctionality"),
    "TestCliServiceOperations": ("tests.unit.test_cli", "TestCliServiceOperations"),
    "TestConstants": ("tests.unit.test_coverage_baseline", "TestConstants"),
    "TestDirectCoverageBoostAPI": (
        "tests.unit.test_services",
        "TestDirectCoverageBoostAPI",
    ),
    "TestDirectCoverageBoostConfig": (
        "tests.unit.test_services",
        "TestDirectCoverageBoostConfig",
    ),
    "TestDirectCoverageBoostConnection": (
        "tests.unit.test_services",
        "TestDirectCoverageBoostConnection",
    ),
    "TestDirectCoverageBoostObservability": (
        "tests.unit.test_services",
        "TestDirectCoverageBoostObservability",
    ),
    "TestDirectCoverageBoostServices": (
        "tests.unit.test_services",
        "TestDirectCoverageBoostServices",
    ),
    "TestDirectCoverageBoostTypes": (
        "tests.unit.test_services",
        "TestDirectCoverageBoostTypes",
    ),
    "TestDispatcherSurgical": ("tests.unit.test_dispatcher", "TestDispatcherSurgical"),
    "TestExceptions": ("tests.unit.test_coverage_baseline", "TestExceptions"),
    "TestFlextDbOracleApiRealFunctionality": (
        "tests.unit.test_api",
        "TestFlextDbOracleApiRealFunctionality",
    ),
    "TestFlextDbOracleApiSafeMethods": (
        "tests.unit.test_api",
        "TestFlextDbOracleApiSafeMethods",
    ),
    "TestFlextDbOracleApiWorking": (
        "tests.unit.test_api",
        "TestFlextDbOracleApiWorking",
    ),
    "TestFlextDbOracleCli": ("tests.unit.test_cli", "TestFlextDbOracleCli"),
    "TestFlextDbOracleClientIntegration": (
        "tests.unit.test_cli",
        "TestFlextDbOracleClientIntegration",
    ),
    "TestFlextDbOracleClientReal": (
        "tests.unit.test_cli",
        "TestFlextDbOracleClientReal",
    ),
    "TestFlextDbOracleClientRealFunctionality": (
        "tests.unit.test_client",
        "TestFlextDbOracleClientRealFunctionality",
    ),
    "TestFlextDbOracleConnectionSimple": (
        "tests.unit.test_services",
        "TestFlextDbOracleConnectionSimple",
    ),
    "TestFlextDbOracleFields": ("tests.unit.test_fields", "TestFlextDbOracleFields"),
    "TestFlextDbOracleMetadataManagerComprehensive": (
        "tests.unit.test_services",
        "TestFlextDbOracleMetadataManagerComprehensive",
    ),
    "TestFlextDbOracleProtocols": (
        "tests.unit.test_protocols",
        "TestFlextDbOracleProtocols",
    ),
    "TestFlextDbOracleServices": (
        "tests.unit.test_coverage_baseline",
        "TestFlextDbOracleServices",
    ),
    "TestFlextDbOracleServicesBasic": (
        "tests.unit.test_services",
        "TestFlextDbOracleServicesBasic",
    ),
    "TestFlextDbOracleServicesPlaceholderRemovals": (
        "tests.unit.test_services",
        "TestFlextDbOracleServicesPlaceholderRemovals",
    ),
    "TestFlextDbOracleSettings": (
        "tests.unit.test_models",
        "TestFlextDbOracleSettings",
    ),
    "TestFlextDbOracleTypes": ("tests.unit.test_typings", "TestFlextDbOracleTypes"),
    "TestModuleImports": ("tests.unit.test_coverage_baseline", "TestModuleImports"),
    "TestOracleConnectionHelper": ("tests.unit.test_cli", "TestOracleConnectionHelper"),
    "TestOutputFormatter": ("tests.unit.test_cli", "TestOutputFormatter"),
    "TestRealOracleApi": ("tests.unit.test_oracle_example", "TestRealOracleApi"),
    "TestRealOracleConnection": (
        "tests.unit.test_oracle_example",
        "TestRealOracleConnection",
    ),
    "TestRealOracleErrorHandling": (
        "tests.unit.test_oracle_example",
        "TestRealOracleErrorHandling",
    ),
    "TestRealOracleExceptionHierarchy": (
        "tests.unit.test_oracle_exceptions",
        "TestRealOracleExceptionHierarchy",
    ),
    "TestRealOracleExceptionsAdvanced": (
        "tests.unit.test_oracle_exceptions",
        "TestRealOracleExceptionsAdvanced",
    ),
    "TestRealOracleExceptionsCore": (
        "tests.unit.test_oracle_exceptions",
        "TestRealOracleExceptionsCore",
    ),
    "TestServiceErrorHandling": (
        "tests.unit.test_services",
        "TestServiceErrorHandling",
    ),
    "TestUtilities": ("tests.unit.test_coverage_baseline", "TestUtilities"),
    "TestYamlModule": ("tests.unit.test_cli", "TestYamlModule"),
    "Testc": ("tests.unit.test_constants", "Testc"),
    "Teste": ("tests.unit.test_exceptions", "Teste"),
    "Testm": ("tests.unit.test_models", "Testm"),
    "Testu": ("tests.unit.test_utilities", "Testu"),
    "c": ("flext_core.constants", "FlextConstants"),
    "conftest": "tests.unit.conftest",
    "connected_oracle_api": ("tests.unit.conftest", "connected_oracle_api"),
    "d": ("flext_core.decorators", "FlextDecorators"),
    "docker_control": ("tests.unit.conftest", "docker_control"),
    "e": ("flext_core.exceptions", "FlextExceptions"),
    "ensure_shared_docker_container": (
        "tests.unit.conftest",
        "ensure_shared_docker_container",
    ),
    "h": ("flext_core.handlers", "FlextHandlers"),
    "logger": ("tests.unit.conftest", "logger"),
    "m": ("flext_core.models", "FlextModels"),
    "mock_oracle_config": ("tests.unit.conftest", "mock_oracle_config"),
    "oracle_api": ("tests.unit.conftest", "oracle_api"),
    "oracle_available": ("tests.unit.conftest", "oracle_available"),
    "oracle_config": ("tests.unit.conftest", "oracle_config"),
    "oracle_container": ("tests.unit.conftest", "oracle_container"),
    "p": ("flext_core.protocols", "FlextProtocols"),
    "r": ("flext_core.result", "FlextResult"),
    "real_oracle_config": ("tests.unit.conftest", "real_oracle_config"),
    "s": ("flext_core.service", "FlextService"),
    "safe_get_first_value": ("tests.unit.test_oracle_example", "safe_get_first_value"),
    "shared_oracle_container": ("tests.unit.conftest", "shared_oracle_container"),
    "t": ("flext_core.typings", "FlextTypes"),
    "test_api": "tests.unit.test_api",
    "test_cleanup": ("tests.unit.conftest", "test_cleanup"),
    "test_cli": "tests.unit.test_cli",
    "test_client": "tests.unit.test_client",
    "test_config": "tests.unit.test_config",
    "test_constants": "tests.unit.test_constants",
    "test_coverage_baseline": "tests.unit.test_coverage_baseline",
    "test_dispatcher": "tests.unit.test_dispatcher",
    "test_exceptions": "tests.unit.test_exceptions",
    "test_fields": "tests.unit.test_fields",
    "test_metadata": "tests.unit.test_metadata",
    "test_models": "tests.unit.test_models",
    "test_oracle_example": "tests.unit.test_oracle_example",
    "test_oracle_exceptions": "tests.unit.test_oracle_exceptions",
    "test_protocols": "tests.unit.test_protocols",
    "test_services": "tests.unit.test_services",
    "test_typings": "tests.unit.test_typings",
    "test_utilities": "tests.unit.test_utilities",
    "u": ("flext_core.utilities", "FlextUtilities"),
    "x": ("flext_core.mixins", "FlextMixins"),
}

__all__ = [
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
    "d",
    "docker_control",
    "e",
    "ensure_shared_docker_container",
    "h",
    "logger",
    "m",
    "mock_oracle_config",
    "oracle_api",
    "oracle_available",
    "oracle_config",
    "oracle_container",
    "p",
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
    "test_dispatcher",
    "test_exceptions",
    "test_fields",
    "test_metadata",
    "test_models",
    "test_oracle_example",
    "test_oracle_exceptions",
    "test_protocols",
    "test_services",
    "test_typings",
    "test_utilities",
    "u",
    "x",
]


install_lazy_exports(__name__, globals(), _LAZY_IMPORTS)
