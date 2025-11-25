# FLEXT-DB-Oracle Project Guidelines

**Reference**: See [../CLAUDE.md](../CLAUDE.md) for FLEXT ecosystem standards and general rules.

---

## Project Overview

**FLEXT-DB-Oracle** is the enterprise Oracle Database integration foundation for the FLEXT ecosystem, providing Oracle connectivity, SQL operations, schema management, and database infrastructure using SQLAlchemy 2 + oracledb.

**Version**: 0.9.0  
**Status**: Production-ready  
**Python**: 3.13+

**Key Architecture**:
- Single consolidated API class: `FlextDbOracleApi`
- Wraps SQLAlchemy 2.0 and oracledb driver internally
- Uses flext-core patterns: `FlextResult[T]` railway pattern, `FlextService` base class

**CRITICAL CONSTRAINT - ZERO TOLERANCE**:
- **api.py** is the ONLY file that may import SQLAlchemy directly
- **All other code must use the FlextDbOracleApi abstraction**
- Breaking this constraint violates the foundation library's core purpose

---

## Essential Commands

```bash
# Setup and validation
make setup                    # Complete development environment setup
make validate                 # Complete validation (lint + type + security + test)
make check                    # Quick check (lint + type)

# Quality gates
make lint                     # Ruff linting
make type-check               # Pyrefly type checking
make security                 # Bandit security scan
make test                     # Run tests
```

---

## Key Patterns

### Oracle Database Operations

```python
from flext_core import FlextResult
from flext_db_oracle import FlextDbOracleApi

db = FlextDbOracleApi()

# Execute query
result = db.execute_query("SELECT * FROM users")
if result.is_success:
    rows = result.unwrap()
```

---

## Critical Development Rules

### ZERO TOLERANCE Policies

**ABSOLUTELY FORBIDDEN**:
- ❌ Direct SQLAlchemy imports outside api.py
- ❌ Exception-based error handling (use FlextResult)
- ❌ Type ignores or `Any` types
- ❌ Mockpatch in tests

**MANDATORY**:
- ✅ Use `FlextResult[T]` for all operations
- ✅ Use FlextDbOracleApi abstraction for all database operations
- ✅ Complete type annotations
- ✅ Zero Ruff violations

---

**Additional Resources**: [../CLAUDE.md](../CLAUDE.md) (workspace), [README.md](README.md) (overview)
