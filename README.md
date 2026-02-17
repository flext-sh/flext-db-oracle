# FLEXT-DB-Oracle

[![Python 3.13+](https://img.shields.io/badge/python-3.13+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

**FLEXT-DB-Oracle** is the definitive Oracle Database integration library for the FLEXT ecosystem. Built on top of **SQLAlchemy 2.0** and **python-oracledb**, it provides enterprise-grade connectivity, robust connection pooling, and strict type safety for all Oracle interactions.

Part of the [FLEXT](https://github.com/flext-sh/flext) ecosystem.

## 🚀 Key Features

- **Enterprise Connectivity**: High-performance connection pooling with automatic failover and reconnection strategies.
- **Modern Modern SQLAlchemy**: Full support for SQLAlchemy 2.0+ patterns, including strict typing and modern query construction.
- **Schema Introspection**: Comprehensive metadata extraction for tables, columns, constraints, and indexes.
- **Railway-Oriented**: All database operations return `FlextResult[T]`, ensuring predictable and safe error handling.
- **Type Safety**: Strictly typed API compliant with MyPy strict mode.
- **Secure**: Built-in credential management and secure connection handling.

## 📦 Installation

To install `flext-db-oracle`:

```bash
pip install flext-db-oracle
```

Or with Poetry:

```bash
poetry add flext-db-oracle
```

## 🛠️ Usage

### Basic Connection and Query

Connect to Oracle and execute queries safely.

```python
from flext_db_oracle.api import FlextDbOracleApi
from flext_db_oracle.models import FlextDbOracleModels

# 1. Configure the Connection
config = FlextDbOracleModels.OracleConfig(
    host="oracle-db.example.com",
    port=1521,
    service_name="ORCL",
    username="app_user",
    password="secure_password"
)

# 2. Initialize the API
db = FlextDbOracleApi(config)

# 3. Execute a Query
# Returns FlextResult[List[Dict[str, Any]]]
result = db.query(
    sql="SELECT * FROM employees WHERE department_id = :dept_id",
    params={"dept_id": 10}
)

if result.is_success:
    rows = result.unwrap()
    print(f"Retrieved {len(rows)} employees.")
else:
    print(f"Query failed: {result.error}")
```

### Schema Introspection

Inspect database metadata with ease.

```python
# Introspect a specific table
table_result = db.get_table_schema("employees")

if table_result.is_success:
    schema = table_result.unwrap()
    print(f"Table: {schema.name}")
    for col in schema.columns:
        print(f" - {col.name}: {col.type}")
```

### Connection Management

Use the `connect()` context manager for manual connection handling when needed.

```python
with db.connect() as conn:
    # conn is a standard SQLAlchemy Connection object
    conn.execute(text("UPDATE employees SET status = 'ACTIVE'"))
    conn.commit()
```

## 🏗️ Architecture

FLEXT-DB-Oracle serves as the data persistence layer for Oracle components in the FLEXT ecosystem:

- **API Layer**: `FlextDbOracleApi` provides the main entry point for applications.
- **Service Layer**: Handles connection lifecycles, transaction management, and schema logic.
- **Infrastructure Adapter**: Wraps `SQLAlchemy` and `oracledb` to provide a unified, type-safe interface.

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](docs/development.md) for details on setting up your environment, running tests against local Oracle containers, and submitting pull requests.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
