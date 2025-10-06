"""Unit tests for flext_db_oracle.config module.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_db_oracle import FlextDbOracleConfig


class TestFlextDbOracleConfig:
    """Test FlextDbOracleConfig functionality."""

    def test_config_creation(self) -> None:
        """Test config can be created."""
        config = FlextDbOracleConfig()
        assert config is not None

    def test_config_attributes(self) -> None:
        """Test config has required attributes."""
        config = FlextDbOracleConfig()
        assert hasattr(config, "oracle_host")
        assert hasattr(config, "oracle_port")
        assert hasattr(config, "oracle_service_name")
