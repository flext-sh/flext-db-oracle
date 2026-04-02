# AUTO-GENERATED FILE — DO NOT EDIT MANUALLY.
# Regenerate with: make gen
#
"""Tests package."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import TYPE_CHECKING as _TYPE_CHECKING

from flext_core.lazy import install_lazy_exports, merge_lazy_imports

if _TYPE_CHECKING:
    from flext_core import FlextTypes
    from flext_tests import d, h, r, s, x

    from tests import (
        conftest,
        constants,
        e2e,
        exceptions,
        integration,
        models,
        protocols,
        typings,
        unit,
        utilities,
    )
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
    from tests.e2e import OperationTestError, TestOracleE2E, test_oracle
    from tests.exceptions import (
        FlextDbOracleTestExceptions,
        FlextDbOracleTestExceptions as e,
    )
    from tests.integration import TestOracleIntegration
    from tests.models import FlextDbOracleTestModels, FlextDbOracleTestModels as m
    from tests.protocols import (
        FlextDbOracleTestProtocols,
        FlextDbOracleTestProtocols as p,
    )
    from tests.typings import FlextDbOracleTestTypes, FlextDbOracleTestTypes as t
    from tests.unit import (
        TestApiModule,
        TestApiSurgicalSimple,
        TestBasicModelCreation,
        Testc,
        TestCLIRealFunctionality,
        TestCliServiceOperations,
        TestConstants,
        TestDirectCoverageBoostAPI,
        TestDirectCoverageBoostConfig,
        TestDirectCoverageBoostConnection,
        TestDirectCoverageBoostObservability,
        TestDirectCoverageBoostServices,
        TestDirectCoverageBoostTypes,
        TestDispatcherSurgical,
        Teste,
        TestExceptions,
        TestFlextDbOracleApiRealFunctionality,
        TestFlextDbOracleApiSafeMethods,
        TestFlextDbOracleApiWorking,
        TestFlextDbOracleCli,
        TestFlextDbOracleClientIntegration,
        TestFlextDbOracleClientReal,
        TestFlextDbOracleClientRealFunctionality,
        TestFlextDbOracleConnectionSimple,
        TestFlextDbOracleFields,
        TestFlextDbOracleMetadataManagerComprehensive,
        TestFlextDbOracleProtocols,
        TestFlextDbOracleServices,
        TestFlextDbOracleServicesBasic,
        TestFlextDbOracleServicesPlaceholderRemovals,
        TestFlextDbOracleSettings,
        TestFlextDbOracleTypes,
        Testm,
        TestModuleImports,
        TestOracleConnectionHelper,
        TestOutputFormatter,
        TestRealOracleApi,
        TestRealOracleConnection,
        TestRealOracleErrorHandling,
        TestRealOracleExceptionHierarchy,
        TestRealOracleExceptionsAdvanced,
        TestRealOracleExceptionsCore,
        TestServiceErrorHandling,
        Testu,
        TestUtilities,
        TestYamlModule,
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
        safe_get_first_value,
        shared_oracle_container,
        test_api,
        test_cleanup,
        test_cli,
        test_client,
        test_config,
        test_constants,
        test_coverage_baseline,
        test_dispatcher,
        test_exceptions,
        test_fields,
        test_metadata,
        test_models,
        test_oracle_example,
        test_oracle_exceptions,
        test_protocols,
        test_services,
        test_typings,
        test_utilities,
    )
    from tests.utilities import (
        FlextDbOracleTestUtilities,
        FlextDbOracleTestUtilities as u,
    )

_LAZY_IMPORTS: Mapping[str, str | Sequence[str]] = merge_lazy_imports(
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
        "d": "flext_tests",
        "e": ("tests.exceptions", "FlextDbOracleTestExceptions"),
        "e2e": "tests.e2e",
        "exceptions": "tests.exceptions",
        "flext_domains": "tests.conftest",
        "h": "flext_tests",
        "integration": "tests.integration",
        "m": ("tests.models", "FlextDbOracleTestModels"),
        "models": "tests.models",
        "p": ("tests.protocols", "FlextDbOracleTestProtocols"),
        "protocols": "tests.protocols",
        "pytest_configure": "tests.conftest",
        "pytest_runtest_makereport": "tests.conftest",
        "pytest_sessionstart": "tests.conftest",
        "r": "flext_tests",
        "s": "flext_tests",
        "t": ("tests.typings", "FlextDbOracleTestTypes"),
        "test_database_setup": "tests.conftest",
        "typings": "tests.typings",
        "u": ("tests.utilities", "FlextDbOracleTestUtilities"),
        "unit": "tests.unit",
        "utilities": "tests.utilities",
        "x": "flext_tests",
    },
)


install_lazy_exports(__name__, globals(), _LAZY_IMPORTS)
