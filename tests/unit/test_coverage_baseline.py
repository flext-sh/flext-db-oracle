"""Behavioral contract tests for flext-db-oracle public surface.

Exercises the OBSERVABLE public contract of settings, the password value
object, the Column model, and the composed services facade: return values,
``r[T]`` outcomes, raised validation errors, and public model state. No
private attributes, no internal-collaborator spying, no line-coverage pokes.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from flext_db_oracle import FlextDbOracleSettings
from tests import m, tm

if TYPE_CHECKING:
    from flext_db_oracle.services import FlextDbOracleServices


class TestsFlextDbOracleCoverageBaseline:
    """Behavioral contract for the flext-db-oracle public API."""

    @staticmethod
    def test_settings_expose_provided_connection_fields(
        oracle_unit_settings: FlextDbOracleSettings,
    ) -> None:
        """Settings return the exact host/port/service/user supplied at build."""
        tm.that(oracle_unit_settings.DbOracle.host, eq="localhost")
        tm.that(oracle_unit_settings.DbOracle.port, eq=1521)
        tm.that(oracle_unit_settings.DbOracle.service_name, eq="TEST")
        tm.that(oracle_unit_settings.DbOracle.username, eq="testuser")

    @staticmethod
    def test_settings_password_is_a_plain_string(
        oracle_unit_settings: FlextDbOracleSettings,
    ) -> None:
        """The namespace stores the password as a plain string scalar."""
        tm.that(oracle_unit_settings.DbOracle.password, eq="testpass")

    @staticmethod
    def test_settings_service_name_round_trips_verbatim() -> None:
        """service_name is stored verbatim (no case normalization in layer-0)."""
        settings = FlextDbOracleSettings.model_validate({
            "DbOracle": {
                "host": "localhost",
                "port": 1521,
                "service_name": "lower_svc",
                "username": "testuser",
                "password": "testpass",
            },
        })
        tm.that(settings.DbOracle.service_name, eq="lower_svc")

    @staticmethod
    def test_settings_ssl_fields_are_independent() -> None:
        """ssl_cert_file and ssl_server_cert_dn keep their supplied values."""
        settings = FlextDbOracleSettings.model_validate({
            "DbOracle": {
                "host": "secure.example.com",
                "port": 2484,
                "service_name": "SECURE_DB",
                "username": "secure_user",
                "password": "p" + "1" * 12,
                "ssl_cert_file": "/path/to/cert.pem",
            },
        })
        tm.that(settings.DbOracle.ssl_cert_file, eq="/path/to/cert.pem")
        tm.that(settings.DbOracle.ssl_server_cert_dn, none=True)

    @staticmethod
    def test_password_equality_and_secret_access() -> None:
        """Password exposes its root string, str form, and wrapper equality."""
        password = m.DbOracle.Password("h" + "2" * 6)
        tm.that(password.root, eq="h" + "2" * 6)
        tm.that(str(password), eq="h" + "2" * 6)
        tm.that(password, eq=m.DbOracle.Password("h" + "2" * 6))
        tm.that(password, ne=m.DbOracle.Password("other"))

    @staticmethod
    def test_column_exposes_public_fields() -> None:
        """Column stores name/type/nullable/default as public field state."""
        column = m.DbOracle.Column(
            name="ID",
            data_type="NUMBER",
            nullable=False,
            default_value="1",
        )
        tm.that(column.name, eq="ID")
        tm.that(column.data_type, eq="NUMBER")
        tm.that(column.nullable, eq=False)
        tm.that(column.default_value, eq="1")

    @staticmethod
    def test_column_mapping_access_contract() -> None:
        """Column supports mapping-style key access and membership."""
        column = m.DbOracle.Column(name="ID", data_type="NUMBER")
        tm.that(column["column_name"], eq="ID")
        tm.that(column["data_type"], eq="NUMBER")
        tm.that("nullable" in column, eq=True)
        tm.that("unknown_key" in column, eq=False)
        tm.that(column["unknown_key"], eq="")

    @staticmethod
    def test_service_exposes_bound_settings(
        oracle_unit_services: FlextDbOracleServices,
        oracle_unit_settings: FlextDbOracleSettings,
    ) -> None:
        """The facade returns the exact settings it was constructed with."""
        tm.that(oracle_unit_services.settings, eq=oracle_unit_settings)
        tm.that(oracle_unit_services.db_config, eq=oracle_unit_settings)

    @staticmethod
    def test_service_is_not_connected_before_connect(
        oracle_unit_services: FlextDbOracleServices,
    ) -> None:
        """A freshly built facade reports no active engine."""
        tm.that(oracle_unit_services.connected(), eq=False)

    @staticmethod
    def test_service_execute_returns_active_configuration(
        oracle_unit_services: FlextDbOracleServices,
        oracle_unit_settings: FlextDbOracleSettings,
    ) -> None:
        """execute() yields the active configuration as its default result."""
        result = oracle_unit_services.execute()
        tm.ok(result)
        tm.that(result.value, eq=oracle_unit_settings)

    @staticmethod
    def test_build_select_with_columns(
        oracle_unit_services: FlextDbOracleServices,
    ) -> None:
        """build_select emits a SELECT over the named columns and table."""
        sql = tm.ok(oracle_unit_services.build_select("USERS", ["ID", "NAME"]))
        tm.that(sql, has=["SELECT", "FROM", "USERS", "ID", "NAME"])

    @staticmethod
    def test_build_select_without_columns_selects_star(
        oracle_unit_services: FlextDbOracleServices,
    ) -> None:
        """build_select with no column list projects all columns."""
        sql = tm.ok(oracle_unit_services.build_select("USERS"))
        tm.that(sql, has=["SELECT", "*", "USERS"])

    @staticmethod
    def test_build_insert_statement_binds_columns(
        oracle_unit_services: FlextDbOracleServices,
    ) -> None:
        """build_insert_statement produces an INSERT with named binds."""
        sql = tm.ok(
            oracle_unit_services.build_insert_statement("USERS", ["ID", "NAME"])
        )
        tm.that(sql, has=["INSERT INTO", "USERS", ":ID", ":NAME"])

    @staticmethod
    def test_build_update_statement_sets_and_filters(
        oracle_unit_services: FlextDbOracleServices,
    ) -> None:
        """build_update_statement produces an UPDATE with SET and WHERE binds."""
        sql = tm.ok(
            oracle_unit_services.build_update_statement("USERS", ["NAME"], ["ID"])
        )
        tm.that(sql, has=["UPDATE", "SET", ":NAME", "WHERE", ":ID"])

    @staticmethod
    def test_build_delete_statement_filters_by_where(
        oracle_unit_services: FlextDbOracleServices,
    ) -> None:
        """build_delete_statement produces a DELETE constrained by WHERE binds."""
        sql = tm.ok(oracle_unit_services.build_delete_statement("USERS", ["ID"]))
        tm.that(sql, has=["DELETE FROM", "USERS", "WHERE", ":ID"])

    @staticmethod
    def test_create_table_ddl_from_column_models(
        oracle_unit_services: FlextDbOracleServices,
    ) -> None:
        """create_table_ddl compiles CREATE TABLE with the column definitions."""
        columns: list[m.DbOracle.Column] = [
            m.DbOracle.Column(name="ID", data_type="NUMBER", nullable=False),
        ]
        sql = tm.ok(oracle_unit_services.create_table_ddl("ACCOUNTS", columns))
        tm.that(sql, has=["CREATE TABLE", "ACCOUNTS", "ID", "NUMBER"])

    @staticmethod
    def test_drop_table_ddl(oracle_unit_services: FlextDbOracleServices) -> None:
        """drop_table_ddl compiles a DROP TABLE for the named table."""
        sql = tm.ok(oracle_unit_services.drop_table_ddl("ACCOUNTS"))
        tm.that(sql, has=["DROP TABLE", "ACCOUNTS"])

    @staticmethod
    def test_build_create_index_statement_success(
        oracle_unit_services: FlextDbOracleServices,
    ) -> None:
        """A well-formed index config compiles to a CREATE INDEX statement."""
        sql = tm.ok(
            oracle_unit_services.build_create_index_statement({
                "index_name": "IX_USERS_ID",
                "table_name": "USERS",
                "columns": ["ID"],
            }),
        )
        tm.that(sql, has=["CREATE INDEX", "IX_USERS_ID", "USERS", "ID"])

    @staticmethod
    def test_build_create_index_rejects_invalid_payload(
        oracle_unit_services: FlextDbOracleServices,
    ) -> None:
        """An index config missing required keys fails with a validation error."""
        result = oracle_unit_services.build_create_index_statement({
            "unexpected": "value"
        })
        tm.fail(result, has="Invalid CREATE INDEX settings")

    @staticmethod
    def test_build_create_index_rejects_empty_columns(
        oracle_unit_services: FlextDbOracleServices,
    ) -> None:
        """An index definition with no columns is rejected."""
        result = oracle_unit_services.build_create_index_statement({
            "index_name": "IX_EMPTY",
            "table_name": "USERS",
            "columns": [],
        })
        tm.fail(result, has="at least one column")
