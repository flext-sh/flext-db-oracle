"""Examples for flext-db-oracle.

This package contains example code demonstrating how to use the flext-db-oracle library
for Oracle database operations using SQLAlchemy 2 and oracledb driver.

Available Examples:
    - 04_comprehensive_oracle_usage.py: Complete Oracle operations demo
    - cli_examples.py: CLI command demonstrations
    - sqlalchemy2_example.py: SQLAlchemy 2 integration patterns
    - __init__.py: This file with example imports and basic usage

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import logging
import os

# Prefer module-specific logger over root logger
logger = logging.getLogger(__name__)

# Import core components at module level to satisfy linting
try:
    from flext_db_oracle import FlextDbOracleApi, FlextDbOracleConfig
from flext_db_oracle.utilities import FlextDbOracleUtilities
except Exception:  # pragma: no cover - optional import for examples
    FlextDbOracleApi = None
    FlextDbOracleConfig = None


def demo_basic_usage() -> None:
    """Demonstrate basic flext-db-oracle usage."""
    # Bail out if optional imports are unavailable
    if FlextDbOracleApi is None or FlextDbOracleConfig is None:
        return

    # Check environment configuration
    env_vars = [
        "FLEXT_TARGET_ORACLE_HOST",
        "FLEXT_TARGET_ORACLE_USERNAME",
        "FLEXT_TARGET_ORACLE_PASSWORD",
    ]

    configured = sum(1 for var in env_vars if os.getenv(var))

    if configured < len(env_vars):
        for _var in env_vars:
            pass
        return

    # Create configuration
    try:
        config = FlextDbOracleConfig(
            host=os.getenv("FLEXT_TARGET_ORACLE_HOST", "localhost"),
            port=int(os.getenv("FLEXT_TARGET_ORACLE_PORT", "1521")),
            username=os.getenv("FLEXT_TARGET_ORACLE_USERNAME", "user"),
            password=os.getenv("FLEXT_TARGET_ORACLE_PASSWORD", "password"),
            service_name=os.getenv("FLEXT_TARGET_ORACLE_SERVICE_NAME", "ORCLPDB1"),
        )
    except Exception:
        return

    # Create API instance
    try:
        api = FlextDbOracleApi(config)
    except Exception:
        return

    # Test connection
    try:
        connected_api = api.connect()
        
        # Use utilities for cleaner railway-oriented code
        if FlextDbOracleUtilities.safe_test_connection(connected_api):
            # Quick functionality test using utilities
            schemas = FlextDbOracleUtilities.safe_get_schemas(connected_api)
            logger.info("Found %d schemas", len(schemas))
            connected_api.disconnect()

    except Exception:
        logger.exception("Demo usage failed")


def show_available_examples() -> None:
    """Show information about available examples."""
    examples: list[dict[str, object]] = [
        {
            "name": "example_04_comprehensive_oracle_usage.py",
            "description": "Complete Oracle operations demonstration",
            "features": [
                "Connection management",
                "Schema operations",
                "Query execution",
                "Metadata introspection",
            ],
        },
        {
            "name": "cli_examples.py",
            "description": "CLI command demonstrations",
            "features": [
                "Command-line interface",
                "Interactive examples",
                "Output formatting",
            ],
        },
        {
            "name": "sqlalchemy2_example.py",
            "description": "SQLAlchemy 2 integration patterns",
            "features": [
                "Direct SQL execution",
                "Transaction management",
                "Metadata operations",
            ],
        },
        {
            "name": "__init__.py (this file)",
            "description": "Basic usage and imports",
            "features": [
                "Simple connection test",
                "Environment check",
                "Quick start guide",
            ],
        },
    ]

    for example in examples:
        features = example.get("features", [])
        if isinstance(features, list):
            for _feature in features:
                pass


if __name__ == "__main__":
    # Run basic demo when executed directly
    demo_basic_usage()
    show_available_examples()
