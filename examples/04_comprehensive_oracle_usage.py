"""Comprehensive FLEXT Oracle Database Usage Example.

Demonstrates advanced Oracle database operations using flext-db-oracle
with real-world patterns including connection management, transactions,
metadata exploration, and error handling.

Copyright (c) 2025 FLEXT Contributors
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import asyncio
import os

from flext_core import get_logger

from flext_db_oracle import (
    FlextDbOracleApi,
    FlextDbOracleConfig,
)

# Setup logging
logger = get_logger(__name__)


def create_sample_config() -> FlextDbOracleConfig:
    """Create sample Oracle configuration for examples."""
    return FlextDbOracleConfig(
        host=os.getenv("ORACLE_HOST", "localhost"),
        port=int(os.getenv("ORACLE_PORT", "1521")),
        username=os.getenv("ORACLE_USERNAME", "system"),
        password=os.getenv("ORACLE_PASSWORD", "oracle"),
        service_name=os.getenv("ORACLE_SERVICE_NAME", "ORCLPDB1"),
        encoding="UTF-8",
    )


def demonstrate_connection_patterns() -> None:
    """Demonstrate different connection management patterns."""
    logger.info("🔗 Demonstrating Connection Patterns")

    # Pattern 1: Direct configuration
    config = create_sample_config()
    api = FlextDbOracleApi(config, "demo_connection")
    logger.info("✅ Created API with direct configuration")

    # Pattern 2: From environment variables
    try:
        FlextDbOracleApi.from_env()
        logger.info("✅ Created API from environment variables")
    except Exception as e:
        logger.warning(f"⚠️ Environment API creation failed: {e}")

    # Pattern 3: With configuration parameters
    FlextDbOracleApi.with_config(
        host="example.oracle.com",
        port=1521,
        username="demo_user",
        password="demo_pass",
        service_name="DEMO_DB",
    )
    logger.info("✅ Created API with configuration parameters")

    # Pattern 4: Context manager usage (auto-connect/disconnect)
    logger.info("🔄 Testing context manager pattern")
    try:
        with api as connected_api:
            logger.info("✅ Connected via context manager")
            # Connection operations would go here
            logger.info(f"Connection status: {connected_api.is_connected}")
    except Exception as e:
        logger.warning(f"⚠️ Context manager connection failed: {e}")


def demonstrate_configuration_patterns() -> None:
    """Demonstrate advanced configuration patterns."""
    logger.info("⚙️ Demonstrating Configuration Patterns")

    # Pattern 1: Minimal configuration
    FlextDbOracleConfig(
        host="localhost",
        username="user",
        password="pass",
        service_name="DB",
    )
    logger.info("✅ Created minimal configuration")

    # Pattern 2: Production configuration with all options
    production_config = FlextDbOracleConfig(
        host="prod.oracle.company.com",
        port=1521,
        username="prod_user",
        password="secure_password",
        service_name="PROD_DB",
        encoding="UTF-8",
        schema="PROD_SCHEMA",
    )
    logger.info("✅ Created production configuration")

    # Pattern 3: Configuration validation
    try:
        # Test configuration validation
        production_config.model_validate(
            {
                "host": "test.oracle.com",
                "port": 1521,
                "username": "test",
                "password": "test",
                "service_name": "TEST",
            },
        )
        logger.info("✅ Configuration validation passed")
    except Exception as e:
        logger.warning(f"⚠️ Configuration validation failed: {e}")


def demonstrate_query_patterns() -> None:
    """Demonstrate different query execution patterns."""
    logger.info("📊 Demonstrating Query Patterns")

    config = create_sample_config()
    api = FlextDbOracleApi(config, "demo_queries")

    # Simulate query operations (without actual Oracle connection)

    # Pattern 1: Simple query
    query_result = api.query("SELECT 1 as test_value FROM DUAL")
    if query_result.is_failure:
        logger.info(
            f"📝 Simple query pattern demonstrated (simulated): {query_result.error}",
        )

    # Pattern 2: Parameterized query
    param_query_result = api.query(
        "SELECT * FROM employees WHERE department_id = :dept_id",
        {"dept_id": 10},
    )
    if param_query_result.is_failure:
        logger.info(
            f"📝 Parameterized query pattern demonstrated (simulated): {param_query_result.error}",
        )

    # Pattern 3: Single row query
    single_result = api.query_one("SELECT COUNT(*) as total FROM employees")
    if single_result.is_failure:
        logger.info(
            f"📝 Single row query pattern demonstrated (simulated): {single_result.error}",
        )

    # Pattern 4: Batch operations
    operations = [
        (
            "UPDATE employees SET salary = salary * 1.1 WHERE department_id = :dept_id",
            {"dept_id": 10},
        ),
        (
            "INSERT INTO audit_log (operation, timestamp) VALUES (:op, SYSDATE)",
            {"op": "salary_update"},
        ),
        ("COMMIT", None),
    ]

    batch_result = api.execute_batch(operations)
    if batch_result.is_failure:
        logger.info(
            f"📝 Batch operations pattern demonstrated (simulated): {batch_result.error}",
        )


def demonstrate_metadata_exploration() -> None:
    """Demonstrate metadata exploration capabilities."""
    logger.info("🔍 Demonstrating Metadata Exploration")

    config = create_sample_config()
    api = FlextDbOracleApi(config, "demo_metadata")

    # Pattern 1: List all schemas
    schemas_result = api.get_schemas()
    if schemas_result.is_failure:
        logger.info(
            f"📝 Schema listing pattern demonstrated (simulated): {schemas_result.error}",
        )

    # Pattern 2: List tables in a schema
    tables_result = api.get_tables("HR")
    if tables_result.is_failure:
        logger.info(
            f"📝 Table listing pattern demonstrated (simulated): {tables_result.error}",
        )

    # Pattern 3: Get column information for a table
    columns_result = api.get_columns("EMPLOYEES")
    if columns_result.is_failure:
        logger.info(
            f"📝 Column information pattern demonstrated (simulated): {columns_result.error}",
        )

    # Pattern 4: Test connection health
    health_result = api.test_connection()
    if health_result.is_failure:
        logger.info(
            f"📝 Connection health check pattern demonstrated (simulated): {health_result.error}",
        )


def demonstrate_transaction_patterns() -> None:
    """Demonstrate transaction management patterns."""
    logger.info("💳 Demonstrating Transaction Patterns")

    config = create_sample_config()
    FlextDbOracleApi(config, "demo_transactions")

    # Pattern 1: Manual transaction management
    try:
        # Simulated transaction pattern
        logger.info("📝 Manual transaction pattern:")
        logger.info("  1. BEGIN TRANSACTION")
        logger.info("  2. Execute business operations")
        logger.info("  3. COMMIT or ROLLBACK based on results")

        # This would be real code with actual connection:
        # with api.transaction() as txn:
        #     if result1.is_success and result2.is_success:
        #         txn.commit()
        #         txn.rollback()

    except Exception as e:
        logger.warning(f"⚠️ Transaction pattern failed: {e}")


def demonstrate_error_handling_patterns() -> None:
    """Demonstrate comprehensive error handling patterns."""
    logger.info("❌ Demonstrating Error Handling Patterns")

    config = create_sample_config()
    api = FlextDbOracleApi(config, "demo_errors")

    # Pattern 1: Connection error handling
    try:
        # This will fail since we don't have real Oracle connection
        api.connect()
    except ValueError as e:
        logger.info(f"✅ Connection error handled: {e}")
    except Exception as e:
        logger.info(f"✅ General connection error handled: {e}")

    # Pattern 2: Query error handling with FlextResult
    result = api.query("INVALID SQL SYNTAX")
    if result.is_failure:
        logger.info(f"✅ Query error handled via FlextResult: {result.error}")

    # Pattern 3: Graceful degradation
    fallback_result = demonstrate_fallback_operations(api)
    logger.info(f"✅ Fallback operations result: {fallback_result}")


def demonstrate_fallback_operations(api: FlextDbOracleApi) -> str:
    """Demonstrate fallback operations when primary operations fail."""
    # Try primary operation
    primary_result = api.test_connection()
    if primary_result.is_success:
        return "Primary operation succeeded"

    # Primary failed, try fallback
    logger.info("Primary operation failed, trying fallback...")

    # Fallback: return cached/default data
    return "Using fallback data due to connection failure"


def demonstrate_performance_patterns() -> None:
    """Demonstrate performance optimization patterns."""
    logger.info("⚡ Demonstrating Performance Patterns")

    config = create_sample_config()
    FlextDbOracleApi(config, "demo_performance")

    # Pattern 1: Connection pooling (simulated)
    logger.info("📝 Connection pooling pattern:")
    logger.info("  - Use connection pool for multiple operations")
    logger.info("  - Reuse connections across requests")
    logger.info("  - Configure pool size based on workload")

    # Pattern 2: Batch operations for efficiency
    logger.info("📝 Batch operations pattern:")
    logger.info("  - Group multiple operations together")
    logger.info("  - Reduce round trips to database")
    logger.info("  - Use prepared statements for repeated queries")

    # Pattern 3: Async operations (when available)
    logger.info("📝 Async operations pattern:")
    logger.info("  - Use async/await for I/O operations")
    logger.info("  - Non-blocking database operations")
    logger.info("  - Better resource utilization")


def demonstrate_monitoring_patterns() -> None:
    """Demonstrate monitoring and observability patterns."""
    logger.info("📊 Demonstrating Monitoring Patterns")

    config = create_sample_config()
    FlextDbOracleApi(config, "demo_monitoring")

    # Pattern 1: Health checks
    logger.info("📝 Health check pattern:")
    logger.info("  - Regular connection health verification")
    logger.info("  - Database responsiveness monitoring")
    logger.info("  - Automatic alerting on failures")

    # Pattern 2: Performance metrics
    logger.info("📝 Performance metrics pattern:")
    logger.info("  - Query execution time tracking")
    logger.info("  - Connection pool utilization")
    logger.info("  - Error rate monitoring")

    # Pattern 3: Structured logging
    logger.info("📝 Structured logging pattern:")
    logger.info("  - Consistent log format across operations")
    logger.info("  - Correlation IDs for request tracing")
    logger.info("  - Log levels for different environments")


def demonstrate_integration_patterns() -> None:
    """Demonstrate integration with FLEXT ecosystem."""
    logger.info("🔗 Demonstrating Integration Patterns")

    # Pattern 1: FlextResult usage
    logger.info("📝 FlextResult integration:")
    logger.info("  - Railway-oriented programming")
    logger.info("  - Chain operations safely")
    logger.info("  - Handle errors functionally")

    # Pattern 2: Container registration
    logger.info("📝 Container integration:")
    logger.info("  - Register Oracle services in DI container")
    logger.info("  - Share connections across components")
    logger.info("  - Lifecycle management")

    # Pattern 3: Plugin system
    logger.info("📝 Plugin system integration:")
    logger.info("  - Extend Oracle functionality via plugins")
    logger.info("  - Custom query transformations")
    logger.info("  - Performance monitoring plugins")


async def demonstrate_async_patterns() -> None:
    """Demonstrate async/await patterns where applicable."""
    logger.info("⚡ Demonstrating Async Patterns")

    # Simulate async operations
    logger.info("📝 Async operation patterns:")

    # Pattern 1: Async connection management
    await asyncio.sleep(0.1)  # Simulate async work
    logger.info("  ✅ Async connection established")

    # Pattern 2: Async query execution
    await asyncio.sleep(0.1)  # Simulate async work
    logger.info("  ✅ Async query executed")

    # Pattern 3: Async batch operations
    await asyncio.sleep(0.1)  # Simulate async work
    logger.info("  ✅ Async batch operations completed")


def main() -> None:
    """Main function demonstrating all Oracle usage patterns."""
    logger.info("🚀 Starting Comprehensive Oracle Database Usage Examples")

    try:
        # Core patterns
        logger.info("\n📋 1. Connection Management Patterns")
        demonstrate_connection_patterns()

        logger.info("\n⚙️ 2. Configuration Patterns")
        demonstrate_configuration_patterns()

        logger.info("\n📊 3. Query Execution Patterns")
        demonstrate_query_patterns()

        logger.info("\n🔍 4. Metadata Exploration")
        demonstrate_metadata_exploration()

        logger.info("\n💳 5. Transaction Management")
        demonstrate_transaction_patterns()

        logger.info("\n❌ 6. Error Handling Patterns")
        demonstrate_error_handling_patterns()

        logger.info("\n⚡ 7. Performance Optimization")
        demonstrate_performance_patterns()

        logger.info("\n📊 8. Monitoring and Observability")
        demonstrate_monitoring_patterns()

        logger.info("\n🔗 9. FLEXT Ecosystem Integration")
        demonstrate_integration_patterns()

        # Async patterns
        logger.info("\n⚡ 10. Async/Await Patterns")
        asyncio.run(demonstrate_async_patterns())

        logger.info("\n🎉 All Oracle usage patterns demonstrated successfully!")

        # Summary
        logger.info("\n📚 Key Takeaways:")
        logger.info("  • Use FlextDbOracleApi for high-level operations")
        logger.info("  • Always handle errors with FlextResult pattern")
        logger.info("  • Use context managers for automatic resource cleanup")
        logger.info("  • Implement proper connection pooling for performance")
        logger.info("  • Leverage metadata exploration for schema discovery")
        logger.info("  • Use batch operations for efficiency")
        logger.info("  • Implement comprehensive monitoring and logging")
        logger.info("  • Integrate with FLEXT ecosystem patterns")

    except Exception as e:
        logger.exception(f"❌ Example execution failed: {e}")
        raise


if __name__ == "__main__":
    main()
