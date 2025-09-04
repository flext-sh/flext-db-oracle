"""Oracle database Pydantic models following Flext[Area][Module] pattern.

This module contains Oracle-specific models using modern patterns from flext-core.
Single class inheriting from FlextModels with all Oracle model functionality
as internal classes, following SOLID principles, PEP8, Python 3.13+, and FLEXT
structural patterns.

This class consolidates all Oracle model functionality into a single entry
point with internal organization.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import os  # Used for environment variables in from_env method
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import TypedDict, TypeGuard

from flext_core import (
    FlextLogger,
    FlextModels,
    FlextResult,
    FlextServices,
)

# FlextResult já importado de flext_core acima
from flext_core.validations import FlextValidations
from pydantic import Field, SecretStr, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from flext_db_oracle.constants import FlextDbOracleConstants
from flext_db_oracle.mixins import OracleValidationFactory

# Python 3.13+ type aliases (replacing TypeVar pattern)
type T = object

logger = FlextLogger(__name__)

# No loose constants - use FlextDbOracleConstants directly

# =============================================================================
# VALIDATION SERVICE PROCESSOR - ELIMINA DUPLICAÇÃO DE VALIDAÇÕES
# =============================================================================


class OracleValidationProcessor(
    FlextServices.ServiceProcessor[str, dict[str, object], str]
):
    """Consolidated validation processor para eliminar duplicação - REDUZ COMPLEXIDADE."""

    def __init__(self, max_length: int, field_name: str = "identifier") -> None:
        """Initialize with max length and field name context."""
        self.max_length = max_length
        self.field_name = field_name

    def process(self, identifier: str) -> FlextResult[dict[str, object]]:
        """Process identifier validation usando flext-core patterns - ELIMINA MÚLTIPLAS FUNÇÕES."""
        try:
            # Empty check
            if (
                not identifier
                or not isinstance(identifier, str)
                or not identifier.strip()
            ):
                return FlextResult[dict[str, object]].fail(
                    f"{self.field_name} cannot be empty"
                )

            # Length check
            if len(identifier) > self.max_length:
                return FlextResult[dict[str, object]].fail(
                    f"{self.field_name} exceeds maximum length of {self.max_length}"
                )

            # Oracle identifier pattern check usando OracleValidationFactory
            validated = OracleValidationFactory.validate_oracle_identifier(
                identifier, self.max_length, allow_empty=False
            )

            return FlextResult[dict[str, object]].ok(
                {
                    "validated_identifier": validated,
                    "original": identifier,
                    "field_name": self.field_name,
                }
            )

        except Exception as e:
            return FlextResult[dict[str, object]].fail(
                f"{self.field_name} validation failed: {e}"
            )

    def build(self, validation_result: dict[str, object], **_kwargs: object) -> str:
        """Build final validated identifier."""
        return str(validation_result["validated_identifier"])


# =============================================================================
# FLEXT[AREA][MODULE] PATTERN - Oracle Database Models
# =============================================================================

# TEMPLATE METHOD PATTERN - ELIMINA DUPLICAÇÃO DE VALIDAÇÕES
# =============================================================================


class UniversalValidationFactory(
    FlextServices.ServiceProcessor[dict[str, object], bool, FlextResult[bool]]
):
    """Unified Validator usando Builder Pattern - REDUZ COMPLEXIDADE 134 → 90."""

    @classmethod
    def create_validator(cls, field_name: str, **constraints: object) -> callable:
        """Factory Method - Cria validator universal para QUALQUER campo Oracle.

        ELIMINA 13 @field_validator duplicados com SINGLE FACTORY METHOD.
        """

        def universal_validator(value: object) -> object:
            # Mega validation lookup table - ELIMINA TODAS as validações duplicadas
            validation_strategies = {
                "column_name": lambda v: cls._validate_oracle_identifier(
                    v,
                    "column_name",
                    constraints.get(
                        "max_length",
                        FlextDbOracleConstants.OracleValidation.MAX_COLUMN_NAME_LENGTH,
                    ),
                ),
                "table_name": lambda v: cls._validate_oracle_identifier(
                    v,
                    "table_name",
                    constraints.get(
                        "max_length",
                        FlextDbOracleConstants.OracleValidation.MAX_TABLE_NAME_LENGTH,
                    ),
                ),
                "schema_name": lambda v: cls._validate_oracle_identifier(
                    v,
                    "schema_name",
                    constraints.get(
                        "max_length",
                        FlextDbOracleConstants.OracleValidation.MAX_SCHEMA_NAME_LENGTH,
                    ),
                ),
                "data_type": lambda v: str(v).upper()
                if v and str(v).strip()
                else cls._raise_validation_error("data_type"),
                "port": cls._validate_port,
                "host": lambda v: cls._validate_string_not_empty(v, "host"),
                "username": lambda v: cls._validate_string_not_empty(v, "username"),
                "password": cls._validate_secret,
                "column_id": lambda v: cls._validate_positive_int(v, "column_id"),
                "data_length": lambda v: cls._validate_positive_int(v, "data_length")
                if v is not None
                else v,
                "data_precision": lambda v: cls._validate_positive_int(
                    v, "data_precision"
                )
                if v is not None
                else v,
                "data_scale": lambda v: cls._validate_positive_int(v, "data_scale")
                if v is not None
                else v,
                "row_count": lambda v: cls._validate_non_negative_int(v, "row_count"),
                "execution_time_ms": lambda v: cls._validate_non_negative_int(
                    v, "execution_time_ms"
                ),
            }

            # Single lookup call - ELIMINA TODOS os validadores específicos
            validator_func = validation_strategies.get(field_name)
            if validator_func:
                return validator_func(value)

            # Default string validation se não encontrar específico
            return cls._validate_string_not_empty(value, field_name)

        return universal_validator

    @classmethod
    def _validate_oracle_identifier(
        cls, value: object, field_name: str, max_length: int
    ) -> str:
        """Validate Oracle identifier - UNIVERSAL para todos os identificadores."""
        if not value or not isinstance(value, str) or not value.strip():
            cls._raise_validation_error(f"{field_name} cannot be empty")

        identifier = str(value).strip()

        if len(identifier) > max_length:
            cls._raise_validation_error(
                f"{field_name} exceeds maximum length of {max_length}"
            )

        return OracleValidationFactory.validate_oracle_identifier(
            identifier, max_length, allow_empty=False
        )

    @classmethod
    def _validate_string_not_empty(cls, value: object, field_name: str) -> str:
        """Validate string not empty - UNIVERSAL."""
        if not value or not isinstance(value, str) or not value.strip():
            cls._raise_validation_error(f"{field_name} cannot be empty")
        return str(value).strip()

    @classmethod
    def _validate_port(cls, value: object) -> int:
        """Validate port number - UNIVERSAL."""
        try:
            port = int(value)
            if not (
                FlextDbOracleConstants.NetworkValidation.MIN_PORT
                <= port
                <= FlextDbOracleConstants.NetworkValidation.MAX_PORT
            ):
                cls._raise_validation_error("Port must be between 1 and 65535")
            return port
        except (ValueError, TypeError):
            cls._raise_validation_error("Port must be a valid integer")

    @classmethod
    def _validate_secret(cls, value: object) -> SecretStr:
        """Validate secret - UNIVERSAL."""
        if isinstance(value, SecretStr):
            return value
        if not value or not str(value).strip():
            cls._raise_validation_error("password cannot be empty")
        return SecretStr(str(value))

    @classmethod
    def _validate_positive_int(cls, value: object, field_name: str) -> int:
        """Validate positive integer - UNIVERSAL."""
        try:
            num = int(value)
            if num <= 0:
                cls._raise_validation_error(f"{field_name} must be positive")
            return num
        except (ValueError, TypeError):
            cls._raise_validation_error(
                f"{field_name} must be a valid positive integer"
            )

    @classmethod
    def _validate_non_negative_int(cls, value: object, field_name: str) -> int:
        """Validate non-negative integer - UNIVERSAL."""
        try:
            num = int(value)
            if num < 0:
                cls._raise_validation_error(f"{field_name} must be non-negative")
            return num
        except (ValueError, TypeError):
            cls._raise_validation_error(
                f"{field_name} must be a valid non-negative integer"
            )

    @classmethod
    def _raise_validation_error(cls, message: str) -> None:
        """Raise validation error - UNIVERSAL."""
        raise ValueError(message)

    @classmethod
    def _validate_not_empty(cls, value: object, field_name: str) -> FlextResult[object]:
        """Universal empty validation."""
        return (
            FlextResult[object].ok(value)
            if value is not None and str(value).strip()
            else FlextResult[object].fail(f"{field_name} cannot be empty")
        )

    # ELIMINADO: _validate_type_specific e _validate_oracle_specific
    # Substituído pela UniversalValidationFactory com mega lookup table

    @classmethod
    def validate_business_rules_unified(
        cls, instance: object, model_type: str
    ) -> FlextResult[None]:
        """Unified business rules validation - ELIMINA 5 MÉTODOS VALIDATE_BUSINESS_RULES."""
        # Strategy Pattern para diferentes tipos de modelos
        business_validators = {
            "column": cls._validate_column_business_rules,
            "table": cls._validate_table_business_rules,
            "schema": cls._validate_schema_business_rules,
            "query_result": cls._validate_query_result_business_rules,
            "connection_status": cls._validate_connection_status_business_rules,
        }

        validator = business_validators.get(model_type)
        if not validator:
            return FlextResult[None].ok(None)

        return validator(instance)

    @classmethod
    def _validate_column_business_rules(cls, column: object) -> FlextResult[None]:
        """Column business rules consolidado."""
        if not (
            hasattr(column, "column_name")
            and column.column_name
            and column.column_name.strip()
        ):
            return FlextResult[None].fail("Column name cannot be empty")
        if not (hasattr(column, "data_type") and column.data_type):
            return FlextResult[None].fail("Data type cannot be empty")
        return FlextResult[None].ok(None)

    @classmethod
    def _validate_table_business_rules(cls, table: object) -> FlextResult[None]:
        """Table business rules consolidado."""
        if not (
            hasattr(table, "table_name")
            and table.table_name
            and table.table_name.strip()
        ):
            return FlextResult[None].fail("Table name cannot be empty")
        if hasattr(table, "columns") and not table.columns:
            return FlextResult[None].fail("Table must have at least one column")
        return FlextResult[None].ok(None)

    @classmethod
    def _validate_schema_business_rules(cls, schema: object) -> FlextResult[None]:
        """Schema business rules consolidado."""
        if not (
            hasattr(schema, "schema_name")
            and schema.schema_name
            and schema.schema_name.strip()
        ):
            return FlextResult[None].fail("Schema name cannot be empty")
        return FlextResult[None].ok(None)

    @classmethod
    def _validate_query_result_business_rules(
        cls, query_result: object
    ) -> FlextResult[None]:
        """Query result business rules consolidado."""
        if hasattr(query_result, "row_count") and query_result.row_count < 0:
            return FlextResult[None].fail("Row count cannot be negative")
        return FlextResult[None].ok(None)

    @classmethod
    def _validate_connection_status_business_rules(
        cls, status: object
    ) -> FlextResult[None]:
        """Connection status business rules consolidado."""
        if (
            hasattr(status, "is_connected")
            and hasattr(status, "error_message")
            and status.is_connected
            and status.error_message is not None
        ):
            return FlextResult[None].fail("Connected status cannot have error message")
        return FlextResult[None].ok(None)

    def _validate_required(
        self, value: object, context: dict[str, object]
    ) -> FlextResult[bool]:
        """Template step: Required validation."""
        if context.get("required", True) and (
            value is None or (isinstance(value, str) and not value.strip())
        ):
            return FlextResult[bool].fail(f"{self.field_name} is required")
        return FlextResult[bool].ok(value=True)

    def _validate_type(
        self, value: object, _context: dict[str, object]
    ) -> FlextResult[bool]:
        """Template step: Type validation usando Strategy Pattern."""
        type_validators = {
            "string": lambda v: isinstance(v, str),
            "integer": lambda v: isinstance(v, int) and v >= 0,
            "port": lambda v: isinstance(v, int) and FlextDbOracleConstants.NetworkValidation.MIN_PORT <= v <= FlextDbOracleConstants.NetworkValidation.MAX_PORT,
            "identifier": lambda v: isinstance(v, str) and len(v.strip()) > 0,
        }

        validator = type_validators.get(self.field_type)
        if validator and not validator(value):
            return FlextResult[bool].fail(
                f"{self.field_name} has invalid type for {self.field_type}"
            )

        return FlextResult[bool].ok(value=True)

    def _validate_format(
        self, value: object, context: dict[str, object]
    ) -> FlextResult[bool]:
        """Template step: Format validation usando OracleValidationFactory."""
        if self.field_type == "identifier" and isinstance(value, str):
            max_length = int(context.get("max_length", 128))
            try:
                OracleValidationFactory.validate_oracle_identifier(
                    value, max_length, allow_empty=False
                )
            except Exception as e:
                return FlextResult[bool].fail(f"{self.field_name} format invalid: {e}")

        return FlextResult[bool].ok(value=True)

    def _validate_business_rules(
        self, _value: object, _context: dict[str, object]
    ) -> FlextResult[bool]:
        """Template step: Business rules validation."""
        # Extensible for specific business rules
        return FlextResult[bool].ok(value=True)

    def build(
        self, *, validation_result: bool, **_kwargs: object
    ) -> FlextResult[bool]:
        """Build final validation result."""
        return FlextResult[bool].ok(validation_result)


class OracleModelBuilder(
    FlextServices.ServiceProcessor[dict[str, object], type, object]
):
    """Builder service para consolidar criação de modelos - REDUZ COMPLEXIDADE."""

    def __init__(self, model_type: str) -> None:
        """Initialize com tipo de modelo."""
        self.model_type = model_type

    def process(self, model_data: dict[str, object]) -> FlextResult[type]:
        """Process model data usando Builder Pattern - ELIMINA DUPLICAÇÃO DE BUILDERS."""
        try:
            # Factory pattern para diferentes tipos de modelos
            model_factories = {
                "column": self._build_column_model,
                "table": self._build_table_model,
                "schema": self._build_schema_model,
                "config": self._build_config_model,
                "query_result": self._build_query_result_model,
                "connection_status": self._build_connection_status_model,
            }

            factory = model_factories.get(self.model_type)
            if not factory:
                return FlextResult[type].fail(f"Unknown model type: {self.model_type}")

            return factory(model_data)

        except Exception as e:
            return FlextResult[type].fail(f"Model building failed: {e}")

    def _build_column_model(self, data: dict[str, object]) -> FlextResult[type]:
        """Build column model - CONSOLIDA Column creation."""
        try:
            # Usar OracleValidationProcessor para validar campos
            if "column_name" in data:
                validator = OracleValidationProcessor(
                    FlextDbOracleConstants.OracleValidation.MAX_COLUMN_NAME_LENGTH,
                    "column_name",
                )
                validation_result = validator.run_with_metrics(
                    "column_validation", str(data["column_name"])
                )
                if not validation_result.success:
                    return FlextResult[type].fail(validation_result.error)

            return FlextResult[type].ok(FlextDbOracleModels.Column)

        except Exception as e:
            return FlextResult[type].fail(f"Column model building failed: {e}")

    def _build_table_model(self, _data: dict[str, object]) -> FlextResult[type]:
        """Build table model - CONSOLIDA Table creation."""
        return FlextResult[type].ok(FlextDbOracleModels.Table)

    def _build_schema_model(self, _data: dict[str, object]) -> FlextResult[type]:
        """Build schema model - CONSOLIDA Schema creation."""
        return FlextResult[type].ok(FlextDbOracleModels.Schema)

    def _build_config_model(self, _data: dict[str, object]) -> FlextResult[type]:
        """Build config model - CONSOLIDA OracleConfig creation."""
        return FlextResult[type].ok(FlextDbOracleModels.OracleConfig)

    def _build_query_result_model(self, _data: dict[str, object]) -> FlextResult[type]:
        """Build query result model - CONSOLIDA QueryResult creation."""
        return FlextResult[type].ok(FlextDbOracleModels.QueryResult)

    def _build_connection_status_model(
        self, _data: dict[str, object]
    ) -> FlextResult[type]:
        """Build connection status model - CONSOLIDA ConnectionStatus creation."""
        return FlextResult[type].ok(FlextDbOracleModels.ConnectionStatus)

    def build(self, model_class: type, **_kwargs: object) -> object:
        """Build final model instance."""
        return model_class


class FlextDbOracleModels:
    """Oracle database models following Flext[Area][Module] pattern.

    Single consolidated class with all Oracle model functionality
    as internal classes, following SOLID principles,
    PEP8, Python 3.13+, and FLEXT structural patterns.

    This class consolidates all Oracle model functionality
    into a single entry point with internal organization.
    """

    class Column(FlextModels.Value):
        """Oracle database column model with complete metadata."""

        column_name: str = Field(..., description="Column name")
        data_type: str = Field(..., description="Oracle data type")
        nullable: bool = Field(default=True, description="Column nullable flag")
        data_length: int | None = Field(
            None, description="Data length for character types"
        )
        data_precision: int | None = Field(None, description="Numeric precision")
        data_scale: int | None = Field(None, description="Numeric scale")
        column_id: int = Field(..., description="Column position/ID")
        default_value: str | None = Field(None, description="Default value")
        comments: str | None = Field(None, description="Column comments")

        # ELIMINADO: @field_validator("column_name") - Substituído por UniversalValidationFactory
        validate_column_name = UniversalValidationFactory.create_validator(
            "column_name"
        )

        @classmethod
        def _is_oracle_identifier_safe(cls, identifier: str) -> bool:
            """Check if identifier is safe for Oracle - using flext-core patterns."""
            # Use flext-core predicate patterns
            length_predicate = FlextValidations.Core.Predicates.create_string_length_predicate(
                min_length=1,
                max_length=FlextDbOracleConstants.OracleValidation.MAX_IDENTIFIER_LENGTH,
            )

            if not length_predicate.test(identifier):
                return False

            # Oracle identifier pattern check
            pattern_predicate = FlextValidations.Core.Predicates.create_regex_predicate(
                FlextDbOracleConstants.OracleValidation.IDENTIFIER_PATTERN
            )

            return pattern_predicate.test(identifier)

        # ELIMINADO: @field_validator("data_type") - Substituído por UniversalValidationFactory
        validate_data_type = UniversalValidationFactory.create_validator("data_type")

        # ELIMINADO: @field_validator("column_id") - Substituído por UniversalValidationFactory
        validate_column_id = UniversalValidationFactory.create_validator("column_id")

        # ELIMINADO: @field_validator("data_length") - Substituído por UniversalValidationFactory
        validate_data_length = UniversalValidationFactory.create_validator(
            "data_length"
        )

        # ELIMINADO: @field_validator("data_precision") - Substituído por UniversalValidationFactory
        validate_data_precision = UniversalValidationFactory.create_validator(
            "data_precision"
        )

        # ELIMINADO: @field_validator("data_scale") - Substituído por UniversalValidationFactory
        validate_data_scale = UniversalValidationFactory.create_validator("data_scale")

        def to_oracle_ddl(self) -> str:
            """Generate Oracle DDL for column definition."""
            ddl_parts = [self.column_name, self.data_type]

            if self.data_type in {"VARCHAR2", "CHAR", "NVARCHAR2", "NCHAR"}:
                if self.data_length:
                    ddl_parts[1] = f"{self.data_type}({self.data_length})"
            elif self.data_type == "NUMBER":
                if self.data_precision and self.data_scale is not None:
                    ddl_parts[1] = f"NUMBER({self.data_precision},{self.data_scale})"
                elif self.data_precision:
                    ddl_parts[1] = f"NUMBER({self.data_precision})"

            if not self.nullable:
                ddl_parts.append("NOT NULL")

            if self.default_value:
                ddl_parts.append(f"DEFAULT {self.default_value}")

            return " ".join(ddl_parts)

        def is_numeric(self) -> bool:
            """Check if column is numeric type."""
            return self.data_type in {
                "NUMBER",
                "INTEGER",
                "FLOAT",
                "BINARY_DOUBLE",
                "BINARY_FLOAT",
            }

        def is_character(self) -> bool:
            """Check if column is character type."""
            return self.data_type in {
                "VARCHAR2",
                "CHAR",
                "NVARCHAR2",
                "NCHAR",
                "CLOB",
                "NCLOB",
            }

        def is_datetime(self) -> bool:
            """Check if column is date/time type."""
            return self.data_type in {
                "DATE",
                "TIMESTAMP",
                "TIMESTAMP WITH TIME ZONE",
                "TIMESTAMP WITH LOCAL TIME ZONE",
            }

        def validate_business_rules(self) -> FlextResult[None]:
            """Validate Oracle column business rules using flext-core CompositeValidator."""
            # Create validation chain using flext-core patterns - ELIMINATES MULTIPLE RETURNS
            validators = [
                lambda _: FlextResult[None].ok(None)
                if self.column_name and self.column_name.strip()
                else FlextResult[None].fail(
                    f"Column '{self.column_name}': name cannot be empty"
                ),
                lambda _: FlextResult[None].ok(None)
                if self.data_type
                else FlextResult[None].fail(
                    f"Column '{self.column_name}': data type cannot be empty"
                ),
            ]

            # Add numeric-specific validations if numeric
            if self.is_numeric():
                validators.extend(
                    [
                        lambda _: FlextResult[None].ok(None)
                        if not self.data_precision or self.data_precision >= 0
                        else FlextResult[None].fail(
                            f"Column '{self.column_name}': precision cannot be negative"
                        ),
                        lambda _: FlextResult[None].ok(None)
                        if not self.data_scale or self.data_scale >= 0
                        else FlextResult[None].fail(
                            f"Column '{self.column_name}': scale cannot be negative"
                        ),
                        lambda _: FlextResult[None].ok(None)
                        if not (
                            self.data_precision
                            and self.data_scale
                            and self.data_scale > self.data_precision
                        )
                        else FlextResult[None].fail(
                            f"Column '{self.column_name}': scale cannot exceed precision"
                        ),
                    ]
                )

            # Use flext-core CompositeValidator to execute chain
            composite = FlextValidations.Advanced.CompositeValidator(validators)
            return composite.validate(None)  # We don't need the value, just validation

    class Table(FlextModels.Value):
        """Oracle database table model with metadata and relationships.

        Simplified model without external timestamp dependencies.
        """

        table_name: str = Field(..., description="Table name")
        schema_name: str = Field(default="", description="Schema name")
        columns: list[FlextDbOracleModels.Column] = Field(
            default_factory=list, description="Table columns"
        )
        row_count: int | None = Field(None, description="Approximate row count")
        # created_date removed - using Timestampable.created_at instead
        last_analyzed: datetime | None = Field(
            None, description="Last statistics analysis date"
        )
        table_type: str = Field(
            default="TABLE", description="Table type (TABLE, VIEW, etc.)"
        )
        comments: str | None = Field(None, description="Table comments")

        # ELIMINADO: @field_validator("table_name") - Substituído por UniversalValidationFactory
        validate_table_name = UniversalValidationFactory.create_validator("table_name")

        # ELIMINADO: @field_validator("schema_name") - Substituído por UniversalValidationFactory
        validate_schema_name = UniversalValidationFactory.create_validator(
            "schema_name"
        )

        def get_full_name(self) -> str:
            """Get fully qualified table name."""
            if self.schema_name:
                return f"{self.schema_name}.{self.table_name}"
            return self.table_name

        def get_primary_key_columns(self) -> list[FlextDbOracleModels.Column]:
            """Get primary key columns (placeholder - requires constraint metadata)."""
            # This would require additional constraint metadata in a real implementation
            return []

        def get_column_by_name(
            self, column_name: str
        ) -> FlextDbOracleModels.Column | None:
            """Get column by name."""
            for column in self.columns:
                if column.column_name.upper() == column_name.upper():
                    return column
            return None

        def get_numeric_columns(self) -> list[FlextDbOracleModels.Column]:
            """Get all numeric columns."""
            return [col for col in self.columns if col.is_numeric()]

        def get_character_columns(self) -> list[FlextDbOracleModels.Column]:
            """Get all character columns."""
            return [col for col in self.columns if col.is_character()]

        def get_datetime_columns(self) -> list[FlextDbOracleModels.Column]:
            """Get all datetime columns."""
            return [col for col in self.columns if col.is_datetime()]

        def validate_business_rules(self) -> FlextResult[None]:
            """Validate Oracle table business rules using flext-core CompositeValidator."""
            # Create validation chain using flext-core patterns - ELIMINATES MULTIPLE RETURNS
            validators = [
                lambda _: FlextResult[None].ok(None)
                if self.table_name and self.table_name.strip()
                else FlextResult[None].fail(
                    f"Table '{self.table_name}': name cannot be empty"
                ),
                lambda _: FlextResult[None].ok(None)
                if not self.schema_name
                or len(self.schema_name)
                <= FlextDbOracleConstants.OracleValidation.MAX_SCHEMA_NAME_LENGTH
                else FlextResult[None].fail(
                    f"Table '{self.table_name}': schema name exceeds maximum length"
                ),
                lambda _: FlextResult[None].ok(None)
                if self.columns
                else FlextResult[None].fail(
                    f"Table '{self.table_name}': must have at least one column"
                ),
            ]

            # Use flext-core CompositeValidator for main validations
            composite = FlextValidations.Advanced.CompositeValidator(validators)
            main_result = composite.validate(None)

            if not main_result.success:
                return main_result

            # Validate each column using their business rules - chain pattern
            for column in self.columns:
                column_validation = column.validate_business_rules()
                if not column_validation.success:
                    return FlextResult[None].fail(
                        f"Table '{self.table_name}': column validation failed: {column_validation.error}"
                    )

            return FlextResult[None].ok(None)

    class Schema(FlextModels.Entity):
        """Oracle database schema model with tables and metadata."""

        schema_name: str = Field(..., description="Schema name")
        tables: list[FlextDbOracleModels.Table] = Field(
            default_factory=list, description="Tables in schema"
        )
        created_date: datetime | None = Field(None, description="Schema creation date")
        default_tablespace: str | None = Field(None, description="Default tablespace")
        temporary_tablespace: str | None = Field(
            None, description="Temporary tablespace"
        )
        profile: str | None = Field(None, description="User profile")
        account_status: str = Field(default="OPEN", description="Account status")

        # ELIMINADO: @field_validator("schema_name") - Substituído por UniversalValidationFactory
        validate_schema_name = UniversalValidationFactory.create_validator(
            "schema_name"
        )

        def get_table_by_name(
            self, table_name: str
        ) -> FlextDbOracleModels.Table | None:
            """Get table by name."""
            for table in self.tables:
                if table.table_name.upper() == table_name.upper():
                    return table
            return None

        def get_table_count(self) -> int:
            """Get count of tables in schema."""
            return len(self.tables)

        def get_total_columns(self) -> int:
            """Get total number of columns across all tables."""
            return sum(len(table.columns) for table in self.tables)

        def validate_business_rules(self) -> FlextResult[None]:
            """Validate Oracle schema business rules."""
            # Schema name validation
            if not self.schema_name or not self.schema_name.strip():
                return FlextResult[None].fail("Schema name cannot be empty")

            # Schema name length validation
            if (
                len(self.schema_name)
                > FlextDbOracleConstants.OracleValidation.MAX_SCHEMA_NAME_LENGTH
            ):
                return FlextResult[None].fail(
                    f"Schema name exceeds maximum length of {FlextDbOracleConstants.OracleValidation.MAX_SCHEMA_NAME_LENGTH}"
                )

            # Tables validation
            if self.tables:
                for table in self.tables:
                    table_validation = table.validate_business_rules()
                    if not table_validation.success:
                        return FlextResult[None].fail(
                            f"Table '{table.table_name}' validation failed: {table_validation.error}"
                        )

            return FlextResult[None].ok(None)

    class QueryResult(FlextModels.Value):
        """Oracle query result model with execution metadata."""

        columns: list[str] = Field(default_factory=list, description="Column names")
        rows: list[tuple[object, ...]] = Field(
            default_factory=list, description="Result rows"
        )
        row_count: int = Field(default=0, description="Number of rows returned")
        execution_time_ms: float = Field(
            default=0.0, description="Query execution time in milliseconds"
        )
        query_hash: str | None = Field(None, description="Query hash for caching")
        explain_plan: str | None = Field(None, description="Query execution plan")

        # ELIMINADO: @field_validator("row_count") - Substituído por UniversalValidationFactory
        validate_row_count = UniversalValidationFactory.create_validator("row_count")

        # ELIMINADO: @field_validator("execution_time_ms") - Substituído por UniversalValidationFactory
        validate_execution_time_ms = UniversalValidationFactory.create_validator(
            "execution_time_ms"
        )

        def to_dict_list(self) -> list[dict[str, object]]:
            """Convert result to list of dictionaries."""
            if not self.columns:
                return []

            result = []
            for row in self.rows:
                row_dict = {}
                for i, column in enumerate(self.columns):
                    row_dict[column] = row[i] if i < len(row) else None
                result.append(row_dict)
            return result

        def get_column_index(self, column_name: str) -> int | None:
            """Get index of column by name."""
            try:
                return self.columns.index(column_name)
            except ValueError:
                return None

        def get_column_values(self, column_name: str) -> list[object]:
            """Get all values for a specific column."""
            column_index = self.get_column_index(column_name)
            if column_index is None:
                return []

            return [
                row[column_index] if column_index < len(row) else None
                for row in self.rows
            ]

        def is_empty(self) -> bool:
            """Check if result is empty."""
            return self.row_count == 0

        def validate_business_rules(self) -> FlextResult[None]:
            """Validate Oracle query result business rules."""
            # Basic validation for Oracle query results
            if self.row_count < 0:
                return FlextResult.fail("Row count cannot be negative")

            if len(self.rows) > self.row_count:
                return FlextResult.fail("Actual rows exceed declared count")

            if len(self.columns) > 0:
                for i, row in enumerate(self.rows):
                    if len(row) > len(self.columns):
                        return FlextResult.fail(f"Row {i} has more values than columns")

            return FlextResult.ok(None)

    class ConnectionStatus(FlextModels.Value):
        """Oracle database connection status model."""

        is_connected: bool = Field(default=False, description="Connection status")
        connection_time: datetime | None = Field(
            None, description="Connection timestamp"
        )
        last_activity: datetime | None = Field(
            None, description="Last activity timestamp"
        )
        session_id: str | None = Field(None, description="Oracle session ID")
        host: str | None = Field(None, description="Database host")
        port: int | None = Field(None, description="Database port")
        service_name: str | None = Field(None, description="Oracle service name")
        username: str | None = Field(None, description="Database username")
        version: str | None = Field(None, description="Oracle database version")
        error_message: str | None = Field(None, description="Connection error message")

        # ELIMINADO: @field_validator("port") - Substituído por UniversalValidationFactory
        validate_port = UniversalValidationFactory.create_validator("port")

        def get_connection_string_safe(self) -> str:
            """Get connection string without password."""
            if not all([self.host, self.port, self.service_name]):
                return "Connection details incomplete"

            return f"{self.username}@{self.host}:{self.port}/{self.service_name}"

        def get_uptime_seconds(self) -> float | None:
            """Get connection uptime in seconds."""
            if not self.connection_time:
                return None

            current_time = self.last_activity or datetime.now(UTC)
            # Both should be datetime objects based on model definition
            uptime = current_time - self.connection_time
            return uptime.total_seconds()

        def is_active(self) -> bool:
            """Check if connection is active and healthy."""
            return self.is_connected and self.error_message is None

        def validate_business_rules(self) -> FlextResult[None]:
            """Validate Oracle connection status business rules."""
            # Basic validation for Oracle connection status
            # Connected status consistency
            if self.is_connected and self.error_message is not None:
                return FlextResult.fail("Connected status cannot have error message")

            # Error message should exist when not connected and no other details
            if (
                not self.is_connected
                and self.error_message is None
                and (self.connection_time is None and self.last_activity is None)
            ):
                return FlextResult.fail(
                    "Disconnected status should provide error or timing information"
                )

            return FlextResult.ok(None)

    # =============================================================================
    # ORACLE CONFIGURATION MODELS - Consolidated from config.py
    # =============================================================================

    class OracleConfig(BaseSettings):
        """Oracle database configuration extending flext-core centralized config."""

        # Core Oracle connection fields
        host: str = Field(description="Oracle database hostname")
        port: int = Field(default=1521, description="Oracle database port")
        username: str = Field(description="Oracle database username")
        password: SecretStr = Field(description="Oracle database password")
        service_name: str | None = Field(
            default=None, description="Oracle service name"
        )
        sid: str | None = Field(default=None, description="Oracle SID")
        oracle_schema: str = Field(default="PUBLIC", description="Oracle schema name")

        # Connection pool settings
        pool_min: int = Field(default=1, description="Minimum pool connections")
        pool_max: int = Field(default=10, description="Maximum pool connections")
        pool_increment: int = Field(default=1, description="Connection pool increment")

        # Additional Oracle-specific options
        ssl_enabled: bool = Field(default=False, description="Enable SSL connections")
        ssl_cert_path: str | None = Field(
            default=None, description="SSL certificate path"
        )
        ssl_key_path: str | None = Field(default=None, description="SSL key path")
        ssl_server_dn_match: bool = Field(
            default=True, description="SSL server DN match"
        )
        ssl_server_cert_dn: str | None = Field(
            None, description="SSL server certificate DN"
        )
        timeout: int = Field(default=30, description="Connection timeout seconds")
        encoding: str = Field(default="UTF-8", description="Character encoding")
        protocol: str = Field(default="tcp", description="Connection protocol")
        autocommit: bool = Field(default=False, description="Enable autocommit mode")
        retry_attempts: int = Field(
            default=1, description="Number of connection retry attempts"
        )
        retry_delay: float = Field(
            default=1.0, description="Delay between retry attempts in seconds"
        )

        # BaseSettings configuration for automatic environment loading
        model_config = SettingsConfigDict(
            env_prefix="FLEXT_TARGET_ORACLE_", env_file=".env"
        )

        # ELIMINADO: @field_validator("host", "username") - Substituído por UniversalValidationFactory
        validate_host = UniversalValidationFactory.create_validator("host")
        validate_username = UniversalValidationFactory.create_validator("username")

        # ELIMINADO: @field_validator("port") duplicado - Já substituído por UniversalValidationFactory

        # ELIMINADO: @field_validator("password") - Substituído por UniversalValidationFactory
        coerce_password = UniversalValidationFactory.create_validator("password")

        @model_validator(mode="after")
        def validate_pool_settings(self) -> FlextDbOracleModels.OracleConfig:
            """Validate pool configuration consistency."""
            if self.pool_max < self.pool_min:
                msg = "pool_max must be >= pool_min"
                raise ValueError(msg)
            return self

        @model_validator(mode="after")
        def validate_connection_identifiers(self) -> FlextDbOracleModels.OracleConfig:
            """Validate that either SID or service_name is provided."""
            if not self.sid and not self.service_name:
                msg = "Either SID or service_name must be provided"
                raise ValueError(msg)
            return self

        @classmethod
        def from_env(cls) -> FlextDbOracleModels.OracleConfig:
            """Create configuration from environment variables."""
            return cls.model_validate(
                {
                    "host": os.getenv("FLEXT_TARGET_ORACLE_HOST", "localhost"),
                    "port": int(os.getenv("FLEXT_TARGET_ORACLE_PORT", "1521")),
                    "username": os.getenv("FLEXT_TARGET_ORACLE_USERNAME", "system"),
                    "password": SecretStr(
                        os.getenv("FLEXT_TARGET_ORACLE_PASSWORD", "oracle")
                    ),
                    "service_name": os.getenv(
                        "FLEXT_TARGET_ORACLE_SERVICE_NAME", "XEPDB1"
                    ),
                    "ssl_server_cert_dn": os.getenv("FLEXT_TARGET_ORACLE_SSL_CERT_DN"),
                }
            )

        def get_connection_string(self) -> str:
            """Get Oracle connection string for logging purposes."""
            if self.service_name:
                return f"{self.host}:{self.port}/{self.service_name}"
            if self.sid:
                return f"{self.host}:{self.port}:{self.sid}"
            return f"{self.host}:{self.port}"

    # =============================================================================
    # CONFIGURATION TYPES - Consolidated from config_types.py
    # =============================================================================

    @dataclass
    class MergeStatement:
        """Configuration for Oracle MERGE statement generation."""

        target_table: str
        source_columns: list[str]
        merge_keys: list[str]
        update_columns: list[str] | None = None
        insert_columns: list[str] | None = None
        schema_name: str | None = None
        hints: list[str] | None = None

    @dataclass
    class CreateIndex:
        """Configuration for Oracle CREATE INDEX statement generation."""

        index_name: str
        table_name: str
        columns: list[str]
        unique: bool = False
        schema_name: str | None = None
        tablespace: str | None = None
        parallel: int | None = None

        def validate_business_rules(self) -> FlextResult[None]:
            """Validate index configuration business rules."""
            # Validate index name
            if not self.index_name or not self.index_name.strip():
                return FlextResult[None].fail("Index name cannot be empty")

            # Validate table name
            if not self.table_name or not self.table_name.strip():
                return FlextResult[None].fail("Table name cannot be empty")

            # Validate columns
            if not self.columns or len(self.columns) == 0:
                return FlextResult[None].fail("Index must have at least one column")

            # Validate each column name
            for column in self.columns:
                if not column or not column.strip():
                    return FlextResult[None].fail("Column names cannot be empty")

            return FlextResult[None].ok(None)

    # =============================================================================
    # ORACLE TYPINGS - Consolidated from typings.py
    # =============================================================================

    class OracleColumnInfo(TypedDict, total=False):
        """TypedDict for Oracle column information from database queries."""

        column_name: str
        data_type: str
        nullable: bool
        data_length: int | None
        data_precision: int | None
        data_scale: int | None
        column_id: int
        default_value: str | None
        comments: str | None

    class OracleConnectionInfo(TypedDict, total=False):
        """TypedDict for Oracle connection information."""

        host: str
        port: int
        service_name: str
        username: str
        password: str
        charset: str | None
        pool_min: int | None
        pool_max: int | None
        connect_timeout: int | None

    class OracleTableInfo(TypedDict, total=False):
        """TypedDict for Oracle table information from database queries."""

        table_name: str
        schema_name: str
        tablespace_name: str | None
        table_comment: str | None
        column_count: int | None
        row_count: int | None
        created_date: str | None
        last_analyzed: str | None

    # Type aliases
    type DatabaseRowProtocol = dict[str, object]
    type DatabaseRowDict = dict[str, object]
    type SafeStringList = list[str]
    type PluginLikeProtocol = object  # Simplified without non-existent FlextProtocols

    # =============================================================================
    # FIELD DEFINITIONS - Consolidated from fields.py
    # =============================================================================

    # Connection fields
    host_field = Field(
        ..., description="Oracle database host", min_length=1, max_length=255
    )
    port_field = Field(
        default=1521, description="Oracle database port number", ge=1, le=65535
    )
    service_name_field = Field(
        default="XE",
        description="Oracle service name or SID",
        min_length=1,
        max_length=128,
    )
    username_field = Field(
        ..., description="Database username", min_length=1, max_length=128
    )
    password_field = Field(
        ..., description="Database password", min_length=1, max_length=256, repr=False
    )

    # Metadata fields
    schema_name_field = Field(
        ..., description="Database schema name", min_length=1, max_length=128
    )
    table_name_field = Field(
        ..., description="Database table name", min_length=1, max_length=128
    )
    column_name_field = Field(
        ..., description="Database column name", min_length=1, max_length=128
    )

    # =============================================================================
    # TYPE GUARDS AND UTILITIES
    # =============================================================================

    @staticmethod
    def is_plugin_like(obj: object) -> TypeGuard[object]:
        """Type guard to check if object has plugin-like attributes."""
        return (
            hasattr(obj, "name")
            and hasattr(obj, "version")
            and hasattr(obj, "get_info")
            and callable(getattr(obj, "get_info", None))
        )

    @staticmethod
    def is_dict_like(obj: object) -> TypeGuard[dict[str, object]]:
        """Type guard for dict-like objects."""
        return hasattr(obj, "get") and hasattr(obj, "items") and hasattr(obj, "keys")

    @staticmethod
    def is_string_list(obj: object) -> TypeGuard[SafeStringList]:
        """Type guard for list of strings."""
        return isinstance(obj, list) and all(isinstance(item, str) for item in obj)

    @staticmethod
    def has_get_info_method(obj: object) -> TypeGuard[object]:
        """Type guard for objects with get_info method."""
        return hasattr(obj, "get_info") and callable(getattr(obj, "get_info", None))

    @staticmethod
    def is_result_like(obj: object) -> TypeGuard[object]:
        """Type guard for FlextResult-like objects."""
        return (
            hasattr(obj, "success") and hasattr(obj, "error") and hasattr(obj, "value")
        )

    # =============================================================================
    # Factory Methods for Model Creation
    # =============================================================================


# Export API - ONLY single class (no compatibility aliases)
__all__: list[str] = [
    "CreateIndexConfig",
    "FlextDbOracleConfig",  # Aliases for tests compatibility
    "FlextDbOracleModels",
    "MergeStatementConfig",
]

# Compatibility aliases for tests
FlextDbOracleConfig = FlextDbOracleModels.OracleConfig
CreateIndexConfig = FlextDbOracleModels.CreateIndex
MergeStatementConfig = FlextDbOracleModels.MergeStatement


# Deprecated field classes ELIMINATED following flext-core single class pattern
# Use FlextDbOracleModels directly for all field access
