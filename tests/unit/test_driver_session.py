"""Behavioral tests for the caller-owned Oracle driver session contract.

``u.DbOracle.build_engine`` is observed through the public engine URL, the
pool size and the driver arguments SQLAlchemy hands to the DBAPI in its
public ``do_connect`` event (the listener stops the checkout before any
socket opens). ``fetch_models`` and ``execute_driver_sql`` run on a real
in-memory SQLAlchemy connection the test owns (``memory_connection``
in the unit conftest), so the injected connection's
own state (a TEMP table) proves the work stayed on that connection.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from collections.abc import Mapping, MutableMapping

import oracledb
import pytest
from sqlalchemy import Connection, Engine, event
from sqlalchemy.engine.interfaces import Dialect
from sqlalchemy.pool import ConnectionPoolEntry

from flext_db_oracle import FlextDbOracleSettings
from tests import c, m, t, tm, u


@pytest.mark.unit
class TestsFlextDbOracleDriverSession:
    """Public contract of the engine builder and connection-scoped helpers."""

    _DESCRIPTOR = (
        "(DESCRIPTION=(ADDRESS=(PROTOCOL=TCPS)(HOST=adw.example)(PORT=1522))"
        "(CONNECT_DATA=(SERVICE_NAME=svc_high)))"
    )

    class CheckoutStopped(Exception):
        """Raised by the do_connect listener once the driver arguments exist."""

    class SampleRow(m.BaseModel):
        """Scenario row model mapped from the in-memory result set."""

        id: int
        ratio: float
        raw: bytes
        label: str

    @staticmethod
    def _settings(overrides: t.JsonMapping) -> FlextDbOracleSettings:
        """Build settings with a password plus the scenario overrides.

        Returns:
            The validated settings instance.

        """
        return FlextDbOracleSettings.model_validate({
            "DbOracle": {"username": "app", "password": "s3cr:t@x", **overrides},
        })

    @classmethod
    def _driver_arguments(cls, engine: Engine) -> Mapping[str, t.Scalar]:
        """Capture the DBAPI keyword arguments of the engine's first checkout.

        Returns:
            The keyword arguments SQLAlchemy passes to ``oracledb.connect``.

        """
        captured: MutableMapping[str, t.Scalar] = {}

        def stop_checkout(
            dialect: Dialect,
            conn_rec: ConnectionPoolEntry,
            cargs: tuple[str, ...],
            cparams: Mapping[str, t.Scalar],
        ) -> None:
            _ = dialect, conn_rec, cargs
            captured.update(cparams)
            raise cls.CheckoutStopped

        event.listen(engine, "do_connect", stop_checkout)
        with pytest.raises(cls.CheckoutStopped):
            engine.connect()
        return captured

    # ------------------------------------------------------------------ #
    # settings                                                           #
    # ------------------------------------------------------------------ #

    @staticmethod
    def test_dsn_defaults_to_none_and_round_trips() -> None:
        """``dsn`` is unset by default and stores a caller descriptor verbatim."""
        tm.that(FlextDbOracleSettings().DbOracle.dsn, none=True)
        settings = FlextDbOracleSettings.model_validate({
            "DbOracle": {"dsn": TestsFlextDbOracleDriverSession._DESCRIPTOR},
        })
        tm.that(settings.DbOracle.dsn, eq=TestsFlextDbOracleDriverSession._DESCRIPTOR)

    @staticmethod
    def test_pool_max_below_pool_min_is_rejected() -> None:
        """A pool maximum lower than its minimum fails settings validation."""
        with pytest.raises(ValueError, match="pool_max"):
            FlextDbOracleSettings.model_validate({
                "DbOracle": {"pool_min": 5, "pool_max": 4},
            })

    # ------------------------------------------------------------------ #
    # build_engine                                                       #
    # ------------------------------------------------------------------ #

    @classmethod
    def test_build_engine_uses_host_port_service_without_dsn(cls) -> None:
        """Without ``dsn`` the URL carries host, port and service name."""
        settings = cls._settings({
            "host": "db.internal",
            "port": 1530,
            c.ContextKey.SERVICE_NAME: "ORCLPDB",
            "pool_min": 3,
            "pool_max": 7,
        })
        engine = u.DbOracle.build_engine(settings)
        tm.that(engine.url.host, eq="db.internal")
        tm.that(engine.url.port, eq=1530)
        tm.that(engine.url.query["service_name"], eq="ORCLPDB")
        tm.that(engine.url.username, eq="app")
        tm.that(engine.url.password, eq="s3cr:t@x")
        tm.that(engine.pool.size(), eq=3)
        arguments = cls._driver_arguments(engine)
        tm.that(str(arguments["dsn"]), has="db.internal")
        tm.that(arguments["tcp_connect_timeout"], eq=settings.DbOracle.timeout)
        tm.fail("mode" in arguments)

    @classmethod
    def test_build_engine_sends_dsn_and_sysdba_mode_to_driver(cls) -> None:
        """A configured ``dsn`` and SYSDBA mode reach the driver arguments."""
        settings = cls._settings({"dsn": cls._DESCRIPTOR, "mode": "SYSDBA"})
        engine = u.DbOracle.build_engine(settings)
        tm.that(engine.url.host, none=True)
        arguments = cls._driver_arguments(engine)
        tm.that(arguments["dsn"], eq=cls._DESCRIPTOR)
        tm.that(arguments["mode"], eq=oracledb.AUTH_MODE_SYSDBA)
        tm.that(arguments["user"], eq="app")

    @classmethod
    def test_build_engine_merges_caller_connect_args(cls) -> None:
        """Caller driver arguments the settings do not own are forwarded."""
        engine = u.DbOracle.build_engine(
            cls._settings({"dsn": cls._DESCRIPTOR}),
            {"config_dir": "/etc/oracle/tns", "expire_time": 2},
        )
        arguments = cls._driver_arguments(engine)
        tm.that(arguments["config_dir"], eq="/etc/oracle/tns")
        tm.that(arguments["expire_time"], eq=2)
        tm.that(arguments["dsn"], eq=cls._DESCRIPTOR)

    @classmethod
    def test_build_engine_rejects_connect_args_owned_by_settings(cls) -> None:
        """A caller argument that repeats a settings-owned one fails loud."""
        with pytest.raises(ValueError, match="dsn"):
            u.DbOracle.build_engine(
                cls._settings({"dsn": cls._DESCRIPTOR}),
                {"dsn": "other_alias"},
            )

    @staticmethod
    def test_build_engine_requires_password() -> None:
        """Settings without a password cannot build an engine."""
        with pytest.raises(ValueError, match="Password is required"):
            u.DbOracle.build_engine(FlextDbOracleSettings())

    # ------------------------------------------------------------------ #
    # connection-scoped execution                                        #
    # ------------------------------------------------------------------ #

    @classmethod
    def test_fetch_models_maps_native_values_on_caller_connection(
        cls,
        memory_connection: Connection,
    ) -> None:
        """Rows from the caller's connection become typed models, values native."""
        created = u.DbOracle.execute_driver_sql(
            "CREATE TEMP TABLE sample (id INTEGER, ratio REAL, raw BLOB, label TEXT)",
            connection=memory_connection,
        )
        tm.that(created, eq=0)
        inserted = u.DbOracle.execute_driver_sql(
            "INSERT INTO sample VALUES (:id, :ratio, :raw, 'HH24:MI')",
            {"id": 7, "ratio": 0.25, "raw": b"\x00\xff"},
            connection=memory_connection,
        )
        tm.that(inserted, eq=1)
        rows = u.DbOracle.fetch_models(
            "SELECT id, ratio, raw, label FROM sample WHERE id = :id",
            {"id": 7},
            model=cls.SampleRow,
            connection=memory_connection,
        )
        tm.that(len(rows), eq=1)
        row = rows[0]
        tm.that(row, is_=cls.SampleRow)
        tm.that(row.id, eq=7)
        tm.that(row.ratio, eq=0.25)
        tm.that(row.raw, eq=b"\x00\xff")
        tm.that(row.label, eq="HH24:MI")

    @classmethod
    def test_fetch_models_returns_empty_sequence_without_rows(
        cls,
        memory_connection: Connection,
    ) -> None:
        """A query with no matching rows yields an empty sequence."""
        _ = u.DbOracle.execute_driver_sql(
            "CREATE TEMP TABLE sample (id INTEGER, ratio REAL, raw BLOB, label TEXT)",
            connection=memory_connection,
        )
        rows = u.DbOracle.fetch_models(
            "SELECT id, ratio, raw, label FROM sample",
            model=cls.SampleRow,
            connection=memory_connection,
        )
        tm.that(len(rows), eq=0)


__all__: list[str] = ["TestsFlextDbOracleDriverSession"]
