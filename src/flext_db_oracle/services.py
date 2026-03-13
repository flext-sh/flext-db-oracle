"""Generic Oracle Database services delegating to flext-core and SQLAlchemy.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import hashlib
import time
from collections.abc import Generator, Mapping, Sequence
from contextlib import contextmanager
from importlib import import_module
from typing import Self, override
from urllib.parse import quote_plus

import oracledb
from flext_core import FlextService, r
from pydantic import RootModel, TypeAdapter, ValidationError
from sqlalchemy.exc import (
    DatabaseError as SQLAlchemyDatabaseError,
    OperationalError as SQLAlchemyOperationalError,
    SQLAlchemyError,
)

from flext_db_oracle.constants import c
from flext_db_oracle.models import FlextDbOracleModels, m
from flext_db_oracle.settings import FlextDbOracleSettings
from flext_db_oracle.typings import t
from flext_db_oracle.utilities import u

OracleDatabaseError: type[Exception] = oracledb.DatabaseError
OracleInterfaceError: type[Exception] = oracledb.InterfaceError


class _ObjectRows(RootModel[list[object]]):
    """Pydantic root model for generic list payloads."""

    root: list[object]


class _StrictIntValue(RootModel[int]):
    """Pydantic root model for strict integer validation."""

    root: int


class _CountValue(RootModel[int | str]):
    """Pydantic root model for count value (int or numeric string)."""

    root: int | str


_STRING_LIST_ADAPTER = TypeAdapter(list[str])


def _validate_config_map(value: object) -> m.ConfigMap | None:
    """Validate arbitrary mapping input as ConfigMap."""
    try:
        return m.ConfigMap(value)
    except ValidationError:
        return None


def _normalize_params(params: m.ConfigMap | None) -> m.ConfigMap:
    """Normalize optional parameters into ConfigMap."""
    if params is not None:
        return params
    return m.ConfigMap(root={})


def _parse_rowcount(value: object) -> int:
    """Parse strict integer rowcount via Pydantic."""
    try:
        return _StrictIntValue(value).root
    except ValidationError:
        return 0


def _parse_count_value(value: object) -> int:
    """Parse row count value accepting int or numeric string."""
    try:
        validated = _CountValue(value).root
    except ValidationError:
        return 0
    try:
        return int(validated)
    except (TypeError, ValueError):
        return 0


def _normalize_singer_type(value: str | list[str]) -> str:
    """Normalize Singer type input to a single string value."""
    try:
        values = _STRING_LIST_ADAPTER.validate_python(value)
    except ValidationError:
        return str(value)
    return values[0] if values else "string"


def _extract_object_rows(value: object) -> list[object]:
    """Extract list payload using Pydantic validation."""
    return _ObjectRows(value).root


def _sqlalchemy_create_engine(url: str) -> object:
    """Create SQLAlchemy engine via runtime import to keep type boundaries explicit."""
    sqlalchemy_module = import_module("sqlalchemy")
    create_engine_func = getattr(sqlalchemy_module, "create_engine", None)
    if not callable(create_engine_func):
        msg = "sqlalchemy.create_engine unavailable"
        raise TypeError(msg)
    return create_engine_func(url, pool_pre_ping=True, pool_recycle=3600, echo=False)


def _sqlalchemy_text(statement: str) -> object:
    """Build SQL text object via runtime import."""
    sqlalchemy_module = import_module("sqlalchemy")
    text_func = getattr(sqlalchemy_module, "text", None)
    if not callable(text_func):
        msg = "sqlalchemy.text unavailable"
        raise TypeError(msg)
    return text_func(statement)


def _engine_connect(engine: object) -> object:
    """Open connection context manager from engine."""
    connect_method = getattr(engine, "connect", None)
    if not callable(connect_method):
        msg = "Database engine does not expose connect()"
        raise TypeError(msg)
    return connect_method()


def _engine_begin(engine: object) -> object:
    """Open transaction context manager from engine."""
    begin_method = getattr(engine, "begin", None)
    if not callable(begin_method):
        msg = "Database engine does not expose begin()"
        raise TypeError(msg)
    return begin_method()


def _context_enter(context_manager: object) -> object:
    """Enter dynamic context manager and return inner object."""
    enter_method = getattr(context_manager, "__enter__", None)
    if not callable(enter_method):
        msg = "Context manager does not expose __enter__()"
        raise TypeError(msg)
    return enter_method()


def _context_exit(context_manager: object) -> None:
    """Exit dynamic context manager safely."""
    exit_method = getattr(context_manager, "__exit__", None)
    if callable(exit_method):
        _ = exit_method(None, None, None)


def _engine_dispose(engine: object) -> None:
    """Dispose engine resources through dynamic method lookup."""
    dispose_method = getattr(engine, "dispose", None)
    if callable(dispose_method):
        dispose_method()


def _connection_execute(
    connection: object, statement: object, parameters: m.ConfigMap | None = None
) -> object:
    """Execute statement on dynamic SQL connection."""
    execute_method = getattr(connection, "execute", None)
    if not callable(execute_method):
        msg = "Database connection does not expose execute()"
        raise TypeError(msg)
    normalized_params = _normalize_params(parameters)
    return execute_method(statement, normalized_params.root)


class FlextDbOracleServices(FlextService[FlextDbOracleSettings]):
    """Generic Oracle database services using flext-core patterns."""

    def __init__(self, config: FlextDbOracleSettings) -> None:
        """Initialize with configuration."""
        super().__init__()
        self._db_config = config
        self._config = config
        self._engine: object | None = None
        self._operations: list[FlextDbOracleModels.DbOracle.OperationRecord] = []
        self._plugins: dict[str, object] = {}
        self._metrics: dict[str, object] = {}

    def build_create_index_statement(self, _config: object) -> r[str]:
        """Build Oracle CREATE INDEX statement from configuration."""
        try:
            if not isinstance(_config, Mapping):
                return r[str].fail("Invalid CREATE INDEX config payload")
            payload = {
                "table_name": str(_config.get("table_name", "")),
                "index_name": str(_config.get("index_name", "")),
                "columns": [str(col) for col in _config.get("columns", [])],
                "unique": bool(_config.get("unique", False)),
                "schema_name": str(_config.get("schema_name", "")),
                "tablespace": str(_config.get("tablespace", "")),
                "parallel": int(_config.get("parallel", 1)),
            }
            config = FlextDbOracleModels.DbOracle.CreateIndexConfig.model_validate(
                payload
            )
            if not config.columns:
                return r[str].fail("Index definition requires at least one column")
            schema_prefix = f"{config.schema_name}." if config.schema_name else ""
            unique_prefix = "UNIQUE " if config.unique else ""
            columns = ", ".join(config.columns)
            sql = f"CREATE {unique_prefix}INDEX {config.index_name} ON {schema_prefix}{config.table_name} ({columns})"
            if config.tablespace:
                sql = f"{sql} TABLESPACE {config.tablespace}"
            if config.parallel > 1:
                sql = f"{sql} PARALLEL {config.parallel}"
            return r[str].ok(sql)
        except ValidationError as e:
            return r[str].fail(f"Invalid CREATE INDEX config: {e}")

    def build_delete_statement(
        self, table_name: str, where_columns: list[str], schema: str | None = None
    ) -> r[str]:
        """Build DELETE statement - simplified."""
        wheres = " AND ".join(f"{col} = :{col}" for col in where_columns)
        schema_prefix = f"{schema}." if schema else ""
        sql = f"DELETE FROM {schema_prefix}{table_name} WHERE {wheres}"
        return r[str].ok(sql)

    def build_insert_statement(
        self,
        table_name: str,
        columns: list[str],
        schema: str | None = None,
        returning_columns: list[str] | None = None,
    ) -> r[str]:
        """Build INSERT statement - simplified."""
        cols = ", ".join(columns)
        vals = ", ".join(f":{col}" for col in columns)
        schema_prefix = f"{schema}." if schema else ""
        sql = f"INSERT INTO {schema_prefix}{table_name} ({cols}) VALUES ({vals})"
        if returning_columns:
            ret = ", ".join(returning_columns)
            sql += f" RETURNING {ret}"
        return r[str].ok(sql)

    def build_select(
        self,
        table_name: str,
        columns: list[str] | None = None,
        conditions: m.ConfigMap | object | None = None,
        schema_name: str | None = None,
    ) -> r[str]:
        """Build SELECT query - simplified implementation."""
        typed_conditions = (
            conditions
            if isinstance(conditions, m.ConfigMap) or conditions is None
            else m.ConfigMap(conditions)
        )
        cols = ", ".join(columns) if columns else "*"
        if typed_conditions and typed_conditions.root:
            where_pairs = [f"{k} = :{k}" for k in typed_conditions.root]
            where = f" WHERE {' AND '.join(where_pairs)}"
        else:
            where = ""
        schema_prefix = f"{schema_name.upper()}." if schema_name else ""
        sql = f"SELECT {cols} FROM {schema_prefix}{table_name.upper()}{where}"
        return r[str].ok(sql)

    def build_update_statement(
        self,
        table_name: str,
        set_columns: list[str],
        where_columns: list[str],
        schema: str | None = None,
    ) -> r[str]:
        """Build UPDATE statement - simplified."""
        sets = ", ".join(f"{col}=:{col}" for col in set_columns)
        wheres = " AND ".join(f"{col} = :{col}" for col in where_columns)
        schema_prefix = f"{schema}." if schema else ""
        sql = f"UPDATE {schema_prefix}{table_name} SET {sets} WHERE {wheres}"
        return r[str].ok(sql)

    def connect(self) -> r[Self]:
        """Establish Oracle database connection."""
        url_result = self._build_connection_url()
        if url_result.is_failure:
            return r[Self].fail(url_result.error or "Failed to build connection URL")
        self._engine = _sqlalchemy_create_engine(url_result.value)
        try:
            connect_ctx = _engine_connect(self._engine)
            conn = _context_enter(connect_ctx)
            try:
                _ = _connection_execute(conn, _sqlalchemy_text("SELECT 1 FROM dual"))
            finally:
                _context_exit(connect_ctx)
            self.logger.info(f"Connected to Oracle database: {self._db_config.host}")
            return r[Self].ok(self)
        except (
            OracleDatabaseError,
            OracleInterfaceError,
            ConnectionError,
            SQLAlchemyDatabaseError,
            SQLAlchemyOperationalError,
            SQLAlchemyError,
            OSError,
        ) as e:
            local_host = self._db_config.host in {
                "localhost",
                c.DbOracle.Platform.LOCALHOST_IP,
            }
            default_port = c.DbOracle.Connection.DEFAULT_PORT
            if local_host and self._db_config.port != default_port:
                self._db_config.port = default_port
                retry_url_result = self._build_connection_url()
                if retry_url_result.is_success:
                    self._engine = _sqlalchemy_create_engine(retry_url_result.value)
                    try:
                        connect_ctx = _engine_connect(self._engine)
                        conn = _context_enter(connect_ctx)
                        try:
                            _ = _connection_execute(
                                conn, _sqlalchemy_text("SELECT 1 FROM dual")
                            )
                        finally:
                            _context_exit(connect_ctx)
                        self.logger.info(
                            f"Connected to Oracle database: {self._db_config.host}"
                        )
                        return r[Self].ok(self)
                    except (
                        OracleDatabaseError,
                        OracleInterfaceError,
                        ConnectionError,
                        SQLAlchemyDatabaseError,
                        SQLAlchemyOperationalError,
                        SQLAlchemyError,
                        OSError,
                    ):
                        self._engine = None
            self._engine = None
            self.logger.exception("Oracle connection failed")
            return r[Self].fail(f"Connection failed: {e}")

    def convert_singer_type(
        self, singer_type: str | list[str] = "string", _format_hint: str | None = None
    ) -> r[str]:
        """Convert Singer type to Oracle type - simplified."""
        singer_type = _normalize_singer_type(singer_type)
        if _format_hint == "date-time":
            return r[str].ok("TIMESTAMP")
        type_map = {
            "string": "VARCHAR2(4000)",
            "integer": "NUMBER(38)",
            "number": "NUMBER",
            "boolean": "NUMBER(1)",
            "date-time": "TIMESTAMP",
        }
        oracle_type = type_map.get(singer_type, "VARCHAR2(255)")
        return r[str].ok(oracle_type)

    def create_table_ddl(
        self,
        table_name: str,
        columns: Sequence[FlextDbOracleModels.DbOracle.Column | object],
        schema: str | None = None,
    ) -> r[str]:
        """Generate CREATE TABLE DDL - simplified."""
        col_defs: list[str] = []
        primary_keys: list[str] = []
        for col in columns:
            if isinstance(col, FlextDbOracleModels.DbOracle.Column):
                name = col.name or "unknown"
                data_type = col.data_type or "VARCHAR2(255)"
                nullable = "" if col.nullable else " NOT NULL"
                if getattr(col, "primary_key", False):
                    primary_keys.append(name)
            elif isinstance(col, Mapping):
                name_value = col.get("name") or col.get("column_name")
                data_type_value = col.get("data_type")
                nullable_value = col.get("nullable", True)
                name = str(name_value) if name_value is not None else "unknown"
                data_type = (
                    str(data_type_value)
                    if data_type_value is not None
                    else "VARCHAR2(255)"
                )
                nullable = "" if bool(nullable_value) else " NOT NULL"
                if bool(col.get("primary_key", False)):
                    primary_keys.append(name)
            else:
                continue
            col_defs.append(f"{name} {data_type}{nullable}")
        if primary_keys:
            col_defs.append(f"PRIMARY KEY ({', '.join(primary_keys)})")
        schema_prefix = f"{schema}." if schema else ""
        ddl = f"CREATE TABLE {schema_prefix}{table_name} (\n  {', '.join(col_defs)}\n)"
        return r[str].ok(ddl)

    def disconnect(self) -> r[bool]:
        """Disconnect from Oracle database."""
        engine = self._engine
        if engine is not None:
            _engine_dispose(engine)
            self._engine = None
            self.logger.info("Disconnected from Oracle database")
        return r[bool].ok(True)

    def drop_table_ddl(self, table_name: str, schema: str | None = None) -> r[str]:
        """Generate DROP TABLE DDL."""
        schema_prefix = f"{schema}." if schema else ""
        ddl = f"DROP TABLE {schema_prefix}{table_name}"
        return r[str].ok(ddl)

    @override
    def execute(self, **_kwargs: t.Scalar) -> r[FlextDbOracleSettings]:
        """Execute main domain service operation - return config."""
        test_result = self.test_connection()
        if test_result.is_success:
            return r[FlextDbOracleSettings].ok(self._db_config)
        return r[FlextDbOracleSettings].fail(
            test_result.error or "Connection test failed"
        )

    def execute_many(
        self,
        sql: str,
        params_list: Sequence[Mapping[str, object] | m.ConfigMap],
    ) -> r[int]:
        """Execute SQL statement multiple times."""
        if not self.is_connected():
            return r[int].fail("Not connected to database")
        engine_result = self._get_engine()
        if engine_result.is_failure:
            return r[int].fail(engine_result.error or "Failed to get database engine")
        try:
            connect_ctx = _engine_connect(engine_result.value)
            conn = _context_enter(connect_ctx)
            try:
                total_affected = 0
                for params in params_list:
                    typed_params = (
                        params
                        if isinstance(params, m.ConfigMap)
                        else m.ConfigMap(params)
                    )
                    result = _connection_execute(
                        conn, _sqlalchemy_text(sql), typed_params
                    )
                    rowcount_raw = getattr(result, "rowcount", 0)
                    total_affected += _parse_rowcount(rowcount_raw)
                return r[int].ok(total_affected)
            finally:
                _context_exit(connect_ctx)
        except (
            OracleDatabaseError,
            OracleInterfaceError,
            ConnectionError,
            SQLAlchemyDatabaseError,
            SQLAlchemyOperationalError,
            SQLAlchemyError,
            OSError,
        ) as e:
            return r[int].fail(f"Bulk execution failed: {e}")

    def execute_query(
        self, sql: str, params: m.ConfigMap | None = None
    ) -> r[list[m.Dict]]:
        """Execute SQL query and return results."""
        if not self.is_connected():
            return r[list[m.Dict]].fail("Not connected to database")
        engine_result = self._get_engine()
        if engine_result.is_failure:
            return r[list[m.Dict]].fail(
                engine_result.error or "Failed to get database engine"
            )
        try:
            connect_ctx = _engine_connect(engine_result.value)
            conn = _context_enter(connect_ctx)
            try:
                result = _connection_execute(conn, _sqlalchemy_text(sql), params)
                rows: list[m.Dict] = self._normalize_query_rows(result)
                return r[list[m.Dict]].ok(rows)
            finally:
                _context_exit(connect_ctx)
        except (
            OracleDatabaseError,
            OracleInterfaceError,
            ConnectionError,
            SQLAlchemyDatabaseError,
            SQLAlchemyOperationalError,
            SQLAlchemyError,
            OSError,
        ) as e:
            return r[list[m.Dict]].fail(f"Query execution failed: {e}")

    def execute_statement(self, sql: str, params: m.ConfigMap | None = None) -> r[int]:
        """Execute SQL statement and return affected rows."""
        if not self.is_connected():
            return r[int].fail("Not connected to database")
        engine_result = self._get_engine()
        if engine_result.is_failure:
            return r[int].fail(engine_result.error or "Failed to get database engine")
        try:
            transaction_ctx = _engine_begin(engine_result.value)
            conn = _context_enter(transaction_ctx)
            try:
                result = _connection_execute(conn, _sqlalchemy_text(sql), params)
                rowcount_raw = getattr(result, "rowcount", 0)
                rowcount = _parse_rowcount(rowcount_raw)
                return r[int].ok(rowcount)
            finally:
                _context_exit(transaction_ctx)
        except (
            OracleDatabaseError,
            OracleInterfaceError,
            ConnectionError,
            SQLAlchemyDatabaseError,
            SQLAlchemyOperationalError,
            SQLAlchemyError,
            OSError,
        ) as e:
            return r[int].fail(f"Statement execution failed: {e}")

    def fetch_one(
        self, sql: str, params: m.ConfigMap | None = None
    ) -> r[m.Dict | None]:
        """Execute query and return first result."""
        return self.execute_query(sql, params).map(
            lambda rows: rows[0] if rows else None
        )

    def generate_query_hash(
        self, sql: str = "", params: m.ConfigMap | object | None = None
    ) -> r[str]:
        """Generate query hash - simplified."""
        typed_params = (
            params
            if isinstance(params, m.ConfigMap) or params is None
            else m.ConfigMap(params)
        )
        hash_input = f"{sql}_{typed_params!s}"
        return r[str].ok(hashlib.sha256(hash_input.encode()).hexdigest()[:16])

    def get_columns(
        self, table_name: str, schema_name: str | None = None
    ) -> r[list[FlextDbOracleModels.DbOracle.Column]]:
        """Get column information for Oracle table."""
        if schema_name:
            sql = "\nSELECT column_name, data_type, data_length, data_precision, data_scale, nullable\nFROM all_tab_columns\nWHERE table_name = UPPER(:table_name) AND owner = UPPER(:schema_name)\nORDER BY column_id\n"
            params = m.ConfigMap(
                root={"table_name": table_name, "schema_name": schema_name}
            )
        else:
            sql = "\nSELECT column_name, data_type, data_length, data_precision, data_scale, nullable\nFROM user_tab_columns\nWHERE table_name = UPPER(:table_name)\nORDER BY column_id\n"
            params = m.ConfigMap(root={"table_name": table_name})
        return self.execute_query(sql, params).map(
            lambda rows: [
                FlextDbOracleModels.DbOracle.Column(
                    name=str(row.root.get("column_name", "")),
                    data_type=str(row.root.get("data_type", "")),
                    nullable=str(row.root.get("nullable", "Y")) == "Y",
                    default_value=str(row.root.get("data_default", "")),
                )
                for row in rows
            ]
        )

    @contextmanager
    def get_connection(self) -> Generator[object]:
        """Get database connection context manager."""
        engine = self._engine
        if engine is None:
            msg = "No database connection established"
            raise RuntimeError(msg)
        connect_ctx = _engine_connect(engine)
        connection = _context_enter(connect_ctx)
        try:
            yield connection
        finally:
            _context_exit(connect_ctx)

    def get_connection_status(self) -> r[FlextDbOracleModels.DbOracle.ConnectionStatus]:
        """Get connection status - simplified."""
        return r[FlextDbOracleModels.DbOracle.ConnectionStatus].ok(
            FlextDbOracleModels.DbOracle.ConnectionStatus(
                is_connected=self.is_connected(),
                host=self._db_config.host,
                port=self._db_config.port,
                service_name=self._db_config.service_name,
                username=self._db_config.username,
                error_message="" if self.is_connected() else "Connection unavailable",
            )
        )

    def get_metrics(self) -> r[FlextDbOracleModels.DbOracle.HealthStatus]:
        """Get metrics status with explicit observability integration check."""
        try:
            observability_module = import_module("flext_observability")
        except ModuleNotFoundError:
            return r[FlextDbOracleModels.DbOracle.HealthStatus].fail(
                "flext-observability integration unavailable; install flext-observability"
            )
        metric_factory = getattr(observability_module, "flext_metric", None)
        if not callable(metric_factory):
            return r[FlextDbOracleModels.DbOracle.HealthStatus].fail(
                "flext-observability does not expose flext_metric"
            )
        status = "connected" if self.is_connected() else "disconnected"
        metrics_payload: dict[str, str] = {
            metric_name: str(metric_value)
            for metric_name, metric_value in self._metrics.items()
        }
        return r[FlextDbOracleModels.DbOracle.HealthStatus].ok(
            FlextDbOracleModels.DbOracle.HealthStatus.model_validate({
                "status": f"{status}_with_observability",
                "timestamp": self._get_current_timestamp(),
                "service": "oracle",
                "database": self._db_config.service_name,
                "metrics": metrics_payload,
            })
        )

    def get_operations(self) -> r[list[FlextDbOracleModels.DbOracle.OperationRecord]]:
        """Get tracked operations."""
        return r[list[FlextDbOracleModels.DbOracle.OperationRecord]].ok(
            self._operations.copy()
        )

    def get_plugin(self, _name: str) -> r[object]:
        """Get plugin data from local service registry."""
        if not _name:
            return r[object].fail("Plugin name is required")
        try:
            _ = import_module("flext_plugin.api")
        except ModuleNotFoundError:
            return r[object].fail(
                "flext-plugin integration unavailable; install flext-plugin"
            )
        if _name not in self._plugins:
            return r[object].fail(f"Plugin '{_name}' not found")
        return r[object].ok(self._plugins[_name])

    def get_primary_key_columns(
        self, table_name: str, schema_name: str | None = None
    ) -> r[list[str]]:
        """Alias for get_primary_keys."""
        return self.get_primary_keys(table_name, schema_name)

    def get_primary_keys(
        self, table_name: str, schema: str | None = None
    ) -> r[list[str]]:
        """Get primary key column names for specified table."""

        def _fetch_keys() -> list[str]:
            if schema:
                sql = "\n                SELECT column_name\n                FROM all_constraints c, all_cons_columns cc\n                WHERE c.constraint_type = 'P'\n                AND c.constraint_name = cc.constraint_name\n                AND c.table_name = UPPER(:table_name)\n                AND c.owner = UPPER(:schema)\n                ORDER BY cc.position\n                "
                params = m.ConfigMap(root={"table_name": table_name, "schema": schema})
            else:
                sql = "\n                SELECT column_name\n                FROM user_constraints c, user_cons_columns cc\n                WHERE c.constraint_type = 'P'\n                AND c.constraint_name = cc.constraint_name\n                AND c.table_name = UPPER(:table_name)\n                ORDER BY cc.position\n                "
                params = m.ConfigMap(root={"table_name": table_name})
            query_result = self.execute_query(sql, params)
            if query_result.is_failure:
                raise RuntimeError(query_result.error or "Query execution failed")
            return [str(row.root["column_name"]) for row in query_result.value]

        return u.try_(
            _fetch_keys,
            catch=(
                OracleDatabaseError,
                OracleInterfaceError,
                ConnectionError,
                SQLAlchemyDatabaseError,
                SQLAlchemyOperationalError,
                SQLAlchemyError,
                OSError,
                RuntimeError,
            ),
        ).map_error(lambda e: f"Failed to get primary keys: {e}")

    def get_schemas(self) -> r[list[str]]:
        """Get list of Oracle schemas."""
        sql = "SELECT username as schema_name FROM all_users WHERE username NOT IN ('SYS', 'SYSTEM', 'ANONYMOUS', 'XDB', 'CTXSYS', 'MDSYS', 'WMSYS') ORDER BY username"
        return self.execute_query(sql).map(
            lambda rows: [str(row.root["schema_name"]) for row in rows]
        )

    def get_table_metadata(
        self, table_name: str, schema: str | None = None
    ) -> r[FlextDbOracleModels.DbOracle.TableMetadata]:
        """Get complete table metadata."""

        def _fetch_metadata() -> FlextDbOracleModels.DbOracle.TableMetadata:
            columns_result = self.get_columns(table_name, schema)
            if columns_result.is_failure:
                raise RuntimeError(columns_result.error or "Failed to get columns")

            pk_result = self.get_primary_keys(table_name, schema)
            if pk_result.is_failure:
                raise RuntimeError(pk_result.error or "Failed to get primary keys")

            return FlextDbOracleModels.DbOracle.TableMetadata(
                table_name=table_name,
                schema_name=schema or "",
                columns=[
                    FlextDbOracleModels.DbOracle.ColumnMetadata(
                        name=column.name,
                        data_type=column.data_type,
                        nullable=column.nullable,
                    )
                    for column in columns_result.value
                ],
                primary_keys=pk_result.value,
            )

        return u.try_(
            _fetch_metadata,
            catch=(
                OracleDatabaseError,
                OracleInterfaceError,
                ConnectionError,
                SQLAlchemyOperationalError,
                OSError,
                RuntimeError,
            ),
        ).map_error(lambda e: f"Failed to get table metadata: {e}")

    def get_table_row_count(
        self, table_name: str, schema_name: str | None = None
    ) -> r[int]:
        """Get row count - simplified."""

        def _fetch_count() -> int:
            schema = f"{schema_name}." if schema_name else ""
            sql = f"SELECT COUNT(*) as count FROM {schema}{table_name}"
            query_result = self.execute_query(sql)
            if query_result.is_failure:
                raise RuntimeError(query_result.error or "Query execution failed")
            return self._parse_count_from_rows(query_result.value)

        return u.try_(
            _fetch_count,
            catch=(
                OracleDatabaseError,
                OracleInterfaceError,
                ConnectionError,
                SQLAlchemyOperationalError,
                OSError,
                RuntimeError,
            ),
        ).map_error(lambda e: f"Failed to get row count: {e}")

    def get_tables(self, schema: str | None = None) -> r[list[str]]:
        """Get list of tables in Oracle schema."""
        if schema:
            sql = "SELECT table_name FROM all_tables WHERE owner = UPPER(:schema_name) ORDER BY table_name"
            params: m.ConfigMap | None = m.ConfigMap(root={"schema_name": schema})
        else:
            sql = "SELECT table_name FROM user_tables ORDER BY table_name"
            params = None
        return self.execute_query(sql, params).map(
            lambda rows: [str(row.root["table_name"]) for row in rows]
        )

    def health_check(self) -> r[FlextDbOracleModels.DbOracle.HealthStatus]:
        """Perform health check."""
        return r[FlextDbOracleModels.DbOracle.HealthStatus].ok(
            FlextDbOracleModels.DbOracle.HealthStatus(
                status="healthy" if self.is_connected() else "unhealthy",
                timestamp=self._get_current_timestamp(),
                service="oracle",
                database=self._db_config.service_name,
                metrics={
                    "connected": self.is_connected(),
                    "host": self._db_config.host,
                    "port": self._db_config.port,
                },
            )
        )

    def is_connected(self) -> bool:
        """Check if connected to Oracle database."""
        return self._engine is not None

    def list_plugins(self) -> r[m.ConfigMap]:
        """List plugin names from local service registry."""
        try:
            _ = import_module("flext_plugin.api")
        except ModuleNotFoundError:
            return r[m.ConfigMap].fail(
                "flext-plugin integration unavailable; install flext-plugin"
            )
        plugin_names = list(self._plugins.keys())
        return r[m.ConfigMap].ok(m.ConfigMap(root=dict.fromkeys(plugin_names, True)))

    def map_singer_schema(
        self,
        singer_schema: FlextDbOracleModels.DbOracle.SingerSchema
        | object
        | Mapping[str, object],
    ) -> r[FlextDbOracleModels.DbOracle.TypeMapping]:
        """Map Singer schema to Oracle types - simplified."""
        raw_properties: object | None = None
        if isinstance(singer_schema, FlextDbOracleModels.DbOracle.SingerSchema):
            schema_model = singer_schema
        else:
            if not isinstance(singer_schema, Mapping):
                return r[FlextDbOracleModels.DbOracle.TypeMapping].fail(
                    "Singer schema must be a mapping"
                )
            raw_properties = singer_schema.get("properties", {})
            if not isinstance(raw_properties, Mapping):
                return r[FlextDbOracleModels.DbOracle.TypeMapping].fail(
                    "Singer schema properties must be a mapping"
                )
            normalized_properties: dict[
                str, FlextDbOracleModels.DbOracle.SingerField
            ] = {}
            for field_name, field_def in raw_properties.items():
                if isinstance(field_def, Mapping):
                    field_type = field_def.get("type", "string")
                    if isinstance(field_type, str):
                        normalized_properties[str(field_name)] = (
                            FlextDbOracleModels.DbOracle.SingerField(type=field_type)
                        )
                    else:
                        normalized_properties[str(field_name)] = (
                            FlextDbOracleModels.DbOracle.SingerField(type="string")
                        )
                else:
                    normalized_properties[str(field_name)] = (
                        FlextDbOracleModels.DbOracle.SingerField(type="string")
                    )
            schema_model = FlextDbOracleModels.DbOracle.SingerSchema.model_validate({
                "properties": normalized_properties
            })
        mapping = m.ConfigMap(root={})
        for field_name, field_def in schema_model.properties.items():
            raw_field = (
                raw_properties.get(field_name)
                if isinstance(raw_properties, Mapping)
                else None
            )
            format_value = (
                raw_field.get("format") if isinstance(raw_field, Mapping) else None
            )
            format_hint = format_value if isinstance(format_value, str) else None
            conversion = self.convert_singer_type(field_def.type, format_hint)
            if conversion.is_success:
                mapping.root[field_name] = conversion.value
        normalized_mapping = {key: str(value) for key, value in mapping.root.items()}
        type_mapping = FlextDbOracleModels.DbOracle.TypeMapping.model_validate({
            "mapping": normalized_mapping
        })
        return r[FlextDbOracleModels.DbOracle.TypeMapping].ok(type_mapping)

    def record_metric(
        self,
        _name: str,
        _value: float,
        _tags: m.ConfigMap | object | None = None,
    ) -> r[bool]:
        """Record metric through flext-observability when available."""
        if not _name:
            return r[bool].fail("Metric name is required")
        try:
            observability_module = import_module("flext_observability")
        except ModuleNotFoundError:
            return r[bool].fail(
                "flext-observability integration unavailable; install flext-observability"
            )
        metric_factory = getattr(observability_module, "flext_metric", None)
        if not callable(metric_factory):
            return r[bool].fail("flext-observability does not expose flext_metric")
        typed_tags = (
            _tags
            if isinstance(_tags, m.ConfigMap) or _tags is None
            else m.ConfigMap(_tags)
        )
        tags_payload = (
            typed_tags.root if typed_tags is not None else dict[str, object]()
        )
        metric_result = metric_factory(
            name=_name, value=_value, tags=m.Dict(tags_payload)
        )
        if getattr(metric_result, "is_failure", False):
            return r[bool].fail(
                getattr(
                    metric_result, "error", "Metric recording failed in observability"
                )
            )
        self._metrics[_name] = {
            "value": _value,
            "tags": tags_payload,
            "timestamp": self._get_current_timestamp(),
        }
        return r[bool].ok(True)

    def register_plugin(self, _name: str, _plugin: object) -> r[bool]:
        """Register plugin via flext-plugin when available."""
        if not _name:
            return r[bool].fail("Plugin name is required")
        plugin_payload = _validate_config_map(_plugin)
        if plugin_payload is None:
            return r[bool].fail("Plugin payload must be a mapping")
        try:
            _ = import_module("flext_plugin.api")
            _ = import_module("flext_plugin.models")
        except ModuleNotFoundError:
            return r[bool].fail(
                "flext-plugin integration unavailable; install flext-plugin"
            )
        payload = dict(plugin_payload.root)
        payload["name"] = str(payload.get("name", _name))
        self._plugins[_name] = payload
        return r[bool].ok(True)

    def test_connection(self) -> r[bool]:
        """Test Oracle database connection."""
        engine_result = self._get_engine()
        if engine_result.is_failure:
            return r[bool].fail("Not connected to database")
        try:
            connect_ctx = _engine_connect(engine_result.value)
            conn = _context_enter(connect_ctx)
            try:
                _ = _connection_execute(conn, _sqlalchemy_text("SELECT 1 FROM dual"))
            finally:
                _context_exit(connect_ctx)
            return r[bool].ok(True)
        except (
            OracleDatabaseError,
            OracleInterfaceError,
            ConnectionError,
            SQLAlchemyDatabaseError,
            SQLAlchemyOperationalError,
            SQLAlchemyError,
            OSError,
        ) as e:
            return r[bool].fail(f"Connection test failed: {e}")

    def track_operation(
        self,
        operation_type: str = "",
        duration: float = 0.0,
        *,
        success: bool = True,
        metadata: m.ConfigMap | object | None = None,
    ) -> r[bool]:
        """Track database operation for monitoring."""

        def _track() -> bool:
            metadata_value = (
                metadata
                if isinstance(metadata, m.ConfigMap)
                else m.ConfigMap(metadata or {})
            )
            operation = FlextDbOracleModels.DbOracle.OperationRecord(
                operation_type=operation_type,
                duration=duration,
                success=success,
                metadata_info=str(metadata_value),
                timestamp=self._get_current_timestamp(),
            )
            self._operations.append(operation)
            return True

        return u.try_(
            _track,
            catch=(
                OracleDatabaseError,
                OracleInterfaceError,
                ConnectionError,
                SQLAlchemyOperationalError,
                OSError,
            ),
        ).map_error(lambda e: f"Failed to track operation: {e}")

    def transaction(self) -> Generator[object]:
        """Get transaction context for database operations."""
        engine = self._engine
        if engine is None:
            msg = "No database connection established"
            raise RuntimeError(msg)
        transaction_ctx = _engine_begin(engine)
        transaction = _context_enter(transaction_ctx)
        try:
            yield transaction
        finally:
            _context_exit(transaction_ctx)

    def unregister_plugin(self, _name: str) -> r[bool]:
        """Unregister plugin from local service registry."""
        if not _name:
            return r[bool].fail("Plugin name is required")
        try:
            _ = import_module("flext_plugin.api")
        except ModuleNotFoundError:
            return r[bool].fail(
                "flext-plugin integration unavailable; install flext-plugin"
            )
        if _name not in self._plugins:
            return r[bool].fail(f"Plugin '{_name}' not found")
        self._plugins.pop(_name)
        return r[bool].ok(True)

    def _build_connection_url(self) -> r[str]:
        """Build Oracle connection URL from configuration."""
        try:
            password = self._db_config.password
            if not password:
                return r[str].fail("Password is required for database connection")
            encoded_password = quote_plus(str(password).encode())
            service_name = self._db_config.service_name
            base = f"oracle+oracledb://{self._db_config.username}:{encoded_password}@{self._db_config.host}:{self._db_config.port}"
            url = f"{base}/?service_name={service_name}"
            return r[str].ok(url)
        except (
            OracleDatabaseError,
            OracleInterfaceError,
            ConnectionError,
            SQLAlchemyDatabaseError,
            SQLAlchemyOperationalError,
            SQLAlchemyError,
            OSError,
        ) as e:
            return r[str].fail(f"Failed to build connection URL: {e}")

    def _extract_mapping_rows(self, mapping_result: object) -> list[object]:
        """Extract all SQLAlchemy mapping rows from a mapping result."""
        all_method = getattr(mapping_result, "all", None)
        if not callable(all_method):
            return []
        rows = all_method()
        return _extract_object_rows(rows)

    def _get_current_timestamp(self) -> str:
        """Get current timestamp for operation tracking."""
        return str(int(time.time()))

    def _get_engine(self) -> r[object]:
        """Get database engine."""
        if not self._engine or not self.is_connected():
            return r[object].fail("Not connected to database")
        return r[object].ok(self._engine)

    def _normalize_query_rows(self, query_result: object) -> list[m.Dict]:
        """Normalize SQLAlchemy query result rows into typed mapping models."""
        mappings_method = getattr(query_result, "mappings", None)
        if not callable(mappings_method):
            return []
        mapping_result = mappings_method()
        return [
            self._normalize_row(row)
            for row in self._extract_mapping_rows(mapping_result)
        ]

    def _normalize_row(self, row: Mapping[str, object] | object) -> m.Dict:
        """Normalize a single SQLAlchemy mapping row into a typed map."""
        if isinstance(row, Mapping):
            validated_mapping = _validate_config_map(row)
        else:
            validated_mapping = _validate_config_map(getattr(row, "_mapping", None))
        if validated_mapping is None:
            return m.Dict(root={})
        return m.Dict(
            root={str(key): value for key, value in validated_mapping.root.items()}
        )

    def _parse_count_from_rows(self, rows: list[m.Dict]) -> int:
        """Parse COUNT(*) value from normalized query rows."""
        if not rows:
            return 0
        count_value = rows[0].root.get("count")
        if count_value is None:
            return 0
        return _parse_count_value(count_value)


__all__ = ["FlextDbOracleServices"]
