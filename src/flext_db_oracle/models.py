# AUTO-GENERATED FILE — Regenerate with: make gen
"""Oracle Database models using FLEXT ecosystem patterns.

This module provides Oracle-specific models extending flext-core patterns
for data structures and domain objects.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from typing import ClassVar

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

        Password: ClassVar[type[FlextDbOracleCredentialModel]] = (
            FlextDbOracleCredentialModel
        )

        DbOracleDomainModel: ClassVar[
            type[FlextDbOracleModelsQuery.DbOracleDomainModel]
        ] = FlextDbOracleModelsQuery.DbOracleDomainModel
        RowData: ClassVar[type[FlextDbOracleModelsQuery.RowData]] = (
            FlextDbOracleModelsQuery.RowData
        )
        ColumnMetadata: ClassVar[type[FlextDbOracleModelsQuery.ColumnMetadata]] = (
            FlextDbOracleModelsQuery.ColumnMetadata
        )
        ConnectionStatus: ClassVar[
            type[FlextDbOracleModelsConnection.ConnectionStatus]
        ] = FlextDbOracleModelsConnection.ConnectionStatus
        QueryResult: ClassVar[type[FlextDbOracleModelsQuery.QueryResult]] = (
            FlextDbOracleModelsQuery.QueryResult
        )
        OperationRecord: ClassVar[
            type[FlextDbOracleModelsConnection.OperationRecord]
        ] = FlextDbOracleModelsConnection.OperationRecord
        HealthStatus: ClassVar[type[FlextDbOracleModelsConnection.HealthStatus]] = (
            FlextDbOracleModelsConnection.HealthStatus
        )
        TableMetadata: ClassVar[type[FlextDbOracleModelsSchema.TableMetadata]] = (
            FlextDbOracleModelsSchema.TableMetadata
        )
        TypeMapping: ClassVar[type[FlextDbOracleModelsSchema.TypeMapping]] = (
            FlextDbOracleModelsSchema.TypeMapping
        )
        SingerField: ClassVar[type[FlextDbOracleModelsSchema.SingerField]] = (
            FlextDbOracleModelsSchema.SingerField
        )
        SingerSchema: ClassVar[type[FlextDbOracleModelsSchema.SingerSchema]] = (
            FlextDbOracleModelsSchema.SingerSchema
        )
        Table: ClassVar[type[FlextDbOracleModelsSchema.Table]] = (
            FlextDbOracleModelsSchema.Table
        )
        Column: ClassVar[type[FlextDbOracleModelsSchema.Column]] = (
            FlextDbOracleModelsSchema.Column
        )
        Schema: ClassVar[type[FlextDbOracleModelsSchema.Schema]] = (
            FlextDbOracleModelsSchema.Schema
        )
        CreateIndexConfig: ClassVar[
            type[FlextDbOracleModelsSchema.CreateIndexConfig]
        ] = FlextDbOracleModelsSchema.CreateIndexConfig

        # Command classes for dispatcher integration
        ConnectCommand: ClassVar[type[FlextDbOracleModelsCommand.ConnectCommand]] = (
            FlextDbOracleModelsCommand.ConnectCommand
        )
        DisconnectCommand: ClassVar[
            type[FlextDbOracleModelsCommand.DisconnectCommand]
        ] = FlextDbOracleModelsCommand.DisconnectCommand
        TestConnectionCommand: ClassVar[
            type[FlextDbOracleModelsCommand.TestConnectionCommand]
        ] = FlextDbOracleModelsCommand.TestConnectionCommand
        ExecuteQueryCommand: ClassVar[
            type[FlextDbOracleModelsCommand.ExecuteQueryCommand]
        ] = FlextDbOracleModelsCommand.ExecuteQueryCommand
        FetchOneCommand: ClassVar[type[FlextDbOracleModelsCommand.FetchOneCommand]] = (
            FlextDbOracleModelsCommand.FetchOneCommand
        )
        ExecuteStatementCommand: ClassVar[
            type[FlextDbOracleModelsCommand.ExecuteStatementCommand]
        ] = FlextDbOracleModelsCommand.ExecuteStatementCommand
        ExecuteManyCommand: ClassVar[
            type[FlextDbOracleModelsCommand.ExecuteManyCommand]
        ] = FlextDbOracleModelsCommand.ExecuteManyCommand
        GetSchemasCommand: ClassVar[
            type[FlextDbOracleModelsCommand.GetSchemasCommand]
        ] = FlextDbOracleModelsCommand.GetSchemasCommand
        GetTablesCommand: ClassVar[
            type[FlextDbOracleModelsCommand.GetTablesCommand]
        ] = FlextDbOracleModelsCommand.GetTablesCommand
        GetColumnsCommand: ClassVar[
            type[FlextDbOracleModelsCommand.GetColumnsCommand]
        ] = FlextDbOracleModelsCommand.GetColumnsCommand


m = FlextDbOracleModels

__all__: list[str] = ["FlextDbOracleModels", "m"]
