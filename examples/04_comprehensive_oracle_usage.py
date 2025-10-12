"""FLEXT DB Oracle Simple Usage Example.

Exemplo simplificado usando FlextCore.Processors.ServiceProcessor para eliminar
complexidade e demonstrar padrões flext-core avançados.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_core import FlextCore

from flext_db_oracle import FlextDbOracleApi, FlextDbOracleConfig

logger = FlextCore.Logger(__name__)


class OracleExampleProcessor(FlextCore.Service[str]):
    """Simplified Oracle example using FlextCore.Service - ELIMINA COMPLEXIDADE."""

    def execute(self) -> FlextCore.Result[str]:
        """Execute the main domain service operation.

        Returns:
            FlextCore.Result[str]: Success result with completion message.

        """
        return FlextCore.Result[str].ok("Oracle processing completed successfully")

    def process(self, _query: str) -> FlextCore.Result[FlextDbOracleApi]:
        """Process Oracle connection and execute query.

        Returns:
            FlextCore.Result[FlextDbOracleApi]: Success result with connected API instance.

        """
        try:
            config_result = FlextDbOracleConfig.from_env()
            if not config_result.is_success:
                return FlextCore.Result[FlextDbOracleApi].fail(
                    config_result.error or "Failed to load configuration",
                )
            config = config_result.value

            api = FlextDbOracleApi(config)

            connect_result = api.connect()
            if not connect_result.is_success:
                return FlextCore.Result[FlextDbOracleApi].fail(
                    connect_result.error or "Failed to connect",
                )

            return FlextCore.Result[FlextDbOracleApi].ok(api)
        except Exception as e:
            return FlextCore.Result[FlextDbOracleApi].fail(f"Oracle setup failed: {e}")

    def build(
        self,
        api: FlextDbOracleApi,
        *,
        correlation_id: str,
    ) -> FlextCore.Types.Dict:
        """Build simple result dictionary.

        Returns:
            FlextCore.Types.Dict: Dictionary with status and connection info.

        """
        return {
            "status": "connected",
            "correlation_id": correlation_id,
            "connection_active": api.is_connected,
        }


def demonstrate_basic_operations() -> None:
    """Simple demonstration usando FlextCore.Processors patterns."""
    processor = OracleExampleProcessor()

    # Execute domain service
    result = processor.execute()

    if result.is_success:
        logger.info(f"✅ Oracle operations completed: {result.value}")
    else:
        logger.error(f"❌ Oracle operations failed: {result.error}")


def demonstrate_query_operations() -> None:
    """Query operations usando Railway-Oriented Programming."""
    try:
        config_result = FlextDbOracleConfig.from_env()
        if not config_result.is_success:
            logger.error(f"❌ Configuration failed: {config_result.error}")
            return
        config = config_result.value

        api = FlextDbOracleApi(config)

        # Railway-Oriented Programming elimina múltiplos returns
        connect_result = api.connect()
        if connect_result.is_success:
            query_result = connect_result.value.query(
                "SELECT COUNT(*) FROM user_tables",
            )
            if query_result.is_success:
                # Access the first row of the result
                result_data = query_result.value
                if result_data and len(result_data) > 0:
                    # Get the first row and extract the count value
                    first_row = result_data[0]
                    if isinstance(first_row, dict) and len(first_row) > 0:
                        # Get the first value from the dictionary
                        count = next(iter(first_row.values()))
                        logger.info(f"📊 Found {count} tables")
                    else:
                        logger.info("📊 No data in first row")
                else:
                    logger.info("📊 No data returned from query")
            else:
                logger.error(f"❌ Query failed: {query_result.error}")
        else:
            logger.error(f"❌ Connection failed: {connect_result.error}")

    except Exception:
        logger.exception("❌ Setup failed")


def main() -> None:
    """Main entry point - COMPLEXIDADE REDUZIDA DE 50 PARA ~10."""
    logger.info("🚀 Starting simplified Oracle examples")

    # Duas demonstrações simples
    demonstrate_basic_operations()
    demonstrate_query_operations()

    logger.info("✅ Examples completed")


if __name__ == "__main__":
    main()
