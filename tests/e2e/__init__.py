# AUTO-GENERATED FILE — Regenerate with: make gen
"""Flext Db Oracle package."""

from __future__ import annotations

import typing as _t

from flext_core.lazy import build_lazy_import_map, install_lazy_exports

if _t.TYPE_CHECKING:
    from flext_db_oracle.test_oracle import OperationTestError, TestOracleE2E
_LAZY_IMPORTS = build_lazy_import_map(
    {
        ".test_oracle": (
            "OperationTestError",
            "TestOracleE2E",
        ),
    },
)


install_lazy_exports(__name__, globals(), _LAZY_IMPORTS)

__all__ = [
    "OperationTestError",
    "TestOracleE2E",
]
