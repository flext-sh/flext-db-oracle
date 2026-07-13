"""Test exceptions for flext-db-oracle.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_db_oracle import FlextDbOracleExceptions


class FlextDbOracleTestExceptions(FlextDbOracleExceptions):
    """Test exceptions namespace for flext-db-oracle."""


e = FlextDbOracleTestExceptions

__all__: list[str] = ["FlextDbOracleTestExceptions", "e"]
