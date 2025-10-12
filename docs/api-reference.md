# API Reference

Oracle Database integration API for FLEXT ecosystem - version 0.9.9.

## Core Imports

```python
from flext_db_oracle import (
    FlextDbOracleApi,
    FlextDbOracleModels,
    OracleConfig
)
```

## FlextDbOracleApi

Oracle database interface providing 36 methods for connection management, query execution, and schema operations using FLEXT patterns.

### Connection Methods

```python
api = FlextDbOracleApi(config)

# Test connection
result = api.test_connection() -> FlextCore.Result[bool]

# Connect to database
result = api.connect() -> FlextCore.Result[Self]

# Disconnect from database
result = api.disconnect() -> FlextCore.Result[None]

# Check connection status
status = api.is_connected() -> bool
```

### Query Methods

```python
# Execute SELECT queries
result = api.query(sql, parameters=None) -> FlextCore.Result[list[FlextCore.Types.Dict]]

# Execute single row SELECT
result = api.query_one(sql, parameters=None) -> FlextCore.Result[dict | None]

# Execute INSERT/UPDATE/DELETE
result = api.execute(sql, parameters=None) -> FlextCore.Result[int]

# Execute multiple statements
result = api.execute_many(sql, parameters_list) -> FlextCore.Result[int]
```

### Schema Methods

```python
# Get available schemas
result = api.get_schemas() -> FlextCore.Result[FlextCore.Types.StringList]

# Get tables in schema
result = api.get_tables(schema=None) -> FlextCore.Result[list[FlextCore.Types.Dict]]

# Get column information
result = api.get_columns(table, schema=None) -> FlextCore.Result[list[FlextCore.Types.Dict]]

# Get table metadata
result = api.get_table_metadata(table, schema=None) -> FlextCore.Result[FlextCore.Types.Dict]
```

### Configuration Methods

```python
# Create from environment variables
result = FlextDbOracleApi.from_env() -> FlextCore.Result[FlextDbOracleApi]

# Create from URL
result = FlextDbOracleApi.from_url(url) -> FlextCore.Result[FlextDbOracleApi]

# Get current config
config = api.config -> OracleConfig
```

## OracleConfig

Configuration for Oracle database connections.

```python
from flext_db_oracle.models import FlextDbOracleModels

config = FlextDbOracleModels.OracleConfig(
    host="localhost",
    port=1521,
    service_name="XEPDB1",
    user="system",
    password="Oracle123"
)

# From environment variables
config_result = FlextDbOracleModels.OracleConfig.from_env()
```

## CLI Interface

Command-line interface with SimpleNamespace placeholders.

```python
from flext_db_oracle import FlextDbOracleCliService

cli = FlextDbOracleCliService()
result = cli.execute_health_check()
```

## Error Handling

All methods return FlextCore.Result for type-safe error handling.

```python
result = api.query("SELECT 1 FROM DUAL")
if result.is_success:
    data = result.value
else:
    error = result.error
```

## Limitations

- No methods (0 /keywords found)
- No DataFrame support
- CLI uses SimpleNamespace placeholders (client.py:60-67)
- Only SQLAlchemy abstraction (no direct Python-oracledb)

---

Updated: September 17, 2025 | Version: 0.9.9
