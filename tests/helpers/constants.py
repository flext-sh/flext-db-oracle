"""Test constants for flext-db-oracle tests.

Centralized constants for test fixtures, factories, and test data.
Does NOT duplicate src/flext_db_oracle/constants.py - only test-specific constants.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import Final

from flext_db_oracle.constants import FlextDbOracleConstants


class TestsConstants(FlextDbOracleConstants):
    """Centralized test constants following flext-core nested class pattern."""

    class Paths:
        """Test path constants."""

        TEST_INPUT_DIR: Final[str] = "tests/fixtures/data/input"
        TEST_OUTPUT_DIR: Final[str] = "tests/fixtures/data/output"
        TEST_TEMP_PREFIX: Final[str] = "flext_db_oracle_test_"

    class Connection:
        """Connection test constants."""

        TEST_SERVICE_NAME: Final[str] = "TEST_SERVICE"
        TEST_SID: Final[str] = "TEST_SID"
        TEST_TNS_NAME: Final[str] = "TEST_TNS"
        TEST_HOST: Final[str] = "localhost"
        TEST_PORT: Final[int] = 1521
        TEST_USER: Final[str] = "test_user"
        TEST_PASSWORD: Final[str] = "test_password"

    class Database:
        """Database test constants."""

        TEST_SCHEMA: Final[str] = "TEST_SCHEMA"
        TEST_TABLE: Final[str] = "TEST_TABLE"
        TEST_COLUMN: Final[str] = "TEST_COLUMN"
        TEST_INDEX: Final[str] = "TEST_INDEX"

    class Query:
        """Query test constants."""

        TEST_SELECT_QUERY: Final[str] = "SELECT * FROM test_table WHERE id = :id"
        TEST_INSERT_QUERY: Final[str] = (
            "INSERT INTO test_table (id, name) VALUES (:id, :name)"
        )
        TEST_UPDATE_QUERY: Final[str] = (
            "UPDATE test_table SET name = :name WHERE id = :id"
        )
        TEST_DELETE_QUERY: Final[str] = "DELETE FROM test_table WHERE id = :id"

    class Data:
        """Data test constants."""

        TEST_DATA_TYPE: Final[str] = "VARCHAR2"
        TEST_DATA_SIZE: Final[int] = 255
        TEST_NULLABLE: Final[bool] = True


# Standardized short name for use in tests
c = TestsConstants
__all__ = ["TestsConstants", "c"]
