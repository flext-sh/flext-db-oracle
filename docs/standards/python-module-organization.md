# Python Module Organization & Semantic Patterns

**FLEXT DB Oracle Module Architecture & Enterprise Oracle Integration Standards**

---

## 🏗️ **Module Architecture Overview**

FLEXT DB Oracle implements a **specialized Clean Architecture** for Oracle database integration, building on FLEXT Core patterns while providing Oracle-specific enterprise capabilities. This architecture serves as the template for all Oracle-related projects in the FLEXT ecosystem.

### **Core Design Principles**

1. **Oracle-First Design**: Optimized for Oracle database patterns and performance
2. **FLEXT Core Integration**: Built on FlextResult[T] and Clean Architecture patterns
3. **Enterprise Security**: SSL/TLS, connection pooling, and audit logging
4. **Schema Intelligence**: Complete Oracle metadata introspection and DDL generation
5. **Singer Foundation**: Provides base patterns for tap-oracle and target-oracle

---

## 📁 **Module Structure & Responsibilities**

### **Foundation Layer**

```python
# Oracle integration foundation - entry point for all Oracle operations
src/flext_db_oracle/
├── __init__.py              # 🎯 Public API gateway (Oracle-specific exports)
├── version.py               # 🎯 Version management with Oracle client compatibility
├── constants.py             # 🎯 Oracle-specific constants and defaults
└── exceptions.py            # 🎯 Oracle-specific exception hierarchy
```

**Responsibility**: Establish Oracle database integration contracts and error handling.

**Import Pattern**:

```python
# Primary Oracle integration imports
from flext_db_oracle import (
    FlextDbOracleApi,           # Main application service
    FlextDbOracleConfig,        # Configuration management
    FlextDbOracleConnection     # Connection handling
)

# FLEXT Core integration (automatic)
from flext_core import FlextResult, FlextContainer
```

### **Configuration & Connection Layer**

```python
# Oracle-specific configuration and connection management
├── config.py                # ⚙️ FlextDbOracleConfig - Pydantic-based configuration
├── connection.py            # ⚙️ FlextDbOracleConnection - Connection pooling
└── observability.py         # ⚙️ Oracle performance monitoring and logging
```

**Responsibility**: Handle Oracle connection lifecycle, security, and monitoring.

**Configuration Pattern**:

```python
from flext_db_oracle.config import FlextDbOracleConfig
from flext_db_oracle.connection import FlextDbOracleConnection

# Environment-based configuration
config = FlextDbOracleConfig.from_env().value
connection = FlextDbOracleConnection(config)

# Connection with enterprise features
connect_result = connection.create_pool()
if connect_result.success:
    # Oracle connection pool ready with SSL/TLS
    pass
```

### **Application Service Layer**

```python
# High-level Oracle application services
├── api.py                   # 🚀 FlextDbOracleApi - Main application service
├── cli.py                   # 🚀 Command-line interface integration
└── plugins.py               # 🚀 Plugin system for Oracle extensions
```

**Responsibility**: Provide high-level Oracle operations with business logic and extensibility.

**Usage Pattern**:

```python
from flext_db_oracle import FlextDbOracleApi

# High-level Oracle operations
api = FlextDbOracleApi.from_env("production")
connect_result = api.connect()

if connect_result.success:
    # Execute queries with Oracle optimizations
    query_result = api.execute_query(
        "SELECT * FROM employees WHERE department_id = :dept_id",
        {"dept_id": 10}
    )

    # Bulk operations with Oracle-specific performance
    bulk_result = api.bulk_insert(
        schema="HR",
        table="EMPLOYEES",
        columns=["ID", "NAME", "SALARY"],
        values=[[1, "John", 50000], [2, "Jane", 60000]]
    )
```

### **Domain & Metadata Layer**

```python
# Oracle schema introspection and metadata management
├── metadata.py              # 🏛️ Oracle schema introspection and DDL generation
├── types.py                 # 🏛️ Oracle-specific type definitions and Pydantic models
└── models.py                # 🏛️ Oracle domain entities (tables, columns, schemas)
```

**Responsibility**: Rich Oracle schema modeling and metadata operations.

**Domain Modeling Pattern**:

```python
from flext_db_oracle.metadata import FlextDbOracleMetadataManager
from flext_db_oracle.types import TDbOracleSchema, TDbOracleTable
from flext_core import FlextEntity

class FlextDbOracleSchema(FlextEntity):
    """Rich Oracle schema entity with business logic"""
    name: str
    tables: List[TDbOracleTable]
    views: List[dict]

    def generate_documentation(self) -> FlextResult[str]:
        """Generate schema documentation"""
        return FlextResult[None].ok(self._build_schema_docs())

    def analyze_dependencies(self) -> FlextResult[Dict[str, List[str]]]:
        """Analyze table dependencies"""
        return FlextResult[None].ok(self._calculate_dependencies())

# Usage with Oracle metadata
metadata_manager = FlextDbOracleMetadataManager(connection)
schema_result = metadata_manager.get_schema_metadata("HR")

if schema_result.success:
    schema = schema_result.value
    docs_result = schema.generate_documentation()
```

### **Infrastructure & Integration Layer**

```python
# External integrations and infrastructure concerns
├── singer_integration.py    # 🔧 Singer SDK base patterns for taps/targets
├── meltano_patterns.py      # 🔧 Meltano orchestration patterns
└── security.py             # 🔧 SSL/TLS, encryption, and audit logging
```

**Responsibility**: Integration with external systems and cross-cutting concerns.

**Singer Integration Pattern**:

```python
from flext_db_oracle.singer_integration import (
    FlextOracleBaseTap,
    FlextOracleBaseTarget,
    oracle_schema_to_singer_catalog
)

class MyOracleTap(FlextOracleBaseTap):
    """Oracle tap built on FLEXT DB Oracle"""

    def discover_streams(self) -> List[Stream]:
        # Use FLEXT DB Oracle metadata for automatic discovery
        schema_result = self.oracle_api.get_schema_metadata(self.config.schema)

        if schema_result.success:
            return oracle_schema_to_singer_catalog(schema_result.value)

        return []
```

### **Utility & Extension Layer**

```python
# Utilities and Oracle-specific extensions
├── utils.py                 # 🔧 Pure utility functions for Oracle operations
├── performance.py           # 🔧 Oracle performance optimization utilities
└── migration.py             # 🔧 Database migration and schema evolution utilities
```

**Responsibility**: Reusable Oracle utilities and performance optimizations.

**Utility Pattern**:

```python
from flext_db_oracle.utils import (
    format_oracle_identifier,
    build_connection_string,
    parse_oracle_error
)
from flext_db_oracle.performance import (
    optimize_query_hints,
    analyze_execution_plan
)

# Oracle-specific utilities
table_name = format_oracle_identifier("user_data")  # "USER_DATA"
conn_string = build_connection_string(config)
error_info = parse_oracle_error("ORA-00942: table or view does not exist")

# Performance optimization
optimized_sql = optimize_query_hints(original_sql, table_statistics)
execution_plan = analyze_execution_plan(cursor)
```

---

## 🎯 **Semantic Naming Conventions**

### **Public API Naming (FlextDbOracleXxx)**

All public exports use the `FlextDbOracle` prefix for clear namespace separation:

```python
# Main API classes
FlextDbOracleApi            # Main application service for Oracle operations
FlextDbOracleConfig         # Configuration management with validation
FlextDbOracleConnection     # Connection pooling and resource management
FlextDbOracleMetadataManager # Schema introspection and DDL generation

# Domain models
FlextDbOracleSchema         # Oracle schema domain entity
FlextDbOracleTable          # Oracle table domain entity
FlextDbOracleColumn         # Oracle column domain entity
FlextDbOracleIndex          # Oracle index domain entity

# Specialized services
FlextDbOraclePerformanceMonitor # Performance monitoring service
FlextDbOracleSecurityManager    # Security and audit service
FlextDbOraclePluginManager      # Plugin system manager
```

**Rationale**: `FlextDbOracle` prefix prevents conflicts and clearly identifies Oracle-specific functionality.

### **Module-Level Naming**

```python
# Module names reflect Oracle-specific concerns
api.py                      # Contains FlextDbOracleApi and high-level operations
config.py                   # Contains FlextDbOracleConfig and settings management
connection.py               # Contains FlextDbOracleConnection and pooling
metadata.py                 # Contains Oracle schema introspection
types.py                    # Contains Oracle-specific type definitions
security.py                 # Contains SSL/TLS and security features
```

**Pattern**: Oracle-focused modules with clear single responsibility.

### **Type Definition Naming**

```python
# Oracle-specific type aliases
TDbOracleQueryResult       # Query result type with Oracle metadata
TDbOracleConnectionStatus  # Connection pool status information
TDbOracleSchema           # Schema metadata type
TDbOracleTable            # Table metadata type
TDbOracleColumn           # Column metadata type
TDbOracleIndex            # Index metadata type
TDbOracleConstraint       # Constraint metadata type

# Configuration types
TDbOracleConnectionParams # Connection parameter dictionary
TDbOraclePoolConfig       # Connection pool configuration
TDbOracleSSLConfig        # SSL/TLS configuration
```

**Pattern**: `TDbOracle` prefix for type aliases, descriptive names for Oracle concepts.

---

## 📦 **Import Patterns & Best Practices**

### **Recommended Import Styles**

#### **1. Primary Pattern (Recommended for Applications)**

```python
# Import main Oracle classes - gets essential functionality
from flext_db_oracle import (
    FlextDbOracleApi,
    FlextDbOracleConfig,
    FlextDbOracleConnection
)

# FLEXT Core automatically available
from flext_core import FlextResult  # Automatic with FlextDbOracle

# Use Oracle patterns directly
def process_oracle_data(config_dict: dict) -> FlextResult[ProcessedData]:
    config = FlextDbOracleConfig(**config_dict)
    api = FlextDbOracleApi(config)
    return api.connect().flat_map(lambda _: api.execute_query("SELECT * FROM users"))
```

#### **2. Specific Module Pattern (For Advanced Oracle Operations)**

```python
# Import from specific modules for Oracle specialization
from flext_db_oracle.api import FlextDbOracleApi
from flext_db_oracle.metadata import FlextDbOracleMetadataManager
from flext_db_oracle.performance import optimize_oracle_query
from flext_db_oracle.security import enable_oracle_ssl

# More explicit for Oracle-specific features
```

#### **3. Singer Integration Pattern**

```python
# Import Singer-specific patterns
from flext_db_oracle.singer_integration import (
    FlextOracleBaseTap,
    FlextOracleBaseTarget,
    oracle_schema_to_singer_catalog
)
from flext_db_oracle.meltano_patterns import (
    create_meltano_oracle_config,
    optimize_meltano_oracle_pipeline
)

# Building Singer components on Oracle foundation
class MyOracleTap(FlextOracleBaseTap):
    def get_records(self, context: dict) -> Iterator[dict]:
        # Oracle-optimized record extraction
        return self.oracle_api.stream_query_results(self.sql, batch_size=10000)
```

### **Anti-Patterns (Forbidden)**

```python
# ❌ Don't import everything
from flext_db_oracle import *

# ❌ Don't import internal Oracle implementations
from flext_db_oracle._connection_base import _OracleConnectionImpl

# ❌ Don't bypass Oracle API patterns
import oracledb  # Use FlextDbOracleConnection instead

# ❌ Don't create custom Oracle result types
class OracleResult[T]:  # Use FlextResult[T] consistently
    pass
```

---

## 🏛️ **Oracle-Specific Architectural Patterns**

### **Layer Separation for Oracle**

```python
# Oracle-specific Clean Architecture layers
┌─────────────────────────────────────────────────────────┐
│            Application Layer                            │  # api.py, cli.py
│    (Oracle API, CLI, Plugin Management)                │
├─────────────────────────────────────────────────────────┤
│              Domain Layer                               │  # metadata.py, models.py
│   (Oracle Schema Models, Business Logic)               │  # types.py
├─────────────────────────────────────────────────────────┤
│           Infrastructure Layer                          │  # connection.py, config.py
│  (Connection Pooling, SSL/TLS, Configuration)          │  # observability.py, security.py
├─────────────────────────────────────────────────────────┤
│            Foundation Layer                             │  # FLEXT Core integration
│     (FlextResult, FlextContainer, Type System)         │  # exceptions.py, constants.py
└─────────────────────────────────────────────────────────┘
```

### **Oracle Connection Lifecycle Pattern**

```python
# Proper Oracle connection management with pooling
from flext_db_oracle import FlextDbOracleApi, FlextDbOracleConfig
from flext_core import FlextResult

class OracleService:
    """Service demonstrating proper Oracle connection patterns"""

    def __init__(self, config: FlextDbOracleConfig):
        self.api = FlextDbOracleApi(config)
        self._connected = False

    async def __aenter__(self) -> 'OracleService':
        """Async context manager for connection lifecycle"""
        connect_result = await self.api.connect_async()
        if connect_result.is_failure:
            raise RuntimeError(f"Oracle connection failed: {connect_result.error}")
        self._connected = True
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Ensure proper cleanup"""
        if self._connected:
            await self.api.disconnect_async()

    def execute_business_operation(self, data: dict) -> FlextResult[ProcessedData]:
        """Business operation with proper error handling"""
        if not self._connected:
            return FlextResult[None].fail("Oracle connection not established")

        return (
            self._validate_input(data)
            .flat_map(self._transform_for_oracle)
            .flat_map(self._execute_oracle_operations)
            .map(self._format_response)
        )

# Usage pattern
async def process_oracle_workflow(config: FlextDbOracleConfig, data: dict):
    async with OracleService(config) as oracle_service:
        result = oracle_service.execute_business_operation(data)
        return result
```

### **Oracle Schema Intelligence Pattern**

```python
# Leverage Oracle metadata for intelligent operations
from flext_db_oracle import FlextDbOracleApi, FlextDbOracleMetadataManager
from flext_core import FlextResult

class IntelligentOracleOperations:
    """Demonstrate Oracle schema intelligence patterns"""

    def __init__(self, api: FlextDbOracleApi):
        self.api = api
        self.metadata_manager = FlextDbOracleMetadataManager(api.connection)

    def smart_table_sync(self, source_schema: str, target_schema: str) -> FlextResult[SyncReport]:
        """Intelligent table synchronization using Oracle metadata"""
        return (
            self.metadata_manager.get_schema_metadata(source_schema)
            .flat_map(lambda source: self.metadata_manager.get_schema_metadata(target_schema)
                     .map(lambda target: (source, target)))
            .flat_map(self._analyze_schema_differences)
            .flat_map(self._generate_sync_operations)
            .flat_map(self._execute_sync_operations)
        )

    def auto_generate_ddl(self, schema_name: str, table_pattern: str) -> FlextResult[List[str]]:
        """Auto-generate DDL for schema objects"""
        return (
            self.metadata_manager.get_schema_metadata(schema_name)
            .map(lambda schema: [table for table in schema.tables
                               if self._matches_pattern(table.name, table_pattern)])
            .flat_map(self._generate_table_ddl_statements)
        )

    def optimize_queries_for_schema(self, queries: List[str], schema: str) -> FlextResult[List[str]]:
        """Optimize queries based on Oracle schema statistics"""
        return (
            self.metadata_manager.get_schema_metadata(schema)
            .flat_map(lambda schema_meta: self._analyze_table_statistics(schema_meta))
            .map(lambda stats: [self._optimize_query(query, stats) for query in queries])
        )
```

---

## 🔄 **Oracle-Specific Railway-Oriented Programming**

### **Oracle Query Patterns with FlextResult**

```python
# Oracle-optimized query patterns
from flext_db_oracle import FlextDbOracleApi
from flext_core import FlextResult

def complex_oracle_workflow(api: FlextDbOracleApi, customer_id: str) -> FlextResult[CustomerReport]:
    """Complex Oracle workflow with error handling"""
    return (
        # Step 1: Validate customer exists
        api.execute_query(
            "SELECT customer_id FROM customers WHERE customer_id = :cust_id",
            {"cust_id": customer_id}
        )
        .flat_map(lambda result: _validate_customer_exists(result))

        # Step 2: Get customer orders with Oracle-specific optimizations
        .flat_map(lambda _: api.execute_query(
            """
            SELECT /*+ FIRST_ROWS(100) */
                   o.order_id, o.order_date, o.total_amount,
                   COUNT(oi.item_id) as item_count
            FROM orders o
            JOIN order_items oi ON o.order_id = oi.order_id
            WHERE o.customer_id = :cust_id
              AND o.order_date >= SYSDATE - 365
            GROUP BY o.order_id, o.order_date, o.total_amount
            ORDER BY o.order_date DESC
            """,
            {"cust_id": customer_id}
        ))

        # Step 3: Calculate customer metrics
        .map(lambda orders: _calculate_customer_metrics(orders))

        # Step 4: Generate comprehensive report
        .flat_map(lambda metrics: _generate_customer_report(customer_id, metrics))
    )

def batch_oracle_processing(api: FlextDbOracleApi, items: List[dict]) -> FlextResult[BatchResult]:
    """Batch processing with Oracle bulk operations"""
    batch_size = 10000  # Oracle-optimized batch size

    return (
        # Validate all items first
        FlextResult[None].ok(items)
        .flat_map(_validate_batch_items)

        # Process in Oracle-optimized batches
        .flat_map(lambda validated_items: api.bulk_insert(
            schema="DATA_WAREHOUSE",
            table="STAGING_ITEMS",
            columns=["item_id", "item_data", "processing_date"],
            values=[[item["id"], json.dumps(item["data"]), datetime.utcnow()]
                   for item in validated_items],
            batch_size=batch_size
        ))

        # Execute Oracle stored procedure for processing
        .flat_map(lambda _: api.execute_query(
            "BEGIN process_staging_items(:batch_id); END;",
            {"batch_id": generate_batch_id()}
        ))

        # Return processing results
        .map(lambda _: BatchResult(processed_count=len(items), status="SUCCESS"))
    )
```

### **Oracle Connection Pool Management**

```python
# Advanced connection pool patterns with error recovery
from flext_db_oracle import FlextDbOracleConnection, FlextDbOracleConfig
from flext_core import FlextResult

class RobustOracleConnection:
    """Robust Oracle connection with automatic recovery"""

    def __init__(self, config: FlextDbOracleConfig):
        self.config = config
        self.connection = FlextDbOracleConnection(config)
        self.retry_attempts = 3
        self.retry_delay = 1.0

    def execute_with_retry(self, sql: str, params: dict = None) -> FlextResult[Any]:
        """Execute Oracle query with automatic retry on connection failure"""
        return self._retry_operation(
            lambda: self.connection.execute_query(sql, params),
            self.retry_attempts
        )

    def _retry_operation(self, operation: Callable, attempts: int) -> FlextResult[Any]:
        """Generic retry pattern for Oracle operations"""
        if attempts <= 0:
            return FlextResult[None].fail("Max retry attempts exceeded")

        result = operation()

        if result.success:
            return result

        # Check for recoverable Oracle errors
        if self._is_recoverable_error(result.error):
            # Wait and reconnect
            time.sleep(self.retry_delay)
            reconnect_result = self.connection.create_pool()

            if reconnect_result.success:
                return self._retry_operation(operation, attempts - 1)

        return result

    def _is_recoverable_error(self, error: str) -> bool:
        """Identify recoverable Oracle errors"""
        recoverable_patterns = [
            "ORA-03113",  # End-of-file on communication channel
            "ORA-03114",  # Not connected to ORACLE
            "ORA-12170",  # TNS:Connect timeout occurred
            "ORA-12571",  # TNS:packet writer failure
        ]
        return any(pattern in error for pattern in recoverable_patterns)
```

---

## 🎯 **Oracle Performance Optimization Patterns**

### **Query Optimization with Oracle Hints**

```python
# Oracle-specific performance optimization patterns
from flext_db_oracle.performance import OracleQueryOptimizer, OracleHintBuilder

class PerformantOracleQueries:
    """Demonstrate Oracle performance optimization patterns"""

    def __init__(self, api: FlextDbOracleApi):
        self.api = api
        self.optimizer = OracleQueryOptimizer(api.connection)

    def optimized_large_table_query(self, table: str, filters: dict) -> FlextResult[QueryResult]:
        """Query large tables with Oracle-specific optimizations"""

        # Build optimized query with hints
        hint_builder = OracleHintBuilder()
        hints = (
            hint_builder
            .use_index("EMPLOYEES_DEPT_IDX")  # Use specific index
            .first_rows(1000)                 # Optimize for first N rows
            .parallel(4)                      # Use parallel execution
            .build()
        )

        optimized_sql = f"""
        SELECT /*+ {hints} */
               employee_id, name, department_id, salary
        FROM {table}
        WHERE department_id = :dept_id
          AND hire_date >= :start_date
          AND salary BETWEEN :min_salary AND :max_salary
        ORDER BY hire_date DESC
        """

        return self.api.execute_query(optimized_sql, filters)

    def bulk_data_extraction(self, table: str, batch_size: int = 50000) -> FlextResult[Iterator[List[dict]]]:
        """Extract large datasets efficiently using Oracle cursor sharing"""

        cursor_sql = f"""
        SELECT /*+ FIRST_ROWS({batch_size}) */
               *
        FROM {table}
        ORDER BY rowid
        """

        return (
            self.api.get_connection()
            .flat_map(lambda conn: self._create_server_cursor(conn, cursor_sql))
            .map(lambda cursor: self._batch_iterator(cursor, batch_size))
        )

    def partition_aware_processing(self, partition_table: str, date_range: tuple) -> FlextResult[ProcessingResult]:
        """Process partitioned tables with partition pruning"""

        # Oracle partition pruning query
        partition_sql = f"""
        SELECT /*+ PARTITION_RANGE({partition_table} :start_date :end_date) */
               partition_name,
               COUNT(*) as row_count,
               MIN(created_date) as min_date,
               MAX(created_date) as max_date
        FROM {partition_table}
        WHERE created_date BETWEEN :start_date AND :end_date
        GROUP BY partition_name
        ORDER BY partition_name
        """

        return (
            self.api.execute_query(partition_sql, {
                "start_date": date_range[0],
                "end_date": date_range[1]
            })
            .flat_map(self._process_partitions_in_parallel)
        )
```

### **Oracle Connection Pool Tuning**

```python
# Oracle-specific connection pool optimization
from flext_db_oracle import FlextDbOracleConfig

def create_production_oracle_config() -> FlextDbOracleConfig:
    """Create production-optimized Oracle configuration"""
    return FlextDbOracleConfig(
        host="oracle-prod.company.com",
        port=1521,
        service_name="PROD",
        username="app_user",
        password="secure_password",

        # Oracle-optimized connection pool settings
        pool_min=10,              # Maintain minimum connections
        pool_max=50,              # Scale up to 50 connections
        pool_increment=5,         # Add 5 connections at a time
        timeout=60,               # 60-second timeout for operations

        # Oracle-specific optimizations
        encoding="AL32UTF8",      # Oracle Unicode encoding
        autocommit=False,         # Explicit transaction control

        # Performance tuning
        arraysize=10000,          # Fetch array size for bulk operations
        prefetchrows=1000,        # Prefetch rows for performance

        # Connection validation
        validate_connection=True,  # Validate connections before use
        ping_on_checkout=True,    # Ping database on connection checkout

        # SSL configuration for production
        protocol="tcps",
        ssl_cert_path="/etc/ssl/certs/oracle-client.pem",
        ssl_server_dn_match=True
    )

def create_etl_oracle_config() -> FlextDbOracleConfig:
    """Create ETL-optimized Oracle configuration"""
    return FlextDbOracleConfig(
        # ETL-specific optimizations
        pool_min=5,               # Fewer connections for batch processing
        pool_max=20,              # Moderate scaling for ETL workloads
        timeout=1800,             # 30-minute timeout for long-running ETL

        # Bulk operation optimizations
        arraysize=50000,          # Large fetch array for ETL
        prefetchrows=10000,       # High prefetch for bulk processing

        # Transaction management
        autocommit=False,         # Explicit commits for ETL consistency
        isolation_level="READ_COMMITTED"  # Appropriate isolation level
    )
```

---

## 🔒 **Oracle Security Patterns**

### **Secure Oracle Connection Management**

```python
# Oracle security and audit patterns
from flext_db_oracle.security import (
    FlextDbOracleSecurityManager,
    OracleAuditLogger,
    SecureCredentialManager
)

class SecureOracleService:
    """Demonstrate Oracle security best practices"""

    def __init__(self, config: FlextDbOracleConfig):
        self.api = FlextDbOracleApi(config)
        self.security_manager = FlextDbOracleSecurityManager(config)
        self.audit_logger = OracleAuditLogger(config.audit_settings)

    def secure_data_access(self, user_context: UserContext, query: str) -> FlextResult[QueryResult]:
        """Secure data access with auditing"""
        return (
            # Validate user permissions
            self.security_manager.validate_user_permissions(user_context, query)
            .flat_map(lambda _: self._audit_query_request(user_context, query))

            # Execute with row-level security
            .flat_map(lambda _: self._execute_with_rls(user_context, query))

            # Audit successful access
            .flat_map(lambda result: self._audit_query_success(user_context, query, result)
                     .map(lambda _: result))
        )

    def _execute_with_rls(self, user_context: UserContext, query: str) -> FlextResult[QueryResult]:
        """Execute query with Oracle Row-Level Security"""

        # Set Oracle application context for RLS
        context_sql = """
        BEGIN
            DBMS_SESSION.SET_CONTEXT('USER_CONTEXT', 'USER_ID', :user_id);
            DBMS_SESSION.SET_CONTEXT('USER_CONTEXT', 'DEPARTMENT', :department);
            DBMS_SESSION.SET_CONTEXT('USER_CONTEXT', 'ROLE', :role);
        END;
        """

        return (
            self.api.execute_query(context_sql, {
                "user_id": user_context.user_id,
                "department": user_context.department,
                "role": user_context.role
            })
            .flat_map(lambda _: self.api.execute_query(query))
        )

    def _audit_query_request(self, user_context: UserContext, query: str) -> FlextResult[None]:
        """Audit query request"""
        audit_entry = {
            "event_type": "QUERY_REQUEST",
            "user_id": user_context.user_id,
            "query_hash": hashlib.sha256(query.encode()).hexdigest(),
            "timestamp": datetime.utcnow(),
            "source_ip": user_context.source_ip
        }

        return self.audit_logger.log_security_event(audit_entry)
```

### **Oracle SSL/TLS Configuration**

```python
# SSL/TLS configuration for Oracle connections
from flext_db_oracle.security import SSLConfigBuilder

def create_secure_oracle_config() -> FlextDbOracleConfig:
    """Create SSL-enabled Oracle configuration"""

    ssl_config = (
        SSLConfigBuilder()
        .enable_ssl()
        .set_certificate_path("/etc/ssl/certs/oracle-client.pem")
        .set_private_key_path("/etc/ssl/private/oracle-client.key")
        .set_ca_certificate_path("/etc/ssl/certs/oracle-ca.pem")
        .require_server_verification()
        .set_server_dn("CN=oracle-prod.company.com,OU=IT,O=Company")
        .build()
    )

    return FlextDbOracleConfig(
        host="oracle-secure.company.com",
        port=2484,  # Secure port
        service_name="SECURE_PROD",
        username="secure_app_user",
        password=SecretStr("secure_password"),

        # SSL configuration
        protocol="tcps",
        ssl_config=ssl_config,

        # Security settings
        validate_certificates=True,
        require_encryption=True,
        cipher_suites=["TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384"]
    )
```

---

## 🧪 **Oracle-Specific Testing Patterns**

### **Test Organization for Oracle Components**

```python
# Oracle-specific test structure
tests/
├── unit/                           # Unit tests (no Oracle database required)
│   ├── test_config.py             # FlextDbOracleConfig tests
│   ├── test_api.py                # FlextDbOracleApi tests (mocked)
│   ├── test_metadata_parsing.py   # Metadata parsing logic tests
│   ├── test_query_building.py     # Query building utilities tests
│   └── test_type_conversions.py   # Oracle type conversion tests
├── integration/                    # Integration tests (require Oracle)
│   ├── test_oracle_connection.py  # Oracle connection integration
│   ├── test_oracle_queries.py     # Query execution integration
│   ├── test_oracle_metadata.py    # Metadata extraction integration
│   ├── test_oracle_performance.py # Performance optimization tests
│   └── test_oracle_security.py    # Security feature integration
├── e2e/                           # End-to-end tests
│   ├── test_singer_integration.py # Singer tap/target workflows
│   ├── test_meltano_pipeline.py   # Meltano orchestration tests
│   └── test_production_scenarios.py # Production-like scenarios
├── oracle_test_fixtures/           # Oracle test data and fixtures
│   ├── test_schemas.sql           # Test schema definitions
│   ├── test_data.sql              # Test data setup
│   └── oracle_docker_setup.py     # Oracle XE Docker setup
└── conftest.py                    # Test configuration and fixtures
```

### **Oracle Integration Testing Patterns**

```python
# Oracle integration testing with proper setup/teardown
import pytest
from flext_db_oracle import FlextDbOracleApi, FlextDbOracleConfig
from flext_core import FlextResult

@pytest.fixture(scope="session")
def oracle_test_config() -> FlextDbOracleConfig:
    """Oracle test configuration"""
    return FlextDbOracleConfig(
        host="localhost",
        port=1521,
        service_name="XEPDB1",  # Oracle XE test database
        username="testuser",
        password="testpass",
        schema="TESTSCHEMA"
    )

@pytest.fixture(scope="session")
def oracle_api(oracle_test_config: FlextDbOracleConfig) -> FlextDbOracleApi:
    """Oracle API instance for testing"""
    api = FlextDbOracleApi(oracle_test_config)

    # Setup test database
    connect_result = api.connect()
    if connect_result.is_failure:
        pytest.skip(f"Oracle database not available: {connect_result.error}")

    # Create test schema
    api.execute_ddl("""
        CREATE TABLE IF NOT EXISTS test_employees (
            employee_id NUMBER PRIMARY KEY,
            name VARCHAR2(100) NOT NULL,
            department VARCHAR2(50),
            salary NUMBER(10,2),
            hire_date DATE DEFAULT SYSDATE
        )
    """)

    yield api

    # Cleanup
    api.execute_ddl("DROP TABLE test_employees")
    api.disconnect()

class TestOracleIntegration:
    """Oracle integration tests"""

    def test_oracle_connection(self, oracle_api: FlextDbOracleApi):
        """Test Oracle database connection"""
        status_result = oracle_api.get_connection_status()

        assert status_result.success
        assert status_result.value.is_connected
        assert status_result.value.active_connections > 0

    def test_oracle_query_execution(self, oracle_api: FlextDbOracleApi):
        """Test Oracle query execution"""
        # Insert test data
        insert_result = oracle_api.execute_query("""
            INSERT INTO test_employees (employee_id, name, department, salary)
            VALUES (:emp_id, :name, :dept, :salary)
        """, {
            "emp_id": 1,
            "name": "John Doe",
            "dept": "Engineering",
            "salary": 75000.00
        })

        assert insert_result.success

        # Query test data
        query_result = oracle_api.execute_query("""
            SELECT employee_id, name, department, salary
            FROM test_employees
            WHERE employee_id = :emp_id
        """, {"emp_id": 1})

        assert query_result.success
        assert len(query_result.value.rows) == 1

        row = query_result.value.rows[0]
        assert row[0] == 1  # employee_id
        assert row[1] == "John Doe"  # name
        assert row[2] == "Engineering"  # department
        assert row[3] == 75000.00  # salary

    def test_oracle_bulk_operations(self, oracle_api: FlextDbOracleApi):
        """Test Oracle bulk insert operations"""
        test_data = [
            [2, "Jane Smith", "Marketing", 65000.00],
            [3, "Bob Wilson", "Sales", 55000.00],
            [4, "Alice Johnson", "Engineering", 80000.00]
        ]

        bulk_result = oracle_api.bulk_insert(
            schema="TESTSCHEMA",
            table="TEST_EMPLOYEES",
            columns=["EMPLOYEE_ID", "NAME", "DEPARTMENT", "SALARY"],
            values=test_data,
            batch_size=1000
        )

        assert bulk_result.success
        assert bulk_result.value == 3  # 3 rows inserted

        # Verify bulk insert
        count_result = oracle_api.execute_query(
            "SELECT COUNT(*) FROM test_employees WHERE employee_id IN (2, 3, 4)"
        )

        assert count_result.success
        assert count_result.value.rows[0][0] == 3

    def test_oracle_metadata_extraction(self, oracle_api: FlextDbOracleApi):
        """Test Oracle schema metadata extraction"""
        metadata_result = oracle_api.get_schema_metadata("TESTSCHEMA")

        assert metadata_result.success

        schema = metadata_result.value
        assert schema.name == "TESTSCHEMA"
        assert len(schema.tables) > 0

        # Find test table
        test_table = next((t for t in schema.tables if t.name == "TEST_EMPLOYEES"), None)
        assert test_table is not None
        assert len(test_table.columns) == 5  # All columns present

        # Verify column details
        column_names = [col.name for col in test_table.columns]
        assert "EMPLOYEE_ID" in column_names
        assert "NAME" in column_names
        assert "DEPARTMENT" in column_names
        assert "SALARY" in column_names
        assert "HIRE_DATE" in column_names
```

### **Oracle Performance Testing**

```python
# Performance testing for Oracle operations
import time
import pytest
from flext_db_oracle import FlextDbOracleApi

class TestOraclePerformance:
    """Oracle performance tests"""

    @pytest.mark.performance
    def test_connection_pool_performance(self, oracle_api: FlextDbOracleApi):
        """Test connection pool performance under load"""
        start_time = time.time()

        # Execute multiple concurrent queries
        query_results = []
        for i in range(100):
            result = oracle_api.execute_query(
                "SELECT :iteration FROM DUAL",
                {"iteration": i}
            )
            query_results.append(result)

        execution_time = time.time() - start_time

        # Verify all queries succeeded
        assert all(result.success for result in query_results)

        # Performance assertion (adjust based on environment)
        assert execution_time < 10.0  # Should complete in under 10 seconds

        # Connection pool should be efficient
        status = oracle_api.get_connection_status().value
        assert status.active_connections <= status.pool_size

    @pytest.mark.performance
    def test_bulk_insert_performance(self, oracle_api: FlextDbOracleApi):
        """Test bulk insert performance with large datasets"""

        # Generate large test dataset
        large_dataset = [
            [i, f"Employee_{i}", f"Dept_{i % 10}", float(50000 + (i * 100))]
            for i in range(10000)  # 10,000 records
        ]

        start_time = time.time()

        bulk_result = oracle_api.bulk_insert(
            schema="TESTSCHEMA",
            table="TEST_EMPLOYEES",
            columns=["EMPLOYEE_ID", "NAME", "DEPARTMENT", "SALARY"],
            values=large_dataset,
            batch_size=5000  # Oracle-optimized batch size
        )

        execution_time = time.time() - start_time

        assert bulk_result.success
        assert bulk_result.value == 10000

        # Performance assertion (adjust based on environment)
        assert execution_time < 30.0  # Should complete in under 30 seconds

        # Cleanup large dataset
        oracle_api.execute_query("DELETE FROM test_employees WHERE employee_id >= 5")
```

---

## 📏 **Oracle Code Quality Standards**

### **Oracle-Specific Type Annotations**

```python
# Oracle-specific type annotations and validation
from typing import Dict, List, Optional, Union, Literal
from pydantic import BaseModel, Field, validator
from decimal import Decimal
from datetime import datetime, date

# Oracle data type mappings
OracleDataType = Literal[
    "VARCHAR2", "CHAR", "NVARCHAR2", "NCHAR", "CLOB", "NCLOB",
    "NUMBER", "INTEGER", "FLOAT", "BINARY_FLOAT", "BINARY_DOUBLE",
    "DATE", "TIMESTAMP", "TIMESTAMP WITH TIME ZONE",
    "RAW", "BLOB", "ROWID", "UROWID"
]

OracleConnectionProtocol = Literal["tcp", "tcps", "ipc"]

class FlextDbOracleColumn(BaseModel):
    """Oracle column metadata with complete type safety"""
    name: str = Field(..., min_length=1, max_length=128)
    data_type: OracleDataType
    data_length: Optional[int] = Field(None, ge=0, le=4000)
    data_precision: Optional[int] = Field(None, ge=1, le=38)
    data_scale: Optional[int] = Field(None, ge=-84, le=127)
    nullable: bool = True
    default_value: Optional[str] = None

    @validator('data_length')
    def validate_data_length(cls, v, values):
        """Validate data length based on Oracle data type"""
        data_type = values.get('data_type')
        if data_type in ['VARCHAR2', 'NVARCHAR2'] and v is None:
            raise ValueError(f'{data_type} requires data_length')
        return v

    @validator('data_precision')
    def validate_precision(cls, v, values):
        """Validate precision for numeric types"""
        data_type = values.get('data_type')
        if data_type == 'NUMBER' and v is None:
            # NUMBER without precision defaults to maximum
            return 38
        return v

# Oracle query result types
class FlextDbOracleQueryResult(BaseModel):
    """Oracle query result with complete metadata"""
    rows: List[tuple]
    columns: List[str]
    row_count: int = Field(..., ge=0)
    execution_time_ms: float = Field(..., ge=0)
    oracle_metadata: Dict[str, Any] = Field(default_factory=dict)

    class Config:
        arbitrary_types_allowed = True  # Allow tuple types

# Oracle connection status
class FlextDbOracleConnectionStatus(BaseModel):
    """Oracle connection pool status"""
    is_connected: bool
    pool_size: int = Field(..., ge=0)
    active_connections: int = Field(..., ge=0)
    available_connections: int = Field(..., ge=0)
    total_connections_created: int = Field(..., ge=0)
    oracle_version: Optional[str] = None

    @validator('available_connections')
    def validate_available_connections(cls, v, values):
        """Ensure available + active <= pool_size"""
        active = values.get('active_connections', 0)
        pool_size = values.get('pool_size', 0)
        if v + active > pool_size:
            raise ValueError('Available + active connections exceeds pool size')
        return v
```

### **Oracle Error Handling Standards**

```python
# Oracle-specific error handling with detailed error categorization
from enum import Enum
from typing import Optional

class OracleErrorCategory(Enum):
    """Oracle error categories for proper handling"""
    CONNECTION_ERROR = "connection"
    AUTHENTICATION_ERROR = "authentication"
    PERMISSION_ERROR = "permission"
    SYNTAX_ERROR = "syntax"
    DATA_ERROR = "data"
    RESOURCE_ERROR = "resource"
    UNKNOWN_ERROR = "unknown"

class OracleErrorAnalyzer:
    """Analyze Oracle errors for proper categorization and handling"""

    ERROR_PATTERNS = {
        OracleErrorCategory.CONNECTION_ERROR: [
            "ORA-03113", "ORA-03114", "ORA-12170", "ORA-12571", "ORA-12543"
        ],
        OracleErrorCategory.AUTHENTICATION_ERROR: [
            "ORA-01017", "ORA-01045", "ORA-28000", "ORA-28001", "ORA-28002"
        ],
        OracleErrorCategory.PERMISSION_ERROR: [
            "ORA-00942", "ORA-01031", "ORA-01749", "ORA-00980"
        ],
        OracleErrorCategory.SYNTAX_ERROR: [
            "ORA-00900", "ORA-00901", "ORA-00904", "ORA-00907", "ORA-00936"
        ],
        OracleErrorCategory.DATA_ERROR: [
            "ORA-01400", "ORA-01438", "ORA-01439", "ORA-12899", "ORA-01722"
        ],
        OracleErrorCategory.RESOURCE_ERROR: [
            "ORA-00020", "ORA-00018", "ORA-04031", "ORA-01652", "ORA-01654"
        ]
    }

    @classmethod
    def categorize_error(cls, error_message: str) -> OracleErrorCategory:
        """Categorize Oracle error for appropriate handling"""
        for category, patterns in cls.ERROR_PATTERNS.items():
            if any(pattern in error_message for pattern in patterns):
                return category
        return OracleErrorCategory.UNKNOWN_ERROR

    @classmethod
    def get_recovery_strategy(cls, error_category: OracleErrorCategory) -> str:
        """Get recovery strategy for Oracle error category"""
        strategies = {
            OracleErrorCategory.CONNECTION_ERROR: "retry_with_backoff",
            OracleErrorCategory.AUTHENTICATION_ERROR: "refresh_credentials",
            OracleErrorCategory.PERMISSION_ERROR: "check_privileges",
            OracleErrorCategory.SYNTAX_ERROR: "fix_query_syntax",
            OracleErrorCategory.DATA_ERROR: "validate_input_data",
            OracleErrorCategory.RESOURCE_ERROR: "wait_and_retry",
            OracleErrorCategory.UNKNOWN_ERROR: "escalate_to_dba"
        }
        return strategies.get(error_category, "manual_investigation")

# Oracle-aware error handling function
def handle_oracle_error(error_message: str) -> FlextResult[ErrorRecoveryPlan]:
    """Handle Oracle errors with category-specific recovery strategies"""
    category = OracleErrorAnalyzer.categorize_error(error_message)
    recovery_strategy = OracleErrorAnalyzer.get_recovery_strategy(category)

    recovery_plan = ErrorRecoveryPlan(
        error_category=category,
        recovery_strategy=recovery_strategy,
        is_recoverable=category != OracleErrorCategory.SYNTAX_ERROR,
        estimated_recovery_time=_estimate_recovery_time(category)
    )

    return FlextResult[None].ok(recovery_plan)
```

---

## 🌐 **FLEXT Ecosystem Integration Guidelines**

### **Cross-Project Oracle Integration**

```python
# Seamless integration with other FLEXT Oracle projects
from flext_db_oracle import FlextDbOracleApi, FlextDbOracleConfig
from flext_tap_oracle import FlextOracleTap  # Singer tap
from flext_target_oracle import FlextOracleTarget  # Singer target
from flext_oracle_wms import FlextOracleWmsClient  # WMS integration
from flext_core import FlextResult, FlextContainer

class OracleEcosystemOrchestrator:
    """Orchestrate Oracle operations across FLEXT ecosystem"""

    def __init__(self, container: FlextContainer):
        self.container = container
        self.base_api = container.get("oracle_api").value

    def create_data_pipeline(self, source_config: dict, target_config: dict) -> FlextResult[DataPipeline]:
        """Create end-to-end Oracle data pipeline"""
        return (
            # Create Oracle tap using FLEXT DB Oracle foundation
            self._create_oracle_tap(source_config)
            .flat_map(lambda tap: self._create_oracle_target(target_config)
                     .map(lambda target: (tap, target)))

            # Setup pipeline orchestration
            .flat_map(lambda components: self._create_pipeline_orchestration(*components))

            # Validate pipeline connectivity
            .flat_map(self._validate_pipeline_connectivity)
        )

    def sync_oracle_to_wms(self, sync_config: OracleWmsSyncConfig) -> FlextResult[SyncReport]:
        """Synchronize Oracle data with WMS system"""
        wms_client = FlextOracleWmsClient(sync_config.wms_config)

        return (
            # Extract data from Oracle using FLEXT DB Oracle
            self.base_api.execute_query(sync_config.extract_query)
            .map(lambda result: self._transform_for_wms(result.rows))

            # Load data to WMS using specialized client
            .flat_map(lambda wms_data: wms_client.bulk_update_inventory(wms_data))

            # Generate sync report
            .map(lambda result: SyncReport(
                records_processed=len(result.updated_items),
                sync_timestamp=datetime.utcnow(),
                status="SUCCESS"
            ))
        )

    def create_oracle_analytics_workflow(self, analytics_config: dict) -> FlextResult[AnalyticsWorkflow]:
        """Create Oracle analytics workflow with ecosystem integration"""
        return (
            # Setup Oracle extraction
            self._setup_oracle_extraction(analytics_config["source"])
            .flat_map(lambda extractor: self._setup_data_transformation(analytics_config["transform"]))
            .flat_map(lambda transformer: self._setup_oracle_analytics_target(analytics_config["target"]))

            # Create workflow orchestration
            .map(lambda components: AnalyticsWorkflow(*components))
        )
```

### **Configuration Consistency Across Ecosystem**

```python
# Consistent configuration patterns across Oracle projects
from flext_core import FlextSettings
from flext_db_oracle import FlextDbOracleConfig

class FlextEcosystemOracleSettings(FlextSettings):
    """Unified Oracle settings for entire FLEXT ecosystem"""

    # Base Oracle connection (shared across all Oracle projects)
    oracle_base: FlextDbOracleConfig = Field(default_factory=FlextDbOracleConfig)

    # Project-specific Oracle configurations
    oracle_tap: Optional[Dict[str, Any]] = None      # tap-oracle settings
    oracle_target: Optional[Dict[str, Any]] = None   # target-oracle settings
    oracle_wms: Optional[Dict[str, Any]] = None      # Oracle WMS settings
    oracle_api: Optional[Dict[str, Any]] = None      # API service settings

    class Config:
        env_prefix = "FLEXT_ORACLE_"
        env_nested_delimiter = "__"

    @property
    def tap_oracle_config(self) -> FlextDbOracleConfig:
        """Get Oracle tap configuration"""
        base_config = self.oracle_base.dict()
        tap_overrides = self.oracle_tap or {}
        return FlextDbOracleConfig(**{**base_config, **tap_overrides})

    @property
    def target_oracle_config(self) -> FlextDbOracleConfig:
        """Get Oracle target configuration"""
        base_config = self.oracle_base.dict()
        target_overrides = self.oracle_target or {}
        return FlextDbOracleConfig(**{**base_config, **target_overrides})

# Usage across ecosystem projects
def setup_oracle_ecosystem(container: FlextContainer) -> FlextResult[None]:
    """Setup Oracle integration across entire FLEXT ecosystem"""

    # Load unified configuration
    settings = FlextEcosystemOracleSettings()

    # Register Oracle services in container
    return (
        # Base Oracle API
        FlextResult[None].ok(FlextDbOracleApi(settings.oracle_base))
        .flat_map(lambda api: container.register("oracle_api", api))

        # Oracle tap service
        .flat_map(lambda _: container.register("oracle_tap",
                                             FlextOracleTap(settings.tap_oracle_config)))

        # Oracle target service
        .flat_map(lambda _: container.register("oracle_target",
                                             FlextOracleTarget(settings.target_oracle_config)))

        # Validate all Oracle services
        .flat_map(lambda _: validate_oracle_ecosystem_connectivity(container))
    )
```

---

## 📋 **Oracle Module Creation Checklist**

### **Oracle-Specific Module Checklist**

- [ ] **Oracle Compatibility**: Tested with Oracle 11g, 12c, 18c, 19c, 21c
- [ ] **Connection Pooling**: Implements efficient Oracle connection pooling
- [ ] **SSL/TLS Support**: Secure connections with certificate validation
- [ ] **Oracle Types**: Proper handling of Oracle-specific data types
- [ ] **Performance**: Oracle hints and optimizations where appropriate
- [ ] **Metadata**: Oracle schema introspection capabilities
- [ ] **Bulk Operations**: Efficient bulk insert/update operations
- [ ] **Error Handling**: Oracle-specific error categorization and recovery
- [ ] **Audit Support**: Security audit logging for Oracle operations
- [ ] **Singer Integration**: Compatible with Singer tap/target patterns

### **FLEXT Ecosystem Integration Checklist**

- [ ] **FlextResult**: All operations return FlextResult[T] consistently
- [ ] **FLEXT Core Integration**: Uses FlextContainer and FlextSettings
- [ ] **Configuration**: Follows FLEXT configuration patterns
- [ ] **Type Safety**: Complete type annotations with Oracle-specific types
- [ ] **Documentation**: Comprehensive docstrings with Oracle examples
- [ ] **Testing**: Oracle integration tests with Docker Oracle XE
- [ ] **Performance**: Benchmarked against Oracle best practices
- [ ] **Security**: Secure credential handling and SSL/TLS support
- [ ] **Observability**: Integration with FLEXT observability stack
- [ ] **Ecosystem**: Compatible with other FLEXT Oracle projects

### **Quality Gate Checklist**

- [ ] **Oracle Linting**: `make lint` passes with Oracle-specific rules
- [ ] **Oracle Type Check**: `make type-check` passes with Oracle types
- [ ] **Oracle Tests**: `make test` passes including Oracle integration tests
- [ ] **Oracle Security**: `make security` passes with Oracle security patterns
- [ ] **Oracle Performance**: Performance benchmarks meet Oracle standards
- [ ] **Oracle Documentation**: Complete Oracle-specific documentation
- [ ] **Oracle Examples**: Working examples with Oracle database
- [ ] **Ecosystem Impact**: Validated across dependent Oracle projects

---

**Last Updated**: August 2, 2025  
**Target Audience**: FLEXT Oracle ecosystem developers and contributors  
**Scope**: Python module organization for Oracle database integration within FLEXT ecosystem  
**Version**: 0.9.0 → 1.0.0 Oracle specialization guidelines  
**Oracle Compatibility**: Oracle Database 11g+ with optimal support for 19c+
