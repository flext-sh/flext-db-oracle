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

from __future__ import annotations

import re
from dataclasses import dataclass

# IMPORTS REDUZIDOS - Usando flext-core diretamente
from flext_core import FlextResult
from flext_core.validations import FlextValidations as Validations

from flext_db_oracle.constants import FlextDbOracleConstants

# ELIMINADO - Usando FlextValidations.Advanced.CompositeValidator do flext-core


class OracleIdentifierValidation:
    """Oracle validation usando FlextValidations.Core.Predicates - ELIMINA 9 RETURNS."""

    # Oracle reserved words como constante classe
    ORACLE_RESERVED = frozenset(
        {
            "SELECT",
            "FROM",
            "WHERE",
            "INSERT",
            "UPDATE",
            "DELETE",
            "CREATE",
            "DROP",
            "ALTER",
            "TABLE",
            "INDEX",
            "VIEW",
            "PROCEDURE",
            "FUNCTION",
            "TRIGGER",
            "SEQUENCE",
            "PACKAGE",
            "CONSTRAINT",
            "PRIMARY",
            "FOREIGN",
            "KEY",
            "UNIQUE",
            "NOT",
            "NULL",
            "CHECK",
            "DEFAULT",
            "REFERENCES",
            "ON",
            "CASCADE",
            "RESTRICT",
            "SET",
            "COMMIT",
            "ROLLBACK",
            "SAVEPOINT",
        }
    )

    @staticmethod
    def create_oracle_identifier_validator() -> Validations.Advanced.CompositeValidator:
        """Cria CompositeValidator usando FlextValidations.Core.Predicates - ELIMINA RETURNS."""
        # Usar Predicates do flext-core para eliminar múltiplos returns
        not_empty_pred = Validations.Core.Predicates(
            lambda x: bool(x and isinstance(x, str)), "not_empty"
        )

        length_pred = Validations.Core.Predicates(
            lambda x: len(str(x))
            <= FlextDbOracleConstants.OracleValidation.MAX_IDENTIFIER_LENGTH,
            "length_check",
        )

        pattern_pred = Validations.Core.Predicates(
            lambda x: bool(
                re.match(
                    FlextDbOracleConstants.OracleValidation.IDENTIFIER_PATTERN, str(x)
                )
            ),
            "pattern_check",
        )

        reserved_pred = Validations.Core.Predicates(
            lambda x: str(x).upper() not in OracleIdentifierValidation.ORACLE_RESERVED,
            "reserved_words_check",
        )

        # Combinar predicates usando operações lógicas - ELIMINA COMPLEXIDADE
        combined_predicate = not_empty_pred & length_pred & pattern_pred & reserved_pred

        # Converter para validator function
        def validator_func(identifier: str) -> FlextResult[str]:
            result = combined_predicate(identifier)
            if result.success:
                return FlextResult[str].ok(identifier.upper())
            return FlextResult[str].fail(result.error)

        return Validations.Advanced.CompositeValidator([validator_func])


# ELIMINADO - Usando FlextValidations.Advanced.CompositeValidator


# ELIMINADO - Usando FlextValidations.Advanced.CompositeValidator


class OracleValidationFactory:
    """Factory usando FlextValidations.Core.Predicates - ELIMINA MÚLTIPLOS RETURNS."""

    @staticmethod
    def create_identifier_validator(
        max_length: int, *, allow_empty: bool = False
    ) -> Validations.Advanced.CompositeValidator:
        """Cria validador usando Predicates combinados - ELIMINA COMPLEXIDADE."""
        # Predicates base usando flext-core
        predicates = []

        if not allow_empty:
            predicates.append(
                Validations.Core.Predicates(
                    lambda x: bool(x and x.strip()), "not_empty"
                )
            )

        predicates.extend(
            [
                Validations.Core.Predicates(
                    lambda x: len(str(x)) <= max_length, "length_check"
                ),
                # Reuse Oracle identifier validation
                Validations.Core.Predicates(
                    lambda x: str(x).upper()
                    not in OracleIdentifierValidation.ORACLE_RESERVED,
                    "oracle_reserved_check",
                ),
            ]
        )

        # Combinar todos os predicates em um - ELIMINA MÚLTIPLOS VALIDATORS
        combined = predicates[0]
        for pred in predicates[1:]:
            combined &= pred

        def single_validator(value: str) -> FlextResult[str]:
            result = combined(value)
            return (
                FlextResult[str].ok(value.strip().upper())
                if result.success
                else FlextResult[str].fail(result.error)
            )

        return Validations.Advanced.CompositeValidator([single_validator])

    @staticmethod
    def validate_oracle_identifier(
        value: str, max_length: int, *, allow_empty: bool = False
    ) -> str:
        """Valida usando CompositeValidator - SINGLE RETURN."""
        if allow_empty and not value:
            return ""

        # Single return usando Railway-Oriented Programming
        return (
            OracleValidationFactory.create_identifier_validator(
                max_length, allow_empty=allow_empty
            )
            .validate(value)
            .unwrap_or_raise(ValueError)
        )  # flext-core unwrap_or_raise


@dataclass
class ParameterObject:
    """Parameter Object usando dataclass - mais simples que implementação customizada."""

    params: dict[str, object] = None

    def __post_init__(self) -> None:
        """Initialize params dict if None."""
        if self.params is None:
            self.params = {}

    def get(self, key: str, *, default: object = None) -> object:
        return self.params.get(key, default)

    def require(self, key: str) -> object:
        if key not in self.params:
            msg = f"Required parameter '{key}' not provided"
            raise KeyError(msg)
        return self.params[key]

    def has(self, key: str) -> bool:
        return key in self.params


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
