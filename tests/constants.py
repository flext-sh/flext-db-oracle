"""Test constants for flext-db-oracle.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import Final

from flext_tests import FlextTestsConstants

from flext_db_oracle import FlextDbOracleConstants


class TestsFlextDbOracleConstants(FlextTestsConstants, FlextDbOracleConstants):
    """Test constants for flext-db-oracle."""

    class DbOracle(FlextDbOracleConstants.DbOracle):
        """DbOracle domain test constants."""

        class Tests:
            """Test-specific constants."""

            class Paths:
                """Test path constants."""

                TEST_INPUT_DIR: Final[str] = "tests/fixtures/data/input"
                TEST_OUTPUT_DIR: Final[str] = "tests/fixtures/data/output"
                TEST_TEMP_PREFIX: Final[str] = "flext_db_oracle_test_"

            class TestConnection:
                """Connection test constants."""

                TEST_SERVICE_NAME: Final[str] = "TEST_SERVICE"
                TEST_SID: Final[str] = "TEST_SID"
                TEST_TNS_NAME: Final[str] = "TEST_TNS"
                TEST_HOST: Final[str] = "localhost"
                TEST_PORT: Final[int] = 1521
                TEST_USER: Final[str] = "test_user"
                TEST_PASSWORD: Final[str] = "test_password"

            class TestDatabase:
                """Database test constants."""

                TEST_SCHEMA: Final[str] = "TEST_SCHEMA"
                TEST_TABLE: Final[str] = "TEST_TABLE"
                TEST_COLUMN: Final[str] = "TEST_COLUMN"
                TEST_INDEX: Final[str] = "TEST_INDEX"

            class TestQuery:
                """Query test constants."""

                TEST_SELECT_QUERY: Final[str] = (
                    "SELECT * FROM test_table WHERE id = :id"
                )
                TEST_INSERT_QUERY: Final[str] = (
                    "INSERT INTO test_table (id, name) VALUES (:id, :name)"
                )
                TEST_UPDATE_QUERY: Final[str] = (
                    "UPDATE test_table SET name = :name WHERE id = :id"
                )
                TEST_DELETE_QUERY: Final[str] = "DELETE FROM test_table WHERE id = :id"

            class TestData:
                """Data test constants."""

                TEST_DATA_TYPE: Final[str] = "VARCHAR2"
                TEST_DATA_SIZE: Final[int] = 255
                TEST_NULLABLE: Final[bool] = True


c = TestsFlextDbOracleConstants
__all__ = ["TestsFlextDbOracleConstants", "c"]
