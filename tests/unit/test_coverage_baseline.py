"""Behavioral contract tests for flext-db-oracle public surface.

Exercises the OBSERVABLE public contract of settings, the password value
object, the Column model, and the composed services facade: return values,
``r[T]`` outcomes, raised validation errors, and public model state. No
private attributes, no internal-collaborator spying, no line-coverage pokes.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import pytest
from flext_tests import tm

from flext_db_oracle import FlextDbOracleSettings, p
from flext_db_oracle.services.facade import FlextDbOracleServices
from tests import m


class TestsFlextDbOracleCoverageBaseline:
    """Behavioral contract for the flext-db-oracle public API."""

    @pytest.fixture
    def settings(self) -> FlextDbOracleSettings:
        """Return a valid Oracle settings instance for service construction."""
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
    def service(self, settings: FlextDbOracleSettings) -> FlextDbOracleServices:
        """Return a services facade bound to the valid settings."""
        return FlextDbOracleServices(settings=settings)

    # ------------------------------------------------------------------
    # FlextDbOracleSettings — construction and public field state
    # ------------------------------------------------------------------

    # NOTE (multi-agent): ADR-005 — settings is a layer-0 scalar namespace under
    # settings.DbOracle.*. Flat fields, Password wrapping, uppercase/ssl fallback
    # validators and the settings-level from_url/from_env factories were removed
    # by design; the namespaced contract is what remains to cover.
    def test_settings_expose_provided_connection_fields(
        self,
        settings: FlextDbOracleSettings,
    ) -> None:
        """Settings return the exact host/port/service/user supplied at build."""
        tm.that(settings.DbOracle.host, eq="localhost")
        tm.that(settings.DbOracle.port, eq=1521)
        tm.that(settings.DbOracle.service_name, eq="TEST")
        tm.that(settings.DbOracle.username, eq="testuser")

    def test_settings_password_is_a_plain_string(
        self,
        settings: FlextDbOracleSettings,
    ) -> None:
        """The namespace stores the password as a plain string scalar."""
        tm.that(settings.DbOracle.password, eq="testpass")

    def test_settings_service_name_round_trips_verbatim(self) -> None:
        """service_name is stored verbatim (no case normalization in layer-0)."""
        settings = FlextDbOracleSettings(
            DbOracle={
                "host": "localhost",
                "port": 1521,
                "service_name": "lower_svc",
                "username": "testuser",
                "password": "testpass",
            },
        )
        tm.that(settings.DbOracle.service_name, eq="lower_svc")

    def test_settings_ssl_fields_are_independent(self) -> None:
        """ssl_cert_file and ssl_server_cert_dn keep their supplied values."""
        settings = FlextDbOracleSettings(
            DbOracle={
                "host": "secure.example.com",
                "port": 2484,
                "service_name": "SECURE_DB",
                "username": "secure_user",
                "password": "secure_pass",
                "ssl_cert_file": "/path/to/cert.pem",
            },
        )
        tm.that(settings.DbOracle.ssl_cert_file, eq="/path/to/cert.pem")
        tm.that(settings.DbOracle.ssl_server_cert_dn, none=True)

    # ------------------------------------------------------------------
    # Password value object contract
    # ------------------------------------------------------------------

    def test_password_equality_and_secret_access(self) -> None:
        """Password compares to raw strings and to other Password wrappers."""
        password = m.DbOracle.Password("hunter2")
        tm.that(password.get_secret_value(), eq="hunter2")
        tm.that(password, eq="hunter2")
        tm.that(password, eq=m.DbOracle.Password("hunter2"))
        tm.that(password, ne=m.DbOracle.Password("other"))
        tm.that(str(password), eq="hunter2")

    # ------------------------------------------------------------------
    # Column model contract
    # ------------------------------------------------------------------

    def test_column_exposes_public_fields(self) -> None:
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

    def test_column_mapping_access_contract(self) -> None:
        """Column supports mapping-style key access and membership."""
        column = m.DbOracle.Column(name="ID", data_type="NUMBER")
        tm.that(column["column_name"], eq="ID")
        tm.that(column["data_type"], eq="NUMBER")
        tm.that(column, has="nullable")
        tm.that(column, lacks="unknown_key")
        tm.that(column["unknown_key"], eq="")

    # ------------------------------------------------------------------
    # FlextDbOracleServices facade — lifecycle and config exposure
    # ------------------------------------------------------------------

    def test_service_exposes_bound_settings(
        self,
        service: FlextDbOracleServices,
        settings: FlextDbOracleSettings,
    ) -> None:
        """The facade returns the exact settings it was constructed with."""
        assert service.settings is settings
        assert service.db_config is settings

    def test_service_is_not_connected_before_connect(
        self,
        service: FlextDbOracleServices,
    ) -> None:
        """A freshly built facade reports no active engine."""
        tm.that(service.connected(), eq=False)

    def test_service_execute_returns_active_configuration(
        self,
        service: FlextDbOracleServices,
        settings: FlextDbOracleSettings,
    ) -> None:
        """execute() yields the active configuration as its default result."""
        result = service.execute()
        tm.ok(result)
        assert result.value is settings

    # ------------------------------------------------------------------
    # FlextDbOracleServices facade — SQL builder contracts (r[str])
    # ------------------------------------------------------------------

    def test_build_select_with_columns(
        self,
        service: FlextDbOracleServices,
    ) -> None:
        """build_select emits a SELECT over the named columns and table."""
        sql = tm.ok(service.build_select("USERS", ["ID", "NAME"]))
        tm.that(sql, has=["SELECT", "FROM", "USERS", "ID", "NAME"])

    def test_build_select_without_columns_selects_star(
        self,
        service: FlextDbOracleServices,
    ) -> None:
        """build_select with no column list projects all columns."""
        sql = tm.ok(service.build_select("USERS"))
        tm.that(sql, has=["SELECT", "*", "USERS"])

    def test_build_insert_statement_binds_columns(
        self,
        service: FlextDbOracleServices,
    ) -> None:
        """build_insert_statement produces an INSERT with named binds."""
        sql = tm.ok(service.build_insert_statement("USERS", ["ID", "NAME"]))
        tm.that(sql, has=["INSERT INTO", "USERS", ":ID", ":NAME"])

    def test_build_update_statement_sets_and_filters(
        self,
        service: FlextDbOracleServices,
    ) -> None:
        """build_update_statement produces an UPDATE with SET and WHERE binds."""
        sql = tm.ok(service.build_update_statement("USERS", ["NAME"], ["ID"]))
        tm.that(sql, has=["UPDATE", "SET", ":NAME", "WHERE", ":ID"])

    def test_build_delete_statement_filters_by_where(
        self,
        service: FlextDbOracleServices,
    ) -> None:
        """build_delete_statement produces a DELETE constrained by WHERE binds."""
        sql = tm.ok(service.build_delete_statement("USERS", ["ID"]))
        tm.that(sql, has=["DELETE FROM", "USERS", "WHERE", ":ID"])

    def test_create_table_ddl_from_column_models(
        self,
        service: FlextDbOracleServices,
    ) -> None:
        """create_table_ddl compiles CREATE TABLE with the column definitions."""
        columns: list[p.DbOracle.Column] = [
            m.DbOracle.Column(name="ID", data_type="NUMBER", nullable=False),
        ]
        sql = tm.ok(service.create_table_ddl("ACCOUNTS", columns))
        tm.that(sql, has=["CREATE TABLE", "ACCOUNTS", "ID", "NUMBER"])

    def test_drop_table_ddl(self, service: FlextDbOracleServices) -> None:
        """drop_table_ddl compiles a DROP TABLE for the named table."""
        sql = tm.ok(service.drop_table_ddl("ACCOUNTS"))
        tm.that(sql, has=["DROP TABLE", "ACCOUNTS"])

    def test_build_create_index_statement_success(
        self,
        service: FlextDbOracleServices,
    ) -> None:
        """A well-formed index config compiles to a CREATE INDEX statement."""
        sql = tm.ok(
            service.build_create_index_statement({
                "index_name": "IX_USERS_ID",
                "table_name": "USERS",
                "columns": ["ID"],
            }),
        )
        tm.that(sql, has=["CREATE INDEX", "IX_USERS_ID", "USERS", "ID"])

    def test_build_create_index_rejects_invalid_payload(
        self,
        service: FlextDbOracleServices,
    ) -> None:
        """An index config missing required keys fails with a validation error."""
        result = service.build_create_index_statement({"unexpected": "value"})
        tm.fail(result, has="Invalid CREATE INDEX settings")

    def test_build_create_index_rejects_empty_columns(
        self,
        service: FlextDbOracleServices,
    ) -> None:
        """An index definition with no columns is rejected."""
        result = service.build_create_index_statement({
            "index_name": "IX_EMPTY",
            "table_name": "USERS",
            "columns": [],
        })
        tm.fail(result, has="at least one column")
