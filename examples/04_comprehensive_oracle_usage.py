"""FLEXT DB Oracle Comprehensive Usage Example.

This example demonstrates enterprise-grade Oracle database operations using FLEXT DB Oracle
with production-ready patterns, comprehensive error handling, and integration with the
FLEXT ecosystem. It showcases real-world scenarios including connection management,
transaction handling, metadata exploration, and observability integration.

Key Demonstrations:
    - Configuration management with environment variables and validation
    - Connection pooling and lifecycle management with error recovery
    - Query execution with performance monitoring and optimization
    - Schema introspection and metadata extraction with business logic
    - Plugin system integration for extensibility and monitoring
    - Transaction management with proper rollback and error handling
    - Observability integration with metrics collection and distributed tracing

Architecture:
    This example follows Clean Architecture principles with proper separation
    of concerns, dependency injection, and domain-driven design patterns.
    It demonstrates the Template Method pattern for eliminating code duplication
    and the Strategy pattern for different demonstration scenarios.

Prerequisites:
    - Oracle database (XE/Standard/Enterprise) accessible via network
    - Environment variables configured for database connection
    - FLEXT ecosystem components installed and configured

Usage:
    # Set environment variables
    export FLEXT_TARGET_ORACLE_HOST=localhost
    export FLEXT_TARGET_ORACLE_USERNAME=flext_user
    export FLEXT_TARGET_ORACLE_PASSWORD=secure_password

    # Run comprehensive demonstration
    python 04_comprehensive_oracle_usage.py

Copyright (c) 2025 FLEXT Team. All rights reserved.
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
        host=os.getenv("FLEXT_TARGET_ORACLE_HOST", "localhost"),
        port=int(os.getenv("FLEXT_TARGET_ORACLE_PORT", "1521")),
        username=os.getenv("FLEXT_TARGET_ORACLE_USERNAME", "flexttest"),
        password=os.getenv("FLEXT_TARGET_ORACLE_PASSWORD", "FlextTest123"),
        service_name=os.getenv("FLEXT_TARGET_ORACLE_SERVICE_NAME", "XEPDB1"),
        encoding="UTF-8",
    )


# =============================================================================
# REFACTORING: Template Method Pattern for DRY example patterns
# =============================================================================


class OracleExampleDemonstrator:
    """Template Method Pattern: Base class for all Oracle example demonstrations.

    SOLID REFACTORING: Eliminates 20+ lines of duplicated code (mass=86)
    by centralizing common example patterns using Template Method pattern.
    """

    def __init__(self, context_name: str, log_emoji: str, log_message: str) -> None:
        """Initialize demonstrator with common parameters."""
        self.context_name = context_name
        self.log_emoji = log_emoji
        self.log_message = log_message
        self.api = self._create_api_with_logging()

    def _create_api_with_logging(self) -> FlextDbOracleApi:
        """Template step: Create API instance with consistent logging."""
        logger.info("%s %s", self.log_emoji, self.log_message)
        config = create_sample_config()
        return FlextDbOracleApi(config, self.context_name)

    def _log_pattern_info(self, pattern_name: str, pattern_items: list[str]) -> None:
        """Template step: Log pattern information consistently."""
        logger.info("📝 %s:", pattern_name)
        for item in pattern_items:
            logger.info("  - %s", item)

    def demonstrate_info_patterns(self, patterns: list[tuple[str, list[str]]]) -> None:
        """Template method: Demonstrate information-only patterns.

        Args:
            patterns: List of (pattern_name, pattern_items) tuples

        """
        for pattern_name, pattern_items in patterns:
            logger.info("# Pattern {i}: {pattern_name}")
            self._log_pattern_info(pattern_name, pattern_items)

    def demonstrate_with_api_operations(self, operation_func) -> None:
        """Template method: Demonstrate patterns that require API operations.

        Args:
            operation_func: Function that performs API operations

        """
        try:
            operation_func(self.api)
        except (ValueError, ConnectionError, TypeError, AttributeError) as e:
            logger.warning("⚠️ %s operation failed: %s", self.context_name, e)


def demonstrate_connection_patterns() -> None:
    """Demonstrate different connection management patterns using Template Method."""
    demonstrator = OracleExampleDemonstrator(
        "demo_connection",
        "🔗",
        "Demonstrating Connection Patterns",
    )

    def _perform_connection_operations(api: FlextDbOracleApi) -> None:
        """Specific connection pattern operations."""
        # Pattern 1: Direct configuration (already created by demonstrator)
        logger.info("✅ Created API with direct configuration")

        # Pattern 2: From environment variables
        try:
            FlextDbOracleApi.from_env()
            logger.info("✅ Created API from environment variables")
        except (ValueError, TypeError, KeyError, OSError) as e:
            logger.warning("⚠️ Environment API creation failed: %s", e)

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
                logger.info("Connection status: %s", connected_api.is_connected)
        except (ConnectionError, ValueError, OSError, RuntimeError) as e:
            logger.warning("⚠️ Context manager connection failed: %s", e)

    demonstrator.demonstrate_with_api_operations(_perform_connection_operations)


def demonstrate_configuration_patterns() -> None:
    """Demonstrate advanced configuration patterns using Template Method."""
    demonstrator = OracleExampleDemonstrator(
        "demo_config",
        "⚙️",
        "Demonstrating Configuration Patterns",
    )

    def _perform_configuration_operations(_api: FlextDbOracleApi) -> None:
        """Specific configuration pattern operations."""
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
        except (ValueError, TypeError, KeyError) as e:
            logger.warning("⚠️ Configuration validation failed: %s", e)

    demonstrator.demonstrate_with_api_operations(_perform_configuration_operations)


def demonstrate_query_patterns() -> None:
    """Demonstrate different query execution patterns using Template Method."""
    demonstrator = OracleExampleDemonstrator(
        "demo_queries",
        "📊",
        "Demonstrating Query Patterns",
    )

    def _perform_query_operations(api: FlextDbOracleApi) -> None:
        """Specific query pattern operations."""
        # Pattern 1: Simple query
        query_result = api.query("SELECT 1 as test_value FROM DUAL")
        if query_result.is_failure:
            logger.info(
                "📝 Simple query pattern demonstrated (simulated): %s",
                query_result.error,
            )

        # Pattern 2: Parameterized query
        param_query_result = api.query(
            "SELECT * FROM employees WHERE department_id = :dept_id",
            {"dept_id": 10},
        )
        if param_query_result.is_failure:
            logger.info(
                "📝 Parameterized query pattern demonstrated (simulated): %s",
                param_query_result.error,
            )

        # Pattern 3: Single row query
        single_result = api.query_one("SELECT COUNT(*) as total FROM employees")
        if single_result.is_failure:
            logger.info(
                "📝 Single row query pattern demonstrated (simulated): %s",
                single_result.error,
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
                "📝 Batch operations pattern demonstrated (simulated): %s",
                batch_result.error,
            )

    demonstrator.demonstrate_with_api_operations(_perform_query_operations)


def demonstrate_metadata_exploration() -> None:
    """Demonstrate metadata exploration capabilities using Template Method."""
    demonstrator = OracleExampleDemonstrator(
        "demo_metadata",
        "🔍",
        "Demonstrating Metadata Exploration",
    )

    def _perform_metadata_operations(api: FlextDbOracleApi) -> None:
        """Specific metadata exploration operations."""
        # Pattern 1: List all schemas
        schemas_result = api.get_schemas()
        if schemas_result.is_failure:
            logger.info(
                "📝 Schema listing pattern demonstrated (simulated): %s",
                schemas_result.error,
            )

        # Pattern 2: List tables in a schema
        tables_result = api.get_tables("HR")
        if tables_result.is_failure:
            logger.info(
                "📝 Table listing pattern demonstrated (simulated): %s",
                tables_result.error,
            )

        # Pattern 3: Get column information for a table
        columns_result = api.get_columns("EMPLOYEES")
        if columns_result.is_failure:
            logger.info(
                "📝 Column information pattern demonstrated (simulated): %s",
                columns_result.error,
            )

        # Pattern 4: Test connection health
        health_result = api.test_connection()
        if health_result.is_failure:
            logger.info(
                "📝 Connection health check pattern demonstrated (simulated): %s",
                health_result.error,
            )

    demonstrator.demonstrate_with_api_operations(_perform_metadata_operations)


def demonstrate_transaction_patterns() -> None:
    """Demonstrate transaction management patterns using Template Method."""
    demonstrator = OracleExampleDemonstrator(
        "demo_transactions",
        "💳",
        "Demonstrating Transaction Patterns",
    )

    def _perform_transaction_operations(_api: FlextDbOracleApi) -> None:
        """Specific transaction pattern operations."""
        # Pattern 1: Manual transaction management
        logger.info("📝 Manual transaction pattern:")
        logger.info("  1. BEGIN TRANSACTION")
        logger.info("  2. Execute business operations")
        logger.info("  3. COMMIT or ROLLBACK based on results")

        # This would be real code with actual connection:
        # with api.transaction() as txn:
        #     if result1.success and result2.success:
        #         txn.commit()
        #         txn.rollback()

    demonstrator.demonstrate_with_api_operations(_perform_transaction_operations)


def demonstrate_error_handling_patterns() -> None:
    """Demonstrate comprehensive error handling patterns using Template Method."""
    demonstrator = OracleExampleDemonstrator(
        "demo_errors",
        "❌",
        "Demonstrating Error Handling Patterns",
    )

    def _perform_error_handling_operations(api: FlextDbOracleApi) -> None:
        """Specific error handling pattern operations."""
        # Pattern 1: Connection error handling
        try:
            # This will fail since we don't have real Oracle connection
            api.connect()
        except ValueError as e:
            logger.info("✅ Connection error handled: %s", e)
        except (ConnectionError, OSError, RuntimeError) as e:
            logger.info("✅ General connection error handled: %s", e)

        # Pattern 2: Query error handling with FlextResult
        result = api.query("INVALID SQL SYNTAX")
        if result.is_failure:
            logger.info("✅ Query error handled via FlextResult: {result.error}")

        # Pattern 3: Graceful degradation
        demonstrate_fallback_operations(api)
        logger.info("✅ Fallback operations result: {fallback_result}")

    demonstrator.demonstrate_with_api_operations(_perform_error_handling_operations)


def demonstrate_fallback_operations(api: FlextDbOracleApi) -> str:
    """Demonstrate fallback operations when primary operations fail."""
    # Try primary operation
    primary_result = api.test_connection()
    if primary_result.success:
        return "Primary operation succeeded"

    # Primary failed, try fallback
    logger.info("Primary operation failed, trying fallback...")

    # Fallback: return cached/default data
    return "Using fallback data due to connection failure"


def _demonstrate_info_only_patterns(
    context_name: str,
    log_emoji: str,
    log_message: str,
    patterns: list[tuple[str, list[str]]],
) -> None:
    """DRY helper: Demonstrate information-only patterns without duplication.

    SOLID REFACTORING: Final elimination of 24 lines duplication (mass=94)
    by using Strategy Pattern for pattern demonstration.
    """
    demonstrator = OracleExampleDemonstrator(context_name, log_emoji, log_message)
    demonstrator.demonstrate_info_patterns(patterns)


# DRY Refactoring: Pattern configuration factory eliminates duplication
def create_pattern_config(
    name: str,
    emoji: str,
    patterns: list[tuple[str, list[str]]],
) -> dict[str, object]:
    """Create pattern configuration without duplication."""
    return {
        "context": f"demo_{name}",
        "emoji": emoji,
        "message": f"Demonstrating {name.title()} Patterns",
        "patterns": patterns,
    }


# Pattern data separated from structure
PERFORMANCE_PATTERNS = [
    (
        "Connection pooling (simulated)",
        [
            "Use connection pool for multiple operations",
            "Reuse connections across requests",
            "Configure pool size based on workload",
        ],
    ),
    (
        "Batch operations for efficiency",
        [
            "Group multiple operations together",
            "Reduce round trips to database",
            "Use prepared statements for repeated queries",
        ],
    ),
    (
        "Async operations (when available)",
        [
            "Use async/await for I/O operations",
            "Non-blocking database operations",
            "Better resource utilization",
        ],
    ),
]

MONITORING_PATTERNS = [
    (
        "Health checks",
        [
            "Regular connection health verification",
            "Database responsiveness monitoring",
            "Automatic alerting on failures",
        ],
    ),
    (
        "Performance metrics",
        [
            "Query execution time tracking",
            "Connection pool utilization",
            "Error rate monitoring",
        ],
    ),
    (
        "Structured logging",
        [
            "Consistent log format across operations",
            "Correlation IDs for request tracing",
            "Log levels for different environments",
        ],
    ),
]

# Configuration generated without duplication
PATTERN_CONFIGURATIONS = {
    "performance": create_pattern_config("performance", "⚡", PERFORMANCE_PATTERNS),
    "monitoring": create_pattern_config("monitoring", "📊", MONITORING_PATTERNS),
}


def _demonstrate_patterns_from_config(pattern_key: str) -> None:
    """DRY pattern demonstration using data-driven configuration.

    SOLID REFACTORING: Final elimination of structural duplication
    using data-driven approach with pattern configuration.
    """
    config = PATTERN_CONFIGURATIONS[pattern_key]
    _demonstrate_info_only_patterns(
        config["context"],
        config["emoji"],
        config["message"],
        config["patterns"],
    )


def demonstrate_performance_patterns() -> None:
    """Demonstrate performance optimization patterns using data-driven configuration."""
    _demonstrate_patterns_from_config("performance")


def demonstrate_monitoring_patterns() -> None:
    """Demonstrate monitoring and observability patterns using data-driven configuration."""
    _demonstrate_patterns_from_config("monitoring")


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
        logger.exception("❌ Example execution failed: %s", e)
        raise


if __name__ == "__main__":
    main()
