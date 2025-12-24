"""FLEXT DB Oracle Simple Usage Example.

Exemplo simplificado usando FlextProcessors.ServiceProcessor para eliminar
complexidade e demonstrar padrões flext-core avançados.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from flext import FlextLogger, FlextResult, FlextService, t

logger = FlextLogger(__name__)


class OracleExampleProcessor(FlextService[str]):
    """Simplified Oracle example using FlextService - ELIMINA COMPLEXIDADE."""

    def execute(self, **_kwargs: object) -> FlextResult[str]:
        """Execute the main domain service operation.

        Args:
            **kwargs: Optional operation parameters.

        Returns:
            FlextResult[str]: Success result with completion message.

        """
        return FlextResult[str].ok("Oracle processing completed successfully")

    def process(self, _query: str) -> FlextResult[str]:
        """Process Oracle connection and execute query.

        Returns:
            FlextResult[str]: Success result with processing message.

        """
        try:
            # Simulate API usage without actual connection
            logger.info("Oracle API would be created and connected here")
            logger.info("Would execute query: %s", _query)

            return FlextResult[str].ok("Oracle processing simulated successfully")
        except Exception as e:
            return FlextResult[str].fail(f"Oracle setup failed: {e}")

    def build(
        self,
        *,
        correlation_id: str,
    ) -> dict[str, t.JsonValue]:
        """Build simple result dictionary.

        Returns:
            dict[str, t.JsonValue]: Dictionary with status and connection info.

        """
        return {
            "status": "connected",
            "correlation_id": correlation_id,
            "connection_active": True,
        }


def demonstrate_basic_operations() -> None:
    """Simple demonstration usando FlextProcessors patterns."""
    processor = OracleExampleProcessor()

    # Execute domain service
    result = processor.execute()

    if result.is_success:
        logger.info(f"✅ Oracle operations completed: {result.value}")
    else:
        logger.error(f"❌ Oracle operations failed: {result.error}")


def demonstrate_query_operations() -> None:
    """Query operations simulation usando Railway-Oriented Programming patterns."""
    try:
        logger.info("✅ Configuration would be created successfully")
        logger.info("🔌 Would connect to Oracle database here")
        logger.info("📊 Would execute query: SELECT COUNT(*) FROM user_tables")
        logger.info("📊 Would find tables (simulated)")

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
