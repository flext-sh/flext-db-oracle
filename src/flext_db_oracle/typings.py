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
from flext_infra import t

from flext_core import u


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

        type ConnectionConfiguration = t.ContainerValueMapping
        type ConnectionPool = t.ContainerValueMapping
        type ConnectionString = str
        type ConnectionParams = t.ConfigurationMapping
        type SslConfiguration = Mapping[
            str,
            str | bool | t.ContainerValueMapping,
        ]
        type AuthenticationConfig = Mapping[
            str,
            str | t.ContainerValueMapping,
        ]

        type SqlQuery = str
        type QueryParameters = t.ContainerValueMapping
        type QueryResult = t.ContainerValueMapping
        type QueryMetadata = Mapping[
            str,
            str | int | t.ContainerValueMapping,
        ]
        type PreparedStatement = Mapping[
            str,
            str | t.ContainerValueMapping,
        ]
        type QueryExecution = Mapping[
            str,
            t.Scalar | t.ContainerValueMapping,
        ]

        type TransactionConfiguration = t.ConfigurationMapping
        type TransactionState = Mapping[
            str,
            str | bool | t.ContainerValueMapping,
        ]
        type IsolationLevel = str
        type TransactionBlock = Sequence[Mapping[str, str | t.ContainerValueMapping]]
        type SavepointConfig = t.HeaderMapping
        type RollbackConfig = Mapping[str, str | bool | t.StrSequence]

        type SchemaDefinition = t.ContainerValueMapping
        type TableDefinition = Mapping[
            str,
            str | Sequence[Mapping[str, str | bool | int]],
        ]
        type ColumnDefinition = Mapping[
            str,
            t.Scalar | t.ContainerValueMapping,
        ]
        type IndexDefinition = Mapping[
            str,
            str | t.StrSequence | t.ContainerValueMapping,
        ]
        type ConstraintDefinition = Mapping[str, str | t.StrSequence | bool]
        type ViewDefinition = Mapping[
            str,
            str | t.ContainerValueMapping,
        ]

        type SessionConfiguration = Mapping[
            str,
            t.Scalar | t.ContainerValueMapping,
        ]
        type SessionState = Mapping[
            str,
            t.ContainerValue | t.ContainerValueMapping,
        ]
        type SessionVariables = t.ContainerValueMapping
        type SessionMetrics = t.ConfigValueMapping
        type SessionPooling = Mapping[
            str,
            int | bool | str | t.ContainerValueMapping,
        ]
        type SessionTimeout = t.HeaderMapping

        type PerformanceMetrics = Mapping[
            str,
            t.Numeric | t.ContainerValueMapping,
        ]
        type QueryPlan = Mapping[
            str,
            str | int | Sequence[t.ContainerValueMapping],
        ]
        type ExecutionStats = Mapping[
            str,
            t.Numeric | str | t.ContainerValueMapping,
        ]
        type IndexUsage = Mapping[
            str,
            t.Scalar | t.ContainerValueMapping,
        ]
        type CacheConfiguration = Mapping[str, int | str | bool]
        type OptimizationHints = Mapping[str, str | t.StrSequence]

        type UserPermissions = Mapping[str, t.StrSequence | t.BoolMapping]
        type RoleDefinition = Mapping[
            str,
            str | t.StrSequence | t.ContainerValueMapping,
        ]
        type PrivilegeConfiguration = Mapping[
            str,
            bool | t.StrSequence | t.ContainerValueMapping,
        ]
        type AccessPolicy = Mapping[
            str,
            str | bool | t.ContainerValueMapping,
        ]
        type EncryptionConfig = Mapping[
            str,
            str | bool | t.ContainerValueMapping,
        ]
        type AuditConfiguration = Mapping[
            str,
            bool | str | t.ContainerValueMapping,
        ]

        type OracleDataType = str
        type PythonDataType = type
        type TypeMapping = t.ContainerValueMapping
        type DataConversion = t.ContainerValueMapping
        type TypeValidation = Mapping[str, bool | str | t.StrSequence]
        type NullHandling = Mapping[str, bool | t.ContainerValue]

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
        type OracleProjectConfig = t.ContainerValueMapping

        type CliScalar = t.Scalar | None
        "CLI scalar type - Scalar value or None for optional CLI parameters."

    CONTAINER_VALUE_ADAPTER: u.TypeAdapter[t.ContainerValue] = u.TypeAdapter(
        t.ContainerValue
    )
    CONTAINER_VALUE_MAPPING_ADAPTER: u.TypeAdapter[t.ContainerValueMapping] = (
        u.TypeAdapter(t.ContainerValueMapping)
    )
    FLAT_CONTAINER_LIST_ADAPTER: u.TypeAdapter[t.FlatContainerList] = u.TypeAdapter(
        t.FlatContainerList
    )
    STR_SEQUENCE_ADAPTER: u.TypeAdapter[t.StrSequence] = u.TypeAdapter(t.StrSequence)


t = FlextDbOracleTypes

__all__: list[str] = ["FlextDbOracleTypes", "t"]
