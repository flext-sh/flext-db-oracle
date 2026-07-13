"""Behavioral tests for FlextDbOracleExceptions public contract.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import pytest

from flext_core import e
from flext_db_oracle import FlextDbOracleExceptions


class TestsFlextDbOracleExceptions:
    """Public-contract behavior of the Oracle exception family."""

    def test_error_carries_message_in_str(self) -> None:
        """Error exposes its message through str()."""
        error = FlextDbOracleExceptions.Error("boom failure")

        assert "boom failure" in str(error)

    def test_error_is_raisable_and_catchable_as_base_error(self) -> None:
        """Error propagates through pytest.raises as an e.BaseError."""
        message = "explode now"
        with pytest.raises(e.BaseError, match="explode"):
            raise FlextDbOracleExceptions.Error(message)

    def test_error_metadata_defaults_to_none(self) -> None:
        """Error metadata fields default to None when omitted."""
        error = FlextDbOracleExceptions.Error("no metadata")

        assert error.oracle_error_code is None
        assert error.sql_state is None

    def test_error_preserves_supplied_metadata(self) -> None:
        """Error retains oracle_error_code and sql_state as given."""
        error = FlextDbOracleExceptions.Error(
            "with metadata",
            oracle_error_code="ORA-12345",
            sql_state="08001",
        )

        assert error.oracle_error_code == "ORA-12345"
        assert error.sql_state == "08001"

    def test_connection_error_preserves_metadata(self) -> None:
        """OracleConnectionError retains TNS and connection-string metadata."""
        error = FlextDbOracleExceptions.OracleConnectionError(
            "Connection failed",
            tns_error="TNS-12541",
            connection_string="host:1521/svc",
        )

        assert "Connection failed" in str(error)
        assert error.tns_error == "TNS-12541"
        assert error.connection_string == "host:1521/svc"

    def test_processing_error_preserves_metadata(self) -> None:
        """ProcessingError retains operation-type and stage metadata."""
        error = FlextDbOracleExceptions.ProcessingError(
            "batch failed",
            operation_type="INSERT",
            processing_stage="commit",
        )

        assert error.operation_type == "INSERT"
        assert error.processing_stage == "commit"

    def test_timeout_error_preserves_metadata(self) -> None:
        """OracleTimeoutError retains query-id and elapsed-time metadata."""
        error = FlextDbOracleExceptions.OracleTimeoutError(
            "query timed out",
            query_id="q-42",
            elapsed_time=12.5,
        )

        assert error.query_id == "q-42"
        assert error.elapsed_time == pytest.approx(12.5)

    @pytest.mark.parametrize(
        ("factory", "base"),
        [
            (FlextDbOracleExceptions.Error, e.BaseError),
            (FlextDbOracleExceptions.OracleConnectionError, e.ConnectionError),
            (FlextDbOracleExceptions.ProcessingError, e.OperationError),
            (FlextDbOracleExceptions.OracleTimeoutError, e.TimeoutError),
        ],
    )
    def test_each_error_extends_its_flext_core_base(
        self,
        factory: type[e.BaseError],
        base: type[e.BaseError],
    ) -> None:
        """Every Oracle error is a subclass of its flext-core base contract."""
        assert issubclass(factory, base)
        assert isinstance(factory("msg"), base)

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
        self,
        factory: type[e.BaseError],
    ) -> None:
        """Each Oracle error can be raised and caught as a builtin Exception."""
        message = "raised message"
        with pytest.raises(Exception, match="raised message") as exc_info:
            raise factory(message)

        assert "raised message" in str(exc_info.value)
