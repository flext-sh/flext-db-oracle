# flext-db-oracle - Oracle Database Integration Library

**Type**: Oracle Database Integration | **Version**: 0.9.0 | **Updated**: 2025-09-17

Oracle database integration library for Python applications using SQLAlchemy and python-oracledb.

## ⚡ Quick Start

```bash
# Production-ready installation
poetry install

# Enterprise Oracle connection testing
flext-db-oracle test-connection --config production.toml

# Development with Oracle XE container
docker-compose -f docker-compose.oracle.yml up -d
poetry run python -c "from flext_db_oracle import FlextDbOracleApi; print('🚀 Ready for Oracle operations!')"
```

## Features

### Current Implementation

**Architecture**:
- Clean Architecture with Domain-Driven Design patterns
- FlextResult monadic error handling
- SQLAlchemy 2.0 integration with python-oracledb driver
- FLEXT ecosystem integration

**Technology Stack**:
- Python 3.13+ support
- SQLAlchemy 2.0 for ORM operations
- python-oracledb 3.x driver (replaces cx_Oracle)
- Pydantic v2 for data validation

**Quality Features**:
- 28 test files with 8,633 lines of tests
- Oracle XE 21 container validation
- SQL injection prevention
- Type safety with MyPy compliance

### Known Limitations

1. **No async support**: Modern Python applications expect async/await patterns
2. **CLI formatters incomplete**: SimpleNamespace placeholders in client.py:60-67
3. **Missing DataFrame integration**: python-oracledb 3.4+ supports DataFrames
4. **No Oracle 23ai features**: Vector types, statement pipelining not implemented

## FLEXT Ecosystem Integration

### Oracle Database Foundation

flext-db-oracle provides Oracle database integration for the FLEXT ecosystem:

```
┌─────────────────────────────────────────────────────────────────┐
│                    FLEXT ECOSYSTEM (32+ Projects)               │
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

### Core Responsibilities

1. **Oracle Connectivity**: Connection pooling and resource management
2. **Schema Operations**: Metadata extraction, DDL generation, schema comparison
3. **Query Execution**: Type-safe query execution with FlextResult pattern
4. **Foundation Services**: Base for Singer taps, targets, and DBT projects
5. **Plugin Architecture**: Framework for validation and monitoring

## Usage Examples

### Oracle Database Operations

```python
# Basic Oracle database operations
from flext_db_oracle import FlextDbOracleApi, OracleConfig

api = FlextDbOracleApi(OracleConfig(
    host="oracle-server",
    port=1521,
    service_name="XEPDB1",
    username="app_user",
    password="secure_password"
))

# Type-safe operations with FlextResult error handling
result = api.query("SELECT * FROM employees WHERE department = :dept", {"dept": "Engineering"})
if result.is_success:
    employees = result.unwrap()
    print(f"Found {len(employees)} engineers")
```

**Features**:
- python-oracledb 3.x driver with thin/thick mode support
- Connection pooling configuration
- Transaction management with context managers
- Schema introspection (tables, views, indexes, procedures)

### FLEXT Ecosystem Integration

```python
# FLEXT ecosystem integration
from flext_core import FlextResult, FlextLogger, FlextDomainService
from flext_cli import FlextCliMain

class OracleDataService(FlextDomainService[Dict]):
    def __init__(self) -> None:
        super().__init__()
        self._logger = FlextLogger(__name__)

    def process_data(self, data: Dict) -> FlextResult[Dict]:
        # FlextResult error handling pattern
        return FlextResult[Dict].ok(processed_data)
```

**FLEXT Integration**:
- FlextResult monadic error handling
- FlextContainer dependency injection
- FlextLogger structured logging
- FlextTypes data validation

### CLI Interface

```bash
# CLI operations
flext-db-oracle test-connection --config production.toml
flext-db-oracle schema-info --schema SALES
flext-db-oracle query --sql "SELECT COUNT(*) FROM orders" --format json
flext-db-oracle health-check --monitoring
```

**Note**: CLI formatters are currently incomplete (SimpleNamespace placeholders)

**Developer Tools**:
- CLI interface via `flext-db-oracle` command (formatters need implementation)
- Docker development with Oracle XE 21 container
- Test suite with Oracle container validation (28 test files, 8,633 lines)
- Quality gates: MyPy, Ruff, Bandit

## 🚀 Quick Start

### Installation

```bash
# Clone the FLEXT ecosystem
git clone https://github.com/flext-sh/flext.git
cd flext/flext-db-oracle

# Install with Poetry
poetry install

# Development setup with all dependencies
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
from pydantic import SecretStr

# Create configuration
config = FlextDbOracleConfig(
    host="localhost",
    port=1521,
    service_name="XEPDB1",
    username="system",
    password=SecretStr("Oracle123")
)

# Create API instance
api = FlextDbOracleApi(config)

# Test connection using FlextResult pattern
connection_result = api.test_connection()
if connection_result.success:
    print("✅ Connected successfully")
else:
    print(f"❌ Connection failed: {connection_result.error}")

# Query execution with parameters
query_result = api.query(
    "SELECT table_name FROM user_tables WHERE rownum <= :limit",
    {"limit": 5}
)

if query_result.success:
    print(f"Found {query_result.value.row_count} tables")
    for row in query_result.value.rows:
        print(f"  - {row[0]}")
else:
    print(f"Query failed: {query_result.error}")
```

#### 3. Schema Introspection

```python
# Get database schemas
schemas_result = api.get_schemas()
if schemas_result.success:
    print(f"Available schemas: {schemas_result.value}")

# Get tables in a schema
tables_result = api.get_tables("HR")
if tables_result.success:
    print(f"Tables in HR schema: {tables_result.value}")

# Get table columns
columns_result = api.get_columns("EMPLOYEES", "HR")
if columns_result.success:
    for column in columns_result.value:
        print(f"  - {column}")
```

#### 4. CLI Usage

```bash
# Test connection
flext-db-oracle connect-env

# List schemas
flext-db-oracle schemas

# List tables in a schema
flext-db-oracle tables --schema HR

# Execute query
flext-db-oracle query --sql "SELECT COUNT(*) FROM hr.employees"

# Health check
flext-db-oracle health
```

## 🧪 Development Environment

### Local Oracle Setup

Use Docker for local Oracle development:

```bash
# Start Oracle XE 21c (takes 2-3 minutes to initialize)
docker-compose -f docker-compose.oracle.yml up -d

# Monitor startup progress
docker-compose -f docker-compose.oracle.yml logs -f oracle-xe

# Test connectivity once ready
make oracle-connect
```

### Development Commands

```bash
# Complete development setup
make setup                    # Install dependencies + pre-commit hooks

# Quality gates (run before committing)
make validate                 # Full validation: lint + type + security + test
make check                    # Quick validation: lint + type only
make test                     # Run all tests

# Testing strategies
make test-unit                # Fast unit tests (no Oracle dependency)
make test-integration         # Integration tests (requires Oracle)
make test-fast                # Tests without coverage for speed

# Code quality
make format                   # Auto-format code with ruff
make lint                     # Comprehensive linting
make type-check
make security                 # Security scanning with bandit

# Oracle-specific operations
make oracle-test              # Basic Oracle connectivity test
make oracle-connect           # Interactive connection test
```

### Testing

The project follows a comprehensive testing strategy:

```bash
# Run specific test categories
pytest -m unit                # Unit tests only (fast)
pytest -m integration         # Integration tests (needs Oracle)
pytest -m "not slow"          # Exclude slow tests
pytest --lf                   # Last failed tests only

# Test with coverage
pytest --cov=src/flext_db_oracle --cov-report=html
pytest --cov=src/flext_db_oracle --cov-fail-under=90
```

**Current Test Coverage**: 33% overall (improvement in progress)

- Connection module: 53% (significantly improved)
- Metadata module: 42% (comprehensive testing)
- API module: 26% (core methods functional)
- CLI module: 0% (testing in development)

## 📚 Documentation

### Project Information

For general project information, architecture details, and usage examples, see the main documentation in this README.

### Integration Guides

- **FLEXT Ecosystem Integration**: Built on flext-core patterns
- **Singer/Meltano Compatibility**: Environment variable conventions
- **Plugin Development**: Extensible architecture framework

### Configuration Reference

```bash
# Required connection parameters
FLEXT_TARGET_ORACLE_HOST              # Oracle server hostname
FLEXT_TARGET_ORACLE_PORT              # Oracle port (default: 1521)
FLEXT_TARGET_ORACLE_USERNAME          # Oracle username
FLEXT_TARGET_ORACLE_PASSWORD          # Oracle password
FLEXT_TARGET_ORACLE_SERVICE_NAME      # Oracle service name

# Optional configuration
FLEXT_TARGET_ORACLE_POOL_MIN          # Min pool size (default: 5)
FLEXT_TARGET_ORACLE_POOL_MAX          # Max pool size (default: 20)
FLEXT_TARGET_ORACLE_TIMEOUT           # Connection timeout (default: 30)

# Development settings
ORACLE_INTEGRATION_TESTS              # Enable integration tests
ORACLE_SQL_LOGGING                    # Enable SQL query logging
```

## 🏆 Quality Standards

### **Current Quality Metrics**

- **Test Coverage**: 33% (actively improving from 21%)
- **Type Safety**: Python 3.13+ with comprehensive type hints
- **Linting**: Ruff with extensive rules enabled
- **Security**: Bandit + pip-audit scanning
- **Architecture**: Clean Architecture with SOLID principles

### **Development Standards**

- **FLEXT Core Integration**: Consistent FlextResult and FlextContainer patterns
- **Error Handling**: Railway-oriented programming throughout
- **Testing**: Real code validation approach (no excessive mocking)
- **Documentation**: Code examples that actually work
- **Configuration**: Environment-first with validation

### **Quality Gates**

All changes must pass:

```bash
make validate     # Combines: lint + type-check + security + test
```

Individual checks:

- `make lint` - Code style and quality
- `make type-check` - Static type checking
- `make security` - Security vulnerability scanning
- `make test` - Test suite execution

## 🤝 Integration with FLEXT Ecosystem

### **FLEXT Core Patterns**

```python
# FlextResult for error handling
from flext_core import FlextResult

def database_operation() -> FlextResult[QueryResult]:
    try:
        result = perform_query()
        return FlextResult[QueryResult].ok(result)
    except Exception as e:
        return FlextResult[QueryResult].fail(f"Operation failed: {e}")

# FlextContainer for dependency injection
from flext_core import FlextContainer

container = FlextContainer()
oracle_service = container.resolve(FlextDbOracleApi)
```

### **Singer Ecosystem Foundation**

This library serves as the foundation for:

- **flext-tap-oracle**: Oracle data extraction
- **flext-target-oracle**: Oracle data loading
- **flext-dbt-oracle**: Oracle data transformation

### **Service Integration**

Integrates with FLEXT services:

- **FlexCore (Go)**: Plugin system integration
- **FLEXT Service (Go/Python)**: Python bridge for Oracle operations
- **FLEXT API**: REST endpoints for database operations

## 🔒 Security

### **Security Features**

- **Parameterized Queries**: SQL injection prevention
- **Environment Variables**: Secure credential management
- **Connection Security**: SSL/TLS support for encrypted connections
- **Access Control**: Role-based database access patterns

### **Security Validation**

```bash
make security              # Run comprehensive security scanning
poetry run bandit src/     # Security issue detection
poetry run pip-audit       # Dependency vulnerability scanning
```

## 🛠️ Troubleshooting

### **Common Issues**

#### Connection Problems

```bash
# Test Oracle connectivity
make oracle-connect

# Check Oracle container status
docker-compose -f docker-compose.oracle.yml ps

# View Oracle startup logs
docker-compose -f docker-compose.oracle.yml logs oracle-xe
```

#### Development Issues

```bash
# Ensure all dependencies installed
make install-dev

# Reset development environment
make clean-all && make setup

# Run comprehensive health check
make doctor
```

### **Debug Mode**

```python
import logging

# Enable debug logging
logging.getLogger('flext_db_oracle').setLevel(logging.DEBUG)
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

# Enable SQL query logging
import os
os.environ['ORACLE_SQL_LOGGING'] = '1'
```

## 📝 Contributing

### **Development Process**

```bash
# Setup development environment
git clone https://github.com/flext-sh/flext.git
cd flext/flext-db-oracle
make setup

# Create feature branch
git checkout -b feature/your-feature

# Make changes and validate
make validate

# Run comprehensive tests
make test-all
```

### **Contribution Requirements**

1. **Follow FLEXT patterns**: FlextResult, dependency injection, Clean Architecture
2. **Maintain quality gates**: All quality checks must pass
3. **Add comprehensive tests**: Focus on real code validation over mocks
4. **Update documentation**: All public APIs documented with working examples
5. **Performance consideration**: Benchmark critical database operations

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🔗 Links

- **[FLEXT Ecosystem](https://github.com/flext-sh/flext)** - Complete FLEXT platform
- **[FLEXT Core](../flext-core/README.md)** - Foundation library
- **[Oracle Documentation](https://docs.oracle.com)** - Oracle database reference

---

**FLEXT DB Oracle** - Reliable Oracle integration for enterprise data platforms.
