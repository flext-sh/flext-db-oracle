# AUTO-GENERATED FILE — Regenerate with: make gen
"""Flext Db Oracle package."""

from __future__ import annotations

import typing as _t

from flext_core.lazy import build_lazy_import_map, install_lazy_exports

if _t.TYPE_CHECKING:
    from flext_db_oracle.test_oracle import TestOracleIntegration, mock_oracle_config
_LAZY_IMPORTS = build_lazy_import_map(
    {
        ".test_oracle": (
            "TestOracleIntegration",
            "mock_oracle_config",
        ),
    },
)


install_lazy_exports(__name__, globals(), _LAZY_IMPORTS)

__all__ = [
    "TestOracleIntegration",
    "mock_oracle_config",
]
