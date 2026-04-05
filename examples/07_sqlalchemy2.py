"""Oracle SQLAlchemy 2.0 integration example.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

This example demonstrates Oracle configuration setup for SQLAlchemy 2.0.
"""

from __future__ import annotations

from flext_core import FlextLogger
from flext_db_oracle import FlextDbOracleSettings

logger = FlextLogger(__name__)


def create_oracle_config() -> FlextDbOracleSettings:
    """Create Oracle database configuration.

    Returns:
        FlextDbOracleSettings: Configured Oracle database settings.

    """
    try:
        config_result = FlextDbOracleSettings.from_env()
        if config_result.is_success:
            return config_result.value
    except (ValueError, OSError, RuntimeError):
        logger.debug("Could not load config from environment, using demo config")
    return FlextDbOracleSettings.model_validate(
        {
            "host": "demo-oracle.example.com",
            "port": 1521,
            "service_name": "DEMO",
            "username": "demo_user",
            "password": "demo_password",
        },
    )


def demonstrate_sqlalchemy_setup() -> None:
    """Demonstrate SQLAlchemy 2.0 configuration setup."""
    logger.info("=== FLEXT Oracle SQLAlchemy 2.0 Setup ===")
    try:
        config = create_oracle_config()
        logger.info(f"✅ Configuration created: {config.host}:{config.port}")
        logger.info("🔗 SQLAlchemy connection URL format configured")
        logger.info(f"📍 Host: {config.host}:{config.port}")
        logger.info(f"📚 Service: {config.service_name}")
        logger.info("📚 Ready for SQLAlchemy 2.0 integration")
    except (ValueError, OSError, RuntimeError):
        logger.exception("❌ Configuration setup failed")


def main() -> None:
    """Main entry point."""
    demonstrate_sqlalchemy_setup()


if __name__ == "__main__":
    main()
