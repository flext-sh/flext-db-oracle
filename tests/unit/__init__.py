# AUTO-GENERATED FILE — Regenerate with: make gen
"""Unit package."""

from __future__ import annotations

from typing import TYPE_CHECKING

from flext_core.lazy import build_lazy_import_map, install_lazy_exports

if TYPE_CHECKING:
    from flext_db_oracle.tests.unit.exceptions import (
        FlextDbOracleTestExceptions as FlextDbOracleTestExceptions,
        e as e,
    )
    from flext_db_oracle.tests.unit.test_api import (
        TestsFlextDbOracleApi as TestsFlextDbOracleApi,
    )
    from flext_db_oracle.tests.unit.test_cli import (
        TestsFlextDbOracleCli as TestsFlextDbOracleCli,
    )
    from flext_db_oracle.tests.unit.test_client import (
        TestsFlextDbOracleClient as TestsFlextDbOracleClient,
    )
    from flext_db_oracle.tests.unit.test_config import (
        TestsFlextDbOracleConfig as TestsFlextDbOracleConfig,
    )
    from flext_db_oracle.tests.unit.test_conftest_constants import (
        TestsFlextDbOracleConftestConstants as TestsFlextDbOracleConftestConstants,
    )
    from flext_db_oracle.tests.unit.test_constants import (
        TestsFlextDbOracleConstantsUnit as TestsFlextDbOracleConstantsUnit,
    )
    from flext_db_oracle.tests.unit.test_coverage_baseline import (
        TestsFlextDbOracleCoverageBaseline as TestsFlextDbOracleCoverageBaseline,
    )
    from flext_db_oracle.tests.unit.test_dispatcher import (
        TestsFlextDbOracleDispatcher as TestsFlextDbOracleDispatcher,
    )
    from flext_db_oracle.tests.unit.test_exceptions import (
        TestsFlextDbOracleExceptions as TestsFlextDbOracleExceptions,
    )
    from flext_db_oracle.tests.unit.test_fields import (
        TestsFlextDbOracleFields as TestsFlextDbOracleFields,
    )
    from flext_db_oracle.tests.unit.test_metadata import (
        TestsFlextDbOracleMetadata as TestsFlextDbOracleMetadata,
    )
    from flext_db_oracle.tests.unit.test_models import (
        TestsFlextDbOracleModelsUnit as TestsFlextDbOracleModelsUnit,
    )
    from flext_db_oracle.tests.unit.test_oracle_example import (
        TestsFlextDbOracleOracleExample as TestsFlextDbOracleOracleExample,
    )
    from flext_db_oracle.tests.unit.test_oracle_exceptions import (
        TestsFlextDbOracleOracleExceptions as TestsFlextDbOracleOracleExceptions,
    )
    from flext_db_oracle.tests.unit.test_protocols import (
        TestsFlextDbOracleProtocolsUnit as TestsFlextDbOracleProtocolsUnit,
    )
    from flext_db_oracle.tests.unit.test_services import (
        TestsFlextDbOracleServices as TestsFlextDbOracleServices,
    )
    from flext_db_oracle.tests.unit.test_typings import (
        TestsFlextDbOracleTypingsUnit as TestsFlextDbOracleTypingsUnit,
    )
    from flext_db_oracle.tests.unit.test_utilities import (
        TestsFlextDbOracleUtilitiesUnit as TestsFlextDbOracleUtilitiesUnit,
    )
_LAZY_IMPORTS = build_lazy_import_map(
    {
        ".conftest": ("conftest",),
        ".exceptions": (
            "FlextDbOracleTestExceptions",
            "e",
        ),
        ".test_api": ("TestsFlextDbOracleApi",),
        ".test_cli": ("TestsFlextDbOracleCli",),
        ".test_client": ("TestsFlextDbOracleClient",),
        ".test_config": ("TestsFlextDbOracleConfig",),
        ".test_conftest_constants": ("TestsFlextDbOracleConftestConstants",),
        ".test_constants": ("TestsFlextDbOracleConstantsUnit",),
        ".test_coverage_baseline": ("TestsFlextDbOracleCoverageBaseline",),
        ".test_dispatcher": ("TestsFlextDbOracleDispatcher",),
        ".test_exceptions": ("TestsFlextDbOracleExceptions",),
        ".test_fields": ("TestsFlextDbOracleFields",),
        ".test_metadata": ("TestsFlextDbOracleMetadata",),
        ".test_models": ("TestsFlextDbOracleModelsUnit",),
        ".test_oracle_example": ("TestsFlextDbOracleOracleExample",),
        ".test_oracle_exceptions": ("TestsFlextDbOracleOracleExceptions",),
        ".test_protocols": ("TestsFlextDbOracleProtocolsUnit",),
        ".test_services": ("TestsFlextDbOracleServices",),
        ".test_typings": ("TestsFlextDbOracleTypingsUnit",),
        ".test_utilities": ("TestsFlextDbOracleUtilitiesUnit",),
    },
)


install_lazy_exports(
    __name__,
    globals(),
    _LAZY_IMPORTS,
    publish_all=False,
)
