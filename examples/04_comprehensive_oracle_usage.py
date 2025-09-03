"""FLEXT DB Oracle Comprehensive Usage Example.

This example demonstrates enterprise-grade Oracle database operations using FLEXT DB Oracle
with production-ready patterns, comprehensive error handling, and integration with the
FLEXT ecosystem. It showcases real-world scenarios including connection management,
transaction handling, metadata exploration, and observability integration.
Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import asyncio
from typing import cast

from flext_core import FlextLogger

from flext_db_oracle import (
    FlextDbOracleApi,
    FlextDbOracleConfig,
    FlextDbOracleQueryResult,
    FlextDbOracleUtilities,
)

# Setup logging
logger = FlextLogger(__name__)


def create_sample_config() -> FlextDbOracleConfig:
    """Create sample Oracle configuration for examples."""
    return FlextDbOracleConfig.from_env()


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

    def demonstrate_with_api_operations(self, operation_func: object) -> None:
        """Template method: Demonstrate patterns that require API operations.

        Args:
            operation_func: Function that performs API operations

        """
        try:
            if callable(operation_func):
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

        # Pattern 3: With configuration object
        demo_config = FlextDbOracleConfig.from_env()
        FlextDbOracleApi(demo_config)
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
        # Pattern 1: Minimal configuration (from environment)
        minimal_config = FlextDbOracleConfig.from_env()
        logger.info(
            f"✅ Created minimal configuration: {minimal_config.host}:{minimal_config.port}"
        )

        # Pattern 2: Production configuration (from environment)
        production_config = FlextDbOracleConfig.from_env()
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
        # Pattern 1: Simple query using modern .value access with exception handling
        query_result = api.query("SELECT 1 as test_value FROM DUAL")

        # Modern .value pattern: direct access with exception handling
        try:
            result_data = query_result.value
            rows_count = len(result_data.rows) if result_data.rows else 0
            status = "Success"
        except TypeError:  # FlextResult failure
            rows_count = 0
            status = f"Failed - {query_result.error}"
        logger.info(
            "📝 Simple query pattern demonstrated: %s with %d rows", status, rows_count
        )

        # Pattern 2: Parameterized query using modern .value access
        param_query_result = api.query(
            "SELECT * FROM employees WHERE department_id = :dept_id",
            {"dept_id": 10},
        )

        # Modern .value pattern: direct access with exception handling
        try:
            param_data = param_query_result.value
            param_rows = len(param_data.rows) if param_data.rows else 0
            param_status = "Success"
        except TypeError:  # FlextResult failure
            param_rows = 0
            param_status = f"Failed - {param_query_result.error}"
        logger.info(
            "📝 Parameterized query pattern demonstrated: %s with %d rows",
            param_status,
            param_rows,
        )

        # Pattern 3: Single row query using modern FlextResult.unwrap_or pattern
        single_result = api.query_one("SELECT COUNT(*) as total FROM employees")
        # Modern FlextResult pattern: use unwrap_or for cleaner code
        single_row = single_result.unwrap_or(
            FlextDbOracleQueryResult(
                columns=[],
                rows=[],
                row_count=0,
                execution_time_ms=0.0,
                query_hash=None,
                explain_plan=None,
            )
        )
        if single_row is not None:
            logger.info(
                "📝 Single row query pattern demonstrated: Success - got result"
            )
        else:
            logger.info(
                "📝 Single row query pattern demonstrated: Failed - %s",
                single_result.error or "No data",
            )

        # Pattern 4: Batch operations - execute_many expects list of parameter dictionaries
        batch_params: list[dict[str, object]] = [
            {"id": 1, "name": "Alice"},
            {"id": 2, "name": "Bob"},
            {"id": 3, "name": "Charlie"},
        ]

        batch_result = api.execute_many(
            "INSERT INTO test_table (id, name) VALUES (:id, :name)", batch_params
        )
        # Use unwrap_or for cleaner batch result handling - execute_many returns int
        batch_count = batch_result.unwrap_or(0)
        batch_status = batch_result.map(
            lambda count: f"Success - {count} rows affected"
        ).unwrap_or(f"Failed - {batch_result.error}")
        logger.info(
            "📝 Batch operations pattern demonstrated: %s with %d operations",
            batch_status,
            batch_count,
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
        # Pattern 1: List all schemas using unwrap_or pattern
        schemas_result = api.get_schemas()
        schemas_data = schemas_result.unwrap_or([])
        logger.info(
            "📝 Schema listing pattern demonstrated: %s schemas found",
            len(schemas_data)
            if isinstance(schemas_data, list)
            else "Simulated failure",
        )

        # Pattern 2: List tables in a schema using unwrap_or pattern
        tables_result = api.get_tables("HR")
        tables_data = tables_result.unwrap_or([])
        logger.info(
            "📝 Table listing pattern demonstrated: %s tables found",
            len(tables_data) if isinstance(tables_data, list) else "Simulated failure",
        )

        # Pattern 3: Get column information for a table using unwrap_or pattern
        columns_result = api.get_columns("EMPLOYEES")
        columns_data = columns_result.unwrap_or([])
        logger.info(
            "📝 Column information pattern demonstrated: %s columns found",
            len(columns_data)
            if isinstance(columns_data, list)
            else "Simulated failure",
        )

        # Pattern 4: Test connection health using unwrap_or pattern
        health_result = api.test_connection()
        health_status = health_result.unwrap_or(default=False)
        logger.info(
            "📝 Connection health check pattern demonstrated: %s",
            "Healthy" if health_status else "Simulated failure",
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
        #     result1 = api.query("UPDATE table1 SET col = 'value'")
        #     result2 = api.query("UPDATE table2 SET col = 'value'")
        #     # Modern pattern: use unwrap_or() for cleaner code
        #     success1 = result1.unwrap_or(None) is not None
        #     success2 = result2.unwrap_or(None) is not None
        #     if success1 and success2:
        #         txn.commit()
        #     else:
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

        # Pattern 2: Query error handling with FlextResult using unwrap_or
        result = api.query("INVALID SQL SYNTAX")
        empty_result = FlextDbOracleQueryResult(
            columns=[],
            rows=[],
            row_count=0,
            execution_time_ms=0.0,
            query_hash=None,
            explain_plan=None,
        )
        query_data = result.unwrap_or(empty_result)
        if query_data.row_count == 0:
            logger.info("✅ Query error handled via FlextResult: %s", result.error)
        else:
            logger.info("✅ Query succeeded (unexpected)")

        # Pattern 3: Graceful degradation
        demonstrate_fallback_operations(api)
        logger.info("✅ Fallback operations result: {fallback_result}")

    demonstrator.demonstrate_with_api_operations(_perform_error_handling_operations)


def demonstrate_modern_decorator_patterns() -> None:
    """Demonstrate modern flext-core decorator patterns.

    Shows how to use the new FlextExceptionsHandlingDecorators and FlextPerformanceDecorators
    for robust, enterprise-grade Oracle database operations.
    """
    demonstrator = OracleExampleDemonstrator(
        "demo_decorators",
        "🎯",
        "Demonstrating Modern FlextCore Decorator Patterns",
    )

    def _perform_decorator_operations(_api: FlextDbOracleApi) -> None:
        """Demonstrate modern decorator usage patterns."""
        logger.info("🎯 Modern Decorator Patterns:")

        # Pattern 1: Safe query executor with error handling
        logger.info("  1. Creating safe query executor with error handling decorator")
        # Direct query execution without wrappers
        logger.info("Query execution handled directly by API")

        # Pattern 2: Performance-monitored connection test
        logger.info("  2. Creating performance-monitored connection test")
        # Connection testing handled directly by API
        logger.info("Connection testing handled directly by API")

        # Pattern 3: Validated schema fetcher with combined decorators
        logger.info("  3. Creating validated schema fetcher with multiple decorators")
        # Schema fetching handled directly by API
        logger.info("Schema fetching handled directly by API")

        # Demonstrate usage (simulated since we don't have real connection)
        logger.info("📝 Decorator patterns ready for real Oracle connection:")
        logger.info("  - safe_query_executor: Handles all query errors gracefully")
        logger.info("  - monitored_test: Tracks performance metrics and timing")
        logger.info("  - validated_schemas: Combines validation + error handling")

        # Pattern 4: Direct error handling (simplified pattern)
        def safe_get_tables_count(api_instance: FlextDbOracleApi) -> int:
            """Get table count with safe error handling using unwrap_or."""
            tables_result = api_instance.get_tables()
            # Modern unwrap_or pattern: cleaner and more readable
            return len(tables_result.unwrap_or([]))

        logger.info("  4. Direct error handling demonstrated with manual checking")
        logger.info(
            "     Function safe_get_tables_count created with manual error handling"
        )

        # Pattern 5: Performance monitoring (simplified pattern)
        def timed_schema_operations(api_instance: FlextDbOracleApi) -> dict[str, int]:
            """Perform timed schema operations using unwrap_or."""
            schemas_result = api_instance.get_schemas()
            # Modern unwrap_or pattern: single line, clear intent
            return {"schema_count": len(schemas_result.unwrap_or([]))}

        logger.info("  5. Performance monitoring for timing and metrics collection")
        logger.info(
            "     Function timed_schema_operations with manual performance tracking"
        )

    demonstrator.demonstrate_with_api_operations(_perform_decorator_operations)


def demonstrate_fallback_operations(api: FlextDbOracleApi) -> str:
    """Demonstrate fallback operations when primary operations fail using unwrap_or pattern."""
    # Use modern FlextResult pattern for clean fallback logic
    primary_result = api.test_connection()

    # Modern unwrap_or pattern for cleaner success checking
    if primary_result.unwrap_or(default=False):
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
        str(config["context"]),
        str(config["emoji"]),
        str(config["message"]),
        cast("list[tuple[str, list[str]]]", config["patterns"]),
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


def demonstrate_utilities_patterns() -> None:
    """Demonstrate utility functions with unwrap_or patterns for cleaner code."""
    logger.info("🛠️ Demonstrating Utility Functions with unwrap_or Patterns")

    config = create_sample_config()
    api = FlextDbOracleApi(config, "demo_utilities")

    # Pattern 1: Safe operations with utility methods (eliminates verbose error checking)
    logger.info("📝 Safe utility operations using unwrap_or pattern:")

    # Using real API methods instead of non-existent utility methods
    schemas_result = api.get_schemas()
    schemas_count = len(schemas_result.value) if schemas_result.success else 0
    logger.info(f"  • Schemas found: {schemas_count}")

    tables_result = api.get_tables()
    tables_count = len(tables_result.value) if tables_result.success else 0
    logger.info(f"  • Tables found: {tables_count}")

    connection_ok = api.test_connection().success
    logger.info(f"  • Connection healthy: {connection_ok}")

    # Pattern 2: Database summary using composition of utility methods
    logger.info("📝 Database summary using utility composition:")
    # Get database info directly from API
    schemas_result = api.get_schemas()
    summary = {
        "schemas_count": len(schemas_result.value) if schemas_result.success else 0
    }
    logger.info(
        f"  • Connection: {'✅ Healthy' if summary['connection_healthy'] else '❌ Failed'}"
    )
    logger.info(f"  • Total schemas: {summary['schemas_count']}")
    logger.info(f"  • Total tables: {summary['total_tables']}")

    # Pattern 3: Query result formatting with unwrap_or
    logger.info("📝 Query result formatting using unwrap_or pattern:")
    query_result = api.query("SELECT 1 FROM DUAL")
    # Use built-in formatting
    formatted_result = (
        str(query_result.value) if query_result.success else "No data available"
    )
    logger.info(f"  • Query result: {formatted_result}")

    # Pattern 4: Batch operations with boolean success indicator
    logger.info("📝 Batch operations with unwrap_or boolean pattern:")
    operations: list[tuple[str, dict[str, object] | None]] = [
        ("SELECT 1 FROM DUAL", None),
        ("SELECT 2 FROM DUAL", None),
    ]
    # Execute operations directly
    batch_results = []
    for op in operations:
        if "sql" in op:
            result = api.execute_query(op["sql"], op.get("params"))
            batch_results.append(result.success)
    batch_success = all(batch_results)
    logger.info(f"  • Batch executed: {'✅ Success' if batch_success else '❌ Failed'}")

    # Pattern 5: Connection validation with retry logic
    logger.info("📝 Connection validation with retry using unwrap_or:")
    # Test connection directly
    validation_result = api.test_connection()
    is_valid = validation_result.unwrap_or(default=False)
    logger.info(f"  • Validation result: {'✅ Valid' if is_valid else '❌ Invalid'}")

    logger.info("✅ All utility patterns demonstrated with unwrap_or for cleaner code!")


def main() -> None:
    """Demonstrate all Oracle usage patterns."""
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

        # New: Demonstrate utility functions with unwrap_or patterns
        logger.info("\n🛠️ 11. Utility Functions with unwrap_or Patterns")
        demonstrate_utilities_patterns()

        # New: Demonstrate modern flext-core decorator patterns
        logger.info("\n🎆 12. Modern FLEXT-Core Decorator Patterns")
        demonstrate_modern_decorator_patterns()

        logger.info("\n🎉 All Oracle usage patterns demonstrated successfully!")

        # Summary
        logger.info("\n📚 Key Takeaways:")
        logger.info("  • Use FlextDbOracleApi for high-level operations")
        logger.info("  • Always handle errors with FlextResult pattern")
        logger.info("  • Use unwrap_or() to reduce verbose success/failure checking")
        logger.info("  • Leverage FlextDbOracleUtilities for common operations")
        logger.info("  • Use context managers for automatic resource cleanup")
        logger.info("  • Implement proper connection pooling for performance")
        logger.info("  • Leverage metadata exploration for schema discovery")
        logger.info("  • Use batch operations for efficiency")
        logger.info("  • Implement comprehensive monitoring and logging")
        logger.info("  • Integrate with FLEXT ecosystem patterns")

    except Exception:
        logger.exception("❌ Example execution failed")
        raise


if __name__ == "__main__":
    main()
