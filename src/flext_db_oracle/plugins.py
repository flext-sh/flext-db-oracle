"""FLEXT DB Oracle Plugin System.

This module provides an extensible plugin system for Oracle database operations
using FLEXT Plugin patterns and Clean Architecture principles. It implements
comprehensive plugin examples for performance monitoring, security auditing,
and data validation with DRY patterns and SOLID design principles.

Key Components:
    - OraclePluginFactory: Factory for creating Oracle-specific plugins with DRY patterns
    - OraclePluginHandler: Base handler providing common plugin execution patterns
    - Performance Monitor Plugin: Monitors query execution times and identifies bottlenecks
    - Security Audit Plugin: Provides SQL injection detection and compliance checking
    - Data Validation Plugin: Validates data integrity and business rules

Architecture:
    This module implements the Application layer's plugin concern using Factory
    and Template Method design patterns. It follows Clean Architecture by
    separating plugin creation, execution, and business logic concerns while
    maintaining strong integration with the FLEXT ecosystem.

Example:
    Register and use Oracle plugins:

    >>> from flext_db_oracle import FlextDbOracleApi, register_all_oracle_plugins
    >>> api = FlextDbOracleApi.from_env()
    >>> api.connect()
    >>>
    >>> # Register all built-in plugins
    >>> register_result = register_all_oracle_plugins(api)
    >>> registration_success = register_result.unwrap_or(False)
    >>> if registration_success:
    ...     print("All plugins registered successfully")
    >>>
    >>> # Use performance monitoring plugin
    >>> result = api.execute_with_plugin(
    ...     "performance_monitor",
    ...     {"sql": "SELECT * FROM large_table", "threshold_ms": 500},
    ... )

Integration:
    - Built on flext-plugin foundation for enterprise plugin management
    - Integrates with flext-core FlextResult patterns for error handling
    - Supports flext-observability for plugin operation monitoring
    - Compatible with FLEXT ecosystem plugin discovery and management
    - Provides extension points for custom Oracle-specific functionality

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from collections.abc import Callable
from datetime import UTC, datetime

from flext_core import (
    FlextDomainService,
    FlextPlugin,
    FlextPluginContext,
    FlextResult,
    get_logger,
)

from flext_db_oracle.api import FlextDbOracleApi
from flext_db_oracle.constants import FlextDbOracleConstants
from flext_db_oracle.typings import (
    is_result_like,
)

# Constants for data validation - refatoração DRY real
MAX_VARCHAR_LENGTH = 4000


def _validate_data_types(data: dict[str, object]) -> tuple[list[str], list[str]]:
    """Validate data types - DRY pattern for type validation."""
    errors: list[str] = []
    warnings: list[str] = []

    for key, value in data.items():
        if isinstance(value, str) and len(value) > MAX_VARCHAR_LENGTH:
            warnings.append(
                f"Field {key} exceeds VARCHAR2({MAX_VARCHAR_LENGTH}) limit",
            )

        if key.upper().endswith("_ID") and not isinstance(value, (int, str)):
            errors.append(
                f"Field {key} should be numeric or string for ID fields",
            )

    return errors, warnings


def _validate_business_rules(data: dict[str, object]) -> list[str]:
    """Validate business rules - DRY pattern for business validation.

    SOLID REFACTORING: Reduced complexity from 22 using Extract Method pattern.
    """
    errors: list[str] = []

    # Oracle-specific business rules validation only
    table_name_errors = _validate_table_name_business_rules(data)
    errors.extend(table_name_errors)

    # Validate salary (Oracle-relevant business rule)
    if "salary" in data and data["salary"] is not None:
        try:
            # Type narrowing for MyPy
            salary_value = data["salary"]
            if isinstance(salary_value, (int, float, str)):
                salary = float(salary_value)
                if salary < 0:
                    errors.append("Salary cannot be negative")
            else:
                errors.append("Salary must be a valid number")
        except (ValueError, TypeError):
            errors.append("Salary must be a valid number")

    return errors


def _validate_table_name_business_rules(data: dict[str, object]) -> list[str]:
    """SOLID REFACTORING: Extract Method for table name validation.

    Single Responsibility - handles only table name business rules.
    """
    errors: list[str] = []

    if "table_name" in data and data["table_name"] is not None:
        table_name = str(data["table_name"])
        if (
            len(table_name)
            > FlextDbOracleConstants.OracleValidation.MAX_TABLE_NAME_LENGTH
        ):
            errors.append("Table name too long")

    return errors


def _validate_table_structure(
    table_name: str | None,
    api: FlextDbOracleApi,
) -> list[str]:
    """Validate table structure - DRY pattern for table validation."""
    errors: list[str] = []

    if not table_name:
        return errors

    if len(table_name) > FlextDbOracleConstants.OracleValidation.MAX_TABLE_NAME_LENGTH:
        errors.append(
            f"Table name exceeds maximum length of {FlextDbOracleConstants.OracleValidation.MAX_TABLE_NAME_LENGTH}",
        )

    # Check if table exists - usando API real - refatoração DRY
    try:
        # Using railway pattern for proper error handling
        tables_result = api.get_tables()
        # Modern FlextResult pattern: use .value for tables validation
        if tables_result.is_success:
            tables_list = tables_result.value
            if tables_list:
                # PyRight fix: Proper type checking for table objects
                table_names: list[str] = []
                for table_obj in tables_list:
                    if hasattr(table_obj, "name"):
                        table_names.append(str(table_obj.name))
                    else:
                        table_names.append(str(table_obj))

                if table_name.upper() not in [t.upper() for t in table_names]:
                    errors.append(f"Table '{table_name}' does not exist")
        # If tables_result failed, skip table validation (no error)
    except Exception as e:
        # Log but don't fail validation if table check fails - refatoração DRY real
        logger = get_logger(f"{__name__}._validate_table_structure")
        logger.debug("Table existence check failed: %s", str(e))

    return errors


# =============================================================================
# FLEXT[AREA][MODULE] PATTERN - Oracle Plugins (DRY CONSOLIDATED)
# =============================================================================


def create_performance_monitor_plugin() -> FlextResult[FlextPlugin]:
    """Create a performance monitoring plugin using consolidated DRY factory."""
    return FlextDbOraclePlugins.create_performance_monitor()


def performance_monitor_plugin_handler(
    api: FlextDbOracleApi,
    sql: str | None = None,
    execution_time_ms: float | None = None,
    **kwargs: object,
) -> FlextResult[dict[str, object]]:
    """Handle performance monitoring plugin execution using DRY patterns."""
    try:
        threshold_raw = kwargs.get("threshold_ms", 1000)
        threshold_ms = (
            float(threshold_raw)
            if isinstance(threshold_raw, (int, float, str))
            else 1000.0
        )

        result_data = FlextDbOraclePlugins._create_base_result_data(
            "oracle_performance_monitor",
            api,
            {
                "sql": sql,
                "execution_time_ms": execution_time_ms,
                "threshold_ms": threshold_ms,
                "is_slow_query": False,
                "recommendations": [],
            },
        )

        if execution_time_ms and execution_time_ms > threshold_ms:
            result_data["is_slow_query"] = True
            recommendations_raw = result_data.get("recommendations", [])

            # PyRight FIX: Ensure proper list[str] typing with type narrowing
            recommendations: list[str] = []
            if isinstance(recommendations_raw, list):
                recommendations = [
                    str(item) if item is not None else ""
                    for item in recommendations_raw
                ]

            recommendations.extend([
                "Consider adding database indexes",
                "Review query execution plan",
                "Check for missing WHERE clauses",
                "Analyze table statistics",
            ])
            result_data["recommendations"] = recommendations

            # Log slow query if configured
            if kwargs.get("log_slow_queries", True):
                logger = get_logger("oracle_performance_monitor")
                logger.warning(
                    "Slow query detected: %.2fms > %.2fms threshold",
                    execution_time_ms,
                    threshold_ms,
                )

        return FlextResult[dict[str, object]].ok(result_data)

    except (ValueError, TypeError, AttributeError) as e:
        return FlextDbOraclePlugins._handle_plugin_exception(e, "Performance monitor")


def create_security_audit_plugin() -> FlextResult[FlextPlugin]:
    """Create a security audit plugin using consolidated DRY factory."""
    return FlextDbOraclePlugins.create_security_audit()


def security_audit_plugin_handler(
    api: FlextDbOracleApi,
    sql: str | None = None,
    operation_type: str | None = None,
    **kwargs: object,
) -> FlextResult[dict[str, object]]:
    """Handle security audit plugin execution using DRY patterns.

    SOLID REFACTORING: Reduced complexity from 24 using Extract Method pattern.
    """
    try:
        # SOLID Extract Method - Create base result structure
        result_data = FlextDbOraclePlugins._create_base_result_data(
            "oracle_security_audit",
            api,
            {
                "sql": sql,
                "operation_type": operation_type,
                "security_warnings": [],
                "compliance_status": "compliant",
            },
        )

        # SOLID Extract Method - Process SQL security audit
        if sql:
            security_warnings = _process_sql_security_audit(sql, api, kwargs)
            result_data["security_warnings"] = security_warnings

            # SOLID Extract Method - Update compliance status
            result_data["compliance_status"] = _determine_compliance_status(
                security_warnings,
            )

        return FlextResult[dict[str, object]].ok(result_data)

    except (ValueError, TypeError, AttributeError) as e:
        return FlextDbOraclePlugins._handle_plugin_exception(e, "Security audit")


def _process_sql_security_audit(
    sql: str,
    api: FlextDbOracleApi,
    kwargs: dict[str, object],
) -> list[str]:
    """SOLID REFACTORING: Extract Method for SQL security audit processing.

    Single Responsibility - handles all SQL-related security checks.
    """
    security_warnings: list[str] = []
    sql_upper = sql.upper()

    # SOLID Extract Method - Check SQL injection patterns
    injection_warnings = _check_sql_injection_patterns(sql_upper, kwargs)
    security_warnings.extend(injection_warnings)

    # SOLID Extract Method - Audit DDL operations
    ddl_warnings = _audit_ddl_operations(sql_upper, api, kwargs)
    security_warnings.extend(ddl_warnings)

    return security_warnings


def _check_sql_injection_patterns(
    sql_upper: str,
    kwargs: dict[str, object],
) -> list[str]:
    """SOLID REFACTORING: Extract Method for SQL injection pattern detection.

    Single Responsibility - handles only SQL injection pattern checking.
    """
    warnings: list[str] = []

    if kwargs.get("check_sql_injection", True):
        suspicious_patterns = [
            "' OR '1'='1'",
            "UNION SELECT",
            "DROP TABLE",
            "DELETE FROM",
            "; --",
        ]

        warnings.extend(
            f"Potential SQL injection pattern detected: {pattern}"
            for pattern in suspicious_patterns
            if pattern in sql_upper
        )

    return warnings


def _audit_ddl_operations(
    sql_upper: str,
    api: FlextDbOracleApi,  # noqa: ARG001 - api kept for consistent interface
    kwargs: dict[str, object],
) -> list[str]:
    """SOLID REFACTORING: Extract Method for DDL operation auditing.

    Single Responsibility - handles only DDL operation detection and logging.
    """
    warnings: list[str] = []

    if kwargs.get("audit_ddl_operations", True):
        ddl_operations = ["CREATE", "ALTER", "DROP", "TRUNCATE"]

        for operation in ddl_operations:
            if sql_upper.startswith(operation):
                warnings.append(
                    f"DDL operation detected: {operation}",
                )
                logger = get_logger("oracle_security_audit")
                logger.info(
                    "DDL operation audited: %s",
                    operation,
                )

    return warnings


def _determine_compliance_status(security_warnings: list[str]) -> str:
    """SOLID REFACTORING: Extract Method for compliance status determination.

    Single Responsibility - handles only compliance status logic.
    """
    if not security_warnings:
        return "compliant"
    if len(security_warnings) > 1:
        return "non_compliant"
    return "warning"


def create_data_validation_plugin() -> FlextResult[FlextPlugin]:
    """Create a data validation plugin using consolidated DRY factory."""
    return FlextDbOraclePlugins.create_data_validation()


def data_validation_plugin_handler(
    api: FlextDbOracleApi,
    data: dict[str, object] | None = None,
    table_name: str | None = None,
    **kwargs: object,
) -> FlextResult[dict[str, object]]:
    """Handle data validation plugin execution using DRY patterns."""
    try:
        result_data = FlextDbOraclePlugins._create_base_result_data(
            "oracle_data_validator",
            api,
            {
                "table_name": table_name,
                "data": data,
                "validation_errors": [],
                "validation_warnings": [],
                "validation_status": "valid",
            },
        )

        # PyRight FIX: Safe access to validation lists with proper typing
        validation_errors_obj = result_data.get("validation_errors", [])
        validation_warnings_obj = result_data.get("validation_warnings", [])

        # Ensure proper list[str] typing with type narrowing
        validation_errors: list[str] = []
        if isinstance(validation_errors_obj, list):
            validation_errors = [
                str(item) if item is not None else "" for item in validation_errors_obj
            ]

        validation_warnings: list[str] = []
        if isinstance(validation_warnings_obj, list):
            validation_warnings = [
                str(item) if item is not None else ""
                for item in validation_warnings_obj
            ]

        # Apply DRY validation patterns - refatoração real
        if data and kwargs.get("validate_data_types", True):
            type_errors, type_warnings = _validate_data_types(data)
            validation_errors.extend(type_errors)
            validation_warnings.extend(type_warnings)

        if kwargs.get("enforce_business_rules", True) and data:
            business_errors = _validate_business_rules(data)
            validation_errors.extend(business_errors)

        if table_name:
            table_errors = _validate_table_structure(table_name, api)
            validation_errors.extend(table_errors)

        # Update result_data with modified lists
        result_data["validation_errors"] = validation_errors
        result_data["validation_warnings"] = validation_warnings

        # Set validation status
        if validation_errors:
            result_data["validation_status"] = "invalid"
        elif validation_warnings:
            result_data["validation_status"] = "warning"

        return FlextResult[dict[str, object]].ok(result_data)

    except (ValueError, TypeError, AttributeError) as e:
        return FlextDbOraclePlugins._handle_plugin_exception(e, "Data validation")


# Plugin registry for easy access - using wrapper functions that return correct types
ORACLE_PLUGINS: dict[str, Callable[[], FlextResult[FlextPlugin]]] = {
    "performance_monitor": create_performance_monitor_plugin,
    "security_audit": create_security_audit_plugin,
    "data_validator": create_data_validation_plugin,
}


def _register_single_plugin(  # noqa: PLR0911
    api: FlextDbOracleApi,
    plugin_name: str,
    plugin_creator: object,
) -> str:
    """DRY helper: Register single plugin and return status message."""
    try:
        # Guard clause: Check if creator is callable
        if not callable(plugin_creator):
            return f"❌ {plugin_name}: Plugin creator is not callable"

        # Execute plugin creator
        plugin_result = plugin_creator()

        # Guard clause: Check if result is valid FlextResult-like
        if not is_result_like(plugin_result):
            return f"❌ {plugin_name}: Plugin creator returned invalid result"

        # Modern FlextResult pattern: use unwrap_or for plugin creation
        # PyRight FIX: Properly typed lambda with object parameter
        def default_fallback(_unused: object) -> None:
            return None

        plugin = getattr(plugin_result, "unwrap_or", default_fallback)(None)
        if plugin is None:
            error_msg = getattr(plugin_result, "error", "Unknown error")
            return f"creation_failed: {error_msg}"
        if plugin is None:
            return "failed: plugin is None"

        # Register plugin and return result
        register_result = api.register_plugin(plugin_name, plugin)
        # Modern FlextResult pattern: use .value for plugin registration
        if register_result.is_success:
            return "registered"
        return f"failed: {register_result.error}"

    except Exception as e:
        return f"error: {e}"


def register_all_oracle_plugins(api: FlextDbOracleApi) -> FlextResult[dict[str, str]]:
    """Register all Oracle plugins with the API using DRY helper."""
    results: dict[str, str] = {}

    for plugin_name, plugin_creator in ORACLE_PLUGINS.items():
        results[plugin_name] = _register_single_plugin(api, plugin_name, plugin_creator)

    return FlextResult[dict[str, str]].ok(results)


# =============================================================================
# FLEXT[AREA][MODULE] PATTERN - Oracle Plugins
# =============================================================================


class FlextDbOraclePlugins(FlextDomainService[dict[str, str]]):
    """Oracle database plugins following Flext[Area][Module] pattern - DRY CONSOLIDATED.

    MAJOR DRY REFACTORING: Consolidates FlextOraclePlugin + OraclePluginFactory + OraclePluginHandler
    into single large class following user feedback to "criar classes grandes e aplicar conceitos DRY".

    Inherits from FlextDomainService to leverage FLEXT Core domain service patterns.
    This class serves as the SINGLE ENTRY POINT for ALL Oracle plugin functionality:
    - Plugin creation and factory patterns (from OraclePluginFactory)
    - Plugin implementation and interface compliance (from FlextOraclePlugin)
    - Plugin execution handlers and DRY patterns (from OraclePluginHandler)
    - Plugin registry and lifecycle management (from FlextDbOraclePlugins)

    Examples:
        Plugin management operations:
        >>> plugins = FlextDbOraclePlugins()
        >>> api = FlextDbOracleApi.from_env().value
        >>> result = plugins.register_all_plugins(api)
        >>> print(f"Registered plugins: {result.value}")

    """

    # =============================================================================
    # CONSOLIDATED PLUGIN CONSTANTS AND FACTORY PATTERNS
    # =============================================================================

    _PLUGIN_VERSION = "0.9.0"
    _PLUGIN_AUTHOR = "FLEXT Team"

    # =============================================================================
    # CONSOLIDATED PLUGIN IMPLEMENTATION (from FlextOraclePlugin)
    # =============================================================================

    class _InternalOraclePlugin:
        """Internal Oracle plugin implementation consolidated into FlextDbOraclePlugins.

        DRY CONSOLIDATION: Moved from separate FlextOraclePlugin class to eliminate
        multiple small classes and follow DRY principles with large consolidated class.
        """

        def __init__(
            self,
            name: str,
            version: str,
            config: dict[str, object],
            handler: object = None,
        ) -> None:
            """Initialize Oracle plugin with configuration and handler."""
            self._name = name
            self._version = version
            self._config = config.copy()
            self._handler = handler
            self._logger = get_logger(f"FlextOraclePlugin.{name}")

        @property
        def name(self) -> str:
            """Plugin name from abstract interface."""
            return self._name

        @property
        def version(self) -> str:
            """Plugin version from abstract interface."""
            return self._version

        def initialize(self, context: FlextPluginContext) -> FlextResult[None]:
            """Initialize plugin with context from abstract interface."""
            try:
                # Use context for initialization if needed
                _ = context  # Acknowledge parameter for interface compliance
                self._logger.info("Oracle plugin initialized", plugin_name=self.name)
                return FlextResult[None].ok(None)
            except Exception as e:
                return FlextResult[None].fail(f"Oracle plugin initialization failed: {e}")

        def shutdown(self) -> FlextResult[None]:
            """Shutdown plugin and release resources from abstract interface."""
            try:
                self._logger.info("Oracle plugin shutdown", plugin_name=self.name)
                return FlextResult[None].ok(None)
            except Exception as e:
                return FlextResult[None].fail(f"Oracle plugin shutdown failed: {e}")

        def configure(self, config: dict[str, object]) -> FlextResult[None]:
            """Configure plugin with provided settings."""
            try:
                self._config.update(config)
                self._logger.info("Oracle plugin configured", plugin_name=self.name)
                return FlextResult[None].ok(None)
            except Exception as e:
                return FlextResult[None].fail(f"Oracle plugin configuration failed: {e}")

        def get_config(self) -> dict[str, object]:
            """Get plugin configuration."""
            return self._config.copy()

        def get_info(self) -> dict[str, object]:
            """Get plugin information."""
            return {
                "name": self._name,
                "version": self._version,
                "plugin_type": self._config.get("plugin_type", "unknown"),
                "description": self._config.get("description", ""),
                "author": self._config.get("author", "FLEXT Team"),
            }

        def get_handler(self) -> object:
            """Get plugin handler."""
            return self._handler

    # =============================================================================
    # CONSOLIDATED FACTORY PATTERNS (from OraclePluginFactory)
    # =============================================================================

    @classmethod
    def _create_plugin_template(
        cls,
        name: str,
        description: str,
        plugin_type: str,
        specific_config: dict[str, object],
    ) -> FlextResult[FlextPlugin]:
        """Template method for creating Oracle plugins with consistent patterns.

        DRY CONSOLIDATION: Moved from OraclePluginFactory to eliminate separate factory class.
        """
        base_config: dict[str, object] = {
            "description": description,
            "author": cls._PLUGIN_AUTHOR,
            "plugin_type": plugin_type,
        }

        # Merge base config with specific config
        full_config: dict[str, object] = {**base_config, **specific_config}

        try:
            # Create concrete internal plugin implementation
            plugin = cls._InternalOraclePlugin(
                name=name,
                version=cls._PLUGIN_VERSION,
                config=full_config,
                handler=specific_config.get("callable_obj"),
            )
            return FlextResult[FlextPlugin].ok(plugin)
        except Exception as e:
            return FlextResult[FlextPlugin].fail(
                f"Failed to create Oracle plugin '{name}': {e}"
            )

    # =============================================================================
    # CONSOLIDATED HANDLER PATTERNS (from OraclePluginHandler)
    # =============================================================================

    @staticmethod
    def _create_base_result_data(
        plugin_name: str,
        _api: FlextDbOracleApi,
        additional_fields: dict[str, object] | None = None,
    ) -> dict[str, object]:
        """Template method: Create base result data structure.

        DRY CONSOLIDATION: Moved from OraclePluginHandler to eliminate separate handler class.
        """
        base_data: dict[str, object] = {
            "plugin_name": plugin_name,
            "timestamp": datetime.now(UTC).isoformat(),
        }

        if additional_fields:
            base_data.update(additional_fields)

        return base_data

    @staticmethod
    def _handle_plugin_exception(
        e: Exception,
        plugin_name: str,
    ) -> FlextResult[dict[str, object]]:
        """Template method: Consistent exception handling for plugins.

        DRY CONSOLIDATION: Moved from OraclePluginHandler to eliminate separate handler class.
        """
        return FlextResult[dict[str, object]].fail(f"{plugin_name} plugin failed: {e}")

    def execute(self) -> FlextResult[dict[str, str]]:
        """Execute plugin management operation.

        Returns plugin registry status indicating available plugins.
        """
        try:
            return FlextResult[dict[str, str]].ok({
                "status": "available",
                "plugins": ", ".join(ORACLE_PLUGINS.keys()),
                "count": str(len(ORACLE_PLUGINS)),
            })
        except Exception as e:
            return FlextResult[dict[str, str]].fail(f"Plugin registry failed: {e}")

    @staticmethod
    def register_all_plugins(api: FlextDbOracleApi) -> FlextResult[dict[str, str]]:
        """Register all Oracle plugins using factory pattern."""
        return register_all_oracle_plugins(api)

    @classmethod
    def create_performance_monitor(cls) -> FlextResult[FlextPlugin]:
        """Create performance monitoring plugin using consolidated DRY template."""
        return cls._create_plugin_template(
            name="oracle_performance_monitor",
            description="Monitor Oracle database performance and identify slow queries",
            plugin_type="monitor",
            specific_config={
                "threshold_ms": 1000,
                "log_slow_queries": True,
                "collect_execution_plans": False,
                "callable_obj": performance_monitor_plugin_handler,
            },
        )

    @classmethod
    def create_security_audit(cls) -> FlextResult[FlextPlugin]:
        """Create security audit plugin using consolidated DRY template."""
        return cls._create_plugin_template(
            name="oracle_security_audit",
            description="Security audit and compliance monitoring for Oracle operations",
            plugin_type="security",
            specific_config={
                "check_sql_injection": True,
                "audit_ddl_operations": True,
                "log_privilege_escalations": True,
                "callable_obj": security_audit_plugin_handler,
            },
        )

    @classmethod
    def create_data_validation(cls) -> FlextResult[FlextPlugin]:
        """Create data validation plugin using consolidated DRY template."""
        return cls._create_plugin_template(
            name="oracle_data_validator",
            description="Validate data integrity and business rules for Oracle operations",
            plugin_type="validator",
            specific_config={
                "validate_data_types": True,
                "check_constraints": True,
                "enforce_business_rules": True,
                "callable_obj": data_validation_plugin_handler,
            },
        )

    @staticmethod
    def get_available_plugins() -> dict[str, Callable[[], FlextResult[FlextPlugin]]]:
        """Get available Oracle plugin factories."""
        return ORACLE_PLUGINS.copy()

    def validate_plugin_configuration(self, api: FlextDbOracleApi) -> FlextResult[bool]:
        """Validate plugin configuration for Oracle API."""
        try:
            # Check if API has plugin capabilities
            if not hasattr(api, "register_plugin"):
                return FlextResult[bool].fail(
                    "API does not support plugin registration"
                )

            # Verify plugin registry is properly populated
            if not ORACLE_PLUGINS:
                return FlextResult[bool].fail("No plugins available in registry")

            return FlextResult[bool].ok(data=True)
        except Exception as e:
            return FlextResult[bool].fail(
                f"Plugin configuration validation failed: {e}"
            )


__all__: list[str] = [
    "ORACLE_PLUGINS",
    "FlextDbOraclePlugins",
    "create_data_validation_plugin",
    "create_performance_monitor_plugin",
    "create_security_audit_plugin",
    "data_validation_plugin_handler",
    "performance_monitor_plugin_handler",
    "register_all_oracle_plugins",
    "security_audit_plugin_handler",
]
