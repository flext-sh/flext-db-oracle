"""FlextDbOracle utilities module."""

from __future__ import annotations

from collections.abc import Callable, Iterable, Mapping
from enum import StrEnum
from functools import cache, wraps
from typing import Annotated, Any, TypeIs, TypeVar, get_type_hints

from flext_core import FlextResult, FlextUtilities
from pydantic import BaseModel, BeforeValidator, ConfigDict

T = TypeVar("T")


class FlextDbOracleUtilities(FlextUtilities):
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
            enum_cls: type[E], valid: frozenset[E], value: object
        ) -> TypeIs[E]:
            if isinstance(value, enum_cls):
                return value in valid
            if isinstance(value, str):
                try:
                    return enum_cls(value) in valid
                except ValueError:
                    return False
            return False

        @staticmethod
        def parse[E: StrEnum](enum_cls: type[E], value: str | E) -> FlextResult[E]:
            if isinstance(value, enum_cls):
                return FlextResult.ok(value)
            try:
                return FlextResult.ok(enum_cls(value))
            except ValueError:
                return FlextResult.fail(f"Invalid {enum_cls.__name__}: '{value}'")

        @staticmethod
        def coerce_validator[E: StrEnum](enum_cls: type[E]) -> Callable[[Any], E]:
            """BeforeValidator factory para Pydantic."""

            def _coerce(v: Any) -> E:
                if isinstance(v, enum_cls):
                    return v
                if isinstance(v, str):
                    try:
                        return enum_cls(v)
                    except ValueError:
                        pass
                msg = f"Invalid {enum_cls.__name__}: {v!r}"
                raise ValueError(msg)

            return _coerce

        @staticmethod
        @cache
        def values[E: StrEnum](enum_cls: type[E]) -> frozenset[str]:
            return frozenset(m.value for m in enum_cls)

    class Collection:
        """Parsing de Sequence/Mapping com StrEnums."""

        @staticmethod
        def parse_sequence[E: StrEnum](
            enum_cls: type[E], values: Iterable[str | E]
        ) -> FlextResult[tuple[E, ...]]:
            parsed, errors = [], []
            for i, v in enumerate(values):
                if isinstance(v, enum_cls):
                    parsed.append(v)
                else:
                    try:
                        parsed.append(enum_cls(v))
                    except ValueError:
                        errors.append(f"[{i}]: '{v}'")
            return (
                FlextResult.fail(f"Invalid: {errors}")
                if errors
                else FlextResult.ok(tuple(parsed))
            )

        @staticmethod
        def coerce_list_validator[E: StrEnum](
            enum_cls: type[E],
        ) -> Callable[[Any], list[E]]:
            def _coerce(value: Any) -> list[E]:
                if not isinstance(value, (list, tuple, set)):
                    msg = "Expected sequence"
                    raise ValueError(msg)
                result = []
                for i, item in enumerate(value):
                    if isinstance(item, enum_cls):
                        result.append(item)
                    elif isinstance(item, str):
                        try:
                            result.append(enum_cls(item))
                        except ValueError:
                            msg = f"Invalid at [{i}]: {item!r}"
                            raise ValueError(msg)
                    else:
                        msg = f"Expected str at [{i}]"
                        raise ValueError(msg)
                return result

            return _coerce

    class Args:
        """@validated, parse_kwargs - ZERO boilerplate de validação."""

        @staticmethod
        def validated[P, R](func: Callable[P, R]) -> Callable[P, R]:
            """Decorator com validate_call - aceita str OU enum, converte auto."""
            from pydantic import validate_call

            return validate_call(
                config=ConfigDict(arbitrary_types_allowed=True, use_enum_values=False),
                validate_return=False,
            )(func)

        @staticmethod
        def validated_with_result[P, R](
            func: Callable[P, FlextResult[R]],
        ) -> Callable[P, FlextResult[R]]:
            """ValidationError → FlextResult.fail()."""
            from pydantic import validate_call

            @wraps(func)
            def wrapper(*args: Any, **kwargs: Any) -> FlextResult[R]:
                try:
                    return validate_call(
                        config=ConfigDict(arbitrary_types_allowed=True),
                        validate_return=False,
                    )(func)(*args, **kwargs)
                except Exception as e:
                    return FlextResult.fail(str(e))

            return wrapper

        @staticmethod
        def parse_kwargs[E: StrEnum](
            kwargs: Mapping[str, Any], enum_fields: Mapping[str, type[E]]
        ) -> FlextResult[dict[str, Any]]:
            parsed, errors = dict(kwargs), []
            for field, enum_cls in enum_fields.items():
                if field in parsed and isinstance(parsed[field], str):
                    try:
                        parsed[field] = enum_cls(parsed[field])
                    except ValueError:
                        errors.append(f"{field}: '{parsed[field]}'")
            return (
                FlextResult.fail(f"Invalid: {errors}")
                if errors
                else FlextResult.ok(parsed)
            )

        @staticmethod
        def get_enum_params(func: Callable[..., Any]) -> dict[str, type[StrEnum]]:
            """Extrai parâmetros StrEnum da signature."""
            try:
                hints = get_type_hints(func)
            except:
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
            model_cls: type[M], data: Mapping[str, Any], *, strict: bool = False
        ) -> FlextResult[M]:
            try:
                return FlextResult.ok(model_cls.model_validate(data, strict=strict))
            except Exception as e:
                return FlextResult.fail(f"Validation failed: {e}")

        @staticmethod
        def merge_defaults[M: BaseModel](
            model_cls: type[M],
            defaults: Mapping[str, Any],
            overrides: Mapping[str, Any],
        ) -> FlextResult[M]:
            return FlextDbOracleUtilities.Model.from_dict(
                model_cls, {**defaults, **overrides}
            )

        @staticmethod
        def update[M: BaseModel](instance: M, **updates: Any) -> FlextResult[M]:
            try:
                current = instance.model_dump()
                current.update(updates)
                return FlextResult.ok(type(instance).model_validate(current))
            except Exception as e:
                return FlextResult.fail(f"Update failed: {e}")

    class Pydantic:
        """Fábricas de Annotated types."""

        @staticmethod
        def coerced_enum[E: StrEnum](enum_cls: type[E]) -> type:
            return Annotated[
                enum_cls,
                BeforeValidator(FlextDbOracleUtilities.Enum.coerce_validator(enum_cls)),
            ]


__all__ = [
    "FlextDbOracleUtilities",
]
