# AUTO-GENERATED FILE — Regenerate with: make gen
"""Unit package."""

from __future__ import annotations

from flext_core.lazy import build_lazy_import_map, install_lazy_exports

_LAZY_IMPORTS = build_lazy_import_map({
    ".conftest": ("conftest",),
    ".exceptions": ("FlextDbOracleTestExceptions",),
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
    ),
})


install_lazy_exports(__name__, globals(), _LAZY_IMPORTS, publish_all=False)
