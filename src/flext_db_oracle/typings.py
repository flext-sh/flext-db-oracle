"""FLEXT DB Oracle Types - Domain-specific Oracle database type definitions.

This module provides Oracle database-specific type definitions extending FlextTypes.
Follows FLEXT standards:
- Domain-specific complex types only
- No simple aliases to primitive types
- Python 3.13+ syntax
- Extends FlextInfraTypes properly

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Literal

import oracledb
from flext_cli import FlextInfraTypes
from pydantic import TypeAdapter

from flext_core import FlextTypes


class FlextDbOracleTypes(FlextInfraTypes):
    """Oracle database-specific type definitions extending FlextTypes.

    Domain-specific type system for Oracle database operations.
    Contains ONLY complex Oracle-specific types, no simple aliases.
    Uses Python 3.13+ type syntax and patterns.
    """

    class DbOracle:
        """Oracle connection complex types.

        Python 3.13+ best practice: keep contracts centralized in inherited `FlextInfraTypes.*`.
        """

        OracleDatabaseError: type[Exception] = oracledb.DatabaseError
        OracleInterfaceError: type[Exception] = oracledb.InterfaceError

        type ConnectionConfiguration = FlextTypes.ContainerValueMapping
        type ConnectionPool = FlextTypes.ContainerValueMapping
        type ConnectionString = str
        type ConnectionParams = FlextTypes.ConfigurationMapping
        type SslConfiguration = Mapping[
            str,
            str | bool | FlextTypes.ContainerValueMapping,
        ]
        type AuthenticationConfig = Mapping[
            str,
            str | FlextTypes.ContainerValueMapping,
        ]

        type SqlQuery = str
        type QueryParameters = FlextTypes.ContainerValueMapping
        type QueryResult = FlextTypes.ContainerValueMapping
        type QueryMetadata = Mapping[
            str,
            str | int | FlextTypes.ContainerValueMapping,
        ]
        type PreparedStatement = Mapping[
            str,
            str | FlextTypes.ContainerValueMapping,
        ]
        type QueryExecution = Mapping[
            str,
            FlextTypes.Scalar | FlextTypes.ContainerValueMapping,
        ]

        type TransactionConfiguration = FlextTypes.ConfigurationMapping
        type TransactionState = Mapping[
            str,
            str | bool | FlextTypes.ContainerValueMapping,
        ]
        type IsolationLevel = str
        type TransactionBlock = Sequence[
            Mapping[str, str | FlextTypes.ContainerValueMapping]
        ]
        type SavepointConfig = FlextTypes.HeaderMapping
        type RollbackConfig = Mapping[str, str | bool | FlextTypes.StrSequence]

        type SchemaDefinition = FlextTypes.ContainerValueMapping
        type TableDefinition = Mapping[
            str,
            str | Sequence[Mapping[str, str | bool | int]],
        ]
        type ColumnDefinition = Mapping[
            str,
            FlextTypes.Scalar | FlextTypes.ContainerValueMapping,
        ]
        type IndexDefinition = Mapping[
            str,
            str | FlextTypes.StrSequence | FlextTypes.ContainerValueMapping,
        ]
        type ConstraintDefinition = Mapping[str, str | FlextTypes.StrSequence | bool]
        type ViewDefinition = Mapping[
            str,
            str | FlextTypes.ContainerValueMapping,
        ]

        type SessionConfiguration = Mapping[
            str,
            FlextTypes.Scalar | FlextTypes.ContainerValueMapping,
        ]
        type SessionState = Mapping[
            str,
            FlextTypes.ContainerValue | FlextTypes.ContainerValueMapping,
        ]
        type SessionVariables = FlextTypes.ContainerValueMapping
        type SessionMetrics = FlextTypes.ConfigValueMapping
        type SessionPooling = Mapping[
            str,
            int | bool | str | FlextTypes.ContainerValueMapping,
        ]
        type SessionTimeout = FlextInfraTypes.HeaderMapping

        type PerformanceMetrics = Mapping[
            str,
            FlextInfraTypes.Numeric | FlextTypes.ContainerValueMapping,
        ]
        type QueryPlan = Mapping[
            str,
            str | int | Sequence[FlextTypes.ContainerValueMapping],
        ]
        type ExecutionStats = Mapping[
            str,
            FlextInfraTypes.Numeric | str | FlextTypes.ContainerValueMapping,
        ]
        type IndexUsage = Mapping[
            str,
            FlextTypes.Scalar | FlextTypes.ContainerValueMapping,
        ]
        type CacheConfiguration = Mapping[str, int | str | bool]
        type OptimizationHints = Mapping[str, str | FlextTypes.StrSequence]

        type UserPermissions = Mapping[
            str, FlextTypes.StrSequence | FlextInfraTypes.BoolMapping
        ]
        type RoleDefinition = Mapping[
            str,
            str | FlextTypes.StrSequence | FlextTypes.ContainerValueMapping,
        ]
        type PrivilegeConfiguration = Mapping[
            str,
            bool | FlextTypes.StrSequence | FlextTypes.ContainerValueMapping,
        ]
        type AccessPolicy = Mapping[
            str,
            str | bool | FlextTypes.ContainerValueMapping,
        ]
        type EncryptionConfig = Mapping[
            str,
            str | bool | FlextTypes.ContainerValueMapping,
        ]
        type AuditConfiguration = Mapping[
            str,
            bool | str | FlextTypes.ContainerValueMapping,
        ]

        type OracleDataType = str
        type PythonDataType = type
        type TypeMapping = FlextTypes.ContainerValueMapping
        type DataConversion = FlextTypes.ContainerValueMapping
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
        type OracleProjectConfig = FlextTypes.ContainerValueMapping

        type CliScalar = FlextTypes.Scalar | None
        "CLI scalar type - Scalar value or None for optional CLI parameters."

    CONTAINER_VALUE_ADAPTER: TypeAdapter[FlextTypes.ContainerValue] = TypeAdapter(
        FlextTypes.ContainerValue,
    )
    CONTAINER_VALUE_MAPPING_ADAPTER: TypeAdapter[FlextTypes.ContainerValueMapping] = (
        TypeAdapter(FlextTypes.ContainerValueMapping)
    )
    FLAT_CONTAINER_LIST_ADAPTER: TypeAdapter[FlextTypes.FlatContainerList] = (
        TypeAdapter(FlextTypes.FlatContainerList)
    )
    STR_SEQUENCE_ADAPTER: TypeAdapter[FlextTypes.StrSequence] = TypeAdapter(
        FlextTypes.StrSequence,
    )


t = FlextDbOracleTypes

__all__ = ["FlextDbOracleTypes", "t"]
