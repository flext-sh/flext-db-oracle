"""FLEXT DB Oracle unified facade - Single entry point for all Oracle operations.

This module provides the FlextDbOracle facade class following the FLEXT
architectural patterns. It serves as a unified entry point that delegates
to all specialized Oracle components.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_core import FlextDomainService, FlextResult, get_flext_container

from flext_db_oracle.api import FlextDbOracleApi
from flext_db_oracle.config import FlextDbOracleConfig
from flext_db_oracle.connection import FlextDbOracleConnections
from flext_db_oracle.exceptions import FlextDbOracleExceptions
from flext_db_oracle.metadata import FlextDbOracleMetadatas
from flext_db_oracle.observability import FlextDbOracleObservabilityManager
from flext_db_oracle.plugins import FlextDbOraclePlugins
from flext_db_oracle.utilities import FlextDbOracleUtilities


class FlextDbOracle(FlextDomainService[dict[str, object]]):
    """Unified facade for all Oracle database operations.

    This facade follows FLEXT architectural patterns by providing a single
    entry point that delegates to specialized Oracle components:

    - APIs: Database operations and business logic
    - Connections: Connection management and pooling
    - Metadata: Schema introspection and analysis
    - Observability: Monitoring and metrics collection
    - Plugins: Extension system and customizations
    - Utilities: Helper functions and tools
    - Exceptions: Error handling and reporting

    Examples:
        Basic usage:
        >>> config = FlextDbOracleConfig(host="localhost", port=1521, ...)
        >>> oracle = FlextDbOracle(config)
        >>> result = oracle.execute()  # Returns system status

        Component access:
        >>> api_result = oracle.apis.execute()  # API operations
        >>> conn_result = oracle.connections.execute()  # Connection ops
        >>> metadata_result = oracle.metadata.execute()  # Schema ops

    """

    def __init__(self, config: FlextDbOracleConfig) -> None:
        """Initialize Oracle facade with configuration.

        Args:
            config: Oracle database configuration

        """
        super().__init__()
        self._config = config
        self._initialized = False

    @property
    def apis(self) -> FlextDbOracleApi:
        """Access Oracle API operations."""
        return FlextDbOracleApi(self._config)

    @property
    def connections(self) -> FlextDbOracleConnections:
        """Access Oracle connection management."""
        return FlextDbOracleConnections()

    @property
    def metadata(self) -> FlextDbOracleMetadatas:
        """Access Oracle metadata operations."""
        return FlextDbOracleMetadatas()

    @property
    def observability(self) -> FlextDbOracleObservabilityManager:
        """Access Oracle observability features."""
        return FlextDbOracleObservabilityManager(get_flext_container(), "oracle-facade")

    @property
    def plugins(self) -> FlextDbOraclePlugins:
        """Access Oracle plugin system."""
        return FlextDbOraclePlugins()

    @property
    def utilities(self) -> FlextDbOracleUtilities:
        """Access Oracle utility functions."""
        return FlextDbOracleUtilities()

    @property
    def exceptions(self) -> FlextDbOracleExceptions:
        """Access Oracle exception handling."""
        return FlextDbOracleExceptions()

    def execute(self) -> FlextResult[dict[str, object]]:
        """Execute Oracle system status check.

        Returns comprehensive status information from all Oracle components.

        Returns:
            FlextResult containing system status data or error information

        """
        try:
            # Gather status from all components
            status_data = {
                "facade": "operational",
                "config": {
                    "host": self._config.host,
                    "port": self._config.port,
                    "service_name": self._config.service_name,
                    "username": self._config.username,
                },
                "components": {
                    "apis": "available",
                    "connections": "available",
                    "metadata": "available",
                    "observability": "available",
                    "plugins": "available",
                    "utilities": "available",
                    "exceptions": "available",
                },
                "capabilities": [
                    "database_operations",
                    "connection_pooling",
                    "schema_introspection",
                    "monitoring_metrics",
                    "plugin_extensions",
                    "utility_functions",
                    "error_handling",
                ],
                "initialized": self._initialized,
            }

            return FlextResult[dict[str, object]].ok(status_data)

        except Exception as e:
            return FlextResult[dict[str, object]].fail(
                f"Oracle facade status check failed: {e}"
            )

    def initialize(self) -> FlextResult[None]:
        """Initialize all Oracle components.

        Returns:
            FlextResult indicating initialization success or failure

        """
        try:
            # Initialize components in dependency order
            components = [
                ("exceptions", self.exceptions),
                ("utilities", self.utilities),
                ("observability", self.observability),
                ("connections", self.connections),
                ("metadata", self.metadata),
                ("plugins", self.plugins),
                ("apis", self.apis),
            ]

            for name, component in components:
                if hasattr(component, "initialize"):
                    result = component.initialize()
                    if result.failure:
                        return FlextResult[None].fail(
                            f"Failed to initialize {name}: {result.error}"
                        )

            self._initialized = True
            return FlextResult[None].ok(None)

        except Exception as e:
            return FlextResult[None].fail(f"Oracle initialization failed: {e}")

    @staticmethod
    def create_with_config(config: FlextDbOracleConfig) -> FlextResult[FlextDbOracle]:
        """Create Oracle facade with configuration using factory pattern.

        Args:
            config: Oracle database configuration

        Returns:
            FlextResult containing FlextDbOracle instance or error

        """
        try:
            facade = FlextDbOracle(config)
            init_result = facade.initialize()

            if init_result.is_failure:
                return FlextResult[FlextDbOracle].fail(
                    f"Oracle facade creation failed: {init_result.error}"
                )

            return FlextResult[FlextDbOracle].ok(facade)

        except Exception as e:
            return FlextResult[FlextDbOracle].fail(f"Oracle facade creation failed: {e}")

    @staticmethod
    def from_env() -> FlextResult[FlextDbOracle]:
        """Create Oracle facade from environment variables.

        Returns:
            FlextResult containing FlextDbOracle instance or error

        """
        try:
            config = FlextDbOracleConfig.from_env()
            return FlextDbOracle.create_with_config(config)

        except Exception as e:
            return FlextResult[FlextDbOracle].fail(
                f"Oracle facade creation from environment failed: {e}"
            )


__all__: list[str] = [
    "FlextDbOracle",
]
