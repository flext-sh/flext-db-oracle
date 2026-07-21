"""Test utilities for flext-db-oracle.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import os
import time
from typing import TYPE_CHECKING, ClassVar

from flext_tests import FlextTestsUtilities, e, tk

from flext_db_oracle import u
from tests import c, m, p, t

if TYPE_CHECKING:
    from collections.abc import MutableMapping


class TestsFlextDbOracleUtilities(FlextTestsUtilities, u):
    """Test utilities for flext-db-oracle."""

    class Tests(FlextTestsUtilities.Tests):
        """Test-specific utilities."""

        _PORT_BINDINGS_ADAPTER: ClassVar[p.TypeAdapter[t.StrMapping]] = m.TypeAdapter(
            t.StrMapping,
        )

        @classmethod
        def normalize_port_bindings(
            cls,
            value: t.JsonValue | t.JsonMapping,
        ) -> t.StrMapping:
            """Normalize Docker port bindings into a typed mapping."""
            try:
                return cls._PORT_BINDINGS_ADAPTER.validate_python(value)
            except e.ValidationError:
                return {}

        @classmethod
        def resolve_oracle_test_port(
            cls,
            docker_control: tk,
            container_name: str,
        ) -> int:
            """Resolve the exposed Oracle test port from Docker state."""
            env_port = os.getenv("TEST_ORACLE_PORT")
            if env_port is not None and env_port.isdigit():
                env_port_int = int(env_port)
                status_result = docker_control.fetch_container_status(
                    container_name,
                )
                if status_result.success:
                    status_value = status_result.value
                    raw_ports = getattr(status_value, "ports", {})
                    ports = cls.normalize_port_bindings(
                        raw_ports if isinstance(raw_ports, dict) else {},
                    )
                    for container_port, host_port in ports.items():
                        if (
                            container_port.startswith("1521")
                            and host_port.isdigit()
                            and int(host_port) == env_port_int
                        ):
                            return env_port_int
            fallback_port = 1522
            container_settings = c.Tests.SHARED_CONTAINERS.get(container_name)
            if container_settings is not None:
                configured_port = container_settings.get("port")
                if isinstance(configured_port, int):
                    fallback_port = configured_port
            for _ in range(30):
                status_result = docker_control.fetch_container_status(
                    container_name,
                )
                if status_result.success:
                    status_value = status_result.value
                    raw_ports = getattr(status_value, "ports", {})
                    ports = cls.normalize_port_bindings(
                        raw_ports if isinstance(raw_ports, dict) else {},
                    )
                    for container_port, host_port in ports.items():
                        if container_port.startswith("1521") and host_port.isdigit():
                            return int(host_port)
                time.sleep(2)
            return fallback_port

        class StubPluginApi:
            """In-memory plugin API stub used by service integration tests."""

            _registry: ClassVar[
                MutableMapping[
                    str,
                    m.Tests.StubPluginEntity,
                ]
            ] = {}

            def register_plugin(
                self,
                plugin: p.Tests.StubPluginEntity,
            ) -> p.Tests.StubResult:
                """Register a plugin in the in-memory registry."""
                self._registry[plugin.name] = plugin
                return m.Tests.StubResult()

            def unregister_plugin(
                self,
                plugin_name: str,
            ) -> p.Tests.StubResult:
                """Remove a plugin from the in-memory registry."""
                if plugin_name not in self._registry:
                    return m.Tests.StubResult(
                        failure=True,
                        error=f"Plugin '{plugin_name}' not found",
                    )
                del self._registry[plugin_name]
                return m.Tests.StubResult()

            def list_plugins(
                self,
            ) -> t.SequenceOf[p.Tests.StubPluginEntity]:
                """Return all registered plugins."""
                return list(self._registry.values())

            def fetch_plugin(
                self,
                plugin_name: str,
            ) -> p.Tests.StubPluginEntity | None:
                """Return a plugin by name when present."""
                return self._registry.get(plugin_name)


u = TestsFlextDbOracleUtilities

__all__: list[str] = ["TestsFlextDbOracleUtilities", "u"]
