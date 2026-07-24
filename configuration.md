# Configuration

<!-- TOC START -->
- [Basic Configuration](#basic-configuration)
  - [Environment Variables](#environment-variables)
  - [Code Configuration](#code-configuration)
- [Connection Parameters](#connection-parameters)
- [Testing Connection](#testing-connection)
- [CLI Configuration](#cli-configuration)
<!-- TOC END -->

Oracle database connection configuration for flext-db-oracle.

## Basic Configuration

### Environment Variables

```bash
export ORACLE_HOST="localhost"
export ORACLE_PORT="1521"
export ORACLE_SERVICE_NAME="XEPDB1"
export ORACLE_USERNAME="system"
export ORACLE_PASSWORD="Oracle123"
```

### Code Configuration

```python
import os

# Provide environment values so the API can be built from env vars.
os.environ["ORACLE_DBORACLE__HOST"] = "localhost"
os.environ["ORACLE_DBORACLE__PORT"] = "1521"
os.environ["ORACLE_DBORACLE__SERVICE_NAME"] = "XEPDB1"
os.environ["ORACLE_DBORACLE__USERNAME"] = "system"
os.environ["ORACLE_DBORACLE__PASSWORD"] = "Oracle123"

from flext_db_oracle import FlextDbOracleApi, FlextDbOracleSettings

# From environment
api_result = FlextDbOracleApi.from_env()
if api_result.success:
    api = api_result.value

# Direct configuration
settings = FlextDbOracleSettings(
    DbOracle={
        "host": "localhost",
        "port": 1521,
        "service_name": "XEPDB1",
        "username": "system",
        "password": "Oracle123",
    }
)
api = FlextDbOracleApi(settings)
```

## Connection Parameters

| Parameter    | Type | Default | Description            |
| ------------ | ---- | ------- | ---------------------- |
| host         | str  | -       | Oracle server hostname |
| port         | int  | 1521    | Oracle port number     |
| service_name | str  | -       | Oracle service name    |
| user         | str  | -       | Oracle username        |
| password     | str  | -       | Oracle password        |

## Testing Connection

```python
import os

# Seed environment values so the API can be resolved from settings.
os.environ["ORACLE_DBORACLE__HOST"] = "localhost"
os.environ["ORACLE_DBORACLE__PORT"] = "1521"
os.environ["ORACLE_DBORACLE__SERVICE_NAME"] = "XEPDB1"
os.environ["ORACLE_DBORACLE__USERNAME"] = "system"
os.environ["ORACLE_DBORACLE__PASSWORD"] = "Oracle123"

from flext_db_oracle import FlextDbOracleApi

api_result = FlextDbOracleApi.from_env()
if api_result.success:
    api = api_result.value

    # Test connection
    result = api.test_connection()
    if result.success:
        print("Connected to Oracle")
    else:
        print(f"Connection failed: {result.error}")
else:
    print(f"API could not be created: {api_result.error}")
```

## CLI Configuration

```bash
# Set Oracle connection for CLI commands
export ORACLE_HOST=localhost
export ORACLE_PORT=1521
export ORACLE_SERVICE_NAME=XEPDB1
export ORACLE_USERNAME=system
export ORACLE_PASSWORD=Oracle123

# Test connection
python -m flext_db_oracle.cli health
```

For advanced configuration patterns, see the FLEXT workspace documentation.

______________________________________________________________________

Updated: April 14, 2026 | Version: 0.12.0-dev
