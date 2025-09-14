# Architecture

Oracle database integration architecture for flext-db-oracle v0.9.0.

## Module Structure

```
src/flext_db_oracle/
├── api.py           # FlextDbOracleApi (36 methods)
├── services.py      # Database operations (8 helper classes)
├── models.py        # OracleConfig and data models
├── client.py        # CLI client (SimpleNamespace placeholders)
├── cli.py           # CLI service (2 helper classes)
├── connection.py    # Connection management
├── metadata.py      # Schema introspection
├── utilities.py     # Helper functions
├── constants.py     # Configuration constants
├── exceptions.py    # Oracle-specific exceptions
├── mixins.py        # Validation mixins
└── plugins.py       # Plugin system
```

## Data Flow

1. **Configuration**: OracleConfig from environment or direct setup
2. **API Layer**: FlextDbOracleApi orchestrates operations
3. **Services Layer**: FlextDbOracleServices handles SQL operations
4. **SQLAlchemy**: Text constructs with python-oracledb driver
5. **Oracle Database**: Connection via SQLAlchemy engine

## Error Handling

All operations return FlextResult[T] for type-safe error handling:

```python
result = api.query("SELECT 1 FROM DUAL")
if result.is_success:
    data = result.value
else:
    error = result.error
```

## Connection Management

- SQLAlchemy 2.0 engine with connection pooling
- python-oracledb driver (version 3.2.0+)
- Connection string: `oracle+oracledb://user:pass@host:port/service`

## Limitations

- Synchronous operations only (no async/await)
- SQLAlchemy abstraction only (no direct python-oracledb)
- CLI placeholders (SimpleNamespace in client.py:60-67)

---

Updated: September 17, 2025 | Version: 0.9.0