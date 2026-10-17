"""Oracle Database schema, Singer mapping and DDL models.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from types import MappingProxyType
from typing import cast

from flext_cli import FlextCliModels
from flext_core import u as core_u

from flext_db_oracle import t
from flext_db_oracle._models.query_models import FlextDbOracleModelsQuery


class FlextDbOracleModelsSchema:
    """Oracle Database schema models composed into ``m.DbOracle``."""

    class TableMetadata(FlextCliModels.Entity):
        """Complete table metadata for Oracle introspection."""

        table_name: str = core_u.Field(description="Oracle table name")
        schema_name: str = core_u.Field(
            "",
            description="Oracle schema name",
            validate_default=True,
        )
        columns: t.SequenceOf[FlextDbOracleModelsQuery.ColumnMetadata] = core_u.Field(
            default_factory=lambda: (),
            description="Column metadata for the table",
        )
        primary_keys: t.StrSequence = core_u.Field(
            default_factory=tuple[str, ...],
            description="Primary key column names",
        )

        def __getitem__(self, key: str) -> t.JsonValue:
            """Get item from table metadata.

            Returns:
                The resulting ``t.JsonValue``.

            """
            dump = self.model_dump()
            value = dump.get(key, "")
            return str(value)

        def __contains__(self, key: str) -> bool:
            """Check if key is in table metadata.

            Returns:
                The resulting ``bool``.

            """
            return key in self.model_dump()

    class TypeMapping(FlextCliModels.Entity):
        """Singer-to-Oracle type mapping."""

        mapping: t.StrMapping = core_u.Field(
            default_factory=lambda: MappingProxyType[str, str]({}),
            description="Singer-to-Oracle type conversion map",
        )

        def __getitem__(self, key: str) -> str:
            """Get mapped type for key.

            Returns:
                The resulting ``str``.

            """
            value: str = self.mapping[key]
            return value

        def __len__(self) -> int:
            """Get number of type mappings.

            Returns:
                The resulting ``int``.

            """
            return len(self.mapping)

        def __contains__(self, key: str) -> bool:
            """Check if key is in type mapping.

            Returns:
                The resulting ``bool``.

            """
            return key in self.mapping

    class SingerField(FlextCliModels.Entity):
        """Singer field definition."""

        type: str | t.StrSequence = core_u.Field(
            "string",
            description="Singer JSON Schema type or type array",
            validate_default=True,
        )

    class SingerSchema(FlextCliModels.Entity):
        """Singer schema container with typed properties."""

        properties: t.MappingKV[str, FlextDbOracleModelsSchema.SingerField] = (
            core_u.Field(
                default_factory=lambda: MappingProxyType(
                    cast(
                        "dict[str, FlextDbOracleModelsSchema.SingerField]",
                        {},
                    ),
                ),
                description="Singer schema property definitions",
            )
        )

    class Table(FlextCliModels.Entity):
        """Table metadata using flext-core Entity."""

        name: str = core_u.Field(description="Table name")
        owner: str = core_u.Field(
            "",
            description="Table owner or schema",
            validate_default=True,
        )
        columns: t.SequenceOf[FlextDbOracleModelsSchema.Column] = core_u.Field(
            default_factory=lambda: (),
            description="Column definitions for the table",
        )

    class Column(FlextCliModels.Entity):
        """Column metadata using flext-core Entity."""

        name: str = core_u.Field(description="Column name")
        data_type: str = core_u.Field(description="Oracle data type")
        nullable: bool = core_u.Field(
            default=True,
            description="Whether the column allows NULL values",
            validate_default=True,
        )
        primary_key: bool = core_u.Field(
            default=False,
            description="Whether this column is a primary key",
            validate_default=True,
        )
        default_value: str = core_u.Field(
            "",
            description="Default value for the column",
            validate_default=True,
        )

        def __getitem__(self, key: str) -> t.JsonValue:
            """Get item from column metadata.

            Returns:
                The resulting ``t.JsonValue``.

            """
            key_map: t.JsonMapping = {
                "column_name": self.name,
                "name": self.name,
                "data_type": self.data_type,
                "nullable": self.nullable,
                "primary_key": self.primary_key,
                "default_value": self.default_value,
            }
            if key in key_map:
                return key_map[key]
            return ""

        def __contains__(self, key: str) -> bool:
            """Check if key is in column metadata.

            Returns:
                The resulting ``bool``.

            """
            return key in {
                "name",
                "column_name",
                "data_type",
                "nullable",
                "primary_key",
                "default_value",
            }

    class Schema(FlextCliModels.Entity):
        """Schema metadata using flext-core Entity."""

        name: str = core_u.Field(description="Schema name")
        tables: t.SequenceOf[FlextDbOracleModelsSchema.Table] = core_u.Field(
            default_factory=lambda: (),
            description="Tables within this schema",
        )

    class CreateIndexConfig(FlextCliModels.Entity):
        """Create index settings using flext-core Entity."""

        table_name: str = core_u.Field(description="Target table for the index")
        index_name: str = core_u.Field(description="Name of the index to create")
        columns: t.StrSequence = core_u.Field(
            description="Columns to include in the index",
        )
        unique: bool = core_u.Field(
            default=False,
            description="Whether the index enforces uniqueness",
            validate_default=True,
        )
        schema_name: str = core_u.Field(
            "",
            description="Schema name",
            validate_default=True,
        )
        tablespace: str = core_u.Field(
            "",
            description="Tablespace name",
            validate_default=True,
        )
        parallel: t.PositiveInt = core_u.Field(
            1,
            description="Parallel degree for index creation",
            validate_default=True,
        )


__all__: list[str] = ["FlextDbOracleModelsSchema"]
