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

from flext_core import FlextTypes
from pydantic import TypeAdapter

_ConfigMap = Mapping[str, FlextTypes.ContainerValue]


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
        type ConnectionParams = FlextTypes.ConfigurationMapping
        type SslConfiguration = Mapping[
            str,
            str | bool | Mapping[str, FlextTypes.ContainerValue],
        ]
        type AuthenticationConfig = Mapping[
            str,
            str | Mapping[str, FlextTypes.ContainerValue],
        ]

        type SqlQuery = str
        type QueryParameters = _ConfigMap
        type QueryResult = _ConfigMap
        type QueryMetadata = Mapping[
            str,
            str | int | Mapping[str, FlextTypes.ContainerValue],
        ]
        type PreparedStatement = Mapping[
            str,
            str | Mapping[str, FlextTypes.ContainerValue],
        ]
        type QueryExecution = Mapping[
            str,
            FlextTypes.Scalar | Mapping[str, FlextTypes.ContainerValue],
        ]

        type TransactionConfiguration = FlextTypes.ConfigurationMapping
        type TransactionState = Mapping[
            str,
            str | bool | Mapping[str, FlextTypes.ContainerValue],
        ]
        type IsolationLevel = str
        type TransactionBlock = Sequence[
            Mapping[str, str | Mapping[str, FlextTypes.ContainerValue]]
        ]
        type SavepointConfig = Mapping[str, str | int]
        type RollbackConfig = Mapping[str, str | bool | FlextTypes.StrSequence]

        type SchemaDefinition = _ConfigMap
        type TableDefinition = Mapping[
            str,
            str | Sequence[Mapping[str, str | bool | int]],
        ]
        type ColumnDefinition = Mapping[
            str,
            FlextTypes.Scalar | Mapping[str, FlextTypes.ContainerValue],
        ]
        type IndexDefinition = Mapping[
            str,
            str | FlextTypes.StrSequence | Mapping[str, FlextTypes.ContainerValue],
        ]
        type ConstraintDefinition = Mapping[str, str | FlextTypes.StrSequence | bool]
        type ViewDefinition = Mapping[
            str,
            str | Mapping[str, FlextTypes.ContainerValue],
        ]

        type SessionConfiguration = Mapping[
            str,
            FlextTypes.Scalar | Mapping[str, FlextTypes.ContainerValue],
        ]
        type SessionState = Mapping[
            str,
            FlextTypes.ContainerValue | Mapping[str, FlextTypes.ContainerValue],
        ]
        type SessionVariables = Mapping[str, FlextTypes.ContainerValue]
        type SessionMetrics = Mapping[str, int | float | str]
        type SessionPooling = Mapping[
            str,
            int | bool | str | Mapping[str, FlextTypes.ContainerValue],
        ]
        type SessionTimeout = Mapping[str, int | str]

        type PerformanceMetrics = Mapping[
            str,
            int | float | Mapping[str, FlextTypes.ContainerValue],
        ]
        type QueryPlan = Mapping[
            str,
            str | int | Sequence[Mapping[str, FlextTypes.ContainerValue]],
        ]
        type ExecutionStats = Mapping[
            str,
            int | float | str | Mapping[str, FlextTypes.ContainerValue],
        ]
        type IndexUsage = Mapping[
            str,
            FlextTypes.Scalar | Mapping[str, FlextTypes.ContainerValue],
        ]
        type CacheConfiguration = Mapping[str, int | str | bool]
        type OptimizationHints = Mapping[str, str | FlextTypes.StrSequence]

        type UserPermissions = Mapping[str, FlextTypes.StrSequence | Mapping[str, bool]]
        type RoleDefinition = Mapping[
            str,
            str | FlextTypes.StrSequence | Mapping[str, FlextTypes.ContainerValue],
        ]
        type PrivilegeConfiguration = Mapping[
            str,
            bool | FlextTypes.StrSequence | Mapping[str, FlextTypes.ContainerValue],
        ]
        type AccessPolicy = Mapping[
            str,
            str | bool | Mapping[str, FlextTypes.ContainerValue],
        ]
        type EncryptionConfig = Mapping[
            str,
            str | bool | Mapping[str, FlextTypes.ContainerValue],
        ]
        type AuditConfiguration = Mapping[
            str,
            bool | str | Mapping[str, FlextTypes.ContainerValue],
        ]

        type OracleDataType = str
        type PythonDataType = type
        type TypeMapping = _ConfigMap
        type DataConversion = Mapping[str, FlextTypes.ContainerValue]
        type TypeValidation = Mapping[str, bool | str | FlextTypes.StrSequence]
        type NullHandling = Mapping[str, bool | FlextTypes.ContainerValue]

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
        type OracleProjectConfig = Mapping[str, FlextTypes.ContainerValue]
        type DatabaseConfig = Mapping[str, FlextTypes.Scalar | FlextTypes.StrSequence]
        type SchemaConfig = Mapping[
            str,
            bool | str | Mapping[str, FlextTypes.ContainerValue],
        ]
        type ConnectionConfig = Mapping[str, FlextTypes.ContainerValue]

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

        type CliScalar = FlextTypes.Scalar | None
        "CLI scalar type - Scalar value or None for optional CLI parameters."

    _QUERY_RESULT_ADAPTER: TypeAdapter[FlextTypes.ContainerValue] = TypeAdapter(
        FlextTypes.ContainerValue,
    )


t = FlextDbOracleTypes
__all__ = ["FlextDbOracleTypes", "t"]
