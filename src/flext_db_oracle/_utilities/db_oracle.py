"""FlextDbOracle utilities mixin for Oracle-specific helpers.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import hashlib
import threading
from collections.abc import Mapping, Sequence
from enum import StrEnum
from typing import TYPE_CHECKING, ClassVar
from urllib.parse import quote_plus

import oracledb
from flext_cli import u
from sqlalchemy import (
    Connection as SAConnection,
    Engine as SAEngine,
    Executable,
    TextClause,
    create_engine,
    event,
    func as _sqlalchemy_func,
    select as _sqlalchemy_select,
    text as _sqlalchemy_text,
)
from sqlalchemy.exc import DatabaseError as SADatabaseError
from sqlalchemy.orm import aliased as _sqlalchemy_aliased

from flext_db_oracle import FlextDbOracleSettings, c, m, p, r, settings, t
from flext_db_oracle._models import FlextDbOracleModelsConnection

if TYPE_CHECKING:
    import contextlib

    from sqlalchemy.engine import CursorResult
    from sqlalchemy.pool import ConnectionPoolEntry, PoolProxiedConnection


class FlextDbOracleUtilitiesDbOracle:
    """Oracle-specific utility mixin.

    Groups all Oracle-specific utilities for better organization
    and cross-project access. Access via u.DbOracle.* pattern.

    Example:
        from flext_db_oracle import u
        result = u.DbOracle.Collection.parse_sequence(Status, ["active", "pending"])
        parsed = u.DbOracle.Args.parse_kwargs(kwargs, enum_fields)

    """

    # Driver connections currently checked out of any engine built here: the
    # set a signal handler cancels so a killed process leaves no server call.
    _CHECKED_OUT: ClassVar[set[oracledb.Connection]] = set()
    _CHECKED_OUT_LOCK: ClassVar[threading.Lock] = threading.Lock()

    # Driver exception published for consumers: `except u.DbOracle.DatabaseError`
    # keeps the library import inside the owner facade.
    DatabaseError: ClassVar[type[Exception]] = SADatabaseError

    # Statement builders published natively (every overload kept):
    # `u.DbOracle.select(*columns)`, `u.DbOracle.func.count()` and
    # `u.DbOracle.aliased(Model)`.
    select = staticmethod(_sqlalchemy_select)
    func = _sqlalchemy_func
    aliased = staticmethod(_sqlalchemy_aliased)

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
    def validate_config_map(value: t.JsonValue | t.JsonMapping) -> p.ConfigMap:
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
    def normalize_params(params: p.ConfigMap | None) -> p.ConfigMap:
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

    @classmethod
    def engine(
        cls, url: str, options: FlextDbOracleModelsConnection.EngineOptions
    ) -> SAEngine:
        """Build the Oracle engine honoring the caller's ``options``.

        ``dsn`` replaces the TNS descriptor/alias; ``mode`` maps to the
        oracledb auth mode, ``pool_size``/``max_overflow`` mirror the pool
        bounds, ``connect_timeout`` overrides the settings timeout and
        ``connect_args`` adds driver arguments the settings do not own.

        Returns:
            The unconnected engine; the first checkout opens the session.

        """
        return cls._engine_from(settings, url, options, options.connect_args or {})

    @classmethod
    def build_engine(
        cls,
        config: FlextDbOracleSettings,
        connect_args: Mapping[str, t.Scalar] | None = None,
    ) -> SAEngine:
        """Build the engine of one settings snapshot (services and tests).

        Returns:
            The unconnected engine for ``config``.

        """
        oracle = config.DbOracle
        options = m.DbOracle.EngineOptions(
            dsn=oracle.dsn,
            mode=oracle.mode,
            connect_timeout=oracle.timeout,
            pool_size=oracle.pool_min,
            max_overflow=oracle.pool_max - oracle.pool_min,
            connect_args=connect_args,
        )
        return cls._engine_from(config, "", options, connect_args or {})

    @staticmethod
    def _engine_from(
        config: FlextDbOracleSettings,
        url: str,
        options: FlextDbOracleModelsConnection.EngineOptions,
        driver_args_extra: Mapping[str, t.Scalar],
    ) -> SAEngine:
        """Shared engine builder for a settings snapshot and its options.

        Returns:
            The unconnected engine.

        Raises:
            ValueError: The password is empty, or the extra driver arguments
                repeat an argument the settings already own.

        """
        oracle = config.DbOracle
        if not oracle.password:
            msg = "Password is required for database connection"
            raise ValueError(msg)
        credentials = (
            f"oracle+oracledb://{quote_plus(oracle.username)}"
            f":{quote_plus(oracle.password)}@"
        )
        timeout = (
            options.connect_timeout
            if options.connect_timeout is not None
            else oracle.timeout
        )
        driver_args: dict[str, t.Scalar] = {"tcp_connect_timeout": timeout}
        dsn = options.dsn if options.dsn is not None else oracle.dsn
        if dsn is None:
            url = (
                f"{credentials}{oracle.host}:{oracle.port}"
                f"/?service_name={quote_plus(oracle.service_name)}"
            )
        else:
            url = credentials
            driver_args["dsn"] = dsn
        mode = options.mode if options.mode is not None else oracle.mode
        if mode is not None:
            driver_args["mode"] = (
                oracledb.AUTH_MODE_SYSDBA
                if mode == "SYSDBA"
                else oracledb.AUTH_MODE_SYSOPER
            )
        conflicting = sorted(driver_args.keys() & driver_args_extra.keys())
        if conflicting:
            msg = f"connect_args repeat settings-owned driver arguments: {conflicting}"
            raise ValueError(msg)
        driver_args.update(driver_args_extra)
        pool_size = (
            options.pool_size if options.pool_size is not None else oracle.pool_min
        )
        max_overflow = (
            options.max_overflow
            if options.max_overflow is not None
            else oracle.pool_max - oracle.pool_min
        )
        engine = create_engine(
            url,
            pool_size=pool_size,
            max_overflow=max_overflow,
            pool_pre_ping=True,
            pool_recycle=options.pool_recycle,
            echo=False,
            connect_args=driver_args,
        )
        event.listen(engine, "checkout", FlextDbOracleUtilitiesDbOracle._track_checkout)
        event.listen(engine, "checkin", FlextDbOracleUtilitiesDbOracle._track_checkin)
        return engine

    @classmethod
    def _track_checkout(
        cls,
        dbapi_connection: oracledb.Connection,
        _record: ConnectionPoolEntry,
        _proxy: PoolProxiedConnection,
    ) -> None:
        with cls._CHECKED_OUT_LOCK:
            cls._CHECKED_OUT.add(dbapi_connection)

    @classmethod
    def _track_checkin(
        cls, dbapi_connection: oracledb.Connection, _record: ConnectionPoolEntry
    ) -> None:
        with cls._CHECKED_OUT_LOCK:
            cls._CHECKED_OUT.discard(dbapi_connection)

    @classmethod
    def cancel_active(cls) -> int:
        """Break the server call of every checked-out driver connection.

        ``oracledb.Connection.cancel`` is the driver's thread-safe break: the
        server aborts the running call with ORA-01013 and rolls it back. Meant
        for a process's SIGTERM/SIGINT handler, so a killed CLI leaves no
        session executing on the database.

        Returns:
            How many connections received the break.

        """
        with cls._CHECKED_OUT_LOCK:
            active = tuple(cls._CHECKED_OUT)
        for connection in active:
            connection.cancel()
        return len(active)

    @staticmethod
    def fetch_models_on_connection[M: m.BaseModel](
        sql: Executable | str,
        params: Mapping[str, t.JsonPayload] | None = None,
        *,
        model: type[M],
        connection: SAConnection,
    ) -> Sequence[M]:
        """Run a query on the caller's open connection and validate each row.

        The connection is injected, so session state the caller set on it
        (``ALTER SESSION``, LogMiner, an open transaction) is preserved. Row
        values reach ``model`` as the driver returned them.

        Returns:
            One ``model`` instance per row, in result order.

        """
        statement = sql if isinstance(sql, Executable) else _sqlalchemy_text(sql)
        result = connection.execute(statement, dict(params or {}))
        return [model.model_validate(dict(row)) for row in result.mappings()]

    @staticmethod
    def execute_driver_sql(
        sql: str,
        params: Mapping[str, t.Scalar | None] | None = None,
        *,
        connection: SAConnection,
    ) -> int:
        """Execute driver-native SQL or a PL/SQL block on the caller's connection.

        The statement goes to the driver verbatim: unlike ``text()``, a colon
        inside a string literal (``'HH24:MI'``) is not parsed as a bind.

        Returns:
            The affected row count reported by the driver (zero when unknown).

        """
        result = connection.exec_driver_sql(sql, dict(params or {}))
        return max(result.rowcount, 0)

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
        parameters: p.ConfigMap | None = None,
    ) -> CursorResult[tuple[t.JsonValue, ...]]:
        """Execute statement on SQL connection.

        Returns:
            The resulting ``CursorResult[tuple[t.JsonValue, ...]]``.

        """
        normalized_params = cls.normalize_params(parameters)
        return connection.execute(statement, normalized_params.root)


__all__: tuple[str, ...] = ("FlextDbOracleUtilitiesDbOracle",)
