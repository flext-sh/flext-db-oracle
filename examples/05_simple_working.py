"""Simple working Oracle example demonstrating configuration setup.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

This example demonstrates basic configuration and setup functionality.
"""

from __future__ import annotations

from flext_db_oracle import FlextDbOracleSettings, u

logger = u.fetch_logger(__name__)


def demonstrate_real_functionality() -> None:
    """Demonstrate configuration and basic setup functionality."""
    logger.info("=== FLEXT Oracle Example - Configuration Demo ===")
    try:
        config_result = FlextDbOracleSettings.from_env()
        if config_result.success:
            settings = config_result.value
            logger.info(f"✅ Configuration created: {settings.host}:{settings.port}")
        else:
            settings = FlextDbOracleSettings.model_validate(
                {
                    "host": "demo-host",
                    "username": "demo-user",
                    "password": "demo-password",
                },
            )
            logger.info("✅ Demo configuration created")
        logger.info(f"📋 Host: {settings.host}")
        logger.info(f"📋 Port: {settings.port}")
        logger.info(f"📋 Service: {settings.service_name}")
        username_display = settings.username[:3]
        logger.info("📋 Username: %s***", username_display)
        if settings.host and settings.port > 0:
            logger.info("✅ Configuration is valid")
        else:
            logger.error("❌ Configuration is invalid")
    except (ValueError, OSError, RuntimeError):
        logger.exception("❌ Unexpected error")


def main() -> None:
    """Main entry point."""
    demonstrate_real_functionality()


if __name__ == "__main__":
    main()
