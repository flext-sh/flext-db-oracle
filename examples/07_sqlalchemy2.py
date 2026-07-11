"""Oracle SQLAlchemy 2.0 integration example.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

This example demonstrates Oracle configuration setup for SQLAlchemy 2.0.
"""

from __future__ import annotations

from flext_db_oracle import FlextDbOracleSettings, u

logger = u.fetch_logger(__name__)


def create_oracle_config() -> FlextDbOracleSettings:
    """Create Oracle database configuration.

    Returns:
        FlextDbOracleSettings: Configured Oracle database settings.

    """
    try:
        config_result = FlextDbOracleSettings.from_env()
        if config_result.success:
            settings_value: FlextDbOracleSettings = config_result.value
            return settings_value
    except (ValueError, OSError, RuntimeError):
        logger.debug("Could not load settings from environment, using demo settings")
    return FlextDbOracleSettings.model_validate(
        {
            "host": "demo-oracle.example.com",
            "port": 1521,
            "service_name": "DEMO",
            "username": "demo_user",
            "password": "demo_password",
        },
    )


def _display_sqlalchemy_setup(settings: FlextDbOracleSettings) -> None:
    """Display SQLAlchemy 2.0 configuration details."""
    logger.info(f"✅ Configuration created: {settings.host}:{settings.port}")
    logger.info("🔗 SQLAlchemy connection URL format configured")
    logger.info(f"📍 Host: {settings.host}:{settings.port}")
    logger.info(f"📚 Service: {settings.service_name}")
    logger.info("📚 Ready for SQLAlchemy 2.0 integration")


def demonstrate_sqlalchemy_setup() -> None:
    """Demonstrate SQLAlchemy 2.0 configuration setup."""
    logger.info("=== FLEXT Oracle SQLAlchemy 2.0 Setup ===")
    try:
        settings = create_oracle_config()
        _display_sqlalchemy_setup(settings)
    except (ValueError, OSError, RuntimeError):
        logger.exception("❌ Configuration setup failed")


def main() -> None:
    """Main entry point."""
    demonstrate_sqlalchemy_setup()


if __name__ == "__main__":
    main()
