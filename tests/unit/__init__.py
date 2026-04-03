# AUTO-GENERATED FILE — DO NOT EDIT MANUALLY.
# Regenerate with: make gen
#
"""Unit package."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import TYPE_CHECKING as _TYPE_CHECKING

from flext_core.lazy import install_lazy_exports

if _TYPE_CHECKING:
    from flext_core import FlextTypes
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
    from flext_db_oracle import (
        conftest,
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
        test_oracle_example,
        test_oracle_exceptions,
        test_protocols,
        test_services,
        test_typings,
        test_utilities,
    )
    from flext_db_oracle.conftest import (
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
        shared_oracle_container,
        test_cleanup,
    )
    from flext_db_oracle.test_api import (
        TestApiModule,
        TestApiSurgicalSimple,
        TestFlextDbOracleApiRealFunctionality,
        TestFlextDbOracleApiSafeMethods,
        TestFlextDbOracleApiWorking,
    )
    from flext_db_oracle.test_cli import TestFlextDbOracleClientReal
    from flext_db_oracle.test_client import TestFlextDbOracleClientRealFunctionality
    from flext_db_oracle.test_config import TestFlextDbOracleSettings
    from flext_db_oracle.test_constants import Testc
    from flext_db_oracle.test_coverage_baseline import TestModuleImports
    from flext_db_oracle.test_dispatcher import TestDispatcherSurgical
    from flext_db_oracle.test_exceptions import Teste
    from flext_db_oracle.test_fields import TestFlextDbOracleFields
    from flext_db_oracle.test_models import Testm
    from flext_db_oracle.test_oracle_example import safe_get_first_value
    from flext_db_oracle.test_oracle_exceptions import TestRealOracleExceptionsCore
    from flext_db_oracle.test_protocols import TestFlextDbOracleProtocols
    from flext_db_oracle.test_services import (
        TestDirectCoverageBoostAPI,
        TestFlextDbOracleConnectionSimple,
        TestFlextDbOracleMetadataManagerComprehensive,
        TestFlextDbOracleServicesBasic,
    )
    from flext_db_oracle.test_typings import TestFlextDbOracleTypes
    from flext_db_oracle.test_utilities import Testu

_LAZY_IMPORTS: FlextTypes.LazyImportIndex = {
    "TestApiModule": "flext_db_oracle.test_api",
    "TestApiSurgicalSimple": "flext_db_oracle.test_api",
    "TestDirectCoverageBoostAPI": "flext_db_oracle.test_services",
    "TestDispatcherSurgical": "flext_db_oracle.test_dispatcher",
    "TestFlextDbOracleApiRealFunctionality": "flext_db_oracle.test_api",
    "TestFlextDbOracleApiSafeMethods": "flext_db_oracle.test_api",
    "TestFlextDbOracleApiWorking": "flext_db_oracle.test_api",
    "TestFlextDbOracleClientReal": "flext_db_oracle.test_cli",
    "TestFlextDbOracleClientRealFunctionality": "flext_db_oracle.test_client",
    "TestFlextDbOracleConnectionSimple": "flext_db_oracle.test_services",
    "TestFlextDbOracleFields": "flext_db_oracle.test_fields",
    "TestFlextDbOracleMetadataManagerComprehensive": "flext_db_oracle.test_services",
    "TestFlextDbOracleProtocols": "flext_db_oracle.test_protocols",
    "TestFlextDbOracleServicesBasic": "flext_db_oracle.test_services",
    "TestFlextDbOracleSettings": "flext_db_oracle.test_config",
    "TestFlextDbOracleTypes": "flext_db_oracle.test_typings",
    "TestModuleImports": "flext_db_oracle.test_coverage_baseline",
    "TestRealOracleExceptionsCore": "flext_db_oracle.test_oracle_exceptions",
    "Testc": "flext_db_oracle.test_constants",
    "Teste": "flext_db_oracle.test_exceptions",
    "Testm": "flext_db_oracle.test_models",
    "Testu": "flext_db_oracle.test_utilities",
    "c": ("flext_core.constants", "FlextConstants"),
    "cleanup_queries": "flext_db_oracle.conftest",
    "conftest": "flext_db_oracle.conftest",
    "connect_result": "flext_db_oracle.conftest",
    "connected_api": "flext_db_oracle.conftest",
    "connected_oracle_api": "flext_db_oracle.conftest",
    "d": ("flext_core.decorators", "FlextDecorators"),
    "docker_control": "flext_db_oracle.conftest",
    "e": ("flext_core.exceptions", "FlextExceptions"),
    "ensure_shared_docker_container": "flext_db_oracle.conftest",
    "h": ("flext_core.handlers", "FlextHandlers"),
    "logger": "flext_db_oracle.conftest",
    "m": ("flext_core.models", "FlextModels"),
    "mock_oracle_config": "flext_db_oracle.conftest",
    "oracle_api": "flext_db_oracle.conftest",
    "oracle_available": "flext_db_oracle.conftest",
    "oracle_config": "flext_db_oracle.conftest",
    "oracle_container": "flext_db_oracle.conftest",
    "p": ("flext_core.protocols", "FlextProtocols"),
    "plsql_query": "flext_db_oracle.conftest",
    "r": ("flext_core.result", "FlextResult"),
    "real_oracle_config": "flext_db_oracle.conftest",
    "s": ("flext_core.service", "FlextService"),
    "safe_get_first_value": "flext_db_oracle.test_oracle_example",
    "shared_oracle_container": "flext_db_oracle.conftest",
    "t": ("flext_core.typings", "FlextTypes"),
    "test_api": "flext_db_oracle.test_api",
    "test_cleanup": "flext_db_oracle.conftest",
    "test_cli": "flext_db_oracle.test_cli",
    "test_client": "flext_db_oracle.test_client",
    "test_config": "flext_db_oracle.test_config",
    "test_constants": "flext_db_oracle.test_constants",
    "test_coverage_baseline": "flext_db_oracle.test_coverage_baseline",
    "test_dispatcher": "flext_db_oracle.test_dispatcher",
    "test_exceptions": "flext_db_oracle.test_exceptions",
    "test_fields": "flext_db_oracle.test_fields",
    "test_metadata": "flext_db_oracle.test_metadata",
    "test_models": "flext_db_oracle.test_models",
    "test_oracle_example": "flext_db_oracle.test_oracle_example",
    "test_oracle_exceptions": "flext_db_oracle.test_oracle_exceptions",
    "test_protocols": "flext_db_oracle.test_protocols",
    "test_services": "flext_db_oracle.test_services",
    "test_typings": "flext_db_oracle.test_typings",
    "test_utilities": "flext_db_oracle.test_utilities",
    "u": ("flext_core.utilities", "FlextUtilities"),
    "x": ("flext_core.mixins", "FlextMixins"),
}


install_lazy_exports(__name__, globals(), _LAZY_IMPORTS)
