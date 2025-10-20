#!/usr/bin/env python3
"""Simple working Oracle example using only real API methods.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

This example demonstrates the actual functionality available in flext-db-oracle
without inventing non-existent methods.
"""

from __future__ import annotations

from flext_core import FlextLogger
from flext_db_oracle import FlextDbOracleApi, FlextDbOracleConfig

logger = FlextLogger(__name__)


def demonstrate_real_functionality() -> None:
    """Demonstrate actual working functionality."""
    logger.info("=== FLEXT Oracle Example - Real Functionality ===")

    try:
        # 1. Create configuration from environment
        config_result = FlextDbOracleConfig.from_env()
        if not config_result.is_success:
            logger.error(f"❌ Configuration failed: {config_result.error}")
            return
        config = config_result.value
        logger.info(f"✅ Configuration created: {config.host}:{config.port}")

        # 2. Create API instance
        api = FlextDbOracleApi(config)
        logger.info("✅ API instance created")

        # 3. Test connection
        connection_result = api.test_connection()
        if connection_result.is_success:
            logger.info("✅ Connection test successful")
        else:
            logger.error(f"❌ Connection test failed: {connection_result.error}")
            return

        # 4. Get schemas (if connected)
        with api as connected_api:
            schemas_result = connected_api.get_schemas()
            if schemas_result.is_success:
                logger.info(f"✅ Found {len(schemas_result.value)} schemas")
            else:
                logger.warning(f"⚠️  Could not get schemas: {schemas_result.error}")

            # 5. Execute simple query
            query_result = connected_api.query("SELECT SYSDATE FROM DUAL")
            if query_result.is_success:
                result_data = query_result.value
                logger.info(f"✅ Query successful: {len(result_data)} rows")
                if result_data:
                    logger.info(f"   First row: {result_data[0]}")
            else:
                logger.warning(f"⚠️  Query failed: {query_result.error}")

    except Exception:
        logger.exception("❌ Example failed")


if __name__ == "__main__":
    demonstrate_real_functionality()
