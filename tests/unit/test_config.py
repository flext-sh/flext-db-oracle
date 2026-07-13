"""Behavioral unit tests for flext_db_oracle.settings module.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from flext_tests import tm

from flext_db_oracle import FlextDbOracleSettings, c

# NOTE (multi-agent): ADR-005 — settings is a layer-0 scalar namespace under
# settings.DbOracle.*. The flat fields, from_url/from_env factories and custom
# validators were removed by design; tests cover the namespaced contract only.


class TestsFlextDbOracleSettings:
    """Public contract of FlextDbOracleSettings (namespace, defaults, singleton)."""

    def test_defaults_match_published_oracle_constants(self) -> None:
        """A settings object with no overrides exposes the documented defaults."""
        settings = FlextDbOracleSettings()

        tm.that(settings.DbOracle.host, eq=c.DbOracle.DEFAULT_HOST)
        tm.that(settings.DbOracle.port, eq=c.DbOracle.DEFAULT_PORT)
        tm.that(settings.DbOracle.service_name, eq=c.DbOracle.DEFAULT_SERVICE_NAME)
        tm.that(settings.DbOracle.username, eq=c.DbOracle.DEFAULT_USERNAME)
        tm.that(settings.DbOracle.timeout, eq=c.DbOracle.DEFAULT_TIMEOUT)
        tm.that(settings.DbOracle.pool_min, eq=c.DbOracle.DEFAULT_POOL_MIN)
        tm.that(settings.DbOracle.pool_max, eq=c.DbOracle.DEFAULT_POOL_MAX)
        tm.that(settings.DbOracle.name, eq=c.DbOracle.DEFAULT_DATABASE_NAME)
        tm.that(settings.DbOracle.sid, none=True)
        tm.that(settings.DbOracle.enable_dispatcher, eq=False)

    def test_model_dump_exposes_every_public_field(self) -> None:
        """model_dump surfaces the full public field set inside the namespace."""
        dumped = FlextDbOracleSettings().model_dump()

        expected_fields = {
            "host",
            "port",
            "service_name",
            "username",
            "password",
            "timeout",
            "pool_min",
            "pool_max",
            "sid",
            "name",
            "ssl_cert_file",
            "ssl_server_cert_dn",
            "enable_dispatcher",
        }
        assert expected_fields <= set(dumped["DbOracle"])

    def test_namespace_overrides_round_trip(self) -> None:
        """Caller-provided DbOracle values are stored and readable."""
        settings = FlextDbOracleSettings(
            DbOracle={
                "host": "db.internal",
                "port": 1522,
                "username": "appuser",
                "service_name": "PRODSVC",
                "password": "apppass",
            },
        )

        tm.that(settings.DbOracle.host, eq="db.internal")
        tm.that(settings.DbOracle.port, eq=1522)
        tm.that(settings.DbOracle.username, eq="appuser")
        tm.that(settings.DbOracle.service_name, eq="PRODSVC")
        tm.that(settings.DbOracle.password, eq="apppass")

    def test_sid_only_configuration_is_accepted_without_service_name(self) -> None:
        """A legacy SID connection is valid even with a blank service_name."""
        settings = FlextDbOracleSettings(DbOracle={"service_name": "", "sid": "legacy"})

        tm.that(settings.DbOracle.sid, eq="legacy")
        tm.that(settings.DbOracle.service_name, eq="")

    def test_password_defaults_to_empty_string(self) -> None:
        """Omitting the password yields an empty string, not a None-crash."""
        tm.that(FlextDbOracleSettings().DbOracle.password, eq="")

    def test_ssl_fields_default_to_none(self) -> None:
        """SSL certificate fields are unset by default."""
        settings = FlextDbOracleSettings()

        tm.that(settings.DbOracle.ssl_cert_file, none=True)
        tm.that(settings.DbOracle.ssl_server_cert_dn, none=True)

    def test_explicit_ssl_fields_are_preserved(self) -> None:
        """Explicit SSL certificate values round-trip through the namespace."""
        settings = FlextDbOracleSettings(
            DbOracle={
                "ssl_cert_file": "/etc/oracle/cert.pem",
                "ssl_server_cert_dn": "CN=oracle,O=flext",
            },
        )

        tm.that(settings.DbOracle.ssl_cert_file, eq="/etc/oracle/cert.pem")
        tm.that(settings.DbOracle.ssl_server_cert_dn, eq="CN=oracle,O=flext")

    def test_fetch_global_returns_shared_singleton(self) -> None:
        """fetch_global without overrides yields the shared singleton instance."""
        first = FlextDbOracleSettings.fetch_global()
        second = FlextDbOracleSettings.fetch_global()

        assert first is second

    def test_fetch_global_overrides_return_isolated_clone(self) -> None:
        """fetch_global with overrides returns a clone; the singleton is untouched."""
        singleton = FlextDbOracleSettings.fetch_global()
        clone = FlextDbOracleSettings.fetch_global(
            overrides={"DbOracle": {"host": "clone-host"}},
        )

        assert clone is not singleton
        tm.that(clone.DbOracle.host, eq="clone-host")
        tm.that(singleton.DbOracle.host, eq=c.DbOracle.DEFAULT_HOST)

    def test_clone_preserves_canonical_type(self) -> None:
        """The namespaced clone returns the canonical settings type."""
        clone = FlextDbOracleSettings.fetch_global().clone(
            DbOracle={"host": "test", "port": 9000},
        )

        tm.that(clone, is_=FlextDbOracleSettings)
        tm.that(clone.DbOracle.host, eq="test")
        tm.that(clone.DbOracle.port, eq=9000)
