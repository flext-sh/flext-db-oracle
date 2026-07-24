# Integration

<!-- TOC START -->
- [FLEXT Core Integration](#flext-core-integration)
- [Singer Ecosystem](#singer-ecosystem)
  - [flext-tap-oracle](#flext-tap-oracle)
  - [flext-target-oracle](#flext-target-oracle)
  - [flext-dbt-oracle](#flext-dbt-oracle)
- [CLI Integration](#cli-integration)
- [Connection Patterns](#connection-patterns)
- [Available Operations](#available-operations)
<!-- TOC END -->

FLEXT ecosystem integration patterns for flext-db-oracle.

## FLEXT Core Integration

```python
from flext_cli import u
from flext_core import FlextSettings
from flext_db_oracle import FlextDbOracleApi, OracleConfig

# r error handling
result = api.query("SELECT 1 FROM DUAL")
if result.success:
    data = result.value
else:
    error = result.error

# FlextLogger usage
logger = u.fetch_logger(__name__)
logger.info("Oracle operation completed")
```

## Singer Ecosystem

Foundation for Singer taps and targets:

### flext-tap-oracle

Uses FlextDbOracleApi for data extraction from Oracle databases.

### flext-target-oracle

Uses FlextDbOracleApi for data loading into Oracle databases.

### flext-dbt-oracle

Uses FlextDbOracleApi for Oracle SQL transformations.

## CLI Integration

Integrates with flext-cli but uses SimpleNamespace placeholders:

```python
from flext_db_oracle import FlextDbOracleCliService

cli = FlextDbOracleCliService()
result = cli.execute_health_check()
```

## Connection Patterns

```python
# Environment-based configuration
api = FlextDbOracleApi.from_env()

# Direct configuration
settings = OracleConfig(
    host="localhost",
    port=1521,
    service_name="XEPDB1",
    user="system",
    password="Oracle123",
)
api = FlextDbOracleApi(settings)
```

## Available Operations

- Schema introspection (get_schemas, get_tables, get_columns)
- Query execution (query, execute, execute_many)
- Connection management (connect, disconnect, test_connection)
- Configuration from environment or URLs

______________________________________________________________________

Updated: April 14, 2026 | Version: 0.12.0-dev
