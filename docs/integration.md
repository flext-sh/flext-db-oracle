# Integration

FLEXT ecosystem integration patterns for flext-db-oracle.

## FLEXT Core Integration

```python
from flext_core import FlextBus
from flext_core import FlextConfig
from flext_core import FlextConstants
from flext_core import FlextContainer
from flext_core import FlextContext
from flext_core import FlextDecorators
from flext_core import FlextDispatcher
from flext_core import FlextExceptions
from flext_core import h
from flext_core import FlextLogger
from flext_core import x
from flext_core import FlextModels
from flext_core import FlextProcessors
from flext_core import p
from flext_core import FlextRegistry
from flext_core import FlextResult
from flext_core import FlextRuntime
from flext_core import FlextService
from flext_core import t
from flext_core import u
from flext_db_oracle import FlextDbOracleApi, OracleConfig

# FlextResult error handling
result = api.query("SELECT 1 FROM DUAL")
if result.is_success:
    data = result.value
else:
    error = result.error

# FlextLogger usage
logger = FlextLogger(__name__)
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
config = OracleConfig(
    host="localhost",
    port=1521,
    service_name="XEPDB1",
    user="system",
    password="Oracle123"
)
api = FlextDbOracleApi(config)
```

## Available Operations

- Schema introspection (get_schemas, get_tables, get_columns)
- Query execution (query, execute, execute_many)
- Connection management (connect, disconnect, test_connection)
- Configuration from environment or URLs

---

Updated: September 17, 2025 | Version: 0.9.9
