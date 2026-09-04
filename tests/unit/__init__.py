# AUTO-GENERATED FILE — Regenerate with: make gen
"""Tests.unit package."""

from __future__ import annotations

from typing import TYPE_CHECKING

from types import MappingProxyType

from flext_core.lazy import build_lazy_import_map, install_lazy_exports

if TYPE_CHECKING:
    from flext_tests import c, d, h, m, p, r, s, t, td, tf, tk, tm, tv, u, x

    from .exceptions import FlextDbOracleTestExceptions, e
    from .test_api import TestsFlextDbOracleApi
    from .test_cli import TestsFlextDbOracleCli
    from .test_client import TestsFlextDbOracleClient
    from .test_config import TestsFlextDbOracleSettings
    from .test_conftest_constants import TestsFlextDbOracleConftestConstants
    from .test_constants import TestsFlextDbOracleConstants
    from .test_coverage_baseline import TestsFlextDbOracleCoverageBaseline
    from .test_dispatcher import TestsFlextDbOracleDispatcher
    from .test_exceptions import TestsFlextDbOracleExceptions
    from .test_fields import TestsFlextDbOracleFields
    from .test_metadata import TestsFlextDbOracleMetadata
    from .test_models import TestsFlextDbOracleModels
    from .test_oracle_example import TestsFlextDbOracleOracleExample
    from .test_oracle_exceptions import TestsFlextDbOracleOracleExceptions
    from .test_protocols import TestsFlextDbOracleProtocols
    from .test_services import TestsFlextDbOracleServices
    from .test_typings import TestsFlextDbOracleTypings
    from .test_utilities import TestsFlextDbOracleUtilitiesUnit
__all__: tuple[str, ...] = (
    "FlextDbOracleTestExceptions",
    "TestsFlextDbOracleApi",
    "TestsFlextDbOracleCli",
    "TestsFlextDbOracleClient",
    "TestsFlextDbOracleConftestConstants",
    "TestsFlextDbOracleConstants",
    "TestsFlextDbOracleCoverageBaseline",
    "TestsFlextDbOracleDispatcher",
    "TestsFlextDbOracleExceptions",
    "TestsFlextDbOracleFields",
    "TestsFlextDbOracleMetadata",
    "TestsFlextDbOracleModels",
    "TestsFlextDbOracleOracleExample",
    "TestsFlextDbOracleOracleExceptions",
    "TestsFlextDbOracleProtocols",
    "TestsFlextDbOracleServices",
    "TestsFlextDbOracleSettings",
    "TestsFlextDbOracleTypings",
    "TestsFlextDbOracleUtilitiesUnit",
    "c",
    "d",
    "e",
    "h",
    "m",
    "p",
    "r",
    "s",
    "t",
    "td",
    "tf",
    "tk",
    "tm",
    "tv",
    "u",
    "x",
)

_LAZY_IMPORTS = MappingProxyType(
    build_lazy_import_map(
        MappingProxyType({
            ".exceptions": ("FlextDbOracleTestExceptions", "e"),
            ".test_api": ("TestsFlextDbOracleApi",),
            ".test_cli": ("TestsFlextDbOracleCli",),
            ".test_client": ("TestsFlextDbOracleClient",),
            ".test_config": ("TestsFlextDbOracleSettings",),
            ".test_conftest_constants": ("TestsFlextDbOracleConftestConstants",),
            ".test_constants": ("TestsFlextDbOracleConstants",),
            ".test_coverage_baseline": ("TestsFlextDbOracleCoverageBaseline",),
            ".test_dispatcher": ("TestsFlextDbOracleDispatcher",),
            ".test_exceptions": ("TestsFlextDbOracleExceptions",),
            ".test_fields": ("TestsFlextDbOracleFields",),
            ".test_metadata": ("TestsFlextDbOracleMetadata",),
            ".test_models": ("TestsFlextDbOracleModels",),
            ".test_oracle_example": ("TestsFlextDbOracleOracleExample",),
            ".test_oracle_exceptions": ("TestsFlextDbOracleOracleExceptions",),
            ".test_protocols": ("TestsFlextDbOracleProtocols",),
            ".test_services": ("TestsFlextDbOracleServices",),
            ".test_typings": ("TestsFlextDbOracleTypings",),
            ".test_utilities": ("TestsFlextDbOracleUtilitiesUnit",),
            "flext_tests": (
                "c",
                "d",
                "h",
                "m",
                "p",
                "r",
                "s",
                "t",
                "td",
                "tf",
                "tk",
                "tm",
                "tv",
                "u",
                "x",
            ),
        }),
        alias_groups=MappingProxyType({}),
        sort_keys=False,
    )
)

install_lazy_exports(__name__, globals(), _LAZY_IMPORTS, public_exports=__all__)
