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
    from flext_core.decorators import FlextDecorators as d
    from flext_core.handlers import FlextHandlers as h
    from flext_core.mixins import FlextMixins as x
    from flext_core.result import FlextResult as r
    from flext_core.service import FlextService as s
    from flext_db_oracle import (
        conftest,
        constants,
        e2e,
        exceptions,
        integration,
        models,
        protocols,
        test_api,
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
        test_oracle,
        test_oracle_example,
        test_oracle_exceptions,
        test_protocols,
        test_services,
        test_typings,
        test_utilities,
        typings,
        unit,
        utilities,
    )
    from flext_db_oracle.conftest import (
        cleanup_ddl,
        flext_domains,
        result,
        test_database_setup,
        test_schema,
    )
    from flext_db_oracle.constants import (
        FlextDbOracleTestConstants,
        FlextDbOracleTestConstants as c,
    )
    from flext_db_oracle.e2e import OperationTestError
    from flext_db_oracle.exceptions import (
        FlextDbOracleTestExceptions,
        FlextDbOracleTestExceptions as e,
    )
    from flext_db_oracle.integration import TestOracleIntegration
    from flext_db_oracle.models import (
        FlextDbOracleTestModels,
        FlextDbOracleTestModels as m,
    )
    from flext_db_oracle.protocols import (
        FlextDbOracleTestProtocols,
        FlextDbOracleTestProtocols as p,
    )
    from flext_db_oracle.typings import (
        FlextDbOracleTestTypes,
        FlextDbOracleTestTypes as t,
    )
    from flext_db_oracle.unit import (
        TestApiModule,
        TestApiSurgicalSimple,
        Testc,
        TestDirectCoverageBoostAPI,
        TestDispatcherSurgical,
        Teste,
        TestFlextDbOracleApiRealFunctionality,
        TestFlextDbOracleApiSafeMethods,
        TestFlextDbOracleApiWorking,
        TestFlextDbOracleClientReal,
        TestFlextDbOracleClientRealFunctionality,
        TestFlextDbOracleConnectionSimple,
        TestFlextDbOracleFields,
        TestFlextDbOracleMetadataManagerComprehensive,
        TestFlextDbOracleProtocols,
        TestFlextDbOracleServicesBasic,
        TestFlextDbOracleSettings,
        TestFlextDbOracleTypes,
        Testm,
        TestModuleImports,
        TestRealOracleExceptionsCore,
        Testu,
        cleanup_queries,
        connect_result,
        connected_api,
        connected_oracle_api,
        docker_control,
        ensure_shared_docker_container,
        logger,
        mock_oracle_config,
        oracle_api,
        oracle_available,
        oracle_config,
        oracle_container,
        plsql_query,
        real_oracle_config,
        safe_get_first_value,
        shared_oracle_container,
        test_cleanup,
    )
    from flext_db_oracle.utilities import (
        FlextDbOracleTestUtilities,
        FlextDbOracleTestUtilities as u,
    )

_LAZY_IMPORTS: FlextTypes.LazyImportIndex = merge_lazy_imports(
    (
        "flext_db_oracle.e2e",
        "flext_db_oracle.integration",
        "flext_db_oracle.unit",
    ),
    {
        "FlextDbOracleTestConstants": "flext_db_oracle.constants",
        "FlextDbOracleTestExceptions": "flext_db_oracle.exceptions",
        "FlextDbOracleTestModels": "flext_db_oracle.models",
        "FlextDbOracleTestProtocols": "flext_db_oracle.protocols",
        "FlextDbOracleTestTypes": "flext_db_oracle.typings",
        "FlextDbOracleTestUtilities": "flext_db_oracle.utilities",
        "c": ("flext_db_oracle.constants", "FlextDbOracleTestConstants"),
        "cleanup_ddl": "flext_db_oracle.conftest",
        "conftest": "flext_db_oracle.conftest",
        "constants": "flext_db_oracle.constants",
        "d": ("flext_core.decorators", "FlextDecorators"),
        "e": ("flext_db_oracle.exceptions", "FlextDbOracleTestExceptions"),
        "e2e": "flext_db_oracle.e2e",
        "exceptions": "flext_db_oracle.exceptions",
        "flext_domains": "flext_db_oracle.conftest",
        "h": ("flext_core.handlers", "FlextHandlers"),
        "integration": "flext_db_oracle.integration",
        "m": ("flext_db_oracle.models", "FlextDbOracleTestModels"),
        "models": "flext_db_oracle.models",
        "p": ("flext_db_oracle.protocols", "FlextDbOracleTestProtocols"),
        "protocols": "flext_db_oracle.protocols",
        "r": ("flext_core.result", "FlextResult"),
        "result": "flext_db_oracle.conftest",
        "s": ("flext_core.service", "FlextService"),
        "t": ("flext_db_oracle.typings", "FlextDbOracleTestTypes"),
        "test_api": "flext_db_oracle.test_api",
        "test_cli": "flext_db_oracle.test_cli",
        "test_client": "flext_db_oracle.test_client",
        "test_config": "flext_db_oracle.test_config",
        "test_constants": "flext_db_oracle.test_constants",
        "test_coverage_baseline": "flext_db_oracle.test_coverage_baseline",
        "test_database_setup": "flext_db_oracle.conftest",
        "test_dispatcher": "flext_db_oracle.test_dispatcher",
        "test_exceptions": "flext_db_oracle.test_exceptions",
        "test_fields": "flext_db_oracle.test_fields",
        "test_metadata": "flext_db_oracle.test_metadata",
        "test_models": "flext_db_oracle.test_models",
        "test_oracle": "flext_db_oracle.test_oracle",
        "test_oracle_example": "flext_db_oracle.test_oracle_example",
        "test_oracle_exceptions": "flext_db_oracle.test_oracle_exceptions",
        "test_protocols": "flext_db_oracle.test_protocols",
        "test_schema": "flext_db_oracle.conftest",
        "test_services": "flext_db_oracle.test_services",
        "test_typings": "flext_db_oracle.test_typings",
        "test_utilities": "flext_db_oracle.test_utilities",
        "typings": "flext_db_oracle.typings",
        "u": ("flext_db_oracle.utilities", "FlextDbOracleTestUtilities"),
        "unit": "flext_db_oracle.unit",
        "utilities": "flext_db_oracle.utilities",
        "x": ("flext_core.mixins", "FlextMixins"),
    },
)


install_lazy_exports(__name__, globals(), _LAZY_IMPORTS)
