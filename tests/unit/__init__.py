# AUTO-GENERATED FILE — DO NOT EDIT MANUALLY.
# Regenerate with: make gen
#
"""init   module.

This module is part of the FLEXT ecosystem. Docstrings follow PEP 257 and Google style.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import TYPE_CHECKING as _TYPE_CHECKING

from flext_core.lazy import install_lazy_exports

if _TYPE_CHECKING:
    from flext_core import FlextTypes

    from tests.unit.conftest import *
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

_LAZY_IMPORTS: Mapping[str, str | Sequence[str]] = {
    "HealthCheckReport": "tests.unit.test_cli",
    "NamedItem": "tests.unit.test_cli",
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
    "conftest": "tests.unit.conftest",
    "connected_oracle_api": "tests.unit.conftest",
    "docker_control": "tests.unit.conftest",
    "ensure_shared_docker_container": "tests.unit.conftest",
    "logger": "tests.unit.conftest",
    "mock_oracle_config": "tests.unit.conftest",
    "oracle_api": "tests.unit.conftest",
    "oracle_available": "tests.unit.conftest",
    "oracle_config": "tests.unit.conftest",
    "oracle_container": "tests.unit.conftest",
    "real_oracle_config": "tests.unit.conftest",
    "safe_get_first_value": "tests.unit.test_oracle_example",
    "shared_oracle_container": "tests.unit.conftest",
    "test_api": "tests.unit.test_api",
    "test_cleanup": "tests.unit.conftest",
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
}


install_lazy_exports(__name__, globals(), _LAZY_IMPORTS)
