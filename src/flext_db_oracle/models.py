"""Oracle Database models using FLEXT ecosystem patterns.

This module provides Oracle-specific models extending flext-core patterns
for data structures and domain objects.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from flext_cli import FlextCliModels

from flext_db_oracle._models import (
    command_models as _command_models,
    connection_models as _connection_models,
    query_models as _query_models,
    schema_models as _schema_models,
)
from flext_db_oracle._models.base import FlextDbOracleModelsBase
from flext_db_oracle._models.credential import FlextDbOracleCredentialModel


class FlextDbOracleModels(FlextCliModels):
    """Oracle database models using flext-core exclusively.

    Contains ONLY pure domain models (Entity, Value, AggregateRoot, etc.).
    All settings-like classes moved to settings.py.
    All constants moved to constants.py.
    All types moved to typings.py.
    """

    class DbOracle(FlextDbOracleModelsBase):
        """DbOracle domain namespace."""

        Password = FlextDbOracleCredentialModel

        DbOracleDomainModel = _query_models.DbOracleDomainModel
        RowData = _query_models.RowData
        ColumnMetadata = _query_models.ColumnMetadata
        ConnectionStatus = _connection_models.ConnectionStatus
        QueryResult = _query_models.QueryResult
        OperationRecord = _connection_models.OperationRecord
        HealthStatus = _connection_models.HealthStatus
        TableMetadata = _schema_models.TableMetadata
        TypeMapping = _schema_models.TypeMapping
        SingerField = _schema_models.SingerField
        SingerSchema = _schema_models.SingerSchema
        Table = _schema_models.Table
        Column = _schema_models.Column
        Schema = _schema_models.Schema
        CreateIndexConfig = _schema_models.CreateIndexConfig

        # Command classes for dispatcher integration
        ConnectCommand = _command_models.ConnectCommand
        DisconnectCommand = _command_models.DisconnectCommand
        TestConnectionCommand = _command_models.TestConnectionCommand
        ExecuteQueryCommand = _command_models.ExecuteQueryCommand
        FetchOneCommand = _command_models.FetchOneCommand
        ExecuteStatementCommand = _command_models.ExecuteStatementCommand
        ExecuteManyCommand = _command_models.ExecuteManyCommand
        GetSchemasCommand = _command_models.GetSchemasCommand
        GetTablesCommand = _command_models.GetTablesCommand
        GetColumnsCommand = _command_models.GetColumnsCommand


m = FlextDbOracleModels

__all__: list[str] = ["FlextDbOracleModels", "m"]
