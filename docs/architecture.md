# Architecture Overview

Clean Architecture implementation for Oracle Database integration in the FLEXT ecosystem.

## Architecture Principles

### Clean Architecture Layers

```
┌─────────────────────────────────────┐
│ Presentation Layer (CLI/API)        │
├─────────────────────────────────────┤
│ Application Layer (Services)        │
├─────────────────────────────────────┤
│ Domain Layer (Models/Entities)      │
├─────────────────────────────────────┤
│ Infrastructure Layer (SQLAlchemy)   │
└─────────────────────────────────────┘
```

### FLEXT Pattern Integration

| Pattern                | Implementation         | Status         |
| ---------------------- | ---------------------- | -------------- |
| **FlextResult<T>**     | Monadic error handling | 🟢 Complete    |
| **FlextDomainService** | Base service patterns  | 🟢 Implemented |
| **FlextContainer**     | Dependency injection   | 🟡 Partial     |
| **FlextLogger**        | Structured logging     | 🟢 Integrated  |

## Module Architecture

### Core Components

```
src/flext_db_oracle/
├── api.py                 # 🎯 FlextDbOracleApi (orchestration layer)
├── services.py            # 🔧 FlextDbOracleServices (business logic)
├── models.py              # 📋 Domain models and configuration
├── client.py              # 💻 CLI integration layer
├── cli.py                 # ⚡ CLI service implementation
├── connection.py          # 🔗 Connection management
├── exceptions.py          # ❌ Domain-specific exceptions
├── utilities.py           # 🛠️ Helper functions
├── constants.py           # 📝 Configuration constants
├── mixins.py              # 🧩 Validation patterns
└── plugins.py             # 🔌 Extension system
```

**Implementation Stats**:

- 4,517 lines across 12 source files
- 36 API methods in FlextDbOracleApi
- 8 helper classes in services layer
- 28 test files with 8,633 lines of validation

### Data Flow Architecture

```mermaid
graph TB
    Client[Client Application] --> API[FlextDbOracleApi]
    CLI[CLI Interface] --> API

    API --> Container[FlextContainer]
    API --> Logger[FlextLogger]
    API --> Services[FlextDbOracleServices]

    Services --> Models[Domain Models]
    Services --> Connection[Connection Pool]

    Connection --> SQLAlchemy[SQLAlchemy Engine]
    SQLAlchemy --> Driver[python-oracledb]
    Driver --> Oracle[(Oracle Database)]

    Models --> Result[FlextResult<T>]
    Services --> Result
    API --> Result
```

## Domain-Driven Design

### Bounded Context

**Oracle Database Integration Context**:

- **Entities**: OracleConfig, QueryResult, ColumnInfo, TableMetadata
- **Value Objects**: ConnectionString, QueryParameters
- **Domain Services**: Schema introspection, query optimization
- **Application Services**: Connection management, transaction handling

### Aggregates

**Connection Aggregate**:

- Root: OracleConnection
- Entities: ConnectionPool, Transaction
- Behaviors: Connect, disconnect, execute, query

**Schema Aggregate**:

- Root: DatabaseSchema
- Entities: Table, Column, Index, Constraint
- Behaviors: Introspect, compare, generate DDL

## Error Handling Strategy

### FlextResult Pattern

All operations use FlextResult for railway-oriented programming:

```python
from flext_core import FlextResult

def query_operation() -> FlextResult[List[Dict]]:
    # No try/catch - explicit error handling
    connection_result = self._get_connection()
    if connection_result.is_failure:
        return FlextResult[List[Dict]].fail(connection_result.error)

    query_result = self._execute_query(sql)
    if query_result.is_failure:
        return FlextResult[List[Dict]].fail(query_result.error)

    return FlextResult[List[Dict]].ok(query_result.value)
```

### Exception Hierarchy

```python
FlextDbOracleException (base)
├── ConnectionException
├── QueryException
├── SchemaException
└── ConfigurationException
```

## Technology Stack

### Current Implementation

**Database Layer**:

- SQLAlchemy 2.0 (ORM and Core)
- Python-oracledb 3.2+ (Oracle driver)
- Connection pooling and transaction management

**FLEXT Integration**:

- flext-core (FlextResult, FlextContainer, FlextLogger)
- flext-cli (CLI patterns and utilities)
- Domain-driven design patterns

**Quality Assurance**:

- MyPy strict mode type checking
- Ruff comprehensive linting
- Bandit security scanning
- 28 test files with Oracle XE container validation

### Technology Gaps (2025 Standards)

**Missing Modern Features**:

- **Async Support**: No async/await patterns (0 async methods found)
- **DataFrame Integration**: Python-oracledb 3.4+ supports pandas/polars
- **Oracle 23ai Features**: Vector types, statement pipelining
- **Zero-Copy Data**: Apache Arrow PyCapsule Interface

## Connection Management

### SQLAlchemy Integration

```python
# Connection string format
oracle+oracledb://username:password@host:port/service_name

# Engine configuration
engine = create_engine(
    connection_string,
    pool_size=20,
    max_overflow=30,
    pool_timeout=30,
    pool_recycle=3600,
    echo=False  # Production setting
)
```

### Pool Configuration

**Production Settings**:

- Pool size: 20 connections
- Max overflow: 30 connections
- Pool timeout: 30 seconds
- Pool recycle: 3600 seconds (1 hour)
- Pre-ping enabled for connection validation

## Plugin Architecture

### Extension Points

```python
class OraclePlugin(ABC):
    @abstractmethod
    def validate_query(self, sql: str) -> FlextResult[str]:
        """Validate and potentially modify SQL queries"""

    @abstractmethod
    def monitor_performance(self, metrics: Dict) -> FlextResult[None]:
        """Monitor query performance"""
```

**Current Plugin Support**:

- Query validation plugins
- Performance monitoring plugins
- Schema validation plugins
- Custom formatter plugins

## Quality Architecture

### Testing Strategy

**Test Categories**:

- **Unit Tests**: Component isolation with mocks
- **Integration Tests**: Real Oracle XE 21c container
- **Performance Tests**: Connection pool and query optimization
- **Security Tests**: SQL injection prevention

**Coverage Targets**:

- Source code: 90% line coverage
- API methods: 100% method coverage
- Error paths: Comprehensive failure scenario testing

### Development Standards

**Code Quality**:

- Type hints on all public APIs
- Docstrings following Google style
- SOLID principles implementation
- Clean Architecture boundaries enforced

**FLEXT Compliance**:

- FlextResult for all fallible operations
- FlextContainer for dependency injection
- FlextLogger for structured logging
- Domain service patterns throughout

## Future Architecture Evolution

### Planned Improvements

**Async Support** (v0.10.0):

- Async API methods using Python-oracledb async support
- AsyncFlextDbOracleApi parallel implementation
- Backward compatibility maintained

**DataFrame Integration** (v0.10.0):

- Zero-copy data interchange with Apache Arrow
- Direct pandas/polars integration
- Performance optimization for data science workflows

**Oracle 23ai Features** (v0.11.0):

- Vector data type support for AI applications
- Statement pipelining for performance
- Enhanced DRCP multi-pool configuration

---

**Version**: 0.9.9 RC | **Updated**: September 17, 2025
**Pattern**: Clean Architecture + Domain-Driven Design
**Integration**: FLEXT Ecosystem Foundation
