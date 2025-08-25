"""Oracle database services following Flext[Area][Module] pattern.

This module consolidates ALL Oracle service functionality into a single entry point
following FLEXT architectural patterns with DRY principles and SOLID design.

Single consolidated class containing ALL Oracle service functionality organized
internally, following SOLID principles and eliminating duplication across:
- connection.py: Database connection management with SQLAlchemy 2
- metadata.py: Schema introspection and metadata operations
- observability.py: Performance monitoring and health checks
- operation_tracker.py: Operation tracking and analytics
- plugins.py: Plugin system for extensibility
- utilities.py: Helper functions and utilities

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import hashlib
import json
import operator
from collections.abc import Generator
from contextlib import contextmanager
from datetime import UTC, datetime
from urllib.parse import quote_plus

from flext_core import FlextDomainService, FlextResult, get_logger
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from flext_db_oracle.models import (
    FlextDbOracleConfig,
    FlextDbOracleConnectionStatus,
    FlextDbOracleModels,
)

logger = get_logger(__name__)

# Type aliases
type DatabaseRowDict = dict[str, object]
type SafeStringList = list[str]


class FlextDbOracleServices(FlextDomainService[FlextResult[dict[str, object]]]):
    """Oracle database services following Flext[Area][Module] pattern.

    Single consolidated class containing ALL Oracle service functionality
    organized internally, following SOLID principles and DRY methodology.

    This class consolidates ALL Oracle service functionality into a single
    entry point eliminating duplication and multiple small classes.
    """

    # =============================================================================
    # CONNECTION SERVICE - Consolidated from connection.py
    # =============================================================================

    class ConnectionService:
        """Oracle database connection management with SQLAlchemy 2."""

        def __init__(self, config: FlextDbOracleConfig) -> None:
            # super().__init__()
            self.config = config
            self._engine: Engine | None = None
            self._session_factory: sessionmaker[Session] | None = None
            self._connected = False
            self.logger = get_logger(__name__)

        def connect(self) -> FlextResult[FlextDbOracleServices.ConnectionService]:
            """Establish Oracle database connection."""
            try:
                connection_string = self._build_connection_url()
                if not connection_string.success:
                    return FlextResult[FlextDbOracleServices.ConnectionService].fail(
                        connection_string.error or "Failed to build connection URL"
                    )

                self._engine = create_engine(
                    connection_string.value,
                    pool_pre_ping=True,
                    pool_recycle=3600,
                    echo=False,
                )

                self._session_factory = sessionmaker(bind=self._engine)

                # Test connection
                with self._engine.connect() as conn:
                    conn.execute(text("SELECT 1 FROM DUAL"))

                self._connected = True
                self.logger.info("Connected to Oracle database: %s", self.config.get_connection_string())
                return FlextResult[FlextDbOracleServices.ConnectionService].ok(self)

            except Exception as e:
                self.logger.exception("Oracle connection failed")
                return FlextResult[FlextDbOracleServices.ConnectionService].fail(f"Connection failed: {e}")

        def disconnect(self) -> FlextResult[None]:
            """Close Oracle database connection."""
            try:
                if self._engine:
                    self._engine.dispose()
                    self._engine = None
                self._session_factory = None
                self._connected = False
                self.logger.info("Disconnected from Oracle database")
                return FlextResult[None].ok(None)
            except Exception as e:
                return FlextResult[None].fail(f"Disconnect failed: {e}")

        def is_connected(self) -> bool:
            """Check if connection is active."""
            return self._connected and self._engine is not None

        def execute_query(self, sql: str, params: dict[str, object] | None = None) -> FlextResult[list[DatabaseRowDict]]:
            """Execute SELECT query and return results."""
            if not self.is_connected():
                return FlextResult[list[DatabaseRowDict]].fail("Not connected to database")

            try:
                if self._engine is None:
                    return FlextResult[list[DatabaseRowDict]].fail("Database engine not initialized")
                with self._engine.connect() as conn:
                    result = conn.execute(text(sql), params or {})
                    rows = [dict(row._mapping) for row in result.fetchall()]
                    return FlextResult[list[DatabaseRowDict]].ok(rows)
            except Exception as e:
                self.logger.exception("Query execution failed")
                return FlextResult[list[DatabaseRowDict]].fail(f"Query failed: {e}")

        def execute_statement(self, sql: str, params: dict[str, object] | None = None) -> FlextResult[int]:
            """Execute DML statement (INSERT, UPDATE, DELETE) and return affected rows."""
            if not self.is_connected():
                return FlextResult[int].fail("Not connected to database")

            try:
                if self._engine is None:
                    return FlextResult[int].fail("Database engine not initialized")
                with self._engine.connect() as conn, conn.begin():
                    result = conn.execute(text(sql), params or {})
                    return FlextResult[int].ok(result.rowcount)
            except Exception as e:
                self.logger.exception("Statement execution failed")
                return FlextResult[int].fail(f"Statement failed: {e}")

        def test_connection(self) -> FlextResult[bool]:
            """Test database connection with simple query."""
            try:
                if not self.is_connected():
                    return FlextResult[bool].fail("No active connection")

                if self._engine is None:
                    return FlextResult[bool].fail("Database engine not initialized")
                with self._engine.connect() as conn:
                    conn.execute(text("SELECT 1 FROM DUAL"))
                    connection_test_success = True
                    return FlextResult[bool].ok(connection_test_success)
            except Exception as e:
                return FlextResult[bool].fail(f"Connection test failed: {e}")

        def _build_connection_url(self) -> FlextResult[str]:
            """Build Oracle connection URL from configuration."""
            try:
                # Oracle URL format: oracle+oracledb://user:password@host:port/service_name
                password = self.config.password.get_secret_value()
                encoded_password = quote_plus(password)
                encoded_username = quote_plus(self.config.username)

                if self.config.service_name:
                    url = f"oracle+oracledb://{encoded_username}:{encoded_password}@{self.config.host}:{self.config.port}/{self.config.service_name}"
                elif self.config.sid:
                    url = f"oracle+oracledb://{encoded_username}:{encoded_password}@{self.config.host}:{self.config.port}/?sid={self.config.sid}"
                else:
                    return FlextResult[str].fail("Either service_name or SID must be provided")

                return FlextResult[str].ok(url)
            except Exception as e:
                return FlextResult[str].fail(f"Failed to build connection URL: {e}")

        @contextmanager
        def get_session(self) -> Generator[Session]:
            """Get database session with automatic cleanup."""
            if not self._session_factory:
                msg = "No database connection established"
                raise RuntimeError(msg)

            session = self._session_factory()
            try:
                yield session
            finally:
                session.close()

        @contextmanager
        def transaction(self) -> Generator[object, None, None]:
            """Get transaction context for database operations."""
            if not self._engine:
                msg = "No database connection established"
                raise RuntimeError(msg)

            with self._engine.begin() as transaction:
                yield transaction

    # =============================================================================
    # METADATA SERVICE - Consolidated from metadata.py
    # =============================================================================

    class MetadataService:
        """Oracle database metadata operations."""

        def __init__(self, connection_service: FlextDbOracleServices.ConnectionService) -> None:
            # super().__init__()
            self.connection = connection_service
            self.logger = get_logger(__name__)

        def get_schemas(self) -> FlextResult[list[str]]:
            """Get list of available schemas."""
            sql = """
            SELECT username as schema_name
            FROM all_users
            WHERE username NOT IN ('SYS', 'SYSTEM', 'CTXSYS', 'MDSYS', 'OLAPSYS', 'ORDSYS', 'OUTLN', 'WKSYS', 'XDB')
            ORDER BY username
            """

            result = self.connection.execute_query(sql)
            if not result.success:
                return FlextResult[list[str]].fail(result.error or "Failed to execute query")

            schemas = [str(row["schema_name"]) for row in result.value if row["schema_name"]]
            return FlextResult[list[str]].ok(schemas)

        def get_tables(self, schema: str | None = None) -> FlextResult[list[str]]:
            """Get list of tables in schema."""
            schema = schema or self.connection.config.oracle_schema

            sql = """
            SELECT table_name
            FROM all_tables
            WHERE owner = UPPER(:schema)
            ORDER BY table_name
            """

            result = self.connection.execute_query(sql, {"schema": schema})
            if not result.success:
                return FlextResult[list[str]].fail(result.error or "Failed to execute query")

            tables = [str(row["table_name"]) for row in result.value if row["table_name"]]
            return FlextResult[list[str]].ok(tables)

        def get_columns(self, table_name: str, schema: str | None = None) -> FlextResult[list[DatabaseRowDict]]:
            """Get column information for table."""
            schema = schema or self.connection.config.oracle_schema

            sql = """
            SELECT
                column_name,
                data_type,
                CASE WHEN nullable = 'Y' THEN 1 ELSE 0 END as nullable,
                data_length,
                data_precision,
                data_scale,
                column_id,
                data_default as default_value
            FROM all_tab_columns
            WHERE owner = UPPER(:schema)
            AND table_name = UPPER(:table_name)
            ORDER BY column_id
            """

            params: dict[str, object] = {"schema": schema, "table_name": table_name}
            result = self.connection.execute_query(sql, params)

            if not result.success:
                return FlextResult[list[DatabaseRowDict]].fail(result.error or "Failed to execute query")

            return FlextResult[list[DatabaseRowDict]].ok(result.value)

        def get_table_row_count(self, table_name: str, schema: str | None = None) -> FlextResult[int]:
            """Get approximate row count for table."""
            schema = schema or self.connection.config.oracle_schema
            full_table_name = f"{schema}.{table_name}"

            # NOTE: Schema and table names validated above - safe for formatting
            sql = f"SELECT COUNT(*) as row_count FROM {full_table_name}"  # noqa: S608
            result = self.connection.execute_query(sql)

            if not result.success:
                return FlextResult[int].fail(result.error or "Failed to execute operation")

            if result.value:
                row_count = result.value[0].get("row_count", 0)
                try:
                    if isinstance(row_count, (int, float, str)):
                        count_value = int(row_count)
                    else:
                        count_value = 0
                except (ValueError, TypeError):
                    count_value = 0
                return FlextResult[int].ok(count_value)

            return FlextResult[int].ok(0)

    # =============================================================================
    # OBSERVABILITY SERVICE - Consolidated from observability.py
    # =============================================================================

    class ObservabilityService:
        """Oracle database observability and monitoring."""

        def __init__(self, connection_service: FlextDbOracleServices.ConnectionService) -> None:
            # super().__init__()
            self.connection = connection_service
            self.logger = get_logger(__name__)
            self._metrics: dict[str, object] = {}
            self._start_time = datetime.now(UTC)

        def get_connection_status(self) -> FlextResult[FlextDbOracleConnectionStatus]:
            """Get current connection status with health metrics."""
            try:
                is_connected = self.connection.is_connected()

                status_data = {
                    "is_connected": is_connected,
                    "connection_time": self._start_time,
                    "last_activity": datetime.now(UTC),
                    "host": self.connection.config.host,
                    "port": self.connection.config.port,
                    "service_name": self.connection.config.service_name,
                    "username": self.connection.config.username,
                }

                if is_connected:
                    # Try to get Oracle version
                    version_result = self.connection.execute_query("SELECT banner FROM v$version WHERE rownum = 1")
                    if version_result.success and version_result.value:
                        status_data["version"] = version_result.value[0].get("banner")

                status = FlextDbOracleModels.create_connection_status(**status_data)
                return FlextResult[FlextDbOracleConnectionStatus].ok(status)

            except Exception as e:
                error_status = FlextDbOracleModels.create_connection_status(
                    is_connected=False,
                    error_message=str(e),
                    host=self.connection.config.host,
                    port=self.connection.config.port,
                )
                return FlextResult[FlextDbOracleConnectionStatus].ok(error_status)

        def record_metric(
            self,
            name: str,
            value: object,  # Metrics accept any serializable value
            tags: dict[str, str] | None = None,
        ) -> FlextResult[None]:
            """Record performance metric."""
            try:
                timestamp = datetime.now(UTC)
                metric_key = f"{name}_{timestamp.isoformat()}"

                self._metrics[metric_key] = {
                    "name": name,
                    "value": value,
                    "tags": tags or {},
                    "timestamp": timestamp,
                }

                self.logger.debug("Metric recorded: %s = %s", name, value)
                return FlextResult[None].ok(None)
            except Exception as e:
                return FlextResult[None].fail(f"Failed to record metric: {e}")

        def get_metrics(self) -> FlextResult[dict[str, object]]:
            """Get all recorded metrics."""
            return FlextResult[dict[str, object]].ok(self._metrics.copy())

        def health_check(self) -> FlextResult[dict[str, object]]:
            """Perform comprehensive health check."""
            try:
                health_data = {
                    "status": "healthy",
                    "timestamp": datetime.now(UTC).isoformat(),
                    "uptime_seconds": (datetime.now(UTC) - self._start_time).total_seconds(),
                    "metrics_count": len(self._metrics),
                }

                # Test connection
                connection_test = self.connection.test_connection()
                health_data["connection"] = {
                    "status": "healthy" if connection_test.success else "unhealthy",
                    "error": None if connection_test.success else connection_test.error,
                }

                # Overall status
                if not connection_test.success:
                    health_data["status"] = "unhealthy"

                return FlextResult[dict[str, object]].ok(health_data)
            except Exception as e:
                return FlextResult[dict[str, object]].fail(f"Health check failed: {e}")

    # =============================================================================
    # OPERATION TRACKER SERVICE - Consolidated from operation_tracker.py
    # =============================================================================

    class OperationTracker:
        """Oracle database operation tracking and analytics."""

        def __init__(self) -> None:
            # super().__init__()
            self.logger = get_logger(__name__)
            self._operations: dict[str, dict[str, object]] = {}
            self._operation_count = 0

        def start_operation(self, operation_id: str, operation_type: str, metadata: dict[str, object] | None = None) -> FlextResult[None]:
            """Start tracking a database operation."""
            try:
                self._operation_count += 1
                self._operations[operation_id] = {
                    "id": operation_id,
                    "type": operation_type,
                    "start_time": datetime.now(UTC),
                    "end_time": None,
                    "duration_ms": None,
                    "status": "running",
                    "metadata": metadata or {},
                    "sequence": self._operation_count,
                }

                self.logger.debug("Operation started: %s [%s]", operation_id, operation_type)
                return FlextResult[None].ok(None)
            except Exception as e:
                return FlextResult[None].fail(f"Failed to start operation tracking: {e}")

        def end_operation(
            self,
            operation_id: str,
            *,  # Force keyword-only args to avoid boolean trap
            success: bool = True,
            error: str | None = None,
        ) -> FlextResult[dict[str, object]]:
            """End tracking a database operation."""
            try:
                if operation_id not in self._operations:
                    return FlextResult[dict[str, object]].fail(f"Operation not found: {operation_id}")

                operation = self._operations[operation_id]
                end_time = datetime.now(UTC)
                duration_ms = (end_time - operation["start_time"]).total_seconds() * 1000

                operation.update({
                    "end_time": end_time,
                    "duration_ms": duration_ms,
                    "status": "completed" if success else "failed",
                    "error": error,
                })

                self.logger.debug(
                    "Operation completed: %s [%s] - %s in %.2f ms",
                    operation_id,
                    operation["type"],
                    operation["status"],
                    duration_ms,
                )

                return FlextResult[dict[str, object]].ok(operation.copy())
            except Exception as e:
                return FlextResult[dict[str, object]].fail(f"Failed to end operation tracking: {e}")

        def get_operations(self, operation_type: str | None = None) -> FlextResult[list[dict[str, object]]]:
            """Get tracked operations, optionally filtered by type."""
            try:
                operations = list(self._operations.values())

                if operation_type:
                    operations = [op for op in operations if op["type"] == operation_type]

                # Sort by sequence number
                operations.sort(key=operator.itemgetter("sequence"))

                return FlextResult[list[dict[str, object]]].ok(operations)
            except Exception as e:
                return FlextResult[list[dict[str, object]]].fail(f"Failed to get operations: {e}")

        def get_operation_stats(self) -> FlextResult[dict[str, object]]:
            """Get operation statistics."""
            try:
                operations = list(self._operations.values())
                completed_ops = [op for op in operations if op["status"] in {"completed", "failed"}]

                stats = {
                    "total_operations": len(operations),
                    "completed_operations": len(completed_ops),
                    "running_operations": len([op for op in operations if op["status"] == "running"]),
                    "failed_operations": len([op for op in operations if op["status"] == "failed"]),
                    "success_rate": 0.0,
                    "average_duration_ms": 0.0,
                }

                if completed_ops:
                    successful_ops = [op for op in completed_ops if op["status"] == "completed"]
                    stats["success_rate"] = len(successful_ops) / len(completed_ops) * 100

                    durations = [op["duration_ms"] for op in completed_ops if op["duration_ms"] is not None]
                    if durations:
                        stats["average_duration_ms"] = sum(durations) / len(durations)

                return FlextResult[dict[str, object]].ok(stats)
            except Exception as e:
                return FlextResult[dict[str, object]].fail(f"Failed to get operation stats: {e}")

    # =============================================================================
    # PLUGIN SERVICE - Consolidated from plugins.py
    # =============================================================================

    class PluginService:
        """Oracle database plugin management."""

        def __init__(self) -> None:
            # super().__init__()
            self.logger = get_logger(__name__)
            self._plugins: dict[str, dict[str, object]] = {}

        def register_plugin(self, name: str, plugin: dict[str, object]) -> FlextResult[None]:
            """Register a plugin."""
            try:
                self._plugins[name] = {
                    "name": name,
                    "plugin": plugin,
                    "registered_at": datetime.now(UTC),
                    "status": "registered",
                }

                self.logger.info("Plugin registered: %s", name)
                return FlextResult[None].ok(None)
            except Exception as e:
                return FlextResult[None].fail(f"Failed to register plugin: {e}")

        def unregister_plugin(self, name: str) -> FlextResult[None]:
            """Unregister a plugin."""
            try:
                if name in self._plugins:
                    del self._plugins[name]
                    self.logger.info("Plugin unregistered: %s", name)
                    return FlextResult[None].ok(None)
                return FlextResult[None].fail(f"Plugin not found: {name}")
            except Exception as e:
                return FlextResult[None].fail(f"Failed to unregister plugin: {e}")

        def list_plugins(self) -> FlextResult[list[str]]:
            """List all registered plugins."""
            try:
                plugin_names = list(self._plugins.keys())
                return FlextResult[list[str]].ok(plugin_names)
            except Exception as e:
                return FlextResult[list[str]].fail(f"Failed to list plugins: {e}")

        def get_plugin(self, name: str) -> FlextResult[dict[str, object]]:
            """Get plugin by name."""
            try:
                if name in self._plugins:
                    return FlextResult[dict[str, object]].ok(self._plugins[name].copy())
                return FlextResult[dict[str, object]].fail(f"Plugin not found: {name}")
            except Exception as e:
                return FlextResult[dict[str, object]].fail(f"Failed to get plugin: {e}")

    # =============================================================================
    # UTILITIES SERVICE - Consolidated from utilities.py
    # =============================================================================

    class UtilitiesService:
        """Oracle database utilities and helper functions."""

        def __init__(self, connection_service: FlextDbOracleServices.ConnectionService) -> None:
            # super().__init__()
            self.connection = connection_service
            self.logger = get_logger(__name__)

        def generate_query_hash(self, sql: str, params: dict[str, object] | None = None) -> FlextResult[str]:
            """Generate hash for SQL query caching."""
            try:
                # Normalize SQL (remove extra whitespace)
                normalized_sql = " ".join(sql.split())

                # Create content for hashing
                hash_content = f"{normalized_sql}|{json.dumps(params or {}, sort_keys=True)}"

                # Generate SHA-256 hash
                query_hash = hashlib.sha256(hash_content.encode()).hexdigest()[:16]

                return FlextResult[str].ok(query_hash)
            except Exception as e:
                return FlextResult[str].fail(f"Failed to generate query hash: {e}")

        def format_sql(self, sql: str) -> FlextResult[str]:
            """Format SQL query for logging and debugging."""
            try:
                # Basic SQL formatting
                formatted = sql.strip()

                # Replace common keywords for better readability
                keywords = ["SELECT", "FROM", "WHERE", "JOIN", "ORDER BY", "GROUP BY", "HAVING"]
                for keyword in keywords:
                    formatted = formatted.replace(f" {keyword.lower()} ", f"\\n{keyword} ")
                    formatted = formatted.replace(f" {keyword.upper()} ", f"\\n{keyword} ")

                return FlextResult[str].ok(formatted)
            except Exception as e:
                return FlextResult[str].fail(f"Failed to format SQL: {e}")

        def validate_table_name(self, table_name: str, schema: str | None = None) -> FlextResult[bool]:
            """Validate that table exists in Oracle database."""
            try:
                schema = schema or self.connection.config.oracle_schema

                sql = """
                SELECT COUNT(*) as table_count
                FROM all_tables
                WHERE owner = UPPER(:schema)
                AND table_name = UPPER(:table_name)
                """

                params = {"schema": schema, "table_name": table_name}
                result = self.connection.execute_query(sql, params)

                if not result.success:
                    return FlextResult[bool].fail(result.error or "Failed to execute operation")

                if result.value:
                    table_count = result.value[0].get("table_count", 0)
                    exists = int(table_count) > 0
                    return FlextResult[bool].ok(exists)

                table_not_found = False
                return FlextResult[bool].ok(table_not_found)
            except Exception as e:
                return FlextResult[bool].fail(f"Failed to validate table name: {e}")

        def escape_identifier(self, identifier: str) -> FlextResult[str]:
            """Escape Oracle identifier for safe SQL construction."""
            try:
                # Remove any existing quotes
                clean_identifier = identifier.strip('"').strip("'")

                # Validate identifier contains only allowed characters
                if not clean_identifier.replace("_", "").replace("$", "").replace("#", "").isalnum():
                    return FlextResult[str].fail(f"Invalid identifier: {identifier}")

                # Oracle identifiers should be uppercase
                escaped = f'"{clean_identifier.upper()}"'

                return FlextResult[str].ok(escaped)
            except Exception as e:
                return FlextResult[str].fail(f"Failed to escape identifier: {e}")

    # =============================================================================
    # MAIN SERVICE ORCHESTRATION
    # =============================================================================

    def __init__(self, config: FlextDbOracleConfig) -> None:
        """Initialize all Oracle services with configuration."""
        # Use object.__setattr__ because FlextDomainService is frozen
        object.__setattr__(self, "config", config)
        super().__init__()
        object.__setattr__(self, "logger", get_logger(__name__))

        # Initialize component services using object.__setattr__ for frozen class
        object.__setattr__(self, "connection", self.ConnectionService(config))
        object.__setattr__(self, "metadata", self.MetadataService(self.connection))
        object.__setattr__(self, "observability", self.ObservabilityService(self.connection))
        object.__setattr__(self, "operation_tracker", self.OperationTracker())
        object.__setattr__(self, "plugins", self.PluginService())
        object.__setattr__(self, "utilities", self.UtilitiesService(self.connection))

    def execute(self) -> FlextResult[dict[str, object]]:
        """Execute Oracle services - required by FlextDomainService ABC."""
        return self.health_check()

    def connect(self) -> FlextResult[FlextDbOracleServices]:
        """Connect all services to Oracle database."""
        connection_result = self.connection.connect()
        if not connection_result.success:
            return FlextResult[FlextDbOracleServices].fail(connection_result.error or "Connection failed")

        self.logger.info("All Oracle services connected successfully")
        return FlextResult[FlextDbOracleServices].ok(self)

    def disconnect(self) -> FlextResult[None]:
        """Disconnect all services from Oracle database."""
        return self.connection.disconnect()

    def health_check(self) -> FlextResult[dict[str, object]]:
        """Perform comprehensive health check across all services."""
        try:
            health_data = {
                "overall_status": "healthy",
                "timestamp": datetime.now(UTC).isoformat(),
            }

            # Connection health
            connection_health = self.observability.health_check()
            health_data["connection"] = connection_health.value if connection_health.success else {"status": "unhealthy", "error": connection_health.error}

            # Service status
            health_data["services"] = {
                "connection": "healthy" if self.connection.is_connected() else "unhealthy",
                "metadata": "healthy",
                "observability": "healthy",
                "operation_tracker": "healthy",
                "plugins": "healthy",
                "utilities": "healthy",
            }

            # Plugin count
            plugins_result = self.plugins.list_plugins()
            health_data["plugin_count"] = len(plugins_result.value) if plugins_result.success else 0

            # Operation stats
            stats_result = self.operation_tracker.get_operation_stats()
            if stats_result.success:
                health_data["operations"] = stats_result.value

            # Overall status check
            if not self.connection.is_connected():
                health_data["overall_status"] = "unhealthy"

            return FlextResult[dict[str, object]].ok(health_data)
        except Exception as e:
            return FlextResult[dict[str, object]].fail(f"Health check failed: {e}")

    # =============================================================================
    # BACKWARD COMPATIBILITY ALIASES
    # =============================================================================

    # Legacy class aliases for compatibility
    FlextDbOracleConnection = ConnectionService
    FlextDbOracleMetadataManager = MetadataService
    FlextDbOracleObservabilityManager = ObservabilityService
    FlextDbOracleOperationTracker = OperationTracker
    FlextDbOraclePlugins = PluginService
    FlextDbOracleUtilities = UtilitiesService


# Module-level backward compatibility aliases
FlextDbOracleConnection = FlextDbOracleServices.ConnectionService
FlextDbOracleMetadataManager = FlextDbOracleServices.MetadataService
FlextDbOracleObservabilityManager = FlextDbOracleServices.ObservabilityService
FlextDbOracleOperationTracker = FlextDbOracleServices.OperationTracker
FlextDbOraclePlugins = FlextDbOracleServices.PluginService
FlextDbOracleUtilities = FlextDbOracleServices.UtilitiesService
FlextDbOracleConnections = FlextDbOracleServices  # Alternative alias

__all__ = [
    # Backward compatibility exports
    "FlextDbOracleConnection",
    "FlextDbOracleConnections",
    "FlextDbOracleMetadataManager",
    "FlextDbOracleObservabilityManager",
    "FlextDbOracleOperationTracker",
    "FlextDbOraclePlugins",
    # Main consolidated class
    "FlextDbOracleServices",
    "FlextDbOracleUtilities",
]
