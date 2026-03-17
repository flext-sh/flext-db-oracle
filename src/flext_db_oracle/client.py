"""Oracle Database client providing CLI and programmatic access.

This module provides the Oracle database client with CLI functionality
using FLEXT ecosystem patterns for database operations.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence
from types import ModuleType
from typing import override

import oracledb
from flext_core import FlextService, FlextSettings, p, r, u
from pydantic import TypeAdapter, ValidationError
from sqlalchemy.exc import OperationalError as SQLAlchemyOperationalError

from flext_db_oracle.api import FlextDbOracleApi
from flext_db_oracle.constants import c
from flext_db_oracle.settings import FlextDbOracleSettings
from flext_db_oracle.typings import t

OracleDatabaseError = oracledb.DatabaseError
OracleInterfaceError = oracledb.InterfaceError
_GENERAL_LIST_ADAPTER: TypeAdapter[list[t.Container]] = TypeAdapter(list[t.Container])
_CONFIG_DICT_ADAPTER: TypeAdapter[dict[str, t.ContainerValue]] = TypeAdapter(
    dict[str, t.ContainerValue]
)


def _validate_config_map(
    value: Mapping[str, t.ContainerValue] | t.ConfigMap,
) -> t.ConfigMap | None:
    """Validate generic mapping payload with Pydantic."""
    try:
        if isinstance(value, t.ConfigMap):
            return value
        return t.ConfigMap(root=dict(value))
    except ValidationError:
        return None


def _validate_general_list(value: t.ContainerValue) -> list[t.Container] | None:
    """Validate list payload with Pydantic."""
    return _GENERAL_LIST_ADAPTER.validate_python(value)


class FlextDbOracleClient(FlextService[FlextDbOracleSettings]):
    """Oracle Database CLI client with complete FLEXT ecosystem integration.

    This client provides command-line interface operations for Oracle Database
    management using the flext-db-oracle foundation API with full flext-core integration.
    """

    debug: bool = False
    current_connection: FlextDbOracleApi | None = None
    user_preferences: t.ConfigMap = t.ConfigMap(
        root={
            "default_output_format": "table",
            "show_execution_time": "True",
            "auto_confirm_operations": "False",
            "connection_timeout": 30,
            "query_limit": 1000,
        }
    )

    def __init__(
        self,
        *,
        debug: bool = False,
        config_type: type[FlextSettings] | None = None,
        config_overrides: dict[str, t.Scalar] | None = None,
        initial_context: p.Context | None = None,
        subproject: str | None = None,
        services: Mapping[str, t.RegisterableService] | None = None,
        factories: Mapping[str, t.FactoryCallable] | None = None,
        resources: Mapping[str, t.ResourceCallable] | None = None,
        container_overrides: Mapping[str, t.Scalar] | None = None,
        wire_modules: Sequence[ModuleType] | None = None,
        wire_packages: Sequence[str] | None = None,
        wire_classes: Sequence[type] | None = None,
    ) -> None:
        """Initialize Oracle CLI client with proper composition."""
        self._oracle_config = FlextDbOracleSettings()
        super().__init__(
            config_type=config_type,
            config_overrides=config_overrides,
            initial_context=initial_context,
            subproject=subproject,
            services=services,
            factories=factories,
            resources=resources,
            container_overrides=container_overrides,
            wire_modules=wire_modules,
            wire_packages=wire_packages,
            wire_classes=wire_classes,
        )
        self.debug = debug
        self.user_preferences = t.ConfigMap(
            root={
                "default_output_format": "table",
                "show_execution_time": "True",
                "auto_confirm_operations": "False",
                "connection_timeout": 30,
                "query_limit": 1000,
            }
        )

    @property
    def oracle_config(self) -> FlextDbOracleSettings:
        """Get the Oracle configuration."""
        return self._oracle_config

    @classmethod
    def run_cli_command(cls, operation: str, **params: str | int | bool) -> r[str]:
        """Run Oracle CLI command with proper error handling.

        Returns:
        r[str]: Command result or error.

        """
        try:
            client = cls()
            if operation == "health":

                def health_cmd() -> r[t.ConfigMap]:
                    return client.health_check()

                health_result: r[t.ConfigMap] = health_cmd()
                if health_result.is_success:
                    return r[str].ok(f"Health check: {health_result.value}")
                return r[str].fail(health_result.error or "Health check failed")
            if params:
                client.logger.debug(
                    f"Unused CLI parameters for operation '{operation}'",
                    unused_params=str(params),
                )
            return r[str].fail(f"Unknown CLI operation: {operation}")
        except (OracleDatabaseError, OracleInterfaceError, ConnectionError) as e:
            return r[str].fail(f"CLI command failed: {e}")

    def configure_preferences(self, **preferences: str | int | bool) -> r[bool]:
        """Configure client preferences.

        Returns:
        r[bool]: Success or error.

        """
        try:
            self.user_preferences.root.update(preferences)
            self.logger.info(
                "Client preferences updated",
                preferences_info=str(preferences),
            )
            return r[bool].ok(True)
        except (OracleDatabaseError, OracleInterfaceError, ConnectionError) as e:
            return r[bool].fail(f"Preference configuration failed: {e}")

    def connect_to_oracle(
        self,
        host: str | None = None,
        port: int | None = None,
        service_name: str | None = None,
        username: str | None = None,
        password: str | None = None,
    ) -> r[FlextDbOracleApi]:
        """Connect to Oracle database with provided parameters or config defaults.

        Returns:
        r[FlextDbOracleApi]: API instance or error.

        """
        try:
            actual_host = host or self.oracle_config.host
            actual_port = port or self.oracle_config.port
            actual_service_name = service_name or self.oracle_config.service_name
            actual_username = username or self.oracle_config.username
            actual_password_raw = password or self.oracle_config.password
            if not actual_host:
                return r[FlextDbOracleApi].fail("Oracle host is required")
            if not actual_username:
                return r[FlextDbOracleApi].fail("Oracle username is required")
            if not actual_password_raw:
                return r[FlextDbOracleApi].fail("Oracle password is required")
            self.logger.info(
                f"Connecting to Oracle at {actual_host}:{actual_port}/{actual_service_name}"
            )
            actual_password: str | None = (
                str(actual_password_raw) if actual_password_raw else None
            )
            config: FlextDbOracleSettings = FlextDbOracleSettings.model_validate({
                "host": actual_host,
                "port": actual_port,
                "service_name": actual_service_name,
                "username": actual_username,
                "password": actual_password,
            })
            api = FlextDbOracleApi(config=config)
            connect_result: r[FlextDbOracleApi] = api.connect()
            if connect_result.is_success:
                self.current_connection = api
                self.logger.info("Oracle connection established successfully")
                return r[FlextDbOracleApi].ok(api)
            return r[FlextDbOracleApi].fail(
                f"Oracle connection failed: {connect_result.error}"
            )
        except (
            OracleDatabaseError,
            OracleInterfaceError,
            ConnectionError,
            OSError,
            SQLAlchemyOperationalError,
        ) as e:
            return r[FlextDbOracleApi].fail(f"Connection error: {e}")

    def disconnect(self) -> r[bool]:
        """Disconnect from Oracle database.

        Returns:
        r[bool]: Success or error.

        """
        if self.current_connection:
            result: r[bool] = self.current_connection.disconnect()
            self.current_connection = None
            return result
        return r[bool].ok(True)

    @override
    def execute(self) -> r[FlextDbOracleSettings]:
        """Execute the main domain operation for Oracle client.

        Returns:
        r[FlextDbOracleSettings]: Success with settings or failure with error

        """
        return r[FlextDbOracleSettings].ok(self._oracle_config)

    def execute_query(
        self, sql: str, params: t.Query.QueryParameters | None = None
    ) -> r[str]:
        """Execute SQL query with formatted output.

        Returns:
        r[str]: Formatted query results or error.

        """
        query_params = params if params is not None else t.ConfigMap(root={})
        operation_result = self._execute_with_chain(
            "query", sql=sql, params=query_params
        )
        format_type = str(
            self.user_preferences.root.get("default_output_format", "table")
        )
        return self._format_and_display_result(operation_result, format_type)

    def health_check(self) -> r[t.ConfigMap]:
        """Perform Oracle health check.

        Returns:
        r[t.ConfigMap]: Health check result or error.

        """
        return self._execute_health_check()

    def list_schemas(self) -> r[str]:
        """List Oracle schemas with formatted output.

        Returns:
        r[str]: Formatted schemas list or error.

        """
        operation_result: r[t.ConfigMap] = self._execute_with_chain("list_schemas")
        format_type = str(
            self.user_preferences.root.get("default_output_format", "table")
        )
        return self._format_and_display_result(operation_result, format_type)

    def list_tables(self, schema: str | None = None) -> r[str]:
        """List Oracle tables with formatted output.

        Returns:
        r[str]: Formatted tables list or error.

        """
        operation_result: r[t.ConfigMap] = self._execute_with_chain(
            "list_tables", schema=schema or ""
        )
        format_type = str(
            self.user_preferences.root.get("default_output_format", "table")
        )
        return self._format_and_display_result(operation_result, format_type)

    def _adapt_data_for_table(self, data: t.ConfigMap) -> r[list[t.ConfigMap]]:
        """Adapt data for table display.

        Returns:
        r[list[t.ConfigMap]]: Adapted data or error.

        """
        try:

            def adapt_schemas(raw_value: t.ContainerValue) -> list[t.ConfigMap]:
                schemas = _validate_general_list(raw_value)
                if schemas is None:
                    return []
                return [t.ConfigMap(root={"schema": str(schema)}) for schema in schemas]

            def adapt_tables(raw_value: t.ContainerValue) -> list[t.ConfigMap]:
                tables = _validate_general_list(raw_value)
                if tables is None:
                    return []
                return [t.ConfigMap(root={"table": str(table)}) for table in tables]

            def adapt_health(raw_value: t.ContainerValue) -> list[t.ConfigMap]:
                try:
                    health_map = _CONFIG_DICT_ADAPTER.validate_python(raw_value)
                except ValidationError:
                    return []
                health = _validate_config_map(health_map)
                if health is None:
                    return []
                return [
                    t.ConfigMap(root={"key": str(key), "value": str(value)})
                    for key, value in health.items()
                ]

            adaptation_strategies: list[
                tuple[str, Callable[[t.ContainerValue], list[t.ConfigMap]]]
            ] = [
                ("schemas", adapt_schemas),
                ("tables", adapt_tables),
                ("health", adapt_health),
            ]
            data_root = data.root
            for key, strategy in adaptation_strategies:
                if key in data_root:
                    adapted_data = strategy(data_root[key])
                    return r[list[t.ConfigMap]].ok(adapted_data)
            result = [
                t.ConfigMap(root={"key": str(key), "value": str(value)})
                for key, value in data_root.items()
            ]
            return r[list[t.ConfigMap]].ok(result)
        except (OracleDatabaseError, OracleInterfaceError, ConnectionError) as e:
            return r[list[t.ConfigMap]].fail(f"Data adaptation failed: {e}")

    def _build_table_string(self, adapted_data: list[t.ConfigMap]) -> str:
        """Build table string from adapted data."""
        headers: list[str] = list(adapted_data[0].keys())
        rows: list[list[str]] = [[str(row[h]) for h in headers] for row in adapted_data]
        result_str = f"{'|'.join(headers)}\n{'|'.join(['---'] * len(headers))}\n"
        result_str += "\n".join(["|".join(row) for row in rows])
        return result_str

    def _execute_health_check(self) -> r[t.ConfigMap]:
        """Execute Oracle health check.

        Returns:
        r[t.ConfigMap]: Health check result or error.

        """
        try:
            validation_result: r[bool] = self._validate_connection()
            if validation_result.is_failure:
                return r[t.ConfigMap].fail(
                    validation_result.error or "Connection validation failed"
                )
            if not self.current_connection:
                return r[t.ConfigMap].fail("No connection available")
            health_data = t.ConfigMap(
                root={
                    "connection_status": c.Cqrs.CommonStatus.ACTIVE
                    if self.current_connection.is_connected
                    else "inactive",
                    "host": self.current_connection.oracle_config.host,
                    "port": self.current_connection.oracle_config.port,
                    "service_name": self.current_connection.oracle_config.service_name,
                    "timestamp": "now",
                }
            )
            return r[t.ConfigMap].ok(health_data)
        except (OracleDatabaseError, OracleInterfaceError, ConnectionError) as e:
            return r[t.ConfigMap].fail(f"Health check failed: {e}")

    def _execute_operation(
        self, operation: str, **params: t.Scalar | t.ConfigMap
    ) -> r[t.ConfigMap]:
        """Execute Oracle operation with error handling.

        Returns:
        r[t.ConfigMap]: Operation result or error.

        """
        if not self.current_connection:
            return r[t.ConfigMap].fail("No active connection")
        try:
            if operation == "list_schemas":
                return self._handle_list_schemas_operation()
            if operation == "list_tables":
                return self._handle_list_tables_operation(**params)
            if operation == "query":
                return self._handle_query_operation(**params)
            if operation == "health_check":
                return self._handle_health_check_operation()
            return r[t.ConfigMap].fail(f"Unknown operation: {operation}")
        except (OracleDatabaseError, OracleInterfaceError, ConnectionError) as e:
            return r[t.ConfigMap].fail(f"Operation failed: {e}")

    def _execute_with_chain(
        self, operation: str, **params: t.Scalar | t.ConfigMap
    ) -> r[t.ConfigMap]:
        """Execute operation with validation chain.

        Returns:
        r[t.ConfigMap]: Operation result or error.

        """
        validation_result: r[bool] = self._validate_connection()
        if validation_result.is_failure:
            return r[t.ConfigMap].fail(validation_result.error or "Validation failed")
        return self._execute_operation(operation, **params)

    def _format_and_display_result(
        self, operation_result: r[t.ConfigMap], format_type: str = "table"
    ) -> r[str]:
        """Format and display operation result.

        Returns:
        r[str]: Formatted result or error.

        """
        return self._get_formatter_strategy(format_type).flat_map(
            lambda formatter: operation_result.flat_map(
                lambda data: (
                    formatter(data)
                    if callable(formatter)
                    else r[str].fail("Invalid formatter strategy")
                )
            )
        )

    def _format_as_json(self, data: t.ConfigMap) -> r[str]:
        """Format data as JSON output.

        Returns:
        r[str]: JSON formatted data or error.

        """
        return u.try_(
            lambda: data.model_dump_json(indent=2),
            catch=(OracleDatabaseError, OracleInterfaceError, ConnectionError),
        ).map_error(lambda e: f"JSON formatting failed: {e}")

    def _format_as_table(self, data: t.ConfigMap) -> r[str]:
        """Format data as table output.

        Returns:
        r[str]: Table formatted data or error.

        """
        try:
            return self._adapt_data_for_table(data).map(
                lambda adapted_data: (
                    self._build_table_string(adapted_data)
                    if adapted_data
                    else str(adapted_data)
                )
            )
        except (OracleDatabaseError, OracleInterfaceError, ConnectionError) as e:
            return r[str].fail(f"Table formatting failed: {e}")

    def _get_formatter_strategy(
        self, format_type: str
    ) -> r[Callable[[t.ConfigMap], r[str]]]:
        """Get formatter strategy for output format.

        Returns:
        r: Formatter strategy or error.

        """
        try:
            formatter_strategies: list[tuple[str, Callable[[t.ConfigMap], r[str]]]] = [
                ("table", self._format_as_table),
                ("json", self._format_as_json),
                ("plain", lambda data: r[str].ok(str(data))),
            ]
            for supported_format, formatter in formatter_strategies:
                if format_type == supported_format:
                    return r[Callable[[t.ConfigMap], r[str]]].ok(formatter)
            return r[Callable[[t.ConfigMap], r[str]]].fail(
                f"Unsupported format: {format_type}"
            )
        except (OracleDatabaseError, OracleInterfaceError, ConnectionError) as e:
            return r[Callable[[t.ConfigMap], r[str]]].fail(
                f"Formatter strategy error: {e}"
            )

    def _handle_health_check_operation(self) -> r[t.ConfigMap]:
        """Handle health check operation."""
        if self.current_connection is None:
            return r[t.ConfigMap].fail("No active database connection")
        return self.current_connection.get_health_status().map(
            lambda status: t.ConfigMap(root=status.model_dump())
        )

    def _handle_list_schemas_operation(self) -> r[t.ConfigMap]:
        """Handle list schemas operation."""
        if self.current_connection is None:
            return r[t.ConfigMap].fail("No active database connection")
        return self.current_connection.get_schemas().map(
            lambda schemas: t.ConfigMap(root={"schemas": list(schemas)})
        )

    def _handle_list_tables_operation(
        self, **params: t.Scalar | t.ConfigMap
    ) -> r[t.ConfigMap]:
        """Handle list tables operation."""
        if self.current_connection is None:
            return r[t.ConfigMap].fail("No active database connection")
        schema = str(params.get("schema", ""))
        return self.current_connection.get_tables(schema or None).map(
            lambda tables: t.ConfigMap(root={"tables": list(tables)})
        )

    def _handle_query_operation(
        self, **params: t.Scalar | t.ConfigMap
    ) -> r[t.ConfigMap]:
        """Handle query operation."""
        if self.current_connection is None:
            return r[t.ConfigMap].fail("No active database connection")
        sql = str(params.get("sql", ""))
        if not sql:
            return r[t.ConfigMap].fail("SQL query required")
        raw_params = params.get("params", t.ConfigMap(root={}))
        if isinstance(raw_params, t.ConfigMap):
            params_map = raw_params
        else:
            try:
                normalized_params = _CONFIG_DICT_ADAPTER.validate_python(raw_params)
            except ValidationError:
                normalized_params: dict[str, t.ContainerValue] = {}
            params_map = t.ConfigMap(root=normalized_params)
        return self.current_connection.query(sql, params_map.root).map(
            lambda rows: t.ConfigMap(
                root={"rows": [row.root for row in rows], "row_count": len(rows)}
            )
        )

    def _validate_connection(self) -> r[bool]:
        """Validate current Oracle connection.

        Returns:
        r[bool]: Success or error.

        """
        if not self.current_connection:
            return r[bool].fail("No active Oracle connection")
        if not self.current_connection.is_connected:
            return r[bool].fail("Oracle connection not active")
        return r[bool].ok(True)


__all__: list[str] = ["FlextDbOracleClient"]
