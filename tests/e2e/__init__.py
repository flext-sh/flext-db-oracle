# AUTO-GENERATED FILE — DO NOT EDIT MANUALLY.
# Regenerate with: make codegen
#
"""End-to-end tests for flext-db-oracle.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from typing import TYPE_CHECKING

from flext_core.lazy import cleanup_submodule_namespace, lazy_getattr

if TYPE_CHECKING:
    from flext_core.typings import FlextTypes
    from tests.e2e.test_oracle import OperationTestError, TestOracleE2E

_LAZY_IMPORTS: dict[str, tuple[str, str]] = {
    "OperationTestError": ("tests.e2e.test_oracle", "OperationTestError"),
    "TestOracleE2E": ("tests.e2e.test_oracle", "TestOracleE2E"),
}

__all__ = [
    "OperationTestError",
    "TestOracleE2E",
]


def __getattr__(name: str) -> FlextTypes.ModuleExport:
    """Lazy-load module attributes on first access (PEP 562)."""
    return lazy_getattr(name, _LAZY_IMPORTS, globals(), __name__)


def __dir__() -> list[str]:
    """Return list of available attributes for dir() and autocomplete."""
    return sorted(__all__)


cleanup_submodule_namespace(__name__, _LAZY_IMPORTS)
