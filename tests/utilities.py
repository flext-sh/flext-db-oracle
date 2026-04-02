"""Test utilities for flext-db-oracle.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from collections.abc import MutableMapping, Sequence
from typing import ClassVar

from flext_tests import FlextTestsUtilities

from flext_db_oracle import FlextDbOracleUtilities
from tests.models import FlextDbOracleTestModels


class FlextDbOracleTestUtilities(FlextTestsUtilities, FlextDbOracleUtilities):
    """Test utilities for flext-db-oracle."""

    class DbOracle(FlextDbOracleUtilities.DbOracle):
        """DbOracle domain test utilities."""

        class Tests:
            """Test-specific utilities."""

            class StubPluginApi:
                """In-memory plugin API stub used by service integration tests."""

                _registry: ClassVar[
                    MutableMapping[
                        str,
                        FlextDbOracleTestModels.DbOracle.Tests.StubPluginEntity,
                    ]
                ] = {}

                def register_plugin(
                    self,
                    plugin: FlextDbOracleTestModels.DbOracle.Tests.StubPluginEntity,
                ) -> FlextDbOracleTestModels.DbOracle.Tests.StubResult:
                    """Register a plugin in the in-memory registry."""
                    self._registry[plugin.name] = plugin
                    return FlextDbOracleTestModels.DbOracle.Tests.StubResult()

                def unregister_plugin(
                    self,
                    plugin_name: str,
                ) -> FlextDbOracleTestModels.DbOracle.Tests.StubResult:
                    """Remove a plugin from the in-memory registry."""
                    if plugin_name not in self._registry:
                        return FlextDbOracleTestModels.DbOracle.Tests.StubResult(
                            is_failure=True,
                            error=f"Plugin '{plugin_name}' not found",
                        )
                    del self._registry[plugin_name]
                    return FlextDbOracleTestModels.DbOracle.Tests.StubResult()

                def list_plugins(
                    self,
                ) -> Sequence[FlextDbOracleTestModels.DbOracle.Tests.StubPluginEntity]:
                    """Return all registered plugins."""
                    return list(self._registry.values())

                def get_plugin(
                    self,
                    plugin_name: str,
                ) -> FlextDbOracleTestModels.DbOracle.Tests.StubPluginEntity | None:
                    """Return a plugin by name when present."""
                    return self._registry.get(plugin_name)


u = FlextDbOracleTestUtilities
__all__ = ["FlextDbOracleTestUtilities", "u"]
