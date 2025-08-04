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


def demo_basic_usage() -> None:
    """Demonstrate basic flext-db-oracle usage."""
    print("=== FLEXT DB ORACLE - BASIC USAGE EXAMPLE ===")

    # Import core components
    try:
        from flext_db_oracle import FlextDbOracleApi, FlextDbOracleConfig
        print("✅ Successfully imported flext-db-oracle components")
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return

    # Check environment configuration
    env_vars = [
        "FLEXT_TARGET_ORACLE_HOST",
        "FLEXT_TARGET_ORACLE_USERNAME",
        "FLEXT_TARGET_ORACLE_PASSWORD",
    ]

    configured = sum(1 for var in env_vars if os.getenv(var))
    print(f"📋 Environment configuration: {configured}/{len(env_vars)} variables set")

    if configured < len(env_vars):
        print("⚠️  Set Oracle environment variables to test connection:")
        for var in env_vars:
            print(f"   export {var}=<value>")
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
        print("✅ Oracle configuration created successfully")
    except Exception as e:
        print(f"❌ Configuration failed: {e}")
        return

    # Create API instance
    try:
        api = FlextDbOracleApi(config)
        print("✅ FlextDbOracleApi instance created")
    except Exception as e:
        print(f"❌ API creation failed: {e}")
        return

    # Test connection
    try:
        connected_api = api.connect()
        test_result = connected_api.test_connection()

        if test_result.is_success:
            print("✅ Oracle connection test successful")

            # Quick functionality test
            schemas_result = connected_api.get_schemas()
            if schemas_result.is_success:
                schema_count = len(schemas_result.data)
                print(f"📊 Found {schema_count} Oracle schemas")

            connected_api.disconnect()
            print("✅ Disconnected successfully")

        else:
            print(f"❌ Connection test failed: {test_result.error}")

    except Exception as e:
        print(f"❌ Connection error: {e}")

    print("🎯 Basic usage example completed")


def show_available_examples() -> None:
    """Show information about available examples."""
    examples = [
        {
            "name": "04_comprehensive_oracle_usage.py",
            "description": "Complete Oracle operations demonstration",
            "features": ["Connection management", "Schema operations", "Query execution", "Metadata introspection"],
        },
        {
            "name": "cli_examples.py",
            "description": "CLI command demonstrations",
            "features": ["Command-line interface", "Interactive examples", "Output formatting"],
        },
        {
            "name": "sqlalchemy2_example.py",
            "description": "SQLAlchemy 2 integration patterns",
            "features": ["Direct SQL execution", "Transaction management", "Metadata operations"],
        },
        {
            "name": "__init__.py (this file)",
            "description": "Basic usage and imports",
            "features": ["Simple connection test", "Environment check", "Quick start guide"],
        },
    ]

    print("=== AVAILABLE FLEXT DB ORACLE EXAMPLES ===")

    for example in examples:
        print(f"\n📁 {example['name']}")
        print(f"   {example['description']}")
        print("   Features:")
        for feature in example['features']:
            print(f"   • {feature}")

    print("\n🚀 Run any example:")
    print("   python examples/04_comprehensive_oracle_usage.py")
    print("   python examples/cli_examples.py demo")
    print("   python examples/sqlalchemy2_example.py")
    print("   python -c \"from examples import demo_basic_usage; demo_basic_usage()\"")


if __name__ == "__main__":
    # Run basic demo when executed directly
    demo_basic_usage()
    print("\n" + "="*60)
    show_available_examples()
