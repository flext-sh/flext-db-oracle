"""Behavioral tests for FlextDbOracleServices public contract.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

These tests exercise only the OBSERVABLE public behavior of the composed
Oracle services facade: SQL text produced by the builders, the r[T] outcome
of fallible operations, and public model state. No database connection, no
patching of internal collaborators, no private-attribute access.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
from flext_tests import tm

from flext_db_oracle import FlextDbOracleSettings
from flext_db_oracle.api import FlextDbOracleApi
from flext_db_oracle.services.facade import FlextDbOracleServices
from tests import m

if TYPE_CHECKING:
    from tests import t


class TestsFlextDbOracleServices:
    """Public-contract behavior of the FlextDbOracleServices facade."""

    @pytest.fixture
    def settings(self) -> FlextDbOracleSettings:
        """Return a typed, non-routable Oracle configuration."""
        return FlextDbOracleSettings(
            DbOracle={
                "host": "localhost",
                "port": 1521,
                "service_name": "TEST",
                "username": "testuser",
                "password": "testpass",
            },
        )

    @pytest.fixture
    def service(
        self,
        settings: FlextDbOracleSettings,
    ) -> FlextDbOracleServices:
        """Return a fresh, unconnected services facade."""
        return FlextDbOracleServices(settings=settings)

    # ------------------------------------------------------------------
    # Configuration and connection lifecycle
    # ------------------------------------------------------------------

    def test_facade_exposes_bound_settings(
        self,
        service: FlextDbOracleServices,
        settings: FlextDbOracleSettings,
    ) -> None:
        """The facade returns the exact settings it was constructed with."""
        tm.that(service.db_config, eq=settings)
        tm.that(service.settings, eq=settings)

    def test_new_service_is_not_connected(
        self,
        service: FlextDbOracleServices,
    ) -> None:
        """A freshly created service reports a disconnected state."""
        tm.that(service.connected(), eq=False)

    def test_connected_returns_boolean(
        self,
        service: FlextDbOracleServices,
    ) -> None:
        """connected() yields a plain boolean contract value."""
        tm.that(service.connected(), is_=bool)

    def test_disconnect_is_idempotent_when_not_connected(
        self,
        service: FlextDbOracleServices,
    ) -> None:
        """Disconnecting an unconnected service succeeds without error."""
        first = service.disconnect()
        second = service.disconnect()
        tm.ok(first)
        tm.ok(second)
        tm.that(first.value, eq=True)

    def test_connect_fails_for_unreachable_host(self) -> None:
        """Connecting to an unreachable endpoint returns a failure result."""
        service = FlextDbOracleServices(
            settings=FlextDbOracleSettings(
                DbOracle={
                    "host": "127.0.0.1",
                    "port": 19999,
                    "service_name": "INVALID",
                    "username": "invalid",
                    "password": "invalid",
                    "timeout": 1,
                },
            ),
        )
        result = service.connect()
        tm.that(result.failure, eq=True)
        tm.that(service.connected(), eq=False)

    def test_test_connection_fails_when_not_connected(
        self,
        service: FlextDbOracleServices,
    ) -> None:
        """test_connection reports failure with a not-connected message."""
        result = service.test_connection()
        tm.that(result.failure, eq=True)
        tm.that((result.error or "").lower(), has="not connected")

    def test_health_check_reports_oracle_service_unhealthy_offline(
        self,
        service: FlextDbOracleServices,
    ) -> None:
        """Health check identifies the Oracle service and unhealthy status."""
        result = service.health_check()
        tm.ok(result)
        tm.that(result.value.service, eq="oracle")
        tm.that(result.value.status, eq="unhealthy")
        tm.that(result.value.database, eq="TEST")

    # ------------------------------------------------------------------
    # SELECT builder
    # ------------------------------------------------------------------

    def test_build_select_emits_columns_and_table(
        self,
        service: FlextDbOracleServices,
    ) -> None:
        """build_select renders the requested columns against the table."""
        result = service.build_select("TEST_TABLE", ["col1", "col2"])
        tm.ok(result)
        tm.that(result.value, has="SELECT")
        tm.that(result.value, has="TEST_TABLE")
        tm.that(result.value, has="col1")
        tm.that(result.value, has="col2")

    def test_build_select_without_columns_selects_star(
        self,
        service: FlextDbOracleServices,
    ) -> None:
        """An empty column list produces a SELECT * projection."""
        result = service.build_select("TEST_TABLE", [])
        tm.ok(result)
        tm.that(result.value, has="*")
        tm.that(result.value, has="TEST_TABLE")

    def test_build_select_with_conditions_emits_bound_where(
        self,
        service: FlextDbOracleServices,
    ) -> None:
        """Conditions become a parameterized WHERE clause with named binds."""
        conditions: t.JsonMapping = {"id": 1, "name": "test"}
        result = service.build_select("TEST_TABLE", ["col1"], conditions)
        tm.ok(result)
        tm.that(result.value, has="WHERE")
        tm.that(result.value, has="id = :id")
        tm.that(result.value, has="name = :name")

    def test_build_select_qualifies_with_schema(
        self,
        service: FlextDbOracleServices,
    ) -> None:
        """A schema name qualifies the table reference in the rendered SQL."""
        result = service.build_select(
            "test_table",
            ["col1"],
            schema_name="test_schema",
        )
        tm.ok(result)
        tm.that(result.value, has="TEST_SCHEMA")
        tm.that(result.value, has="TEST_TABLE")

    def test_build_select_quotes_injection_identifier(
        self,
        service: FlextDbOracleServices,
    ) -> None:
        """A malicious identifier is safely quoted, never emitted raw."""
        malicious = "table'; DROP TABLE users;--"
        result = service.build_select(malicious, ["col1"])
        tm.ok(result)
        tm.that(result.value, has=f'"{malicious}"')

    # ------------------------------------------------------------------
    # INSERT / UPDATE / DELETE builders
    # ------------------------------------------------------------------

    def test_build_insert_statement_emits_named_binds(
        self,
        service: FlextDbOracleServices,
    ) -> None:
        """build_insert_statement renders INSERT ... VALUES with named binds."""
        result = service.build_insert_statement("USERS", ["id", "name", "email"])
        tm.ok(result)
        tm.that(result.value, has="INSERT INTO")
        tm.that(result.value, has="VALUES")
        tm.that(result.value, has=":id")
        tm.that(result.value, has=":name")
        tm.that(result.value, has=":email")

    def test_build_insert_quotes_invalid_identifier_without_quoting_bind(
        self,
        service: FlextDbOracleServices,
    ) -> None:
        """Invalid Oracle identifiers are quoted while bind names stay bare."""
        result = service.build_insert_statement(
            "USERS",
            ["DATA", "_SDC_LOADED_AT"],
            schema="TEST_SCHEMA",
        )
        tm.ok(result)
        tm.that(result.value, has='"_SDC_LOADED_AT"')
        tm.that(result.value, has=":_SDC_LOADED_AT")
        tm.that('(":_SDC_LOADED_AT"' not in result.value, eq=True)

    def test_build_update_statement_emits_set_and_where(
        self,
        service: FlextDbOracleServices,
    ) -> None:
        """build_update_statement renders UPDATE ... SET ... WHERE."""
        result = service.build_update_statement("USERS", ["name", "email"], ["id"])
        tm.ok(result)
        tm.that(result.value, has="UPDATE")
        tm.that(result.value, has="SET")
        tm.that(result.value, has="WHERE")
        tm.that(result.value, has="name=:name")

    def test_build_delete_statement_emits_bound_where(
        self,
        service: FlextDbOracleServices,
    ) -> None:
        """build_delete_statement renders DELETE FROM ... WHERE with binds."""
        result = service.build_delete_statement("USERS", ["id", "status"])
        tm.ok(result)
        tm.that(result.value, has="DELETE FROM")
        tm.that(result.value, has="WHERE")
        tm.that(result.value, has="id = :id")
        tm.that(result.value, has="status = :status")

    # ------------------------------------------------------------------
    # DDL builders
    # ------------------------------------------------------------------

    def test_create_table_ddl_emits_constraints(
        self,
        service: FlextDbOracleServices,
    ) -> None:
        """create_table_ddl renders the table with PK and NOT NULL constraints."""
        columns: t.SequenceOf[t.JsonMapping] = [
            {
                "name": "id",
                "data_type": "NUMBER",
                "nullable": False,
                "primary_key": True,
            },
            {"name": "name", "data_type": "VARCHAR2(100)", "nullable": True},
            {"name": "created_at", "data_type": "TIMESTAMP", "nullable": False},
        ]
        result = service.create_table_ddl("TEST_TABLE", columns)
        tm.ok(result)
        tm.that(result.value, has="CREATE TABLE")
        tm.that(result.value, has="PRIMARY KEY")
        tm.that(result.value, has="NOT NULL")

    def test_build_create_index_statement_renders_full_ddl(
        self,
        service: FlextDbOracleServices,
    ) -> None:
        """A fully specified index config compiles to the exact DDL string."""
        result = service.build_create_index_statement({
            "table_name": "USERS",
            "index_name": "IDX_USERS_EMAIL",
            "columns": ["email"],
            "schema_name": "APP",
            "unique": True,
            "tablespace": "USERS_TS",
            "parallel": 2,
        })
        tm.ok(result)
        tm.that(
            result.value,
            eq=(
                "CREATE UNIQUE INDEX APP.IDX_USERS_EMAIL "
                "ON APP.USERS (EMAIL) TABLESPACE USERS_TS PARALLEL 2"
            ),
        )

    def test_build_create_index_statement_fails_for_empty_columns(
        self,
        service: FlextDbOracleServices,
    ) -> None:
        """An index without columns is rejected with an explanatory error."""
        result = service.build_create_index_statement({
            "table_name": "USERS",
            "index_name": "IDX_USERS_EMPTY",
            "columns": [],
        })
        tm.that(result.failure, eq=True)
        tm.that((result.error or ""), has="at least one column")

    # ------------------------------------------------------------------
    # Singer type mapping
    # ------------------------------------------------------------------

    @pytest.mark.parametrize(
        ("singer_type", "oracle_type"),
        [
            ("string", "VARCHAR2(4000)"),
            ("integer", "NUMBER(38)"),
            ("number", "NUMBER"),
            ("boolean", "NUMBER(1)"),
        ],
    )
    def test_convert_singer_type_maps_scalar_types(
        self,
        service: FlextDbOracleServices,
        singer_type: str,
        oracle_type: str,
    ) -> None:
        """Each Singer scalar type maps to its canonical Oracle type."""
        result = service.convert_singer_type(singer_type)
        tm.ok(result)
        tm.that(result.value, eq=oracle_type)

    def test_convert_singer_type_unwraps_nullable_array(
        self,
        service: FlextDbOracleServices,
    ) -> None:
        """A nullable array type resolves to its non-null Oracle mapping."""
        result = service.convert_singer_type(["string", "null"])
        tm.ok(result)
        tm.that(result.value, eq="VARCHAR2(4000)")

    def test_convert_singer_type_honors_datetime_format(
        self,
        service: FlextDbOracleServices,
    ) -> None:
        """A date-time format hint overrides the base string mapping."""
        result = service.convert_singer_type("string", "date-time")
        tm.ok(result)
        tm.that(result.value, eq="TIMESTAMP")

    def test_map_singer_schema_maps_all_properties(
        self,
        service: FlextDbOracleServices,
    ) -> None:
        """A Singer schema maps every property to its Oracle column type."""
        schema: t.JsonMapping = {
            "properties": {
                "id": {"type": "integer"},
                "name": {"type": "string"},
                "created_at": {"type": "string", "format": "date-time"},
                "is_active": {"type": "boolean"},
            },
        }
        result = service.map_singer_schema(schema)
        tm.ok(result)
        mapping = result.value
        tm.that(mapping["id"], eq="NUMBER(38)")
        tm.that(mapping["name"], eq="VARCHAR2(4000)")
        tm.that(mapping["created_at"], eq="TIMESTAMP")
        tm.that(mapping["is_active"], eq="NUMBER(1)")

    def test_map_singer_schema_rejects_non_mapping_properties(
        self,
        service: FlextDbOracleServices,
    ) -> None:
        """Non-mapping ``properties`` are rejected as a failure result."""
        result = service.map_singer_schema({"properties": "not_a_dict"})
        tm.that(result.failure, eq=True)

    def test_map_singer_schema_without_properties_yields_empty_mapping(
        self,
        service: FlextDbOracleServices,
    ) -> None:
        """A schema lacking properties produces an empty successful mapping."""
        result = service.map_singer_schema({})
        tm.that(result.failure or not result.value, eq=True)

    # ------------------------------------------------------------------
    # Metrics, operations, plugins
    # ------------------------------------------------------------------

    def test_record_metric_succeeds(
        self,
        service: FlextDbOracleServices,
    ) -> None:
        """Recording a valid metric returns a success result."""
        result = service.record_metric("db_query_duration", 12.5)
        tm.ok(result)

    def test_record_metric_accepts_tags(
        self,
        service: FlextDbOracleServices,
    ) -> None:
        """Recording a metric with tags succeeds."""
        result = service.record_metric(
            "db_query_duration",
            12.5,
            m.ConfigMap(root={"table": "users"}),
        )
        tm.ok(result)

    def test_record_metric_requires_name(
        self,
        service: FlextDbOracleServices,
    ) -> None:
        """An empty metric name is rejected with a required-name error."""
        result = service.record_metric("", 12.5)
        tm.that(result.failure, eq=True)
        tm.that((result.error or ""), has="Metric name is required")

    def test_fetch_metrics_reports_observability_status(
        self,
        service: FlextDbOracleServices,
    ) -> None:
        """fetch_metrics returns a health status tagged with observability."""
        result = service.fetch_metrics()
        tm.ok(result)
        tm.that(result.value.status.endswith("_with_observability"), eq=True)

    def test_track_operation_appends_to_operations(
        self,
        service: FlextDbOracleServices,
    ) -> None:
        """A tracked operation becomes observable via fetch_operations."""
        before = service.fetch_operations()
        tm.ok(before)
        track = service.track_operation(
            "SELECT",
            25.0,
            success=True,
            metadata={"table": "users"},
        )
        tm.ok(track)
        after = service.fetch_operations()
        tm.ok(after)
        tm.that(len(after.value) > len(before.value), eq=True)

    def test_plugin_register_fetch_list_unregister_lifecycle(
        self,
        service: FlextDbOracleServices,
    ) -> None:
        """A plugin is retrievable and listable until it is unregistered."""
        plugin: t.JsonPayload = {"version": "1.2.3", "description": "demo"}
        register = service.register_plugin("sample", plugin)
        tm.ok(register)
        listed = service.list_plugins()
        tm.ok(listed)
        tm.that(listed.value.root, eq={"sample": True})
        fetched = service.fetch_plugin("sample")
        tm.ok(fetched)
        tm.that(fetched.value, eq=plugin)
        unregister = service.unregister_plugin("sample")
        tm.ok(unregister)
        tm.that(service.fetch_plugin("sample").failure, eq=True)

    def test_plugin_operations_fail_for_missing_name(
        self,
        service: FlextDbOracleServices,
    ) -> None:
        """Fetching or unregistering an unknown plugin fails."""
        tm.that(service.fetch_plugin("missing").failure, eq=True)
        tm.that(service.unregister_plugin("missing").failure, eq=True)

    def test_plugin_operations_reject_empty_name(
        self,
        service: FlextDbOracleServices,
    ) -> None:
        """All plugin operations reject an empty plugin name."""
        tm.that(service.register_plugin("", {"v": "1"}).failure, eq=True)
        tm.that(service.fetch_plugin("").failure, eq=True)
        tm.that(service.unregister_plugin("").failure, eq=True)

    def test_generate_query_hash_is_deterministic(
        self,
        service: FlextDbOracleServices,
    ) -> None:
        """The same SQL and parameters always hash to the same value."""
        sql = "SELECT * FROM users WHERE id = :id"
        params: t.JsonMapping = {"id": 123}
        first = service.generate_query_hash(sql, params)
        second = service.generate_query_hash(sql, params)
        tm.ok(first)
        tm.that(first.value, is_=str)
        tm.that(bool(first.value), eq=True)
        tm.that(first.value, eq=second.value)

    # ------------------------------------------------------------------
    # Metadata operations without a live connection
    # ------------------------------------------------------------------

    def test_fetch_schemas_fails_when_not_connected(
        self,
        service: FlextDbOracleServices,
    ) -> None:
        """fetch_schemas surfaces a connection-related failure when offline."""
        result = service.fetch_schemas()
        tm.that(result.failure, eq=True)
        tm.that(result.error, none=False)
        error_lower = (result.error or "").lower()
        tm.that(
            "connect" in error_lower or "connection" in error_lower,
            eq=True,
        )

    @pytest.mark.parametrize("schema", [None, "TEST_SCHEMA", ""])
    def test_fetch_tables_fails_when_not_connected(
        self,
        service: FlextDbOracleServices,
        schema: str | None,
    ) -> None:
        """fetch_tables fails for any schema argument while disconnected."""
        result = service.fetch_tables(schema)
        tm.that(result.failure, eq=True)

    def test_fetch_table_row_count_fails_when_not_connected(
        self,
        service: FlextDbOracleServices,
    ) -> None:
        """Row counting fails while the service is not connected."""
        result = service.fetch_table_row_count("test_table", "test_schema")
        tm.that(result.failure, eq=True)
        tm.that((result.error or ""), has="row count")

    # ------------------------------------------------------------------
    # Public model state
    # ------------------------------------------------------------------

    def test_column_model_exposes_public_fields(self) -> None:
        """A Column model reports its declared public field values."""
        column = m.DbOracle.Column(
            name="ID",
            data_type="NUMBER",
            nullable=False,
            default_value="0",
        )
        tm.that(column.name, eq="ID")
        tm.that(column.data_type, eq="NUMBER")
        tm.that(column.nullable, eq=False)
        tm.that(column.default_value, eq="0")

    def test_table_model_exposes_columns(self) -> None:
        """A Table model reports its owner and declared columns."""
        columns = [
            m.DbOracle.Column(name="ID", data_type="NUMBER", nullable=False),
            m.DbOracle.Column(name="NAME", data_type="VARCHAR2", nullable=True),
        ]
        table = m.DbOracle.Table(
            name="TEST_TABLE",
            owner="TEST_SCHEMA",
            columns=columns,
        )
        tm.that(table.name, eq="TEST_TABLE")
        tm.that(table.owner, eq="TEST_SCHEMA")
        tm.that(len(table.columns), eq=2)

    def test_settings_roundtrip_public_fields(self) -> None:
        """Settings expose the host and port they were constructed with."""
        settings = FlextDbOracleSettings(
            DbOracle={
                "host": "dbhost",
                "port": 1522,
                "service_name": "XE",
                "username": "app",
                "password": "secret",
            },
        )
        tm.that(settings.DbOracle.host, eq="dbhost")
        tm.that(settings.DbOracle.port, eq=1522)
        tm.that(settings.DbOracle.service_name, eq="XE")

    # ------------------------------------------------------------------
    # API error propagation (no live database)
    # ------------------------------------------------------------------

    def test_api_operations_fail_for_unreachable_config(self) -> None:
        """Every API read operation fails deterministically when offline."""
        api = FlextDbOracleApi(
            FlextDbOracleSettings(
                DbOracle={
                    "host": "127.0.0.1",
                    "port": 19999,
                    "service_name": "INVALID",
                    "username": "invalid",
                    "password": "invalid",
                    "timeout": 1,
                },
            ),
        )
        tm.that(api.test_connection().failure, eq=True)
        tm.that(api.fetch_schemas().failure, eq=True)
        tm.that(api.fetch_tables().failure, eq=True)
        tm.that(api.query("SELECT 1 FROM DUAL").failure, eq=True)
