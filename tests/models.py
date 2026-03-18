"""Test models for flext-db-oracle tests.

Provides TestsFlextDbOracleModels, extending m with flext-db-oracle-specific
models using COMPOSITION INHERITANCE.

Inheritance hierarchy:
- m (flext_tests) - Provides .Tests.* namespace
- FlextDbOracleModels (production) - Provides Oracle domain models

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_db_oracle.models import FlextDbOracleModels


class TestsFlextDbOracleModels(FlextDbOracleModels):
    """Models for flext-db-oracle tests using COMPOSITION INHERITANCE.

    MANDATORY: Inherits from BOTH:
    1. m - for test infrastructure (.Tests.*)
    2. FlextDbOracleModels - for domain models (ConnectionStatus, QueryResult, etc.)

    Access patterns:
    - tm.Tests.* (generic test models from m)
    - tm.ConnectionStatus (Oracle connection status model)
    - tm.QueryResult (Oracle query result model)
    - tm.Table, tm.Column, tm.Schema (Oracle metadata models)
    - m.* (production models via alternative alias)

    Rules:
    - NEVER duplicate models from m or FlextDbOracleModels
    - Only flext-db-oracle-specific test fixtures allowed
    - All generic test models come from m
    - All production models come from FlextDbOracleModels
    """

    class Tests:
        """Project-specific test fixtures namespace.

        Provides test fixtures for flext-db-oracle testing.
        """

        class Oracle:
            """Oracle-specific test fixtures."""


# Short aliases per FLEXT convention
tm = TestsFlextDbOracleModels  # Primary test models alias

__all__ = [
    "TestsFlextDbOracleModels",
    "m",
    "tm",
]

m = TestsFlextDbOracleModels
