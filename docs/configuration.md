# Configuration

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
from flext_db_oracle import FlextDbOracleApi
from flext_db_oracle.models import FlextDbOracleModels

# From environment
config_result = FlextDbOracleModels.OracleConfig.from_env()
if config_result.is_success:
    api = FlextDbOracleApi(config_result.value)

# Direct configuration
config = FlextDbOracleModels.OracleConfig(
    host="localhost",
    port=1521,
    service_name="XEPDB1",
    user="system",
    password="Oracle123"
)
api = FlextDbOracleApi(config)
```

## Connection Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| host | str | - | Oracle server hostname |
| port | int | 1521 | Oracle port number |
| service_name | str | - | Oracle service name |
| user | str | - | Oracle username |
| password | str | - | Oracle password |

## Testing Connection

```python
# Test connection
result = api.test_connection()
if result.is_success:
    print("Connected to Oracle")
else:
    print(f"Connection failed: {result.error}")
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

---

Updated: September 17, 2025 | Version: 0.9.0