# AUTO-GENERATED FILE — Regenerate with: make gen
"""Tests.unit package.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from flext_core.lazy import install_lazy_exports

if TYPE_CHECKING:
    from tests.unit.test_statement_builders import TestsFlextDbOracleStatementBuilders


__all__: tuple[str, ...] = ("TestsFlextDbOracleStatementBuilders",)

install_lazy_exports(
    __name__,
    globals(),
    {"TestsFlextDbOracleStatementBuilders": ".test_statement_builders"},
    public_exports=__all__,
)
