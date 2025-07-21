"""FLEXT DB Oracle CLI - Enterprise Oracle Database Utilities.

REFACTORED:
    Uses flext-core patterns with proper logging and configuration.
Provides comprehensive Oracle database management tools via command line.
"""

from __future__ import annotations

import argparse
import sys
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from argparse import Namespace

from flext_observability.logging import get_logger

from flext_db_oracle.connection.config import ConnectionConfig
from flext_db_oracle.connection.connection import OracleConnection

# Use flext-infrastructure.monitoring.flext-observability for all logging
logger = get_logger(__name__)


def test_connection(args: Namespace) -> int:
    """Test Oracle database connection."""
    logger.info("🔍 Testing Oracle database connection...")

    if args.url:
        config = ConnectionConfig.from_url(args.url)
    else:
        config = ConnectionConfig(
            host=args.host,
            port=args.port,
            sid=args.sid,
            service_name=args.service_name or "XE",
            username=args.username,
            password=args.password,
            pool_min=1,
            pool_max=10,
            pool_increment=1,
            timeout=30,
            encoding="UTF-8",
            ssl_cert_path=None,
            ssl_key_path=None,
            protocol="tcp",
        )

    try:
        conn = OracleConnection(config)
        conn.connect()

        if not conn.is_connected:
            logger.error("❌ Connection test failed: Could not establish connection")
            return 1

        result = conn.fetch_one("SELECT 1 FROM DUAL")
        if not result:
            logger.error("❌ Connection test failed: No result from test query")
            return 1

        logger.info("✅ Connection successful!")
        logger.info("📊 Connection details:")
        logger.info("   Host: %s:%d", config.host, config.port)
        logger.info("   Service: %s", config.service_name or config.sid)
        logger.info("   User: %s", config.username)
        conn.disconnect()

    except Exception:
        logger.exception("❌ Connection failed")
        return 1
    else:
        return 0


def list_tables(args: Namespace) -> int:
    try:
        logger.info("📋 Listing database tables...")

        if args.url:
            config = ConnectionConfig.from_url(args.url)
        else:
            config = ConnectionConfig(
                host=args.host,
                port=args.port,
                sid=args.sid,
                service_name=args.service_name or "XE",
                username=args.username,
                password=args.password,
                pool_min=1,
                pool_max=10,
                pool_increment=1,
                timeout=30,
                encoding="UTF-8",
                ssl_cert_path=None,
                ssl_key_path=None,
                protocol="tcp",
            )

        conn = OracleConnection(config)
        conn.connect()

        schema = args.schema or config.username.upper()

        # Query to get tables
        sql = """
            SELECT table_name, num_rows, tablespace_name
            FROM all_tables
            WHERE owner = :schema
            ORDER BY table_name
        """

        results = conn.fetch_all(sql, {"schema": schema})

    except Exception:
        logger.exception("❌ Failed to list tables")
        return 1
    else:
        if results:
            logger.info("📋 Found %d tables in schema %s:", len(results), schema)
            logger.info("%-30s %-15s %s", "TABLE NAME", "ROWS", "TABLESPACE")
            logger.info("-" * 60)

            for row in results:
                table_name = row[0]
                num_rows = row[1] if row[1] is not None else "Unknown"
                tablespace = row[2] if row[2] is not None else "Default"
                logger.info("%-30s %-15s %s", table_name, num_rows, tablespace)
        else:
            logger.info("No tables found in schema %s", schema)

        conn.disconnect()
        return 0


def describe_table(args: Namespace) -> int:
    try:
        logger.info("📊 Describing table structure...")

        if args.url:
            config = ConnectionConfig.from_url(args.url)
        else:
            config = ConnectionConfig(
                host=args.host,
                port=args.port,
                sid=args.sid,
                service_name=args.service_name or "XE",
                username=args.username,
                password=args.password,
                pool_min=1,
                pool_max=10,
                pool_increment=1,
                timeout=30,
                encoding="UTF-8",
                ssl_cert_path=None,
                ssl_key_path=None,
                protocol="tcp",
            )

        conn = OracleConnection(config)
        conn.connect()

        schema = args.schema or config.username.upper()
        table_name = args.table.upper()

        # Query to get column information
        sql = """
            SELECT column_name, data_type, data_length, data_precision,
                   data_scale, nullable, data_default
            FROM all_tab_columns
            WHERE table_name = :table_name AND owner = :schema
            ORDER BY column_id
        """

        results = conn.fetch_all(sql, {"table_name": table_name, "schema": schema})

    except Exception:
        logger.exception("❌ Failed to describe table")
        return 1
    else:
        if results:
            logger.info("📊 Table structure for %s.%s:", schema, table_name)
            logger.info(
                "%-30s %-15s %-10s %-8s %-10s",
                "COLUMN NAME",
                "DATA TYPE",
                "LENGTH",
                "NULL?",
                "DEFAULT",
            )
            logger.info("-" * 80)

            for row in results:
                col_name = row[0]
                data_type = row[1]
                length = row[2] or ""
                precision = row[3] or ""
                scale = row[4] or ""
                nullable = "YES" if row[5] == "Y" else "NO"
                default = row[6] or ""

                # Format data type with length/precision
                if precision and scale:
                    type_str = f"{data_type}({precision},{scale})"
                elif length and data_type in {"VARCHAR2", "CHAR", "NVARCHAR2", "NCHAR"}:
                    type_str = f"{data_type}({length})"
                else:
                    type_str = data_type

                logger.info(
                    "%-30s %-15s %-10s %-8s %-10s",
                    col_name,
                    type_str,
                    str(length),
                    nullable,
                    str(default)[:10],
                )
        else:
            logger.error("Table %s.%s not found", schema, table_name)
            return 1

        conn.disconnect()
        return 0


def setup_parser() -> argparse.ArgumentParser:
    """Set up command line argument parser."""
    parser = argparse.ArgumentParser(
        description="FLEXT DB Oracle - Enterprise Oracle Database Utilities",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    # Global connection options
    parser.add_argument(
        "--url",
        help="Oracle connection URL (oracle://user:pass@host:port/service)",
    )
    parser.add_argument(
        "--host",
        default="localhost",
        help="Database host (default: localhost)",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=1521,
        help="Database port (default: 1521)",
    )
    parser.add_argument("--sid", help="Oracle SID")
    parser.add_argument("--service-name", help="Oracle service name (default: XE)")
    parser.add_argument("--username", help="Database username")
    parser.add_argument("--password", help="Database password")
    parser.add_argument("--schema", help="Schema name (default: username)")

    # Subcommands
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Test connection command
    test_parser = subparsers.add_parser("test", help="Test database connection")
    test_parser.set_defaults(func=test_connection)

    # List tables command
    tables_parser = subparsers.add_parser("tables", help="List tables in schema")
    tables_parser.set_defaults(func=list_tables)

    # Describe table command
    desc_parser = subparsers.add_parser("describe", help="Describe table structure")
    desc_parser.add_argument("table", help="Table name to describe")
    desc_parser.set_defaults(func=describe_table)

    return parser


def main() -> int:
    try:
        parser = setup_parser()
        args = parser.parse_args()

        if not args.command:
            parser.print_help()
            return 1

        # Validate required connection parameters
        if not args.url:
            if not all([args.username, args.password]):
                logger.error(
                    "❌ Username and password are required when not using --url",
                )
                return 1

            if not args.sid and not args.service_name:
                logger.warning(
                    "⚠️  Neither SID nor service-name specified, "
                    "using default service 'XE'",
                )

        result = args.func(args)
        return result if isinstance(result, int) else 0

    except KeyboardInterrupt:
        logger.info("Operation cancelled by user")
        return 130
    except Exception:
        logger.exception("❌ Unexpected error")
        return 1


if __name__ == "__main__":
    sys.exit(main())
