"""Simple working Oracle example demonstrating configuration setup.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

This example demonstrates basic configuration and setup functionality.
"""

from __future__ import annotations

from flext_db_oracle.settings import FlextDbOracleSettings
from flext_db_oracle.utilities import u

logger = u.fetch_logger(__name__)


def _resolve_settings() -> FlextDbOracleSettings:
    """Resolve settings from env result or fallback demo config."""
    config_result = FlextDbOracleSettings.from_env()
    settings: FlextDbOracleSettings
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
    return settings


def _display_configuration(settings: FlextDbOracleSettings) -> None:
    """Display configuration details and validity."""
    logger.info(f"📋 Host: {settings.host}")
    logger.info(f"📋 Port: {settings.port}")
    logger.info(f"📋 Service: {settings.service_name}")
    username_display = settings.username[:3]
    logger.info("📋 Username: %s***", username_display)
    if settings.host and settings.port > 0:
        logger.info("✅ Configuration is valid")
    else:
        logger.error("❌ Configuration is invalid")


def demonstrate_real_functionality() -> None:
    """Demonstrate configuration and basic setup functionality."""
    logger.info("=== FLEXT Oracle Example - Configuration Demo ===")
    try:
        settings = _resolve_settings()
        _display_configuration(settings)
    except (ValueError, OSError, RuntimeError):
        logger.exception("❌ Unexpected error")


def main() -> None:
    """Main entry point."""
    demonstrate_real_functionality()


if __name__ == "__main__":
    main()
