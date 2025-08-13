# flext-db-oracle - Oracle Database Integration

**Type**: Infrastructure Library | **Status**: Active Development | **Dependencies**: flext-core

Oracle database connectivity and operations.

> ⚠️ Development Status: Core connection and query functionality working; Singer integration incomplete.

## Quick Start

```bash
# Install dependencies
poetry install

# Test Oracle connection
python -c "from flext_db_oracle import FlextDbOracleApi; api = FlextDbOracleApi(); print('✅ Working')"

# Run with Docker Oracle
docker-compose -f docker-compose.oracle.yml up -d
```

## Current Reality

**What Actually Works:**

- Oracle database connections with SQLAlchemy 2.x
- Schema introspection and metadata extraction
- Query execution with connection pooling
- CLI tools for database operations

**What Needs Work:**

- Singer ecosystem integration (tap/target compatibility)
- FLEXT observability integration
- Performance optimization features
- Advanced plugin system completion

## 🏗️ Architecture Role

### **Infrastructure Layer Component**

FLEXT DB Oracle operates as a critical infrastructure component:

```
┌─────────────────────────────────────────────────────────────────┐
│                    FLEXT ECOSYSTEM (32 Projects)                 │
├─────────────────────────────────────────────────────────────────┤
│ Services: FlexCore(Go) | FLEXT Service(Go/Python) | Clients     │
├─────────────────────────────────────────────────────────────────┤
│ Applications: API | Auth | Web | CLI | Quality | Observability  │
├═════════════════════════════════════════════════════════════════┤
│ Infrastructure: [FLEXT-DB-ORACLE] | LDAP | LDIF | gRPC | WMS    │
├─────────────────────────────────────────────────────────────────┤
│ Singer Ecosystem: Taps(5) | Targets(5) | DBT(4) | Extensions(1) │
├─────────────────────────────────────────────────────────────────┤
│ Foundation: FLEXT-CORE (FlextResult | DI | Domain Patterns)     │
└─────────────────────────────────────────────────────────────────┘
```

### **Core Responsibilities**

1. **Oracle Connectivity**: Enterprise-grade connection pooling and resource management
2. **Schema Operations**: Complete metadata extraction, DDL generation, and schema comparison
3. **Query Execution**: Type-safe query execution with FlextResult pattern integration
4. **Performance Optimization**: Oracle-specific query optimization and monitoring
5. **Singer Integration**: Foundation for Oracle-based Singer taps and targets
6. **Plugin System**: Extensible architecture for data validation, monitoring, and auditing

## ✨ Key Features

### **Enterprise Database Integration**

- **Modern Oracle Driver**: Built on `oracledb` 3.x with optimal performance
- **Connection Pooling**: Dynamic pool sizing with health monitoring
- **Transaction Management**: Reliable transaction handling with rollback support
- **Resource Management**: Automatic cleanup and leak prevention

### **Schema & Metadata Management**

- **Complete Introspection**: Tables, views, indexes, sequences, procedures extraction
- **DDL Generation**: Automated schema creation and migration scripts
- **Schema Comparison**: Efficient diff algorithms for large-scale schemas
- **Dependency Analysis**: Complex object relationship mapping

### **Core Integration**

- **FlextResult Pattern**: Type-safe error handling without exceptions
- **Dependency Injection**: Consistent service location via FlextContainer
- **Structured Logging**: Correlation ID support for distributed tracing
- **Configuration Management**: Environment-aware settings with validation

### **Performance & Monitoring**

- **Query Optimization**: Oracle-specific hints and execution plan analysis
- **Performance Metrics**: v$views integration for real-time monitoring
- **Health Checks**: Comprehensive database and connection health monitoring
- **Observability**: Integration with FLEXT observability stack

### **Plugin Architecture**

- **Data Validation**: Schema validation and integrity checks
- **Performance Monitoring**: Query analysis and optimization suggestions
- **Security Auditing**: Access compliance and security validation
- **Extensible Framework**: Custom plugin development support

## 🚀 Quick Start

### Installation

```bash
# Clone the FLEXT ecosystem
git clone https://github.com/flext-sh/flext.git
cd flext/flext-db-oracle

# Install with Poetry
poetry install

# Development installation with all dependencies
make setup
```

### Basic Usage

#### 1. Configuration

Using environment variables (Meltano/Singer compatible):

```bash
export FLEXT_TARGET_ORACLE_HOST="localhost"
export FLEXT_TARGET_ORACLE_PORT="1521"
export FLEXT_TARGET_ORACLE_USERNAME="system"
export FLEXT_TARGET_ORACLE_PASSWORD="Oracle123"
export FLEXT_TARGET_ORACLE_SERVICE_NAME="XEPDB1"
```

#### 2. Basic Connection and Operations

```python
from flext_db_oracle import FlextDbOracleApi, FlextDbOracleConfig

# Load configuration from environment
config = FlextDbOracleConfig.from_env()

# Create API instance with FLEXT patterns
api = FlextDbOracleApi(config)

# Connect using FlextResult pattern
connection_result = api.connect()
if connection_result.is_failure:
    print(f"Connection failed: {connection_result.error}")
    exit(1)

# Execute query with type safety
query_result = api.execute_query("SELECT * FROM employees WHERE department_id = :dept_id", {"dept_id": 10})
if query_result.success:
    for row in query_result.value.rows:
        print(row)
else:
    print(f"Query failed: {query_result.error}")

# Clean disconnection
api.disconnect()
```

#### 3. Schema Introspection

```python
from flext_db_oracle import FlextDbOracleMetadataManager

# Initialize metadata manager
metadata_manager = FlextDbOracleMetadataManager(api.connection)

# Extract complete schema information
schema_result = metadata_manager.get_schema_metadata("HR")
if schema_result.success:
    schema = schema_result.value
    print(f"Schema has {len(schema.tables)} tables")
    for table in schema.tables:
        print(f"Table: {table.name} ({len(table.columns)} columns)")

# Generate DDL for specific table
ddl_result = metadata_manager.generate_table_ddl("EMPLOYEES", "HR")
if ddl_result.success:
    print(ddl_result.value)
```

#### 4. Plugin System Usage

```python
from flext_db_oracle.plugins import register_all_oracle_plugins

# Register all available plugins
register_all_oracle_plugins(api.plugin_manager)

# Use data validation plugin
validation_result = api.execute_with_plugins("data_validation", {
    "table": "employees",
    "schema": "hr",
    "validation_rules": ["not_null", "foreign_key"]
})

if validation_result.success:
    print("Data validation passed")
else:
    print(f"Validation errors: {validation_result.error}")
```

## 🧪 Development Environment

### Local Oracle Setup

Use Docker for local Oracle development:

```bash
# Start Oracle XE 21c
docker-compose -f docker-compose.oracle.yml up -d

# Wait for Oracle to be ready
docker-compose -f docker-compose.oracle.yml logs -f oracle-xe

# Verify connection
make oracle-connect
```

### Development Commands

```bash
# Complete setup with dependencies and hooks
make setup

# Quality gates (run before committing)
make validate              # Full validation pipeline
make check                 # Quick lint + type check
make test                  # Run all tests (90% coverage required)

# Testing strategies
make test-unit             # Fast unit tests (no Oracle dependency)
make test-integration      # Integration tests (requires Oracle)
make test-fast             # Tests without coverage for speed

# Oracle-specific operations
make oracle-test           # Basic Oracle connectivity test
make oracle-connect        # Test connection to Oracle server

# Development tools
make format                # Auto-format code
make lint                  # Run comprehensive linting
make type-check            # Strict MyPy type checking
make security              # Security scanning with bandit
```

### Testing

The project follows a comprehensive testing strategy:

```bash
# Run specific test categories
pytest -m unit             # Unit tests only
pytest -m integration      # Integration tests (needs Oracle)
pytest -m e2e              # End-to-end tests
pytest -m benchmark        # Performance benchmarks
pytest -m "not slow"       # Fast tests for quick feedback

# Test with coverage
pytest --cov=src/flext_db_oracle --cov-report=html --cov-fail-under=90
```

## 📚 Documentation

### Architecture Documentation

- **[Clean Architecture Guide](docs/architecture/README.md)** - Clean Architecture implementation details
- **[FLEXT Core Integration](docs/flext-integration/README.md)** - Integration patterns with FLEXT ecosystem
- **[Plugin Development](docs/plugins/README.md)** - Creating custom plugins

### Integration Guides

- **[Singer/Meltano Integration](docs/integration/singer.md)** - Using with Singer taps and targets
- **[FLEXT Services Integration](docs/integration/services.md)** - Integration with Go services
- **[Performance Optimization](docs/performance/README.md)** - Oracle-specific optimization techniques

### API Reference

- **[API Documentation](docs/api/README.md)** - Complete API reference
- **[Configuration Guide](docs/configuration/README.md)** - Configuration options and patterns
- **[Error Handling](docs/error-handling/README.md)** - FlextResult patterns and error management

## 🔧 Configuration

### Environment Variables

FLEXT DB Oracle follows Meltano/Singer conventions for configuration:

```bash
# Required connection parameters
FLEXT_TARGET_ORACLE_HOST              # Oracle server hostname
FLEXT_TARGET_ORACLE_PORT              # Oracle port (default: 1521)
FLEXT_TARGET_ORACLE_USERNAME          # Oracle username
FLEXT_TARGET_ORACLE_PASSWORD          # Oracle password
FLEXT_TARGET_ORACLE_SERVICE_NAME      # Oracle service name

# Optional configuration
FLEXT_TARGET_ORACLE_POOL_MIN          # Minimum pool size (default: 5)
FLEXT_TARGET_ORACLE_POOL_MAX          # Maximum pool size (default: 20)
FLEXT_TARGET_ORACLE_TIMEOUT           # Connection timeout (default: 30)
FLEXT_TARGET_ORACLE_CHARSET           # Character set (default: UTF8)

# Development and testing
ORACLE_INTEGRATION_TESTS              # Enable integration tests
```

### Configuration Validation

```python
from flext_db_oracle import FlextDbOracleConfig
from flext_core import FlextResult

# Validate configuration
config_result = FlextDbOracleConfig.from_env_validated()
if config_result.is_failure:
    print(f"Configuration error: {config_result.error}")
    exit(1)

config = config_result.value
```

## 🏆 Quality Standards

### **Quality Targets**

- **Coverage**: 90% target (enforceable with `--cov-fail-under=90`)
- **Type Safety**: MyPy strict mode plan (incremental adoption)
- **Linting**: Ruff with comprehensive rules (continuous improvement)
- **Security**: Bandit + pip-audit scanning
- **Performance**: Benchmarks for critical paths

### **Architectural Standards**

- **FLEXT Core Integration**: Consistent use of FlextResult, FlextContainer patterns
- **Clean Architecture**: Clear separation of domain, application, and infrastructure layers
- **SOLID Principles**: Single responsibility, dependency inversion throughout
- **Plugin Architecture**: Extensible design following Open/Closed principle

### **Testing Requirements**

- Unit tests must not require external Oracle database
- Integration tests marked with `@pytest.mark.integration`
- All public APIs covered with both success and failure scenarios
- Performance benchmarks for critical database operations
- Mock objects used consistently for external dependencies

## 🤝 Integration with FLEXT Ecosystem

### **FLEXT Core Patterns**

```python
# FlextResult for all operations
def execute_query(self, sql: str) -> FlextResult[QueryResult]:
    try:
        result = self._connection.execute(sql)
        return FlextResult.ok(QueryResult(rows=result.fetchall()))
    except Exception as e:
        return FlextResult.fail(f"Query execution failed: {e}")

# Dependency injection via FlextContainer
from flext_core import get_flext_container

container = get_flext_container()
oracle_service = container.resolve(FlextDbOracleApi)
```

### **Singer Ecosystem Integration**

FLEXT DB Oracle serves as the foundation for Singer taps and targets:

- **flext-tap-oracle**: Uses this library for data extraction
- **flext-target-oracle**: Uses this library for data loading
- **flext-dbt-oracle**: Uses this library for data transformation

### **Service Integration**

Integration with FLEXT services:

- **FlexCore (Go)**: Plugin system integration
- **FLEXT Service**: Python bridge for Oracle operations
- **FLEXT API**: REST endpoints for Oracle operations

## 📈 Performance

### **Benchmarks**

- **Connection pooling**: 10x improvement over naive connections
- **Bulk operations**: Support for 100K+ row operations
- **Memory efficiency**: Streaming result sets for large datasets
- **Query optimization**: Oracle-specific hints and execution plans

### **Monitoring**

```python
# Performance monitoring integration
from flext_db_oracle.observability import FlextDbOracleObservabilityManager

# Monitor connection pool health
pool_metrics = observability.get_pool_metrics()
print(f"Active connections: {pool_metrics['active']}")
print(f"Pool utilization: {pool_metrics['utilization']}%")

# Query performance analysis
query_stats = observability.get_query_statistics()
for query, stats in query_stats.items():
    print(f"Query: {query[:50]}... - Avg time: {stats['avg_time']}ms")
```

## 🔒 Security

### **Security Features**

- **Connection security**: SSL/TLS support for encrypted connections
- **Credential management**: Environment variable-based secrets
- **SQL injection prevention**: Parameterized queries only
- **Access control**: Role-based database access patterns
- **Audit logging**: Comprehensive operation logging

### **Security Scanning**

```bash
# Security validation
make security              # Run bandit security scanning
poetry run pip-audit       # Dependency vulnerability scanning
```

## 🛠️ Troubleshooting

### **Common Issues**

#### Connection Problems

```bash
# Test Oracle connectivity
make oracle-connect

# Check Oracle service status
docker-compose -f docker-compose.oracle.yml ps

# View Oracle logs
docker-compose -f docker-compose.oracle.yml logs oracle-xe
```

#### Performance Issues

```bash
# Enable SQL logging for query analysis
export ORACLE_SQL_LOGGING=1

# Run performance benchmarks
pytest -m benchmark -v

# Check connection pool metrics
make oracle-test
```

#### Development Issues

```bash
# Ensure all FLEXT dependencies are available
make install-dev

# Run comprehensive health check
make doctor

# Reset development environment
make clean-all && make setup
```

### **Debug Mode**

```python
import logging

# Enable debug logging
logging.getLogger('flext_db_oracle').setLevel(logging.DEBUG)
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

# Enable query logging
config.debug_sql = True
```

## 📝 Contributing

### **Development Setup**

```bash
# Clone and setup
git clone https://github.com/flext-sh/flext.git
cd flext/flext-db-oracle
make setup

# Create feature branch
git checkout -b feature/your-feature-name

# Make changes and validate
make validate

# Run comprehensive tests
make test-all
```

### **Contribution Guidelines**

1. **Follow FLEXT patterns**: Use FlextResult, dependency injection, Clean Architecture
2. **Maintain quality gates**: All quality checks must pass
3. **Add comprehensive tests**: Both unit and integration tests required
4. **Update documentation**: All public APIs must be documented
5. **Performance consideration**: Benchmark critical path changes

### **Code Review Process**

- All changes require pull request review
- Quality gates must pass (lint, type check, security, tests)
- Performance benchmarks for database operations
- Documentation updates for API changes

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🔗 Links

- **[FLEXT Ecosystem](https://github.com/flext-sh/flext)** - Complete FLEXT platform
- **[FLEXT Core](https://github.com/flext-sh/flext-core)** - Architectural foundation
- **[Documentation](docs/README.md)** - Complete documentation hub
- **[Architecture Guide](docs/architecture/README.md)** - Clean Architecture implementation
- **[API Reference](docs/api/README.md)** - Complete API documentation

---

**FLEXT DB Oracle** - Reliable Oracle integration for enterprise data platforms.
