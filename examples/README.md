# FLEXT DB Oracle Examples

This directory contains examples demonstrating real-world usage patterns for FLEXT DB Oracle. Each example follows practices and showcases different integration scenarios within the FLEXT ecosystem.

## 📋 Example Categories

### **Core Integration Examples**

#### **`04_comprehensive_oracle_usage.py`**

**Complete Oracle Integration Workflow**

Demonstrates comprehensive Oracle database operations including:

- Configuration management and environment-based setup
- Connection pooling and lifecycle management
- Schema introspection and metadata operations
- Query execution with performance monitoring
- Plugin system integration and custom functionality
- Error handling and observability integration

**Key Features:**

- Enterprise-grade error handling with FlextResult patterns
- Performance monitoring and metrics collection
- Plugin system demonstration with real Oracle operations
- Configuration validation and multi-environment support

#### **`07_sqlalchemy2.py`**

**SQLAlchemy 2 Integration Patterns**

Shows modern SQLAlchemy 2 usage patterns with FLEXT DB Oracle:

- Modern /patterns for database operations
- Connection session management and transaction handling
- ORM integration with Oracle-specific optimizations
- Advanced query building and execution patterns

**Key Features:**

- SQLAlchemy 2.x integration with Clean Architecture
- Transaction management and connection pooling
- Oracle-specific SQL optimizations and hints
- Type-safe query building and result handling

### **CLI and Tooling Examples**

#### **`06_cli.py`**

**Command Line Interface Demonstrations**

Comprehensive CLI usage examples covering:

- Database connection testing and validation
- Query execution with multiple output formats
- Schema exploration and metadata extraction
- Plugin management and registration
- Health monitoring and status checking

**Key Features:**

- Rich terminal formatting and user experience
- Multiple output formats (table, JSON, YAML, CSV)
- Error handling and user feedback patterns
- Integration with FLEXT CLI ecosystem

## 🚀 Running Examples

### **Prerequisites**

#### **Oracle Database Setup**

```bash
# Start Oracle XE for examples
docker-compose -f docker-compose.oracle.yml up -d

# Wait for Oracle to be ready
docker logs -f flext-oracle-xe

# Verify Oracle connectivity
sqlplus sys/oracle@localhost:1521/XE as sysdba
```

#### **Environment Configuration**

```bash
# Set required environment variables
export FLEXT_TARGET_ORACLE_HOST=localhost
export FLEXT_TARGET_ORACLE_PORT=1521
export FLEXT_TARGET_ORACLE_SERVICE_NAME=XEPDB1
export FLEXT_TARGET_ORACLE_USERNAME=flext_user
export FLEXT_TARGET_ORACLE_PASSWORD=flext_password

# Optional configuration for advanced features
export FLEXT_TARGET_ORACLE_SCHEMA=FLEXT_EXAMPLES
export FLEXT_TARGET_ORACLE_POOL_MIN=2
export FLEXT_TARGET_ORACLE_POOL_MAX=10
```

### **Example Execution**

```bash
# Run comprehensive Oracle example
cd examples/
python 04_comprehensive_oracle_usage.py

# Run SQLAlchemy 2 integration example
python 07_sqlalchemy2.py

# Run CLI examples
python 06_cli.py

# Run all examples with validation
make run-examples
```

## 🎯 Example Details

### **Comprehensive Oracle Usage Example**

```python
"""
04_comprehensive_oracle_usage.py - Complete Integration Demonstration

This example shows:
1. Configuration loading and validation
2. Connection establishment with error handling
3. Schema introspection and metadata extraction
4. Query execution with performance monitoring
5. Plugin system integration
6. Observability and monitoring
7. Graceful error handling and cleanup
"""

from flext_db_oracle import FlextDbOracleApi, FlextDbOracleConfig
from flext_core import FlextResult

def demonstrate_comprehensive_usage():
    """Demonstrate comprehensive Oracle database usage."""

    # Load configuration from environment
    config_result = FlextDbOracleConfig.from_env()
    if config_result.is_failure:
        print(f"Configuration failed: {config_result.error}")
        return

    config = config_result.value
    api = FlextDbOracleApi(config)

    # Demonstrate complete workflow
    with api:
        # Test connection
        connection_result = api.test_connection()
        print(f"Connection: {'✅ Success' if connection_result.unwrap_or(False) else '❌ Failed'}")

        # Query execution using modern unwrap_or pattern
        query_result = api.execute_query("SELECT SYSDATE FROM DUAL")
        query_data = query_result.unwrap_or(None)
        if query_data is not None:
            print(f"Current time: {query_data.rows[0][0]}")

        # Schema operations using modern unwrap_or pattern
        schemas_result = api.get_schemas()
        schemas_data = schemas_result.unwrap_or([])
        if schemas_data:
            print(f"Available schemas: {len(schemas_data)}")

if __name__ == "__main__":
    demonstrate_comprehensive_usage()
```

### **SQLAlchemy 2 Integration Example**

```python
"""
07_sqlalchemy2.py - Modern SQLAlchemy Integration

Demonstrates:
1. SQLAlchemy 2.x patterns with Oracle
2. Connection session management
3. Transaction handling and rollback
4. ORM integration with Oracle-specific features
5. Performance optimization techniques
"""

from flext_db_oracle import FlextDbOracleConnection
from sqlalchemy import text, select
from sqlalchemy.orm import Session

def demonstrate_sqlalchemy2_patterns():
    """Demonstrate SQLAlchemy 2 integration patterns."""

    connection = FlextDbOracleConnection.from_env()

    with connection:
        # Session-based operations
        with connection.session() as session:
            # Raw SQL execution
            result = session.execute(text("SELECT COUNT(*) FROM user_tables"))
            table_count = result.scalar()
            print(f"User tables: {table_count}")

            # Transaction management
            with session.begin():
                # Transactional operations here
                session.execute(text("INSERT INTO audit_log VALUES (SYSDATE, 'Example')"))
                # Automatic commit on success, rollback on exception

if __name__ == "__main__":
    demonstrate_sqlalchemy2_patterns()
```

### **CLI Usage Examples**

```python
"""
06_cli.py - Command Line Interface Demonstrations

Shows practical CLI usage patterns:
1. Connection testing and validation
2. Query execution with formatting
3. Schema exploration workflows
4. Plugin management operations
5. Health monitoring and diagnostics
"""

import subprocess
import os

def demonstrate_cli_patterns():
    """Demonstrate CLI usage patterns."""

    # Set environment for examples
    env = os.environ.copy()
    env.update({
        'FLEXT_TARGET_ORACLE_HOST': 'localhost',
        'FLEXT_TARGET_ORACLE_PORT': '1521',
        'FLEXT_TARGET_ORACLE_SERVICE_NAME': 'XEPDB1',
        'FLEXT_TARGET_ORACLE_USERNAME': 'flext_user',
        'FLEXT_TARGET_ORACLE_PASSWORD': 'flext_password'
    })

    # Test connection (pseudo-code; prefer in-process or wrappers)
    print("Testing connection...")
    # rc, out, err = run([sys.executable, '-m', 'flext_db_oracle.cli', 'connect-env'], env=env)
    # Simulated result object below for documentation purposes:
    class Result:
        """Lightweight result for documentation."""
        def __init__(self, returncode: int, stdout: str = '', stderr: str = '') -> None:
            self.returncode = returncode
            self.stdout = stdout
            self.stderr = stderr
    result = Result(0, 'Connected OK')

    if result.returncode == 0:
        print("✅ Connection successful")

        # Execute sample query
        print("\nExecuting query...")
        # rc2, out2, err2 = run([sys.executable, '-m', 'flext_db_oracle.cli', 'query', '--sql', 'SELECT table_name FROM user_tables'], env=env)
        out2 = "TABLE_NAME\nUSERS\nORDERS\n"  # simulated
        print(out2)
    else:
        print(f"❌ Connection failed: {result.stderr}")

if __name__ == "__main__":
    demonstrate_cli_patterns()
```

## 📊 Example Use Cases

### **Development Scenarios**

#### **Local Development Setup**

```python
# Quick setup for local development
def setup_local_development():
    """Setup local development environment."""
    config = FlextDbOracleConfig(
        host="localhost",
        port=1521,
        service_name="XEPDB1",
        username="dev_user",
        password=SecretStr("dev_password"),
        pool_min=1,
        pool_max=5
    )
    return FlextDbOracleApi(config)
```

#### **Testing and Validation**

```python
# Configuration for testing scenarios
def setup_testing_environment():
    """Setup testing environment with isolated database."""
    config = FlextDbOracleConfig.from_env("TEST_ORACLE_")
    api = FlextDbOracleApi(config, context_name="testing")

    # Enable comprehensive logging for testing
    api.enable_debug_logging()
    return api
```

### **Production Scenarios**

#### **Enterprise Configuration**

```python
# Production-ready configuration with security
def setup_production_environment():
    """Setup production environment with enterprise features."""
    config = FlextDbOracleConfig.from_env("PROD_ORACLE_")

    # Validate production configuration
    validation_result = config.validate_domain_rules()
    if validation_result.is_failure:
        raise RuntimeError(f"Invalid production config: {validation_result.error}")

    # Create API with production settings
    api = FlextDbOracleApi(config, context_name="production")

    # Register monitoring plugins
from flext_db_oracle.plugins import register_all_oracle_plugins
    register_all_oracle_plugins(api)

    return api
```

#### **High-Availability Setup**

```python
# High-availability configuration with failover
def setup_ha_environment():
    """Setup high-availability Oracle environment."""
    primary_config = FlextDbOracleConfig.from_env("PRIMARY_ORACLE_")

    api = FlextDbOracleApi(primary_config, context_name="ha_primary")

    # Configure connection pooling for HA
    api.configure_ha_pooling(
        min_connections=10,
        max_connections=50,
        retry_attempts=3,
        failover_timeout=30
    )

    return api
```

## 🔧 Development Guidelines

### **Creating New Examples**

1. **Follow naming convention**: `##_descriptive_name.py`
2. **Include comprehensive docstrings**: Explain purpose and key concepts
3. **Handle errors gracefully**: Use FlextResult patterns throughout
4. **Demonstrate best practices**: Show production patterns
5. **Include cleanup code**: Proper resource management

### **Example Structure Template**

```python
"""
Example Title - Brief Description

This example demonstrates:
1. Primary concept or workflow
2. Key integration points
3. Best practices showcase
4. Error handling patterns

Prerequisites:
- Oracle database access
- Environment variables configured
- Required dependencies installed

Usage:
    python example_name.py
"""

from flext_db_oracle import FlextDbOracleApi
from flext_core import FlextResult

def main() -> None:
    """Main example execution function."""
    try:
        # Example implementation
        demonstrate_feature()

    except Exception as e:
        print(f"Example failed: {e}")
        return 1

    print("Example completed successfully")
    return 0

def demonstrate_feature() -> None:
    """Demonstrate specific feature or workflow."""
    # Implementation with proper error handling
    pass

if __name__ == "__main__":
    exit(main())
```

### **Testing Examples**

All examples include self-validation and testing:

```bash
# Validate all examples
make validate-examples

# Run examples with test data
make test-examples

# Performance benchmark examples
make benchmark-examples
```

## 🧭 Integration Patterns

### **FLEXT Ecosystem Integration**

Examples demonstrate integration with:

- **flext-core**: Foundation patterns and result handling
- **flext-observability**: Monitoring and metrics collection
- **flext-cli**: Command-line interface patterns
- **flext-plugin**: Extensibility and plugin development

### **External System Integration**

Examples show integration with:

- **SQLAlchemy 2**: Modern ORM patterns
- **Pydantic**: Configuration and validation
- **Rich**: Terminal formatting and user experience
- **Docker**: Containerized Oracle environments

---

These examples provide practical, production-ready patterns for integrating FLEXT DB Oracle into real-world applications while maintaining enterprise-grade quality standards.
