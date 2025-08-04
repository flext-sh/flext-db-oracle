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


def demo_basic_usage() -> None:
    """Demonstrate basic flext-db-oracle usage."""
    # Import core components
    try:
        from flext_db_oracle import FlextDbOracleApi, FlextDbOracleConfig

    except ImportError:
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
        test_result = connected_api.test_connection()

        if test_result.success:

            # Quick functionality test
            schemas_result = connected_api.get_schemas()
            if schemas_result.success:
                len(schemas_result.data)

            connected_api.disconnect()

    except Exception as e:
        logging.exception("Demo usage failed: %s", e)


def show_available_examples() -> None:
    """Show information about available examples."""
    examples = [
        {
            "name": "04_comprehensive_oracle_usage.py",
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
        for _feature in example["features"]:
            pass


if __name__ == "__main__":
    # Run basic demo when executed directly
    demo_basic_usage()
    show_available_examples()
