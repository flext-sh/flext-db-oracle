"""FLEXT DB Oracle Types - Domain-specific Oracle database type definitions.

This module provides Oracle database-specific type definitions extending t.
Follows FLEXT standards:
- Domain-specific complex types only
- No simple aliases to primitive types
- Python 3.13+ syntax
- Extends t properly

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from typing import Literal

from flext_core import t

# =============================================================================
# DB ORACLE-SPECIFIC TYPE VARIABLES - Domain-specific TypeVars for Oracle operations
# =============================================================================


# Oracle database domain TypeVars
class FlextDbOracleTypes(t):
    """Oracle database-specific type definitions extending t.

    Domain-specific type system for Oracle database operations.
    Contains ONLY complex Oracle-specific types, no simple aliases.
    Uses Python 3.13+ type syntax and patterns.
    """

    # =========================================================================
    # ORACLE CONNECTION TYPES - Database connection configuration
    # =========================================================================

    class Connection:
        """Oracle connection complex types.

        Python 3.13+ best practice: Use TypeAlias for better type checking.
        """

        ConnectionConfiguration: type = dict[
            str, str | int | bool | dict[str, t.JsonValue]
        ]
        """Oracle connection configuration type."""
        ConnectionPool: type = dict[str, int | bool | str]
        """Oracle connection pool type."""
        ConnectionString: type = str
        """Oracle connection string type."""
        ConnectionParams: type = dict[str, str | int | bool]
        """Oracle connection parameters type."""
        SslConfiguration: type = dict[str, str | bool | dict[str, t.JsonValue]]
        """Oracle SSL configuration type."""
        AuthenticationConfig: type = dict[str, str | dict[str, t.JsonValue]]
        """Oracle authentication configuration type."""

    # =========================================================================
    # ORACLE QUERY TYPES - SQL query and execution types
    # =========================================================================

    class Query:
        """Oracle query complex types.

        Python 3.13+ best practice: Use TypeAlias for better type checking.
        """

        SqlQuery: type = str
        """Oracle SQL query type."""
        QueryParameters: type = dict[str, t.JsonValue]
        """Oracle query parameters type."""
        QueryResult: type = dict[str, t.JsonValue | list[t.JsonValue]]
        """Oracle query result type."""
        QueryMetadata: type = dict[str, str | int | dict[str, t.JsonValue]]
        """Oracle query metadata type."""
        PreparedStatement: type = dict[str, str | dict[str, t.JsonValue]]
        """Oracle prepared statement type."""
        QueryExecution: type = dict[str, str | int | bool | dict[str, t.JsonValue]]
        """Oracle query execution type."""

    # =========================================================================
    # ORACLE TRANSACTION TYPES - Transaction management types
    # =========================================================================

    class Transaction:
        """Oracle transaction complex types.

        Python 3.13+ best practice: Use TypeAlias for better type checking.
        """

        TransactionConfiguration: type = dict[str, str | int | bool]
        """Oracle transaction configuration type."""
        TransactionState: type = dict[str, str | bool | dict[str, t.JsonValue]]
        """Oracle transaction state type."""
        IsolationLevel: type = str
        """Oracle isolation level type."""
        TransactionBlock: type = list[dict[str, str | dict[str, t.JsonValue]]]
        """Oracle transaction block type."""
        SavepointConfig: type = dict[str, str | int]
        """Oracle savepoint configuration type."""
        RollbackConfig: type = dict[str, str | bool | list[str]]
        """Oracle rollback configuration type."""

    # =========================================================================
    # ORACLE SCHEMA TYPES - Database schema and structure types
    # =========================================================================

    class Schema:
        """Oracle schema complex types.

        Python 3.13+ best practice: Use TypeAlias for better type checking.
        """

        SchemaDefinition: type = dict[str, str | list[dict[str, t.JsonValue]]]
        """Oracle schema definition type."""
        TableDefinition: type = dict[str, str | list[dict[str, str | bool | int]]]
        """Oracle table definition type."""
        ColumnDefinition: type = dict[str, str | int | bool | dict[str, t.JsonValue]]
        """Oracle column definition type."""
        IndexDefinition: type = dict[str, str | list[str] | dict[str, t.JsonValue]]
        """Oracle index definition type."""
        ConstraintDefinition: type = dict[str, str | list[str] | bool]
        """Oracle constraint definition type."""
        ViewDefinition: type = dict[str, str | dict[str, t.JsonValue]]
        """Oracle view definition type."""

    # =========================================================================
    # ORACLE SESSION TYPES - Database session management types
    # =========================================================================

    class Session:
        """Oracle session complex types.

        Python 3.13+ best practice: Use TypeAlias for better type checking.
        """

        SessionConfiguration: type = dict[
            str, str | int | bool | dict[str, t.JsonValue]
        ]
        """Oracle session configuration type."""
        SessionState: type = dict[str, t.JsonValue | dict[str, t.JsonValue]]
        """Oracle session state type."""
        SessionVariables: type = dict[str, t.JsonValue]
        """Oracle session variables type."""
        SessionMetrics: type = dict[str, int | float | str]
        """Oracle session metrics type."""
        SessionPooling: type = dict[str, int | bool | str | dict[str, t.JsonValue]]
        """Oracle session pooling type."""
        SessionTimeout: type = dict[str, int | str]
        """Oracle session timeout type."""

    # =========================================================================
    # ORACLE PERFORMANCE TYPES - Performance monitoring and optimization types
    # =========================================================================

    class Performance:
        """Oracle performance complex types.

        Python 3.13+ best practice: Use TypeAlias for better type checking.
        """

        PerformanceMetrics: type = dict[str, int | float | dict[str, t.JsonValue]]
        """Oracle performance metrics type."""
        QueryPlan: type = dict[str, str | int | list[dict[str, t.JsonValue]]]
        """Oracle query plan type."""
        ExecutionStats: type = dict[str, int | float | str | dict[str, t.JsonValue]]
        """Oracle execution statistics type."""
        IndexUsage: type = dict[str, str | int | bool | dict[str, t.JsonValue]]
        """Oracle index usage type."""
        CacheConfiguration: type = dict[str, int | str | bool]
        """Oracle cache configuration type."""
        OptimizationHints: type = dict[str, str | list[str]]
        """Oracle optimization hints type."""

    # =========================================================================
    # ORACLE SECURITY TYPES - Database security and access control types
    # =========================================================================

    class Security:
        """Oracle security complex types.

        Python 3.13+ best practice: Use TypeAlias for better type checking.
        """

        UserPermissions: type = dict[str, list[str] | dict[str, bool]]
        """Oracle user permissions type."""
        RoleDefinition: type = dict[str, str | list[str] | dict[str, t.JsonValue]]
        """Oracle role definition type."""
        PrivilegeConfiguration: type = dict[
            str, bool | list[str] | dict[str, t.JsonValue]
        ]
        """Oracle privilege configuration type."""
        AccessPolicy: type = dict[str, str | bool | dict[str, t.JsonValue]]
        """Oracle access policy type."""
        EncryptionConfig: type = dict[str, str | bool | dict[str, t.JsonValue]]
        """Oracle encryption configuration type."""
        AuditConfiguration: type = dict[str, bool | str | dict[str, t.JsonValue]]
        """Oracle audit configuration type."""

    # =========================================================================
    # ORACLE DATA TYPES - Oracle-specific data type mappings
    # =========================================================================

    class DataTypes:
        """Oracle data type complex mappings.

        Python 3.13+ best practice: Use TypeAlias for better type checking.
        """

        OracleDataType: type = str
        """Oracle data type."""
        PythonDataType: type = type[object]
        """Python data type."""
        TypeMapping: type = dict[str, str | type[object]]
        """Oracle type mapping."""
        DataConversion: type = dict[str, t.JsonValue | object]
        """Oracle data conversion."""
        TypeValidation: type = dict[str, bool | str | list[str]]
        """Oracle type validation."""
        NullHandling: type = dict[str, bool | t.JsonValue]
        """Oracle null handling."""

    # =========================================================================
    # ORACLE PROJECT TYPES - Domain-specific project types extending t
    # =========================================================================

    class OracleProject:
        """Oracle database-specific project types extending t.

        Adds Oracle database-specific project types while inheriting generic types
        from t. Follows domain separation principle: Oracle domain owns
        Oracle-specific types.
        """

        # Oracle-specific project types extending the generic ones
        # Python 3.13+ best practice: Use TypeAlias for better type checking
        ProjectType: type = Literal[
            # Generic types inherited from t
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
        """Oracle project type literal."""

        # Oracle-specific project configurations
        OracleProjectConfig: type = dict[str, t.JsonValue]
        """Oracle project configuration type."""
        DatabaseConfig: type = dict[str, str | int | bool | list[str]]
        """Oracle database configuration type."""
        SchemaConfig: type = dict[str, bool | str | dict[str, t.JsonValue]]
        """Oracle schema configuration type."""
        ConnectionConfig: type = dict[str, t.JsonValue]
        """Oracle connection configuration type."""


# =============================================================================
# PUBLIC API EXPORTS - Oracle DB TypeVars and types
# =============================================================================

__all__: list[str] = [
    "FlextDbOracleTypes",
]
