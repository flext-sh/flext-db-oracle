"""FLEXT DB Oracle Types - Domain-specific Oracle database type definitions.

This module provides Oracle database-specific type definitions extending FlextCore.Types.
Follows FLEXT standards:
- Domain-specific complex types only
- No simple aliases to primitive types
- Python 3.13+ syntax
- Extends FlextCore.Types properly

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from typing import Literal

from flext_core import FlextCore

# =============================================================================
# DB ORACLE-SPECIFIC TYPE VARIABLES - Domain-specific TypeVars for Oracle operations
# =============================================================================


# Oracle database domain TypeVars
class FlextDbOracleTypes(FlextCore.Types):
    """Oracle database-specific type definitions extending FlextCore.Types.

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
            str, str | int | bool | FlextCore.Types.Dict
        ]
        type ConnectionPool = dict[str, int | bool | str]
        type ConnectionString = str
        type ConnectionParams = dict[str, str | int | bool]
        type SslConfiguration = dict[str, str | bool | FlextCore.Types.Dict]
        type AuthenticationConfig = dict[str, str | FlextCore.Types.Dict]

    # =========================================================================
    # ORACLE QUERY TYPES - SQL query and execution types
    # =========================================================================

    class Query:
        """Oracle query complex types."""

        type SqlQuery = str
        type QueryParameters = dict[str, FlextCore.Types.JsonValue]
        type QueryResult = dict[str, FlextCore.Types.JsonValue | FlextCore.Types.List]
        type QueryMetadata = dict[str, str | int | FlextCore.Types.Dict]
        type PreparedStatement = dict[str, str | dict[str, FlextCore.Types.JsonValue]]
        type QueryExecution = dict[str, str | int | bool | FlextCore.Types.Dict]

    # =========================================================================
    # ORACLE TRANSACTION TYPES - Transaction management types
    # =========================================================================

    class Transaction:
        """Oracle transaction complex types."""

        type TransactionConfiguration = dict[str, str | int | bool]
        type TransactionState = dict[str, str | bool | FlextCore.Types.Dict]
        type IsolationLevel = str
        type TransactionBlock = list[
            dict[str, str | dict[str, FlextCore.Types.JsonValue]]
        ]
        type SavepointConfig = dict[str, str | int]
        type RollbackConfig = dict[str, str | bool | FlextCore.Types.StringList]

    # =========================================================================
    # ORACLE SCHEMA TYPES - Database schema and structure types
    # =========================================================================

    class Schema:
        """Oracle schema complex types."""

        type SchemaDefinition = dict[
            str, str | list[dict[str, FlextCore.Types.JsonValue]]
        ]
        type TableDefinition = dict[str, str | list[dict[str, str | bool | int]]]
        type ColumnDefinition = dict[str, str | int | bool | FlextCore.Types.Dict]
        type IndexDefinition = dict[
            str, str | FlextCore.Types.StringList | FlextCore.Types.Dict
        ]
        type ConstraintDefinition = dict[str, str | FlextCore.Types.StringList | bool]
        type ViewDefinition = dict[str, str | dict[str, FlextCore.Types.JsonValue]]

    # =========================================================================
    # ORACLE SESSION TYPES - Database session management types
    # =========================================================================

    class Session:
        """Oracle session complex types."""

        type SessionConfiguration = dict[str, str | int | bool | FlextCore.Types.Dict]
        type SessionState = dict[str, FlextCore.Types.JsonValue | FlextCore.Types.Dict]
        type SessionVariables = dict[str, FlextCore.Types.JsonValue]
        type SessionMetrics = dict[str, int | float | str]
        type SessionPooling = dict[str, int | bool | str | FlextCore.Types.Dict]
        type SessionTimeout = dict[str, int | str]

    # =========================================================================
    # ORACLE PERFORMANCE TYPES - Performance monitoring and optimization types
    # =========================================================================

    class Performance:
        """Oracle performance complex types."""

        type PerformanceMetrics = dict[str, int | float | FlextCore.Types.Dict]
        type QueryPlan = dict[
            str, str | int | list[dict[str, FlextCore.Types.JsonValue]]
        ]
        type ExecutionStats = dict[str, int | float | str | FlextCore.Types.Dict]
        type IndexUsage = dict[str, str | int | bool | FlextCore.Types.Dict]
        type CacheConfiguration = dict[str, int | str | bool]
        type OptimizationHints = dict[str, str | FlextCore.Types.StringList]

    # =========================================================================
    # ORACLE SECURITY TYPES - Database security and access control types
    # =========================================================================

    class Security:
        """Oracle security complex types."""

        type UserPermissions = dict[
            str, FlextCore.Types.StringList | FlextCore.Types.BoolDict
        ]
        type RoleDefinition = dict[
            str, str | FlextCore.Types.StringList | dict[str, FlextCore.Types.JsonValue]
        ]
        type PrivilegeConfiguration = dict[
            str, bool | FlextCore.Types.StringList | FlextCore.Types.Dict
        ]
        type AccessPolicy = dict[str, str | bool | dict[str, FlextCore.Types.JsonValue]]
        type EncryptionConfig = dict[str, str | bool | FlextCore.Types.Dict]
        type AuditConfiguration = dict[str, bool | str | FlextCore.Types.Dict]

    # =========================================================================
    # ORACLE DATA TYPES - Oracle-specific data type mappings
    # =========================================================================

    class DataTypes:
        """Oracle data type complex mappings."""

        type OracleDataType = str
        type PythonDataType = type[object]
        type TypeMapping = dict[str, str | type[object]]
        type DataConversion = dict[str, FlextCore.Types.JsonValue | object]
        type TypeValidation = dict[str, bool | str | FlextCore.Types.StringList]
        type NullHandling = dict[str, bool | FlextCore.Types.JsonValue]

    # =========================================================================
    # ORACLE PROJECT TYPES - Domain-specific project types extending FlextCore.Types
    # =========================================================================

    class OracleProject:
        """Oracle database-specific project types extending FlextCore.Types.Project.

        Adds Oracle database-specific project types while inheriting generic types
        from FlextCore.Types. Follows domain separation principle: Oracle domain owns
        Oracle-specific types.
        """

        # Oracle-specific project types extending the generic ones
        type ProjectType = Literal[
            # Generic types inherited from FlextCore.Types.Project
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
        type OracleProjectConfig = dict[str, FlextCore.Types.ConfigValue | object]
        type DatabaseConfig = dict[str, str | int | bool | FlextCore.Types.StringList]
        type SchemaConfig = dict[str, bool | str | FlextCore.Types.Dict]
        type ConnectionConfig = dict[str, FlextCore.Types.ConfigValue | object]


# =============================================================================
# PUBLIC API EXPORTS - Oracle DB TypeVars and types
# =============================================================================

__all__: FlextCore.Types.StringList = [
    "FlextDbOracleTypes",
]
