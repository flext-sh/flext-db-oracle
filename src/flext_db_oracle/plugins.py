"""Oracle Database Plugins - Extensible plugin examples.

Copyright (c) 2025 FLEXT Contributors
SPDX-License-Identifier: MIT

Examples of custom plugins for Oracle database operations.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from flext_core import FlextResult, get_logger
from flext_plugin import FlextPlugin, create_flext_plugin

if TYPE_CHECKING:
    from flext_db_oracle.api import FlextDbOracleApi

# Constants for data validation - refatoração DRY real
MAX_VARCHAR_LENGTH = 4000
MAX_TABLE_NAME_LENGTH = 150
MAX_AGE_LIMIT = 150


def _validate_data_types(data: dict[str, Any]) -> tuple[list[str], list[str]]:
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


def _validate_business_rules(data: dict[str, Any]) -> list[str]:
    """Validate business rules - DRY pattern for business validation."""
    errors: list[str] = []

    if data.get("email"):
        email = str(data["email"])
        if "@" not in email or "." not in email:
            errors.append("Invalid email format")

    if data.get("age"):
        try:
            age = int(data["age"])
            if age < 0 or age > MAX_AGE_LIMIT:
                errors.append(
                    f"Age must be between 0 and {MAX_AGE_LIMIT}",
                )
        except (ValueError, TypeError):
            errors.append("Age must be a valid number")

    return errors


def _validate_table_structure(table_name: str | None, api: FlextDbOracleApi) -> list[str]:
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


def create_performance_monitor_plugin() -> FlextResult[FlextPlugin]:
    """Create a performance monitoring plugin."""
    # Usar assinaturas corretas da API real - refatoração DRY
    plugin = create_flext_plugin(
        name="oracle_performance_monitor",
        version="1.0.0",
        config={
            "description": "Monitor Oracle database performance and identify slow queries",
            "author": "FLEXT Team",
            "threshold_ms": 1000,
            "log_slow_queries": True,
            "collect_execution_plans": False,
        },
    )

    return FlextResult.ok(plugin)


def performance_monitor_plugin_handler(
    api: FlextDbOracleApi,
    sql: str | None = None,
    execution_time_ms: float | None = None,
    **kwargs: Any,  # noqa: ANN401
) -> FlextResult[dict[str, Any]]:
    """Handle performance monitoring plugin execution."""
    try:
        threshold_ms = kwargs.get("threshold_ms", 1000)

        result_data = {
            "plugin_name": "oracle_performance_monitor",
            "timestamp": api._observability.get_current_timestamp(),  # noqa: SLF001
            "sql": sql,
            "execution_time_ms": execution_time_ms,
            "threshold_ms": threshold_ms,
            "is_slow_query": False,
            "recommendations": [],
        }

        if execution_time_ms and execution_time_ms > threshold_ms:
            result_data["is_slow_query"] = True
            result_data["recommendations"].extend(
                [
                    "Consider adding database indexes",
                    "Review query execution plan",
                    "Check for missing WHERE clauses",
                    "Analyze table statistics",
                ],
            )

            # Log slow query if configured
            if kwargs.get("log_slow_queries", True):
                api._logger.warning(  # noqa: SLF001
                    "Slow query detected: %.2fms > %.2fms threshold",
                    execution_time_ms,
                    threshold_ms,
                )

        return FlextResult.ok(result_data)

    except (ValueError, TypeError, AttributeError) as e:
        return FlextResult.fail(f"Performance monitor plugin failed: {e}")


def create_security_audit_plugin() -> FlextResult[FlextPlugin]:
    """Create a security audit plugin."""
    # Usar assinaturas corretas da API real - refatoração DRY
    plugin = create_flext_plugin(
        name="oracle_security_audit",
        version="1.0.0",
        config={
            "description": "Security audit and compliance monitoring for Oracle operations",
            "author": "FLEXT Team",
            "plugin_type": "security",
            "check_sql_injection": True,
            "audit_ddl_operations": True,
            "log_privilege_escalations": True,
            "callable_obj": security_audit_plugin_handler,
        },
    )

    return FlextResult.ok(plugin)


def security_audit_plugin_handler(
    api: FlextDbOracleApi,
    sql: str | None = None,
    operation_type: str | None = None,
    **kwargs: Any,  # noqa: ANN401
) -> FlextResult[dict[str, Any]]:
    """Handle security audit plugin execution."""
    try:
        # Type annotation explícita para result_data - refatoração DRY real
        result_data: dict[str, Any] = {
            "plugin_name": "oracle_security_audit",
            "timestamp": api._observability.get_current_timestamp(),  # noqa: SLF001
            "sql": sql,
            "operation_type": operation_type,
            "security_warnings": [],
            "compliance_status": "compliant",
        }

        # Garantir type safety para security_warnings list
        security_warnings: list[str] = result_data["security_warnings"]

        if sql:
            sql_upper = sql.upper()

            # Check for potential SQL injection patterns
            if kwargs.get("check_sql_injection", True):
                suspicious_patterns = [
                    "' OR '1'='1'",
                    "UNION SELECT",
                    "DROP TABLE",
                    "DELETE FROM",
                    "; --",
                ]

                for pattern in suspicious_patterns:
                    if pattern in sql_upper:
                        security_warnings.append(
                            f"Potential SQL injection pattern detected: {pattern}",
                        )
                        result_data["compliance_status"] = "warning"

            # Audit DDL operations
            if kwargs.get("audit_ddl_operations", True):
                ddl_operations = ["CREATE", "ALTER", "DROP", "TRUNCATE"]

                for operation in ddl_operations:
                    if sql_upper.startswith(operation):
                        security_warnings.append(
                            f"DDL operation detected: {operation}",
                        )
                        api._logger.info(  # noqa: SLF001
                            "DDL operation audited: %s",
                            operation,
                        )

        if security_warnings:
            result_data["compliance_status"] = (
                "non_compliant" if len(security_warnings) > 1 else "warning"
            )

        return FlextResult.ok(result_data)

    except (ValueError, TypeError, AttributeError) as e:
        return FlextResult.fail(f"Security audit plugin failed: {e}")


def create_data_validation_plugin() -> FlextResult[FlextPlugin]:
    """Create a data validation plugin."""
    # Usar assinaturas corretas da API real - refatoração DRY
    plugin = create_flext_plugin(
        name="oracle_data_validator",
        version="1.0.0",
        config={
            "description": "Validate data integrity and business rules for Oracle operations",
            "author": "FLEXT Team",
            "plugin_type": "validator",
            "validate_data_types": True,
            "check_constraints": True,
            "enforce_business_rules": True,
            "callable_obj": data_validation_plugin_handler,
        },
    )

    return FlextResult.ok(plugin)


def data_validation_plugin_handler(
    api: FlextDbOracleApi,
    data: dict[str, Any] | None = None,
    table_name: str | None = None,
    **kwargs: Any,  # noqa: ANN401
) -> FlextResult[dict[str, Any]]:
    """Handle data validation plugin execution."""
    try:
        # Type annotation explícita para result_data - refatoração DRY real
        result_data: dict[str, Any] = {
            "plugin_name": "oracle_data_validator",
            "timestamp": api._observability.get_current_timestamp(),  # noqa: SLF001
            "table_name": table_name,
            "data": data,
            "validation_errors": [],
            "validation_warnings": [],
            "validation_status": "valid",
        }

        # Garantir type safety para validation lists
        validation_errors: list[str] = result_data["validation_errors"]
        validation_warnings: list[str] = result_data["validation_warnings"]

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

        # Set validation status
        if validation_errors:
            result_data["validation_status"] = "invalid"
        elif validation_warnings:
            result_data["validation_status"] = "warning"

        return FlextResult.ok(result_data)

    except (ValueError, TypeError, AttributeError) as e:
        return FlextResult.fail(f"Data validation plugin failed: {e}")


# Plugin registry for easy access
ORACLE_PLUGINS = {
    "performance_monitor": create_performance_monitor_plugin,
    "security_audit": create_security_audit_plugin,
    "data_validator": create_data_validation_plugin,
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
