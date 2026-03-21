"""FLEXT DB Oracle Types - Domain-specific Oracle database type definitions.

This module provides Oracle database-specific type definitions extending FlextTypes.
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
from pydantic import TypeAdapter

_ConfigMap = dict[str, _core_t.ContainerValue]


class FlextDbOracleTypes(FlextTypes):
    """Oracle database-specific type definitions extending FlextTypes.

    Domain-specific type system for Oracle database operations.
    Contains ONLY complex Oracle-specific types, no simple aliases.
    Uses Python 3.13+ type syntax and patterns.
    """

    class DbOracle:
        """Oracle connection complex types.

        Python 3.13+ best practice: Use TypeAlias for better type checking.
        """

        type ConnectionConfiguration = _ConfigMap
        type ConnectionPool = _ConfigMap
        type ConnectionString = str
        type ConnectionParams = dict[str, str | int | bool]
        type SslConfiguration = dict[
            str,
            str | bool | dict[str, _core_t.ContainerValue],
        ]
        type AuthenticationConfig = dict[str, str | dict[str, _core_t.ContainerValue]]

        type SqlQuery = str
        type QueryParameters = _ConfigMap
        type QueryResult = _ConfigMap
        type QueryMetadata = dict[str, str | int | dict[str, _core_t.ContainerValue]]
        type PreparedStatement = dict[str, str | dict[str, _core_t.ContainerValue]]
        type QueryExecution = dict[
            str,
            str | int | bool | dict[str, _core_t.ContainerValue],
        ]

        type TransactionConfiguration = dict[str, str | int | bool]
        type TransactionState = dict[
            str,
            str | bool | dict[str, _core_t.ContainerValue],
        ]
        type IsolationLevel = str
        type TransactionBlock = list[dict[str, str | dict[str, _core_t.ContainerValue]]]
        type SavepointConfig = dict[str, str | int]
        type RollbackConfig = dict[str, str | bool | list[str]]

        type SchemaDefinition = _ConfigMap
        type TableDefinition = dict[str, str | list[dict[str, str | bool | int]]]
        type ColumnDefinition = dict[
            str,
            str | int | bool | dict[str, _core_t.ContainerValue],
        ]
        type IndexDefinition = dict[
            str,
            str | list[str] | dict[str, _core_t.ContainerValue],
        ]
        type ConstraintDefinition = dict[str, str | list[str] | bool]
        type ViewDefinition = dict[str, str | dict[str, _core_t.ContainerValue]]

        type SessionConfiguration = dict[
            str,
            str | int | bool | dict[str, _core_t.ContainerValue],
        ]
        type SessionState = dict[
            str,
            _core_t.ContainerValue | dict[str, _core_t.ContainerValue],
        ]
        type SessionVariables = dict[str, _core_t.ContainerValue]
        type SessionMetrics = dict[str, int | float | str]
        type SessionPooling = dict[
            str,
            int | bool | str | dict[str, _core_t.ContainerValue],
        ]
        type SessionTimeout = dict[str, int | str]

        type PerformanceMetrics = dict[
            str,
            int | float | dict[str, _core_t.ContainerValue],
        ]
        type QueryPlan = dict[str, str | int | list[dict[str, _core_t.ContainerValue]]]
        type ExecutionStats = dict[
            str,
            int | float | str | dict[str, _core_t.ContainerValue],
        ]
        type IndexUsage = dict[
            str,
            str | int | bool | dict[str, _core_t.ContainerValue],
        ]
        type CacheConfiguration = dict[str, int | str | bool]
        type OptimizationHints = dict[str, str | list[str]]

        type UserPermissions = dict[str, list[str] | dict[str, bool]]
        type RoleDefinition = dict[
            str,
            str | list[str] | dict[str, _core_t.ContainerValue],
        ]
        type PrivilegeConfiguration = dict[
            str,
            bool | list[str] | dict[str, _core_t.ContainerValue],
        ]
        type AccessPolicy = dict[str, str | bool | dict[str, _core_t.ContainerValue]]
        type EncryptionConfig = dict[
            str,
            str | bool | dict[str, _core_t.ContainerValue],
        ]
        type AuditConfiguration = dict[
            str,
            bool | str | dict[str, _core_t.ContainerValue],
        ]

        type OracleDataType = str
        type PythonDataType = type
        type TypeMapping = _ConfigMap
        type DataConversion = dict[str, _core_t.ContainerValue]
        type TypeValidation = dict[str, bool | str | list[str]]
        type NullHandling = dict[str, bool | _core_t.ContainerValue]

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
        type OracleProjectConfig = dict[str, _core_t.ContainerValue]
        type DatabaseConfig = dict[str, str | int | bool | list[str]]
        type SchemaConfig = dict[str, bool | str | dict[str, _core_t.ContainerValue]]
        type ConnectionConfig = dict[str, _core_t.ContainerValue]

        type ConnectionTypeLiteral = Literal["service_name", "sid", "tns"]
        type QueryTypeLiteral = Literal[
            "SELECT",
            "INSERT",
            "UPDATE",
            "DELETE",
            "CREATE",
            "DROP",
            "ALTER",
        ]
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

        type CliScalar = _core_t.Scalar | None
        "CLI scalar type - Scalar value or None for optional CLI parameters."

    _QUERY_RESULT_ADAPTER: TypeAdapter[FlextTypes.ContainerValue] = TypeAdapter(
        FlextTypes.ContainerValue,
    )


t = FlextDbOracleTypes
__all__ = ["FlextDbOracleTypes", "t"]
