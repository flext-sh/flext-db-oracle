# AUTO-GENERATED FILE — Regenerate with: make gen
"""E2e package."""

from __future__ import annotations

from typing import TYPE_CHECKING

from flext_core.lazy import build_lazy_import_map, install_lazy_exports

if TYPE_CHECKING:
    from flext_db_oracle.tests.e2e.test_oracle import (
        OperationTestErrorE2E as OperationTestErrorE2E,
        TestsFlextDbOracleEOracle as TestsFlextDbOracleEOracle,
    )
_LAZY_IMPORTS = build_lazy_import_map(
    {
        ".test_oracle": (
            "OperationTestErrorE2E",
            "TestsFlextDbOracleEOracle",
        ),
    },
)


install_lazy_exports(
    __name__,
    globals(),
    _LAZY_IMPORTS,
    publish_all=False,
)
