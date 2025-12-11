"""Unit tests for flext_db_oracle.config module.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from flext_db_oracle import FlextDbOracleSettings


class TestFlextDbOracleSettings:
    """Test FlextDbOracleSettings functionality."""

    def test_config_creation(self) -> None:
        """Test config can be created."""
        config = FlextDbOracleSettings()
        assert config is not None

    def test_config_attributes(self) -> None:
        """Test config has required attributes."""
        config = FlextDbOracleSettings()
        assert hasattr(config, "host")
        assert hasattr(config, "port")
        assert hasattr(config, "service_name")
