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

import os
from typing import cast

from flext_core import FlextLogger
from pydantic import SecretStr

from flext_db_oracle import (
    FlextDbOracleApi,
    FlextDbOracleConfig,
    FlextDbOracleUtilities,
)

logger = FlextLogger(__name__)


def demo_basic_usage() -> None:
    """Demonstrate basic flext-db-oracle usage."""
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

    # Create configuration using from_env method
    try:
        config = FlextDbOracleConfig.from_env()
    except Exception:
        return

    # Create API instance
    try:
        api = FlextDbOracleApi(config)
    except Exception:
        return

    # Test connection
    try:
        connected_api_result = api.connect()
        if not connected_api_result.is_success:
            return
        connected_api = connected_api_result.value

        # Use real API methods for functionality test
        connection_test = connected_api.test_connection()
        if connection_test.success:
            # Quick functionality test using real API
            schemas_result = connected_api.get_schemas()
            if schemas_result.success:
                logger.info("Found %d schemas", len(schemas_result.value))
            else:
                logger.warning("Could not get schemas: %s", schemas_result.error)
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
        features: list[str] = cast("list[str]", example.get("features", []))
        if isinstance(features, list):
            for _feature in features:
                pass


if __name__ == "__main__":
    # Run basic demo when executed directly
    demo_basic_usage()
    show_available_examples()
