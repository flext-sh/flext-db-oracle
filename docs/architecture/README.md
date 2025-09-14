# FLEXT DB Oracle Architecture

**Clean Architecture and Domain-Driven Design Implementation**

FLEXT DB Oracle implements Clean Architecture principles combined with Domain-Driven Design (DDD) to provide a maintainable, testable, and extensible Oracle database integration solution within the FLEXT ecosystem.

## 🏗️ Architectural Overview

### **Clean Architecture Layers**

```
┌─────────────────────────────────────────────────────────────────┐
│                         FLEXT DB ORACLE                         │
├─────────────────────────────────────────────────────────────────┤
│ Presentation Layer (CLI, External Interfaces)                  │
│  • cli.py - Command-line interface                             │
│  • External API contracts                                      │
├─────────────────────────────────────────────────────────────────┤
│ Application Layer (Use Cases, Services)                        │
│  • api.py - FlextDbOracleApi (Application Service)            │
│  • Plugin orchestration and workflow coordination              │
│  • Use case implementations                                    │
├─────────────────────────────────────────────────────────────────┤
│ Domain Layer (Business Logic, Entities)                        │
│  • types.py - Domain entities and value objects               │
│  • metadata.py - Domain services for schema operations        │
│  • Business rules and domain logic                            │
├─────────────────────────────────────────────────────────────────┤
│ Infrastructure Layer (External Concerns)                       │
│  • connection.py - Database connectivity                      │
│  • config.py - Configuration management                       │
│  • observability.py - Monitoring and logging                  │
│  • plugins.py - Plugin system implementation                  │
├═════════════════════════════════════════════════════════════════┤
│                         FLEXT CORE                             │
│  FlextResult | FlextContainer | Domain Patterns | Logging     │
└─────────────────────────────────────────────────────────────────┘
```

### **FLEXT Ecosystem Position**

FLEXT DB Oracle serves as a critical infrastructure component:

```
┌─────────────────────────────────────────────────────────────────┐
│                    FLEXT ECOSYSTEM                              │
├─────────────────────────────────────────────────────────────────┤
│ Go Services                                                     │
│  • FlexCore (port 8080) - Runtime container with plugins      │
│  • FLEXT Service (port 8081) - Data platform with Python      │
├─────────────────────────────────────────────────────────────────┤
│ Application Services                                            │
│  • flext-api - REST API services                              │
│  • flext-auth - Authentication services                       │
│  • flext-web - Web interface                                  │
├═════════════════════════════════════════════════════════════════┤
│ Infrastructure Layer                                            │
│  • [FLEXT-DB-ORACLE] ← YOU ARE HERE                           │
│  • flext-ldap - LDAP connectivity                             │
│  • flext-grpc - gRPC communications                           │
├─────────────────────────────────────────────────────────────────┤
│ Singer Ecosystem (Built on FLEXT-DB-ORACLE)                   │
│  • flext-tap-oracle - Data extraction                         │
│  • flext-target-oracle - Data loading                         │
│  • flext-dbt-oracle - Data transformation                     │
├─────────────────────────────────────────────────────────────────┤
│ Foundation                                                      │
│  • flext-core - FlextResult, DI, Domain patterns              │
│  • flext-observability - Monitoring and health checks         │
└─────────────────────────────────────────────────────────────────┘
```

## 🎯 Architectural Principles

### **1. Dependency Rule**

Dependencies point inward toward the domain layer:

```python
# ✅ CORRECT: Infrastructure depends on Domain
class FlextDbOracleConnection:  # Infrastructure
    def __init__(self, config: FlextDbOracleConfig):  # Domain
        self._config = config

# ✅ CORRECT: Application depends on Domain
class FlextDbOracleApi:  # Application
    def __init__(self, metadata_service: IMetadataService):  # Domain Interface
        self._metadata = metadata_service

# ❌ INCORRECT: Domain depending on Infrastructure
class MetadataService:  # Domain
    def __init__(self, connection: FlextDbOracleConnection):  # Infrastructure
        # VIOLATES dependency rule
```

### **2. FLEXT Core Integration**

All layers integrate consistently with FLEXT Core patterns:

```python
from flext_core import FlextResult, get_flext_container, FlextLogger

# FlextResult for all operations
def execute_query(self, sql: str) -> FlextResult[QueryResult]:
    try:
        result = self._connection.execute(sql)
        return FlextResult[None].ok(QueryResult(rows=result.fetchall()))
    except Exception as e:
        return FlextResult[None].fail(f"Query execution failed: {e}")

# Dependency injection via container
container = FlextContainer.get_global()
oracle_service = container.resolve(IOracleService)

# Structured logging with correlation
logger = FlextLogger("flext.db.oracle.api")
logger.info("Executing Oracle operation", extra={"correlation_id": context.correlation_id})
```

### **3. Domain-Driven Design**

Clear domain modeling with ubiquitous language:

```python
# Domain Entities
@dataclass
class OracleTable:
    name: str
    schema: str
    columns: List[OracleColumn]
    indexes: List[OracleIndex]

    def get_primary_key(self) -> Optional[OracleIndex]:
        return next((idx for idx in self.indexes if idx.is_primary), None)

# Domain Services
class IMetadataService(Protocol):
    def extract_schema_metadata(self, schema_name: str) -> FlextResult[OracleSchema]:
        ...

    def generate_table_ddl(self, table: OracleTable) -> FlextResult[str]:
        ...

# Value Objects
@dataclass(frozen=True)
class ConnectionString:
    host: str
    port: int
    service_name: str

    def to_oracle_dsn(self) -> str:
        return f"{self.host}:{self.port}/{self.service_name}"
```

## 🔧 Component Architecture

### **1. Application Layer (api.py)**

Main application service coordinating use cases:

```python
class FlextDbOracleApi:
    """Main application service implementing Oracle database use cases.

    Coordinates between domain services and infrastructure components
    while maintaining Clean Architecture boundaries.
    """

    def __init__(
        self,
        config: FlextDbOracleConfig,
        container: FlextContainer
    ):
        # Resolve dependencies via container
        self._connection_service = container.resolve(IConnectionService)
        self._metadata_service = container.resolve(IMetadataService)
        self._plugin_manager = container.resolve(IPluginManager)
        self._observability = container.resolve(IObservabilityService)

    def connect(self) -> FlextResult[None]:
        """Use case: Establish Oracle database connection."""
        return self._connection_service.connect()

    def get_schema_metadata(self, schema: str) -> FlextResult[OracleSchema]:
        """Use case: Extract complete schema metadata."""
        return self._metadata_service.extract_schema_metadata(schema)
```

### **2. Domain Layer (types.py, metadata.py)**

Core business logic and domain entities:

```python
# Domain Entities (types.py)
class TDbOracleSchema(BaseModel):
    """Oracle schema domain entity with business rules."""
    name: str
    tables: List[TDbOracleTable]
    views: List[TDbOracleView]
    sequences: List[TDbOracleSequence]

    def get_table_dependencies(self) -> Dict[str, List[str]]:
        """Business logic: Calculate table dependencies."""
        # Domain logic for dependency analysis

# Domain Services (metadata.py)
class FlextDbOracleMetadataManager:
    """Domain service for Oracle metadata operations."""

    def __init__(self, repository: IOracleRepository):
        self._repository = repository  # Dependency inversion

    def extract_schema_metadata(self, schema_name: str) -> FlextResult[OracleSchema]:
        """Extract complete schema metadata with business rules."""
        # Business logic for metadata extraction
```

### **3. Infrastructure Layer**

External concerns and technical implementations:

```python
# Database Connectivity (connection.py)
class FlextDbOracleConnection:
    """Infrastructure component for Oracle database connectivity."""

    def __init__(self, config: FlextDbOracleConfig):
        self._config = config
        self._pool: Optional[Pool] = None

    def create_connection_pool(self) -> FlextResult[None]:
        """Create Oracle connection pool with enterprise settings."""
        try:
            self._pool = oracledb.create_pool(
                user=self._config.username,
                password=self._config.password.get_secret_value(),
                dsn=self._config.get_dsn(),
                min=self._config.pool_min,
                max=self._config.pool_max
            )
            return FlextResult[None].ok(None)
        except Exception as e:
            return FlextResult[None].fail(f"Pool creation failed: {e}")

# Configuration Management (config.py)
class FlextDbOracleConfig(BaseSettings):
    """Infrastructure configuration with validation."""

    host: str = Field(..., description="Oracle server hostname")
    port: int = Field(1521, description="Oracle port")
    service_name: str = Field(..., description="Oracle service name")
    username: str = Field(..., description="Oracle username")
    password: SecretStr = Field(..., description="Oracle password")

    @field_validator('port')
    @classmethod
    def validate_port(cls, v: int) -> int:
        if not 1024 <= v <= 65535:
            raise ValueError('Port must be between 1024 and 65535')
        return v
```

## 🔌 Plugin Architecture

### **Plugin System Design**

Extensible architecture following Open/Closed Principle:

```python
# Plugin Interface (Domain Layer)
class IOraclePlugin(Protocol):
    """Plugin interface for extending Oracle operations."""

    def supports(self, operation: str) -> bool:
        """Check if plugin supports the operation."""

    def execute(self, context: OracleOperationContext) -> FlextResult[object]:
        """Execute plugin logic."""

# Plugin Manager (Application Layer)
class OraclePluginManager:
    """Manages Oracle plugins with dependency injection."""

    def __init__(self, container: FlextContainer):
        self._plugins: List[IOraclePlugin] = []
        self._container = container

    def register_plugin(self, plugin_type: Type[IOraclePlugin]) -> None:
        """Register plugin via dependency injection."""
        plugin = self._container.resolve(plugin_type)
        self._plugins.append(plugin)

    def execute_plugins(self, operation: str, context: OracleOperationContext) -> FlextResult[List[object]]:
        """Execute all plugins that support the operation."""
        results = []
        for plugin in self._plugins:
            if plugin.supports(operation):
                result = plugin.execute(context)
                if result.is_failure:
                    return result
                results.append(result.value)
        return FlextResult[None].ok(results)

# Concrete Plugin Implementation (Infrastructure Layer)
class DataValidationPlugin(IOraclePlugin):
    """Plugin for Oracle data validation."""

    def supports(self, operation: str) -> bool:
        return operation in ["insert", "update", "bulk_load"]

    def execute(self, context: OracleOperationContext) -> FlextResult[object]:
        # Validation logic
        return FlextResult[None].ok({"validation": "passed"})
```

## 🏢 Enterprise Patterns

### **1. Repository Pattern**

Data access abstraction following DDD:

```python
# Domain Interface
class IOracleRepository(Protocol):
    def get_table_metadata(self, schema: str, table: str) -> FlextResult[OracleTable]:
        ...

    def execute_query(self, sql: str, params: Dict[str, object]) -> FlextResult[QueryResult]:
        ...

# Infrastructure Implementation
class OracleRepository(IOracleRepository):
    def __init__(self, connection: FlextDbOracleConnection):
        self._connection = connection

    def get_table_metadata(self, schema: str, table: str) -> FlextResult[OracleTable]:
        # SQLAlchemy-based implementation
        pass

    def execute_query(self, sql: str, params: Dict[str, object]) -> FlextResult[QueryResult]:
        # Safe parameterized query execution
        pass
```

### **2. Factory Pattern**

Object creation with dependency injection:

```python
class OracleServiceFactory:
    """Factory for creating Oracle services with proper dependencies."""

    def __init__(self, container: FlextContainer):
        self._container = container

    def create_api(self, config: FlextDbOracleConfig) -> FlextDbOracleApi:
        """Create API with all dependencies resolved."""
        # Register configuration
        self._container.register_instance(FlextDbOracleConfig, config)

        # Register services
        self._container.register(IOracleRepository, OracleRepository)
        self._container.register(IMetadataService, MetadataService)

        # Resolve and return API
        return self._container.resolve(FlextDbOracleApi)
```

### **3. Observer Pattern**

Event-driven architecture for monitoring:

```python
class OracleOperationEvent:
    """Domain event for Oracle operations."""
    def __init__(self, operation: str, context: Dict[str, object]):
        self.operation = operation
        self.context = context
        self.timestamp = datetime.utcnow()

class IOperationObserver(Protocol):
    def handle_operation_event(self, event: OracleOperationEvent) -> None:
        ...

class ObservabilityObserver(IOperationObserver):
    """Observer for collecting operation metrics."""
    def handle_operation_event(self, event: OracleOperationEvent) -> None:
        # Collect metrics and traces
        pass
```

## 🔄 Data Flow Architecture

### **Query Execution Flow**

```
1. CLI/API Request
   ↓
2. Application Service (api.py)
   ↓
3. Domain Service (metadata.py)
   ↓
4. Repository Interface (Domain)
   ↓
5. Repository Implementation (Infrastructure)
   ↓
6. Connection Pool (connection.py)
   ↓
7. Oracle Database
   ↓
8. FlextResult Response Chain
```

### **Plugin Execution Flow**

```
1. Operation Request
   ↓
2. Plugin Manager
   ↓
3. Plugin Discovery (supports check)
   ↓
4. Plugin Execution (parallel)
   ↓
5. Result Aggregation
   ↓
6. FlextResult Response
```

## 🎯 Architectural Benefits

### **Maintainability**

- **Clear Separation**: Each layer has distinct responsibilities
- **Dependency Inversion**: Easy to mock and test
- **Plugin System**: Extensible without modifying core code
- **FLEXT Integration**: Consistent patterns across ecosystem

### **Testability**

- **Layer Isolation**: Test each layer independently
- **Dependency Injection**: Easy to mock dependencies
- **FlextResult Pattern**: Predictable error handling
- **Repository Pattern**: Database operations abstracted

### **Scalability**

- **Connection Pooling**: Efficient resource management
- **Plugin Architecture**: Horizontal feature extension
- **Event-Driven**: Loose coupling between components
- **Clean Boundaries**: Independent scaling of layers

### **Enterprise Readiness**

- **Security Integration**: Built-in security patterns
- **Observability**: Comprehensive monitoring and tracing
- **Configuration Management**: Environment-aware settings
- **Error Handling**: Consistent error management

## 📊 Architecture Metrics

### **Layer Dependencies**

- ✅ **Domain Layer**: Zero external dependencies
- ✅ **Application Layer**: Depends only on Domain + FLEXT Core
- ✅ **Infrastructure Layer**: Implements Domain interfaces
- ✅ **Presentation Layer**: Depends on Application + Domain

### **Code Organization**

- **Domain Logic**: Concentrated in `types.py` and domain services
- **Application Logic**: Orchestrated in `api.py`
- **Infrastructure**: Isolated in connection, config, observability modules
- **Cross-cutting Concerns**: Handled via FLEXT Core integration

### **Quality Metrics**

- **Cyclomatic Complexity**: Reduced through SOLID refactoring
- **Coupling**: Minimized through dependency inversion
- **Cohesion**: High within each architectural layer
- **Testability**: Enhanced through dependency injection

---

This Clean Architecture implementation ensures FLEXT DB Oracle remains maintainable, testable, and extensible while providing Oracle database integration for the FLEXT ecosystem.
