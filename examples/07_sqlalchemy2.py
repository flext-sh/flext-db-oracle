"""SQLAlchemy 2 Example for flext-db-oracle.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

This example demonstrates how to use the flext-db-oracle library
with SQLAlchemy 2 for Oracle database operations including:
"""

import sys
from collections.abc import Iterator
from contextlib import contextmanager

from sqlalchemy import Engine, text

from flext_core import FlextLogger
from flext_db_oracle import FlextDbOracleApi, FlextDbOracleModels

logger = FlextLogger(__name__)


def create_oracle_config() -> FlextDbOracleModels.OracleConfig:
    """Create Oracle configuration from environment variables.

    Returns:
        FlextDbOracleModels.OracleConfig: Validated Oracle configuration.

    Raises:
        ValueError: If configuration loading fails.

    """
    config_result = FlextDbOracleModels.OracleConfig.from_env()
    if not config_result.is_success:
        msg = f"Failed to load configuration: {config_result.error}"
        raise ValueError(msg)
    return config_result.value


@contextmanager
def oracle_connection() -> Iterator[Engine]:
    """Context manager for Oracle SQLAlchemy connection.

    Raises:
        RuntimeError: If connection to Oracle fails.
        NotImplementedError: If engine access is not implemented.

    """
    config = create_oracle_config()
    api = FlextDbOracleApi(config)

    connect_result = api.connect()

    # Use modern FlextResult pattern for clean error handling
    if not connect_result.is_success:
        error_msg = connect_result.error or "Connection failed"
        msg = f"Failed to connect to Oracle: {error_msg}"
        raise RuntimeError(msg)

    try:
        # Get SQLAlchemy engine from API
        # Note: This is a simplified example - actual implementation would need
        # to expose the engine from the API or services layer
        # For now, we'll raise an error since engine access is not implemented
        msg = "Engine access not implemented in this example"
        raise NotImplementedError(msg)

    finally:
        # Cleanup connection
        disconnect_result = api.disconnect()
        if not disconnect_result.is_success:
            logger.warning(f"Failed to disconnect: {disconnect_result.error}")


def demonstrate_basic_queries() -> None:
    """Demonstrate basic SQLAlchemy 2 queries."""
    with oracle_connection() as engine:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT SYSDATE FROM DUAL"))
            result.fetchone()

        # Database version query
        with engine.connect() as conn:
            result = conn.execute(text("SELECT BANNER FROM V$VERSION WHERE ROWNUM = 1"))
            result.fetchone()

        # Session information
        with engine.connect() as conn:
            result = conn.execute(
                text("""
              SELECT
                  USER as current_user,
                  SYS_CONTEXT('USERENV', 'SESSION_USER') as session_user,
                  SYS_CONTEXT('USERENV', 'SERVER_HOST') as server_host
              FROM DUAL
          """),
            )
            result.fetchone()


def demonstrate_table_operations() -> None:
    """Demonstrate table operations with SQLAlchemy 2."""
    with oracle_connection() as engine:
        # List tables in schema
        with engine.connect() as conn:
            result = conn.execute(
                text("""
              SELECT table_name, num_rows, last_analyzed
              FROM all_tables
              WHERE owner = 'FLEXTTEST'
              ORDER BY table_name
          """),
            )

            tables = result.fetchall()
            for _table in tables:
                pass

        # Query EMPLOYEES table data
        with engine.connect() as conn:
            result = conn.execute(
                text("""
              SELECT employee_id, first_name, last_name, email, hire_date
              FROM FLEXTTEST.EMPLOYEES
              WHERE ROWNUM <= 5
              ORDER BY employee_id
          """),
            )

            employees = result.fetchall()
            for _emp in employees:
                pass


def demonstrate_metadata_introspection() -> None:
    """Demonstrate SQLAlchemy 2 metadata introspection."""
    with oracle_connection() as engine, engine.connect() as conn:
        # Column information for EMPLOYEES table
        result = conn.execute(
            text("""
              SELECT
                  column_name,
                  data_type,
                  data_length,
                  data_precision,
                  data_scale,
                  nullable,
                  column_id
              FROM all_tab_columns
              WHERE owner = 'FLEXTTEST'
              AND table_name = 'EMPLOYEES'
              ORDER BY column_id
          """),
        )

        columns = result.fetchall()
        for col in columns:
            "NULL" if col[5] == "Y" else "NOT NULL"
            if col[3]:  # Has precision
                f"{col[1]}({col[3]},{col[4] or 0})"
            elif col[2]:  # Has length
                f"{col[1]}({col[2]})"
            else:
                col[1]


def demonstrate_transaction_management() -> None:
    """Demonstrate SQLAlchemy 2 transaction management."""
    with oracle_connection() as engine, engine.connect() as conn, conn.begin() as trans:
        # Demonstrate transaction with rollback
        try:
            # Count before
            result = conn.execute(
                text("SELECT COUNT(*) FROM FLEXTTEST.EMPLOYEES"),
            )
            row = result.fetchone()
            if row:
                row[0]

            # This would normally insert, but we'll rollback
            trans.rollback()

            # Count after rollback
            result = conn.execute(
                text("SELECT COUNT(*) FROM FLEXTTEST.EMPLOYEES"),
            )
            row = result.fetchone()
            if row:
                row[0]

        except Exception:
            trans.rollback()


def main() -> int:
    """Demonstrate SQLAlchemy 2 integration.

    Returns:
        int: Exit code (0 for success, 1 for failure).

    """
    # Check environment
    create_oracle_config()

    try:
        # Run all demonstrations
        demonstrate_basic_queries()
        demonstrate_table_operations()
        demonstrate_metadata_introspection()
        demonstrate_transaction_management()

    except Exception:
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
