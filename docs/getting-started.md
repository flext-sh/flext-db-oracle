# Getting Started with flext-db-oracle

<!-- TOC START -->

- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Quick Connection Test](#quick-connection-test)
- [Basic Operations](#basic-operations)
  - [Query Execution](#query-execution)
  - [Schema Operations](#schema-operations)
- [Oracle XE Development Container](#oracle-xe-development-container)
- [Configuration Options](#configuration-options)
  - [Environment Variables](#environment-variables)
  - [Configuration from Environment](#configuration-from-environment)
- [CLI Interface](#cli-interface)
- [Current Capabilities](#current-capabilities)
- [Next Steps](#next-steps)
- [Need Help](#need-help)
- [Related Documentation](#related-documentation)

<!-- TOC END -->

Oracle Database integration for the FLEXT ecosystem - get connected in 5 minutes.

## Prerequisites

- Python 3.13+
- Oracle database access (XE 21c container or remote Oracle)
- Poetry for dependency management

## Installation

```bash
# Clone FLEXT ecosystem
git clone https://github.com/flext-sh/flext.git
cd flext/flext-db-oracle

# Install dependencies
poetry install

# Development setup (optional)
make setup
```

## Quick Connection Test

```python
from flext_db_oracle import FlextDbOracleApi, OracleConfig

# Configure Oracle connection
config = OracleConfig(
    host="localhost",
    port=1521,
    service_name="XEPDB1",
    username="system",
    password="Oracle123"
)

# Create API instance with FLEXT patterns
api = FlextDbOracleApi(config)

# Test connection using FlextResult pattern
connection_result = api.test_connection()
if connection_result.is_success:
    print("✅ Connected to Oracle successfully")
else:
    print(f"❌ Connection failed: {connection_result.error}")
```

## Basic Operations

### Query Execution

```python
# Execute SELECT query with parameters
result = api.query(
    "SELECT table_name FROM user_tables WHERE rownum <= :limit",
    {"limit": 5}
)

if result.is_success:
    tables = result.unwrap()
    print(f"Found {len(tables)} tables")
    for table in tables:
        print(f"  - {table.get('table_name')}")
```

### Schema Operations

```python
# List available schemas
schemas_result = api.get_schemas()
if schemas_result.is_success:
    schemas = schemas_result.unwrap()
    print(f"Available schemas: {schemas}")

# Get tables in a schema
tables_result = api.get_tables("SYSTEM")
if tables_result.is_success:
    tables = tables_result.unwrap()
    print(f"SYSTEM schema has {len(tables)} tables")
```

## Oracle XE Development Container

For local development, use Oracle XE 21c container:

```bash
# Start Oracle XE container (takes 2-3 minutes to initialize)
docker-compose -f docker-compose.oracle.yml up -d

# Monitor startup progress
docker-compose -f docker-compose.oracle.yml logs -f oracle-xe

# Test connectivity once ready
make oracle-connect
```

**Connection Details**:

- Host: localhost
- Port: 1521
- Service Name: XEPDB1
- Username: system
- Password: Oracle123

## Configuration Options

### Environment Variables

```bash
export FLEXT_TARGET_ORACLE_HOST="localhost"
export FLEXT_TARGET_ORACLE_PORT="1521"
export FLEXT_TARGET_ORACLE_SERVICE_NAME="XEPDB1"
export FLEXT_TARGET_ORACLE_USERNAME="system"
export FLEXT_TARGET_ORACLE_PASSWORD="Oracle123"
```

### Configuration from Environment

```python
from flext_db_oracle import FlextDbOracleApi

# Load configuration from environment variables
api_result = FlextDbOracleApi.from_env()
if api_result.is_success:
    api = api_result.unwrap()
    print("API configured from environment")
```

## CLI Interface

```bash
# Basic health check
python -m flext_db_oracle.cli health

# List schemas
python -m flext_db_oracle.cli schemas

# Execute SQL query
python -m flext_db_oracle.cli query "SELECT COUNT(*) FROM dual"

# Note: CLI formatters currently use SimpleNamespace placeholders
```

## Current Capabilities

**Working Features**:

- SQLAlchemy 2.0 integration with Oracle
- FlextResult error handling patterns
- Connection pooling and management
- Schema introspection (tables, columns)
- Query execution with parameter binding
- FLEXT ecosystem integration patterns

**Known Limitations**:

- CLI formatters incomplete (SimpleNamespace placeholders in client.py:60-67)
- No support (required for modern Python applications)
- No DataFrame integration (Python-oracledb 3.4+ supports DataFrames)
- No Oracle 23ai features (Vector types, statement pipelining)

## Next Steps

1. **Architecture Overview** - Understand the design patterns
1. **API Reference** - Complete API documentation
1. **Configuration Guide** - Advanced configuration options
1. **Development Guide** - Contributing to the project

## Need Help

- **Documentation**: Check the docs/ directory
- **Issues**: [GitHub Issues](https://github.com/flext-sh/flext/issues)
- **Troubleshooting**: See troubleshooting.md

---

**Version**: 0.9.9 RC | **Updated**: September 17, 2025
**Part of**: FLEXT Ecosystem - Oracle Database Integration Foundation

## Related Documentation

**Within Project**:

- Architecture - Architecture and design patterns
- API Reference - Complete API documentation
- Troubleshooting - Common issues and solutions

**Across Projects**:

- [flext-core Foundation](https://github.com/organization/flext/tree/main/flext-core/docs/architecture/overview.md) - Clean architecture and CQRS patterns
- [flext-core Service Patterns](https://github.com/organization/flext/tree/main/flext-core/docs/guides/service-patterns.md) - Service patterns and dependency injection
- [flext-oracle-oic Integration](https://github.com/organization/flext/tree/main/flext-oracle-oic/CLAUDE.md) - Oracle Integration Cloud patterns

**External Resources**:

- [PEP 257 - Docstring Conventions](https://peps.python.org/pep-0257/)
- [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html)
