#!/usr/bin/env python3
"""Simple working Oracle example demonstrating configuration setup.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

This example demonstrates basic configuration and setup functionality.
"""

from __future__ import annotations

from flext_core import FlextLogger

from flext_db_oracle import FlextDbOracleConfig

logger = FlextLogger(__name__)


def demonstrate_real_functionality() -> None:
    """Demonstrate configuration and basic setup functionality."""
    logger.info("=== FLEXT Oracle Example - Configuration Demo ===")

    try:
        # 1. Create configuration from environment (with defaults)
        config_result = FlextDbOracleConfig.from_env()
        if config_result.is_success:
            config = config_result.value
            logger.info(f"✅ Configuration created: {config.host}:{config.port}")
        else:
            # Create demo config if env config fails
            config = FlextDbOracleConfig(
                host="demo-host", username="demo-user", password="demo-password"
            )
            logger.info("✅ Demo configuration created")

        # 2. Show configuration values
        logger.info(f"📋 Host: {config.host}")
        logger.info(f"📋 Port: {config.port}")
        logger.info(f"📋 Service: {config.service_name}")
        username_display = (
            config.username.get_secret_value()[:3]
            if hasattr(config.username, "get_secret_value")
            else str(config.username)[:3]
        )
        logger.info(f"📋 Username: {username_display}***")

        # 3. Demonstrate config validation
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
