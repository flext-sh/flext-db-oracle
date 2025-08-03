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
    >>> if register_result.is_success:
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

Author: FLEXT Development Team
Version: 2.0.0
License: MIT

"""

from __future__ import annotations

from typing import TYPE_CHECKING

from flext_core import FlextResult, get_logger
from flext_plugin import FlextPlugin, create_flext_plugin

if TYPE_CHECKING:
    from flext_db_oracle.api import FlextDbOracleApi

# Constants for data validation - refatoração DRY real
MAX_VARCHAR_LENGTH = 4000
MAX_TABLE_NAME_LENGTH = 150
MAX_AGE_LIMIT = 150


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

    # SOLID Extract Method - Validate individual business rules
    email_errors = _validate_email_business_rules(data)
    age_errors = _validate_age_business_rules(data)
    table_name_errors = _validate_table_name_business_rules(data)

    # Combine all validation errors
    errors.extend(email_errors)
    errors.extend(age_errors)
    errors.extend(table_name_errors)

    return errors


def _validate_email_business_rules(data: dict[str, object]) -> list[str]:
    """SOLID REFACTORING: Extract Method for email validation.

    Single Responsibility - handles only email business rules.
    """
    errors: list[str] = []

    if "email" in data:
        email_value = data["email"]
        if email_value is None:
            errors.append("Email cannot be None")
        else:
            email = str(email_value)
            if "@" not in email or "." not in email:
                errors.append("Invalid email format")

    return errors


def _validate_age_business_rules(data: dict[str, object]) -> list[str]:
    """SOLID REFACTORING: Extract Method for age validation.

    Single Responsibility - handles only age business rules with type safety.
    """
    errors: list[str] = []

    if "age" in data and data["age"] is not None:
        try:
            # MYPY FIX: Safe conversion from object to int
            age_value = data["age"]
            if isinstance(age_value, (int, str)):
                age = int(age_value)
            else:
                errors.append("Age must be a number")
                return errors
            if age <= 0 or age > MAX_AGE_LIMIT:
                errors.append(
                    f"Age must be between 1 and {MAX_AGE_LIMIT}",
                )
        except (ValueError, TypeError):
            errors.append("Age must be a valid number")

    return errors


def _validate_table_name_business_rules(data: dict[str, object]) -> list[str]:
    """SOLID REFACTORING: Extract Method for table name validation.

    Single Responsibility - handles only table name business rules.
    """
    errors: list[str] = []

    if "table_name" in data and data["table_name"] is not None:
        table_name = str(data["table_name"])
        if len(table_name) > MAX_TABLE_NAME_LENGTH:
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

    if len(table_name) > MAX_TABLE_NAME_LENGTH:
        errors.append(
            f"Table name exceeds maximum length of {MAX_TABLE_NAME_LENGTH}",
        )

    # Check if table exists - usando API real - refatoração DRY
    try:
        tables_result = api.get_tables()
        if tables_result.is_success and tables_result.data:
            table_names = [
                getattr(t, "name", str(t)) if hasattr(t, "name") else str(t)
                for t in tables_result.data
            ]
            if table_name.upper() not in [t.upper() for t in table_names]:
                errors.append(f"Table '{table_name}' does not exist")
    except Exception as e:  # noqa: BLE001 # broad exception for plugin safety
        # Log but don't fail validation if table check fails - refatoração DRY real
        logger = get_logger(f"{__name__}._validate_table_structure")
        logger.debug("Table existence check failed: %s", str(e))

    return errors


# =============================================================================
# REFACTORING: Template Method + Factory Pattern for DRY plugin creation
# =============================================================================


class OraclePluginFactory:
    """Factory for creating Oracle plugins with DRY patterns.

    SOLID REFACTORING: Eliminates 18+ lines of duplicated plugin creation code
    (mass=95) using Template Method and Factory patterns.
    """

    _PLUGIN_VERSION = "0.9.0"
    _PLUGIN_AUTHOR = "FLEXT Team"

    @classmethod
    def _create_plugin_template(
        cls,
        name: str,
        description: str,
        plugin_type: str,
        specific_config: dict[str, object],
    ) -> FlextResult[FlextPlugin]:
        """Template method for creating Oracle plugins with consistent patterns."""
        base_config: dict[str, object] = {
            "description": description,
            "author": cls._PLUGIN_AUTHOR,
            "plugin_type": plugin_type,
        }

        # Merge base config with specific config
        full_config: dict[str, object] = {**base_config, **specific_config}

        plugin: FlextPlugin | None = create_flext_plugin(
            name=name,
            version=cls._PLUGIN_VERSION,
            config=full_config,
        )

        if plugin is None:
            return FlextResult.fail(f"Failed to create plugin '{name}'")

        return FlextResult.ok(plugin)

    @classmethod
    def create_performance_monitor(cls) -> FlextResult[FlextPlugin]:
        """Create performance monitoring plugin using DRY template."""
        return cls._create_plugin_template(
            name="oracle_performance_monitor",
            description="Monitor Oracle database performance and identify slow queries",
            plugin_type="monitor",
            specific_config={
                "threshold_ms": 1000,
                "log_slow_queries": True,
                "collect_execution_plans": False,
            },
        )

    @classmethod
    def create_security_audit(cls) -> FlextResult[FlextPlugin]:
        """Create security audit plugin using DRY template."""
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
        """Create data validation plugin using DRY template."""
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


class OraclePluginHandler:
    """Base handler providing DRY patterns for Oracle plugin execution.

    SOLID REFACTORING: Centralizes common plugin execution patterns.
    """

    @staticmethod
    def create_base_result_data(
        plugin_name: str,
        api: FlextDbOracleApi,
        additional_fields: dict[str, object] | None = None,
    ) -> dict[str, object]:
        """Template method: Create base result data structure."""
        base_data: dict[str, object] = {
            "plugin_name": plugin_name,
            "timestamp": api._observability.get_current_timestamp(),  # noqa: SLF001
        }

        if additional_fields:
            base_data.update(additional_fields)

        return base_data

    @staticmethod
    def handle_plugin_exception(
        e: Exception,
        plugin_name: str,
    ) -> FlextResult[dict[str, object]]:
        """Template method: Consistent exception handling for plugins."""
        return FlextResult.fail(f"{plugin_name} plugin failed: {e}")


def create_performance_monitor_plugin() -> FlextResult[FlextPlugin]:
    """Create a performance monitoring plugin using DRY factory."""
    return OraclePluginFactory.create_performance_monitor()


def performance_monitor_plugin_handler(
    api: FlextDbOracleApi,
    sql: str | None = None,
    execution_time_ms: float | None = None,
    **kwargs: object,
) -> FlextResult[dict[str, object]]:
    """Handle performance monitoring plugin execution using DRY patterns."""
    try:
        threshold_raw = kwargs.get("threshold_ms", 1000)
        threshold_ms = float(threshold_raw) if isinstance(threshold_raw, (int, float, str)) else 1000.0

        result_data = OraclePluginHandler.create_base_result_data(
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
            recommendations: list[str] = recommendations_raw if isinstance(recommendations_raw, list) else []
            if isinstance(recommendations, list):
                recommendations.extend(
                    [
                        "Consider adding database indexes",
                        "Review query execution plan",
                        "Check for missing WHERE clauses",
                        "Analyze table statistics",
                    ],
                )
                result_data["recommendations"] = recommendations

            # Log slow query if configured
            if kwargs.get("log_slow_queries", True):
                api._logger.warning(  # noqa: SLF001
                    "Slow query detected: %.2fms > %.2fms threshold",
                    execution_time_ms,
                    threshold_ms,
                )

        return FlextResult.ok(result_data)

    except (ValueError, TypeError, AttributeError) as e:
        return OraclePluginHandler.handle_plugin_exception(e, "Performance monitor")


def create_security_audit_plugin() -> FlextResult[FlextPlugin]:
    """Create a security audit plugin using DRY factory."""
    return OraclePluginFactory.create_security_audit()


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
        result_data = OraclePluginHandler.create_base_result_data(
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

        return FlextResult.ok(result_data)

    except (ValueError, TypeError, AttributeError) as e:
        return OraclePluginHandler.handle_plugin_exception(e, "Security audit")


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
    api: FlextDbOracleApi,
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
                api._logger.info(  # noqa: SLF001
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
    """Create a data validation plugin using DRY factory."""
    return OraclePluginFactory.create_data_validation()


def data_validation_plugin_handler(
    api: FlextDbOracleApi,
    data: dict[str, object] | None = None,
    table_name: str | None = None,
    **kwargs: object,
) -> FlextResult[dict[str, object]]:
    """Handle data validation plugin execution using DRY patterns."""
    try:
        result_data = OraclePluginHandler.create_base_result_data(
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

        # MYPY FIX: Safe access to validation lists
        validation_errors_obj = result_data.get("validation_errors", [])
        validation_warnings_obj = result_data.get("validation_warnings", [])
        validation_errors: list[str] = (
            validation_errors_obj if isinstance(validation_errors_obj, list) else []
        )
        validation_warnings: list[str] = (
            validation_warnings_obj if isinstance(validation_warnings_obj, list) else []
        )

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

        return FlextResult.ok(result_data)

    except (ValueError, TypeError, AttributeError) as e:
        return OraclePluginHandler.handle_plugin_exception(e, "Data validation")


# Plugin registry for easy access - using DRY factory methods
ORACLE_PLUGINS = {
    "performance_monitor": OraclePluginFactory.create_performance_monitor,
    "security_audit": OraclePluginFactory.create_security_audit,
    "data_validator": OraclePluginFactory.create_data_validation,
}


def register_all_oracle_plugins(api: FlextDbOracleApi) -> FlextResult[dict[str, str]]:
    """Register all Oracle plugins with the API."""
    results = {}

    for plugin_name, plugin_creator in ORACLE_PLUGINS.items():
        try:
            plugin_result = plugin_creator()
            if plugin_result.is_success:
                plugin = plugin_result.data
                # Type annotation explícita para plugin - refatoração DRY real
                if plugin is not None:
                    register_result = api.register_plugin(plugin)
                    if register_result.is_success:
                        results[plugin_name] = "registered"
                    else:
                        results[plugin_name] = f"failed: {register_result.error}"
                else:
                    results[plugin_name] = "failed: plugin is None"
            else:
                results[plugin_name] = f"creation_failed: {plugin_result.error}"
        except Exception as e:  # noqa: BLE001
            results[plugin_name] = f"error: {e}"

    return FlextResult.ok(results)


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
