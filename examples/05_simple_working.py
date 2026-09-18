"""Simple working Oracle example demonstrating configuration setup.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

This example demonstrates basic configuration and setup functionality.
"""

from __future__ import annotations

import os

from flext_db_oracle import FlextDbOracleSettings, u

logger = u.fetch_logger(__name__)


def _resolve_settings() -> FlextDbOracleSettings:
    """Resolve settings from the env-backed singleton or fallback demo config."""
    settings = FlextDbOracleSettings.fetch_global()
    if settings.DbOracle.password:
        logger.info(
            f"✅ Configuration created: {settings.DbOracle.host}:{settings.DbOracle.port}"
        )
    else:
        settings = FlextDbOracleSettings.model_validate({
            "DbOracle": {
                "host": "demo-host",
                "username": "demo-user",
                "password": os.environ.get("FLEXT_DEMO_ORACLE_PASSWORD", "<demo>"),
            }
        })
        logger.info("✅ Demo configuration created")
    return settings


def _display_configuration(settings: FlextDbOracleSettings) -> None:
    """Display configuration details and validity."""
    logger.info(f"📋 Host: {settings.DbOracle.host}")
    logger.info(f"📋 Port: {settings.DbOracle.port}")
    logger.info(f"📋 Service: {settings.DbOracle.service_name}")
    username_display = settings.DbOracle.username[:3]
    logger.info("📋 Username: %s***", username_display)
    if settings.DbOracle.host and settings.DbOracle.port > 0:
        logger.info("✅ Configuration is valid")
    else:
        logger.error("❌ Configuration is invalid")


def demonstrate_real_functionality() -> None:
    """Demonstrate configuration and basic setup functionality."""
    logger.info("=== FLEXT Oracle Example - Configuration Demo ===")
    # Why: no-hidden-errors — let a real failure escape with its traceback
    # instead of a broad except that only logs and hides the cause.
    settings = _resolve_settings()
    _display_configuration(settings)


def main() -> None:
    """Run the main entry point."""
    demonstrate_real_functionality()


if __name__ == "__main__":
    main()
