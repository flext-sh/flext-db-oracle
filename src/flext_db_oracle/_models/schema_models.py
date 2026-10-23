"""Oracle Database schema, Singer mapping and DDL models.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from types import MappingProxyType
from typing import cast

from flext_cli import m

from flext_db_oracle import t
from flext_db_oracle._models import FlextDbOracleModelsQuery


class FlextDbOracleModelsSchema:
    """Oracle Database schema models composed into ``m.DbOracle``."""

    class TableMetadata(m.Entity):
        """Complete table metadata for Oracle introspection."""

        table_name: str = m.Field(description="Oracle table name")
        schema_name: str = m.Field(
            default="",
            description="Oracle schema name",
            validate_default=True,
        )
        columns: t.SequenceOf[FlextDbOracleModelsQuery.ColumnMetadata] = m.Field(
            default_factory=lambda: (),
            description="Column metadata for the table",
        )
        primary_keys: t.StrSequence = m.Field(
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

    class TypeMapping(m.Entity):
        """Singer-to-Oracle type mapping."""

        mapping: t.StrMapping = m.Field(
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

    class SingerField(m.Entity):
        """Singer field definition."""

        type: str | t.StrSequence = m.Field(
            default="string",
            description="Singer JSON Schema type or type array",
            validate_default=True,
        )

    class SingerSchema(m.Entity):
        """Singer schema container with typed properties."""

        properties: t.MappingKV[str, FlextDbOracleModelsSchema.SingerField] = m.Field(
            default_factory=lambda: MappingProxyType(
                cast(
                    "dict[str, FlextDbOracleModelsSchema.SingerField]",
                    {},
                ),
            ),
            description="Singer schema property definitions",
        )

    class Table(m.Entity):
        """Table metadata using flext-core Entity."""

        name: str = m.Field(description="Table name")
        owner: str = m.Field(
            default="",
            description="Table owner or schema",
            validate_default=True,
        )
        columns: t.SequenceOf[FlextDbOracleModelsSchema.Column] = m.Field(
            default_factory=lambda: (),
            description="Column definitions for the table",
        )

    class Column(m.Entity):
        """Column metadata using flext-core Entity."""

        name: str = m.Field(description="Column name")
        data_type: str = m.Field(description="Oracle data type")
        nullable: bool = m.Field(
            default=True,
            description="Whether the column allows NULL values",
            validate_default=True,
        )
        primary_key: bool = m.Field(
            default=False,
            description="Whether this column is a primary key",
            validate_default=True,
        )
        default_value: str = m.Field(
            default="",
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

    class Schema(m.Entity):
        """Schema metadata using flext-core Entity."""

        name: str = m.Field(description="Schema name")
        tables: t.SequenceOf[FlextDbOracleModelsSchema.Table] = m.Field(
            default_factory=lambda: (),
            description="Tables within this schema",
        )

    class CreateIndexConfig(m.Entity):
        """Create index settings using flext-core Entity."""

        table_name: str = m.Field(description="Target table for the index")
        index_name: str = m.Field(description="Name of the index to create")
        columns: t.StrSequence = m.Field(
            description="Columns to include in the index",
        )
        unique: bool = m.Field(
            default=False,
            description="Whether the index enforces uniqueness",
            validate_default=True,
        )
        schema_name: str = m.Field(
            default="",
            description="Schema name",
            validate_default=True,
        )
        tablespace: str = m.Field(
            default="",
            description="Tablespace name",
            validate_default=True,
        )
        parallel: t.PositiveInt = m.Field(
            default=1,
            description="Parallel degree for index creation",
            validate_default=True,
        )


__all__: list[str] = ["FlextDbOracleModelsSchema"]
