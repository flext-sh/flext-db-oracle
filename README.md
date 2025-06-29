# Oracle Database Core Shared Library

[![Python 3.13+](https://img.shields.io/badge/python-3.13+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

Shared Oracle database utilities and core components for the PyAuto framework. This library provides enterprise-grade Oracle database connectivity, schema management, SQL parsing, data comparison, and maintenance tools.

## Features

### 🔌 Database Connectivity

- **Modern Oracle Support**: Uses `oracledb` (new Oracle Python driver) with optional `cx_Oracle` legacy support
- **Connection Pooling**: Enterprise connection pool management
- **Async Support**: Full async/await support for high-performance applications
- **Security**: Built-in credential management and secure connection handling

### 📊 Schema Management

- **Schema Analysis**: Complete Oracle schema introspection and metadata extraction
- **DDL Generation**: Automated DDL script generation for tables, indexes, constraints
- **Schema Comparison**: Advanced schema diff and synchronization tools
- **Migration Support**: Database migration planning and execution utilities

### 🔍 SQL Tools

- **SQL Parsing**: Advanced SQL statement parsing and analysis using `sqlparse`
- **Query Optimization**: SQL performance analysis and optimization suggestions
- **Execution Plans**: Explain plan analysis and visualization
- **Statement Validation**: SQL syntax validation and best practices checking

### 📈 Data Operations

- **Data Comparison**: Row-level data comparison between tables/schemas
- **Bulk Operations**: High-performance bulk insert/update/delete operations
- **ETL Support**: Extract, Transform, Load utilities for data migration
- **Data Validation**: Comprehensive data quality and integrity checks

### 🛠️ Maintenance Tools

- **Health Monitoring**: Database health checks and performance monitoring
- **Space Management**: Tablespace and storage analysis
- **Index Analysis**: Index usage statistics and optimization recommendations
- **Backup Utilities**: Backup validation and restore testing tools

## Installation

```bash
# Basic installation
pip install oracledb-core-shared

# With legacy cx_Oracle support
pip install oracledb-core-shared[legacy]

# With analytics capabilities
pip install oracledb-core-shared[analytics]

# Full installation with all features
pip install oracledb-core-shared[full]
```

## Quick Start

### Basic Connection

```python
from oracledb_core_shared import OracleConnection, ConnectionConfig

# Configure connection
config = ConnectionConfig(
    host="oracle-server.company.com",
    port=1521,
    service_name="ORCL",
    user="app_user",
    password="secure_password"
)

# Create connection
async with OracleConnection(config) as conn:
    result = await conn.execute("SELECT * FROM user_tables")
    print(result.fetchall())
```

### Schema Analysis

```python
from oracledb_core_shared.schema import SchemaAnalyzer

analyzer = SchemaAnalyzer(connection)

# Get complete schema metadata
schema_info = await analyzer.analyze_schema("HR")

# Generate DDL for specific table
ddl = await analyzer.generate_table_ddl("HR", "EMPLOYEES")
print(ddl)
```

### Data Comparison

```python
from oracledb_core_shared.compare import DataComparator

comparator = DataComparator(source_conn, target_conn)

# Compare table data
differences = await comparator.compare_tables(
    "HR.EMPLOYEES",
    "HR_BACKUP.EMPLOYEES"
)

# Generate sync script
sync_script = comparator.generate_sync_sql(differences)
```

## CLI Tools

The library includes several command-line utilities:

```bash
# Schema operations
oracle-schema analyze --schema HR --output schema_report.json
oracle-schema compare --source-schema HR --target-schema HR_BACKUP

# Data comparison
oracle-compare tables --source HR.EMPLOYEES --target HR_BACKUP.EMPLOYEES
oracle-compare schemas --source HR --target HR_TEST

# Maintenance operations
oracle-maintenance health-check --output health_report.json
oracle-maintenance analyze-indexes --schema HR
oracle-maintenance cleanup-temp-objects
```

## Documentation

Comprehensive documentation is available in the `/docs` directory:

- **[Getting Started](docs/getting-started.md)**: Installation and basic usage
- **[API Reference](docs/api-reference/)**: Complete API documentation
- **[Schema Tools](docs/schema-tools.md)**: Schema management and analysis
- **[Data Operations](docs/data-operations.md)**: Data comparison and migration
- **[Maintenance](docs/maintenance.md)**: Database maintenance utilities
- **[Oracle Resources](docs/oracle-resources/)**: Official Oracle documentation and tools

### Oracle Official Documentation

The `docs/oracle-resources/` directory contains:

- Oracle Database documentation (HTML downloads)
- SQL Language Reference
- PL/SQL Developer's Guide
- Database Administrator's Guide
- Performance Tuning Guide
- Security Guide

## Configuration

### Environment Variables

```bash
# Database connection
ORACLE_HOST=oracle-server.company.com
ORACLE_PORT=1521
ORACLE_SERVICE_NAME=ORCL
ORACLE_USER=app_user
ORACLE_PASSWORD=secure_password

# Connection pool settings
ORACLE_POOL_MIN=5
ORACLE_POOL_MAX=20
ORACLE_POOL_INCREMENT=5

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json
```

### Configuration File

```yaml
# oracle-config.yaml
database:
  host: oracle-server.company.com
  port: 1521
  service_name: ORCL
  user: app_user
  password_env: ORACLE_PASSWORD

connection_pool:
  min_connections: 5
  max_connections: 20
  increment: 5

schema_analysis:
  include_system_objects: false
  analyze_dependencies: true
  generate_statistics: true

comparison:
  batch_size: 10000
  ignore_columns: ["CREATED_DATE", "MODIFIED_DATE"]
  case_sensitive: true
```

## Development

### Setup Development Environment

```bash
git clone https://github.com/pyauto/oracledb-core-shared.git
cd oracledb-core-shared
poetry install --with dev,docs,testing
poetry shell
```

### Running Tests

```bash
# Unit tests
pytest tests/unit

# Integration tests (requires Oracle database)
pytest tests/integration

# All tests with coverage
pytest --cov=oracledb_core_shared --cov-report=html
```

### Code Quality

```bash
# Linting and formatting
ruff check src tests
black src tests
mypy src

# Security scan
bandit -r src

# Pre-commit hooks
pre-commit run --all-files
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details on our code of conduct and the process for submitting pull requests.

## Architecture

The library follows a modular architecture:

```
oracledb_core_shared/
├── connection/          # Database connection management
├── schema/             # Schema analysis and DDL generation
├── compare/            # Data and schema comparison tools
├── maintenance/        # Database maintenance utilities
├── sql/               # SQL parsing and optimization
├── utils/             # Common utilities and helpers
└── cli/               # Command-line interfaces
```

## Performance

- **Connection Pooling**: Supports up to 100 concurrent connections
- **Bulk Operations**: Optimized for large dataset operations (1M+ rows)
- **Memory Efficient**: Streaming data processing for minimal memory footprint
- **Async Support**: Non-blocking operations for high-throughput applications

## Security

- **Credential Management**: Secure credential storage and rotation
- **SQL Injection Prevention**: Parameterized queries and input validation
- **Connection Encryption**: TLS/SSL support for secure connections
- **Audit Logging**: Comprehensive audit trail for all operations

## License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.

## Support

- **Documentation**: [https://pyauto.github.io/oracledb-core-shared](https://pyauto.github.io/oracledb-core-shared)
- **Issues**: [GitHub Issues](https://github.com/pyauto/oracledb-core-shared/issues)
- **Discussions**: [GitHub Discussions](https://github.com/pyauto/oracledb-core-shared/discussions)

## Acknowledgments

- Oracle Corporation for the official `oracledb` Python driver
- The Python community for excellent database and async libraries
- Contributors and maintainers of the PyAuto framework
