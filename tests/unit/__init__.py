# AUTO-GENERATED FILE — Regenerate with: make gen
"""Unit package."""

from __future__ import annotations

from flext_core.lazy import build_lazy_import_map, install_lazy_exports

_LAZY_IMPORTS = build_lazy_import_map(
    {
        ".conftest": ("conftest",),
        ".exceptions": ("FlextDbOracleTestExceptions",),
        ".test_api": ("TestsFlextDbOracleApi",),
        ".test_cli": ("TestsFlextDbOracleCli",),
        ".test_client": ("TestsFlextDbOracleClient",),
        ".test_config": ("TestsFlextDbOracleConfig",),
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
    },
)


install_lazy_exports(
    __name__,
    globals(),
    _LAZY_IMPORTS,
    publish_all=False,
)
