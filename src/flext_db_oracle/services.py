"""Generic Oracle Database services delegating to flext-core and SQLAlchemy.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import contextlib
import hashlib
import time
from collections.abc import (
    Generator,
    Mapping,
    MutableMapping,
    MutableSequence,
    Sequence,
)
from contextlib import contextmanager
from datetime import UTC, datetime
from importlib import import_module
from typing import Self, override
from urllib.parse import quote_plus

import oracledb
from flext_core import r, s
from pydantic import PrivateAttr, RootModel, TypeAdapter, ValidationError
from sqlalchemy import (
    Connection as SAConnection,
    Engine as SAEngine,
    TextClause,
    create_engine,
    text,
)
from sqlalchemy.engine import CursorResult
from sqlalchemy.exc import (
    DatabaseError as SQLAlchemyDatabaseError,
    OperationalError as SQLAlchemyOperationalError,
    SQLAlchemyError,
)

from flext_db_oracle import c, t, u
from flext_db_oracle.models import FlextDbOracleModels
from flext_db_oracle.settings import FlextDbOracleSettings

OracleDatabaseError: type[Exception] = oracledb.DatabaseError
OracleInterfaceError: type[Exception] = oracledb.InterfaceError


class _CountValue(RootModel[int | str]):
    """Pydantic root model for count value (int or numeric string)."""

    root: int | str


_STRING_LIST_ADAPTER = TypeAdapter(Sequence[str])


def _validate_config_map(value: t.ContainerValue) -> t.ConfigMap | None:
    """Validate arbitrary mapping input as ConfigMap."""
    if not isinstance(value, dict):
        return None
    try:
        return t.ConfigMap.model_validate({"root": value})
    except ValidationError:
        return None


def _normalize_params(params: t.ConfigMap | None) -> t.ConfigMap:
    """Normalize optional parameters into ConfigMap."""
    if params is not None:
        return params
    return t.ConfigMap(root={})


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
        validated = _CountValue.model_validate(value).root
    except ValidationError:
        return 0
    try:
        return int(validated)
    except (TypeError, ValueError):
        return 0


def _normalize_singer_type(value: str | Sequence[str]) -> str:
    """Normalize Singer type input to a single string value."""
    try:
        values = _STRING_LIST_ADAPTER.validate_python(value)
    except ValidationError:
        return str(value)
    return values[0] if values else "string"


def _sqlalchemy_create_engine(url: str) -> SAEngine:
    """Create SQLAlchemy engine."""
    return create_engine(url, pool_pre_ping=True, pool_recycle=3600, echo=False)


def _sqlalchemy_text(statement: str) -> TextClause:
    """Build SQL text t.NormalizedValue."""
    return text(statement)


def _engine_connect(engine: SAEngine) -> SAConnection:
    """Open connection context manager from engine."""
    return engine.connect()


def _engine_begin(engine: SAEngine) -> contextlib.AbstractContextManager[SAConnection]:
    """Open transaction context manager from engine."""
    return engine.begin()


def _context_enter[T](context_manager: contextlib.AbstractContextManager[T]) -> T:
    """Enter dynamic context manager and return inner t.NormalizedValue."""
    return context_manager.__enter__()


def _context_exit(
    context_manager: contextlib.AbstractContextManager[SAConnection],
) -> None:
    """Exit dynamic context manager safely."""
    context_manager.__exit__(None, None, None)


def _engine_dispose(engine: SAEngine) -> None:
    """Dispose engine resources."""
    engine.dispose()


def _connection_execute(
    connection: SAConnection,
    statement: TextClause,
    parameters: t.ConfigMap | None = None,
) -> CursorResult[tuple[t.ContainerValue, ...]]:
    """Execute statement on SQL connection."""
    normalized_params = _normalize_params(parameters)
    return connection.execute(statement, normalized_params.root)


class FlextDbOracleServices(s[FlextDbOracleSettings]):
    """Generic Oracle database services using flext-core patterns."""

    _db_config: FlextDbOracleSettings | None = PrivateAttr(default=None)

    def __init__(self, config: FlextDbOracleSettings) -> None:
        """Initialize with configuration."""
        super().__init__()
        self._db_config = config
        self._config = config
        self._engine: SAEngine | None = None
        self._operations: MutableSequence[
            FlextDbOracleModels.DbOracle.OperationRecord
        ] = []
        self._plugins: MutableMapping[str, t.ContainerValue] = {}
        self._metrics: MutableMapping[str, t.ContainerValue] = {}

    @property
    def db_config(self) -> FlextDbOracleSettings:
        """Return initialized Oracle database configuration."""
        config = self._db_config
        if config is None:
            msg = "Database configuration not initialized"
            raise RuntimeError(msg)
        return config

    def build_create_index_statement(self, _config: t.ContainerValue) -> r[str]:
        """Build Oracle CREATE INDEX statement from configuration."""
        try:
            if not isinstance(_config, Mapping):
                return r[str].fail("Invalid CREATE INDEX config payload")
            raw_columns = _config.get("columns", [])
            columns_list: Sequence[str] = (
                [str(col) for col in raw_columns]
                if isinstance(raw_columns, list)
                else []
            )
            raw_parallel = _config.get("parallel", 1)
            parallel_value = (
                int(raw_parallel) if isinstance(raw_parallel, (int, str)) else 1
            )
            payload = {
                "table_name": str(_config.get("table_name", "")),
                "index_name": str(_config.get("index_name", "")),
                "columns": columns_list,
                "unique": bool(_config.get("unique", False)),
                "schema_name": str(_config.get("schema_name", "")),
                "tablespace": str(_config.get("tablespace", "")),
                "parallel": parallel_value,
            }
            config = FlextDbOracleModels.DbOracle.CreateIndexConfig.model_validate(
                payload,
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
        self,
        table_name: str,
        where_columns: Sequence[str],
        schema: str | None = None,
    ) -> r[str]:
        """Build DELETE statement - simplified."""
        wheres = " AND ".join(f"{col} = :{col}" for col in where_columns)
        schema_prefix = f"{schema}." if schema else ""
        sql = f"DELETE FROM {schema_prefix}{table_name} WHERE {wheres}"
        return r[str].ok(sql)

    def build_insert_statement(
        self,
        table_name: str,
        columns: Sequence[str],
        schema: str | None = None,
        returning_columns: Sequence[str] | None = None,
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
        columns: Sequence[str] | None = None,
        conditions: t.ConfigMap | t.ContainerValueMapping | None = None,
        schema_name: str | None = None,
    ) -> r[str]:
        """Build SELECT query - simplified implementation."""
        typed_conditions = (
            conditions
            if isinstance(conditions, t.ConfigMap) or conditions is None
            else t.ConfigMap.model_validate({"root": dict(conditions)})
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
        set_columns: Sequence[str],
        where_columns: Sequence[str],
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
            self.logger.info(f"Connected to Oracle database: {self.db_config.host}")
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
            local_host = self.db_config.host in {
                "localhost",
                c.DbOracle.Platform.LOCALHOST_IP,
            }
            default_port = c.DbOracle.Connection.DEFAULT_PORT
            if local_host and self.db_config.port != default_port:
                self.db_config.port = default_port
                retry_url_result = self._build_connection_url()
                if retry_url_result.is_success:
                    self._engine = _sqlalchemy_create_engine(retry_url_result.value)
                    try:
                        connect_ctx = _engine_connect(self._engine)
                        conn = _context_enter(connect_ctx)
                        try:
                            _ = _connection_execute(
                                conn,
                                _sqlalchemy_text("SELECT 1 FROM dual"),
                            )
                        finally:
                            _context_exit(connect_ctx)
                        self.logger.info(
                            f"Connected to Oracle database: {self.db_config.host}",
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
        self,
        singer_type: str | Sequence[str] = "string",
        _format_hint: str | None = None,
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
        columns: Sequence[
            FlextDbOracleModels.DbOracle.Column | t.ContainerValueMapping
        ],
        schema: str | None = None,
    ) -> r[str]:
        """Generate CREATE TABLE DDL - simplified."""
        col_defs: Sequence[str] = []
        primary_keys: Sequence[str] = []
        for col in columns:
            if isinstance(col, FlextDbOracleModels.DbOracle.Column):
                name = col.name or c.IDENTIFIER_UNKNOWN
                data_type = col.data_type or "VARCHAR2(255)"
                nullable = "" if col.nullable else " NOT NULL"
                if col.primary_key:
                    primary_keys.append(name)
            elif isinstance(col, Mapping):
                name_value = col.get("name") or col.get("column_name")
                data_type_value = col.get("data_type")
                nullable_value = col.get("nullable", True)
                name = (
                    str(name_value) if name_value is not None else c.IDENTIFIER_UNKNOWN
                )
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
            return r[FlextDbOracleSettings].ok(self.db_config)
        return r[FlextDbOracleSettings].fail(
            test_result.error or "Connection test failed",
        )

    def execute_many(
        self,
        sql: str,
        params_list: Sequence[Mapping[str, t.ContainerValue] | t.ConfigMap],
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
                        if isinstance(params, t.ConfigMap)
                        else t.ConfigMap.model_validate({"root": dict(params)})
                    )
                    result = _connection_execute(
                        conn,
                        _sqlalchemy_text(sql),
                        typed_params,
                    )
                    total_affected += max(result.rowcount, 0)
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
        self,
        sql: str,
        params: t.ConfigMap | None = None,
    ) -> r[Sequence[t.Dict]]:
        """Execute SQL query and return results."""
        if not self.is_connected():
            return r[Sequence[t.Dict]].fail("Not connected to database")
        engine_result = self._get_engine()
        if engine_result.is_failure:
            return r[Sequence[t.Dict]].fail(
                engine_result.error or "Failed to get database engine",
            )
        try:
            connect_ctx = _engine_connect(engine_result.value)
            conn = _context_enter(connect_ctx)
            try:
                result = _connection_execute(conn, _sqlalchemy_text(sql), params)
                rows: Sequence[t.Dict] = self._normalize_query_rows(result)
                return r[Sequence[t.Dict]].ok(rows)
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
            return r[Sequence[t.Dict]].fail(f"Query execution failed: {e}")

    def execute_statement(self, sql: str, params: t.ConfigMap | None = None) -> r[int]:
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
                rowcount = max(result.rowcount, 0)
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
        self,
        sql: str,
        params: t.ConfigMap | None = None,
    ) -> r[t.Dict | None]:
        """Execute query and return first result."""
        return self.execute_query(sql, params).map(
            lambda rows: rows[0] if rows else None,
        )

    def generate_query_hash(
        self,
        sql: str = "",
        params: t.ConfigMap | t.ContainerValueMapping | None = None,
    ) -> r[str]:
        """Generate query hash - simplified."""
        typed_params = (
            params
            if isinstance(params, t.ConfigMap) or params is None
            else t.ConfigMap.model_validate({"root": dict(params)})
        )
        hash_input = f"{sql}_{typed_params!s}"
        return r[str].ok(hashlib.sha256(hash_input.encode()).hexdigest()[:16])

    def get_columns(
        self,
        table_name: str,
        schema_name: str | None = None,
    ) -> r[Sequence[FlextDbOracleModels.DbOracle.Column]]:
        """Get column information for Oracle table."""
        if schema_name:
            sql = "\nSELECT column_name, data_type, data_length, data_precision, data_scale, nullable\nFROM all_tab_columns\nWHERE table_name = UPPER(:table_name) AND owner = UPPER(:schema_name)\nORDER BY column_id\n"
            params = t.ConfigMap(
                root={"table_name": table_name, "schema_name": schema_name},
            )
        else:
            sql = "\nSELECT column_name, data_type, data_length, data_precision, data_scale, nullable\nFROM user_tab_columns\nWHERE table_name = UPPER(:table_name)\nORDER BY column_id\n"
            params = t.ConfigMap(root={"table_name": table_name})
        return self.execute_query(sql, params).map(
            lambda rows: [
                FlextDbOracleModels.DbOracle.Column(
                    name=str(row.root.get("column_name", "")),
                    data_type=str(row.root.get("data_type", "")),
                    nullable=str(row.root.get("nullable", "Y")) == "Y",
                    primary_key=False,
                    default_value=str(row.root.get("data_default", "")),
                )
                for row in rows
            ],
        )

    @contextmanager
    def get_connection(self) -> Generator[SAConnection]:
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
        now = datetime.now(UTC)
        return r[FlextDbOracleModels.DbOracle.ConnectionStatus].ok(
            FlextDbOracleModels.DbOracle.ConnectionStatus(
                is_connected=self.is_connected(),
                last_check=now,
                connection_time=0.0,
                last_activity=now,
                session_id="",
                host=self.db_config.host,
                port=self.db_config.port,
                service_name=self.db_config.service_name,
                username=self.db_config.username,
                db_version="",
                error_message="" if self.is_connected() else "Connection unavailable",
            ),
        )

    def get_metrics(self) -> r[FlextDbOracleModels.DbOracle.HealthStatus]:
        """Get metrics status with explicit observability integration check."""
        try:
            observability_module = import_module("flext_observability")
        except ModuleNotFoundError:
            return r[FlextDbOracleModels.DbOracle.HealthStatus].fail(
                "flext-observability integration unavailable; install flext-observability",
            )
        metric_factory = getattr(observability_module, "flext_metric", None)
        if not callable(metric_factory):
            core_module = import_module("flext_observability._core")
            metric_factory = getattr(core_module, "flext_metric", None)
        if not callable(metric_factory):
            return r[FlextDbOracleModels.DbOracle.HealthStatus].fail(
                "flext-observability does not expose flext_metric",
            )
        status = "connected" if self.is_connected() else "disconnected"
        metrics_payload: Mapping[str, str] = {
            metric_name: str(metric_value)
            for metric_name, metric_value in self._metrics.items()
        }
        return r[FlextDbOracleModels.DbOracle.HealthStatus].ok(
            FlextDbOracleModels.DbOracle.HealthStatus.model_validate({
                "status": f"{status}_with_observability",
                "timestamp": self._get_current_timestamp(),
                "service": "oracle",
                "database": self.db_config.service_name,
                "metrics": metrics_payload,
            }),
        )

    def get_operations(
        self,
    ) -> r[Sequence[FlextDbOracleModels.DbOracle.OperationRecord]]:
        """Get tracked operations."""
        return r[Sequence[FlextDbOracleModels.DbOracle.OperationRecord]].ok(
            self._operations.copy(),
        )

    def get_plugin(self, _name: str) -> r[t.ContainerValue]:
        """Get plugin data from local service registry."""
        if not _name:
            return r[t.ContainerValue].fail("Plugin name is required")
        try:
            _ = import_module("flext_plugin.api")
        except ModuleNotFoundError:
            return r[t.ContainerValue].fail(
                "flext-plugin integration unavailable; install flext-plugin"
            )
        if _name not in self._plugins:
            return r[t.ContainerValue].fail(f"Plugin '{_name}' not found")
        return r[t.ContainerValue].ok(self._plugins[_name])

    def get_primary_key_columns(
        self,
        table_name: str,
        schema_name: str | None = None,
    ) -> r[Sequence[str]]:
        """Alias for get_primary_keys."""
        return self.get_primary_keys(table_name, schema_name)

    def get_primary_keys(
        self,
        table_name: str,
        schema: str | None = None,
    ) -> r[Sequence[str]]:
        """Get primary key column names for specified table."""

        def _fetch_keys() -> Sequence[str]:
            if schema:
                sql = "\n                SELECT column_name\n                FROM all_constraints c, all_cons_columns cc\n                WHERE c.constraint_type = 'P'\n                AND c.constraint_name = cc.constraint_name\n                AND c.table_name = UPPER(:table_name)\n                AND c.owner = UPPER(:schema)\n                ORDER BY cc.position\n                "
                params = t.ConfigMap(root={"table_name": table_name, "schema": schema})
            else:
                sql = "\n                SELECT column_name\n                FROM user_constraints c, user_cons_columns cc\n                WHERE c.constraint_type = 'P'\n                AND c.constraint_name = cc.constraint_name\n                AND c.table_name = UPPER(:table_name)\n                ORDER BY cc.position\n                "
                params = t.ConfigMap(root={"table_name": table_name})
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

    def get_schemas(self) -> r[Sequence[str]]:
        """Get list of Oracle schemas."""
        sql = "SELECT username as schema_name FROM all_users WHERE username NOT IN ('SYS', 'SYSTEM', 'ANONYMOUS', 'XDB', 'CTXSYS', 'MDSYS', 'WMSYS') ORDER BY username"
        return self.execute_query(sql).map(
            lambda rows: [str(row.root["schema_name"]) for row in rows],
        )

    def get_table_metadata(
        self,
        table_name: str,
        schema: str | None = None,
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
        self,
        table_name: str,
        schema_name: str | None = None,
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

    def get_tables(self, schema: str | None = None) -> r[Sequence[str]]:
        """Get list of tables in Oracle schema."""
        if schema:
            sql = "SELECT table_name FROM all_tables WHERE owner = UPPER(:schema_name) ORDER BY table_name"
            params: t.ConfigMap | None = t.ConfigMap(root={"schema_name": schema})
        else:
            sql = "SELECT table_name FROM user_tables ORDER BY table_name"
            params = None
        return self.execute_query(sql, params).map(
            lambda rows: [str(row.root["table_name"]) for row in rows],
        )

    def health_check(self) -> r[FlextDbOracleModels.DbOracle.HealthStatus]:
        """Perform health check."""
        return r[FlextDbOracleModels.DbOracle.HealthStatus].ok(
            FlextDbOracleModels.DbOracle.HealthStatus(
                status="healthy" if self.is_connected() else "unhealthy",
                timestamp=self._get_current_timestamp(),
                service="oracle",
                database=self.db_config.service_name,
                metrics={
                    "connected": self.is_connected(),
                    "host": self.db_config.host,
                    "port": self.db_config.port,
                },
            ),
        )

    def is_connected(self) -> bool:
        """Check if connected to Oracle database."""
        return self._engine is not None

    def list_plugins(self) -> r[t.ConfigMap]:
        """List plugin names from local service registry."""
        try:
            _ = import_module("flext_plugin.api")
        except ModuleNotFoundError:
            return r[t.ConfigMap].fail(
                "flext-plugin integration unavailable; install flext-plugin",
            )
        plugin_names = list(self._plugins.keys())
        return r[t.ConfigMap].ok(t.ConfigMap(root=dict.fromkeys(plugin_names, True)))

    def map_singer_schema(
        self,
        singer_schema: FlextDbOracleModels.DbOracle.SingerSchema
        | t.ContainerValueMapping,
    ) -> r[FlextDbOracleModels.DbOracle.TypeMapping]:
        """Map Singer schema to Oracle types - simplified."""
        raw_properties: Mapping[str, t.ContainerValue] | None = None
        if isinstance(singer_schema, FlextDbOracleModels.DbOracle.SingerSchema):
            schema_model = singer_schema
        else:
            raw_props_value = singer_schema.get("properties", {})
            if not isinstance(raw_props_value, dict):
                return r[FlextDbOracleModels.DbOracle.TypeMapping].fail(
                    "Singer schema properties must be a mapping",
                )
            raw_properties = raw_props_value
            normalized_properties: Mapping[
                str,
                FlextDbOracleModels.DbOracle.SingerField,
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
                "properties": normalized_properties,
            })
        mapping = t.ConfigMap(root={})
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
            "mapping": normalized_mapping,
        })
        return r[FlextDbOracleModels.DbOracle.TypeMapping].ok(type_mapping)

    def record_metric(
        self,
        _name: str,
        _value: float,
        _tags: t.ConfigMap | t.ContainerValueMapping | None = None,
    ) -> r[bool]:
        """Record metric through flext-observability when available."""
        if not _name:
            return r[bool].fail("Metric name is required")
        try:
            observability_module = import_module("flext_observability")
        except ModuleNotFoundError:
            return r[bool].fail(
                "flext-observability integration unavailable; install flext-observability",
            )
        metric_factory = getattr(observability_module, "flext_metric", None)
        if not callable(metric_factory):
            core_module = import_module("flext_observability._core")
            metric_factory = getattr(core_module, "flext_metric", None)
        if not callable(metric_factory):
            return r[bool].fail("flext-observability does not expose flext_metric")
        typed_tags = (
            _tags
            if isinstance(_tags, t.ConfigMap) or _tags is None
            else t.ConfigMap.model_validate({"root": dict(_tags)})
        )
        tags_str: Mapping[str, str] = (
            {str(k): str(v) for k, v in typed_tags.root.items()}
            if typed_tags is not None
            else {}
        )
        metric_result = metric_factory(
            name=_name,
            value=_value,
            tags=t.Dict.model_validate({"root": tags_str}),
        )
        if getattr(metric_result, "is_failure", False):
            return r[bool].fail(
                getattr(
                    metric_result,
                    "error",
                    "Metric recording failed in observability",
                ),
            )
        self._metrics[_name] = self._get_current_timestamp()
        return r[bool].ok(True)

    def register_plugin(self, _name: str, _plugin: t.ContainerValue) -> r[bool]:
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
                "flext-plugin integration unavailable; install flext-plugin",
            )
        self._plugins[_name] = _name
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
        metadata: t.ConfigMap | t.ContainerValueMapping | None = None,
    ) -> r[bool]:
        """Track database operation for monitoring."""

        def _track() -> bool:
            metadata_value = (
                metadata
                if isinstance(metadata, t.ConfigMap)
                else t.ConfigMap.model_validate({
                    "root": dict(metadata) if metadata else {}
                })
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

    def transaction(self) -> Generator[SAConnection]:
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
                "flext-plugin integration unavailable; install flext-plugin",
            )
        if _name not in self._plugins:
            return r[bool].fail(f"Plugin '{_name}' not found")
        self._plugins.pop(_name)
        return r[bool].ok(True)

    def _build_connection_url(self) -> r[str]:
        """Build Oracle connection URL from configuration."""
        try:
            password = self.db_config.password
            if not password:
                return r[str].fail("Password is required for database connection")
            encoded_password = quote_plus(str(password).encode())
            service_name = self.db_config.service_name
            base = f"oracle+oracledb://{self.db_config.username}:{encoded_password}@{self.db_config.host}:{self.db_config.port}"
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

    def _get_current_timestamp(self) -> str:
        """Get current timestamp for operation tracking."""
        return str(int(time.time()))

    def _get_engine(self) -> r[SAEngine]:
        """Get database engine."""
        if not self._engine or not self.is_connected():
            return r[SAEngine].fail("Not connected to database")
        return r[SAEngine].ok(self._engine)

    def _normalize_query_rows(
        self, query_result: CursorResult[tuple[t.ContainerValue, ...]]
    ) -> Sequence[t.Dict]:
        """Normalize SQLAlchemy query result rows into typed mapping models."""
        mapping_result = query_result.mappings()
        rows = mapping_result.all()
        result: Sequence[t.Dict] = []
        for row in rows:
            row_dict: Mapping[str, str] = {
                str(key): str(val) for key, val in dict(row).items()
            }
            result.append(t.Dict.model_validate({"root": row_dict}))
        return result

    def _normalize_row(self, row: Mapping[str, t.ContainerValue]) -> t.Dict:
        """Normalize a single SQLAlchemy mapping row into a typed map."""
        return t.Dict.model_validate(
            {"root": {str(key): value for key, value in row.items()}},
        )

    def _parse_count_from_rows(self, rows: Sequence[t.Dict]) -> int:
        """Parse COUNT(*) value from normalized query rows."""
        if not rows:
            return 0
        count_raw = rows[0].root.get("count")
        if count_raw is None:
            return 0
        count_str = str(count_raw)
        return _parse_count_value(count_str)


s = FlextDbOracleServices

__all__ = ["FlextDbOracleServices", "s"]
