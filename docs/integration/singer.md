# Singer/Meltano Integration Guide

**Integrating FLEXT DB Oracle with Singer Taps, Targets, and Meltano Orchestration**

FLEXT DB Oracle serves as the foundational library for Oracle-based Singer ecosystem components within the FLEXT platform. This guide covers integration patterns for building taps, targets, and DBT models that leverage FLEXT DB Oracle's enterprise-grade Oracle connectivity.

## 🎯 Overview

### **Singer Ecosystem Integration**

FLEXT DB Oracle provides the infrastructure foundation for:

```
┌─────────────────────────────────────────────────────────────────┐
│                    SINGER ECOSYSTEM                             │
├─────────────────────────────────────────────────────────────────┤
│ flext-tap-oracle     │ Extract data from Oracle databases       │
│ flext-target-oracle  │ Load data into Oracle databases          │
│ flext-dbt-oracle     │ Transform data in Oracle                 │
├═════════════════════════════════════════════════════════════════┤
│                  FLEXT-DB-ORACLE                                │
│ • Connection Pooling  • Schema Introspection                    │
│ • Query Execution     • Performance Optimization                │
│ • Error Handling      • Security & Compliance                   │
├─────────────────────────────────────────────────────────────────┤
│                     ORACLE DATABASE                             │
└─────────────────────────────────────────────────────────────────┘
```

### **Integration Benefits**

- **Consistent Oracle Connectivity**: All Singer components use the same reliable connection patterns
- **Schema Discovery**: Automatic catalog generation from Oracle metadata
- **Performance Optimization**: Oracle-specific optimizations and connection pooling
- **Error Handling**: Unified FlextResult patterns across all components
- **Configuration Management**: Consistent environment variable patterns

## 📥 Building Oracle Taps (Data Extraction)

### **Basic Tap Structure**

Create a Singer tap that extracts data from Oracle using FLEXT DB Oracle:

```python
# flext-tap-oracle/tap_oracle/tap.py
from datetime import datetime
from typing import Dict, List, object
from singer_sdk import Tap, Stream
from singer_sdk.typing import PropertiesList, Property, StringType, IntegerType

from flext_db_oracle import FlextDbOracleApi, FlextDbOracleConfig
from flext_core import FlextResult

class TapOracle(Tap):
    """Oracle tap using FLEXT DB Oracle."""

    name = "tap-oracle"
    config_jsonschema = {
        "type": "object",
        "properties": {
            "host": {"type": "string"},
            "port": {"type": "integer", "default": 1521},
            "service_name": {"type": "string"},
            "username": {"type": "string"},
            "password": {"type": "string"},
            "schema": {"type": "string"},
        },
        "required": ["host", "service_name", "username", "password"]
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._oracle_api = None

    @property
    def oracle_api(self) -> FlextDbOracleApi:
        """Get Oracle API instance with lazy initialization."""
        if self._oracle_api is None:
            # Create configuration from tap config
            oracle_config = FlextDbOracleConfig(
                host=self.config["host"],
                port=self.config.get("port", 1521),
                service_name=self.config["service_name"],
                username=self.config["username"],
                password=self.config["password"]
            )

            # Initialize API
            self._oracle_api = FlextDbOracleApi(oracle_config)

            # Establish connection
            connect_result = self._oracle_api.connect()
            if connect_result.is_failure:
                raise RuntimeError(f"Failed to connect to Oracle: {connect_result.error}")

        return self._oracle_api

    def discover_streams(self) -> List[Stream]:
        """Discover available Oracle tables as Singer streams."""
        streams = []

        # Get schema metadata using FLEXT DB Oracle
        schema_name = self.config.get("schema", self.config["username"].upper())
        metadata_result = self.oracle_api.get_schema_metadata(schema_name)

        if metadata_result.is_failure:
            self.logger.error(f"Failed to get schema metadata: {metadata_result.error}")
            return streams

        schema = metadata_result.value

        # Create streams for each table
        for table in schema.tables:
            stream = OracleTableStream(
                tap=self,
                name=table.name.lower(),
                schema=self._table_to_singer_schema(table),
                oracle_table=table
            )
            streams.append(stream)

        return streams

    def _table_to_singer_schema(self, table) -> Dict[str, object]:
        """Convert Oracle table metadata to Singer schema."""
        properties = {}

        for column in table.columns:
            # Map Oracle types to Singer types
            if column.data_type.upper() in ['VARCHAR2', 'CHAR', 'CLOB', 'NVARCHAR2']:
                singer_type = StringType()
            elif column.data_type.upper() in ['NUMBER', 'INTEGER', 'BINARY_INTEGER']:
                singer_type = IntegerType()
            else:
                singer_type = StringType()  # Default fallback

            properties[column.name.lower()] = singer_type

        return PropertiesList(*[
            Property(name, prop_type)
            for name, prop_type in properties.items()
        ]).to_dict()

class OracleTableStream(Stream):
    """Stream for Oracle table data."""

    def __init__(self, tap: TapOracle, oracle_table, *args, **kwargs):
        super().__init__(tap, *args, **kwargs)
        self.oracle_table = oracle_table

    def get_records(self, context: Dict[str, object] = None) -> object:
        """Extract records from Oracle table."""
        # Build SQL query
        columns = [col.name for col in self.oracle_table.columns]
        sql = f"SELECT {', '.join(columns)} FROM {self.oracle_table.schema}.{self.oracle_table.name}"

        # Add incremental extraction logic if needed
        if context and "replication_key_value" in context:
            replication_key = self.replication_key
            if replication_key:
                sql += f" WHERE {replication_key} > :last_value"

        # Execute query using FLEXT DB Oracle
        query_result = self.tap.oracle_api.execute_query(sql, context or {})

        if query_result.is_failure:
            self.logger.error(f"Query failed: {query_result.error}")
            return

        # Yield records
        for row in query_result.value.rows:
            record = dict(zip([col.lower() for col in columns], row))
            yield record
```

### **Advanced Tap Features**

#### **Incremental Extraction**

```python
class IncrementalOracleStream(OracleTableStream):
    """Stream with incremental extraction support."""

    replication_method = "INCREMENTAL"
    replication_key = "updated_at"

    def get_records(self, context: Dict[str, object] = None) -> object:
        """Extract records incrementally based on replication key."""
        last_value = context.get("replication_key_value") if context else None

        # Build incremental query
        sql = self._build_incremental_query(last_value)
        params = {"last_value": last_value} if last_value else {}

        # Execute with FLEXT DB Oracle optimizations
        query_result = self.tap.oracle_api.execute_query(sql, params)

        if query_result.is_failure:
            self.logger.error(f"Incremental query failed: {query_result.error}")
            return

        max_replication_value = last_value

        for row in query_result.value.rows:
            record = self._row_to_record(row)

            # Track maximum replication key value
            if record.get(self.replication_key):
                max_replication_value = max(
                    max_replication_value or record[self.replication_key],
                    record[self.replication_key]
                )

            yield record

        # Update context with new replication key value
        if context:
            context["replication_key_value"] = max_replication_value
```

#### **Schema Evolution Handling**

```python
def handle_schema_evolution(self, current_schema: Dict, new_table_metadata) -> Dict:
    """Handle Oracle schema changes during tap execution."""
    new_schema = self._table_to_singer_schema(new_table_metadata)

    # Compare schemas and handle changes
    if current_schema != new_schema:
        self.logger.info(f"Schema evolution detected for {self.name}")

        # Emit schema message for Singer protocol
        self._write_schema_message()

        return new_schema

    return current_schema
```

## 📤 Building Oracle Targets (Data Loading)

### **Basic Target Structure**

Create a Singer target that loads data into Oracle using FLEXT DB Oracle:

```python
# flext-target-oracle/target_oracle/target.py
from typing import Dict, List, Optional

from singer_sdk import Target
from singer_sdk.sinks import SQLSink

from flext_db_oracle import FlextDbOracleApi, FlextDbOracleConfig
from flext_core import FlextResult

class TargetOracle(Target):
    """Oracle target using FLEXT DB Oracle."""

    name = "target-oracle"
    config_jsonschema = {
        "type": "object",
        "properties": {
            "host": {"type": "string"},
            "port": {"type": "integer", "default": 1521},
            "service_name": {"type": "string"},
            "username": {"type": "string"},
            "password": {"type": "string"},
            "default_target_schema": {"type": "string"},
            "batch_size": {"type": "integer", "default": 10000},
        },
        "required": ["host", "service_name", "username", "password"]
    }

    default_sink_class = OracleSink

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._oracle_api = None

    @property
    def oracle_api(self) -> FlextDbOracleApi:
        """Get Oracle API instance."""
        if self._oracle_api is None:
            oracle_config = FlextDbOracleConfig(
                host=self.config["host"],
                port=self.config.get("port", 1521),
                service_name=self.config["service_name"],
                username=self.config["username"],
                password=self.config["password"]
            )

            self._oracle_api = FlextDbOracleApi(oracle_config)

            # Connect with error handling
            connect_result = self._oracle_api.connect()
            if connect_result.is_failure:
                raise RuntimeError(f"Oracle connection failed: {connect_result.error}")

        return self._oracle_api

class OracleSink(SQLSink):
    """Oracle sink with bulk loading optimizations."""

    def __init__(self, target: TargetOracle, *args, **kwargs):
        super().__init__(target, *args, **kwargs)
        self.oracle_api = target.oracle_api

    def process_batch(self, context: Dict) -> None:
        """Process a batch of records with Oracle optimizations."""
        if not self.records_to_drain:
            return

        # Create table if not exists
        self._ensure_table_exists()

        # Bulk insert with Oracle-specific optimizations
        self._bulk_insert_records()

        # Clear processed records
        self.records_to_drain.clear()

    def _ensure_table_exists(self) -> None:
        """Create Oracle table if it doesn't exist."""
        table_name = self.stream_name
        schema_name = self.config.get("default_target_schema", self.oracle_api.config.username.upper())

        # Check if table exists using FLEXT DB Oracle metadata
        table_exists_result = self.oracle_api.table_exists(schema_name, table_name)

        if table_exists_result.is_failure:
            self.logger.error(f"Failed to check table existence: {table_exists_result.error}")
            return

        if not table_exists_result.value:
            # Generate DDL and create table
            ddl = self._generate_create_table_ddl(schema_name, table_name)
            create_result = self.oracle_api.execute_ddl(ddl)

            if create_result.is_failure:
                raise RuntimeError(f"Failed to create table {table_name}: {create_result.error}")

            self.logger.info(f"Created Oracle table {schema_name}.{table_name}")

    def _bulk_insert_records(self) -> None:
        """Bulk insert records using Oracle-specific optimizations."""
        if not self.records_to_drain:
            return

        # Prepare bulk insert data
        columns = list(self.records_to_drain[0].keys())
        values = [
            [record.get(col) for col in columns]
            for record in self.records_to_drain
        ]

        # Execute bulk insert
        bulk_result = self.oracle_api.bulk_insert(
            schema=self.config.get("default_target_schema"),
            table=self.stream_name,
            columns=columns,
            values=values,
            batch_size=self.config.get("batch_size", 10000)
        )

        if bulk_result.is_failure:
            raise RuntimeError(f"Bulk insert failed: {bulk_result.error}")

        self.logger.info(f"Inserted {len(self.records_to_drain)} records into {self.stream_name}")

    def _generate_create_table_ddl(self, schema: str, table: str) -> str:
        """Generate Oracle CREATE TABLE DDL from Singer schema."""
        columns = []

        for field_name, field_schema in self.schema["properties"].items():
            # Map Singer types to Oracle types
            oracle_type = self._singer_type_to_oracle_type(field_schema)
            columns.append(f"{field_name} {oracle_type}")

        return f"""
        CREATE TABLE {schema}.{table} (
            {', '.join(columns)}
        )
        """

    def _singer_type_to_oracle_type(self, field_schema: Dict) -> str:
        """Map Singer schema types to Oracle data types."""
        field_type = field_schema.get("type", ["string"])

        if isinstance(field_type, list):
            # Handle nullable fields
            field_type = [t for t in field_type if t != "null"][0]

        type_mapping = {
            "string": "VARCHAR2(4000)",
            "integer": "NUMBER(38)",
            "number": "NUMBER(38,10)",
            "boolean": "NUMBER(1)",
            "object": "CLOB",
            "array": "CLOB"
        }

        return type_mapping.get(field_type, "VARCHAR2(4000)")
```

### **Advanced Target Features**

#### **Upsert Operations**

```python
def _upsert_records(self) -> None:
    """Perform upsert operations using Oracle MERGE statement."""
    if not self.records_to_drain:
        return

    # Build MERGE statement for upsert
    merge_sql = self._build_upsert_merge_statement()

    # Execute upsert with FLEXT DB Oracle
    upsert_result = self.oracle_api.execute_query(merge_sql, {
        "records": self.records_to_drain
    })

    if upsert_result.is_failure:
        raise RuntimeError(f"Upsert failed: {upsert_result.error}")

def _build_upsert_merge_statement(self) -> str:
    """Build Oracle MERGE statement for upsert operations."""
    # Implementation for Oracle-specific MERGE syntax
    return f"""
    MERGE INTO {self.full_table_name} target
    USING (
        SELECT * FROM TABLE(:records)
    ) source ON (target.id = source.id)
    WHEN MATCHED THEN
        UPDATE SET {self._get_update_columns()}
    WHEN NOT MATCHED THEN
        INSERT ({self._get_insert_columns()})
        VALUES ({self._get_insert_values()})
    """
```

## 🔄 DBT Integration

### **Oracle DBT Models**

Create DBT models that work with Oracle using FLEXT DB Oracle connection patterns:

```yaml
# flext-dbt-oracle/profiles.yml
flext_oracle:
  outputs:
    dev:
      type: oracle
      host: "{{ env_var('FLEXT_TARGET_ORACLE_HOST') }}"
      port: "{{ env_var('FLEXT_TARGET_ORACLE_PORT') | as_number }}"
      service: "{{ env_var('FLEXT_TARGET_ORACLE_SERVICE_NAME') }}"
      user: "{{ env_var('FLEXT_TARGET_ORACLE_USERNAME') }}"
      password: "{{ env_var('FLEXT_TARGET_ORACLE_PASSWORD') }}"
      schema: "{{ env_var('FLEXT_TARGET_ORACLE_SCHEMA', 'ANALYTICS') }}"
      threads: 4
  target: dev
```

### **Oracle-Specific DBT Macros**

```sql
-- flext-dbt-oracle/macros/oracle_utils.sql
{% macro oracle_get_columns_in_query(select_sql) %}
  {% set sql %}
    SELECT column_name, data_type
    FROM ({{ select_sql }}) sample_query
    WHERE ROWNUM = 0
  {% endset %}

  {% if execute %}
    {% set results = run_query(sql) %}
    {% set columns = results.columns[0].values() %}
    {% set data_types = results.columns[1].values() %}
  {% endif %}

  {% set column_list = [] %}
  {% for column in columns %}
    {% set _ = column_list.append(column) %}
  {% endfor %}

  {{ return(column_list) }}
{% endmacro %}

{% macro oracle_optimize_table(table_name) %}
  {% set sql %}
    ALTER TABLE {{ table_name }} ENABLE ROW MOVEMENT;
    ALTER TABLE {{ table_name }} SHRINK SPACE;
  {% endset %}

  {{ run_query(sql) }}
{% endmacro %}
```

## 🎼 Meltano Orchestration

### **Meltano Project Configuration**

Configure Meltano to orchestrate Oracle data pipelines:

```yaml
# meltano.yml
version: 1
default_environment: dev
project_id: flext-oracle-pipeline

environments:
  - name: dev
    config:
      plugins:
        extractors:
          - name: tap-oracle
            pip_url: flext-tap-oracle
        loaders:
          - name: target-oracle
            pip_url: flext-target-oracle

plugins:
  extractors:
    - name: tap-oracle
      namespace: tap_oracle
      pip_url: flext-tap-oracle
      executable: tap-oracle
      capabilities:
        - catalog
        - discover
        - properties
        - state
      settings:
        - name: host
          kind: string
          description: Oracle hostname
        - name: port
          kind: integer
          default: 1521
        - name: service_name
          kind: string
        - name: username
          kind: string
        - name: password
          kind: password
        - name: schema
          kind: string
      select:
        - "employees.*"
        - "departments.*"

  loaders:
    - name: target-oracle
      namespace: target_oracle
      pip_url: flext-target-oracle
      executable: target-oracle
      settings:
        - name: host
          kind: string
        - name: port
          kind: integer
          default: 1521
        - name: service_name
          kind: string
        - name: username
          kind: string
        - name: password
          kind: password
        - name: default_target_schema
          kind: string
          default: ANALYTICS

  transformers:
    - name: dbt-oracle
      namespace: dbt_oracle
      pip_url: flext-dbt-oracle
      executable: dbt

jobs:
  - name: oracle_to_oracle_elt
    tasks:
      - tap-oracle target-oracle
      - dbt-oracle:run
      - dbt-oracle:test
```

### **Running Meltano Pipelines**

```bash
# Install plugins
meltano install

# Discover Oracle schema
meltano invoke tap-oracle --discover > catalog.json

# Run full ELT pipeline
meltano run tap-oracle target-oracle dbt-oracle:run

# Run with state management for incremental extraction
meltano run tap-oracle target-oracle --state-backend=azure
```

## 📊 Performance Optimization

### **Connection Pool Configuration**

```python
# Optimize connection pooling for Singer components
oracle_config = FlextDbOracleConfig(
    host="oracle-server",
    service_name="PROD",
    username="etl_user",
    password="secure_password",
    pool_min=5,           # Minimum connections for Singer workloads
    pool_max=25,          # Maximum connections for parallel extraction
    pool_increment=2,     # Connection increment for scaling
    timeout=60            # Connection timeout for long-running extracts
)
```

### **Bulk Operations**

```python
# Optimize bulk insert performance
def optimize_bulk_insert(self, records: List[Dict]) -> FlextResult[None]:
    """Optimized bulk insert for Singer targets."""

    # Use Oracle-specific bulk loading
    bulk_result = self.oracle_api.bulk_insert(
        schema=self.target_schema,
        table=self.stream_name,
        records=records,
        batch_size=50000,      # Large batch size for performance
        use_bulk_api=True,     # Use Oracle bulk API
        parallel_degree=4      # Parallel loading
    )

    return bulk_result
```

## 🔐 Security Integration

### **Secure Configuration**

```python
# Use FLEXT DB Oracle's secure configuration patterns
from flext_db_oracle import FlextDbOracleConfig
from pydantic import SecretStr

# Singer configuration with security
class SecureSingerConfig:
    def __init__(self):
        self.oracle_config = FlextDbOracleConfig(
            host=os.getenv("ORACLE_HOST"),
            service_name=os.getenv("ORACLE_SERVICE"),
            username=os.getenv("ORACLE_USER"),
            password=SecretStr(os.getenv("ORACLE_PASSWORD")),  # Secure password handling
            ssl_enabled=True,                                   # Enable SSL
            ssl_cert_path="/path/to/oracle-cert.pem"          # SSL certificate
        )
```

### **Audit Logging**

```python
# Enable audit logging for Singer operations
def setup_singer_auditing(self):
    """Setup audit logging for Singer components."""

    # Configure FLEXT DB Oracle observability
    self.oracle_api.observability.enable_audit_logging(
        log_level="INFO",
        include_data_samples=False,  # Don't log sensitive data
        audit_operations=["INSERT", "UPDATE", "DELETE", "SELECT"]
    )
```

## 🎯 Best Practices

### **Schema Management**

1. **Use FLEXT DB Oracle metadata services** for consistent schema discovery
2. **Implement schema evolution handling** in both taps and targets
3. **Validate data types** during schema mapping

### **Performance**

1. **Leverage connection pooling** for all Singer components
2. **Use bulk operations** for large data volumes
3. **Implement parallel processing** where appropriate
4. **Monitor Oracle performance** using built-in observability

### **Error Handling**

1. **Use FlextResult patterns** consistently across all components
2. **Implement retry logic** for transient Oracle issues
3. **Log errors comprehensively** for debugging
4. **Handle connection failures gracefully**

### **Configuration**

1. **Follow Meltano conventions** for environment variables
2. **Use secure credential management** with SecretStr
3. **Implement configuration validation** using Pydantic
4. **Support both development and production environments**

---

This integration guide ensures that all Oracle-based Singer components built on FLEXT DB Oracle follow consistent patterns and leverage the full power of the enterprise-grade Oracle integration library.
