from _typeshed import Incomplete
from flext_core import FlextPlugin, FlextPluginContext, FlextResult

from flext_db_oracle.api import FlextDbOracleApi

__all__ = [
    "ORACLE_PLUGINS",
    "create_data_validation_plugin",
    "create_performance_monitor_plugin",
    "create_security_audit_plugin",
    "data_validation_plugin_handler",
    "performance_monitor_plugin_handler",
    "register_all_oracle_plugins",
    "security_audit_plugin_handler",
]

class FlextOraclePlugin(FlextPlugin):
    def __init__(
        self, name: str, version: str, config: dict[str, object], handler: object = None
    ) -> None: ...
    @property
    def name(self) -> str: ...
    @property
    def version(self) -> str: ...
    def initialize(self, context: FlextPluginContext) -> FlextResult[None]: ...
    def shutdown(self) -> FlextResult[None]: ...
    def get_config(self) -> dict[str, object]: ...
    def get_info(self) -> dict[str, object]: ...
    def get_handler(self) -> object: ...

class OraclePluginFactory:
    @classmethod
    def create_performance_monitor(cls) -> FlextResult[FlextPlugin]: ...
    @classmethod
    def create_security_audit(cls) -> FlextResult[FlextPlugin]: ...
    @classmethod
    def create_data_validation(cls) -> FlextResult[FlextPlugin]: ...

class OraclePluginHandler:
    @staticmethod
    def create_base_result_data(
        plugin_name: str,
        api: FlextDbOracleApi,
        additional_fields: dict[str, object] | None = None,
    ) -> dict[str, object]: ...
    @staticmethod
    def handle_plugin_exception(
        e: Exception, plugin_name: str
    ) -> FlextResult[dict[str, object]]: ...

def create_performance_monitor_plugin() -> FlextResult[FlextPlugin]: ...
def performance_monitor_plugin_handler(
    api: FlextDbOracleApi,
    sql: str | None = None,
    execution_time_ms: float | None = None,
    **kwargs: object,
) -> FlextResult[dict[str, object]]: ...
def create_security_audit_plugin() -> FlextResult[FlextPlugin]: ...
def security_audit_plugin_handler(
    api: FlextDbOracleApi,
    sql: str | None = None,
    operation_type: str | None = None,
    **kwargs: object,
) -> FlextResult[dict[str, object]]: ...
def create_data_validation_plugin() -> FlextResult[FlextPlugin]: ...
def data_validation_plugin_handler(
    api: FlextDbOracleApi,
    data: dict[str, object] | None = None,
    table_name: str | None = None,
    **kwargs: object,
) -> FlextResult[dict[str, object]]: ...

ORACLE_PLUGINS: Incomplete

def register_all_oracle_plugins(
    api: FlextDbOracleApi,
) -> FlextResult[dict[str, str]]: ...
