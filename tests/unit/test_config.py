"""Behavioral unit tests for flext_db_oracle.settings module.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import pytest

from flext_db_oracle import FlextDbOracleSettings, c, m


class TestsFlextDbOracleSettings:
    """Public contract of FlextDbOracleSettings (fields, validation, factories)."""

    def test_defaults_match_published_oracle_constants(self) -> None:
        """A settings object with no overrides exposes the documented defaults."""
        settings = FlextDbOracleSettings()

        assert settings.host == c.DbOracle.DEFAULT_HOST
        assert settings.port == c.DbOracle.DEFAULT_PORT
        assert settings.service_name == c.DbOracle.DEFAULT_SERVICE_NAME
        assert settings.username == c.DbOracle.DEFAULT_USERNAME
        assert settings.timeout == c.DbOracle.DEFAULT_TIMEOUT
        assert settings.pool_min == c.DbOracle.DEFAULT_POOL_MIN
        assert settings.pool_max == c.DbOracle.DEFAULT_POOL_MAX
        assert settings.name == c.DbOracle.DEFAULT_DATABASE_NAME
        assert settings.sid is None
        assert settings.enable_dispatcher is False

    def test_model_dump_exposes_every_public_field(self) -> None:
        """model_dump surfaces the full public field set for serialization."""
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
        assert expected_fields <= set(dumped)

    @pytest.mark.parametrize(
        ("raw", "expected"),
        [
            ("prodsvc", "PRODSVC"),
            ("  mixedCase  ", "MIXEDCASE"),
            ("ALREADY", "ALREADY"),
        ],
    )
    def test_service_name_is_stripped_and_uppercased(
        self, raw: str, expected: str
    ) -> None:
        """service_name normalizes whitespace and casing per its constraints."""
        assert FlextDbOracleSettings(service_name=raw).service_name == expected

    def test_sid_is_stripped_and_uppercased_when_provided(self) -> None:
        """SID honors the same normalization contract as service_name."""
        settings = FlextDbOracleSettings(service_name="", sid="  orcl  ")

        assert settings.sid == "ORCL"

    def test_password_string_input_is_wrapped_and_renders_its_secret(self) -> None:
        """A plain string password is coerced into the password value object."""
        settings = FlextDbOracleSettings(password="s3cr3t")

        assert str(settings.password) == "s3cr3t"

    def test_password_defaults_to_empty_secret(self) -> None:
        """Omitting the password yields an empty rendered secret, not None-crash."""
        assert str(FlextDbOracleSettings().password) == ""

    def test_ssl_server_cert_dn_falls_back_to_cert_file(self) -> None:
        """When only the cert file is supplied, the server DN mirrors it."""
        settings = FlextDbOracleSettings(ssl_cert_file="/etc/oracle/cert.pem")

        assert settings.ssl_server_cert_dn == "/etc/oracle/cert.pem"

    def test_explicit_ssl_server_cert_dn_is_preserved(self) -> None:
        """An explicit server DN is not overwritten by the cert-file fallback."""
        settings = FlextDbOracleSettings(
            ssl_cert_file="/etc/oracle/cert.pem",
            ssl_server_cert_dn="CN=oracle,O=flext",
        )

        assert settings.ssl_server_cert_dn == "CN=oracle,O=flext"

    @pytest.mark.parametrize(
        "overrides",
        [
            {"host": ""},
            {"host": "   "},
            {"username": ""},
            {"port": 0},
            {"port": c.DbOracle.MAX_PORT + 1},
            {"service_name": "", "sid": None},
        ],
    )
    def test_business_rule_violations_reject_construction(
        self, overrides: dict[str, str | int | None]
    ) -> None:
        """Invariant breaches (empty host/user, bad port, no service) are rejected."""
        with pytest.raises(m.ValidationError):
            FlextDbOracleSettings.model_validate(overrides)

    def test_sid_only_configuration_is_accepted_without_service_name(self) -> None:
        """A legacy SID connection is valid even with a blank service_name."""
        settings = FlextDbOracleSettings(service_name="", sid="legacy")

        assert settings.sid == "LEGACY"
        assert settings.service_name == ""

    def test_from_url_parses_host_port_credentials_and_service(self) -> None:
        """from_url yields a success result populated from the connection URL."""
        result = FlextDbOracleSettings.from_url(
            "oracle://appuser:apppass@db.internal:1522/PRODSVC"
        )

        assert result.success is True
        settings = result.unwrap()
        assert settings.host == "db.internal"
        assert settings.port == 1522
        assert settings.username == "appuser"
        assert settings.service_name == "PRODSVC"
        assert str(settings.password) == "apppass"

    def test_from_url_accepts_oracledb_driver_scheme(self) -> None:
        """The oracle+oracledb driver scheme is a valid connection URL."""
        result = FlextDbOracleSettings.from_url(
            "oracle+oracledb://u:p@host:1600/SVC"
        )

        assert result.success is True
        assert result.unwrap().port == 1600

    def test_from_url_reads_service_name_from_query_string(self) -> None:
        """service_name provided via query parameters is honored."""
        result = FlextDbOracleSettings.from_url(
            "oracle://u:p@host:1521?service_name=QSVC"
        )

        assert result.unwrap().service_name == "QSVC"

    def test_from_url_defaults_service_name_when_absent(self) -> None:
        """A URL with no path or query service falls back to the default service."""
        result = FlextDbOracleSettings.from_url("oracle://u:p@host:1521")

        assert result.unwrap().service_name == c.DbOracle.DEFAULT_SERVICE_NAME

    @pytest.mark.parametrize(
        "url",
        [
            "mysql://u:p@host/db",
            "postgresql://u:p@host/db",
            "http://host/db",
        ],
    )
    def test_from_url_rejects_non_oracle_schemes(self, url: str) -> None:
        """Non-Oracle schemes produce a failure result with a descriptive error."""
        result = FlextDbOracleSettings.from_url(url)

        assert result.success is False
        assert "scheme" in (result.error or "").lower()

    def test_from_env_with_unmatched_prefix_yields_default_settings(self) -> None:
        """from_env with a prefix that matches no vars succeeds with defaults."""
        result = FlextDbOracleSettings.from_env(prefix="ZZ_NO_SUCH_ORACLE_PREFIX_")

        assert result.success is True
        settings = result.unwrap()
        assert isinstance(settings, FlextDbOracleSettings)
        assert settings.host == c.DbOracle.DEFAULT_HOST
