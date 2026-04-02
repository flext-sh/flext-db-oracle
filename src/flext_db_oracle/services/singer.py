"""Singer type mapping service mixin for flext-db-oracle.

Provides Singer schema to Oracle type conversion and mapping.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from collections.abc import Mapping, MutableMapping

from flext_core import r
from flext_db_oracle import FlextDbOracleModels, FlextDbOracleServiceBase, t


class FlextDbOracleServiceSinger(FlextDbOracleServiceBase):
    """Mixin providing Singer type mapping for FlextDbOracleServices.

    Handles: convert_singer_type, map_singer_schema.
    """

    def convert_singer_type(
        self,
        singer_type: str | t.StrSequence = "string",
        _format_hint: str | None = None,
    ) -> r[str]:
        """Convert Singer type to Oracle type - simplified."""
        singer_type = self._normalize_singer_type(singer_type)
        if _format_hint == "date-time":
            return r[str].ok("TIMESTAMP")
        type_map = {
            "string": "VARCHAR2(4000)",
            "integer": "NUMBER(38)",
            "number": "NUMBER",
            "boolean": "NUMBER(1)",
            "date-time": "TIMESTAMP",
        }
        oracle_type = type_map.get(singer_type, "VARCHAR2(255)")
        return r[str].ok(oracle_type)

    def map_singer_schema(
        self,
        singer_schema: FlextDbOracleModels.DbOracle.SingerSchema
        | t.ContainerValueMapping,
    ) -> r[FlextDbOracleModels.DbOracle.TypeMapping]:
        """Map Singer schema to Oracle types - simplified."""
        raw_properties: Mapping[str, t.ContainerValue] | None = None
        if isinstance(singer_schema, FlextDbOracleModels.DbOracle.SingerSchema):
            schema_model = singer_schema
        else:
            raw_props_value = singer_schema.get("properties", {})
            if not isinstance(raw_props_value, dict):
                return r[FlextDbOracleModels.DbOracle.TypeMapping].fail(
                    "Singer schema properties must be a mapping",
                )
            raw_properties = raw_props_value
            normalized_properties: MutableMapping[
                str,
                FlextDbOracleModels.DbOracle.SingerField,
            ] = {}
            for field_name, field_def in raw_properties.items():
                if isinstance(field_def, Mapping):
                    field_type = field_def.get("type", "string")
                    if isinstance(field_type, str):
                        normalized_properties[str(field_name)] = (
                            FlextDbOracleModels.DbOracle.SingerField(type=field_type)
                        )
                    else:
                        normalized_properties[str(field_name)] = (
                            FlextDbOracleModels.DbOracle.SingerField(type="string")
                        )
                else:
                    normalized_properties[str(field_name)] = (
                        FlextDbOracleModels.DbOracle.SingerField(type="string")
                    )
            schema_model = FlextDbOracleModels.DbOracle.SingerSchema.model_validate({
                "properties": normalized_properties,
            })
        mapping = t.ConfigMap(root={})
        for field_name, field_def in schema_model.properties.items():
            raw_field = (
                raw_properties.get(field_name)
                if isinstance(raw_properties, Mapping)
                else None
            )
            format_value = (
                raw_field.get("format") if isinstance(raw_field, Mapping) else None
            )
            format_hint = format_value if isinstance(format_value, str) else None
            conversion = self.convert_singer_type(field_def.type, format_hint)
            if conversion.is_success:
                mapping.root[field_name] = conversion.value
        normalized_mapping = {key: str(value) for key, value in mapping.root.items()}
        type_mapping = FlextDbOracleModels.DbOracle.TypeMapping.model_validate({
            "mapping": normalized_mapping,
        })
        return r[FlextDbOracleModels.DbOracle.TypeMapping].ok(type_mapping)


__all__ = ["FlextDbOracleServiceSinger"]
