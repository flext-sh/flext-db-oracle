# AUTO-GENERATED FILE — DO NOT EDIT MANUALLY.
# Regenerate with: make gen
#
"""End-to-end tests for flext-db-oracle.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import TYPE_CHECKING

from flext_core.lazy import install_lazy_exports

if TYPE_CHECKING:
    from tests.e2e import test_oracle as test_oracle
    from tests.e2e.test_oracle import (
        OperationTestError as OperationTestError,
        TestOracleE2E as TestOracleE2E,
    )

_LAZY_IMPORTS: Mapping[str, Sequence[str]] = {
    "OperationTestError": ["tests.e2e.test_oracle", "OperationTestError"],
    "TestOracleE2E": ["tests.e2e.test_oracle", "TestOracleE2E"],
    "test_oracle": ["tests.e2e.test_oracle", ""],
}

_EXPORTS: Sequence[str] = [
    "OperationTestError",
    "TestOracleE2E",
    "test_oracle",
]


install_lazy_exports(__name__, globals(), _LAZY_IMPORTS, _EXPORTS)
