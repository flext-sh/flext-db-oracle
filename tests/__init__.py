"""FLEXT DB Oracle Tests - Test infrastructure and utilities.

Provides TestsFlextDbOracle classes extending FlextTests and FlextDbOracle for comprehensive testing.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from flext_core._utilities.lazy import cleanup_submodule_namespace, lazy_getattr

if TYPE_CHECKING:
    from tests.constants import (
        TestsFlextDbOracleConstants,
        TestsFlextDbOracleConstants as c,
    )
    from tests.models import TestsFlextDbOracleModels, TestsFlextDbOracleModels as m, tm

# Lazy import mapping: export_name -> (module_path, attr_name)
_LAZY_IMPORTS: dict[str, tuple[str, str]] = {
    "TestsFlextDbOracleConstants": ("tests.constants", "TestsFlextDbOracleConstants"),
    "TestsFlextDbOracleModels": ("tests.models", "TestsFlextDbOracleModels"),
    "c": ("tests.constants", "TestsFlextDbOracleConstants"),
    "m": ("tests.models", "TestsFlextDbOracleModels"),
    "tm": ("tests.models", "tm"),
}

__all__ = [
    "TestsFlextDbOracleConstants",
    "TestsFlextDbOracleModels",
    "c",
    "m",
    "tm",
]


def __getattr__(name: str) -> Any:  # noqa: ANN401
    """Lazy-load module attributes on first access (PEP 562)."""
    return lazy_getattr(name, _LAZY_IMPORTS, globals(), __name__)


def __dir__() -> list[str]:
    """Return list of available attributes for dir() and autocomplete."""
    return sorted(__all__)


cleanup_submodule_namespace(__name__, _LAZY_IMPORTS)
