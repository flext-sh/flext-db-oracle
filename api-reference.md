# API Reference

<!-- TOC START -->
- [Core Imports](#core-imports)
- [FlextDbOracleApi](#flextdboracleapi)
  - [Connection Methods](#connection-methods)
  - [Query Methods](#query-methods)
  - [Schema Methods](#schema-methods)
  - [Configuration Methods](#configuration-methods)
- [OracleConfig](#oracleconfig)
- [CLI Interface](#cli-interface)
- [Error Handling](#error-handling)
- [Limitations](#limitations)
- [Related Documentation](#related-documentation)
<!-- TOC END -->

Oracle Database integration API for FLEXT ecosystem - version 0.9.9.

## Core Imports

```python notest
from flext_db_oracle import FlextDbOracleApi, FlextDbOracleModels, OracleConfig
```

## FlextDbOracleApi

Oracle database interface providing 36 methods for connection management, query execution, and schema operations using FLEXT patterns.

### Connection Methods

```python notest
api = FlextDbOracleApi(settings)

# Test connection
result = api.test_connection() -> p.Result[bool]

# Connect to database
result = api.connect() -> p.Result[Self]

# Disconnect from database
result = api.disconnect() -> p.Result[bool]

# Check connection status
status = api.is_connected() -> bool
```

### Query Methods

```python notest
# Execute SELECT queries
result = api.query(sql, parameters=None) -> p.Result[Sequence[m.Dict]]

# Execute single row SELECT
result = api.query_one(sql, parameters=None) -> p.Result[dict | None]

# Execute INSERT/UPDATE/DELETE
result = api.execute(sql, parameters=None) -> p.Result[int]

# Execute multiple statements
result = api.execute_many(sql, parameters_list) -> p.Result[int]
```

### Schema Methods

```python notest
# Get available schemas
result = api.get_schemas() -> p.Result[t.StringList]

# Get tables in schema
result = api.get_tables(schema=None) -> p.Result[Sequence[m.Dict]]

# Get column information
result = api.get_columns(table, schema=None) -> p.Result[Sequence[m.Dict]]

# Get table metadata
result = api.get_table_metadata(table, schema=None) -> p.Result[m.Dict]
```

### Configuration Methods

```python notest
# Create from environment variables
result = FlextDbOracleApi.from_env() -> p.Result[FlextDbOracleApi]

# Create from URL
result = FlextDbOracleApi.from_url(url) -> p.Result[FlextDbOracleApi]

# Get current settings
settings = api.settings -> OracleConfig
```

## OracleConfig

Configuration for Oracle database connections.

```python notest
from flext_db_oracle import FlextDbOracleModels

settings = FlextDbOracleModels.OracleConfig(
    host="localhost",
    port=1521,
    service_name="XEPDB1",
    user="system",
    password="Oracle123",
)

# From environment variables
config_result = FlextDbOracleModels.OracleConfig.from_env()
```

## CLI Interface

Command-line interface with SimpleNamespace placeholders.

```python notest
from flext_db_oracle import FlextDbOracleCliService

cli = FlextDbOracleCliService()
result = cli.execute_health_check()
```

## Error Handling

All methods return r for type-safe error handling.

```python notest
result = api.query("SELECT 1 FROM DUAL")
if result.success:
    data = result.value
else:
    error = result.error
```

## Limitations

- No methods (0 /keywords found)
- No DataFrame support
- CLI uses SimpleNamespace placeholders (client.py:60-67)
- Only SQLAlchemy abstraction (no direct Python-oracledb)

______________________________________________________________________

Updated: April 14, 2026 | Version: 0.12.0-dev

## Related Documentation

**Within Project**:

- Getting Started - Installation and basic usage
- Architecture - Architecture and design patterns
- Troubleshooting - Common issues and solutions

**Across Projects**:

- [flext-core Foundation](https://github.com/organization/flext/tree/main/flext-core/docs/api-reference/foundation.md) - Core APIs and patterns
- [flext-core Railway-Oriented Programming](https://github.com/organization/flext/tree/main/flext-core/docs/guides/railway-oriented-programming.md) - r patterns
- [flext-oracle-oic Integration](https://github.com/organization/flext/tree/main/flext-oracle-oic/AGENTS.md) - Oracle Integration Cloud patterns

**External Resources**:

- [PEP 257 - Docstring Conventions](https://peps.python.org/pep-0257/)
- [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html)
