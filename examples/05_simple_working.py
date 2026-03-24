"""Simple working Oracle example demonstrating configuration setup.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

This example demonstrates basic configuration and setup functionality.
"""

from __future__ import annotations

from flext_core import FlextLogger

from flext_db_oracle import FlextDbOracleSettings

logger = FlextLogger(__name__)


def demonstrate_real_functionality() -> None:
    """Demonstrate configuration and basic setup functionality."""
    logger.info("=== FLEXT Oracle Example - Configuration Demo ===")
    try:
        config_result = FlextDbOracleSettings.from_env()
        if config_result.is_success:
            config = config_result.value
            logger.info(f"✅ Configuration created: {config.host}:{config.port}")
        else:
            config = FlextDbOracleSettings(
                host="demo-host",
                username="demo-user",
                password="demo-password",
            )
            logger.info("✅ Demo configuration created")
        logger.info(f"📋 Host: {config.host}")
        logger.info(f"📋 Port: {config.port}")
        logger.info(f"📋 Service: {config.service_name}")
        username_display = str(config.username)[:3]
        logger.info("📋 Username: %s***", username_display)
        if config.host and config.port > 0:
            logger.info("✅ Configuration is valid")
        else:
            logger.error("❌ Configuration is invalid")
    except Exception:
        logger.exception("❌ Unexpected error")


def main() -> None:
    """Main entry point."""
    demonstrate_real_functionality()


if __name__ == "__main__":
    main()
