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

from collections.abc import (
    Mapping,
    Sequence,
)
from typing import Literal

import oracledb
from flext_core import u
from flext_infra import t


class FlextDbOracleTypes(t):
    """Oracle database-specific type definitions extending t.

    Domain-specific type system for Oracle database operations.
    Contains ONLY complex Oracle-specific types, no simple aliases.
    Uses Python 3.13+ type syntax and patterns.
    """

    class DbOracle:
        """Oracle connection complex types.

        Python 3.13+ best practice: keep contracts centralized in inherited `t.*`.
        """

        OracleDatabaseError: type[Exception] = oracledb.DatabaseError
        OracleInterfaceError: type[Exception] = oracledb.InterfaceError

        type ConnectionConfiguration = t.JsonMapping
        type ConnectionPool = t.JsonMapping
        type ConnectionString = str
        type ConnectionParams = t.ConfigurationMapping
        type SslConfiguration = Mapping[
            str,
            str | bool | t.JsonMapping,
        ]
        type AuthenticationConfig = Mapping[
            str,
            str | t.JsonMapping,
        ]

        type SqlQuery = str
        type QueryParameters = t.JsonMapping
        type QueryResult = t.JsonMapping
        type QueryMetadata = Mapping[
            str,
            str | int | t.JsonMapping,
        ]
        type PreparedStatement = Mapping[
            str,
            str | t.JsonMapping,
        ]
        type QueryExecution = Mapping[
            str,
            t.Scalar | t.JsonMapping,
        ]

        type TransactionConfiguration = t.ConfigurationMapping
        type TransactionState = Mapping[
            str,
            str | bool | t.JsonMapping,
        ]
        type IsolationLevel = str
        type TransactionBlock = Sequence[Mapping[str, str | t.JsonMapping]]
        type SavepointConfig = t.HeaderMapping
        type RollbackConfig = Mapping[str, str | bool | t.StrSequence]

        type SchemaDefinition = t.JsonMapping
        type TableDefinition = Mapping[
            str,
            str | Sequence[Mapping[str, str | bool | int]],
        ]
        type ColumnDefinition = Mapping[
            str,
            t.Scalar | t.JsonMapping,
        ]
        type IndexDefinition = Mapping[
            str,
            str | t.StrSequence | t.JsonMapping,
        ]
        type ConstraintDefinition = Mapping[str, str | t.StrSequence | bool]
        type ViewDefinition = Mapping[
            str,
            str | t.JsonMapping,
        ]

        type SessionConfiguration = Mapping[
            str,
            t.Scalar | t.JsonMapping,
        ]
        type SessionState = Mapping[
            str,
            t.JsonValue | t.JsonMapping,
        ]
        type SessionVariables = t.JsonMapping
        type SessionMetrics = t.ConfigValueMapping
        type SessionPooling = Mapping[
            str,
            int | bool | str | t.JsonMapping,
        ]
        type SessionTimeout = t.HeaderMapping

        type PerformanceMetrics = Mapping[
            str,
            t.Numeric | t.JsonMapping,
        ]
        type QueryPlan = Mapping[
            str,
            str | int | Sequence[t.JsonMapping],
        ]
        type ExecutionStats = Mapping[
            str,
            t.Numeric | str | t.JsonMapping,
        ]
        type IndexUsage = Mapping[
            str,
            t.Scalar | t.JsonMapping,
        ]
        type CacheConfiguration = Mapping[str, int | str | bool]
        type OptimizationHints = Mapping[str, str | t.StrSequence]

        type UserPermissions = Mapping[str, t.StrSequence | t.BoolMapping]
        type RoleDefinition = Mapping[
            str,
            str | t.StrSequence | t.JsonMapping,
        ]
        type PrivilegeConfiguration = Mapping[
            str,
            bool | t.StrSequence | t.JsonMapping,
        ]
        type AccessPolicy = Mapping[
            str,
            str | bool | t.JsonMapping,
        ]
        type EncryptionConfig = Mapping[
            str,
            str | bool | t.JsonMapping,
        ]
        type AuditConfiguration = Mapping[
            str,
            bool | str | t.JsonMapping,
        ]

        type OracleDataType = str
        type PythonDataType = type
        type TypeMapping = t.JsonMapping
        type DataConversion = t.JsonMapping
        type TypeValidation = Mapping[str, bool | str | t.StrSequence]
        type NullHandling = Mapping[str, bool | t.JsonValue]

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
        type OracleProjectConfig = t.JsonMapping

        type CliScalar = t.Scalar | None
        "CLI scalar type - Scalar value or None for optional CLI parameters."

    CONTAINER_VALUE_ADAPTER: u.TypeAdapter[t.JsonValue] = u.TypeAdapter(t.JsonValue)
    CONTAINER_VALUE_MAPPING_ADAPTER: u.TypeAdapter[t.JsonMapping] = u.TypeAdapter(
        t.JsonMapping
    )
    FLAT_CONTAINER_LIST_ADAPTER: u.TypeAdapter[t.JsonList] = u.TypeAdapter(t.JsonList)
    STR_SEQUENCE_ADAPTER: u.TypeAdapter[t.StrSequence] = u.TypeAdapter(t.StrSequence)


t = FlextDbOracleTypes

__all__: list[str] = ["FlextDbOracleTypes", "t"]
