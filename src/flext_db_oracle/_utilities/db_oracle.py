"""FlextDbOracle utilities mixin for Oracle-specific helpers."""

from __future__ import annotations

import contextlib
import hashlib
import os
from enum import StrEnum

from sqlalchemy import (
    Connection as SAConnection,
    Engine as SAEngine,
    TextClause,
    create_engine,
    text,
)
from sqlalchemy.engine import CursorResult

from flext_core import m, r
from flext_db_oracle import FlextDbOracleConstants as c, FlextDbOracleTypes as t


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
            The enum class itself (callers apply Annotated+BeforeValidator as needed).

        """
        return enum_cls

    @staticmethod
    def dispatcher_enabled() -> bool:
        """Return True when dispatcher integration should be used."""
        value = os.getenv(c.DbOracle.OracleEnvironment.ENV_ENABLE_DISPATCHER)
        if value is None:
            return False
        return value.strip().lower() in {"1", "true", "yes", "on"}

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
    def escape_oracle_identifier(identifier: str) -> r[str]:
        """Escape and validate an Oracle identifier for safe use."""
        if not identifier.strip():
            return r[str].fail("Empty Oracle identifier")
        if not identifier.replace("_", "").isalnum():
            return r[str].fail("Invalid Oracle identifier")
        max_len = c.DbOracle.OracleValidation.MAX_IDENTIFIER_LENGTH
        return r[str].ok(identifier[:max_len])

    @classmethod
    def format_query_result(
        cls,
        result: t.ContainerValue,
        format_type: str = "table",
    ) -> r[str]:
        """Format a query result to string or JSON."""
        if format_type == "json":
            return r[str].ok(
                t.CONTAINER_VALUE_ADAPTER.dump_json(
                    result,
                ).decode(),
            )
        return r[str].ok(str(result))

    @staticmethod
    def format_sql_for_oracle(sql: str) -> r[str]:
        """Normalize SQL string formatting for Oracle execution."""
        normalized = " ".join(sql.split())
        return r[str].ok(normalized)

    @classmethod
    def generate_query_hash(
        cls,
        query: str,
        params: t.ContainerValueMapping | None,
    ) -> r[str]:
        """Generate a SHA-256 hash for a query and its parameters."""
        sorted_params = dict(sorted((params or {}).items()))
        serialized = t.CONTAINER_VALUE_MAPPING_ADAPTER.dump_json(
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
        except c.ValidationError:
            return None

    @staticmethod
    def normalize_params(params: t.ConfigMap | None) -> t.ConfigMap:
        """Normalize optional parameters into ConfigMap."""
        if params is not None:
            return params
        return t.ConfigMap(root={})

    @classmethod
    def _parse_rowcount(cls, value: t.ContainerValue) -> int:
        """Parse strict integer rowcount via Pydantic."""
        if isinstance(value, int):
            return value
        try:
            return cls.StrictIntValue.model_validate(
                value,
            ).root
        except c.ValidationError:
            return 0

    @classmethod
    def _parse_count_value(cls, value: t.ContainerValue) -> int:
        """Parse row count value accepting int or numeric string."""
        if isinstance(value, int):
            return value
        if isinstance(value, str):
            try:
                return int(value)
            except ValueError:
                return 0
        try:
            validated = cls.CountValue.model_validate(
                value,
            ).root
        except c.ValidationError:
            return 0
        try:
            return int(validated)
        except (TypeError, ValueError):
            return 0

    @classmethod
    def _normalize_singer_type(cls, value: str | t.StrSequence) -> str:
        """Normalize Singer type input to a single string value."""
        try:
            values = t.STR_SEQUENCE_ADAPTER.validate_python(
                value,
            )
        except c.ValidationError:
            return str(value)
        return values[0] if values else "string"

    @staticmethod
    def _sqlalchemy_create_engine(
        url: str,
        connect_timeout: int | None = None,
    ) -> SAEngine:
        """Create SQLAlchemy engine with optional connection timeout."""
        connect_args: dict[str, int] = {}
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

    @classmethod
    def _connection_execute(
        cls,
        connection: SAConnection,
        statement: TextClause,
        parameters: t.ConfigMap | None = None,
    ) -> CursorResult[tuple[t.ContainerValue, ...]]:
        """Execute statement on SQL connection."""
        normalized_params = cls.normalize_params(
            parameters,
        )
        return connection.execute(statement, normalized_params.root)
