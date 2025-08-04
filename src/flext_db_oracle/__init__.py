"""FLEXT DB Oracle - Enterprise Oracle Database Integration Library.

Modern Oracle database integration library providing enterprise-grade connectivity,
performance optimization, and comprehensive Oracle-specific functionality. Built on
FLEXT Core patterns with Clean Architecture principles for reliable, scalable Oracle
database operations within the FLEXT ecosystem.

Architecture:
    Clean Architecture implementation with clear layer separation:
    - Application Layer: FlextDbOracleApi (main service interface)
    - Domain Layer: Metadata models and Oracle-specific entities
    - Infrastructure Layer: Connection management and configuration
    - Foundation Layer: FLEXT Core integration (FlextResult, FlextContainer)

Key Features:
    - Enterprise connection pooling with SSL/TLS support
    - Comprehensive Oracle schema introspection and metadata management
    - Type-safe query execution with FlextResult[T] error handling patterns
    - Plugin system for extensible Oracle-specific functionality
    - Singer ecosystem foundation for data pipeline development
    - Performance optimization with Oracle-specific hints and bulk operations
    - Security features including audit logging and credential management

Example:
    Basic Oracle database operations:

    >>> from flext_db_oracle import FlextDbOracleApi, FlextDbOracleConfig
    >>>
    >>> # Environment-based configuration (recommended)
    >>> api = FlextDbOracleApi.from_env("production")
    >>>
    >>> # Connect and execute operations
    >>> with api.connect() as oracle:
    ...     # Simple query
    ...     result = oracle.query(
    ...         "SELECT employee_id, name FROM employees WHERE dept_id = :dept",
    ...         {"dept": 10},
    ...     )
    ...     if result.success:
    ...         print(f"Found {result.value.row_count} employees")
    ...
    ...     # Bulk operations
    ...     bulk_result = oracle.execute_batch(
    ...         [
    ...             (
    ...                 "INSERT INTO employees (id, name) VALUES (:id, :name)",
    ...                 {"id": 1, "name": "John"},
    ...             ),
    ...             (
    ...                 "INSERT INTO employees (id, name) VALUES (:id, :name)",
    ...                 {"id": 2, "name": "Jane"},
    ...             ),
    ...         ]
    ...     )

    Schema introspection and metadata:

    >>> from flext_db_oracle import FlextDbOracleMetadataManager
    >>>
    >>> metadata_manager = FlextDbOracleMetadataManager(api.connection)
    >>> schema_result = metadata_manager.get_schema_metadata("HR")
    >>> if schema_result.success:
    ...     schema = schema_result.value
    ...     print(f"Schema {schema.name} has {len(schema.tables)} tables")
    ...     for table in schema.tables:
    ...         print(f"  - {table.name}: {len(table.columns)} columns")

Integration:
    - Foundation for flext-tap-oracle and flext-target-oracle Singer components
    - Compatible with Meltano orchestration for data pipeline workflows
    - Integrates with flext-observability for monitoring and performance tracking
    - Uses flext-core patterns ensuring consistency across FLEXT ecosystem
    - Supports Oracle Warehouse Management System (WMS) integration via flext-oracle-wms

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from .api import FlextDbOracleApi
from .cli import oracle as oracle_cli
from .config import FlextDbOracleConfig
from .connection import FlextDbOracleConnection
from .metadata import (
    FlextDbOracleColumn,
    FlextDbOracleMetadataManager,
    FlextDbOracleSchema,
    FlextDbOracleTable,
)
from .observability import (
    FlextDbOracleErrorHandler,
    FlextDbOracleObservabilityManager,
    FlextDbOracleOperationTracker,
)
from .plugins import (
    ORACLE_PLUGINS,
    create_data_validation_plugin,
    create_performance_monitor_plugin,
    create_security_audit_plugin,
    register_all_oracle_plugins,
)
from .types import (
    TDbOracleColumn,
    TDbOracleConnectionStatus,
    TDbOracleQueryResult,
    TDbOracleSchema,
    TDbOracleTable,
)

__all__: list[str] = [
    # Plugins
    "ORACLE_PLUGINS",
    # Core API
    "FlextDbOracleApi",
    # Metadata
    "FlextDbOracleColumn",
    "FlextDbOracleConfig",
    "FlextDbOracleConnection",
    # Observability (DRY Patterns)
    "FlextDbOracleErrorHandler",
    "FlextDbOracleMetadataManager",
    "FlextDbOracleObservabilityManager",
    "FlextDbOracleOperationTracker",
    "FlextDbOracleSchema",
    "FlextDbOracleTable",
    # Types
    "TDbOracleColumn",
    "TDbOracleConnectionStatus",
    "TDbOracleQueryResult",
    "TDbOracleSchema",
    "TDbOracleTable",
    "create_data_validation_plugin",
    "create_performance_monitor_plugin",
    "create_security_audit_plugin",
    # CLI
    "oracle_cli",
    "register_all_oracle_plugins",
]

__version__ = "0.9.0"
__author__ = "flext-team"
__description__ = (
    "Modern Oracle Database Integration using SQLAlchemy 2 + oracledb "
    "with flext-core patterns"
)
