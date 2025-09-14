# Getting Started

Basic setup and usage for flext-db-oracle v0.9.0.

## Prerequisites

- Python 3.13+
- Access to Oracle database
- Poetry for dependency management

## Installation

```bash
cd flext/flext-db-oracle
poetry install
```

## Basic Usage

```python
from flext_db_oracle import FlextDbOracleApi
from flext_db_oracle.models import FlextDbOracleModels

# Configure connection
config = FlextDbOracleModels.OracleConfig(
    host="localhost",
    port=1521,
    service_name="XEPDB1",
    user="system",
    password="Oracle123"
)

# Create API instance
api = FlextDbOracleApi(config)

# Test connection
result = api.test_connection()
if result.is_success:
    print("Connected to Oracle")
else:
    print(f"Connection failed: {result.error}")

# Execute query
query_result = api.query("SELECT 1 FROM DUAL")
if query_result.is_success:
    data = query_result.value
    print(f"Query returned {len(data)} rows")
```

## Environment Variables

```bash
export ORACLE_HOST="localhost"
export ORACLE_PORT="1521"
export ORACLE_SERVICE_NAME="XEPDB1"
export ORACLE_USERNAME="system"
export ORACLE_PASSWORD="Oracle123"
```

## CLI Usage

```bash
# Test connection (uses environment variables)
python -m flext_db_oracle.cli health

# Note: CLI uses SimpleNamespace placeholders for formatting
```

## Available Operations

- `api.query(sql)` - Execute SELECT statements
- `api.execute(sql)` - Execute INSERT/UPDATE/DELETE statements
- `api.get_schemas()` - List database schemas
- `api.get_tables(schema)` - List tables in schema
- `api.get_columns(table, schema)` - Get column information

## Oracle XE Container

For testing, use Oracle XE container:

```bash
# Start Oracle XE (if docker-compose.yml exists)
docker-compose up -d

# Connect to localhost:1521/XEPDB1 with system/Oracle123
```

## Limitations

- No async support (0 async methods)
- No DataFrame integration
- CLI has SimpleNamespace placeholders
- Only SQLAlchemy abstraction (no direct python-oracledb)

For more details, see [Configuration](configuration.md) and [API Reference](api-reference.md).

---

Updated: September 17, 2025 | Version: 0.9.0