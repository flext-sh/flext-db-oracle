# FLEXT DB Oracle Quick Start Guide

**Get up and running with Oracle database integration in 5 minutes**

This quick start guide will help you set up and use FLEXT DB Oracle for enterprise Oracle database integration. Follow these steps to establish your first connection and start executing operations.

## 🚀 Prerequisites

### **System Requirements**

- **Python**: 3.13+ (required)
- **Oracle Client**: Oracle Instant Client 21c+ (recommended)
- **Poetry**: For dependency management
- **Oracle Database**: Access to Oracle 11g+ database

### **Oracle Database Access**

You'll need:

- Oracle server hostname and port
- Database service name or SID
- Valid username and password
- Network connectivity to Oracle server

## ⚡ 5-Minute Setup

### **Step 1: Installation**

```bash
# Clone the FLEXT ecosystem (if not already done)
git clone https://github.com/flext-sh/flext.git
cd flext/flext-db-oracle

# Install with Poetry
poetry install

# Activate virtual environment
poetry shell
```

### **Step 2: Oracle Client Setup**

#### **Linux/Ubuntu**

```bash
# Download Oracle Instant Client
wget https://download.oracle.com/otn_software/linux/instantclient/216000/instantclient-basic-linux.x64-21.6.0.0.0dbru.zip

# Extract and setup
unzip instantclient-basic-linux.x64-21.6.0.0.0dbru.zip
sudo mv instantclient_21_6 /opt/oracle

# Set environment variables
echo 'export ORACLE_HOME=/opt/oracle/instantclient_21_6' >> ~/.bashrc
echo 'export LD_LIBRARY_PATH=$ORACLE_HOME:$LD_LIBRARY_PATH' >> ~/.bashrc
echo 'export PATH=$ORACLE_HOME:$PATH' >> ~/.bashrc
source ~/.bashrc
```

#### **macOS**

```bash
# Install via Homebrew
brew install instantclient-basic

# Or download manually and setup paths
export ORACLE_HOME=/usr/local/lib/instantclient_21_6
export DYLD_LIBRARY_PATH=$ORACLE_HOME:$DYLD_LIBRARY_PATH
```

#### **Windows**

```powershell
# Download and extract Oracle Instant Client
# Add to PATH environment variable
$env:PATH += ";C:\instantclient_21_6"
```

### **Step 3: Environment Configuration**

Create a `.env` file or set environment variables:

```bash
# Required Oracle connection parameters
export FLEXT_TARGET_ORACLE_HOST="your-oracle-server.com"
export FLEXT_TARGET_ORACLE_PORT="1521"
export FLEXT_TARGET_ORACLE_SERVICE_NAME="PROD"  # or your service name
export FLEXT_TARGET_ORACLE_USERNAME="your_username"
export FLEXT_TARGET_ORACLE_PASSWORD="your_password"

# Optional parameters
export FLEXT_TARGET_ORACLE_SCHEMA="YOUR_SCHEMA"
export FLEXT_TARGET_ORACLE_POOL_MIN="2"
export FLEXT_TARGET_ORACLE_POOL_MAX="10"
```

### **Step 4: Test Connection**

```python
# test_connection.py
from flext_db_oracle import FlextDbOracleApi

def test_oracle_connection():
    """Test Oracle database connection."""

    # Create API instance from environment
    api = FlextDbOracleApi.from_env("quickstart")

    # Test connection
    print("🔌 Testing Oracle connection...")
    connect_result = api.connect()

    if connect_result.is_success:
        print("✅ Connection successful!")

        # Test basic query
        print("🔍 Testing basic query...")
        query_result = api.execute_query("SELECT 1 FROM DUAL")

        if query_result.is_success:
            print("✅ Query test successful!")
            print(f"Result: {query_result.value.rows}")
        else:
            print(f"❌ Query failed: {query_result.error}")

        # Clean up
        api.disconnect()
        print("📤 Connection closed")

    else:
        print(f"❌ Connection failed: {connect_result.error}")

if __name__ == "__main__":
    test_oracle_connection()
```

Run the test:

```bash
python test_connection.py
```

## 🎯 Basic Usage Examples

### **Example 1: Simple Query Execution**

```python
from flext_db_oracle import FlextDbOracleApi, FlextDbOracleConfig

# Method 1: Load from environment (recommended)
api = FlextDbOracleApi.from_env("my_app")

# Method 2: Direct configuration
config = FlextDbOracleConfig(
    host="oracle-server.company.com",
    port=1521,
    service_name="PROD",
    username="app_user",
    password="secure_password"
)
api = FlextDbOracleApi(config)

# Connect and execute query
connect_result = api.connect()
if connect_result.is_success:
    # Simple query
    result = api.execute_query("SELECT * FROM employees WHERE department_id = 10")

    if result.is_success:
        print(f"Found {len(result.value.rows)} employees")
        for row in result.value.rows:
            print(row)

    # Parameterized query (recommended for security)
    result = api.execute_query(
        "SELECT * FROM employees WHERE department_id = :dept_id AND salary > :min_salary",
        {"dept_id": 10, "min_salary": 50000}
    )

    if result.is_success:
        print(f"Found {len(result.value.rows)} high-paid employees")

    api.disconnect()
```

### **Example 2: Schema Introspection**

```python
from flext_db_oracle import FlextDbOracleApi

# Initialize and connect
api = FlextDbOracleApi.from_env()
api.connect()

# Get schema metadata
schema_result = api.get_schema_metadata("HR")
if schema_result.is_success:
    schema = schema_result.value

    print(f"📊 Schema '{schema.name}' Analysis:")
    print(f"  📋 Tables: {len(schema.tables)}")
    print(f"  👁️  Views: {len(schema.views)}")
    print(f"  🔢 Sequences: {len(schema.sequences)}")

    # Display table details
    for table in schema.tables[:5]:  # First 5 tables
        print(f"\n📋 Table: {table.name}")
        print(f"   Columns: {len(table.columns)}")
        print(f"   Row Count: {table.row_count or 'Unknown'}")

        # Show column details
        for col in table.columns[:3]:  # First 3 columns
            print(f"     - {col.name}: {col.data_type}")

api.disconnect()
```

### **Example 3: Bulk Data Operations**

```python
from flext_db_oracle import FlextDbOracleApi

# Initialize
api = FlextDbOracleApi.from_env()
api.connect()

# Bulk insert example
data = [
    [1, "John Doe", "Engineering", 75000],
    [2, "Jane Smith", "Marketing", 65000],
    [3, "Bob Wilson", "Sales", 55000]
]

bulk_result = api.bulk_insert(
    schema="HR",
    table="EMPLOYEES",
    columns=["EMPLOYEE_ID", "NAME", "DEPARTMENT", "SALARY"],
    values=data,
    batch_size=1000
)

if bulk_result.is_success:
    print(f"✅ Successfully inserted {bulk_result.value} rows")
else:
    print(f"❌ Bulk insert failed: {bulk_result.error}")

api.disconnect()
```

## 🐳 Docker Quick Start

### **Using Pre-built Oracle XE**

For development and testing, use Oracle XE in Docker:

```bash
# Start Oracle XE 21c
docker-compose -f docker-compose.oracle.yml up -d

# Wait for Oracle to be ready (check logs)
docker-compose -f docker-compose.oracle.yml logs -f oracle-xe

# When you see "DATABASE IS READY TO USE!", Oracle is ready
```

Update your environment variables for Docker:

```bash
export FLEXT_TARGET_ORACLE_HOST="localhost"
export FLEXT_TARGET_ORACLE_PORT="1521"
export FLEXT_TARGET_ORACLE_SERVICE_NAME="XEPDB1"
export FLEXT_TARGET_ORACLE_USERNAME="system"
export FLEXT_TARGET_ORACLE_PASSWORD="Oracle123"
```

### **Test Docker Setup**

```python
# docker_test.py
from flext_db_oracle import FlextDbOracleApi

def test_docker_oracle():
    """Test Oracle XE in Docker."""

    api = FlextDbOracleApi.from_env("docker_test")

    print("🐳 Testing Docker Oracle XE connection...")
    connect_result = api.connect()

    if connect_result.is_success:
        print("✅ Docker Oracle connection successful!")

        # Create test table
        ddl = """
        CREATE TABLE test_quickstart (
            id NUMBER PRIMARY KEY,
            name VARCHAR2(100),
            created_date DATE DEFAULT SYSDATE
        )
        """

        create_result = api.execute_ddl(ddl)
        if create_result.is_success:
            print("✅ Test table created")

            # Insert test data
            insert_result = api.execute_query(
                "INSERT INTO test_quickstart (id, name) VALUES (:id, :name)",
                {"id": 1, "name": "Quick Start Test"}
            )

            if insert_result.is_success:
                print("✅ Test data inserted")

                # Query test data
                select_result = api.execute_query("SELECT * FROM test_quickstart")
                if select_result.is_success:
                    print(f"✅ Retrieved {len(select_result.value.rows)} rows")
                    print(f"Data: {select_result.value.rows}")

        api.disconnect()
    else:
        print(f"❌ Connection failed: {connect_result.error}")

if __name__ == "__main__":
    test_docker_oracle()
```

## ✅ Verification Checklist

After setup, verify everything works:

### **Connection Test**

```bash
# Run connection test
python -c "
from flext_db_oracle import FlextDbOracleApi
api = FlextDbOracleApi.from_env()
result = api.connect()
print('✅ Connected!' if result.is_success else f'❌ Failed: {result.error}')
api.disconnect() if result.is_success else None
"
```

### **CLI Test**

```bash
# Test CLI interface
flext-db-oracle --help

# Test Oracle connection via CLI
flext-db-oracle test-connection
```

### **Schema Access Test**

```bash
# Test schema access
python -c "
from flext_db_oracle import FlextDbOracleApi
api = FlextDbOracleApi.from_env()
api.connect()
result = api.execute_query('SELECT COUNT(*) FROM user_tables')
print(f'✅ Schema access OK: {result.value.rows[0][0]} tables' if result.is_success else f'❌ Schema access failed: {result.error}')
api.disconnect()
"
```

## 🎯 Next Steps

Now that you have FLEXT DB Oracle working, explore these features:

### **Advanced Features**

- **[Plugin System](docs/plugins/README.md)** - Extend functionality with plugins
- **[Performance Optimization](docs/performance/README.md)** - Optimize for your workload
- **[Security Configuration](docs/security/README.md)** - Secure your Oracle connections

### **Integration Guides**

- **[Singer/Meltano Integration](docs/integration/singer.md)** - Build data pipelines
- **[FLEXT Services Integration](docs/integration/services.md)** - Integrate with FLEXT ecosystem
- **[API Integration](docs/integration/api.md)** - Build REST APIs

### **Development**

- **[Architecture Guide](docs/architecture/README.md)** - Understand the architecture
- **[API Reference](docs/api/README.md)** - Complete API documentation
- **[Configuration Guide](docs/configuration/README.md)** - Advanced configuration

## 🛠️ Troubleshooting

### **Common Issues**

#### **"No module named 'oracledb'"**

```bash
# Install Oracle client library
pip install oracledb

# Or reinstall with all dependencies
poetry install --with dev
```

#### **"DPI-1047: Cannot locate a 64-bit Oracle Client library"**

```bash
# Install Oracle Instant Client
# Linux:
sudo apt-get install libaio1
# Download and extract Oracle Instant Client
# Set LD_LIBRARY_PATH

# macOS:
brew install instantclient-basic

# Windows:
# Download Oracle Instant Client and add to PATH
```

#### **"ORA-12170: TNS:Connect timeout occurred"**

```bash
# Check network connectivity
telnet your-oracle-server 1521

# Verify environment variables
echo $FLEXT_TARGET_ORACLE_HOST
echo $FLEXT_TARGET_ORACLE_PORT
echo $FLEXT_TARGET_ORACLE_SERVICE_NAME
```

#### **"ORA-01017: invalid username/password"**

```bash
# Verify credentials
echo $FLEXT_TARGET_ORACLE_USERNAME
echo $FLEXT_TARGET_ORACLE_PASSWORD

# Test with SQL*Plus if available
sqlplus $FLEXT_TARGET_ORACLE_USERNAME/$FLEXT_TARGET_ORACLE_PASSWORD@$FLEXT_TARGET_ORACLE_HOST:$FLEXT_TARGET_ORACLE_PORT/$FLEXT_TARGET_ORACLE_SERVICE_NAME
```

### **Getting Help**

- **Documentation**: Check the complete [documentation](docs/README.md)
- **Examples**: See [examples/](examples/) directory for more examples
- **Issues**: Report issues on GitHub
- **Community**: Join the FLEXT community discussions

## 🎉 Success

You now have FLEXT DB Oracle up and running! This enterprise-grade Oracle integration library provides:

- ✅ **Type-safe Oracle connectivity** with FlextResult patterns
- ✅ **Connection pooling** for performance and scalability
- ✅ **Schema introspection** for metadata operations
- ✅ **Plugin system** for extensibility
- ✅ **FLEXT ecosystem integration** for data platforms
- ✅ **Security features** with SSL/TLS support
- ✅ **Comprehensive error handling** with detailed diagnostics

Start building your Oracle-powered applications with confidence using FLEXT DB Oracle!
