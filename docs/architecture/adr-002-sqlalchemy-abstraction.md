# Architecture Decision Record: ADR-002


<!-- TOC START -->
- [Context](#context)
- [Decision](#decision)
- [Rationale](#rationale)
  - [Benefits Achieved](#benefits-achieved)
  - [Quality Attributes Addressed](#quality-attributes-addressed)
- [Alternatives Considered](#alternatives-considered)
  - [Option 1: Repository Pattern with Full Abstraction](#option-1-repository-pattern-with-full-abstraction)
  - [Option 2: Direct SQLAlchemy Usage Throughout](#option-2-direct-sqlalchemy-usage-throughout)
  - [Option 3: Query Object Pattern](#option-3-query-object-pattern)
  - [Option 4: CQRS with Separate Read/Write Models](#option-4-cqrs-with-separate-readwrite-models)
  - [Option 5: Data Mapper Pattern](#option-5-data-mapper-pattern)
- [Consequences](#consequences)
  - [Positive Consequences](#positive-consequences)
  - [Negative Consequences](#negative-consequences)
- [Implementation Plan](#implementation-plan)
  - [Phase 1: Foundation Setup (Completed)](#phase-1-foundation-setup-completed)
  - [Phase 2: Core Implementation (In Progress)](#phase-2-core-implementation-in-progress)
  - [Phase 3: Advanced Features (Planned)](#phase-3-advanced-features-planned)
- [Validation Criteria](#validation-criteria)
  - [Functional Validation](#functional-validation)
  - [Quality Validation](#quality-validation)
  - [Performance Validation](#performance-validation)
- [References](#references)
- [Notes](#notes)
  - [Technical Debt Considerations](#technical-debt-considerations)
  - [Future Enhancements](#future-enhancements)
  - [Migration Strategy](#migration-strategy)
  - [Related Decisions](#related-decisions)
<!-- TOC END -->

**ADR Number**: 002
**Title**: SQLAlchemy Abstraction Strategy for Oracle Integration
**Date**: 2025-01-20
**Status**: Accepted

## Context

The flext-db-oracle library needs to provide Oracle database operations while maintaining clean separation between business logic and infrastructure concerns. Key requirements include:

- **Technology Isolation**: Business logic shouldn't depend on specific ORM implementations
- **Ecosystem Compatibility**: Support for SQLAlchemy 2.0+ while allowing future changes
- **Performance**: Efficient database operations without excessive abstraction overhead
- **Maintainability**: Easy to update SQLAlchemy versions or switch ORMs if needed
- **Type Safety**: Full type safety while maintaining ORM flexibility
- **Error Handling**: Consistent error handling across different database operations

The FLEXT ecosystem already uses various database integrations, and there's a need for a standardized Oracle database abstraction pattern.

## Decision

Implement a single-entry-point SQLAlchemy abstraction where:

1. **Only `api.py` imports SQLAlchemy** - Complete encapsulation of ORM dependencies
2. **Domain models remain ORM-agnostic** - No SQLAlchemy imports in business logic
3. **Clean interface abstraction** - All database operations through FlextDbOracleApi
4. **Version management isolation** - SQLAlchemy updates don't affect consuming code

**Key Implementation Details:**

- **Abstraction Layer**: FlextDbOracleApi as the single point of SQLAlchemy interaction
- **Domain Models**: Pydantic v2 models for data validation and serialization
- **Connection Management**: SQLAlchemy engine wrapped in custom connection class
- **Error Translation**: SQLAlchemy exceptions converted to domain-specific exceptions
- **Configuration**: SQLAlchemy engine configuration through FlextDbOracleSettings

## Rationale

This abstraction strategy provides the best balance of encapsulation, performance, and maintainability for enterprise Oracle integration.

### Benefits Achieved

#### Encapsulation Benefits

- **Clean Separation**: Business logic completely isolated from ORM implementation
- **Version Independence**: SQLAlchemy upgrades don't break consuming code
- **Technology Flexibility**: Could switch ORMs without affecting 32+ FLEXT projects
- **Security**: SQLAlchemy-specific vulnerabilities contained within single module

#### Performance Benefits

- **Zero Abstraction Overhead**: Direct SQLAlchemy usage where needed
- **Optimized Queries**: Full access to SQLAlchemy query optimization features
- **Connection Pooling**: SQLAlchemy's enterprise-grade connection management
- **Async Support**: Ready for SQLAlchemy 2.0 async capabilities

#### Ecosystem Benefits

- **FLEXT Integration**: Seamless integration with existing FLEXT patterns
- **Consistent APIs**: Same interface patterns across all FLEXT database libraries
- **Shared Knowledge**: Team expertise applies across all database integrations
- **Testing Consistency**: Same testing patterns and fixtures

### Quality Attributes Addressed

#### Maintainability

- **Single Responsibility**: `api.py` is the only file with SQLAlchemy knowledge
- **Clear Boundaries**: Domain models don't import infrastructure concerns
- **Version Management**: Centralized SQLAlchemy version management
- **Update Isolation**: ORM changes don't cascade to consuming projects

#### Testability

- **Mock Boundaries**: Clear boundaries for unit testing without database
- **Integration Testing**: Full SQLAlchemy testing with real Oracle containers
- **Test Isolation**: Business logic testing independent of ORM implementation

#### Reliability

- **Error Handling**: SQLAlchemy exceptions properly translated to domain errors
- **Connection Resilience**: SQLAlchemy's built-in connection pooling and recovery
- **Transaction Safety**: ACID compliance through SQLAlchemy transaction management

## Alternatives Considered

### Option 1: Repository Pattern with Full Abstraction

**Description**: Create IRepository interfaces with concrete SQLAlchemy implementations
**Pros**: Complete ORM isolation; easy testing with mocks; clear contracts
**Cons**: Performance overhead; complex generic implementations; SQLAlchemy features underutilized
**Decision**: Rejected - Too much abstraction overhead for database operations; SQLAlchemy features would be underutilized

### Option 2: Direct SQLAlchemy Usage Throughout

**Description**: Use SQLAlchemy directly in all modules and services
**Pros**: Maximum performance; full SQLAlchemy feature access; simpler implementation
**Cons**: Tight coupling to SQLAlchemy; version upgrades affect entire codebase; harder testing
**Decision**: Rejected - Violates Clean Architecture principles; creates ecosystem coupling issues

### Option 3: Query Object Pattern

**Description**: Create query objects that encapsulate SQLAlchemy usage
**Pros**: Clean separation; testable query objects; domain-specific query APIs
**Cons**: Complex query object hierarchies; performance overhead; maintenance burden
**Decision**: Considered but not selected - Single-entry-point provides better balance

### Option 4: CQRS with Separate Read/Write Models

**Description**: Command Query Responsibility Segregation with separate models
**Pros**: Optimized read/write paths; clear separation of concerns; scalable architecture
**Cons**: Overkill for current requirements; increases complexity unnecessarily
**Decision**: Rejected - Current use case doesn't require CQRS complexity

### Option 5: Data Mapper Pattern

**Description**: Separate domain objects from database mapping logic
**Pros**: Clean separation; flexible mapping; testable domain logic
**Cons**: Complex mapping logic; performance overhead; SQLAlchemy already provides mapping
**Decision**: Rejected - SQLAlchemy's ORM already provides excellent data mapping

## Consequences

### Positive Consequences

#### Architectural Benefits

- **Clean Architecture Compliance**: Clear separation between domain and infrastructure
- **Single Point of Change**: SQLAlchemy updates isolated to one module
- **Technology Migration Path**: Clear upgrade path for future ORM changes
- **Ecosystem Protection**: 32+ FLEXT projects protected from SQLAlchemy changes

#### Development Benefits

- **Focused Expertise**: Team can specialize in SQLAlchemy usage in one place
- **Consistent Patterns**: Same abstraction pattern can be used for other databases
- **Testing Clarity**: Clear boundaries between unit and integration testing
- **Debugging Ease**: SQLAlchemy operations isolated for performance analysis

#### Quality Benefits

- **Type Safety**: Domain models fully typed without ORM interference
- **Error Consistency**: Uniform error handling across all database operations
- **Performance Optimization**: Full SQLAlchemy performance capabilities available
- **Security**: SQL injection prevention through parameterized queries

### Negative Consequences

#### Complexity Overhead

- **Interface Maintenance**: Additional abstraction layer to maintain
- **Error Translation**: SQLAlchemy exceptions need domain-specific conversion
- **Configuration Complexity**: SQLAlchemy configuration abstracted from direct access

#### Development Overhead

- **Learning Curve**: Team needs to understand both domain APIs and SQLAlchemy
- **Debugging Indirect**: Database issues require understanding both layers
- **Testing Setup**: More complex test fixtures for integration testing

#### Performance Considerations

- **Method Call Overhead**: Additional abstraction layer adds indirection
- **Optimization Limits**: Some SQLAlchemy optimizations may be harder to apply
- **Memory Overhead**: Additional objects for abstraction management

## Implementation Plan

### Phase 1: Foundation Setup (Completed)

1. ✅ Create FlextDbOracleApi as single SQLAlchemy entry point
2. ✅ Implement domain models with Pydantic v2 (no SQLAlchemy dependencies)
3. ✅ Set up error translation layer for domain-specific exceptions
4. ✅ Create connection management wrapper around SQLAlchemy engine

### Phase 2: Core Implementation (In Progress)

1. ✅ Implement query execution through abstraction layer
2. ✅ Add schema introspection capabilities
3. ✅ Set up transaction management
4. ⚠️ CLI integration (60% complete - Rich placeholders)
5. ⏳ Comprehensive testing and error handling

### Phase 3: Advanced Features (Planned)

1. ⏳ Async support for concurrent operations
2. ⏳ Bulk operations optimization
3. ⏳ Query result streaming for large datasets
4. ⏳ Advanced SQLAlchemy features integration

## Validation Criteria

### Functional Validation

- ✅ All Oracle operations work through FlextDbOracleApi abstraction
- ✅ No SQLAlchemy imports outside api.py (grep validation)
- ✅ Domain models remain ORM-agnostic
- ✅ Error handling works consistently across operations

### Quality Validation

- ✅ 95%+ test coverage including integration tests
- ✅ Pyrefly strict mode compliance
- ✅ Ruff linting with zero violations
- ✅ Documentation covers abstraction usage

### Performance Validation

- ⚠️ Sub-100ms response times for simple operations
- ⚠️ Efficient connection pooling utilization
- ⚠️ Memory usage comparable to direct SQLAlchemy usage
- ⏳ Benchmarking against direct SQLAlchemy usage

## References

- [SQLAlchemy 2.0 Documentation](https://sqlalchemy.org/)
- [Clean Architecture Dependencies](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html)
- [Domain-Driven Design Repository Pattern](https://domainlanguage.com/ddd/)
- FLEXT Database Integration Patterns

## Notes

### Technical Debt Considerations

- **Error Translation**: Current exception translation could be more comprehensive
- **Configuration**: SQLAlchemy configuration options could be more exposed
- **Async Support**: Current abstraction needs updates for SQLAlchemy 2.0 async

### Future Enhancements

- **CQRS Implementation**: Separate read/write abstractions if complexity grows
- **Multi-Database Support**: Extend abstraction for other database backends
- **Query Optimization**: Add query planning and optimization layers
- **Caching Integration**: Add query result and metadata caching

### Migration Strategy

- **Backward Compatibility**: Existing FLEXT projects continue to work unchanged
- **Gradual Migration**: New features use abstraction from day one
- **Deprecation Path**: Clear upgrade path for any direct SQLAlchemy usage
- **Testing Coverage**: Comprehensive testing ensures migration safety

### Related Decisions

- ADR-001: Clean Architecture Adoption
- ADR-003: Railway Pattern for Error Handling
- ADR-004: Testing Infrastructure Design
