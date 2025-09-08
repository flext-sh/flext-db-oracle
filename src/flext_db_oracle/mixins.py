"""ELIMINADO - Usando flext-core diretamente.

TODAS as funcionalidades foram movidas para usar FlextMixins, FlextValidations
e FlextServices do flext-core, eliminando duplicação de código.

Use diretamente:
- FlextMixins para comportamentos
- FlextValidations.Advanced.CompositeValidator para validações
- FlextServices.ServiceProcessor para processamento

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

import re
from dataclasses import dataclass

from flext_core import FlextResult, FlextTypes, FlextValidations as Validations

from flext_db_oracle.constants import FlextDbOracleConstants


class OracleIdentifierValidation:
    """Oracle validation usando FlextValidations.Core.Predicates - ELIMINA 9 RETURNS."""

    @staticmethod
    def create_oracle_identifier_validator() -> Validations.Advanced.CompositeValidator:
        """Cria CompositeValidator usando FlextValidations.Core.Predicates - ELIMINA RETURNS."""
        # Usar Predicates do flext-core para eliminar múltiplos returns
        not_empty_pred = Validations.Core.Predicates(
            lambda x: bool(x and isinstance(x, str)),
            "not_empty",
        )

        length_pred = Validations.Core.Predicates(
            lambda x: len(str(x))
            <= FlextDbOracleConstants.OracleValidation.MAX_IDENTIFIER_LENGTH,
            "length_check",
        )

        pattern_pred = Validations.Core.Predicates(
            lambda x: bool(
                re.match(
                    FlextDbOracleConstants.OracleValidation.IDENTIFIER_PATTERN,
                    str(x),
                ),
            ),
            "pattern_check",
        )

        reserved_pred = Validations.Core.Predicates(
            lambda x: str(x).upper()
            not in FlextDbOracleConstants.OracleValidation.ORACLE_RESERVED,
            "reserved_words_check",
        )

        # Combinar predicates usando operações lógicas - ELIMINA COMPLEXIDADE
        combined_predicate = not_empty_pred & length_pred & pattern_pred & reserved_pred

        # Converter para validator function with proper typing
        def validator_func(identifier: object) -> FlextResult[object]:
            if not isinstance(identifier, str):
                return FlextResult[object].fail("Expected string identifier")
            result = combined_predicate(identifier)
            if result.success:
                return FlextResult[object].ok(identifier.upper())
            error_message = result.error or "Validation failed"
            return FlextResult[object].fail(error_message)

        return Validations.Advanced.CompositeValidator([validator_func])


# ELIMINADO - Usando FlextValidations.Advanced.CompositeValidator


# ELIMINADO - Usando FlextValidations.Advanced.CompositeValidator


class OracleValidationFactory:
    """Factory usando FlextValidations.Core.Predicates - ELIMINA MÚLTIPLOS RETURNS."""

    @staticmethod
    def create_identifier_validator(
        max_length: int,
        *,
        allow_empty: bool = False,
    ) -> Validations.Advanced.CompositeValidator:
        """Cria validador usando Predicates combinados - ELIMINA COMPLEXIDADE."""
        # Predicates base usando flext-core
        predicates = []

        if not allow_empty:
            predicates.append(
                Validations.Core.Predicates(
                    lambda x: bool(x and isinstance(x, str) and x.strip()),
                    "not_empty",
                ),
            )

        predicates.extend(
            [
                Validations.Core.Predicates(
                    lambda x: len(str(x)) <= max_length,
                    "length_check",
                ),
                # Reuse Oracle identifier validation
                Validations.Core.Predicates(
                    lambda x: str(x).upper()
                    not in FlextDbOracleConstants.OracleValidation.ORACLE_RESERVED,
                    "oracle_reserved_check",
                ),
            ],
        )

        # Combinar todos os predicates em um - ELIMINA MÚLTIPLOS VALIDATORS
        combined = predicates[0]
        for pred in predicates[1:]:
            combined &= pred

        def single_validator(value: object) -> FlextResult[object]:
            if not isinstance(value, str):
                return FlextResult[object].fail("Expected string value")
            result = combined(value)
            if result.success:
                return FlextResult[object].ok(value.strip().upper())
            error_message = result.error or "Validation failed"
            return FlextResult[object].fail(error_message)

        return Validations.Advanced.CompositeValidator([single_validator])

    @staticmethod
    def validate_oracle_identifier(
        value: str,
        max_length: int,
        *,
        allow_empty: bool = False,
    ) -> str:
        """Valida usando CompositeValidator - SINGLE RETURN."""
        if allow_empty and not value:
            return ""

        # Single return usando Railway-Oriented Programming
        validation_result = OracleValidationFactory.create_identifier_validator(
            max_length,
            allow_empty=allow_empty,
        ).validate(value)

        if validation_result.success:
            return str(validation_result.value)
        raise ValueError(validation_result.error or "Validation failed")


@dataclass
class ParameterObject:
    """Parameter Object usando dataclass - mais simples que implementação customizada."""

    params: FlextTypes.Core.Dict | None = None

    def __post_init__(self) -> None:
        """Initialize params dict if None."""
        if self.params is None:
            object.__setattr__(self, "params", {})

    def get(self, key: str, *, default: object = None) -> object:
        if self.params is None:
            return default
        return self.params.get(key, default)

    def require(self, key: str) -> object:
        if self.params is None or key not in self.params:
            msg = f"Required parameter '{key}' not provided"
            raise KeyError(msg)
        return self.params[key]

    def has(self, key: str) -> bool:
        return self.params is not None and key in self.params


@dataclass
class ConnectionParameters:
    """Connection parameters usando dataclass - elimina boilerplate."""

    host: str
    port: int
    service_name: str
    username: str
    password: str
    test_connection: bool | None = False


# SIMPLIFICADO - Usando lambda functions para transformação
class ErrorContextTransformer:
    """Simplificado - add context to error messages."""

    def __init__(self, context: str) -> None:
        self.context = context

    def transform[T](self, result: FlextResult[T]) -> FlextResult[T]:
        if result.success:
            return result
        return FlextResult[T].fail(f"{self.context}: {result.error}")


# ELIMINADO - Usar FlextMixins diretamente do flext-core
# FlextMixins já tem todas as funcionalidades de performance tracking


# EXPORTS REDUZIDOS - Apenas o essencial Oracle-específico
__all__ = [
    "ConnectionParameters",
    "ErrorContextTransformer",
    "OracleIdentifierValidation",
    "OracleValidationFactory",
    "ParameterObject",
]
