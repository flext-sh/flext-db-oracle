"""FlextDbOracle utilities module."""

from __future__ import annotations

import contextlib
import hashlib
import os
from collections.abc import Mapping
from enum import StrEnum
from typing import Annotated

from flext_core import FlextUtilities, r
from pydantic import BeforeValidator, RootModel, TypeAdapter, ValidationError
from sqlalchemy import (
    Connection as SAConnection,
    Engine as SAEngine,
    TextClause,
    create_engine,
    text,
)
from sqlalchemy.engine import CursorResult

from flext_db_oracle import c, t
from flext_db_oracle.settings import FlextDbOracleSettings


class FlextDbOracleUtilities(FlextUtilities):
    """FlextDbOracle utilities extending FlextUtilities with Oracle-specific helpers.

    Architecture: Advanced utilities with ZERO code bloat through:
    - TypeIs/TypeGuard for narrowing (PEP 742)
    - BeforeValidator factories for Pydantic coercion
    - @validated decorators eliminating manual validation
    - Generic parsing utilities for StrEnums (inherited from parent)
    """

    class DbOracle:
        """Oracle-specific utility namespace.

        This namespace groups all Oracle-specific utilities for better organization
        and cross-project access. Access via u.Oracle.* pattern.

        Example:
            from flext_db_oracle.utilities import u
            result = u.Oracle.Collection.parse_sequence(Status, ["active", "pending"])
            parsed = u.Oracle.Args.parse_kwargs(kwargs, enum_fields)

        """

        class _StrictIntValue(RootModel[int]):
            """Strict integer parser via Pydantic validation."""

            root: int

        class _CountValue(RootModel[int | str]):
            """Numeric value parser accepting int or numeric string."""

            root: int | str

        _STRING_LIST_ADAPTER: TypeAdapter[t.StrSequence] = TypeAdapter(t.StrSequence)

        @staticmethod
        def coerced_enum[E: StrEnum](enum_cls: type[E]) -> type[E]:
            """Create an Annotated StrEnum type with automatic coercion.

            Args:
                enum_cls: The StrEnum class to create an annotated type for.

            Returns:
                An Annotated type that validates and coerces string values to the enum.

            """
            return Annotated[
                enum_cls,
                BeforeValidator(FlextUtilities.coerce_validator(enum_cls)),
            ]

        @classmethod
        def dispatcher_enabled(cls) -> bool:
            """Return True when dispatcher integration should be used."""
            return cls._env_enabled("FLEXT_DB_ORACLE_ENABLE_DISPATCHER")

        @staticmethod
        def _env_enabled(flag_name: str, default: str = "0") -> bool:
            """Check if environment flag is enabled."""
            value = os.environ.get(flag_name, default)
            return value.lower() not in {"0", "false", "no"}

        @staticmethod
        def validate_identifier(identifier: str) -> r[bool]:
            """Validate an Oracle identifier."""
            if not identifier:
                return r[bool].fail("Empty Oracle identifier")
            if len(identifier) > c.DbOracle.OracleValidation.MAX_IDENTIFIER_LENGTH:
                return r[bool].fail("Oracle identifier too long")
            if identifier.upper() in c.DbOracle.OracleValidation.ORACLE_RESERVED:
                return r[bool].fail("Oracle identifier is reserved word")
            return r[bool].ok(True)

        @staticmethod
        def create_config_from_env() -> r[FlextDbOracleSettings]:
            """Create Oracle settings directly from the environment variables."""
            config_result = FlextDbOracleSettings.from_env("FLEXT_DB_ORACLE_")
            if config_result.is_failure:
                return r[FlextDbOracleSettings].fail(config_result.error)
            return r[FlextDbOracleSettings].ok(config_result.value)

        @staticmethod
        def escape_oracle_identifier(identifier: str) -> r[str]:
            """Escape and validate an Oracle identifier for safe use."""
            if not identifier.strip():
                return r[str].fail("Empty Oracle identifier")
            if not identifier.replace("_", "").isalnum():
                return r[str].fail("Invalid Oracle identifier")
            max_len = c.DbOracle.OracleValidation.MAX_IDENTIFIER_LENGTH
            return r[str].ok(identifier[:max_len])

        QUERY_RESULT_ADAPTER: TypeAdapter[t.ContainerValue] = TypeAdapter(
            t.ContainerValue,
        )

        @staticmethod
        def format_query_result(
            result: t.ContainerValue,
            format_type: str = "table",
        ) -> r[str]:
            """Format a query result to string or JSON."""
            if format_type == "json":
                return r[str].ok(
                    FlextDbOracleUtilities.DbOracle.QUERY_RESULT_ADAPTER.dump_json(
                        result,
                    ).decode(),
                )
            return r[str].ok(str(result))

        @staticmethod
        def format_sql_for_oracle(sql: str) -> r[str]:
            """Normalize SQL string formatting for Oracle execution."""
            normalized = " ".join(sql.split())
            return r[str].ok(normalized)

        HASH_PARAMS_ADAPTER: TypeAdapter[Mapping[str, t.ContainerValue]] = TypeAdapter(
            t.ContainerValueMapping,
        )

        @staticmethod
        def generate_query_hash(
            query: str,
            params: Mapping[str, t.ContainerValue] | None,
        ) -> r[str]:
            """Generate a SHA-256 hash for a query and its parameters."""
            sorted_params = dict(sorted((params or {}).items()))
            serialized = FlextDbOracleUtilities.DbOracle.HASH_PARAMS_ADAPTER.dump_json(
                sorted_params,
            ).decode()
            payload = f"{query}|{serialized}".encode()
            return r[str].ok(hashlib.sha256(payload).hexdigest()[:16])

        @staticmethod
        def _validate_config_map(value: t.ContainerValue) -> t.ConfigMap | None:
            """Validate arbitrary mapping input as ConfigMap."""
            if not isinstance(value, dict):
                return None
            try:
                return t.ConfigMap.model_validate({"root": value})
            except ValidationError:
                return None

        @staticmethod
        def normalize_params(params: t.ConfigMap | None) -> t.ConfigMap:
            """Normalize optional parameters into ConfigMap."""
            if params is not None:
                return params
            return t.ConfigMap(root={})

        @staticmethod
        def _parse_rowcount(value: t.ContainerValue) -> int:
            """Parse strict integer rowcount via Pydantic."""
            if isinstance(value, int):
                return value
            try:
                return FlextDbOracleUtilities.DbOracle._StrictIntValue.model_validate(  # noqa: SLF001
                    value
                ).root
            except ValidationError:
                return 0

        @staticmethod
        def _parse_count_value(value: t.ContainerValue) -> int:
            """Parse row count value accepting int or numeric string."""
            if isinstance(value, int):
                return value
            if isinstance(value, str):
                try:
                    return int(value)
                except ValueError:
                    return 0
            try:
                validated = FlextDbOracleUtilities.DbOracle._CountValue.model_validate(  # noqa: SLF001
                    value
                ).root
            except ValidationError:
                return 0
            try:
                return int(validated)
            except (TypeError, ValueError):
                return 0

        @staticmethod
        def _normalize_singer_type(value: str | t.StrSequence) -> str:
            """Normalize Singer type input to a single string value."""
            try:
                values = FlextDbOracleUtilities.DbOracle._STRING_LIST_ADAPTER.validate_python(  # noqa: SLF001
                    value
                )
            except ValidationError:
                return str(value)
            return values[0] if values else "string"

        @staticmethod
        def _sqlalchemy_create_engine(url: str) -> SAEngine:
            """Create SQLAlchemy engine."""
            return create_engine(url, pool_pre_ping=True, pool_recycle=3600, echo=False)

        @staticmethod
        def _sqlalchemy_text(statement: str) -> TextClause:
            """Build SQL text t.NormalizedValue."""
            return text(statement)

        @staticmethod
        def _engine_connect(engine: SAEngine) -> SAConnection:
            """Open connection context manager from engine."""
            return engine.connect()

        @staticmethod
        def _engine_begin(
            engine: SAEngine,
        ) -> contextlib.AbstractContextManager[SAConnection]:
            """Open transaction context manager from engine."""
            return engine.begin()

        @staticmethod
        def _context_exit(
            context_manager: contextlib.AbstractContextManager[SAConnection],
        ) -> None:
            """Exit dynamic context manager safely."""
            context_manager.__exit__(None, None, None)

        @staticmethod
        def _engine_dispose(engine: SAEngine) -> None:
            """Dispose engine resources."""
            engine.dispose()

        @staticmethod
        def _connection_execute(
            connection: SAConnection,
            statement: TextClause,
            parameters: t.ConfigMap | None = None,
        ) -> CursorResult[tuple[t.ContainerValue, ...]]:
            """Execute statement on SQL connection."""
            normalized_params = FlextDbOracleUtilities.DbOracle.normalize_params(
                parameters,
            )
            return connection.execute(statement, normalized_params.root)


__all__ = ["FlextDbOracleUtilities", "u"]

u = FlextDbOracleUtilities
