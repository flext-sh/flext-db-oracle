"""Oracle Database connection and plugin protocol contracts.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from collections.abc import Sequence
from typing import TYPE_CHECKING, Protocol, Self, runtime_checkable

from flext_cli import FlextCliProtocols

if TYPE_CHECKING:
    from flext_core._protocols import FlextProtocolsResult

    from flext_db_oracle import m, t


class FlextDbOracleProtocolsConnection:
    """Oracle Database connection protocol contracts composed into ``p.DbOracle``."""

    @runtime_checkable
    class Connection(Protocol):
        """Protocol for Oracle database connection operations."""

        def connect(self) -> FlextProtocolsResult.Result[Self]:
            """Establish Oracle database connection.

            Returns:
                The connected implementer on success.

            """
            ...

        def disconnect(self) -> FlextProtocolsResult.Result[bool]:
            """Close Oracle database connection.

            Returns:
                Whether the connection was closed.

            """
            ...

        def connected(self) -> bool:
            """Check if Oracle connection is active.

            Returns:
                Whether an active connection exists.

            """
            ...

    @runtime_checkable
    class OraclePlugin(Protocol):
        """Protocol for Oracle database plugins.

        All plugins registered with the FlextDbOracle plugin system
        must satisfy this protocol.
        """

        def fetch_connection(self) -> FlextProtocolsResult.Result[t.JsonValue]:
            """Get current Oracle connection t.JsonValue.

            Returns:
            r: Connection t.JsonValue or error

            """
            ...

        def initialize(self) -> FlextProtocolsResult.Result[bool]:
            """Initialize the plugin."""
            ...

        def shutdown(self) -> FlextProtocolsResult.Result[bool]:
            """Shutdown the plugin."""
            ...

        def test_connection(self) -> FlextProtocolsResult.Result[bool]:
            """Test Oracle database connectivity.

            Returns:
            r[bool]: Connection test result

            """
            ...

    @runtime_checkable
    class PluginRegistry(Protocol):
        """Protocol for Oracle database plugin registry operations."""

        def fetch_plugin(
            self,
            name: str,
        ) -> FlextProtocolsResult.Result[t.JsonPayload | t.FlatContainer]:
            """Get Oracle database plugin by name.

            Args:
            name: Plugin name

            Returns:
            r: Plugin instance or error

            """
            ...

        def list_plugins(self) -> FlextProtocolsResult.Result[Sequence[str]]:
            """List registered Oracle database plugins.

            Returns:
            r[Sequence[str]]: Plugin names or error

            """
            ...

        def register_plugin(
            self,
            name: str,
            plugin: t.JsonPayload | t.FlatContainer,
        ) -> FlextProtocolsResult.Result[bool]:
            """Register Oracle database plugin.

            Args:
            name: Plugin name
            plugin: Plugin instance

            Returns:
            r[bool]: Registration success status

            """
            ...

        def unregister_plugin(self, name: str) -> FlextProtocolsResult.Result[bool]:
            """Unregister Oracle database plugin.

            Args:
            name: Plugin name

            Returns:
            r[bool]: Unregistration success status

            """
            ...

    @runtime_checkable
    class HealthCheck(Protocol):
        """Protocol for Oracle database health check operations."""

        def fetch_connection_status(
            self,
        ) -> FlextProtocolsResult.Result[m.DbOracle.ConnectionStatus]:
            """Get Oracle connection status information.

            Returns:
            r[t.JsonMapping]: Connection status or error

            """
            ...

        def health_check(self) -> FlextProtocolsResult.Result[m.DbOracle.HealthStatus]:
            """Perform Oracle database health check.

            Returns:
            r[t.JsonMapping]: Health status or error

            """
            ...

    @runtime_checkable
    class Runtime(FlextCliProtocols.Base, Protocol):
        """Protocol for a runtime Oracle API service that reports its own validity.

        Declares only the ``valid`` capability this member actually consumes,
        deliberately not extending ``p.Service`` while that base still carries
        unimplemented members (``service_info``, ``ok``, ``fail_op``) which
        would make this protocol structurally unsatisfiable by real services.
        """

        def valid(self) -> bool:
            """Check whether the runtime configuration is valid.

            Returns:
            bool: True when the configuration is usable, False otherwise.

            """
            ...


__all__: list[str] = ["FlextDbOracleProtocolsConnection"]
