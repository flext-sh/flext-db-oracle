# AUTO-GENERATED FILE — Regenerate with: make gen
"""Flext Db Oracle. Models package.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from types import MappingProxyType
from typing import TYPE_CHECKING

from flext_core.lazy import install_lazy_exports

if TYPE_CHECKING:
    from flext_db_oracle._models.base import FlextDbOracleModelsBase
    from flext_db_oracle._models.command_models import (
        ConnectCommand,
        DisconnectCommand,
        ExecuteManyCommand,
        ExecuteQueryCommand,
        ExecuteStatementCommand,
        FetchOneCommand,
        FlextDbOracleModelsCommand,
        GetColumnsCommand,
        GetSchemasCommand,
        GetTablesCommand,
        TestConnectionCommand,
    )
    from flext_db_oracle._models.connection_models import (
        ConnectionStatus,
        FlextDbOracleModelsConnection,
        HealthStatus,
        OperationRecord,
    )
    from flext_db_oracle._models.credential import FlextDbOracleCredentialModel
    from flext_db_oracle._models.query_models import (
        ColumnMetadata,
        DbOracleDomainModel,
        FlextDbOracleModelsQuery,
        QueryResult,
        RowData,
    )
    from flext_db_oracle._models.schema_models import (
        Column,
        CreateIndexConfig,
        FlextDbOracleModelsSchema,
        Schema,
        SingerField,
        SingerSchema,
        Table,
        TableMetadata,
        TypeMapping,
    )


__all__: tuple[str, ...] = (
    "Column",
    "ColumnMetadata",
    "ConnectCommand",
    "ConnectionStatus",
    "CreateIndexConfig",
    "DbOracleDomainModel",
    "DisconnectCommand",
    "ExecuteManyCommand",
    "ExecuteQueryCommand",
    "ExecuteStatementCommand",
    "FetchOneCommand",
    "FlextDbOracleCredentialModel",
    "FlextDbOracleModelsBase",
    "FlextDbOracleModelsCommand",
    "FlextDbOracleModelsConnection",
    "FlextDbOracleModelsQuery",
    "FlextDbOracleModelsSchema",
    "GetColumnsCommand",
    "GetSchemasCommand",
    "GetTablesCommand",
    "HealthStatus",
    "OperationRecord",
    "QueryResult",
    "RowData",
    "Schema",
    "SingerField",
    "SingerSchema",
    "Table",
    "TableMetadata",
    "TestConnectionCommand",
    "TypeMapping",
)

install_lazy_exports(
    __name__,
    globals(),
    MappingProxyType({
        "Column": ".schema_models",
        "ColumnMetadata": ".query_models",
        "ConnectCommand": ".command_models",
        "ConnectionStatus": ".connection_models",
        "CreateIndexConfig": ".schema_models",
        "DbOracleDomainModel": ".query_models",
        "DisconnectCommand": ".command_models",
        "ExecuteManyCommand": ".command_models",
        "ExecuteQueryCommand": ".command_models",
        "ExecuteStatementCommand": ".command_models",
        "FetchOneCommand": ".command_models",
        "FlextDbOracleCredentialModel": ".credential",
        "FlextDbOracleModelsBase": ".base",
        "FlextDbOracleModelsCommand": ".command_models",
        "FlextDbOracleModelsConnection": ".connection_models",
        "FlextDbOracleModelsQuery": ".query_models",
        "FlextDbOracleModelsSchema": ".schema_models",
        "GetColumnsCommand": ".command_models",
        "GetSchemasCommand": ".command_models",
        "GetTablesCommand": ".command_models",
        "HealthStatus": ".connection_models",
        "OperationRecord": ".connection_models",
        "QueryResult": ".query_models",
        "RowData": ".query_models",
        "Schema": ".schema_models",
        "SingerField": ".schema_models",
        "SingerSchema": ".schema_models",
        "Table": ".schema_models",
        "TableMetadata": ".schema_models",
        "TestConnectionCommand": ".command_models",
        "TypeMapping": ".schema_models",
    }),
    public_exports=__all__,
)
