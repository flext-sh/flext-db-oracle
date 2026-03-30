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
    from tests.integration import test_oracle
    from tests.integration.test_oracle import *

_LAZY_IMPORTS: Mapping[str, str | Sequence[str]] = {
    "TestOracleIntegration": "tests.integration.test_oracle",
    "mock_oracle_config": "tests.integration.test_oracle",
    "test_oracle": "tests.integration.test_oracle",
}


install_lazy_exports(__name__, globals(), _LAZY_IMPORTS, sorted(_LAZY_IMPORTS))
