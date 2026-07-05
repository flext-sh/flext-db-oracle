"""Behavioral tests for FlextDbOracleExceptions public contract.

Exercises the observable contract of the Oracle exception family: message
propagation, Oracle-specific metadata fields, flext-core inheritance, and
raise/catch semantics. No live Oracle container is required — the exception
classes are pure value types whose contract is fully observable in-process.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from collections.abc import Callable

import pytest

from flext_core import e
from flext_db_oracle.exceptions import FlextDbOracleExceptions, e as oracle_e


class TestsFlextDbOracleOracleExceptions:
    """Behavioral contract for the Oracle exception family."""

    def test_family_alias_exposes_facade(self) -> None:
        """The `e` alias exported by the module is the facade class itself."""
        assert oracle_e is FlextDbOracleExceptions

    @pytest.mark.parametrize(
        "factory",
        [
            lambda: FlextDbOracleExceptions.Error("boom"),
            lambda: FlextDbOracleExceptions.OracleConnectionError("boom"),
            lambda: FlextDbOracleExceptions.ProcessingError("boom"),
            lambda: FlextDbOracleExceptions.OracleTimeoutError("boom"),
        ],
        ids=["error", "connection", "processing", "timeout"],
    )
    def test_message_is_preserved_and_rendered(
        self,
        factory: Callable[[], FlextDbOracleExceptions.Error],
    ) -> None:
        """Every family member preserves its message on the public surface."""
        exc = factory()

        assert exc.message == "boom"
        assert "boom" in str(exc)

    @pytest.mark.parametrize(
        ("factory", "expected_base"),
        [
            (lambda: FlextDbOracleExceptions.Error("m"), e.BaseError),
            (
                lambda: FlextDbOracleExceptions.OracleConnectionError("m"),
                e.ConnectionError,
            ),
            (
                lambda: FlextDbOracleExceptions.ProcessingError("m"),
                e.OperationError,
            ),
            (
                lambda: FlextDbOracleExceptions.OracleTimeoutError("m"),
                e.TimeoutError,
            ),
        ],
        ids=["error", "connection", "processing", "timeout"],
    )
    def test_members_inherit_flext_core_categories(
        self,
        factory: Callable[[], BaseException],
        expected_base: type[BaseException],
    ) -> None:
        """Each Oracle error is-a its flext-core category and an e.BaseError."""
        exc = factory()

        assert isinstance(exc, expected_base)
        assert isinstance(exc, e.BaseError)
        assert isinstance(exc, Exception)

    def test_error_carries_oracle_metadata(self) -> None:
        """Error exposes Oracle error code and SQL state as public fields."""
        exc = FlextDbOracleExceptions.Error(
            "table missing",
            oracle_error_code="ORA-00942",
            sql_state="42S02",
        )

        assert exc.oracle_error_code == "ORA-00942"
        assert exc.sql_state == "42S02"

    def test_connection_error_carries_tns_metadata(self) -> None:
        """OracleConnectionError exposes TNS and connection-string context."""
        exc = FlextDbOracleExceptions.OracleConnectionError(
            "cannot connect",
            tns_error="TNS-12154",
            connection_string="host:1521/XEPDB1",
        )

        assert exc.tns_error == "TNS-12154"
        assert exc.connection_string == "host:1521/XEPDB1"

    def test_processing_error_carries_operation_metadata(self) -> None:
        """ProcessingError exposes operation type and processing stage."""
        exc = FlextDbOracleExceptions.ProcessingError(
            "insert failed",
            operation_type="INSERT",
            processing_stage="parse",
        )

        assert exc.operation_type == "INSERT"
        assert exc.processing_stage == "parse"

    def test_timeout_error_carries_query_metadata(self) -> None:
        """OracleTimeoutError exposes query id and elapsed time."""
        exc = FlextDbOracleExceptions.OracleTimeoutError(
            "query timed out",
            query_id="q-42",
            elapsed_time=1.5,
        )

        assert exc.query_id == "q-42"
        assert exc.elapsed_time == pytest.approx(1.5)

    @pytest.mark.parametrize(
        "factory",
        [
            lambda: FlextDbOracleExceptions.Error("m"),
            lambda: FlextDbOracleExceptions.OracleConnectionError("m"),
            lambda: FlextDbOracleExceptions.ProcessingError("m"),
            lambda: FlextDbOracleExceptions.OracleTimeoutError("m"),
        ],
        ids=["error", "connection", "processing", "timeout"],
    )
    def test_metadata_defaults_to_none_when_omitted(
        self,
        factory: Callable[[], BaseException],
    ) -> None:
        """Optional metadata is absent (None) unless explicitly supplied."""
        exc = factory()

        optional_fields = (
            "oracle_error_code",
            "sql_state",
            "tns_error",
            "connection_string",
            "operation_type",
            "processing_stage",
            "query_id",
            "elapsed_time",
        )
        present = {
            name: getattr(exc, name)
            for name in optional_fields
            if hasattr(exc, name)
        }
        assert all(value is None for value in present.values())

    def test_connection_error_is_raisable_and_catchable_as_category(self) -> None:
        """A raised OracleConnectionError is caught via its flext-core category."""
        exc = FlextDbOracleExceptions.OracleConnectionError(
            "unreachable",
            tns_error="TNS-12541",
        )

        def _raise() -> None:
            raise exc

        with pytest.raises(e.ConnectionError) as caught:
            _raise()

        assert caught.value is exc
        assert exc.tns_error == "TNS-12541"
        assert "unreachable" in str(caught.value)

    def test_raise_from_preserves_cause_chain(self) -> None:
        """Wrapping a driver error preserves the original via __cause__."""
        root = ValueError("ORA-01017: invalid username/password")

        def _translate() -> None:
            try:
                raise root
            except ValueError as driver_error:
                wrapped = FlextDbOracleExceptions.Error(
                    "authentication failed",
                    oracle_error_code="ORA-01017",
                )
                raise wrapped from driver_error

        with pytest.raises(FlextDbOracleExceptions.Error) as caught:
            _translate()

        assert caught.value.__cause__ is root
        assert caught.value.oracle_error_code == "ORA-01017"
