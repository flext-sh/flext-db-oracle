# C4 Container Diagram - flext-db-oracle

**Container Architecture for Oracle Database Integration**

## Container Overview

The flext-db-oracle library is structured as a single deployable Python package that provides database connectivity services to multiple FLEXT ecosystem applications.

```mermaid
graph TB
    subgraph "FLEXT Ecosystem Applications"
        TAP_APP[flext-tap-oracle<br/>🐍 Python Application<br/>Data Extraction Service]
        TARGET_APP[flext-target-oracle<br/>🐍 Python Application<br/>Data Loading Service]
        DBT_APP[flext-dbt-oracle<br/>🐍 Python Application<br/>Data Transformation Service]
        FLEXT_APP[flext-oud-mig<br/>🐍 Python Application<br/>Migration Tool]
    end

    subgraph "flext-db-oracle Library"
        API_CONTAINER[flext-db-oracle<br/>🐍 Python Library<br/>Database Operations API<br/>Port: N/A (Library)]

        subgraph "Core Components"
            API[FlextDbOracleApi<br/>🎯 Main API<br/>Orchestration Layer]
            SERVICES[FlextDbOracleServices<br/>🔧 Business Logic<br/>Query Building & Execution]
            MODELS[FlextDbOracleModels<br/>📋 Domain Models<br/>Pydantic v2 Models]
            CONNECTION[FlextDbOracleConnection<br/>🔗 Connection Management<br/>SQLAlchemy Pool]
        end

        subgraph "Interface Components"
            CLI[FlextDbOracleCli<br/>💻 CLI Interface<br/>Click Framework]
            CLIENT[FlextDbOracleClient<br/>🎭 Client Operations<br/>Rich UI Components]
        end

        subgraph "Supporting Components"
            EXCEPTIONS[FlextDbOracleExceptions<br/>❌ Error Hierarchy<br/>Domain Exceptions]
            UTILITIES[FlextDbOracleUtilities<br/>🛠️ Helper Functions<br/>Common Operations]
            CONSTANTS[FlextDbOracleConstants<br/>📝 Configuration<br/>System Constants]
        end
    end

    subgraph "External Systems"
        ORACLE_DB[(Oracle Database<br/>XE 21c/19c/18c<br/>Port: 1521)]
        OIC[Oracle Integration Cloud<br/>REST APIs<br/>Port: 443]
        DIRECTORY_SERVICES[Directory Services<br/>LDAP/Active Directory<br/>Port: 389/636]
    end

    subgraph "Development & Testing"
        TEST_FRAMEWORK[pytest<br/>🧪 Testing Framework<br/>Unit/Integration Tests]
        POETRY[Poetry<br/>📦 Package Manager<br/>Dependency Resolution]
        DOCKER_ENV[Docker<br/>🐳 Test Environment<br/>Oracle XE Container]
    end

    %% Internal Library Connections
    API_CONTAINER --> API
    API --> SERVICES
    API --> MODELS
    API --> CONNECTION

    API_CONTAINER --> CLI
    CLI --> CLIENT

    API --> EXCEPTIONS
    API --> UTILITIES
    API --> CONSTANTS

    %% External Connections
    TAP_APP --> API_CONTAINER
    TARGET_APP --> API_CONTAINER
    DBT_APP --> API_CONTAINER
    FLEXT_APP --> API_CONTAINER

    CONNECTION --> ORACLE_DB
    API --> OIC
    API --> DIRECTORY_SERVICES

    %% Development Connections
    TEST_FRAMEWORK --> API_CONTAINER
    POETRY --> API_CONTAINER
    DOCKER_ENV --> ORACLE_DB

    %% Styling
    classDef application fill:#e3f2fd,stroke:#1976d2,stroke-width:2px
    classDef library fill:#fff3e0,stroke:#f57c00,stroke-width:3px
    classDef component fill:#f3e5f5,stroke:#7b1fa2,stroke-width:1px
    classDef external fill:#ffebee,stroke:#d32f2f,stroke-width:2px
    classDef dev fill:#e8f5e8,stroke:#388e3c,stroke-width:2px

    class TAP_APP,TARGET_APP,DBT_APP,FLEXT_APP application
    class API_CONTAINER library
    class API,SERVICES,MODELS,CONNECTION,CLI,CLIENT,EXCEPTIONS,UTILITIES,CONSTANTS component
    class ORACLE_DB,OIC,DIRECTORY_SERVICES external
    class TEST_FRAMEWORK,POETRY,DOCKER_ENV dev
```

## Container Descriptions

### Primary Container: flext-db-oracle Library

**Technology**: Python 3.13+ Library (Poetry package)
**Purpose**: Enterprise Oracle database integration with FLEXT patterns
**Responsibilities**:

- Provide type-safe Oracle database operations
- Implement railway-oriented error handling
- Offer CLI interface for REDACTED_LDAP_BIND_PASSWORDistrative operations
- Support connection pooling and transaction management

**Key Interfaces**:

- **API Interface**: `FlextDbOracleApi` - Main programmatic interface
- **CLI Interface**: `FlextDbOracleCli` - Command-line REDACTED_LDAP_BIND_PASSWORDistrative tools
- **Configuration Interface**: Environment variables and configuration files

### Supporting Applications

#### flext-tap-oracle

**Technology**: Python Application
**Purpose**: Oracle data extraction for Singer taps
**Container Relations**:

- Imports flext-db-oracle library
- Uses FlextDbOracleApi for database queries
- Handles Singer protocol for data extraction

#### flext-target-oracle

**Technology**: Python Application
**Purpose**: Oracle data loading for Singer targets
**Container Relations**:

- Imports flext-db-oracle library
- Uses FlextDbOracleApi for database inserts/updates
- Implements Singer protocol for data loading

#### flext-dbt-oracle

**Technology**: Python Application (dbt adapter)
**Purpose**: Oracle data transformation with dbt
**Container Relations**:

- Imports flext-db-oracle library
- Uses FlextDbOracleApi for dbt operations
- Implements dbt Oracle adapter interface

#### flext-oud-mig

**Technology**: Python Application
**Purpose**: Oracle Unified Directory migration tools
**Container Relations**:

- Imports flext-db-oracle library
- Uses specialized migration APIs
- Handles Oracle directory data operations

### External Systems

#### Oracle Database

**Technology**: Oracle Database XE 21c/19c/18c
**Purpose**: Primary data storage and processing
**Interface**: SQL over TCP/IP (Port 1521)
**Protocols**: Oracle Net Services, SQL\*Net

#### Oracle Integration Cloud (OIC)

**Technology**: Cloud-based integration platform
**Purpose**: Cloud data integration and processing
**Interface**: REST APIs (Port 443)
**Protocols**: HTTPS, OAuth 2.0

#### Directory Services

**Technology**: LDAP/Active Directory
**Purpose**: Authentication and user management
**Interface**: LDAP over TCP/IP (Ports 389/636)
**Protocols**: LDAP, LDAPS

### Development & Testing Infrastructure

#### pytest Testing Framework

**Technology**: Python testing framework
**Purpose**: Comprehensive test execution and validation
**Coverage**: 100% requirement for production code
**Integration**: pytest-xdist for parallel execution

#### Poetry Package Manager

**Technology**: Python dependency management
**Purpose**: Package building and dependency resolution
**Features**: Lock file management, virtual environment handling

#### Docker Test Environment

**Technology**: Containerized Oracle database
**Purpose**: Isolated testing environment
**Image**: Oracle XE 21c container for integration tests

## Technology Choices

### Programming Language

- **Python 3.13+**: Modern type system, performance improvements, exclusive support

### Core Dependencies

- **SQLAlchemy 2.0+**: Enterprise ORM with async support and modern patterns
- **Python-oracledb 3.2+**: Official Oracle driver with performance optimizations
- **Pydantic v2**: Data validation and serialization with modern Python support

### FLEXT Ecosystem

- **flext-core**: Foundation patterns (FlextResult[T], FlextService, FlextContainer)
- **flext-cli**: CLI framework integration (Click + Rich abstractions)

### Development Tools

- **Poetry**: Modern Python packaging and dependency management
- **pytest**: Comprehensive testing with advanced features
- **Ruff**: Fast linting and formatting (replaces multiple tools)
- **Pyrefly**: Next-generation type checking

### Quality Assurance

- **100% Test Coverage**: Mandatory for all production code
- **Type Safety**: Pyrefly strict mode compliance
- **Code Quality**: Ruff linting with zero violations
- **Documentation**: Automated maintenance with quality audits

## Deployment & Runtime

### Library Distribution

- **PyPI Package**: `flext-db-oracle` distributed via PyPI
- **Version Management**: Semantic versioning with compatibility guarantees
- **Dependency Resolution**: Poetry lock files ensure reproducible builds

### Runtime Requirements

- **Python 3.13+**: Exclusive support with modern type features
- **Oracle Client**: Python-oracledb handles client libraries automatically
- **Memory**: Minimal footprint with efficient connection pooling
- **Network**: Reliable connectivity to Oracle databases

### Configuration Management

- **Environment Variables**: Runtime configuration
- **Configuration Files**: Optional YAML/TOML configuration
- **Secrets Management**: Secure credential handling
- **Validation**: Pydantic models ensure configuration correctness

## Security Architecture

### Authentication & Authorization

- **Database Credentials**: Secure storage and rotation
- **Connection Security**: SSL/TLS encryption support
- **Access Control**: Role-based permissions integration

### Data Protection

- **In-Transit**: TLS encryption for database connections
- **At-Rest**: Database-level encryption support
- **Credential Security**: Environment variable isolation

### Audit & Monitoring

- **Query Logging**: Configurable SQL logging (security-conscious)
- **Connection Monitoring**: Pool utilization and performance metrics
- **Error Tracking**: Comprehensive error reporting and alerting

## Scalability & Performance

### Connection Management

- **Connection Pooling**: SQLAlchemy async engine with configurable pools
- **Pool Tuning**: Size, overflow, timeout, and recycle parameters
- **Health Checks**: Automatic connection validation and recovery

### Query Optimization

- **Prepared Statements**: Parameter binding for security and performance
- **Batch Operations**: Support for bulk inserts and updates
- **Result Streaming**: Memory-efficient large result set handling

### Resource Management

- **Memory Efficiency**: Minimal memory footprint design
- **CPU Optimization**: Efficient query processing and data transformation
- **Concurrent Operations**: Async support for high-throughput scenarios

## Monitoring & Observability

### Metrics Collection

- **Performance Metrics**: Query execution times, connection pool utilization
- **Error Rates**: Failed operations and error classifications
- **Resource Usage**: Memory, CPU, and network utilization

### Logging Integration

- **Structured Logging**: JSON-formatted logs with context
- **Log Levels**: Configurable verbosity (ERROR, WARN, INFO, DEBUG)
- **Context Propagation**: Request tracing and correlation IDs

### Health Checks

- **Database Connectivity**: Automatic connection validation
- **Pool Health**: Connection pool status and utilization
- **Service Availability**: Overall service health and readiness

## Evolution Planning

### Version 1.0.0 (Current Target)

- ✅ Complete CLI functionality with Rich integration
- ✅ Production-ready documentation and examples
- ✅ Comprehensive error handling and edge cases
- ✅ Performance benchmarks and optimization

### Future Enhancements

- **Async Support**: Concurrent operations with asyncio
- **DataFrame Integration**: pandas/polars support for analytics
- **Oracle 23ai Features**: Vector operations and AI capabilities
- **Multi-Database Support**: Extended database compatibility

---

**C4 Container Diagram - flext-db-oracle v0.9.0**
**Generated**: 2025-10-10
**Framework**: C4 Model - Container Level
