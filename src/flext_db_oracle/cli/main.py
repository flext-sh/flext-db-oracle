"""Main CLI entry point for Oracle database operations."""

from __future__ import annotations

import argparse
import sys
from typing import Any

from flext_db_oracle.connection.config import ConnectionConfig
from flext_db_oracle.connection.connection import OracleConnection
from flext_db_oracle.utils.logger import configure_logging, get_logger

logger = get_logger(__name__)


def test_connection(args: Any) -> int:
    """Test database connection.

    Args:
        args: Command line arguments.

    Returns:
        Exit code (0 for success, 1 for failure).

    """
    try:
        if args.url:
            config = ConnectionConfig.from_url(args.url)
        else:
            config = ConnectionConfig(
                host=args.host,
                port=args.port,
                sid=args.sid,
                service_name=args.service_name,
                username=args.username,
                password=args.password,
            )

        with OracleConnection(config) as conn:
            result = conn.fetch_one("SELECT 1 FROM DUAL")
            if result:
                logger.info("✅ Connection successful!")
                return 0
            logger.error("❌ Connection test failed: No result from test query")
            return 1

    except Exception as e:
        logger.exception("❌ Connection failed: %s", e)
        return 1


def list_tables(args: Any) -> int:
    """List database tables.

    Args:
        args: Command line arguments.

    Returns:
        Exit code (0 for success, 1 for failure).

    """
    try:
        if args.url:
            config = ConnectionConfig.from_url(args.url)
        else:
            config = ConnectionConfig(
                host=args.host,
                port=args.port,
                sid=args.sid,
                service_name=args.service_name,
                username=args.username,
                password=args.password,
            )

        with OracleConnection(config) as conn:
            tables = conn.get_table_names(args.schema)

            if tables:
                logger.info("📋 Found %d tables:", len(tables))
                for table in tables:
                    print(f"  • {table}")
            else:
                logger.info("No tables found")

            return 0

    except Exception as e:
        logger.exception("❌ Failed to list tables: %s", e)
        return 1


def describe_table(args: Any) -> int:
    """Describe table structure.

    Args:
        args: Command line arguments.

    Returns:
        Exit code (0 for success, 1 for failure).

    """
    try:
        if args.url:
            config = ConnectionConfig.from_url(args.url)
        else:
            config = ConnectionConfig(
                host=args.host,
                port=args.port,
                sid=args.sid,
                service_name=args.service_name,
                username=args.username,
                password=args.password,
            )

        with OracleConnection(config) as conn:
            columns = conn.get_column_info(args.table, args.schema)

            if columns:
                logger.info("📋 Table %s structure:", args.table)
                print(f"{'Column':<30} {'Type':<20} {'Nullable':<10} {'Default':<15}")
                print("-" * 75)

                for col in columns:
                    type_str = col["type"]
                    if col["length"]:
                        type_str += f"({col['length']}"
                        if col["precision"] and col["scale"]:
                            type_str += f",{col['scale']}"
                        type_str += ")"

                    nullable = "YES" if col["nullable"] else "NO"
                    default = str(col["default"]) if col["default"] else ""

                    print(
                        f"{col['name']:<30} {type_str:<20} {nullable:<10} {default:<15}"
                    )
            else:
                logger.info("No columns found for table %s", args.table)

            return 0

    except Exception as e:
        logger.exception("❌ Failed to describe table: %s", e)
        return 1


def main() -> int:
    """Main CLI entry point.

    Returns:
        Exit code.

    """
    parser = argparse.ArgumentParser(
        description="Oracle Database Core Utilities",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    # Global options
    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        default="INFO",
        help="Set logging level",
    )

    # Connection options
    connection_group = parser.add_argument_group("Connection Options")
    connection_group.add_argument(
        "--url", help="Database URL (oracle://user:pass@host:port/service)"
    )
    connection_group.add_argument("--host", default="localhost", help="Database host")
    connection_group.add_argument(
        "--port", type=int, default=1521, help="Database port"
    )
    connection_group.add_argument("--sid", help="Database SID")
    connection_group.add_argument("--service-name", help="Database service name")
    connection_group.add_argument(
        "--username", default="user", help="Database username"
    )
    connection_group.add_argument(
        "--password", default="password", help="Database password"
    )
    connection_group.add_argument("--schema", help="Schema name (optional)")

    # Subcommands
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Test connection command
    test_parser = subparsers.add_parser("test", help="Test database connection")
    test_parser.set_defaults(func=test_connection)

    # List tables command
    tables_parser = subparsers.add_parser("tables", help="List database tables")
    tables_parser.set_defaults(func=list_tables)

    # Describe table command
    describe_parser = subparsers.add_parser("describe", help="Describe table structure")
    describe_parser.add_argument("table", help="Table name to describe")
    describe_parser.set_defaults(func=describe_table)

    # Parse arguments
    args = parser.parse_args()

    # Configure logging
    configure_logging(args.log_level)

    # Execute command
    if hasattr(args, "func"):
        result = args.func(args)
        return int(result) if result is not None else 0
    parser.print_help()
    return 1


if __name__ == "__main__":
    sys.exit(main())
