"""Unit tests for flext_db_oracle.settings module.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from flext_tests import tm

from flext_db_oracle import FlextDbOracleSettings


class TestFlextDbOracleSettings:
    """Test FlextDbOracleSettings functionality."""

    def test_config_creation(self) -> None:
        """Test settings can be created."""
        settings = FlextDbOracleSettings()
        tm.that(settings, none=False)

    def test_config_attributes(self) -> None:
        """Test settings has required attributes."""
        FlextDbOracleSettings()
