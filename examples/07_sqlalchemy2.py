"""Oracle SQLAlchemy 2.0 integration example.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

This example demonstrates Oracle configuration setup for SQLAlchemy 2.0.
"""

from __future__ import annotations

import os

from flext_db_oracle import FlextDbOracleSettings, u

logger = u.fetch_logger(__name__)


def create_oracle_config() -> FlextDbOracleSettings:
    """Create Oracle database configuration.

    Returns:
        FlextDbOracleSettings: Configured Oracle database settings.

    """
    # Why: no-hidden-errors — check the resolved value instead of masking a
    # real failure behind a broad except.
    settings_value = FlextDbOracleSettings.fetch_global()
    if settings_value.DbOracle.password:
        return settings_value
    logger.debug("No password in environment settings, using demo settings")
    return FlextDbOracleSettings.model_validate({
        "DbOracle": {
            "host": "demo-oracle.example.com",
            "port": 1521,
            "service_name": "DEMO",
            "username": "demo_user",
            "password": os.environ.get("FLEXT_DEMO_ORACLE_PASSWORD", "<demo>"),
        }
    })


def _display_sqlalchemy_setup(settings: FlextDbOracleSettings) -> None:
    """Display SQLAlchemy 2.0 configuration details."""
    logger.info(
        f"✅ Configuration created: {settings.DbOracle.host}:{settings.DbOracle.port}"
    )
    logger.info("🔗 SQLAlchemy connection URL format configured")
    logger.info(f"📍 Host: {settings.DbOracle.host}:{settings.DbOracle.port}")
    logger.info(f"📚 Service: {settings.DbOracle.service_name}")
    logger.info("📚 Ready for SQLAlchemy 2.0 integration")


def demonstrate_sqlalchemy_setup() -> None:
    """Demonstrate SQLAlchemy 2.0 configuration setup."""
    logger.info("=== FLEXT Oracle SQLAlchemy 2.0 Setup ===")
    # Why: no-hidden-errors — let a real failure escape with its traceback
    # instead of a broad except that only logs and hides the cause.
    settings = create_oracle_config()
    _display_sqlalchemy_setup(settings)


def main() -> None:
    """Run the main entry point."""
    demonstrate_sqlalchemy_setup()


if __name__ == "__main__":
    main()
