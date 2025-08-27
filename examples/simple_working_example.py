#!/usr/bin/env python3
"""Simple working Oracle example using only real API methods.

This example demonstrates the actual functionality available in flext-db-oracle
without inventing non-existent methods.
"""

from __future__ import annotations

import logging

from flext_db_oracle import FlextDbOracleApi, FlextDbOracleConfig

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def demonstrate_real_functionality() -> None:
    """Demonstrate actual working functionality."""
    logger.info("=== FLEXT Oracle Example - Real Functionality ===")

    try:
        # 1. Create configuration from environment
        config = FlextDbOracleConfig.from_env()
        logger.info(f"✅ Configuration created: {config.host}:{config.port}")

        # 2. Create API instance
        api = FlextDbOracleApi(config)
        logger.info("✅ API instance created")

        # 3. Test connection
        connection_result = api.test_connection()
        if connection_result.success:
            logger.info("✅ Connection test successful")
        else:
            logger.error(f"❌ Connection test failed: {connection_result.error}")
            return

        # 4. Get schemas (if connected)
        with api as connected_api:
            schemas_result = connected_api.get_schemas()
            if schemas_result.success:
                logger.info(f"✅ Found {len(schemas_result.value)} schemas")
            else:
                logger.warning(f"⚠️  Could not get schemas: {schemas_result.error}")

            # 5. Execute simple query
            query_result = connected_api.query("SELECT SYSDATE FROM DUAL")
            if query_result.success:
                result_data = query_result.value
                logger.info(f"✅ Query successful: {len(result_data.rows)} rows")
                logger.info(f"   Columns: {result_data.columns}")
            else:
                logger.warning(f"⚠️  Query failed: {query_result.error}")

    except Exception:
        logger.exception("❌ Example failed")


if __name__ == "__main__":
    demonstrate_real_functionality()
