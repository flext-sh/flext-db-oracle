"""FlextDbOracle utilities mixin for Oracle-specific helpers."""

from __future__ import annotations

import hashlib
from collections.abc import Mapping
from enum import StrEnum
from typing import TYPE_CHECKING

from sqlalchemy import (
    Connection as SAConnection,
    Engine as SAEngine,
    TextClause,
    create_engine,
)

# mro-6int (claude-ulw): import aliases from upstream (flext_core/flext_cli) and
# the settings singleton from the concrete _settings leaf, not the own package
# facade, to break the flext_db_oracle package-init circular import.
from flext_cli import m, p, r, t, u
from flext_db_oracle import FlextDbOracleConstants as c
from flext_db_oracle._settings import settings

if TYPE_CHECKING:
    import contextlib

    from sqlalchemy.engine import CursorResult


class FlextDbOracleUtilitiesDbOracle:
    """Oracle-specific utility mixin.

    Groups all Oracle-specific utilities for better organization
    and cross-project access. Access via u.DbOracle.* pattern.

    Example:
        from flext_db_oracle import u
        result = u.DbOracle.Collection.parse_sequence(Status, ["active", "pending"])
        parsed = u.DbOracle.Args.parse_kwargs(kwargs, enum_fields)

    """

    class StrictIntValue(m.RootModel[int]):
        """Strict integer parser via Pydantic validation."""

        root: int

    class CountValue(m.RootModel[int | str]):
        """Numeric value parser accepting int or numeric string."""

        root: int | str

    @staticmethod
    def coerced_enum[E: StrEnum](enum_cls: type[E]) -> type[E]:
        """Create a coerced enum type with validation.

        Args:
            enum_cls: The StrEnum class to create a coerced type for.

        Returns:
            The enum class itself (callers apply Annotated+m.BeforeValidator as needed).

        """
        return enum_cls

    @staticmethod
    def dispatcher_enabled() -> bool:
        """Return True when dispatcher integration should be used."""
        return settings.DbOracle.enable_dispatcher

    @staticmethod
    def validate_identifier(identifier: str) -> p.Result[bool]:
        """Validate an Oracle identifier."""
        if not identifier:
            return r[bool].fail("Empty Oracle identifier")
        if len(identifier) > c.DbOracle.MAX_IDENTIFIER_LENGTH:
            return r[bool].fail("Oracle identifier too long")
        if identifier.upper() in c.DbOracle.ORACLE_RESERVED:
            return r[bool].fail("Oracle identifier is reserved word")
        return r[bool].ok(True)

    @staticmethod
    def escape_oracle_identifier(identifier: str) -> p.Result[str]:
        """Escape and validate an Oracle identifier for safe use."""
        if not identifier.strip():
            return r[str].fail("Empty Oracle identifier")
        if not identifier.replace("_", "").isalnum():
            return r[str].fail("Invalid Oracle identifier")
        max_len = c.DbOracle.MAX_IDENTIFIER_LENGTH
        return r[str].ok(identifier[:max_len])

    @classmethod
    def format_query_result(
        cls, result: t.JsonPayload, format_type: str = "table"
    ) -> p.Result[str]:
        """Format a query result to string or JSON."""
        if format_type == "json":
            json_payload: t.JsonValue = u.normalize_to_json_value(result)
            return r[str].ok(t.json_value_adapter().dump_json(json_payload).decode())
        return r[str].ok(str(result))

    @staticmethod
    def format_sql_for_oracle(sql: str) -> p.Result[str]:
        """Normalize SQL string formatting for Oracle execution."""
        normalized = " ".join(sql.split())
        return r[str].ok(normalized)

    @classmethod
    def generate_query_hash(
        cls, query: str, params: t.JsonMapping | None
    ) -> p.Result[str]:
        """Generate a SHA-256 hash for a query and its parameters."""
        sorted_params = dict(sorted((params or {}).items()))
        serialized = t.json_mapping_adapter().dump_json(sorted_params).decode()
        payload = f"{query}|{serialized}".encode()
        return r[str].ok(hashlib.sha256(payload).hexdigest()[:16])

    @staticmethod
    def validate_config_map(value: t.JsonValue | t.JsonMapping) -> m.ConfigMap | None:
        """Validate arbitrary mapping input as ConfigMap."""
        if not isinstance(value, Mapping):
            return None
        try:
            return m.ConfigMap.model_validate({"root": dict(value)})
        except c.ValidationError:
            return None

    @staticmethod
    def normalize_params(params: m.ConfigMap | None) -> m.ConfigMap:
        """Normalize optional parameters into ConfigMap."""
        if params is not None:
            return params
        return m.ConfigMap(root={})

    @classmethod
    def _parse_rowcount(cls, value: t.JsonValue) -> int:
        """Parse strict integer rowcount via Pydantic."""
        if isinstance(value, int):
            return value
        try:
            validated_rowcount: int = cls.StrictIntValue.model_validate(value).root
            return validated_rowcount
        except c.ValidationError:
            return 0

    @classmethod
    def _parse_count_value(cls, value: t.JsonValue) -> int:
        """Parse row count value accepting int or numeric string."""
        result: int
        if isinstance(value, int):
            result = value
        elif isinstance(value, str):
            try:
                result = int(value)
            except ValueError:
                result = 0
        else:
            try:
                result = int(cls.CountValue.model_validate(value).root)
            except c.ValidationError:
                result = 0
            except c.EXC_TYPE_VALIDATION:
                result = 0
        return result

    @classmethod
    def _normalize_singer_type(cls, value: str | t.StrSequence) -> str:
        """Normalize Singer type input to a single string value."""
        try:
            values = t.str_sequence_adapter().validate_python(value)
        except c.ValidationError:
            return str(value)
        return values[0] if values else "string"

    @staticmethod
    def _sqlalchemy_create_engine(
        url: str, connect_timeout: int | None = None
    ) -> SAEngine:
        """Create SQLAlchemy engine with optional connection timeout."""
        connect_args: t.MutableMappingKV[str, int] = {}
        if connect_timeout is not None:
            connect_args["tcp_connect_timeout"] = connect_timeout
        return create_engine(
            url,
            pool_pre_ping=True,
            pool_recycle=3600,
            echo=False,
            connect_args=connect_args,
        )

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

    @classmethod
    def _connection_execute(
        cls,
        connection: SAConnection,
        statement: TextClause,
        parameters: m.ConfigMap | None = None,
    ) -> CursorResult[tuple[t.JsonValue, ...]]:
        """Execute statement on SQL connection."""
        normalized_params = cls.normalize_params(parameters)
        return connection.execute(statement, normalized_params.root)
