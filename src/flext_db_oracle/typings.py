"""FLEXT DB Oracle Types - Domain-specific Oracle database type definitions.

This module provides Oracle database-specific type definitions extending FlextTypes.
Follows FLEXT standards:
- Domain-specific complex types only
- No simple aliases to primitive types
- Python 3.13+ syntax
- Extends FlextTypes properly

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from typing import Literal

from flext_core import FlextTypes

# =============================================================================
# DB ORACLE-SPECIFIC TYPE VARIABLES - Domain-specific TypeVars for Oracle operations
# =============================================================================


# Oracle database domain TypeVars
class FlextDbOracleTypes(FlextTypes):
    """Oracle database-specific type definitions extending FlextTypes.

    Domain-specific type system for Oracle database operations.
    Contains ONLY complex Oracle-specific types, no simple aliases.
    Uses Python 3.13+ type syntax and patterns.
    """

    # =========================================================================
    # ORACLE CONNECTION TYPES - Database connection configuration
    # =========================================================================

    class Connection:
        """Oracle connection complex types."""

        type ConnectionConfiguration = dict[
            str, str | int | bool | dict[str, FlextTypes.JsonValue]
        ]
        type ConnectionPool = dict[str, int | bool | str]
        type ConnectionString = str
        type ConnectionParams = dict[str, str | int | bool]
        type SslConfiguration = dict[str, str | bool | dict[str, FlextTypes.JsonValue]]
        type AuthenticationConfig = dict[str, str | dict[str, FlextTypes.JsonValue]]

    # =========================================================================
    # ORACLE QUERY TYPES - SQL query and execution types
    # =========================================================================

    class Query:
        """Oracle query complex types."""

        type SqlQuery = str
        type QueryParameters = dict[str, FlextTypes.JsonValue]
        type QueryResult = dict[str, FlextTypes.JsonValue | list[FlextTypes.JsonValue]]
        type QueryMetadata = dict[str, str | int | dict[str, FlextTypes.JsonValue]]
        type PreparedStatement = dict[str, str | dict[str, FlextTypes.JsonValue]]
        type QueryExecution = dict[
            str, str | int | bool | dict[str, FlextTypes.JsonValue]
        ]

    # =========================================================================
    # ORACLE TRANSACTION TYPES - Transaction management types
    # =========================================================================

    class Transaction:
        """Oracle transaction complex types."""

        type TransactionConfiguration = dict[str, str | int | bool]
        type TransactionState = dict[str, str | bool | dict[str, FlextTypes.JsonValue]]
        type IsolationLevel = str
        type TransactionBlock = list[dict[str, str | dict[str, FlextTypes.JsonValue]]]
        type SavepointConfig = dict[str, str | int]
        type RollbackConfig = dict[str, str | bool | list[str]]

    # =========================================================================
    # ORACLE SCHEMA TYPES - Database schema and structure types
    # =========================================================================

    class Schema:
        """Oracle schema complex types."""

        type SchemaDefinition = dict[str, str | list[dict[str, FlextTypes.JsonValue]]]
        type TableDefinition = dict[str, str | list[dict[str, str | bool | int]]]
        type ColumnDefinition = dict[
            str, str | int | bool | dict[str, FlextTypes.JsonValue]
        ]
        type IndexDefinition = dict[
            str, str | list[str] | dict[str, FlextTypes.JsonValue]
        ]
        type ConstraintDefinition = dict[str, str | list[str] | bool]
        type ViewDefinition = dict[str, str | dict[str, FlextTypes.JsonValue]]

    # =========================================================================
    # ORACLE SESSION TYPES - Database session management types
    # =========================================================================

    class Session:
        """Oracle session complex types."""

        type SessionConfiguration = dict[
            str, str | int | bool | dict[str, FlextTypes.JsonValue]
        ]
        type SessionState = dict[
            str, FlextTypes.JsonValue | dict[str, FlextTypes.JsonValue]
        ]
        type SessionVariables = dict[str, FlextTypes.JsonValue]
        type SessionMetrics = dict[str, int | float | str]
        type SessionPooling = dict[
            str, int | bool | str | dict[str, FlextTypes.JsonValue]
        ]
        type SessionTimeout = dict[str, int | str]

    # =========================================================================
    # ORACLE PERFORMANCE TYPES - Performance monitoring and optimization types
    # =========================================================================

    class Performance:
        """Oracle performance complex types."""

        type PerformanceMetrics = dict[
            str, int | float | dict[str, FlextTypes.JsonValue]
        ]
        type QueryPlan = dict[str, str | int | list[dict[str, FlextTypes.JsonValue]]]
        type ExecutionStats = dict[
            str, int | float | str | dict[str, FlextTypes.JsonValue]
        ]
        type IndexUsage = dict[str, str | int | bool | dict[str, FlextTypes.JsonValue]]
        type CacheConfiguration = dict[str, int | str | bool]
        type OptimizationHints = dict[str, str | list[str]]

    # =========================================================================
    # ORACLE SECURITY TYPES - Database security and access control types
    # =========================================================================

    class Security:
        """Oracle security complex types."""

        type UserPermissions = dict[str, list[str] | dict[str, bool]]
        type RoleDefinition = dict[
            str, str | list[str] | dict[str, FlextTypes.JsonValue]
        ]
        type PrivilegeConfiguration = dict[
            str, bool | list[str] | dict[str, FlextTypes.JsonValue]
        ]
        type AccessPolicy = dict[str, str | bool | dict[str, FlextTypes.JsonValue]]
        type EncryptionConfig = dict[str, str | bool | dict[str, FlextTypes.JsonValue]]
        type AuditConfiguration = dict[
            str, bool | str | dict[str, FlextTypes.JsonValue]
        ]

    # =========================================================================
    # ORACLE DATA TYPES - Oracle-specific data type mappings
    # =========================================================================

    class DataTypes:
        """Oracle data type complex mappings."""

        type OracleDataType = str
        type PythonDataType = type[object]
        type TypeMapping = dict[str, str | type[object]]
        type DataConversion = dict[str, FlextTypes.JsonValue | object]
        type TypeValidation = dict[str, bool | str | list[str]]
        type NullHandling = dict[str, bool | FlextTypes.JsonValue]

    # =========================================================================
    # ORACLE PROJECT TYPES - Domain-specific project types extending FlextTypes
    # =========================================================================

    class OracleProject:
        """Oracle database-specific project types extending FlextTypes.

        Adds Oracle database-specific project types while inheriting generic types
        from FlextTypes. Follows domain separation principle: Oracle domain owns
        Oracle-specific types.
        """

        # Oracle-specific project types extending the generic ones
        type ProjectType = Literal[
            # Generic types inherited from FlextTypes
            "library",
            "application",
            "service",
            # Oracle-specific types
            "oracle-service",
            "database-service",
            "data-warehouse",
            "etl-service",
            "oracle-client",
            "db-migration",
            "schema-manager",
            "data-pipeline",
            "oracle-api",
            "database-api",
            "sql-service",
            "data-connector",
        ]

        # Oracle-specific project configurations
        type OracleProjectConfig = dict[str, FlextTypes.JsonValue]
        type DatabaseConfig = dict[str, str | int | bool | list[str]]
        type SchemaConfig = dict[str, bool | str | dict[str, FlextTypes.JsonValue]]
        type ConnectionConfig = dict[str, FlextTypes.JsonValue]


# =============================================================================
# PUBLIC API EXPORTS - Oracle DB TypeVars and types
# =============================================================================

__all__: list[str] = [
    "FlextDbOracleTypes",
]
