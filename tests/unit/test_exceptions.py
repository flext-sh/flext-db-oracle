"""Behavioral tests for FlextDbOracleExceptions public contract.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import pytest

from flext_core import e
from flext_db_oracle import FlextDbOracleExceptions
from flext_tests import tm


class TestsFlextDbOracleExceptions:
    """Public-contract behavior of the Oracle exception family."""

    def test_error_carries_message_in_str(self) -> None:
        """Error exposes its message through str()."""
        error = FlextDbOracleExceptions.Error("boom failure")

        tm.that(str(error), has="boom failure")

    def test_error_is_raisable_and_catchable_as_base_error(self) -> None:
        """Error propagates through pytest.raises as an e.BaseError."""
        message = "explode now"
        with pytest.raises(e.BaseError, match="explode"):
            raise FlextDbOracleExceptions.Error(message)

    def test_error_metadata_defaults_to_none(self) -> None:
        """Error metadata fields default to None when omitted."""
        error = FlextDbOracleExceptions.Error("no metadata")

        tm.that(error.oracle_error_code, none=True)
        tm.that(error.sql_state, none=True)

    def test_error_preserves_supplied_metadata(self) -> None:
        """Error retains oracle_error_code and sql_state as given."""
        error = FlextDbOracleExceptions.Error(
            "with metadata", oracle_error_code="ORA-12345", sql_state="08001"
        )

        tm.that(error.oracle_error_code, eq="ORA-12345")
        tm.that(error.sql_state, eq="08001")

    def test_connection_error_preserves_metadata(self) -> None:
        """OracleConnectionError retains TNS and connection-string metadata."""
        error = FlextDbOracleExceptions.OracleConnectionError(
            "Connection failed",
            tns_error="TNS-12541",
            connection_string="host:1521/svc",
        )

        tm.that(str(error), has="Connection failed")
        tm.that(error.tns_error, eq="TNS-12541")
        tm.that(error.connection_string, eq="host:1521/svc")

    def test_processing_error_preserves_metadata(self) -> None:
        """ProcessingError retains operation-type and stage metadata."""
        error = FlextDbOracleExceptions.ProcessingError(
            "batch failed", operation_type="INSERT", processing_stage="commit"
        )

        tm.that(error.operation_type, eq="INSERT")
        tm.that(error.processing_stage, eq="commit")

    def test_timeout_error_preserves_metadata(self) -> None:
        """OracleTimeoutError retains query-id and elapsed-time metadata."""
        error = FlextDbOracleExceptions.OracleTimeoutError(
            "query timed out", query_id="q-42", elapsed_time=12.5
        )

        tm.that(error.query_id, eq="q-42")
        tm.that(error.elapsed_time, eq=pytest.approx(12.5))

    @pytest.mark.parametrize(
        ("factory", "base"),
        [
            (FlextDbOracleExceptions.Error, e.BaseError),
            (FlextDbOracleExceptions.OracleConnectionError, e.FlextConnectionError),
            (FlextDbOracleExceptions.ProcessingError, e.OperationError),
            (FlextDbOracleExceptions.OracleTimeoutError, e.FlextTimeoutError),
        ],
    )
    def test_each_error_extends_its_flext_core_base(
        self, factory: type[e.BaseError], base: type[e.BaseError]
    ) -> None:
        """Every Oracle error is a subclass of its flext-core base contract."""
        assert issubclass(factory, base)
        tm.that(factory("msg"), is_=base)

    def test_family_extends_flext_core_exceptions(self) -> None:
        """FlextDbOracleExceptions composes the flext-core exceptions facade."""
        assert issubclass(FlextDbOracleExceptions, e)

    @pytest.mark.parametrize(
        "factory",
        [
            FlextDbOracleExceptions.Error,
            FlextDbOracleExceptions.OracleConnectionError,
            FlextDbOracleExceptions.ProcessingError,
            FlextDbOracleExceptions.OracleTimeoutError,
        ],
    )
    def test_each_error_raises_and_is_catchable_as_exception(
        self, factory: type[e.BaseError]
    ) -> None:
        """Each Oracle error can be raised and caught as a builtin Exception."""
        message = "raised message"
        with pytest.raises(Exception, match="raised message") as exc_info:
            raise factory(message)

        tm.that(str(exc_info.value), has="raised message")
