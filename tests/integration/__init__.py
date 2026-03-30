# AUTO-GENERATED FILE — DO NOT EDIT MANUALLY.
# Regenerate with: make gen
#
"""Integration tests for flext-db-oracle.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import TYPE_CHECKING

from flext_core.lazy import install_lazy_exports

if TYPE_CHECKING:
    from tests.integration import test_oracle as test_oracle
    from tests.integration.test_oracle import (
        TestOracleIntegration as TestOracleIntegration,
        mock_oracle_config as mock_oracle_config,
    )

_LAZY_IMPORTS: Mapping[str, Sequence[str]] = {
    "TestOracleIntegration": ["tests.integration.test_oracle", "TestOracleIntegration"],
    "mock_oracle_config": ["tests.integration.test_oracle", "mock_oracle_config"],
    "test_oracle": ["tests.integration.test_oracle", ""],
}

_EXPORTS: Sequence[str] = [
    "TestOracleIntegration",
    "mock_oracle_config",
    "test_oracle",
]


install_lazy_exports(__name__, globals(), _LAZY_IMPORTS, _EXPORTS)
