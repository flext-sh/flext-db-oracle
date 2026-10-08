"""Test utilities for flext-db-oracle.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import os
import time
from collections.abc import Mapping, MutableMapping
from typing import ClassVar

from flext_tests import FlextTestsDocker, FlextTestsModels, FlextTestsUtilities

from flext_db_oracle import FlextDbOracleUtilities, u
from tests import c, m, t


class TestsFlextDbOracleUtilities(FlextTestsUtilities, FlextDbOracleUtilities):
    """Test utilities for flext-db-oracle."""

    class Tests(FlextTestsUtilities.Tests):
        """Test-specific utilities."""

        _PORT_BINDINGS_ADAPTER: ClassVar[m.TypeAdapter[t.StrMapping]] = u.type_adapter(
            Mapping[str, str],
        )

        @classmethod
        def normalize_port_bindings(
            cls,
            value: t.JsonValue | t.JsonMapping,
        ) -> t.StrMapping:
            """Normalize Docker port bindings into a typed mapping.

            Returns:
                The resulting ``t.StrMapping``.
            """
            # Why: no-hidden-errors — propagate a malformed Docker port
            # payload instead of masking it as "no bindings".
            validated: t.StrMapping = cls._PORT_BINDINGS_ADAPTER.validate_python(value)
            return validated

        @classmethod
        def _oracle_host_ports(
            cls,
            status_value: FlextTestsModels.Tests.ContainerInfo,
        ) -> t.StrMapping:
            """Normalize the port bindings carried by a container status value.

            Returns:
                The resulting ``t.StrMapping``.
            """
            return cls.normalize_port_bindings(status_value.ports)

        @classmethod
        def _env_port_matches(
            cls,
            ports: t.StrMapping,
            env_port_int: int,
        ) -> bool:
            """Report whether any Oracle listener publishes ``env_port_int``.

            Returns:
                The resulting ``bool``.
            """
            return any(
                container_port.startswith("1521")
                and host_port.isdigit()
                and int(host_port) == env_port_int
                for container_port, host_port in ports.items()
            )

        @classmethod
        def _first_oracle_host_port(cls, ports: t.StrMapping) -> int | None:
            """Return the first published Oracle listener host port, if any.

            Returns:
                The resulting ``int | None``.
            """
            for container_port, host_port in ports.items():
                if container_port.startswith("1521") and host_port.isdigit():
                    return int(host_port)
            return None

        @classmethod
        def _fallback_port(cls, container_name: str) -> int:
            """Resolve the configured fallback port for a shared container.

            Returns:
                The resulting ``int``.
            """
            fallback_port = 1522
            container_settings = c.Tests.SHARED_CONTAINERS.get(container_name)
            if container_settings is not None:
                configured_port = container_settings.get("port")
                if isinstance(configured_port, int):
                    fallback_port = configured_port
            return fallback_port

        @classmethod
        def resolve_oracle_test_port(
            cls,
            docker_control: FlextTestsDocker,
            container_name: str,
        ) -> int:
            """Resolve the exposed Oracle test port from Docker state.

            Returns:
                The resulting ``int``.
            """
            env_port = os.getenv("TEST_ORACLE_PORT")
            if env_port is not None and env_port.isdigit():
                env_port_int = int(env_port)
                status_result = docker_control.fetch_container_status(container_name)
                if status_result.success:
                    ports = cls._oracle_host_ports(status_result.value)
                    if cls._env_port_matches(ports, env_port_int):
                        return env_port_int
            fallback_port = cls._fallback_port(container_name)
            for _ in range(30):
                status_result = docker_control.fetch_container_status(container_name)
                if status_result.success:
                    host_port = cls._first_oracle_host_port(
                        cls._oracle_host_ports(status_result.value),
                    )
                    if host_port is not None:
                        return host_port
                time.sleep(2)
            return fallback_port

        class StubPluginApi:
            """In-memory plugin API stub used by service integration tests."""

            _registry: ClassVar[MutableMapping[str, m.Tests.StubPluginEntity]] = {}

            def register_plugin(
                self,
                plugin: m.Tests.StubPluginEntity,
            ) -> m.Tests.StubResult:
                """Register a plugin in the in-memory registry.

                Returns:
                    The resulting ``m.Tests.StubResult``.
                """
                self._registry[plugin.name] = plugin
                return m.Tests.StubResult()

            def unregister_plugin(self, plugin_name: str) -> m.Tests.StubResult:
                """Remove a plugin from the in-memory registry.

                Returns:
                    The resulting ``m.Tests.StubResult``.
                """
                if plugin_name not in self._registry:
                    return m.Tests.StubResult(
                        failure=True,
                        error=f"Plugin '{plugin_name}' not found",
                    )
                del self._registry[plugin_name]
                return m.Tests.StubResult()

            def list_plugins(self) -> t.SequenceOf[m.Tests.StubPluginEntity]:
                """Return all registered plugins."""
                return list(self._registry.values())

            def fetch_plugin(self, plugin_name: str) -> m.Tests.StubPluginEntity | None:
                """Return a plugin by name when present."""
                return self._registry.get(plugin_name)


u = TestsFlextDbOracleUtilities

__all__: list[str] = ["TestsFlextDbOracleUtilities", "u"]
