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
        test_database_setup,
    )
    from tests.constants import (
        FlextDbOracleTestConstants,
        FlextDbOracleTestConstants as c,
    )
    from tests.e2e import OperationTestError
    from tests.exceptions import (
        FlextDbOracleTestExceptions,
        FlextDbOracleTestExceptions as e,
    )
    from tests.integration import TestOracleIntegration
    from tests.models import (
        FlextDbOracleTestModels,
        FlextDbOracleTestModels as m,
    )
    from tests.protocols import (
        FlextDbOracleTestProtocols,
        FlextDbOracleTestProtocols as p,
    )
    from tests.typings import (
        FlextDbOracleTestTypes,
        FlextDbOracleTestTypes as t,
    )
    from tests.unit import (
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
        test_cleanup,
    )
    from tests.utilities import (
        FlextDbOracleTestUtilities,
        FlextDbOracleTestUtilities as u,
    )

_LAZY_IMPORTS: FlextTypes.LazyImportIndex = merge_lazy_imports(
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


install_lazy_exports(__name__, globals(), _LAZY_IMPORTS)
