"""FlextDbOracle utilities module."""

from __future__ import annotations

from collections.abc import Callable, Iterable, Mapping
from enum import StrEnum
from functools import cache, wraps
from typing import Annotated, TypeIs, TypeVar, get_type_hints

from flext_core import r, u as u_core
from pydantic import BaseModel, BeforeValidator, ConfigDict, validate_call

T = TypeVar("T")


class FlextDbOracleUtilities(u_core):
    """TypeIs (PEP 742), BeforeValidator, validate_call, collections.abc, ParamSpec."""

    class Enum:
        """TypeIs genérico, parsing, coerção - ZERO TypeGuard manual."""

        @staticmethod
        def is_member[E: StrEnum](enum_cls: type[E], value: object) -> TypeIs[E]:
            """TypeIs narrowing em AMBAS branches if/else."""
            return isinstance(value, enum_cls) or (
                isinstance(value, str) and value in enum_cls._value2member_map_
            )

        @staticmethod
        def is_subset[E: StrEnum](
            enum_cls: type[E],
            valid: frozenset[E],
            value: object,
        ) -> TypeIs[E]:
            """Check if a value is a member of a valid subset of a StrEnum."""
            if isinstance(value, enum_cls):
                return value in valid
            if isinstance(value, str):
                try:
                    return enum_cls(value) in valid
                except ValueError:
                    return False
            return False

        @staticmethod
        def parse[E: StrEnum](enum_cls: type[E], value: str | E) -> r[E]:
            """Parse a string or enum value to the specified enum type."""
            if isinstance(value, enum_cls):
                return r.ok(value)
            try:
                return r.ok(enum_cls(value))
            except ValueError:
                return r.fail(f"Invalid {enum_cls.__name__}: '{value}'")

        @staticmethod
        def coerce_validator[E: StrEnum](enum_cls: type[E]) -> Callable[[str | E], E]:
            """BeforeValidator factory para Pydantic."""

            def _coerce(v: str | E) -> E:
                if isinstance(v, enum_cls):
                    return v
                if isinstance(v, str):
                    try:
                        return enum_cls(v)
                    except ValueError as exc:
                        msg = f"Invalid {enum_cls.__name__}: {v!r}"
                        raise TypeError(msg) from exc
                msg = f"Invalid {enum_cls.__name__}: {v!r}"
                raise TypeError(msg)

            return _coerce

        @staticmethod
        @cache
        def values[E: StrEnum](enum_cls: type[E]) -> frozenset[str]:
            """Get all string values from a StrEnum as a frozenset."""
            return frozenset(m.value for m in enum_cls)

    class Collection:
        """Parsing de Sequence/Mapping com StrEnums."""

        @staticmethod
        def parse_sequence[E: StrEnum](
            enum_cls: type[E],
            values: Iterable[str | E],
        ) -> r[tuple[E, ...]]:
            """Parse a sequence of values into enum instances.

            Args:
                enum_cls: The StrEnum class to parse values into.
                values: Iterable of string or enum values to parse.

            Returns:
                r containing tuple of parsed enums or error message.

            """
            parsed, errors = [], []
            for i, v in enumerate(values):
                if isinstance(v, enum_cls):
                    parsed.append(v)
                else:
                    try:
                        parsed.append(enum_cls(v))
                    except ValueError:
                        errors.append(f"[{i}]: '{v}'")
            return r.fail(f"Invalid: {errors}") if errors else r.ok(tuple(parsed))

        @staticmethod
        def coerce_list_validator[E: StrEnum](
            enum_cls: type[E],
        ) -> Callable[[list[str | E] | tuple[str | E, ...] | set[str | E]], list[E]]:
            """BeforeValidator factory for lists of enums."""

            def _coerce(
                value: list[str | E] | tuple[str | E, ...] | set[str | E],
            ) -> list[E]:
                if not isinstance(value, (list, tuple, set)):
                    msg = "Expected sequence"
                    raise TypeError(msg)
                result = []
                for i, item in enumerate(value):
                    if isinstance(item, enum_cls):
                        result.append(item)
                    elif isinstance(item, str):
                        try:
                            result.append(enum_cls(item))
                        except ValueError as exc:
                            msg = f"Invalid at [{i}]: {item!r}"
                            raise TypeError(msg) from exc
                    else:
                        msg = f"Expected str at [{i}]"
                        raise TypeError(msg)
                return result

            return _coerce

    class Args:
        """@validated, parse_kwargs - ZERO boilerplate de validação."""

        @staticmethod
        def validated[P, R](func: Callable[P, R]) -> Callable[P, R]:
            """Decorator com validate_call - aceita str OU enum, converte auto."""
            return validate_call(
                config=ConfigDict(arbitrary_types_allowed=True, use_enum_values=False),
                validate_return=False,
            )(func)

        @staticmethod
        def validated_with_result[P, R](
            func: Callable[P, r[R]],
        ) -> Callable[P, r[R]]:
            """ValidationError → r.fail()."""

            @wraps(func)
            def wrapper(*args: object, **kwargs: object) -> r[R]:
                try:
                    return validate_call(
                        config=ConfigDict(arbitrary_types_allowed=True),
                        validate_return=False,
                    )(func)(*args, **kwargs)
                except Exception as e:
                    return r.fail(str(e))

            return wrapper

        @staticmethod
        def parse_kwargs[E: StrEnum](
            kwargs: Mapping[str, object],
            enum_fields: Mapping[str, type[E]],
        ) -> r[dict[str, object]]:
            """Parse kwargs dictionary, converting string values to enums.

            Args:
                kwargs: Keyword arguments to parse.
                enum_fields: Mapping of field names to enum types.

            Returns:
                r containing parsed kwargs or error message.

            """
            parsed, errors = dict(kwargs), []
            for field, enum_cls in enum_fields.items():
                if field in parsed and isinstance(parsed[field], str):
                    try:
                        parsed[field] = enum_cls(parsed[field])
                    except ValueError:
                        errors.append(f"{field}: '{parsed[field]}'")
            return r.fail(f"Invalid: {errors}") if errors else r.ok(parsed)

        @staticmethod
        def get_enum_params(func: Callable[..., object]) -> dict[str, type[StrEnum]]:
            """Extract StrEnum parameters from function signature.

            Args:
                func: Function to extract enum parameters from.

            Returns:
                Dictionary mapping parameter names to StrEnum types.

            """
            try:
                hints = get_type_hints(func)
            except Exception:
                return {}
            return {
                n: h
                for n, h in hints.items()
                if n != "return" and isinstance(h, type) and issubclass(h, StrEnum)
            }

    class Model:
        """from_dict, merge_defaults, update - ZERO try/except."""

        @staticmethod
        def from_dict[M: BaseModel](
            model_cls: type[M],
            data: Mapping[str, object],
            *,
            strict: bool = False,
        ) -> r[M]:
            """Create a model instance from dictionary data.

            Args:
                model_cls: Pydantic model class to instantiate.
                data: Dictionary of data to validate and convert.
                strict: Whether to enforce strict validation.

            Returns:
                r containing validated model or error message.

            """
            try:
                return r.ok(model_cls.model_validate(data, strict=strict))
            except Exception as e:
                return r.fail(f"Validation failed: {e}")

        @staticmethod
        def merge_defaults[M: BaseModel](
            model_cls: type[M],
            defaults: Mapping[str, object],
            overrides: Mapping[str, object],
        ) -> r[M]:
            """Merge default and override dictionaries into a model instance.

            Args:
                model_cls: Pydantic model class to instantiate.
                defaults: Default values mapping.
                overrides: Override values mapping (takes precedence).

            Returns:
                r containing merged model or error message.

            """
            return FlextDbOracleUtilities.Model.from_dict(
                model_cls,
                {**defaults, **overrides},
            )

        @staticmethod
        def update[M: BaseModel](instance: M, **updates: object) -> r[M]:
            """Update a model instance with new values.

            Args:
                instance: Model instance to update.
                **updates: Field values to update.

            Returns:
                r containing updated model or error message.

            """
            try:
                current = instance.model_dump()
                current.update(updates)
                return r.ok(type(instance).model_validate(current))
            except Exception as e:
                return r.fail(f"Update failed: {e}")

    class Pydantic:
        """Factories for Annotated types."""

        @staticmethod
        def coerced_enum[E: StrEnum](
            enum_cls: type[E],
        ) -> type[Annotated[E, BeforeValidator]]:
            """Create an Annotated StrEnum type with automatic coercion.

            Args:
                enum_cls: The StrEnum class to create an annotated type for.

            Returns:
                An Annotated type that validates and coerces string values to the enum.

            """
            return Annotated[
                enum_cls,
                BeforeValidator(FlextDbOracleUtilities.Enum.coerce_validator(enum_cls)),
            ]


__all__ = [
    "FlextDbOracleUtilities",
]
