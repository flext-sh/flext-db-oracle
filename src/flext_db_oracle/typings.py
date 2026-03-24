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

from collections.abc import Mapping, Sequence
from typing import Literal

from flext_core import FlextTypes, t as _core_t
from pydantic import TypeAdapter

_ConfigMap = Mapping[str, _core_t.ContainerValue]


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
        type ConnectionParams = t.ConfigurationMapping
        type SslConfiguration = Mapping[
            str,
            str | bool | Mapping[str, _core_t.ContainerValue],
        ]
        type AuthenticationConfig = Mapping[
            str, str | Mapping[str, _core_t.ContainerValue]
        ]

        type SqlQuery = str
        type QueryParameters = _ConfigMap
        type QueryResult = _ConfigMap
        type QueryMetadata = Mapping[
            str, str | int | Mapping[str, _core_t.ContainerValue]
        ]
        type PreparedStatement = Mapping[
            str, str | Mapping[str, _core_t.ContainerValue]
        ]
        type QueryExecution = Mapping[
            str,
            t.Scalar | Mapping[str, _core_t.ContainerValue],
        ]

        type TransactionConfiguration = t.ConfigurationMapping
        type TransactionState = Mapping[
            str,
            str | bool | Mapping[str, _core_t.ContainerValue],
        ]
        type IsolationLevel = str
        type TransactionBlock = Sequence[
            Mapping[str, str | Mapping[str, _core_t.ContainerValue]]
        ]
        type SavepointConfig = Mapping[str, str | int]
        type RollbackConfig = Mapping[str, str | bool | Sequence[str]]

        type SchemaDefinition = _ConfigMap
        type TableDefinition = Mapping[
            str, str | Sequence[Mapping[str, str | bool | int]]
        ]
        type ColumnDefinition = Mapping[
            str,
            t.Scalar | Mapping[str, _core_t.ContainerValue],
        ]
        type IndexDefinition = Mapping[
            str,
            str | Sequence[str] | Mapping[str, _core_t.ContainerValue],
        ]
        type ConstraintDefinition = Mapping[str, str | Sequence[str] | bool]
        type ViewDefinition = Mapping[str, str | Mapping[str, _core_t.ContainerValue]]

        type SessionConfiguration = Mapping[
            str,
            t.Scalar | Mapping[str, _core_t.ContainerValue],
        ]
        type SessionState = Mapping[
            str,
            _core_t.ContainerValue | Mapping[str, _core_t.ContainerValue],
        ]
        type SessionVariables = Mapping[str, _core_t.ContainerValue]
        type SessionMetrics = Mapping[str, int | float | str]
        type SessionPooling = Mapping[
            str,
            int | bool | str | Mapping[str, _core_t.ContainerValue],
        ]
        type SessionTimeout = Mapping[str, int | str]

        type PerformanceMetrics = Mapping[
            str,
            int | float | Mapping[str, _core_t.ContainerValue],
        ]
        type QueryPlan = Mapping[
            str, str | int | Sequence[Mapping[str, _core_t.ContainerValue]]
        ]
        type ExecutionStats = Mapping[
            str,
            int | float | str | Mapping[str, _core_t.ContainerValue],
        ]
        type IndexUsage = Mapping[
            str,
            t.Scalar | Mapping[str, _core_t.ContainerValue],
        ]
        type CacheConfiguration = Mapping[str, int | str | bool]
        type OptimizationHints = Mapping[str, str | Sequence[str]]

        type UserPermissions = Mapping[str, Sequence[str] | Mapping[str, bool]]
        type RoleDefinition = Mapping[
            str,
            str | Sequence[str] | Mapping[str, _core_t.ContainerValue],
        ]
        type PrivilegeConfiguration = Mapping[
            str,
            bool | Sequence[str] | Mapping[str, _core_t.ContainerValue],
        ]
        type AccessPolicy = Mapping[
            str, str | bool | Mapping[str, _core_t.ContainerValue]
        ]
        type EncryptionConfig = Mapping[
            str,
            str | bool | Mapping[str, _core_t.ContainerValue],
        ]
        type AuditConfiguration = Mapping[
            str,
            bool | str | Mapping[str, _core_t.ContainerValue],
        ]

        type OracleDataType = str
        type PythonDataType = type
        type TypeMapping = _ConfigMap
        type DataConversion = Mapping[str, _core_t.ContainerValue]
        type TypeValidation = Mapping[str, bool | str | Sequence[str]]
        type NullHandling = Mapping[str, bool | _core_t.ContainerValue]

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
        type OracleProjectConfig = Mapping[str, _core_t.ContainerValue]
        type DatabaseConfig = Mapping[str, t.Scalar | Sequence[str]]
        type SchemaConfig = Mapping[
            str, bool | str | Mapping[str, _core_t.ContainerValue]
        ]
        type ConnectionConfig = Mapping[str, _core_t.ContainerValue]

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
