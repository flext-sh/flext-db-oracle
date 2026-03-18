"""Module skeleton for TestsFlextDbOracleTypes.

Test type aliases for flextdboracle.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_core import t as _core_t


class TestsFlextDbOracleTypes:
    """Test type aliases for flextdboracle."""

    # Re-export core types used in tests
    Dict = _core_t.Dict
    ConfigMap = _core_t.ConfigMap


t = TestsFlextDbOracleTypes
__all__ = ["TestsFlextDbOracleTypes", "t"]
