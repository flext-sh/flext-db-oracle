# AUTO-GENERATED FILE — DO NOT EDIT MANUALLY.
# Regenerate with: make codegen
#
"""init   module.

This module is part of the FLEXT ecosystem. Docstrings follow PEP 257 and Google style.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from typing import TYPE_CHECKING

from flext_core.lazy import cleanup_submodule_namespace, lazy_getattr

if TYPE_CHECKING:
    from flext_core.typings import FlextTypes

    from .conftest import (
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
    from .test_api import (
        TestApiModule,
        TestApiSurgicalSimple,
        TestFlextDbOracleApiRealFunctionality,
        TestFlextDbOracleApiSafeMethods,
        TestFlextDbOracleApiWorking,
    )
    from .test_cli import (
        TestCLIRealFunctionality,
        TestCliServiceOperations,
        TestFlextDbOracleCli,
        TestFlextDbOracleClientIntegration,
        TestFlextDbOracleClientReal,
        TestOracleConnectionHelper,
        TestOutputFormatter,
        TestYamlModule,
    )
    from .test_client import TestFlextDbOracleClientRealFunctionality
    from .test_constants import (
        TestFlextDbOracleConstants,
        TestFlextDbOracleConstants as c,
    )
    from .test_coverage_baseline import (
        TestBasicModelCreation,
        TestConstants,
        TestExceptions,
        TestExceptions as e,
        TestFlextDbOracleServices,
        TestModuleImports,
        TestUtilities,
        TestUtilities as u,
    )
    from .test_dispatcher import TestDispatcherSurgical
    from .test_exceptions import TestFlextDbOracleExceptions
    from .test_fields import TestFlextDbOracleFields
    from .test_models import (
        TestFlextDbOracleModels,
        TestFlextDbOracleModels as m,
        TestFlextDbOracleSettings,
    )
    from .test_oracle_example import (
        TestRealOracleApi,
        TestRealOracleConnection,
        TestRealOracleErrorHandling,
        safe_get_first_value,
    )
    from .test_oracle_exceptions import (
        TestRealOracleExceptionHierarchy,
        TestRealOracleExceptionsAdvanced,
        TestRealOracleExceptionsCore,
    )
    from .test_protocols import (
        TestFlextDbOracleProtocols,
        TestFlextDbOracleProtocols as p,
    )
    from .test_services import (
        TestDirectCoverageBoostAPI,
        TestDirectCoverageBoostConfig,
        TestDirectCoverageBoostConnection,
        TestDirectCoverageBoostObservability,
        TestDirectCoverageBoostServices,
        TestDirectCoverageBoostTypes,
        TestDirectCoverageBoostTypes as t,
        TestFlextDbOracleConnectionSimple,
        TestFlextDbOracleMetadataManagerComprehensive,
        TestFlextDbOracleServicesBasic,
        TestFlextDbOracleServicesPlaceholderRemovals,
        TestServiceErrorHandling,
    )
    from .test_typings import TestFlextDbOracleTypes
    from .test_utilities import TestFlextDbOracleUtilities

_LAZY_IMPORTS: dict[str, tuple[str, str]] = {
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
    "TestFlextDbOracleConstants": (
        "tests.unit.test_constants",
        "TestFlextDbOracleConstants",
    ),
    "TestFlextDbOracleExceptions": (
        "tests.unit.test_exceptions",
        "TestFlextDbOracleExceptions",
    ),
    "TestFlextDbOracleFields": ("tests.unit.test_fields", "TestFlextDbOracleFields"),
    "TestFlextDbOracleMetadataManagerComprehensive": (
        "tests.unit.test_services",
        "TestFlextDbOracleMetadataManagerComprehensive",
    ),
    "TestFlextDbOracleModels": ("tests.unit.test_models", "TestFlextDbOracleModels"),
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
    "TestFlextDbOracleUtilities": (
        "tests.unit.test_utilities",
        "TestFlextDbOracleUtilities",
    ),
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
    "c": ("tests.unit.test_constants", "TestFlextDbOracleConstants"),
    "connected_oracle_api": ("tests.unit.conftest", "connected_oracle_api"),
    "docker_control": ("tests.unit.conftest", "docker_control"),
    "e": ("tests.unit.test_coverage_baseline", "TestExceptions"),
    "ensure_shared_docker_container": (
        "tests.unit.conftest",
        "ensure_shared_docker_container",
    ),
    "logger": ("tests.unit.conftest", "logger"),
    "m": ("tests.unit.test_models", "TestFlextDbOracleModels"),
    "mock_oracle_config": ("tests.unit.conftest", "mock_oracle_config"),
    "oracle_api": ("tests.unit.conftest", "oracle_api"),
    "oracle_available": ("tests.unit.conftest", "oracle_available"),
    "oracle_config": ("tests.unit.conftest", "oracle_config"),
    "oracle_container": ("tests.unit.conftest", "oracle_container"),
    "p": ("tests.unit.test_protocols", "TestFlextDbOracleProtocols"),
    "real_oracle_config": ("tests.unit.conftest", "real_oracle_config"),
    "safe_get_first_value": ("tests.unit.test_oracle_example", "safe_get_first_value"),
    "shared_oracle_container": ("tests.unit.conftest", "shared_oracle_container"),
    "t": ("tests.unit.test_services", "TestDirectCoverageBoostTypes"),
    "test_cleanup": ("tests.unit.conftest", "test_cleanup"),
    "u": ("tests.unit.test_coverage_baseline", "TestUtilities"),
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
    "docker_control",
    "e",
    "ensure_shared_docker_container",
    "logger",
    "m",
    "mock_oracle_config",
    "oracle_api",
    "oracle_available",
    "oracle_config",
    "oracle_container",
    "p",
    "real_oracle_config",
    "safe_get_first_value",
    "shared_oracle_container",
    "t",
    "test_cleanup",
    "u",
]


def __getattr__(name: str) -> FlextTypes.ModuleExport:
    """Lazy-load module attributes on first access (PEP 562)."""
    return lazy_getattr(name, _LAZY_IMPORTS, globals(), __name__)


def __dir__() -> list[str]:
    """Return list of available attributes for dir() and autocomplete."""
    return sorted(__all__)


cleanup_submodule_namespace(__name__, _LAZY_IMPORTS)
