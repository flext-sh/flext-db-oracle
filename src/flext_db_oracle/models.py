# AUTO-GENERATED FILE — Regenerate with: make gen
"""Oracle Database models using FLEXT ecosystem patterns.

This module provides Oracle-specific models extending flext-core patterns
for data structures and domain objects.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from flext_cli import FlextCliModels

from flext_db_oracle._models import (
    FlextDbOracleCredentialModel,
    FlextDbOracleModelsBase,
    FlextDbOracleModelsCommand,
    FlextDbOracleModelsConnection,
    FlextDbOracleModelsQuery,
    FlextDbOracleModelsSchema,
)


class FlextDbOracleModels(FlextCliModels):
    """Oracle database models using flext-core exclusively.

    Contains ONLY pure domain models (Entity, Value, AggregateRoot, etc.).
    All settings-like classes moved to settings.py.
    All constants moved to constants.py.
    All types moved to typings.py.
    """

    class DbOracle(
        FlextDbOracleModelsBase,
        FlextDbOracleModelsCommand,
        FlextDbOracleModelsConnection,
        FlextDbOracleCredentialModel,
        FlextDbOracleModelsQuery,
        FlextDbOracleModelsSchema,
    ):
        """DbOracle domain namespace."""

        Password = FlextDbOracleCredentialModel

        DbOracleDomainModel = FlextDbOracleModelsQuery.DbOracleDomainModel
        RowData = FlextDbOracleModelsQuery.RowData
        ColumnMetadata = FlextDbOracleModelsQuery.ColumnMetadata
        ConnectionStatus = FlextDbOracleModelsConnection.ConnectionStatus
        QueryResult = FlextDbOracleModelsQuery.QueryResult
        OperationRecord = FlextDbOracleModelsConnection.OperationRecord
        HealthStatus = FlextDbOracleModelsConnection.HealthStatus
        TableMetadata = FlextDbOracleModelsSchema.TableMetadata
        TypeMapping = FlextDbOracleModelsSchema.TypeMapping
        SingerField = FlextDbOracleModelsSchema.SingerField
        SingerSchema = FlextDbOracleModelsSchema.SingerSchema
        Table = FlextDbOracleModelsSchema.Table
        Column = FlextDbOracleModelsSchema.Column
        Schema = FlextDbOracleModelsSchema.Schema
        CreateIndexConfig = FlextDbOracleModelsSchema.CreateIndexConfig

        # Command classes for dispatcher integration
        ConnectCommand = FlextDbOracleModelsCommand.ConnectCommand
        DisconnectCommand = FlextDbOracleModelsCommand.DisconnectCommand
        TestConnectionCommand = FlextDbOracleModelsCommand.TestConnectionCommand
        ExecuteQueryCommand = FlextDbOracleModelsCommand.ExecuteQueryCommand
        FetchOneCommand = FlextDbOracleModelsCommand.FetchOneCommand
        ExecuteStatementCommand = FlextDbOracleModelsCommand.ExecuteStatementCommand
        ExecuteManyCommand = FlextDbOracleModelsCommand.ExecuteManyCommand
        GetSchemasCommand = FlextDbOracleModelsCommand.GetSchemasCommand
        GetTablesCommand = FlextDbOracleModelsCommand.GetTablesCommand
        GetColumnsCommand = FlextDbOracleModelsCommand.GetColumnsCommand


m = FlextDbOracleModels

__all__: list[str] = ["FlextDbOracleModels", "m"]
