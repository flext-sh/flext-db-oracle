# AUTO-GENERATED FILE — Regenerate with: make gen
"""Tests package."""

from __future__ import annotations

from typing import TYPE_CHECKING

from flext_core.lazy import (
    build_lazy_import_map,
    install_lazy_exports,
    merge_lazy_imports,
)

if TYPE_CHECKING:
    from flext_tests import (
        d as d,
        e as e,
        h as h,
        r as r,
        td as td,
        tf as tf,
        tk as tk,
        tm as tm,
        tv as tv,
        x as x,
    )

    from tests.base import (
        TestsFlextDbOracleServiceBase as TestsFlextDbOracleServiceBase,
        s as s,
    )
    from tests.constants import (
        TestsFlextDbOracleConstants as TestsFlextDbOracleConstants,
        c as c,
    )
    from tests.e2e.test_oracle import (
        TestsFlextDbOracleOracle as TestsFlextDbOracleOracle,
    )
    from tests.models import (
        TestsFlextDbOracleModels as TestsFlextDbOracleModels,
        m as m,
    )
    from tests.protocols import (
        TestsFlextDbOracleProtocols as TestsFlextDbOracleProtocols,
        p as p,
    )
    from tests.settings import TestsFlextDbOracleSettings as TestsFlextDbOracleSettings
    from tests.typings import TestsFlextDbOracleTypes as TestsFlextDbOracleTypes, t as t
    from tests.unit.exceptions import (
        FlextDbOracleTestExceptions as FlextDbOracleTestExceptions,
    )
    from tests.unit.test_api import TestsFlextDbOracleApi as TestsFlextDbOracleApi
    from tests.unit.test_cli import TestsFlextDbOracleCli as TestsFlextDbOracleCli
    from tests.unit.test_client import (
        TestsFlextDbOracleClient as TestsFlextDbOracleClient,
    )
    from tests.unit.test_conftest_constants import (
        TestsFlextDbOracleConftestConstants as TestsFlextDbOracleConftestConstants,
    )
    from tests.unit.test_coverage_baseline import (
        TestsFlextDbOracleCoverageBaseline as TestsFlextDbOracleCoverageBaseline,
    )
    from tests.unit.test_dispatcher import (
        TestsFlextDbOracleDispatcher as TestsFlextDbOracleDispatcher,
    )
    from tests.unit.test_exceptions import (
        TestsFlextDbOracleExceptions as TestsFlextDbOracleExceptions,
    )
    from tests.unit.test_fields import (
        TestsFlextDbOracleFields as TestsFlextDbOracleFields,
    )
    from tests.unit.test_metadata import (
        TestsFlextDbOracleMetadata as TestsFlextDbOracleMetadata,
    )
    from tests.unit.test_oracle_example import (
        TestsFlextDbOracleOracleExample as TestsFlextDbOracleOracleExample,
    )
    from tests.unit.test_oracle_exceptions import (
        TestsFlextDbOracleOracleExceptions as TestsFlextDbOracleOracleExceptions,
    )
    from tests.unit.test_services import (
        TestsFlextDbOracleServices as TestsFlextDbOracleServices,
    )
    from tests.unit.test_typings import (
        TestsFlextDbOracleTypings as TestsFlextDbOracleTypings,
    )
    from tests.unit.test_utilities import (
        TestsFlextDbOracleUtilitiesUnit as TestsFlextDbOracleUtilitiesUnit,
    )
    from tests.utilities import (
        TestsFlextDbOracleUtilities as TestsFlextDbOracleUtilities,
        u as u,
    )
_LAZY_IMPORTS = merge_lazy_imports(
    (
        ".e2e",
        ".integration",
        ".unit",
    ),
    build_lazy_import_map(
        {
            ".base": (
                "TestsFlextDbOracleServiceBase",
                "s",
            ),
            ".conftest": ("conftest",),
            ".constants": (
                "TestsFlextDbOracleConstants",
                "c",
            ),
            ".e2e": ("e2e",),
            ".e2e.test_oracle": ("TestsFlextDbOracleOracle",),
            ".integration": ("integration",),
            ".models": (
                "TestsFlextDbOracleModels",
                "m",
            ),
            ".protocols": (
                "TestsFlextDbOracleProtocols",
                "p",
            ),
            ".settings": ("TestsFlextDbOracleSettings",),
            ".typings": (
                "TestsFlextDbOracleTypes",
                "t",
            ),
            ".unit": ("unit",),
            ".unit.exceptions": ("FlextDbOracleTestExceptions",),
            ".unit.test_api": ("TestsFlextDbOracleApi",),
            ".unit.test_cli": ("TestsFlextDbOracleCli",),
            ".unit.test_client": ("TestsFlextDbOracleClient",),
            ".unit.test_conftest_constants": ("TestsFlextDbOracleConftestConstants",),
            ".unit.test_coverage_baseline": ("TestsFlextDbOracleCoverageBaseline",),
            ".unit.test_dispatcher": ("TestsFlextDbOracleDispatcher",),
            ".unit.test_exceptions": ("TestsFlextDbOracleExceptions",),
            ".unit.test_fields": ("TestsFlextDbOracleFields",),
            ".unit.test_metadata": ("TestsFlextDbOracleMetadata",),
            ".unit.test_oracle_example": ("TestsFlextDbOracleOracleExample",),
            ".unit.test_oracle_exceptions": ("TestsFlextDbOracleOracleExceptions",),
            ".unit.test_services": ("TestsFlextDbOracleServices",),
            ".unit.test_typings": ("TestsFlextDbOracleTypings",),
            ".unit.test_utilities": ("TestsFlextDbOracleUtilitiesUnit",),
            ".utilities": (
                "TestsFlextDbOracleUtilities",
                "u",
            ),
            "flext_tests": (
                "d",
                "e",
                "h",
                "r",
                "td",
                "tf",
                "tk",
                "tm",
                "tv",
                "x",
            ),
        },
    ),
    exclude_names=(
        "cleanup_submodule_namespace",
        "install_lazy_exports",
        "lazy_getattr",
        "logger",
        "merge_lazy_imports",
        "output",
        "output_reporting",
        "pytest_addoption",
        "pytest_collect_file",
        "pytest_collection_modifyitems",
        "pytest_configure",
        "pytest_runtest_setup",
        "pytest_runtest_teardown",
        "pytest_sessionfinish",
        "pytest_sessionstart",
        "pytest_terminal_summary",
        "pytest_warning_recorded",
    ),
    module_name=__name__,
)


install_lazy_exports(
    __name__,
    globals(),
    _LAZY_IMPORTS,
    publish_all=False,
)
