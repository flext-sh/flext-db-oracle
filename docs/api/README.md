# FLEXT DB Oracle API Reference

**Complete API documentation for enterprise Oracle database integration**

This comprehensive API reference covers all public interfaces, classes, and methods provided by FLEXT DB Oracle. The API follows Clean Architecture principles and integrates seamlessly with FLEXT Core patterns.

## 🎯 API Overview

### **Core Components**

FLEXT DB Oracle provides a layered API structure following Clean Architecture:

```
┌─────────────────────────────────────────────────────────────────┐
│                      PUBLIC API SURFACE                         │
├─────────────────────────────────────────────────────────────────┤
│ FlextDbOracleApi        │ Main application service             │
│ FlextDbOracleConfig     │ Configuration management             │
│ FlextDbOracleConnection │ Connection handling                  │
│ FlextDbOracleMetadata*  │ Schema introspection                 │
│ FlextDbOraclePlugin*    │ Plugin system                        │
│ FlextDbOracleTypes      │ Type definitions                     │
├═════════════════════════════════════════════════════════════════┤
│                         FLEXT CORE                              │
│ FlextResult[T]          │ Type-safe error handling             │
│ FlextContainer          │ Dependency injection                 │
│ FlextLogger             │ Structured logging                   │
└─────────────────────────────────────────────────────────────────┘
```

### **Import Patterns**

```python
# Primary imports
from flext_db_oracle import (
    FlextDbOracleApi,
    FlextDbOracleConfig,
    FlextDbOracleConnection
)

# Metadata operations
from flext_db_oracle import (
    FlextDbOracleMetadataManager,
    FlextDbOracleSchema,
    FlextDbOracleTable,
    FlextDbOracleColumn
)

# Plugin system
from flext_db_oracle.plugins import (
    register_all_oracle_plugins,
    create_data_validation_plugin,
    create_performance_monitor_plugin
)

# Type definitions
from flext_db_oracle.types import (
    TDbOracleQueryResult,
    TDbOracleConnectionStatus,
    TDbOracleSchema
)

# FLEXT Core integration
from flext_core import FlextResult, get_flext_container
```

## 🔧 Core API Classes

### **FlextDbOracleApi**

The main application service providing high-level Oracle database operations.

```python
class FlextDbOracleApi:
    """Main Oracle database API with features.

    This class serves as the primary entry point for Oracle database operations,
    providing a clean, type-safe interface that integrates with FLEXT Core patterns.

    Example:
        >>> config = FlextDbOracleConfig.from_env().value
        >>> api = FlextDbOracleApi(config)
        >>> connect_result = api.connect()
        >>> if connect_result.success:
        ...     query_result = api.execute_query("SELECT * FROM employees")
    """

    def __init__(
        self,
        config: FlextDbOracleConfig,
        container: Optional[FlextContainer] = None
    ) -> None:
        """Initialize Oracle API with configuration.

        Args:
            config: Oracle database configuration
            container: Optional dependency injection container

        Raises:
            ValueError: If configuration is invalid
        """

    def connect(self) -> FlextResult[None]:
        """Establish connection to Oracle database.

        Creates a connection pool and validates connectivity.

        Returns:
            FlextResult[None]: Success indicator or error details

        Example:
            >>> api = FlextDbOracleApi(config)
            >>> result = api.connect()
            >>> if result.success:
            ...     print("Connected successfully")
            ... else:
            ...     print(f"Connection failed: {result.error}")
        """

    def disconnect(self) -> FlextResult[None]:
        """Close Oracle database connections.

        Gracefully closes all connections in the pool.

        Returns:
            FlextResult[None]: Success indicator or error details
        """

    def execute_query(
        self,
        sql: str,
        params: Optional[Dict[str, object]] = None
    ) -> FlextResult[TDbOracleQueryResult]:
        """Execute SQL query with parameterized values.

        Args:
            sql: SQL query string (use :param_name for parameters)
            params: Optional parameter dictionary

        Returns:
            FlextResult[TDbOracleQueryResult]: Query results or error

        Example:
            >>> result = api.execute_query(
            ...     "SELECT * FROM employees WHERE department_id = :dept_id",
            ...     {"dept_id": 10}
            ... )
            >>> if result.success:
            ...     for row in result.value.rows:
            ...         print(row)
        """

    def execute_ddl(self, ddl: str) -> FlextResult[None]:
        """Execute DDL statement (CREATE, ALTER, DROP).

        Args:
            ddl: DDL statement string

        Returns:
            FlextResult[None]: Success indicator or error details

        Example:
            >>> ddl = "CREATE TABLE test_table (id NUMBER, name VARCHAR2(100))"
            >>> result = api.execute_ddl(ddl)
            >>> if result.success:
            ...     print("Table created successfully")
        """

    def bulk_insert(
        self,
        schema: str,
        table: str,
        columns: List[str],
        values: List[List[object]],
        batch_size: int = 10000
    ) -> FlextResult[int]:
        """Perform bulk insert operation with Oracle optimizations.

        Args:
            schema: Target schema name
            table: Target table name
            columns: Column names list
            values: List of value rows
            batch_size: Batch size for bulk operations

        Returns:
            FlextResult[int]: Number of rows inserted or error

        Example:
            >>> result = api.bulk_insert(
            ...     schema="HR",
            ...     table="EMPLOYEES",
            ...     columns=["ID", "NAME", "SALARY"],
            ...     values=[[1, "John", 50000], [2, "Jane", 60000]]
            ... )
            >>> if result.success:
            ...     print(f"Inserted {result.value} rows")
        """

    def get_schema_metadata(self, schema: str) -> FlextResult[TDbOracleSchema]:
        """Extract complete schema metadata.

        Args:
            schema: Schema name to introspect

        Returns:
            FlextResult[TDbOracleSchema]: Schema metadata or error

        Example:
            >>> result = api.get_schema_metadata("HR")
            >>> if result.success:
            ...     schema = result.value
            ...     print(f"Schema has {len(schema.tables)} tables")
        """

    def table_exists(self, schema: str, table: str) -> FlextResult[bool]:
        """Check if table exists in schema.

        Args:
            schema: Schema name
            table: Table name

        Returns:
            FlextResult[bool]: True if table exists, False otherwise
        """

    def get_connection_status(self) -> FlextResult[TDbOracleConnectionStatus]:
        """Get current connection pool status.

        Returns:
            FlextResult[TDbOracleConnectionStatus]: Connection status details
        """

    # Factory Methods
    @classmethod
    def from_env(cls, context_name: str = "default") -> 'FlextDbOracleApi':
        """Create API instance from environment variables.

        Args:
            context_name: Context name for logging and identification

        Returns:
            FlextDbOracleApi: Configured API instance

        Raises:
            RuntimeError: If configuration loading fails

        Example:
            >>> api = FlextDbOracleApi.from_env("my_app")
            >>> connect_result = api.connect()
        """

    @classmethod
    def from_url(cls, url: str, context_name: str = "default") -> 'FlextDbOracleApi':
        """Create API instance from connection URL.

        Args:
            url: Oracle connection URL (oracle://user:pass@host:port/service)
            context_name: Context name for logging

        Returns:
            FlextDbOracleApi: Configured API instance

        Example:
            >>> api = FlextDbOracleApi.from_url(
            ...     "oracle://user:pass@localhost:1521/XE"
            ... )
        """
```

### **FlextDbOracleConfig**

Configuration class with validation and multiple loading sources.

```python
class FlextDbOracleConfig(BaseSettings):
    """Oracle database configuration with comprehensive validation.

    Supports loading from environment variables, direct construction,
    and URL parsing with full type safety and validation.
    """

    # Required connection parameters
    host: str = Field(..., description="Oracle server hostname")
    port: int = Field(1521, description="Oracle port number")
    service_name: Optional[str] = Field(None, description="Oracle service name")
    sid: Optional[str] = Field(None, description="Oracle SID")
    username: str = Field(..., description="Oracle username")
    password: SecretStr = Field(..., description="Oracle password")

    # Optional parameters
    schema: Optional[str] = Field(None, description="Default schema")
    encoding: str = Field("UTF-8", description="Character encoding")
    timeout: int = Field(30, description="Connection timeout in seconds")
    autocommit: bool = Field(False, description="Enable autocommit")

    # Connection pool parameters
    pool_min: int = Field(1, description="Minimum pool size")
    pool_max: int = Field(10, description="Maximum pool size")
    pool_increment: int = Field(1, description="Pool size increment")

    # SSL/TLS parameters
    ssl_cert_path: Optional[str] = Field(None, description="SSL certificate path")
    ssl_key_path: Optional[str] = Field(None, description="SSL private key path")
    ssl_server_dn_match: bool = Field(True, description="Verify server DN")
    ssl_server_cert_dn: Optional[str] = Field(None, description="Expected server DN")
    protocol: str = Field("tcp", description="Connection protocol")

    # Validation methods
    @field_validator('port')
    @classmethod
    def validate_port(cls, v: int) -> int:
        """Validate port number range."""
        if not 1024 <= v <= 65535:
            raise ValueError('Port must be between 1024 and 65535')
        return v

    @field_validator('pool_max')
    @classmethod
    def validate_pool_max(cls, v: int, info: ValidationInfo) -> int:
        """Validate pool_max >= pool_min."""
        if 'pool_min' in info.data and v < info.data['pool_min']:
            raise ValueError('pool_max must be >= pool_min')
        return v

    @model_validator(mode='after')
    def validate_service_or_sid(self) -> 'FlextDbOracleConfig':
        """Validate that either service_name or sid is provided."""
        if not self.service_name and not self.sid:
            raise ValueError('Either service_name or sid must be provided')
        return self

    # Factory methods
    @classmethod
    def from_env(cls, prefix: str = "FLEXT_TARGET_ORACLE_") -> FlextResult['FlextDbOracleConfig']:
        """Load configuration from environment variables.

        Args:
            prefix: Environment variable prefix

        Returns:
            FlextResult[FlextDbOracleConfig]: Configuration or error

        Example:
            >>> config_result = FlextDbOracleConfig.from_env()
            >>> if config_result.success:
            ...     config = config_result.value
        """

    @classmethod
    def from_url(cls, url: str) -> FlextResult['FlextDbOracleConfig']:
        """Parse configuration from URL string.

        Args:
            url: Connection URL (oracle://user:pass@host:port/service)

        Returns:
            FlextResult[FlextDbOracleConfig]: Configuration or error

        Example:
            >>> config_result = FlextDbOracleConfig.from_url(
            ...     "oracle://user:pass@localhost:1521/XE"
            ... )
        """

    # Utility methods
    def get_dsn(self) -> str:
        """Get Oracle Data Source Name string."""
        if self.service_name:
            return f"{self.host}:{self.port}/{self.service_name}"
        else:
            return f"{self.host}:{self.port}:{self.sid}"

    def to_connection_params(self) -> Dict[str, object]:
        """Convert to Oracle connection parameters dictionary."""
        params = {
            "user": self.username,
            "password": self.password.get_secret_value(),
            "dsn": self.get_dsn(),
            "encoding": self.encoding,
            "autocommit": self.autocommit
        }

        # Add SSL parameters if configured
        if self.protocol == "tcps":
            params["ssl_context"] = True

        return params

    @property
    def ssl_enabled(self) -> bool:
        """Check if SSL/TLS is enabled."""
        return self.protocol == "tcps" or bool(self.ssl_cert_path)
```

### **FlextDbOracleConnection**

Low-level connection management with pooling and resource management.

```python
class FlextDbOracleConnection:
    """Oracle database connection manager with enterprise features.

    Provides connection pooling, health monitoring, and resource management
    for Oracle database connectivity.
    """

    def __init__(self, config: FlextDbOracleConfig) -> None:
        """Initialize connection manager.

        Args:
            config: Oracle database configuration
        """

    def create_pool(self) -> FlextResult[None]:
        """Create Oracle connection pool.

        Returns:
            FlextResult[None]: Success indicator or error details
        """

    def get_connection(self) -> FlextResult[object]:
        """Get connection from pool.

        Returns:
            FlextResult[Connection]: Oracle connection or error
        """

    def return_connection(self, connection: object) -> FlextResult[None]:
        """Return connection to pool.

        Args:
            connection: Oracle connection to return

        Returns:
            FlextResult[None]: Success indicator or error
        """

    def execute_query(
        self,
        sql: str,
        params: Optional[Dict[str, object]] = None
    ) -> FlextResult[object]:
        """Execute SQL query using pooled connection.

        Args:
            sql: SQL query string
            params: Optional query parameters

        Returns:
            FlextResult[Cursor]: Query cursor or error
        """

    def close(self) -> FlextResult[None]:
        """Close all connections and pool.

        Returns:
            FlextResult[None]: Success indicator or error
        """

    def get_pool_status(self) -> FlextResult[Dict[str, object]]:
        """Get connection pool status information.

        Returns:
            FlextResult[Dict]: Pool status details or error
        """

    def health_check(self) -> FlextResult[bool]:
        """Perform connection health check.

        Returns:
            FlextResult[bool]: True if healthy, False otherwise
        """
```

## 📊 Metadata API

### **FlextDbOracleMetadataManager**

Schema introspection and metadata operations.

```python
class FlextDbOracleMetadataManager:
    """Oracle metadata manager for schema introspection.

    Provides comprehensive Oracle schema analysis and DDL generation
    capabilities with support for tables, views, indexes, and constraints.
    """

    def __init__(self, connection: FlextDbOracleConnection) -> None:
        """Initialize metadata manager.

        Args:
            connection: Oracle connection manager
        """

    def get_schema_metadata(self, schema: str) -> FlextResult[TDbOracleSchema]:
        """Extract complete schema metadata.

        Args:
            schema: Schema name to analyze

        Returns:
            FlextResult[TDbOracleSchema]: Schema metadata or error
        """

    def get_table_metadata(
        self,
        schema: str,
        table: str
    ) -> FlextResult[TDbOracleTable]:
        """Get detailed table metadata.

        Args:
            schema: Schema name
            table: Table name

        Returns:
            FlextResult[TDbOracleTable]: Table metadata or error
        """

    def generate_table_ddl(
        self,
        schema: str,
        table: str
    ) -> FlextResult[str]:
        """Generate CREATE TABLE DDL statement.

        Args:
            schema: Schema name
            table: Table name

        Returns:
            FlextResult[str]: DDL statement or error
        """

    def analyze_table_dependencies(
        self,
        schema: str
    ) -> FlextResult[Dict[str, List[str]]]:
        """Analyze table dependencies within schema.

        Args:
            schema: Schema name to analyze

        Returns:
            FlextResult[Dict]: Dependency mapping or error
        """

    def get_column_statistics(
        self,
        schema: str,
        table: str,
        column: str
    ) -> FlextResult[Dict[str, object]]:
        """Get column statistics for query optimization.

        Args:
            schema: Schema name
            table: Table name
            column: Column name

        Returns:
            FlextResult[Dict]: Column statistics or error
        """
```

## 🔌 Plugin API

### **Plugin Registration**

```python
def register_all_oracle_plugins(
    plugin_manager: object
) -> FlextResult[None]:
    """Register all built-in Oracle plugins.

    Args:
        plugin_manager: Plugin manager instance

    Returns:
        FlextResult[None]: Success indicator or error
    """

def create_data_validation_plugin(
    validation_rules: Dict[str, object]
) -> FlextResult[object]:
    """Create data validation plugin with custom rules.

    Args:
        validation_rules: Validation rule configuration

    Returns:
        FlextResult[Plugin]: Plugin instance or error
    """

def create_performance_monitor_plugin(
    monitoring_config: Dict[str, object]
) -> FlextResult[object]:
    """Create performance monitoring plugin.

    Args:
        monitoring_config: Monitoring configuration

    Returns:
        FlextResult[Plugin]: Plugin instance or error
    """

def create_security_audit_plugin(
    audit_config: Dict[str, object]
) -> FlextResult[object]:
    """Create security audit plugin.

    Args:
        audit_config: Audit configuration

    Returns:
        FlextResult[Plugin]: Plugin instance or error
    """
```

### **Custom Plugin Interface**

```python
from typing import Protocol
from flext_core import FlextResult

class IOraclePlugin(Protocol):
    """Interface for Oracle plugins."""

    def supports(self, operation: str) -> bool:
        """Check if plugin supports the operation.

        Args:
            operation: Operation name

        Returns:
            bool: True if supported
        """

    def execute(
        self,
        context: Dict[str, object]
    ) -> FlextResult[object]:
        """Execute plugin logic.

        Args:
            context: Operation context

        Returns:
            FlextResult[object]: Plugin result or error
        """

    def get_name(self) -> str:
        """Get plugin name."""

    def get_version(self) -> str:
        """Get plugin version."""
```

## 📋 Type Definitions

### **Core Types**

```python
from typing import TypedDict, List, Optional
from pydantic import BaseModel

class TDbOracleQueryResult(BaseModel):
    """Oracle query result type."""
    rows: List[tuple]
    columns: List[str]
    row_count: int
    execution_time_ms: float

class TDbOracleConnectionStatus(BaseModel):
    """Oracle connection status type."""
    is_connected: bool
    pool_size: int
    active_connections: int
    available_connections: int
    total_connections_created: int

class TDbOracleColumn(BaseModel):
    """Oracle column metadata type."""
    name: str
    data_type: str
    data_length: Optional[int]
    data_precision: Optional[int]
    data_scale: Optional[int]
    nullable: bool
    default_value: Optional[str]

class TDbOracleTable(BaseModel):
    """Oracle table metadata type."""
    name: str
    schema: str
    columns: List[TDbOracleColumn]
    row_count: Optional[int]
    size_mb: Optional[float]
    last_analyzed: Optional[str]

class TDbOracleSchema(BaseModel):
    """Oracle schema metadata type."""
    name: str
    tables: List[TDbOracleTable]
    views: List[dict]
    sequences: List[dict]
    procedures: List[dict]
```

## 🎯 Usage Examples

### **Basic Usage Pattern**

```python
from flext_db_oracle import FlextDbOracleApi, FlextDbOracleConfig
from flext_core import FlextResult

# Configure and connect
config = FlextDbOracleConfig.from_env().value
api = FlextDbOracleApi(config)

# Connect with error handling
connect_result = api.connect()
if connect_result.is_failure:
    print(f"Connection failed: {connect_result.error}")
    exit(1)

# Execute queries
query_result = api.execute_query(
    "SELECT employee_id, name, salary FROM employees WHERE department_id = :dept",
    {"dept": 10}
)

if query_result.success:
    for row in query_result.value.rows:
        print(f"Employee: {row}")
else:
    print(f"Query failed: {query_result.error}")

# Clean up
api.disconnect()
```

### **Advanced Usage with Metadata**

```python
from flext_db_oracle import FlextDbOracleApi, FlextDbOracleMetadataManager

# Initialize API
api = FlextDbOracleApi.from_env()
api.connect()

# Get metadata manager
metadata_manager = FlextDbOracleMetadataManager(api.connection)

# Analyze schema
schema_result = metadata_manager.get_schema_metadata("HR")
if schema_result.success:
    schema = schema_result.value

    print(f"Schema {schema.name} contains:")
    for table in schema.tables:
        print(f"  Table: {table.name} ({len(table.columns)} columns)")

    # Generate DDL for a specific table
    ddl_result = metadata_manager.generate_table_ddl("HR", "EMPLOYEES")
    if ddl_result.success:
        print(f"DDL:\n{ddl_result.value}")
```

### **Plugin Usage**

```python
from flext_db_oracle.plugins import register_all_oracle_plugins

# Initialize API with plugins
api = FlextDbOracleApi.from_env()
api.connect()

# Register all built-in plugins
register_result = register_all_oracle_plugins(api.plugin_manager)
if register_result.success:
    print("Plugins registered successfully")

# Execute operation with plugins
validation_result = api.execute_with_plugins("data_validation", {
    "table": "employees",
    "schema": "hr",
    "validation_rules": ["not_null", "foreign_key"]
})

if validation_result.success:
    print("Data validation passed")
else:
    print(f"Validation failed: {validation_result.error}")
```

## 🔍 Error Handling

### **FlextResult Pattern**

All API methods return `FlextResult[T]` for consistent error handling:

```python
# Check for success/failure
result = api.execute_query("SELECT * FROM employees")
if result.success:
    data = result.value
    print(f"Retrieved {len(data.rows)} rows")
else:
    error = result.error
    print(f"Query failed: {error}")

# Pattern matching (Python 3.10+)
match result:
    case FlextResult(success=True, value=data):
        print(f"Success: {len(data.rows)} rows")
    case FlextResult(success=False, error=error):
        print(f"Error: {error}")

# Chaining operations
config_result = FlextDbOracleConfig.from_env()
if config_result.success:
    api = FlextDbOracleApi(config_result.value)
    connect_result = api.connect()
    if connect_result.success:
        # Proceed with operations
        pass
```

### **Common Error Types**

- **Configuration Errors**: Invalid configuration parameters
- **Connection Errors**: Network or authentication failures
- **Query Errors**: SQL syntax or execution errors
- **Permission Errors**: Insufficient database privileges
- **Resource Errors**: Connection pool exhaustion or timeout

---

This API reference provides complete documentation for all public interfaces in FLEXT DB Oracle, enabling developers to build robust Oracle database integrations with confidence.
