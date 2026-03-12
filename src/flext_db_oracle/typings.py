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

from flext_core import FlextTypes, m as _core_m

from flext_db_oracle.models import FlextDbOracleModels

_ConnectionStatus = FlextDbOracleModels.DbOracle.ConnectionStatus
_QueryResult = FlextDbOracleModels.DbOracle.QueryResult
_TableMetadata = FlextDbOracleModels.DbOracle.TableMetadata
_TypeMapping = FlextDbOracleModels.DbOracle.TypeMapping
_ConfigMap = _core_m.ConfigMap


class FlextDbOracleTypes(FlextTypes):
    """Oracle database-specific type definitions extending t.

    Domain-specific type system for Oracle database operations.
    Contains ONLY complex Oracle-specific types, no simple aliases.
    Uses Python 3.13+ type syntax and patterns.
    """

    class DbOracle:
        """Oracle connection complex types.

        Python 3.13+ best practice: Use TypeAlias for better type checking.
        """

        type ConnectionConfiguration = _ConnectionStatus
        type ConnectionPool = _ConfigMap
        type ConnectionString = str
        type ConnectionParams = dict[str, str | int | bool]
        type SslConfiguration = dict[str, str | bool | dict[str, object]]
        type AuthenticationConfig = dict[str, str | dict[str, object]]

    class Query:
        """Oracle query complex types.

        Python 3.13+ best practice: Use TypeAlias for better type checking.
        """

        type SqlQuery = str
        type QueryParameters = _ConfigMap
        type QueryResult = _QueryResult
        type QueryMetadata = dict[str, str | int | dict[str, object]]
        type PreparedStatement = dict[str, str | dict[str, object]]
        type QueryExecution = dict[str, str | int | bool | dict[str, object]]

    class Transaction:
        """Oracle transaction complex types.

        Python 3.13+ best practice: Use TypeAlias for better type checking.
        """

        type TransactionConfiguration = dict[str, str | int | bool]
        type TransactionState = dict[str, str | bool | dict[str, object]]
        type IsolationLevel = str
        type TransactionBlock = list[dict[str, str | dict[str, object]]]
        type SavepointConfig = dict[str, str | int]
        type RollbackConfig = dict[str, str | bool | list[str]]

    class Schema:
        """Oracle schema complex types.

        Python 3.13+ best practice: Use TypeAlias for better type checking.
        """

        type SchemaDefinition = _TableMetadata
        type TableDefinition = dict[str, str | list[dict[str, str | bool | int]]]
        type ColumnDefinition = dict[str, str | int | bool | dict[str, object]]
        type IndexDefinition = dict[str, str | list[str] | dict[str, object]]
        type ConstraintDefinition = dict[str, str | list[str] | bool]
        type ViewDefinition = dict[str, str | dict[str, object]]

    class Session:
        """Oracle session complex types.

        Python 3.13+ best practice: Use TypeAlias for better type checking.
        """

        type SessionConfiguration = dict[str, str | int | bool | dict[str, object]]
        type SessionState = dict[str, object | dict[str, object]]
        type SessionVariables = dict[str, object]
        type SessionMetrics = dict[str, int | float | str]
        type SessionPooling = dict[str, int | bool | str | dict[str, object]]
        type SessionTimeout = dict[str, int | str]

    class Performance:
        """Oracle performance complex types.

        Python 3.13+ best practice: Use TypeAlias for better type checking.
        """

        type PerformanceMetrics = dict[str, int | float | dict[str, object]]
        type QueryPlan = dict[str, str | int | list[dict[str, object]]]
        type ExecutionStats = dict[str, int | float | str | dict[str, object]]
        type IndexUsage = dict[str, str | int | bool | dict[str, object]]
        type CacheConfiguration = dict[str, int | str | bool]
        type OptimizationHints = dict[str, str | list[str]]

    class Security:
        """Oracle security complex types.

        Python 3.13+ best practice: Use TypeAlias for better type checking.
        """

        type UserPermissions = dict[str, list[str] | dict[str, bool]]
        type RoleDefinition = dict[str, str | list[str] | dict[str, object]]
        type PrivilegeConfiguration = dict[str, bool | list[str] | dict[str, object]]
        type AccessPolicy = dict[str, str | bool | dict[str, object]]
        type EncryptionConfig = dict[str, str | bool | dict[str, object]]
        type AuditConfiguration = dict[str, bool | str | dict[str, object]]

    class DataTypes:
        """Oracle data type complex mappings.

        Python 3.13+ best practice: Use TypeAlias for better type checking.
        """

        type OracleDataType = str
        type PythonDataType = type[object]
        type TypeMapping = _TypeMapping
        type DataConversion = dict[str, object]
        type TypeValidation = dict[str, bool | str | list[str]]
        type NullHandling = dict[str, bool | object]

    class Project:
        """Oracle database-specific project types.

        Adds Oracle database-specific project types.
        Follows domain separation principle: Oracle domain owns
        Oracle-specific types.
        """

        type ProjectType = Literal[
            "library",
            "application",
            "service",
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
        type OracleProjectConfig = dict[str, object]
        type DatabaseConfig = dict[str, str | int | bool | list[str]]
        type SchemaConfig = dict[str, bool | str | dict[str, object]]
        type ConnectionConfig = dict[str, object]

    type ConnectionTypeLiteral = Literal["service_name", "sid", "tns"]
    "Oracle connection type literal - references ConnectionType StrEnum members."
    type QueryTypeLiteral = Literal[
        "SELECT", "INSERT", "UPDATE", "DELETE", "CREATE", "DROP", "ALTER"
    ]
    "Oracle query type literal - references QueryType StrEnum members."
    type DataTypeLiteral = Literal[
        "VARCHAR2", "NUMBER", "DATE", "TIMESTAMP", "CLOB", "BLOB", "CHAR", "RAW"
    ]
    "Oracle data type literal - references DataType StrEnum members."


t = FlextDbOracleTypes
__all__ = ["FlextDbOracleTypes", "t"]
