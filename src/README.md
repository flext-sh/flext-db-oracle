# FLEXT DB Oracle - Source Code

This directory contains the complete source code for FLEXT DB Oracle, an enterprise Oracle database integration library built on Clean Architecture principles.

## 📁 Module Organization

### **Core Application Layer**

- **`flext_db_oracle/api.py`** - Main application service providing high-level Oracle operations
- **`flext_db_oracle/cli.py`** - Command-line interface for Oracle database operations

### **Configuration and Infrastructure Layer**

- **`flext_db_oracle/config.py`** - Configuration management with Pydantic validation
- **`flext_db_oracle/connection.py`** - Connection pooling and resource management
- **`flext_db_oracle/observability.py`** - Performance monitoring and metrics collection

### **Domain and Metadata Layer**

- **`flext_db_oracle/metadata.py`** - Oracle schema introspection and DDL generation
- **`flext_db_oracle/types.py`** - Type definitions and Pydantic models
- **`flext_db_oracle/plugins.py`** - Plugin system for extensible functionality

### **Foundation Layer**

- **`flext_db_oracle/__init__.py`** - Public API exports and library initialization
- **`flext_db_oracle/constants.py`** - Oracle-specific constants and defaults
- **`flext_db_oracle/exceptions.py`** - Oracle-specific exception hierarchy
- **`flext_db_oracle/py.typed`** - Type checking marker for MyPy compliance

## 🏗️ Architecture Patterns

### **Clean Architecture Implementation**

The source code follows Clean Architecture principles with clear layer separation:

```
┌─────────────────────────────────────────────────────────────────┐
│                    Application Layer                            │
│  api.py: FlextDbOracleApi (main service)                      │
│  cli.py: Command-line interface                               │
├─────────────────────────────────────────────────────────────────┤
│                      Domain Layer                               │
│  metadata.py: Oracle schema models                            │
│  types.py: Domain entities and value objects                  │
├─────────────────────────────────────────────────────────────────┤
│                  Infrastructure Layer                           │
│  config.py: Configuration management                          │
│  connection.py: Connection pooling                            │
│  observability.py: Monitoring and metrics                     │
│  plugins.py: Plugin system                                    │
├─────────────────────────────────────────────────────────────────┤
│                    Foundation Layer                             │
│  __init__.py: Public API gateway                              │
│  constants.py: System constants                               │
│  exceptions.py: Error handling                                │
└─────────────────────────────────────────────────────────────────┘
```

### **SOLID Principles Implementation**

- **Single Responsibility**: Each module has one clear responsibility
- **Open/Closed**: Plugin system allows extension without modification
- **Liskov Substitution**: All implementations follow interface contracts
- **Interface Segregation**: Specific interfaces for different concerns
- **Dependency Inversion**: Depends on abstractions, not concretions

### **FLEXT Core Integration**

All modules integrate with FLEXT Core patterns:

- **FlextResult[T]**: Railway-oriented programming for error handling
- **FlextContainer**: Dependency injection for service management
- **FlextSettings**: Configuration management with validation
- **FlextModels.Entity**: Domain-driven design entity patterns

## 🎯 Module Naming Conventions

### **Public API Naming**

- All public classes use `FlextDbOracle` prefix (e.g., `FlextDbOracleApi`)
- Type aliases use `TDbOracle` prefix (e.g., `TDbOracleQueryResult`)
- Constants use `ORACLE_` prefix for Oracle-specific values

### **Import Patterns**

```python
# Primary imports (direct imports only - STRICT RULE)
from flext_db_oracle.api import FlextDbOracleApi
from flext_db_oracle.settings import FlextDbOracleSettings
from flext_db_oracle.typings import FlextDbOracleTypes

# Metadata operations (direct imports only)
# Use FlextDbOracleApi for metadata operations - NO aliases allowed

# Plugin system
from flext_db_oracle.plugins import register_all_oracle_plugins

# Type definitions
from flext_db_oracle.types import TDbOracleQueryResult, TDbOracleConnectionStatus
```

## 📊 Code Quality Standards

### **Type Safety Requirements**

- **95%+ type annotation coverage** across all modules
- **Strict MyPy compliance** with no untyped code allowed
- **Enterprise-grade type patterns** using Union, Optional, Dict, List

### **Documentation Standards**

- **Comprehensive module docstrings** with architecture context
- **Complete function documentation** with parameters, returns, and examples
- **Integration examples** showing cross-ecosystem usage
- **Professional English** without marketing content

### **Testing Integration**

- **Unit tests** for business logic without external dependencies
- **Integration tests** for Oracle database operations
- **Performance tests** for optimization validation
- **Security tests** for credential and connection security

## 🔧 Development Guidelines

### **Adding New Modules**

1. Follow Clean Architecture layer placement
2. Use appropriate `FlextDbOracle` prefix for public APIs
3. Implement comprehensive type annotations
4. Add module-specific README.md documentation
5. Include enterprise-grade docstrings with examples

### **Modifying Existing Modules**

1. Maintain backward compatibility for public APIs
2. Update type annotations when changing signatures
3. Preserve SOLID principles and architectural boundaries
4. Update documentation and examples as needed
5. Run full test suite to validate changes

### **Quality Gates**

All code must pass these validation steps:

- `make lint` - Ruff linting with ALL rules enabled
- `make type-check` - MyPy strict type checking
- `make test` - Test suite with 90%+ coverage requirement
- `make security` - Security scanning with Bandit and pip-audit

---

This source code structure provides the foundation for enterprise Oracle database integration within the FLEXT ecosystem, following industry best practices and architectural patterns.
