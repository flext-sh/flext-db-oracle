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
    from tests.unit import (
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
    from tests.unit.test_cli import TestFlextDbOracleClientReal
    from tests.unit.test_client import TestFlextDbOracleClientRealFunctionality
    from tests.unit.test_config import TestFlextDbOracleSettings
    from tests.unit.test_constants import Testc
    from tests.unit.test_coverage_baseline import TestModuleImports
    from tests.unit.test_dispatcher import TestDispatcherSurgical
    from tests.unit.test_exceptions import Teste
    from tests.unit.test_fields import TestFlextDbOracleFields
    from tests.unit.test_models import Testm
    from tests.unit.test_oracle_example import safe_get_first_value
    from tests.unit.test_oracle_exceptions import TestRealOracleExceptionsCore
    from tests.unit.test_protocols import TestFlextDbOracleProtocols
    from tests.unit.test_services import (
        TestDirectCoverageBoostAPI,
        TestFlextDbOracleConnectionSimple,
        TestFlextDbOracleMetadataManagerComprehensive,
        TestFlextDbOracleServicesBasic,
    )
    from tests.unit.test_typings import TestFlextDbOracleTypes
    from tests.unit.test_utilities import Testu

_LAZY_IMPORTS: FlextTypes.LazyImportIndex = {
    "TestApiModule": "tests.unit.test_api",
    "TestApiSurgicalSimple": "tests.unit.test_api",
    "TestDirectCoverageBoostAPI": "tests.unit.test_services",
    "TestDispatcherSurgical": "tests.unit.test_dispatcher",
    "TestFlextDbOracleApiRealFunctionality": "tests.unit.test_api",
    "TestFlextDbOracleApiSafeMethods": "tests.unit.test_api",
    "TestFlextDbOracleApiWorking": "tests.unit.test_api",
    "TestFlextDbOracleClientReal": "tests.unit.test_cli",
    "TestFlextDbOracleClientRealFunctionality": "tests.unit.test_client",
    "TestFlextDbOracleConnectionSimple": "tests.unit.test_services",
    "TestFlextDbOracleFields": "tests.unit.test_fields",
    "TestFlextDbOracleMetadataManagerComprehensive": "tests.unit.test_services",
    "TestFlextDbOracleProtocols": "tests.unit.test_protocols",
    "TestFlextDbOracleServicesBasic": "tests.unit.test_services",
    "TestFlextDbOracleSettings": "tests.unit.test_config",
    "TestFlextDbOracleTypes": "tests.unit.test_typings",
    "TestModuleImports": "tests.unit.test_coverage_baseline",
    "TestRealOracleExceptionsCore": "tests.unit.test_oracle_exceptions",
    "Testc": "tests.unit.test_constants",
    "Teste": "tests.unit.test_exceptions",
    "Testm": "tests.unit.test_models",
    "Testu": "tests.unit.test_utilities",
    "c": ("flext_core.constants", "FlextConstants"),
    "conftest": "tests.unit.conftest",
    "connected_oracle_api": "tests.unit.conftest",
    "d": ("flext_core.decorators", "FlextDecorators"),
    "docker_control": "tests.unit.conftest",
    "e": ("flext_core.exceptions", "FlextExceptions"),
    "ensure_shared_docker_container": "tests.unit.conftest",
    "h": ("flext_core.handlers", "FlextHandlers"),
    "logger": "tests.unit.conftest",
    "m": ("flext_core.models", "FlextModels"),
    "mock_oracle_config": "tests.unit.conftest",
    "oracle_api": "tests.unit.conftest",
    "oracle_available": "tests.unit.conftest",
    "oracle_config": "tests.unit.conftest",
    "oracle_container": "tests.unit.conftest",
    "p": ("flext_core.protocols", "FlextProtocols"),
    "r": ("flext_core.result", "FlextResult"),
    "real_oracle_config": "tests.unit.conftest",
    "s": ("flext_core.service", "FlextService"),
    "safe_get_first_value": "tests.unit.test_oracle_example",
    "shared_oracle_container": "tests.unit.conftest",
    "t": ("flext_core.typings", "FlextTypes"),
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
    "u": ("flext_core.utilities", "FlextUtilities"),
    "x": ("flext_core.mixins", "FlextMixins"),
}


install_lazy_exports(__name__, globals(), _LAZY_IMPORTS)
