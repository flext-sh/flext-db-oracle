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

from flext_core import FlextTypes, t as _core_t
from flext_db_oracle.models import FlextDbOracleModels

# Direct model class imports for type alias use (FlextDbOracleModels.X.Y not valid in type expressions)
_ConnectionStatus = FlextDbOracleModels.DbOracle.ConnectionStatus
_QueryResult = FlextDbOracleModels.DbOracle.QueryResult
_TableMetadata = FlextDbOracleModels.DbOracle.TableMetadata
_TypeMapping = FlextDbOracleModels.DbOracle.TypeMapping
_ConfigMap = _core_t.ConfigMap
JsonValue = _core_t.JsonValue

# =============================================================================
# DB ORACLE-SPECIFIC TYPE VARIABLES - Domain-specific TypeVars for Oracle operations
# =============================================================================


# Oracle database domain TypeVars
class FlextDbOracleTypes(FlextTypes):
    """Oracle database-specific type definitions extending t.

    Domain-specific type system for Oracle database operations.
    Contains ONLY complex Oracle-specific types, no simple aliases.
    Uses Python 3.13+ type syntax and patterns.
    """

    # =========================================================================
    # ORACLE CONNECTION TYPES - Database connection configuration
    # =========================================================================

    class DbOracle:
        """Oracle connection complex types.

        Python 3.13+ best practice: Use TypeAlias for better type checking.
        """

        type ConnectionConfiguration = _ConnectionStatus
        type ConnectionPool = _ConfigMap
        type ConnectionString = str
        type ConnectionParams = dict[str, str | int | bool]
        type SslConfiguration = dict[str, str | bool | dict[str, JsonValue]]
        type AuthenticationConfig = dict[str, str | dict[str, JsonValue]]

    # =========================================================================
    # ORACLE QUERY TYPES - SQL query and execution types
    # =========================================================================

    class Query:
        """Oracle query complex types.

        Python 3.13+ best practice: Use TypeAlias for better type checking.
        """

        type SqlQuery = str
        type QueryParameters = _ConfigMap
        type QueryResult = _QueryResult
        type QueryMetadata = dict[str, str | int | dict[str, JsonValue]]
        type PreparedStatement = dict[str, str | dict[str, JsonValue]]
        type QueryExecution = dict[
            str,
            str | int | bool | dict[str, JsonValue],
        ]

    # =========================================================================
    # ORACLE TRANSACTION TYPES - Transaction management types
    # =========================================================================

    class Transaction:
        """Oracle transaction complex types.

        Python 3.13+ best practice: Use TypeAlias for better type checking.
        """

        type TransactionConfiguration = dict[str, str | int | bool]
        type TransactionState = dict[str, str | bool | dict[str, JsonValue]]
        type IsolationLevel = str
        type TransactionBlock = list[dict[str, str | dict[str, JsonValue]]]
        type SavepointConfig = dict[str, str | int]
        type RollbackConfig = dict[str, str | bool | list[str]]

    # =========================================================================
    # ORACLE SCHEMA TYPES - Database schema and structure types
    # =========================================================================

    class Schema:
        """Oracle schema complex types.

        Python 3.13+ best practice: Use TypeAlias for better type checking.
        """

        type SchemaDefinition = _TableMetadata
        type TableDefinition = dict[str, str | list[dict[str, str | bool | int]]]
        type ColumnDefinition = dict[
            str,
            str | int | bool | dict[str, JsonValue],
        ]
        type IndexDefinition = dict[
            str,
            str | list[str] | dict[str, JsonValue],
        ]
        type ConstraintDefinition = dict[str, str | list[str] | bool]
        type ViewDefinition = dict[str, str | dict[str, JsonValue]]

    # =========================================================================
    # ORACLE SESSION TYPES - Database session management types
    # =========================================================================

    class Session:
        """Oracle session complex types.

        Python 3.13+ best practice: Use TypeAlias for better type checking.
        """

        type SessionConfiguration = dict[
            str,
            str | int | bool | dict[str, JsonValue],
        ]
        type SessionState = dict[
            str,
            JsonValue | dict[str, JsonValue],
        ]
        type SessionVariables = dict[str, JsonValue]
        type SessionMetrics = dict[str, int | float | str]
        type SessionPooling = dict[
            str,
            int | bool | str | dict[str, JsonValue],
        ]
        type SessionTimeout = dict[str, int | str]

    # =========================================================================
    # ORACLE PERFORMANCE TYPES - Performance monitoring and optimization types
    # =========================================================================

    class Performance:
        """Oracle performance complex types.

        Python 3.13+ best practice: Use TypeAlias for better type checking.
        """

        type PerformanceMetrics = dict[
            str,
            int | float | dict[str, JsonValue],
        ]
        type QueryPlan = dict[str, str | int | list[dict[str, JsonValue]]]
        type ExecutionStats = dict[
            str,
            int | float | str | dict[str, JsonValue],
        ]
        type IndexUsage = dict[str, str | int | bool | dict[str, JsonValue]]
        type CacheConfiguration = dict[str, int | str | bool]
        type OptimizationHints = dict[str, str | list[str]]

    # =========================================================================
    # ORACLE SECURITY TYPES - Database security and access control types
    # =========================================================================

    class Security:
        """Oracle security complex types.

        Python 3.13+ best practice: Use TypeAlias for better type checking.
        """

        type UserPermissions = dict[str, list[str] | dict[str, bool]]
        type RoleDefinition = dict[
            str,
            str | list[str] | dict[str, JsonValue],
        ]
        type PrivilegeConfiguration = dict[
            str,
            bool | list[str] | dict[str, JsonValue],
        ]
        type AccessPolicy = dict[str, str | bool | dict[str, JsonValue]]
        type EncryptionConfig = dict[str, str | bool | dict[str, JsonValue]]
        type AuditConfiguration = dict[
            str,
            bool | str | dict[str, JsonValue],
        ]

    # =========================================================================
    # ORACLE DATA TYPES - Oracle-specific data type mappings
    # =========================================================================

    class DataTypes:
        """Oracle data type complex mappings.

        Python 3.13+ best practice: Use TypeAlias for better type checking.
        """

        type OracleDataType = str
        type PythonDataType = type[object]
        type TypeMapping = _TypeMapping
        type DataConversion = dict[str, JsonValue | object]
        type TypeValidation = dict[str, bool | str | list[str]]
        type NullHandling = dict[str, bool | JsonValue]

    # =========================================================================
    # ORACLE PROJECT TYPES - Domain-specific project types extending t
    # =========================================================================

    class Project:
        """Oracle database-specific project types.

        Adds Oracle database-specific project types.
        Follows domain separation principle: Oracle domain owns
        Oracle-specific types.
        """

        # Oracle-specific project types
        type ProjectType = Literal[
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

        # Oracle-specific project configurations
        type OracleProjectConfig = dict[str, JsonValue]
        type DatabaseConfig = dict[str, str | int | bool | list[str]]
        type SchemaConfig = dict[str, bool | str | dict[str, JsonValue]]
        type ConnectionConfig = dict[str, JsonValue]

    # =========================================================================
    # ORACLE LITERAL TYPES - Type-safe string literals for Oracle operations
    # =========================================================================

    # Connection type literals - references StrEnum members from constants
    type ConnectionTypeLiteral = Literal[
        "service_name",
        "sid",
        "tns",
    ]
    """Oracle connection type literal - references ConnectionType StrEnum members."""

    # Query type literals - references StrEnum members from constants
    type QueryTypeLiteral = Literal[
        "SELECT",
        "INSERT",
        "UPDATE",
        "DELETE",
        "CREATE",
        "DROP",
        "ALTER",
    ]
    """Oracle query type literal - references QueryType StrEnum members."""

    # Data type literals - references StrEnum members from constants
    type DataTypeLiteral = Literal[
        "VARCHAR2",
        "NUMBER",
        "DATE",
        "TIMESTAMP",
        "CLOB",
        "BLOB",
        "CHAR",
        "RAW",
    ]
    """Oracle data type literal - references DataType StrEnum members."""


# Namespace composition via class inheritance
# DbOracle namespace provides access to nested classes through inheritance
# Access patterns:
# - t.DbOracle.* for DbOracle-specific types
# - t.Project.* for project types
# - t.Core.* for core types (inherited from parent)

t = FlextDbOracleTypes

__all__ = ["FlextDbOracleTypes", "t"]
