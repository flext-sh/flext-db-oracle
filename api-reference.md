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

```python
from __future__ import annotations

from flext_db_oracle import FlextDbOracleApi, FlextDbOracleSettings
```

## FlextDbOracleApi

Oracle database interface providing 36 methods for connection management, query execution, and schema operations using FLEXT patterns.

### Connection Methods

```python notest
from __future__ import annotations

from typing import Self
from flext_core import p
from flext_db_oracle import FlextDbOracleApi, FlextDbOracleSettings

settings = FlextDbOracleSettings(host="localhost", port=1521, service_name="XEPDB1")
api = FlextDbOracleApi(settings)

# Test connection returns p.Result[bool]
result = api.test_connection()

# Connect to database returns p.Result[FlextDbOracleApi]
result = api.connect()

# Disconnect from database returns p.Result[bool]
result = api.disconnect()

# Check connection status returns bool
status = api.is_connected()
```

### Query Methods

```python notest
from __future__ import annotations

from typing import Sequence
from flext_core import m, p
from flext_db_oracle import FlextDbOracleApi, FlextDbOracleSettings

settings = FlextDbOracleSettings(host="localhost", port=1521, service_name="XEPDB1")
api = FlextDbOracleApi(settings)

sql = "SELECT 1 FROM DUAL"
parameters = None
parameters_list = []

# Execute SELECT queries
result = api.query(sql, parameters=parameters)

# Execute single row SELECT
result = api.query_one(sql, parameters=parameters)

# Execute INSERT/UPDATE/DELETE
result = api.execute(sql, parameters=parameters)

# Execute multiple statements
result = api.execute_many(sql, parameters_list)
```

### Schema Methods

```python notest
from __future__ import annotations

from flext_core import p
from flext_db_oracle import FlextDbOracleApi, FlextDbOracleSettings

settings = FlextDbOracleSettings(host="localhost", port=1521, service_name="XEPDB1")
api = FlextDbOracleApi(settings)

# Get available schemas
result = api.fetch_schemas()

# Get tables in schema
result = api.fetch_tables(schema=None)

# Get column information
result = api.fetch_columns(table="DUAL", schema=None)

# Get table metadata
result = api.fetch_table_metadata(table="DUAL", schema=None)
```

### Configuration Methods

```python
# Create from environment variables
result = FlextDbOracleApi.from_env() -> p.Result[FlextDbOracleApi]

# Create from URL
result = FlextDbOracleApi.from_url(url) -> p.Result[FlextDbOracleApi]

# Get current settings
settings = api.settings -> OracleConfig
```

## OracleConfig

Configuration for Oracle database connections.

```python
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

```python
from flext_db_oracle import FlextDbOracleCliService

cli = FlextDbOracleCliService()
result = cli.execute_health_check()
```

## Error Handling

All methods return r for type-safe error handling.

```python
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
