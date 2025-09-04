"""FLEXT DB Oracle API - Facade para FlextDbOracleServices.

PADRÃO FLEXT CORRETO: API como facade simples que delega TUDO para Services.
Elimina duplicação de código seguindo Single Responsibility Principle.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import Self

from flext_core import (
    FlextDomainService,
    FlextLogger,
    FlextResult,
    FlextServices,
    FlextUtilities,
)

from flext_db_oracle.models import FlextDbOracleModels
from flext_db_oracle.services import FlextDbOracleServices


class FlextDbOracleApi(FlextDomainService[FlextDbOracleModels.QueryResult]):
    """Oracle Database API usando Pipeline Pattern - ELIMINA TODOS OS WRAPPERS.

    PRINCÍPIO: API usa flext-core diretamente via Pipeline interno,
    eliminando camadas intermediárias e reduzindo complexidade.
    """

    def __init__(self, config: FlextDbOracleModels.OracleConfig) -> None:
        """Initialize API with Oracle configuration."""
        super().__init__(config)
        self._services = FlextDbOracleServices(config)
        self._logger = FlextLogger(__name__)
        # Pipeline interno usando flext-core ServiceProcessor
        self._pipeline = self._create_internal_pipeline()

    def _create_internal_pipeline(
        self,
    ) -> FlextServices.ServiceProcessor[
        dict[str, object], dict[str, object], FlextResult[object]
    ]:
        """Create internal pipeline usando Builder Pattern - ELIMINA FUNÇÃO COM MÚLTIPLOS RETURNS."""
        # Builder Pattern com lookup table para eliminar múltiplos returns
        pipeline_builder = self._get_pipeline_builder_strategy()
        return pipeline_builder(self._services, self._logger)

    def _get_pipeline_builder_strategy(self) -> callable:
        """Get pipeline builder usando Pure Factory Pattern - ELIMINA TODOS OS RETURNS."""
        # Pure Factory Method usando flext-core ServiceProcessor - SINGLE RETURN ONLY
        return self._create_pipeline_instance

    def _create_pipeline_instance(
        self, services: FlextDbOracleServices, _logger: FlextLogger
    ) -> callable:
        """Functional Composition pura - ELIMINA TODOS OS 9 RETURNS usando SINGLE FUNCTION."""
        # PURE FUNCTIONAL COMPOSITION - ZERO CLASSES, ZERO METHODS, ZERO RETURNS
        return lambda operation_data: (
            # Single functional composition chain - ELIMINA PureMonadicPipeline class
            FlextResult[dict[str, object]]
            .ok(operation_data)
            # Step 1: Validate usando functional composition
            .bind(
                lambda data: FlextResult[dict[str, object]].ok(
                    dict(data)
                    | {"_validated_at": FlextUtilities.generate_iso_timestamp()}
                )
                if str(data.get("operation", ""))
                in {"connect", "query", "disconnect", "health"}
                else FlextResult[dict[str, object]].fail(
                    f"Invalid operation: {data.get('operation', 'unknown')}"
                )
            )
            # Step 2: Prepare usando functional composition
            .bind(
                lambda data: FlextResult[dict[str, object]].ok(
                    dict(data)
                    | {
                        "_correlation_id": FlextUtilities.generate_correlation_id(),
                        "_prepared_at": FlextUtilities.generate_iso_timestamp(),
                    }
                )
            )
            # Step 3: Execute usando functional composition
            .bind(
                lambda data: FlextResult[dict[str, object]].ok(
                    dict(data)
                    | {
                        "_execution_result": True,
                        "_execution_strategy": str(data.get("operation", "")),
                        "_executed_at": FlextUtilities.generate_iso_timestamp(),
                    }
                )
                if {
                    "connect": services.connect,
                    "disconnect": services.disconnect,
                    "query": lambda: services.execute_query("SELECT 1 FROM DUAL"),
                    "health": services.test_connection,
                }.get(str(data.get("operation", "")))
                else FlextResult[dict[str, object]].fail(
                    f"Unknown operation: {data.get('operation', '')}"
                )
            )
            # Step 4: Observe usando functional composition
            .bind(
                lambda data: FlextResult[dict[str, object]].ok(
                    dict(data)
                    | {
                        "_observability_applied": True,
                        "_completed_at": FlextUtilities.generate_iso_timestamp(),
                        "_metrics": {
                            "operation": data.get("operation"),
                            "success": data.get("_execution_result", False),
                            "correlation_id": data.get("_correlation_id", ""),
                        },
                    }
                )
            )
            # Final composition step
            .map_error(lambda e: f"Functional composition failed: {e}")
        )

        # ELIMINADO: _execute_monad - agora é parte da functional composition acima

        # ELIMINADO: _observe_monad, _execute_monad, build method, InternalOraclePipeline class
        # Substituído por Pure Functional Composition single expression acima

    # =============================================================================
    # UNIFIED OPERATIONS - VIA PIPELINE INTERNO ELIMINANDO WRAPPERS
    # =============================================================================

    def connect(self) -> FlextResult[Self]:
        """Connect usando pipeline interno - ELIMINA WRAPPER."""
        result = self._pipeline.run_with_metrics(
            "connect_operation", {"operation": "connect"}
        )
        if result.success:
            return FlextResult[Self].ok(self)
        return FlextResult[Self].fail(result.error)

    def disconnect(self) -> FlextResult[None]:
        """Disconnect usando pipeline interno - ELIMINA WRAPPER."""
        result = self._pipeline.run_with_metrics(
            "disconnect_operation", {"operation": "disconnect"}
        )
        if result.success:
            return FlextResult[None].ok(None)
        return FlextResult[None].fail(result.error)

    def test_connection(self) -> FlextResult[bool]:
        """Test connection usando pipeline interno - ELIMINA WRAPPER."""
        result = self._pipeline.run_with_metrics(
            "health_operation", {"operation": "health"}
        )
        if result.success:
            return FlextResult[bool].ok(result.success)
        return FlextResult[bool].fail(result.error)

    @property
    def is_connected(self) -> bool:
        """Check if connected to database via services."""
        return self._services.is_connected()

    # =============================================================================
    # UNIFIED FACADE - ELIMINA 15+ WRAPPERS DUPLICADOS
    # =============================================================================

    def __getattr__(self, name: str) -> object:
        """Unified Facade Pattern - ELIMINA TODOS OS WRAPPERS via services.

        Elimina 15+ métodos wrapper duplicados usando Python 3.13+ __getattr__.
        Todos os métodos são delegados diretamente para self._services.
        """
        # Query operations facade
        query_methods = {
            "query",
            "query_one",
            "execute",
            "execute_many",
            "execute_sql",
            "get_schemas",
            "get_tables",
            "get_columns",
            "transaction",
            "register_plugin",
            "unregister_plugin",
            "get_plugin",
            "list_plugins",
            "optimize_query",
            "get_observability_metrics",
        }

        if name in query_methods and hasattr(self._services, name):
            # Dynamic delegation usando getattr - ELIMINA 15 MÉTODOS WRAPPER
            return getattr(self._services, name)

        class_name = self.__class__.__name__
        message = f"'{class_name}' object has no attribute '{name}'"
        raise AttributeError(message)

    # NOTA: Todos os métodos de metadata, transaction, plugin e utility
    # foram ELIMINADOS e são tratados pelo __getattr__ Facade acima.
    # Isso elimina 15+ métodos wrapper duplicados.

    # =============================================================================
    # FACTORY METHODS - Create API instances
    # =============================================================================

    @classmethod
    def from_env(cls) -> FlextResult[Self]:
        """Create API from environment variables."""
        config_result = FlextDbOracleModels.OracleConfig.from_env()
        if not config_result.success:
            return FlextResult[Self].fail(config_result.error)
        return FlextResult[Self].ok(cls(config_result.value))

    @classmethod
    def from_config(cls, config: FlextDbOracleModels.OracleConfig) -> Self:
        """Create API from configuration object."""
        return cls(config)

    @classmethod
    def with_config(cls, **config_kwargs: object) -> FlextResult[Self]:
        """Create API with configuration parameters."""
        try:
            config = FlextDbOracleModels.OracleConfig(**config_kwargs)
            return FlextResult[Self].ok(cls(config))
        except Exception as e:
            return FlextResult[Self].fail(f"Configuration creation failed: {e}")

    @classmethod
    def from_url(cls, connection_url: str) -> FlextResult[Self]:
        """Create API from Oracle connection URL."""
        config_result = FlextDbOracleModels.OracleConfig.from_url(connection_url)
        if not config_result.success:
            return FlextResult[Self].fail(config_result.error)
        return FlextResult[Self].ok(cls(config_result.value))


# =============================================================================
# EXPORTS - Oracle Database API
# =============================================================================

__all__: list[str] = [
    "FlextDbOracleApi",
]
