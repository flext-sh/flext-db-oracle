"""FLEXT DB Oracle - Enterprise Oracle Database Integration Library for FLEXT ecosystem.

Modern Oracle database integration library providing enterprise-grade connectivity,
performance optimization, and comprehensive Oracle-specific functionality. Built on
FLEXT Core patterns with Clean Architecture principles for reliable, scalable Oracle
database operations within the FLEXT data integration ecosystem.

This library serves as the foundation for Oracle-based data integration pipelines,
providing robust database connectivity, metadata management, and performance optimization
specifically tailored for Oracle Database environments.

Architecture (Clean Architecture + DDD):
    - Application Layer: FlextDbOracleApi (main service interface)
    - Domain Layer: Oracle metadata models and database-specific entities
    - Infrastructure Layer: Connection management, pooling, and configuration
    - Foundation Layer: FLEXT Core integration (FlextResult, FlextContainer, logging)

Key Features:
    - Enterprise Connection Management: Advanced connection pooling with SSL/TLS support
    - Schema Introspection: Comprehensive Oracle schema discovery and metadata management
    - Type-Safe Operations: Query execution with FlextResult[T] error handling patterns
    - Performance Optimization: Oracle-specific hints, bulk operations, and query tuning
    - Security & Compliance: Audit logging, credential management, and access control
    - Plugin Architecture: Extensible system for Oracle-specific functionality
    - Singer Integration: Foundation support for Singer tap/target development
    - RAC Support: Oracle Real Application Clusters connectivity and failover
    - Data Pipeline Support: Optimized for ETL/ELT operations in FLEXT ecosystem

Oracle-Specific Features:
    - Advanced data types support (CLOB, BLOB, XMLType, JSON, etc.)
    - Partition-aware operations for performance optimization
    - Oracle-specific SQL features (hierarchical queries, analytic functions)
    - Flashback query support for data recovery and auditing
    - PL/SQL execution and stored procedure integration

Example:
    Basic Oracle database operations with FLEXT patterns:

    >>> from flext_db_oracle import FlextDbOracleApi, FlextDbOracleConfig
    >>> from flext_core import FlextResult
    >>>
    >>> # Environment-based configuration (recommended)
    >>> api = FlextDbOracleApi.from_env("production")
    >>>
    >>> # Connect and execute operations with FlextResult error handling
    >>> with api.connect() as oracle:
    ...     # Type-safe query with parameter binding
    ...     result = oracle.query(
    ...         "SELECT employee_id, name FROM employees WHERE dept_id = :dept",
    ...         {"dept": 10},
    ...     )
    ...     if result.is_success:
    ...         print(f"Found {len(result.data)} employees")
    ...         for row in result.data:
    ...             print(f"ID: {row['employee_id']}, Name: {row['name']}")
    ...     else:
    ...         print(f"Query failed: {result.error}")

    Advanced metadata operations:
    >>> # Schema discovery and metadata management
    >>> metadata_result = api.get_schema_metadata("HR")
    >>> if metadata_result.is_success:
    ...     schema = metadata_result.data
    ...     for table in schema.tables:
    ...         print(f"Table: {table.name}, Columns: {len(table.columns)}")
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

from flext_db_oracle.api import FlextDbOracleApi
from flext_db_oracle.cli import oracle
from flext_db_oracle.config import FlextDbOracleConfig
from flext_db_oracle.config_types import MergeStatementConfig
from flext_db_oracle.connection import FlextDbOracleConnection
from flext_db_oracle.constants import FlextOracleDbConstants
from flext_db_oracle.exceptions import (
    FlextDbOracleAuthenticationError,
    FlextDbOracleConfigurationError,
    FlextDbOracleConnectionError,
    FlextDbOracleError,
    FlextDbOracleMetadataError,
    FlextDbOracleProcessingError,
    FlextDbOracleQueryError,
    FlextDbOracleTimeoutError,
    FlextDbOracleValidationError,
)
from flext_db_oracle.metadata import (
    FlextDbOracleColumn,
    FlextDbOracleMetadataManager,
    FlextDbOracleSchema,
    FlextDbOracleTable,
)
from flext_db_oracle.observability import (
    FlextDbOracleErrorHandler,
    FlextDbOracleObservabilityManager,
    FlextDbOracleOperationTracker,
)
from flext_db_oracle.plugins import (
    ORACLE_PLUGINS,
    create_data_validation_plugin,
    create_performance_monitor_plugin,
    create_security_audit_plugin,
    register_all_oracle_plugins,
)
from flext_db_oracle.typings import (
    CreateIndexConfig,
    TDbOracleColumn,
    TDbOracleConnectionStatus,
    TDbOracleQueryResult,
    TDbOracleSchema,
    TDbOracleTable,
)

# Backward compatibility aliases - maintain 100% compatibility
oracle_cli = oracle  # CLI alias for backward compatibility
# Backward compatibility class alias expected by older imports
FlextDbOracleAPI = FlextDbOracleApi

__all__: list[str] = [
    "ORACLE_PLUGINS",
    "CreateIndexConfig",
    "FlextDbOracleAPI",
    "FlextDbOracleApi",
    "FlextDbOracleAuthenticationError",
    "FlextDbOracleColumn",
    "FlextDbOracleConfig",
    "FlextDbOracleConfigurationError",
    "FlextDbOracleConnection",
    "FlextDbOracleConnectionError",
    "FlextDbOracleError",
    "FlextDbOracleErrorHandler",
    "FlextDbOracleMetadataError",
    "FlextDbOracleMetadataManager",
    "FlextDbOracleObservabilityManager",
    "FlextDbOracleOperationTracker",
    "FlextDbOracleProcessingError",
    "FlextDbOracleQueryError",
    "FlextDbOracleSchema",
    "FlextDbOracleTable",
    "FlextDbOracleTimeoutError",
    "FlextDbOracleValidationError",
    "FlextOracleDbConstants",
    "MergeStatementConfig",
    "TDbOracleColumn",
    "TDbOracleConnectionStatus",
    "TDbOracleQueryResult",
    "TDbOracleSchema",
    "TDbOracleTable",
    "__version__",
    "__version_info__",
    "create_data_validation_plugin",
    "create_performance_monitor_plugin",
    "create_security_audit_plugin",
    "oracle",
    "oracle_cli",
    "register_all_oracle_plugins",
]

__version__ = "0.9.0"
__version_info__ = tuple(int(x) for x in __version__.split(".") if x.isdigit())
__author__ = "flext-team"
__description__ = (
    "Modern Oracle Database Integration using SQLAlchemy 2 + oracledb "
    "with flext-core patterns"
)
