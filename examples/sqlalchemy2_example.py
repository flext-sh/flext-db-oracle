"""SQLAlchemy 2 Example for flext-db-oracle.

This example demonstrates how to use the flext-db-oracle library
with SQLAlchemy 2 for Oracle database operations including:
- Connection management with automatic environment configuration
- Direct SQLAlchemy queries using Oracle engine
- Table metadata introspection
- Transaction management
- Column information retrieval

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import os
from contextlib import contextmanager
from typing import Iterator

from sqlalchemy import text
from sqlalchemy.engine import Engine

from flext_db_oracle import FlextDbOracleConfig, FlextDbOracleConnection


def create_oracle_config() -> FlextDbOracleConfig:
    """Create Oracle configuration from environment variables."""
    return FlextDbOracleConfig(
        host=os.getenv("FLEXT_TARGET_ORACLE_HOST", "localhost"),
        port=int(os.getenv("FLEXT_TARGET_ORACLE_PORT", "1521")),
        username=os.getenv("FLEXT_TARGET_ORACLE_USERNAME", "flexttest"),
        password=os.getenv("FLEXT_TARGET_ORACLE_PASSWORD", "FlextTest123"),
        service_name=os.getenv("FLEXT_TARGET_ORACLE_SERVICE_NAME", "XEPDB1"),
        encoding="UTF-8",
    )


@contextmanager
def oracle_connection() -> Iterator[Engine]:
    """Context manager for Oracle SQLAlchemy connection."""
    config = create_oracle_config()
    connection = FlextDbOracleConnection(config)

    print("🔗 Connecting to Oracle using SQLAlchemy 2...")
    connect_result = connection.connect()

    if connect_result.is_failure:
        print(f"❌ Connection failed: {connect_result.error}")
        raise RuntimeError(f"Failed to connect to Oracle: {connect_result.error}")

    print("✅ Connected to Oracle successfully")

    try:
        # Get SQLAlchemy engine from connection
        engine = connection._engine
        if engine is None:
            raise RuntimeError("Engine not available from connection")

        yield engine

    finally:
        print("🔒 Disconnecting from Oracle...")
        connection.disconnect()
        print("✅ Disconnected successfully")


def demonstrate_basic_queries() -> None:
    """Demonstrate basic SQLAlchemy 2 queries."""
    print("\n=== BASIC SQLALCHEMY 2 QUERIES ===")

    with oracle_connection() as engine:
        # Simple system query
        print("\n1. System Date Query:")
        with engine.connect() as conn:
            result = conn.execute(text("SELECT SYSDATE FROM DUAL"))
            sysdate = result.fetchone()
            print(f"   Current system date: {sysdate[0]}")

        # Database version query
        print("\n2. Database Version:")
        with engine.connect() as conn:
            result = conn.execute(text("SELECT BANNER FROM V$VERSION WHERE ROWNUM = 1"))
            version = result.fetchone()
            print(f"   Database version: {version[0]}")

        # Session information
        print("\n3. Session Information:")
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT 
                    USER as current_user,
                    SYS_CONTEXT('USERENV', 'SESSION_USER') as session_user,
                    SYS_CONTEXT('USERENV', 'SERVER_HOST') as server_host
                FROM DUAL
            """))
            session_info = result.fetchone()
            print(f"   Current user: {session_info[0]}")
            print(f"   Session user: {session_info[1]}")
            print(f"   Server host: {session_info[2]}")


def demonstrate_table_operations() -> None:
    """Demonstrate table operations with SQLAlchemy 2."""
    print("\n=== TABLE OPERATIONS ===")

    with oracle_connection() as engine:
        # List tables in schema
        print("\n1. Tables in FLEXTTEST Schema:")
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT table_name, num_rows, last_analyzed
                FROM all_tables 
                WHERE owner = 'FLEXTTEST'
                ORDER BY table_name
            """))

            tables = result.fetchall()
            for table in tables:
                print(f"   📋 {table[0]} (rows: {table[1]}, analyzed: {table[2]})")

        # Query EMPLOYEES table data
        print("\n2. Sample Data from EMPLOYEES:")
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT employee_id, first_name, last_name, email, hire_date
                FROM FLEXTTEST.EMPLOYEES 
                WHERE ROWNUM <= 5
                ORDER BY employee_id
            """))

            employees = result.fetchall()
            for emp in employees:
                print(f"   👤 ID: {emp[0]}, Name: {emp[1]} {emp[2]}, Email: {emp[3]}, Hired: {emp[4]}")


def demonstrate_metadata_introspection() -> None:
    """Demonstrate SQLAlchemy 2 metadata introspection."""
    print("\n=== METADATA INTROSPECTION ===")

    with oracle_connection() as engine:
        # Column information for EMPLOYEES table
        print("\n1. EMPLOYEES Table Structure:")
        with engine.connect() as conn:
            result = conn.execute(text("""
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
            """))

            columns = result.fetchall()
            for col in columns:
                nullable = "NULL" if col[5] == "Y" else "NOT NULL"
                if col[3]:  # Has precision
                    data_type = f"{col[1]}({col[3]},{col[4] or 0})"
                elif col[2]:  # Has length
                    data_type = f"{col[1]}({col[2]})"
                else:
                    data_type = col[1]

                print(f"   📊 {col[0]}: {data_type} {nullable}")


def demonstrate_transaction_management() -> None:
    """Demonstrate SQLAlchemy 2 transaction management."""
    print("\n=== TRANSACTION MANAGEMENT ===")

    with oracle_connection() as engine:
        # Demonstrate transaction with rollback
        print("\n1. Transaction with Rollback (Safe Test):")
        with engine.connect() as conn:
            with conn.begin() as trans:
                try:
                    # Count before
                    result = conn.execute(text("SELECT COUNT(*) FROM FLEXTTEST.EMPLOYEES"))
                    count_before = result.fetchone()[0]
                    print(f"   Records before: {count_before}")

                    # This would normally insert, but we'll rollback
                    print("   🔄 Rolling back transaction (no actual changes)")
                    trans.rollback()

                    # Count after rollback
                    result = conn.execute(text("SELECT COUNT(*) FROM FLEXTTEST.EMPLOYEES"))
                    count_after = result.fetchone()[0]
                    print(f"   Records after rollback: {count_after}")

                except Exception as e:
                    print(f"   ❌ Transaction error: {e}")
                    trans.rollback()


def main() -> None:
    """Main demonstration function."""
    print("=== FLEXT DB ORACLE - SQLALCHEMY 2 EXAMPLE ===")

    # Check environment
    config = create_oracle_config()
    print(f"📋 Connecting to: {config.host}:{config.port}/{config.service_name}")
    print(f"👤 User: {config.username}")

    try:
        # Run all demonstrations
        demonstrate_basic_queries()
        demonstrate_table_operations()
        demonstrate_metadata_introspection()
        demonstrate_transaction_management()

        print("\n🎉 SQLAlchemy 2 example completed successfully!")

    except Exception as e:
        print(f"\n❌ Example failed: {e}")
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
