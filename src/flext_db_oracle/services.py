"""Oracle database services following Flext[Area][Module] pattern.

Single consolidated class containing ALL Oracle service functionality organized
internally, following SOLID principles and eliminating duplication.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

# hashlib removed - using FlextUtilities.generate_hash instead
from collections.abc import Generator
from contextlib import contextmanager
from datetime import UTC, datetime
from typing import ClassVar, cast
from urllib.parse import quote_plus

from flext_core import (
    FlextDecorators,
    FlextLogger,
    FlextMixins,
    FlextResult,
)
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from flext_db_oracle.constants import FlextDbOracleConstants
from flext_db_oracle.models import FlextDbOracleModels

logger = FlextLogger(__name__)


def _is_safe_sql_identifier(identifier: str) -> bool:
    """Validate SQL identifier to prevent injection.

    Args:
        identifier: SQL identifier to validate

    Returns:
        True if identifier is safe for use in SQL

    """
    if not identifier or not isinstance(identifier, str):
        return False

    # Oracle identifiers: alphanumeric, underscore, dollar sign, hash
    # First character must be letter or underscore
    # Max length 128 characters (Oracle standard)
    max_identifier_length = 128
    if len(identifier) > max_identifier_length:
        return False

    # Check first character
    if not (identifier[0].isalpha() or identifier[0] == "_"):
        return False

    # Check remaining characters
    for char in identifier[1:]:
        if not (char.isalnum() or char in ("_", "$", "#")):
            return False

    # Prevent SQL keywords (basic set)
    reserved_words = {
        "SELECT", "INSERT", "UPDATE", "DELETE", "DROP", "CREATE",
        "ALTER", "TRUNCATE", "GRANT", "REVOKE", "UNION", "ORDER",
        "GROUP", "HAVING", "WHERE", "FROM", "INTO", "VALUES"
    }

    return identifier.upper() not in reserved_words


class FlextDbOracleServices(FlextMixins.Service):
    """Single consolidated Oracle database services class.

    Following flext-core pattern: one class per module, all functionality consolidated.
    Uses FlextServices architecture and FlextMixins for enhanced capabilities.
    """

    # No type aliases - use direct types for clarity

    # Declare fields as Pydantic model fields
    config: FlextDbOracleModels.OracleConfig

    # Internal state attributes - not Pydantic fields
    _engine: Engine | None = None
    _session_factory: object | None = None
    _connected: bool = False
    _metrics: ClassVar[dict[str, object]] = {}
    _operations: list[dict[str, object]]
    _plugins: ClassVar[dict[str, object]] = {}

    # Use centralized constants from FlextDbOracleConstants

    def __init__(
        self, config: FlextDbOracleModels.OracleConfig, **kwargs: object
    ) -> None:
        """Initialize Oracle services with configuration."""
        # Initialize Pydantic model properly
        super().__init__(**kwargs)
        # Set config using object.__setattr__ to bypass Pydantic protection
        object.__setattr__(self, "config", config)

    def model_post_init(self, __context: object, /) -> None:
        """Post-initialization setup for non-Pydantic attributes."""
        # Use object.__setattr__ to bypass frozen instance protection
        object.__setattr__(self, "logger", FlextLogger(__name__))
        object.__setattr__(self, "_engine", None)
        object.__setattr__(self, "_session_factory", None)
        object.__setattr__(self, "_operations", [])
        object.__setattr__(self, "_connected", False)
        object.__setattr__(self, "_plugins", {})

        # CRITICAL: Add connection property that CLI expects
        object.__setattr__(self, "connection", self)

    # =============================================================================
    # CONNECTION METHODS
    # =============================================================================

    @FlextDecorators.Reliability.safe_result
    def connect(self) -> FlextResult[FlextDbOracleServices]:
        """Establish Oracle database connection."""
        try:
            connection_string = self._build_connection_url()
            if not connection_string.success:
                return FlextResult[FlextDbOracleServices].fail(
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
            logger.info(
                "Connected to Oracle database: %s",
                self.config.host,
            )
            return FlextResult[FlextDbOracleServices].ok(self)

        except Exception as e:
            logger.exception("Oracle connection failed")
            return FlextResult[FlextDbOracleServices].fail(f"Connection failed: {e}")

    @FlextDecorators.Reliability.safe_result
    def disconnect(self) -> FlextResult[None]:
        try:
            if self._engine:
                self._engine.dispose()
                self._engine = None
                self._session_factory = None
                self._connected = False
                logger.info("Disconnected from Oracle database")
            return FlextResult[None].ok(None)
        except Exception as e:
            return FlextResult[None].fail(f"Disconnect failed: {e}")

    def is_connected(self) -> bool:
        """Check if connected to Oracle database."""
        return self._connected

    def execute_query(
        self,
        sql: str,
        params: dict[str, object] | None = None,
    ) -> FlextResult[list[dict[str, object]]]:
        """Execute SQL query and return results."""
        try:
            if not self._connected or not self._engine:
                return FlextResult[list[dict[str, object]]].fail(
                    "Not connected to database"
                )

            with self._engine.connect() as conn:
                result = conn.execute(text(sql), params or {})
                rows = [dict(row._mapping) for row in result]
                return FlextResult[list[dict[str, object]]].ok(rows)

        except Exception as e:
            return FlextResult[list[dict[str, object]]].fail(
                f"Query execution failed: {e}"
            )

    def execute_statement(
        self,
        sql: str,
        params: dict[str, object] | None = None,
    ) -> FlextResult[int]:
        """Execute SQL statement and return affected rows."""
        try:
            if not self._connected or not self._engine:
                return FlextResult[int].fail("Not connected to database")

            with self._engine.connect() as conn:
                result = conn.execute(text(sql), params or {})
                return FlextResult[int].ok(result.rowcount)

        except Exception as e:
            return FlextResult[int].fail(f"Statement execution failed: {e}")

    def test_connection(self) -> FlextResult[bool]:
        """Test Oracle database connection."""
        try:
            if not self._connected or not self._engine:
                return FlextResult[bool].fail("Not connected to database")

            with self._engine.connect() as conn:
                conn.execute(text("SELECT 1 FROM DUAL"))
                return FlextResult[bool].ok(data=True)

        except Exception as e:
            return FlextResult[bool].fail(f"Connection test failed: {e}")

    def _build_connection_url(self) -> FlextResult[str]:
        """Build Oracle connection URL from configuration."""
        try:
            # Build Oracle connection string
            password = self.config.password.get_secret_value()
            encoded_password = quote_plus(password)

            # Use SID if available, otherwise use service_name
            database_identifier = self.config.sid or self.config.service_name

            connection_string = (
                f"oracle+oracledb://{self.config.username}:"
                f"{encoded_password}@{self.config.host}:{self.config.port}/"
                f"{database_identifier}"
            )

            return FlextResult[str].ok(connection_string)
        except Exception as e:
            return FlextResult[str].fail(f"Failed to build connection URL: {e}")

    @contextmanager
    def get_session(self) -> Generator[Session]:
        """Get database session context manager."""
        if not self._session_factory:
            msg = "No session factory available"
            raise RuntimeError(msg)

        if not callable(self._session_factory):
            error_msg = "Session factory is not callable"
            raise TypeError(error_msg)
        session: Session = cast("Session", self._session_factory())
        try:
            yield session
        finally:
            session.close()

    @contextmanager
    def transaction(self) -> Generator[object]:
        """Get transaction context for database operations."""
        if not self._engine:
            msg = "No database connection established"
            raise RuntimeError(msg)

        with self._engine.begin() as transaction:
            yield transaction

    def build_select(
        self,
        table_name: str,
        columns: list[str] | None = None,
        conditions: dict[str, object] | None = None,
        schema_name: str | None = None,
    ) -> FlextResult[str]:
        """Build a SELECT query string."""
        try:
            # Validate all SQL identifiers for security
            if not _is_safe_sql_identifier(table_name):
                return FlextResult[str].fail("Invalid table name")

            if schema_name and not _is_safe_sql_identifier(schema_name):
                return FlextResult[str].fail("Invalid schema name")

            if columns:
                for col in columns:
                    if not _is_safe_sql_identifier(col):
                        return FlextResult[str].fail(f"Invalid column name: {col}")

            column_list, full_table_name = self._build_select_base(
                table_name, columns, schema_name
            )
            query = f"SELECT {column_list} FROM {full_table_name}"  # noqa: S608 - Safe: all identifiers validated

            if conditions:
                where_clauses = []
                for key in conditions:
                    if not _is_safe_sql_identifier(key):
                        return FlextResult[str].fail(f"Invalid condition column name: {key}")
                    # Use parameterized query to prevent SQL injection
                    where_clauses.append(f"{key} = :{key}")
                query += f" WHERE {' AND '.join(where_clauses)}"

            return FlextResult[str].ok(query)
        except Exception as e:
            return FlextResult[str].fail(f"Failed to build SELECT query: {e}")

    def build_select_safe(
        self,
        table_name: str,
        columns: list[str] | None = None,
        conditions: dict[str, object] | None = None,
        schema_name: str | None = None,
    ) -> FlextResult[tuple[str, dict[str, object]]]:
        """Build a parameterized SELECT query string with parameters."""
        try:
            column_list, full_table_name = self._build_select_base(
                table_name, columns, schema_name
            )
            query = f"SELECT {column_list} FROM {full_table_name}"  # noqa: S608 - Safe: all identifiers validated
            params: dict[str, object] = {}

            if conditions:
                where_clauses = []
                for key, value in conditions.items():
                    param_name = f"param_{key}"
                    where_clauses.append(f"{key} = :{param_name}")
                    params[param_name] = value
                query += f" WHERE {' AND '.join(where_clauses)}"

            return FlextResult[tuple[str, dict[str, object]]].ok((query, params))
        except Exception as e:
            return FlextResult[tuple[str, dict[str, object]]].fail(
                f"Failed to build safe SELECT query: {e}"
            )

    def _build_select_base(
        self,
        table_name: str,
        columns: list[str] | None = None,
        schema_name: str | None = None,
    ) -> tuple[str, str]:
        """Build base components for SELECT queries."""
        # Build column list
        column_list = ", ".join(columns) if columns else "*"

        # Build full table name
        full_table_name = f"{schema_name}.{table_name}" if schema_name else table_name

        return column_list, full_table_name

    def convert_singer_type(
        self, singer_type: str | list[str], format_hint: str | None = None
    ) -> FlextResult[str]:
        """Convert Singer JSON Schema type to Oracle SQL type."""
        try:
            # Handle array types (e.g., ["string", "null"])
            if isinstance(singer_type, list):
                # Remove null and get the primary type
                non_null_types = [t for t in singer_type if t != "null"]
                if not non_null_types:
                    return FlextResult[str].ok("VARCHAR2(4000)")
                singer_type = non_null_types[0]

            # Convert based on Singer type
            type_mapping = {
                "string": "VARCHAR2(4000)",
                "integer": "NUMBER",
                "number": "NUMBER",
                "boolean": "NUMBER(1)",
                "array": "CLOB",
                "object": "CLOB",
            }

            # Check for format hints
            if format_hint:
                format_mapping = {
                    "date-time": "TIMESTAMP",
                    "date": "DATE",
                    "time": "TIMESTAMP",
                }
                if format_hint in format_mapping:
                    return FlextResult[str].ok(format_mapping[format_hint])

            # Default mapping
            oracle_type = type_mapping.get(singer_type, "VARCHAR2(4000)")
            return FlextResult[str].ok(oracle_type)

        except Exception as e:
            return FlextResult[str].fail(f"Type conversion failed: {e}")

    def _build_primary_key_query(
        self, table_name: str, schema_name: str | None = None
    ) -> tuple[str, dict[str, str]]:
        """Build query to get primary key columns for a table."""
        if schema_name:
            # Query for specific schema
            sql = """
            SELECT cc.column_name
            FROM all_cons_columns cc
            JOIN all_constraints c ON cc.constraint_name = c.constraint_name
            WHERE c.constraint_type = 'P'
            AND c.table_name = UPPER(:table_name)
            AND c.owner = UPPER(:schema_name)
            ORDER BY cc.position
            """
            params = {"table_name": table_name, "schema_name": schema_name}
        else:
            # Query for current user schema
            sql = """
            SELECT cc.column_name
            FROM user_cons_columns cc
            JOIN user_constraints c ON cc.constraint_name = c.constraint_name
            WHERE c.constraint_type = 'P'
            AND c.table_name = UPPER(:table_name)
            ORDER BY cc.position
            """
            params = {"table_name": table_name}

        return sql, params

    # =============================================================================
    # METADATA METHODS
    # =============================================================================

    def get_schemas(self) -> FlextResult[list[str]]:
        """Get list of Oracle schemas."""
        try:
            if not self._connected:
                return FlextResult[list[str]].fail("Not connected to database")

            sql = """
            SELECT username as schema_name
            FROM all_users
            WHERE username NOT IN ('SYS', 'SYSTEM', 'ANONYMOUS', 'XDB', 'CTXSYS', 'MDSYS', 'WMSYS')
            ORDER BY username
            """

            result = self.execute_query(sql)
            if not result.success:
                return FlextResult[list[str]].fail(
                    result.error or "Failed to get schemas"
                )

            schemas = [str(row["schema_name"]) for row in result.value]
            return FlextResult[list[str]].ok(schemas)

        except Exception as e:
            return FlextResult[list[str]].fail(f"Failed to get schemas: {e}")

    def get_tables(self, schema: str | None = None) -> FlextResult[list[str]]:
        """Get list of tables in Oracle schema."""
        try:
            if not self._connected:
                return FlextResult[list[str]].fail("Not connected to database")

            if schema:
                sql = """
                SELECT table_name
                FROM all_tables
                WHERE owner = UPPER(:schema_name)
                ORDER BY table_name
                """
                params = {"schema_name": schema}
            else:
                sql = """
                SELECT table_name
                FROM user_tables
                ORDER BY table_name
                """
                params = {}

            result = self.execute_query(sql, dict(params) if params else None)
            if not result.success:
                return FlextResult[list[str]].fail(
                    result.error or "Failed to get tables"
                )

            tables = [str(row["table_name"]) for row in result.value]
            return FlextResult[list[str]].ok(tables)

        except Exception as e:
            return FlextResult[list[str]].fail(f"Failed to get tables: {e}")

    def get_columns(
        self,
        table_name: str,
        schema_name: str | None = None,
    ) -> FlextResult[list[FlextDbOracleModels.Column]]:
        """Get column information for Oracle table."""
        try:
            if not self._connected:
                return FlextResult[list[FlextDbOracleModels.Column]].fail(
                    "Not connected to database"
                )

            if schema_name:
                sql = """
                SELECT column_name, data_type, data_length, data_precision, data_scale, nullable
                FROM all_tab_columns
                WHERE table_name = UPPER(:table_name) AND owner = UPPER(:schema_name)
                ORDER BY column_id
                """
                params = {"table_name": table_name, "schema_name": schema_name}
            else:
                sql = """
                SELECT column_name, data_type, data_length, data_precision, data_scale, nullable
                FROM user_tab_columns
                WHERE table_name = UPPER(:table_name)
                ORDER BY column_id
                """
                params = {"table_name": table_name}

            result = self.execute_query(sql, dict(params) if params else None)
            if not result.success:
                return FlextResult[list[FlextDbOracleModels.Column]].fail(
                    result.error or "Failed to get columns"
                )

            columns = []
            for row in result.value:
                column = FlextDbOracleModels.Column(
                    column_name=str(row["column_name"]),
                    data_type=str(row["data_type"]),
                    data_length=int(row["data_length"])
                    if (
                        row.get("data_length") is not None
                        and isinstance(row["data_length"], (int, str))
                    )
                    else None,
                    data_precision=int(row["data_precision"])
                    if (
                        row.get("data_precision") is not None
                        and isinstance(row["data_precision"], (int, str))
                    )
                    else None,
                    data_scale=int(row["data_scale"])
                    if (
                        row.get("data_scale") is not None
                        and isinstance(row["data_scale"], (int, str))
                    )
                    else None,
                    nullable=row["nullable"] == "Y",
                    column_id=1,  # Default value, could be populated from query
                    default_value=None,
                    comments=None,
                )
                columns.append(column)

            return FlextResult[list[FlextDbOracleModels.Column]].ok(columns)

        except Exception as e:
            return FlextResult[list[FlextDbOracleModels.Column]].fail(
                f"Failed to get columns: {e}"
            )

    def get_table_row_count(
        self,
        table_name: str,
        schema_name: str | None = None,
    ) -> FlextResult[int]:
        """Get row count for Oracle table."""
        try:
            if not self._connected:
                return FlextResult[int].fail("Not connected to database")

            # Use FlextUtilities for safe SQL identifier validation
            if not _is_safe_sql_identifier(table_name):
                return FlextResult[int].fail("Invalid table name")

            if schema_name and not _is_safe_sql_identifier(schema_name):
                return FlextResult[int].fail("Invalid schema name")

            if schema_name:
                sql = f"SELECT COUNT(*) as row_count FROM {schema_name}.{table_name}"  # noqa: S608 - Safe: identifiers validated
            else:
                sql = f"SELECT COUNT(*) as row_count FROM {table_name}"  # noqa: S608 - Safe: identifiers validated

            result = self.execute_query(sql)
            if not result.success:
                return FlextResult[int].fail(result.error or "Failed to get row count")

            if not result.value:
                count = 0
            else:
                count_value = result.value[0]["row_count"]
                # Safe conversion to int with type check
                count = (
                    int(count_value)
                    if (count_value is not None and isinstance(count_value, (int, str)))
                    else 0
                )
            return FlextResult[int].ok(count)

        except Exception as e:
            return FlextResult[int].fail(f"Failed to get row count: {e}")

    # =============================================================================
    # OBSERVABILITY METHODS
    # =============================================================================

    def get_connection_status(
        self,
    ) -> FlextResult[FlextDbOracleModels.ConnectionStatus]:
        """Get Oracle connection status."""
        try:
            status = FlextDbOracleModels.ConnectionStatus(
                is_connected=self._connected,
                connection_time=FlextUtilities.generate_timestamp() if self._connected else None,
                last_activity=FlextUtilities.generate_timestamp() if self._connected else None,
                session_id=None,  # Could be populated from Oracle session query
                host=self.config.host,
                port=self.config.port,
                service_name=self.config.service_name,
                username=self.config.username,
                version=None,  # Could be populated from Oracle version query
                error_message=None,
            )
            return FlextResult[FlextDbOracleModels.ConnectionStatus].ok(status)

        except Exception as e:
            return FlextResult[FlextDbOracleModels.ConnectionStatus].fail(
                f"Failed to get connection status: {e}"
            )

    def record_metric(
        self,
        name: str,
        value: float,
        tags: dict[str, str] | None = None,
    ) -> FlextResult[None]:
        """Record performance metric."""
        try:
            metric = {
                "name": name,
                "value": value,
                "tags": tags or {},
                "timestamp": datetime.now(UTC).isoformat(),
            }
            self._metrics[name] = metric
            return FlextResult[None].ok(None)

        except Exception as e:
            return FlextResult[None].fail(f"Failed to record metric: {e}")

    def get_metrics(self) -> FlextResult[dict[str, object]]:
        """Get recorded performance metrics."""
        return FlextResult[dict[str, object]].ok(self._metrics.copy())

    def health_check(self) -> FlextResult[dict[str, object]]:
        """Perform Oracle database health check."""
        try:
            health_info = {
                "service": "flext-db-oracle",
                "status": "healthy" if self._connected else "unhealthy",
                "timestamp": datetime.now(UTC).isoformat(),
                "database": {
                    "connected": self._connected,
                    "host": self.config.host,
                    "port": self.config.port,
                    "service_name": self.config.service_name,
                },
            }

            if self._connected:
                # Test connection
                test_result = self.test_connection()
                database_info = cast("dict[str, object]", health_info["database"])
                if test_result.success:
                    database_info["test_query"] = "passed"
                else:
                    health_info["status"] = "degraded"
                    database_info["test_query"] = "failed"

            # Cast to ensure type compatibility
            health_result = cast("dict[str, object]", health_info)
            return FlextResult[dict[str, object]].ok(health_result)

        except Exception as e:
            return FlextResult[dict[str, object]].fail(f"Health check failed: {e}")

    # =============================================================================
    # OPERATION TRACKING METHODS
    # =============================================================================

    def track_operation(
        self,
        operation: str,
        duration_ms: float,
        *,
        success: bool,
        metadata: dict[str, object] | None = None,
    ) -> FlextResult[str]:
        """Track database operation performance."""
        try:
            # Use standard hashlib for operation tracking
            import hashlib

            hash_input = f"{operation}_{datetime.now(UTC).isoformat()}"
            operation_id = hashlib.sha256(hash_input.encode()).hexdigest()[:16]

            operation_record = {
                "id": operation_id,
                "operation": operation,
                "duration_ms": duration_ms,
                "success": success,
                "timestamp": datetime.now(UTC).isoformat(),
                "metadata": metadata or {},
            }

            self._operations.append(operation_record)

            # Keep only last operations (limit to prevent memory growth)
            max_operations = 100
            if len(self._operations) > max_operations:
                self._operations = self._operations[-max_operations:]

            return FlextResult[str].ok(operation_id)

        except Exception as e:
            return FlextResult[str].fail(f"Failed to track operation: {e}")

    def get_operations(self) -> FlextResult[list[dict[str, object]]]:
        """Get tracked operations history."""
        return FlextResult[list[dict[str, object]]].ok(self._operations.copy())

    # =============================================================================
    # PLUGIN METHODS
    # =============================================================================

    def register_plugin(self, name: str, plugin: object) -> FlextResult[None]:
        """Register a plugin."""
        try:
            self._plugins[name] = plugin
            logger.info(f"Plugin '{name}' registered successfully")
            return FlextResult[None].ok(None)

        except Exception as e:
            return FlextResult[None].fail(f"Failed to register plugin '{name}': {e}")

    def unregister_plugin(self, name: str) -> FlextResult[None]:
        """Unregister a plugin."""
        try:
            if name in self._plugins:
                del self._plugins[name]
                logger.info(f"Plugin '{name}' unregistered successfully")
            return FlextResult[None].ok(None)

        except Exception as e:
            return FlextResult[None].fail(f"Failed to unregister plugin '{name}': {e}")

    def list_plugins(self) -> FlextResult[dict[str, object]]:
        """List all registered plugins."""
        try:
            if not self._plugins:
                return FlextResult[dict[str, object]].fail(
                    "plugin listing returned empty"
                )
            return FlextResult[dict[str, object]].ok(self._plugins.copy())

        except Exception as e:
            return FlextResult[dict[str, object]].fail(f"Failed to list plugins: {e}")

    def get_plugin(self, name: str) -> FlextResult[object]:
        """Get a specific plugin."""
        try:
            if name not in self._plugins:
                return FlextResult[object].fail(f"Plugin '{name}' not found")

            return FlextResult[object].ok(self._plugins[name])

        except Exception as e:
            return FlextResult[object].fail(f"Failed to get plugin '{name}': {e}")

    # =============================================================================
    # UTILITY METHODS
    # =============================================================================

    def generate_query_hash(
        self, sql: str, params: dict[str, object] | None = None
    ) -> FlextResult[str]:
        """Generate hash for SQL query caching using FlextDbOracleUtilities."""
        try:
            from flext_db_oracle.utilities import FlextDbOracleUtilities
            
            query_hash = FlextDbOracleUtilities.generate_query_hash(sql, params)
            return FlextResult[str].ok(query_hash)

        except Exception as e:
            return FlextResult[str].fail(f"Failed to generate query hash: {e}")

    def validate_table_name(self, table_name: str) -> FlextResult[bool]:
        """Validate Oracle table name."""
        try:
            # Oracle table name rules
            if (
                not table_name
                or len(table_name)
                > FlextDbOracleConstants.OracleValidation.MAX_TABLE_NAME_LENGTH
            ):
                return FlextResult[bool].ok(data=False)

            # Must start with letter
            if not table_name[0].isalpha():
                return FlextResult[bool].ok(data=False)

            # Only alphanumeric and underscore
            if (
                not table_name.replace("_", "")
                .replace("$", "")
                .replace("#", "")
                .isalnum()
            ):
                return FlextResult[bool].ok(data=False)

            return FlextResult[bool].ok(data=True)

        except Exception as e:
            return FlextResult[bool].fail(f"Table name validation failed: {e}")

    # =============================================================================
    # ADDITIONAL METHODS FOR TEST COMPATIBILITY
    # =============================================================================

    def _ensure_connected(self) -> FlextResult[None]:
        """Ensure database connection is established."""
        if not self._connected or not self._engine:
            return FlextResult[None].fail("Not connected to database")
        return FlextResult[None].ok(None)

    def execute(
        self, query: dict[str, object] | str | None = None
    ) -> FlextResult[dict[str, object]]:
        """Execute command - required by FlextDomainService."""
        try:
            if query is None:
                return FlextResult[dict[str, object]].fail(
                    "Query parameter is required"
                )

            # Handle both string and dict input
            if isinstance(query, str):
                sql = query
                params_dict = None
            else:
                sql = str(query.get("sql", ""))
                params = query.get("params")
                params_dict = dict(params) if isinstance(params, dict) else None

            result = self.execute_query(sql, params_dict)
            if not result.success:
                return FlextResult[dict[str, object]].fail(
                    result.error or "Execution failed"
                )

            # Return first row as dict or empty dict
            rows = result.value
            return FlextResult[dict[str, object]].ok(rows[0] if rows else {})

        except Exception as e:
            return FlextResult[dict[str, object]].fail(f"Execute failed: {e}")

    def execute_sql(
        self, sql: str, params: dict[str, object] | None = None
    ) -> FlextResult[list[dict[str, object]]]:
        """Execute SQL - renamed to avoid override conflict."""
        return self.execute_query(sql, params)

    def execute_many(
        self, sql: str, params_list: list[dict[str, object]]
    ) -> FlextResult[int]:
        """Execute SQL statement multiple times with different parameters."""
        try:
            if not self._connected or not self._engine:
                return FlextResult[int].fail("Not connected to database")

            total_affected = 0
            with self._engine.connect() as conn:
                for params in params_list:
                    result = conn.execute(text(sql), params)
                    total_affected += result.rowcount

            return FlextResult[int].ok(total_affected)

        except Exception as e:
            return FlextResult[int].fail(f"Bulk execution failed: {e}")

    def fetch_one(
        self, sql: str, params: dict[str, object] | None = None
    ) -> FlextResult[dict[str, object] | None]:
        """Execute query and return first result."""
        try:
            result = self.execute_query(sql, dict(params) if params else None)
            if not result.success:
                return FlextResult[dict[str, object] | None].fail(
                    result.error or "Query failed"
                )

            rows = result.value
            if not rows:
                return FlextResult[dict[str, object] | None].ok(None)

            return FlextResult[dict[str, object] | None].ok(rows[0])

        except Exception as e:
            return FlextResult[dict[str, object] | None].fail(f"Fetch one failed: {e}")

    def close(self) -> FlextResult[None]:
        """Close connection - direct implementation to avoid wrapping issues."""
        try:
            if self._engine:
                self._engine.dispose()
                self._engine = None
                self._session_factory = None
                self._connected = False
                logger.info("Oracle connection closed")
            return FlextResult[None].ok(None)
        except Exception as e:
            return FlextResult[None].fail(f"Close failed: {e}")

    def _build_column_info_query(
        self, table_name: str, schema_name: str | None = None
    ) -> tuple[str, dict[str, str]]:
        """Build query to get column information for a table."""
        if schema_name:
            sql = """
            SELECT column_name, data_type, nullable, data_length,
                   data_precision, data_scale, column_id
            FROM all_tab_columns
            WHERE table_name = UPPER(:table_name) AND owner = UPPER(:schema_name)
            ORDER BY column_id
            """
            params = {"table_name": table_name, "schema_name": schema_name}
        else:
            sql = """
            SELECT column_name, data_type, nullable, data_length,
                   data_precision, data_scale, column_id
            FROM user_tab_columns
            WHERE table_name = UPPER(:table_name)
            ORDER BY column_id
            """
            params = {"table_name": table_name}

        return sql, params

    def _convert_column_row_to_dict(self, row_data: list[object]) -> dict[str, object]:
        """Convert column row data to dictionary."""
        if (
            len(row_data)
            < FlextDbOracleConstants.OracleValidation.COLUMN_METADATA_FIELD_COUNT
        ):
            # Pad with None values if needed
            row_data = list(row_data) + [None] * (
                FlextDbOracleConstants.OracleValidation.COLUMN_METADATA_FIELD_COUNT
                - len(row_data)
            )

        return {
            "column_name": row_data[0],
            "data_type": row_data[1],
            "nullable": row_data[2] == "Y" if row_data[2] else True,
            "data_length": row_data[3],
            "data_precision": row_data[4],
            "data_scale": row_data[5],
            "column_id": row_data[6],
        }

    def get_primary_key_columns(
        self, table_name: str, schema_name: str | None = None
    ) -> FlextResult[list[str]]:
        """Get primary key columns for a table."""
        try:
            if not self._connected:
                return FlextResult[list[str]].fail("Not connected to database")

            sql, params = self._build_primary_key_query(table_name, schema_name)
            result = self.execute_query(sql, dict(params) if params else None)

            if not result.success:
                return FlextResult[list[str]].fail(
                    result.error or "Failed to get primary keys"
                )

            pk_columns = [str(row["column_name"]) for row in result.value]
            return FlextResult[list[str]].ok(pk_columns)

        except Exception as e:
            return FlextResult[list[str]].fail(
                f"Failed to get primary key columns: {e}"
            )

    def _build_table_name(self, table_name: str, schema_name: str | None = None) -> str:
        """Build full table name with optional schema."""
        if schema_name:
            return f"{schema_name}.{table_name}"
        return table_name

    def _build_column_definition(
        self, column_def: dict[str, object]
    ) -> FlextResult[str]:
        """Build column definition for DDL."""
        try:
            name = column_def["name"]
            data_type = column_def["data_type"]

            definition = f"{name} {data_type}"

            if not column_def.get("nullable", True):
                definition += " NOT NULL"

            return FlextResult[str].ok(definition)

        except Exception as e:
            return FlextResult[str].fail(f"Failed to build column definition: {e}")

    def create_table_ddl(
        self,
        table_name: str,
        columns: list[dict[str, object]],
        schema_name: str | None = None,
    ) -> FlextResult[str]:
        """Generate CREATE TABLE DDL statement."""
        try:
            full_table_name = self._build_table_name(table_name, schema_name)

            column_defs = []
            primary_keys = []

            for col in columns:
                col_def_result = self._build_column_definition(col)
                if not col_def_result.success:
                    return FlextResult[str].fail(
                        col_def_result.error or "Column definition failed"
                    )

                column_defs.append(col_def_result.value)

                if col.get("primary_key", False):
                    primary_keys.append(col["name"])

            ddl = f"CREATE TABLE {full_table_name} (\n  {', '.join(column_defs)}"

            if primary_keys:
                # Ensure primary_keys contains strings for join operation
                str_primary_keys = [str(key) for key in primary_keys]
                ddl += f",\n  PRIMARY KEY ({', '.join(str_primary_keys)})"

            ddl += "\n)"

            return FlextResult[str].ok(ddl)

        except Exception as e:
            return FlextResult[str].fail(f"Failed to create table DDL: {e}")

    def drop_table_ddl(
        self, table_name: str, schema_name: str | None = None
    ) -> FlextResult[str]:
        """Generate DROP TABLE DDL statement."""
        try:
            full_table_name = self._build_table_name(table_name, schema_name)
            ddl = f"DROP TABLE {full_table_name}"
            return FlextResult[str].ok(ddl)
        except Exception as e:
            return FlextResult[str].fail(f"Failed to create drop table DDL: {e}")

    def map_singer_schema(
        self, singer_schema: dict[str, object]
    ) -> FlextResult[dict[str, str]]:
        """Map Singer JSON schema to Oracle column types."""
        try:
            mapping = {}
            # Type-safe access to properties - singer_schema is already guaranteed to be dict[str, object]
            properties = singer_schema.get("properties", {})
            if not isinstance(properties, dict):
                return FlextResult[dict[str, str]].fail("Invalid properties format")

            for field_name, field_def in properties.items():
                if not isinstance(field_def, dict):
                    continue
                field_type = field_def.get("type")
                field_format = field_def.get("format")

                # Type-safe conversion with default fallback
                if field_type is not None:
                    conversion_result = self.convert_singer_type(
                        field_type, field_format
                    )
                else:
                    conversion_result = FlextResult[str].ok("VARCHAR2(4000)")
                if conversion_result.success:
                    mapping[field_name] = conversion_result.value
                else:
                    mapping[field_name] = "VARCHAR2(4000)"  # Default fallback

            return FlextResult[dict[str, str]].ok(mapping)

        except Exception as e:
            return FlextResult[dict[str, str]].fail(f"Schema mapping failed: {e}")

    def build_insert_statement(
        self,
        table_name: str,
        columns: list[str],
        schema_name: str | None = None,
        returning_columns: list[str] | None = None,
    ) -> FlextResult[str]:
        """Build INSERT statement."""
        try:
            full_table_name = self._build_table_name(table_name, schema_name)

            # Validate all column names to prevent SQL injection
            for col in columns:
                if not _is_safe_sql_identifier(col):
                    return FlextResult[str].fail(f"Invalid column name: {col}")
            if returning_columns:
                for col in returning_columns:
                    if not _is_safe_sql_identifier(col):
                        return FlextResult[str].fail(f"Invalid RETURNING column name: {col}")

            column_list = ", ".join(columns)
            value_placeholders = ", ".join(f":{col}" for col in columns)

            sql = f"INSERT INTO {full_table_name} ({column_list}) VALUES ({value_placeholders})"  # noqa: S608 - Safe: all identifiers validated

            if returning_columns:
                sql += f" RETURNING {', '.join(returning_columns)}"

            return FlextResult[str].ok(sql)

        except Exception as e:
            return FlextResult[str].fail(f"Failed to build INSERT statement: {e}")

    def build_update_statement(
        self,
        table_name: str,
        set_columns: list[str],
        where_columns: list[str],
        schema_name: str | None = None,
    ) -> FlextResult[str]:
        """Build UPDATE statement."""
        try:
            full_table_name = self._build_table_name(table_name, schema_name)

            # Validate all column names to prevent SQL injection
            for col in set_columns:
                if not _is_safe_sql_identifier(col):
                    return FlextResult[str].fail(f"Invalid SET column name: {col}")
            for col in where_columns:
                if not _is_safe_sql_identifier(col):
                    return FlextResult[str].fail(f"Invalid WHERE column name: {col}")

            set_clauses = [f"{col} = :{col}" for col in set_columns]
            where_clauses = [f"{col} = :where_{col}" for col in where_columns]

            sql = f"UPDATE {full_table_name} SET {', '.join(set_clauses)} WHERE {' AND '.join(where_clauses)}"  # noqa: S608 - Safe: all identifiers validated

            return FlextResult[str].ok(sql)

        except Exception as e:
            return FlextResult[str].fail(f"Failed to build UPDATE statement: {e}")

    def build_delete_statement(
        self, table_name: str, where_columns: list[str], schema_name: str | None = None
    ) -> FlextResult[str]:
        """Build DELETE statement."""
        try:
            full_table_name = self._build_table_name(table_name, schema_name)

            # Validate all column names to prevent SQL injection
            for col in where_columns:
                if not _is_safe_sql_identifier(col):
                    return FlextResult[str].fail(f"Invalid WHERE column name: {col}")

            where_clauses = [f"{col} = :{col}" for col in where_columns]

            sql = f"DELETE FROM {full_table_name} WHERE {' AND '.join(where_clauses)}"  # noqa: S608 - Safe: all identifiers validated

            return FlextResult[str].ok(sql)

        except Exception as e:
            return FlextResult[str].fail(f"Failed to build DELETE statement: {e}")

    def build_merge_statement(self, config: object) -> FlextResult[str]:
        """Build MERGE statement from configuration."""
        try:
            # Extract config attributes safely
            target_table = getattr(config, "target_table", "")
            source_columns = getattr(config, "source_columns", [])
            merge_keys = getattr(config, "merge_keys", [])
            schema_name = getattr(config, "schema_name", None)

            full_table_name = self._build_table_name(target_table, schema_name)

            # Validate ALL column names to prevent SQL injection
            for col in source_columns:
                if not _is_safe_sql_identifier(col):
                    return FlextResult[str].fail(f"Invalid source column name: {col}")
            for key in merge_keys:
                if not _is_safe_sql_identifier(key):
                    return FlextResult[str].fail(f"Invalid merge key column name: {key}")

            # Build source SELECT
            source_select = f"SELECT {', '.join(f':{col} as {col}' for col in source_columns)} FROM dual"  # noqa: S608 - Safe: all column names validated

            # Build merge conditions
            merge_conditions = [f"tgt.{key} = src.{key}" for key in merge_keys]

            # Build update and insert clauses
            non_key_columns = [col for col in source_columns if col not in merge_keys]
            update_set = [f"{col} = src.{col}" for col in non_key_columns]
            insert_columns = ", ".join(source_columns)
            insert_values = ", ".join(f"src.{col}" for col in source_columns)

            # SQL generation is safe - uses parameterized queries
            sql = f"""MERGE INTO {full_table_name} tgt
USING ({source_select}) src
ON ({" AND ".join(merge_conditions)})
WHEN MATCHED THEN
  UPDATE SET {", ".join(update_set)}
WHEN NOT MATCHED THEN
  INSERT ({insert_columns})
  VALUES ({insert_values})"""  # noqa: S608 - Safe: all column names validated

            return FlextResult[str].ok(sql)

        except Exception as e:
            return FlextResult[str].fail(f"Failed to build MERGE statement: {e}")

    def build_create_index_statement(self, config: object) -> FlextResult[str]:
        """Build CREATE INDEX statement from configuration."""
        try:
            # Extract config attributes safely
            index_name = getattr(config, "index_name", "")
            table_name = getattr(config, "table_name", "")
            columns = getattr(config, "columns", [])
            schema_name = getattr(config, "schema_name", None)
            unique = getattr(config, "unique", False)
            tablespace = getattr(config, "tablespace", None)
            parallel = getattr(config, "parallel", None)

            # Validate ALL column names to prevent SQL injection
            for col in columns:
                if not _is_safe_sql_identifier(col):
                    return FlextResult[str].fail(f"Invalid column name: {col}")
            if tablespace and not _is_safe_sql_identifier(tablespace):
                return FlextResult[str].fail(f"Invalid tablespace name: {tablespace}")

            full_table_name = self._build_table_name(table_name, schema_name)
            full_index_name = self._build_table_name(index_name, schema_name)

            sql = "CREATE"
            if unique:
                sql += " UNIQUE"

            sql += (
                f" INDEX {full_index_name} ON {full_table_name} ({', '.join(columns)})"
            )

            if tablespace:
                sql += f" TABLESPACE {tablespace}"

            if parallel:
                sql += f" PARALLEL {parallel}"

            return FlextResult[str].ok(sql)

        except Exception as e:
            return FlextResult[str].fail(f"Failed to build CREATE INDEX statement: {e}")


# Export the single class following flext-core pattern
__all__ = ["FlextDbOracleServices"]
