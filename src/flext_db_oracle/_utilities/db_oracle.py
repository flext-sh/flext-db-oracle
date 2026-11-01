"""FlextDbOracle utilities mixin for Oracle-specific helpers.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import hashlib
from collections.abc import Mapping, Sequence
from enum import StrEnum
from typing import TYPE_CHECKING, Literal

import oracledb
from flext_cli import u
from sqlalchemy import (
    Connection as SAConnection,
    Engine as SAEngine,
    TextClause,
    create_engine,
    text as _sqlalchemy_text,
)

from flext_db_oracle import c, m, p, r, settings, t

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

    @staticmethod
    def text(statement: str) -> TextClause:
        """Build a SQLAlchemy text clause through the database facade.

        SQLAlchemy is owned by flext-db-oracle: consumers construct statement
        clauses here instead of importing the library.

        Returns:
            The resulting ``TextClause``.

        """
        return _sqlalchemy_text(statement)

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
        """Validate an Oracle identifier.

        Returns:
            The resulting ``p.Result[bool]``.

        """
        if not identifier:
            return r[bool].fail("Empty Oracle identifier")
        if len(identifier) > c.DbOracle.MAX_IDENTIFIER_LENGTH:
            return r[bool].fail("Oracle identifier too long")
        if identifier.upper() in c.DbOracle.ORACLE_RESERVED:
            return r[bool].fail("Oracle identifier is reserved word")
        return r[bool].ok(value=True)

    @staticmethod
    def escape_oracle_identifier(identifier: str) -> p.Result[str]:
        """Escape and validate an Oracle identifier for safe use.

        Returns:
            The resulting ``p.Result[str]``.

        """
        if not identifier.strip():
            return r[str].fail("Empty Oracle identifier")
        if not identifier.replace("_", "").isalnum():
            return r[str].fail("Invalid Oracle identifier")
        max_len = c.DbOracle.MAX_IDENTIFIER_LENGTH
        return r[str].ok(identifier[:max_len])

    @classmethod
    def format_query_result(
        cls,
        result: t.JsonPayload | t.JsonMapping | tuple[t.JsonValue, ...],
        format_type: str = "table",
    ) -> p.Result[str]:
        """Format a query result to string or JSON.

        Returns:
            The resulting ``p.Result[str]``.

        """
        if format_type == "json":
            json_payload: t.JsonValue = u.normalize_to_json_value(result)
            return r[str].ok(u.json_value_adapter().dump_json(json_payload).decode())
        return r[str].ok(str(result))

    @staticmethod
    def format_sql_for_oracle(sql: str) -> p.Result[str]:
        """Normalize SQL string formatting for Oracle execution.

        Returns:
            The resulting ``p.Result[str]``.

        """
        normalized = " ".join(sql.split())
        return r[str].ok(normalized)

    @classmethod
    def generate_query_hash(
        cls,
        query: str,
        params: t.JsonMapping | None,
    ) -> p.Result[str]:
        """Generate a SHA-256 hash for a query and its parameters.

        Returns:
            The resulting ``p.Result[str]``.

        """
        sorted_params = dict(sorted((params or {}).items()))
        serialized = u.json_mapping_adapter().dump_json(sorted_params).decode()
        payload = f"{query}|{serialized}".encode()
        return r[str].ok(hashlib.sha256(payload).hexdigest()[:16])

    @staticmethod
    def validate_config_map(value: t.JsonValue | t.JsonMapping) -> m.ConfigMap:
        """Validate arbitrary mapping input as ConfigMap.

        Returns:
            The resulting ``m.ConfigMap``.

        Raises:
            TypeError: ``value`` is not a mapping.

        """
        # Why: no-hidden-errors — propagate the raw failure instead of
        # masking a malformed mapping as an empty/None sentinel.
        if not isinstance(value, Mapping):
            msg = f"Oracle config map requires a mapping, got {type(value).__name__}"
            raise TypeError(msg)
        return m.ConfigMap.model_validate({"root": dict(value)})

    @staticmethod
    def normalize_params(params: m.ConfigMap | None) -> m.ConfigMap:
        """Normalize optional parameters into ConfigMap.

        Returns:
            The resulting ``m.ConfigMap``.

        """
        if params is not None:
            return params
        return m.ConfigMap(root={})

    @staticmethod
    def _parse_count_value(value: str) -> int:
        """Parse row count value from a numeric count string.

        Returns:
            The resulting ``int``.

        """
        return int(value)

    @staticmethod
    def _normalize_singer_type(value: str | Sequence[str]) -> str:
        """Normalize Singer type input to a single string value.

        Returns:
            The resulting ``str``.

        Raises:
            ValueError: If Singer type sequence must not be empty.

        """
        if isinstance(value, str):
            return value
        validated = u.validate_value(u.str_sequence_adapter(), value).unwrap()
        if not validated:
            msg = "Singer type sequence must not be empty"
            raise ValueError(msg)
        return validated[0]

    @staticmethod
    def engine(
        url: str,
        *,
        connect_args: Mapping[str, object] | None = None,
        pool_size: int | None = None,
        max_overflow: int | None = None,
        pool_recycle: int | None = None,
        connect_timeout: int | None = None,
        mode: Literal["SYSDBA", "SYSOPER"] | None = None,
    ) -> SAEngine:
        """Build a SQLAlchemy engine through the database facade.

        SQLAlchemy is owned by flext-db-oracle: consumers construct engines
        here instead of importing the library. ``mode`` maps to the oracledb
        privilege mode (AUTH_MODE_SYSDBA/AUTH_MODE_SYSOPER) via ``connect_args``.

        Returns:
            The resulting ``SAEngine``.

        """
        return FlextDbOracleUtilitiesDbOracle._sqlalchemy_create_engine(
            url,
            connect_timeout=connect_timeout,
            mode=mode,
            connect_args=connect_args,
            pool_size=pool_size,
            max_overflow=max_overflow,
            pool_recycle=pool_recycle,
        )

    @staticmethod
    def _sqlalchemy_create_engine(
        url: str,
        connect_timeout: int | None = None,
        mode: Literal["SYSDBA", "SYSOPER"] | None = None,
        connect_args: Mapping[str, object] | None = None,
        pool_size: int | None = None,
        max_overflow: int | None = None,
        pool_recycle: int | None = None,
    ) -> SAEngine:
        """Create SQLAlchemy engine with optional connection timeout.

        ``mode`` maps to the oracledb privilege mode (AUTH_MODE_SYSDBA/
        AUTH_MODE_SYSOPER) via ``connect_args`` — SYSDBA logins reject a
        normal connection with ORA-28009. ``connect_args`` carries any extra
        driver keyword (e.g. ``dsn`` for TNS descriptors) and wins over the
        scalars above when they collide.

        Returns:
            The resulting ``SAEngine``.

        """
        resolved: dict[str, object] = {}
        if connect_timeout is not None:
            resolved["tcp_connect_timeout"] = connect_timeout
        if mode is not None:
            resolved["mode"] = (
                oracledb.AUTH_MODE_SYSDBA
                if mode == "SYSDBA"
                else oracledb.AUTH_MODE_SYSOPER
            )
        if connect_args:
            resolved.update(connect_args)
        options: dict[str, object] = {
            "pool_pre_ping": True,
            "pool_recycle": pool_recycle if pool_recycle is not None else 3600,
            "echo": False,
            "connect_args": resolved,
        }
        if pool_size is not None:
            options["pool_size"] = pool_size
        if max_overflow is not None:
            options["max_overflow"] = max_overflow
        return create_engine(url, **options)

    @staticmethod
    def _engine_connect(engine: SAEngine) -> SAConnection:
        """Open connection context manager from engine.

        Returns:
            The resulting ``SAConnection``.

        """
        return engine.connect()

    @staticmethod
    def _engine_begin(
        engine: SAEngine,
    ) -> contextlib.AbstractContextManager[SAConnection]:
        """Open transaction context manager from engine.

        Returns:
            The resulting ``contextlib.AbstractContextManager[SAConnection]``.

        """
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
        """Execute statement on SQL connection.

        Returns:
            The resulting ``CursorResult[tuple[t.JsonValue, ...]]``.

        """
        normalized_params = cls.normalize_params(parameters)
        return connection.execute(statement, normalized_params.root)


__all__: tuple[str, ...] = ("FlextDbOracleUtilitiesDbOracle",)
