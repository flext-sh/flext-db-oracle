"""Oracle database Pydantic models following Flext[Area][Module] pattern.

This module contains Oracle-specific models using modern patterns from flext-core.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Self, TypedDict, TypeGuard, cast

from flext_core import FlextLogger, FlextModels, FlextResult, FlextTypes
from pydantic import Field, SecretStr, field_validator, model_validator
from pydantic.fields import FieldInfo
from pydantic_settings import BaseSettings, SettingsConfigDict

from flext_db_oracle.constants import FlextDbOracleConstants
from flext_db_oracle.mixins import OracleValidationFactory

logger = FlextLogger(__name__)


class FlextDbOracleModels:
    """Oracle database models following Flext[Area][Module] pattern."""

    # ==========================================================================
    # ORACLE-SPECIFIC FIELD FACTORY METHODS
    # ==========================================================================

    @classmethod
    def host_field(cls, default: str = "localhost", **kwargs: object) -> FieldInfo:
        """Create Oracle host field with validation.

        Args:
            default: Default host value
            **kwargs: Additional Pydantic field kwargs

        Returns:
            Configured Pydantic field for Oracle host addresses

        """
        description = cast(
            "str", kwargs.get("description", "Oracle database host address")
        )
        min_length = cast("int", kwargs.get("min_length", 1))
        max_length = cast(
            "int",
            kwargs.get(
                "max_length",
                FlextDbOracleConstants.OracleValidation.MAX_HOSTNAME_LENGTH,
            ),
        )
        return cast(
            "FieldInfo",
            Field(
                default=default,
                description=description,
                min_length=min_length,
                max_length=max_length,
            ),
        )

    @classmethod
    def port_field(cls, default: int = 1521, **kwargs: object) -> FieldInfo:
        """Create Oracle port field with validation.

        Args:
            default: Default port value (1521 for Oracle)
            **kwargs: Additional Pydantic field kwargs

        Returns:
            Configured Pydantic field for Oracle port numbers

        """
        description = cast(
            "str", kwargs.get("description", "Oracle database port number")
        )
        ge = cast("int", kwargs.get("ge", 1))
        le = cast("int", kwargs.get("le", 65535))
        return cast(
            "FieldInfo",
            Field(
                default=default,
                description=description,
                ge=ge,
                le=le,
            ),
        )

    @classmethod
    def username_field(cls, **kwargs: object) -> FieldInfo:
        """Create Oracle username field with validation.

        Args:
            **kwargs: Additional Pydantic field kwargs

        Returns:
            Configured Pydantic field for Oracle usernames

        """
        description = cast("str", kwargs.get("description", "Oracle database username"))
        min_length = cast("int", kwargs.get("min_length", 1))
        max_length = cast(
            "int",
            kwargs.get(
                "max_length",
                FlextDbOracleConstants.OracleValidation.MAX_USERNAME_LENGTH,
            ),
        )
        return cast(
            "FieldInfo",
            Field(
                description=description,
                min_length=min_length,
                max_length=max_length,
            ),
        )

    @classmethod
    def password_field(cls, **kwargs: object) -> FieldInfo:
        """Create Oracle password field with validation.

        Args:
            **kwargs: Additional Pydantic field kwargs

        Returns:
            Configured Pydantic field for Oracle passwords (SecretStr)

        """
        description = cast("str", kwargs.get("description", "Oracle database password"))
        min_length = cast("int", kwargs.get("min_length", 1))
        return cast(
            "FieldInfo",
            Field(
                description=description,
                min_length=min_length,
            ),
        )

    @classmethod
    def service_name_field(cls, **kwargs: object) -> FieldInfo:
        """Create Oracle service name field with validation.

        Args:
            **kwargs: Additional Pydantic field kwargs

        Returns:
            Configured Pydantic field for Oracle service names

        """
        description = cast(
            "str", kwargs.get("description", "Oracle database service name")
        )
        min_length = cast("int", kwargs.get("min_length", 1))
        max_length = cast(
            "int",
            kwargs.get(
                "max_length",
                FlextDbOracleConstants.OracleValidation.MAX_SERVICE_NAME_LENGTH,
            ),
        )
        return cast(
            "FieldInfo",
            Field(
                description=description,
                min_length=min_length,
                max_length=max_length,
            ),
        )

    class ColumnInfo(FlextModels.Value):
        """Oracle database column model with complete metadata."""

        column_name: str = Field(..., description="Column name")
        data_type: str = Field(..., description="Oracle data type")
        nullable: bool = Field(default=True, description="Column nullable flag")
        data_length: int | None = Field(
            default=None,
            description="Data length for character types",
        )
        data_precision: int | None = Field(
            default=None, description="Numeric precision"
        )
        data_scale: int | None = Field(default=None, description="Numeric scale")
        column_id: int = Field(..., description="Column position/ID")
        default_value: str | None = Field(default=None, description="Default value")
        comments: str | None = Field(default=None, description="Column comments")

        @property
        def full_type_spec(self) -> str:
            """Get complete type specification including precision/scale."""
            type_spec = self.data_type
            if self.data_precision is not None:
                if self.data_scale is not None:
                    type_spec += f"({self.data_precision},{self.data_scale})"
                else:
                    type_spec += f"({self.data_precision})"
            elif self.data_length is not None:
                type_spec += f"({self.data_length})"
            return type_spec

        @property
        def is_key_column(self) -> bool:
            """Check if this column is likely a primary key (heuristic)."""
            name_lower = self.column_name.lower()
            return (
                name_lower in {"id", "pk"}
                or name_lower.endswith(("_id", "_pk"))
                or (self.column_id == 1 and not self.nullable)
            )

        @field_validator("column_name")
        @classmethod
        def validate_column_name(cls, value: str) -> str:
            """Validate column name."""
            return OracleValidationFactory.validate_oracle_identifier(
                value,
                FlextDbOracleConstants.OracleValidation.MAX_COLUMN_NAME_LENGTH,
                allow_empty=False,
            )

        @field_validator("data_type")
        @classmethod
        def validate_data_type(cls, value: str) -> str:
            """Validate data type."""
            if not value or not value.strip():
                msg = "Data type cannot be empty"
                raise ValueError(msg)
            return value.upper()

        def validate_business_rules(self) -> FlextResult[None]:
            """Validate Oracle column-specific business rules."""
            try:
                # Column ID must be positive
                if self.column_id <= 0:
                    return FlextResult[None].fail("Column ID must be positive")

                # Numeric types should have precision/scale
                if (
                    self.data_type in {"NUMBER", "DECIMAL", "NUMERIC"}
                    and self.data_precision is None
                ):
                    return FlextResult[None].fail(
                        f"Numeric type {self.data_type} should have precision defined"
                    )

                return FlextResult[None].ok(None)
            except Exception as e:
                return FlextResult[None].fail(
                    f"Column business rule validation failed: {e}"
                )

        @field_validator("column_id")
        @classmethod
        def validate_column_id(cls, value: int) -> int:
            """Validate column ID."""
            if value <= 0:
                msg = "Column ID must be positive"
                raise ValueError(msg)
            return value

        @field_validator("data_length", "data_precision")
        @classmethod
        def validate_positive_or_none(cls, value: int | None) -> int | None:
            """Validate positive integer or None."""
            if value is not None and value <= 0:
                msg = "Value must be positive"
                raise ValueError(msg)
            return value

        @field_validator("data_scale")
        @classmethod
        def validate_non_negative_or_none(cls, value: int | None) -> int | None:
            """Validate non-negative integer or None for data_scale."""
            if value is not None and value < 0:
                msg = "Value must be non-negative"
                raise ValueError(msg)
            return value

        def is_numeric(self) -> bool:
            """Check if column is numeric type."""
            return self.data_type in {
                "NUMBER",
                "INTEGER",
                "FLOAT",
                "BINARY_DOUBLE",
                "BINARY_FLOAT",
            }

        def is_character(self) -> bool:
            """Check if column is character type."""
            return self.data_type in {
                "VARCHAR2",
                "CHAR",
                "NVARCHAR2",
                "NCHAR",
                "CLOB",
                "NCLOB",
            }

        def is_datetime(self) -> bool:
            """Check if column is date/time type."""
            return self.data_type in {
                "DATE",
                "TIMESTAMP",
                "TIMESTAMP WITH TIME ZONE",
                "TIMESTAMP WITH LOCAL TIME ZONE",
            }

        def to_oracle_ddl(self) -> str:
            """Generate Oracle DDL for column definition."""
            ddl_parts = [self.column_name, self.data_type]

            # Add length/precision for appropriate types
            if (
                self.data_type in {"VARCHAR2", "CHAR", "NVARCHAR2", "NCHAR"}
                and self.data_length
            ):
                ddl_parts[1] = f"{self.data_type}({self.data_length})"
            elif self.data_type == "NUMBER":
                if self.data_precision and self.data_scale is not None:
                    ddl_parts[1] = (
                        f"{self.data_type}({self.data_precision},{self.data_scale})"
                    )
                elif self.data_precision:
                    ddl_parts[1] = f"{self.data_type}({self.data_precision})"

            # Add NOT NULL constraint if applicable
            if not self.nullable:
                ddl_parts.append("NOT NULL")

            # Add default value if specified
            if self.default_value:
                ddl_parts.append(f"DEFAULT {self.default_value}")

            return " ".join(ddl_parts)

    class TableInfo(FlextModels.Value):
        """Oracle database table model with metadata and relationships."""

        table_name: str = Field(..., description="Table name")
        schema_name: str = Field(default="", description="Schema name")
        columns: list[FlextDbOracleModels.ColumnInfo] = Field(
            default_factory=list,
            description="Table columns",
        )
        row_count: int | None = Field(default=None, description="Approximate row count")
        last_analyzed: datetime | None = Field(
            default=None,
            description="Last statistics analysis date",
        )
        table_type: str = Field(
            default="TABLE",
            description="Table type (TABLE, VIEW, etc.)",
        )
        comments: str | None = Field(default=None, description="Table comments")

        @field_validator("table_name")
        @classmethod
        def validate_table_name(cls, value: str) -> str:
            """Validate table name."""
            return OracleValidationFactory.validate_oracle_identifier(
                value,
                FlextDbOracleConstants.OracleValidation.MAX_TABLE_NAME_LENGTH,
                allow_empty=False,
            )

        @field_validator("schema_name")
        @classmethod
        def validate_schema_name(cls, value: str) -> str:
            """Validate schema name."""
            if (
                value
                and len(value)
                > FlextDbOracleConstants.OracleValidation.MAX_SCHEMA_NAME_LENGTH
            ):
                msg = "Schema name exceeds maximum length"
                raise ValueError(msg)
            return value

        def get_full_name(self) -> str:
            """Get fully qualified table name."""
            if self.schema_name:
                return f"{self.schema_name}.{self.table_name}"
            return self.table_name

        def get_column_by_name(
            self, column_name: str
        ) -> FlextDbOracleModels.ColumnInfo | None:
            """Get column by name."""
            for column in self.columns:
                if column.column_name.upper() == column_name.upper():
                    return column
            return None

        def validate_business_rules(self) -> FlextResult[None]:
            """Validate Oracle table-specific business rules."""
            try:
                # Table must have at least one column if defined
                if not self.columns:
                    return FlextResult[None].fail("Table must have at least one column")

                # Row count should be non-negative
                if self.row_count is not None and self.row_count < 0:
                    return FlextResult[None].fail("Row count cannot be negative")

                return FlextResult[None].ok(None)
            except Exception as e:
                return FlextResult[None].fail(f"Table validation failed: {e}")

    class SchemaInfo(FlextModels.Entity):
        """Oracle database schema model with tables and metadata."""

        schema_name: str = Field(..., description="Schema name")
        tables: list[FlextDbOracleModels.TableInfo] = Field(
            default_factory=list,
            description="Tables in schema",
        )
        created_date: datetime | None = Field(
            default=None, description="Schema creation date"
        )
        default_tablespace: str | None = Field(
            default=None, description="Default tablespace"
        )
        temporary_tablespace: str | None = Field(
            default=None,
            description="Temporary tablespace",
        )
        profile: str | None = Field(default=None, description="User profile")
        account_status: str = Field(default="OPEN", description="Account status")

        @field_validator("schema_name")
        @classmethod
        def validate_schema_name(cls, value: str) -> str:
            """Validate schema name."""
            return OracleValidationFactory.validate_oracle_identifier(
                value,
                FlextDbOracleConstants.OracleValidation.MAX_SCHEMA_NAME_LENGTH,
                allow_empty=False,
            )

        def get_table_by_name(
            self, table_name: str
        ) -> FlextDbOracleModels.TableInfo | None:
            """Get table by name."""
            for table in self.tables:
                if table.table_name.upper() == table_name.upper():
                    return table
            return None

        def get_table_count(self) -> int:
            """Get count of tables in schema."""
            return len(self.tables)

    class QueryResult(FlextModels.Value):
        """Oracle query result model with execution metadata."""

        columns: FlextTypes.Core.StringList = Field(
            default_factory=list, description="Column names"
        )
        rows: list[FlextTypes.Core.List] = Field(
            default_factory=list,
            description="Result rows",
        )
        row_count: int = Field(default=0, description="Number of rows returned")
        execution_time_ms: float = Field(
            default=0.0,
            description="Query execution time in milliseconds",
        )
        query_hash: str | None = Field(None, description="Query hash for caching")
        explain_plan: str | None = Field(None, description="Query execution plan")

        @field_validator("row_count")
        @classmethod
        def validate_row_count(cls, value: int) -> int:
            """Validate row count."""
            if value < 0:
                msg = "Row count cannot be negative"
                raise ValueError(msg)
            return value

        @field_validator("execution_time_ms")
        @classmethod
        def validate_execution_time(cls, value: float) -> float:
            """Validate execution time."""
            if value < 0:
                msg = "Execution time cannot be negative"
                raise ValueError(msg)
            return value

        def to_dict_list(self) -> list[FlextTypes.Core.Dict]:
            """Convert result to list of dictionaries."""
            if not self.columns:
                return []

            result = []
            for row in self.rows:
                row_dict = {}
                for i, column in enumerate(self.columns):
                    row_dict[column] = row[i] if i < len(row) else None
                result.append(row_dict)
            return result

        def get_column_values(self, column_name: str) -> FlextTypes.Core.List:
            """Get all values for a specific column."""
            try:
                column_index = self.columns.index(column_name)
                return [
                    row[column_index] if column_index < len(row) else None
                    for row in self.rows
                ]
            except ValueError:
                return []

        def is_empty(self) -> bool:
            """Check if result is empty."""
            return self.row_count == 0

        def validate_business_rules(self) -> FlextResult[None]:
            """Validate Oracle query result business rules."""
            try:
                # Row count should match actual rows
                if len(self.rows) != self.row_count:
                    return FlextResult[None].fail("Row count mismatch with actual rows")

                # If we have rows, we should have columns
                if self.row_count > 0 and not self.columns:
                    return FlextResult[None].fail(
                        "Query result has rows but no column definitions"
                    )

                # All rows should have consistent structure with columns
                if self.columns:
                    for row_idx, row in enumerate(self.rows):
                        if len(row) > len(self.columns):
                            return FlextResult[None].fail(
                                f"Row {row_idx} has more values than columns",
                            )

                return FlextResult[None].ok(None)
            except Exception as e:
                return FlextResult[None].fail(f"Business rule validation failed: {e}")

    class ConnectionStatus(FlextModels.Value):
        """Oracle database connection status model."""

        is_connected: bool = Field(default=False, description="Connection status")
        connection_time: datetime | None = Field(
            None,
            description="Connection timestamp",
        )
        last_activity: datetime | None = Field(
            None,
            description="Last activity timestamp",
        )
        session_id: str | None = Field(None, description="Oracle session ID")
        host: str | None = Field(None, description="Database host")
        port: int | None = Field(None, description="Database port")
        service_name: str | None = Field(None, description="Oracle service name")
        username: str | None = Field(None, description="Database username")
        version: str | None = Field(None, description="Oracle database version")
        error_message: str | None = Field(None, description="Connection error message")

        def validate_business_rules(self) -> FlextResult[None]:
            """Validate Oracle connection-specific business rules."""
            try:
                # Connected status should have valid timestamps
                if self.is_connected:
                    if self.connection_time is None:
                        return FlextResult[None].fail(
                            "Connected status requires connection_time"
                        )
                    if self.last_activity is None:
                        return FlextResult[None].fail(
                            "Connected status requires last_activity"
                        )

                # Host and port should be set for active connections
                if self.is_connected and (not self.host or not self.port):
                    return FlextResult[None].fail(
                        "Connected status requires host and port"
                    )

                return FlextResult[None].ok(None)
            except Exception as e:
                return FlextResult[None].fail(
                    f"Connection status business rule validation failed: {e}"
                )

        @field_validator("port")
        @classmethod
        def validate_port(cls, value: int | None) -> int | None:
            """Validate port number."""
            if value is None:
                return 1521  # Oracle default port
            max_port = 65535
            if not 1 <= value <= max_port:
                msg = f"Port must be between 1 and 65535, got {value}"
                raise ValueError(msg)
            return value

        def get_connection_string_safe(self) -> str:
            """Get connection string without password."""
            if not all([self.host, self.port, self.service_name]):
                return "Connection details incomplete"
            return f"{self.username}@{self.host}:{self.port}/{self.service_name}"

        def get_uptime_seconds(self) -> float | None:
            """Get connection uptime in seconds."""
            if not self.connection_time:
                return None
            current_time = self.last_activity or datetime.now(UTC)
            uptime = current_time - self.connection_time
            return uptime.total_seconds()

        def is_active(self) -> bool:
            """Check if connection is active and healthy."""
            return self.is_connected and self.error_message is None

    class OracleConfig(BaseSettings):
        """Oracle database configuration extending flext-core centralized config."""

        # Core Oracle connection fields
        host: str = Field(description="Oracle database hostname")
        port: int = Field(default=1521, description="Oracle database port")
        username: str = Field(description="Oracle database username")
        password: SecretStr = Field(description="Oracle database password")
        service_name: str | None = Field(
            default=None,
            description="Oracle service name",
        )
        sid: str | None = Field(default=None, description="Oracle SID")
        oracle_schema: str = Field(default="PUBLIC", description="Oracle schema name")

        # Connection pool settings
        pool_min: int = Field(default=1, description="Minimum pool connections")
        pool_max: int = Field(default=10, description="Maximum pool connections")
        pool_increment: int = Field(default=1, description="Connection pool increment")

        # Additional Oracle-specific options
        ssl_enabled: bool = Field(default=False, description="Enable SSL connections")
        ssl_cert_path: str | None = Field(
            default=None,
            description="SSL certificate path",
        )
        ssl_key_path: str | None = Field(default=None, description="SSL key path")
        ssl_server_dn_match: bool = Field(
            default=True,
            description="SSL server DN match",
        )
        ssl_server_cert_dn: str | None = Field(
            default=None,
            description="SSL server certificate DN",
        )
        timeout: int = Field(default=30, description="Connection timeout seconds")
        encoding: str = Field(default="UTF-8", description="Character encoding")
        protocol: str = Field(default="tcp", description="Connection protocol")
        autocommit: bool = Field(default=False, description="Enable autocommit mode")
        retry_attempts: int = Field(
            default=1,
            description="Number of connection retry attempts",
        )
        retry_delay: float = Field(
            default=1.0,
            description="Delay between retry attempts in seconds",
        )

        # ------------------------------------------------------------------
        # Backward-compat / alias expectations (tests e outros pacotes)
        # Não adicionamos novos campos reais para evitar duplicação de estado;
        # em vez disso aceitamos nomes antigos via normalização pré-model e
        # expomos propriedades somente-leitura coerentes.
        # ------------------------------------------------------------------

        # BaseSettings configuration for automatic environment loading
        model_config = SettingsConfigDict(
            env_prefix="FLEXT_TARGET_ORACLE_",
            env_file=".env",
        )

        @model_validator(mode="before")
        @classmethod
        def _apply_aliases(cls, data: object) -> object:
            """Normaliza chaves de entrada aceitando aliases esperados.

            Aceita: schema -> oracle_schema, use_ssl -> ssl_enabled,
            pool_min_size -> pool_min, pool_max_size -> pool_max.
            Ignora pool_enabled (derivada) se fornecida.
            """
            if isinstance(data, dict):
                if "schema" in data and "oracle_schema" not in data:
                    data["oracle_schema"] = data["schema"]
                if "use_ssl" in data and "ssl_enabled" not in data:
                    data["ssl_enabled"] = data["use_ssl"]
                if "pool_min_size" in data and "pool_min" not in data:
                    data["pool_min"] = data["pool_min_size"]
                if "pool_max_size" in data and "pool_max" not in data:
                    data["pool_max"] = data["pool_max_size"]
            return data

        # ------------------------------------------------------------------
        # Propriedades derivadas (não armazenam valor extra)
        # ------------------------------------------------------------------
        @property
        def schema_name(self) -> str:
            """Get the Oracle schema name (compatibility property)."""
            return self.oracle_schema

        @property
        def use_ssl(self) -> bool:
            return self.ssl_enabled

        @property
        def pool_min_size(self) -> int:
            return self.pool_min

        @property
        def pool_max_size(self) -> int:
            return self.pool_max

        @property
        def pool_enabled(self) -> bool:
            """Considera pool habilitado se max > 1 ou min > 1."""
            return self.pool_max > 1 or self.pool_min > 1

        @field_validator("host", "username")
        @classmethod
        def validate_required_string(cls, value: str) -> str:
            """Validate required string fields."""
            if not value or not value.strip():
                msg = "Field cannot be empty"
                raise ValueError(msg)
            return value.strip()

        @field_validator("port")
        @classmethod
        def validate_port(cls, value: int) -> int:
            """Validate port number."""
            max_port = 65535
            if not 1 <= value <= max_port:
                msg = f"Port must be between 1 and 65535, got {value}"
                raise ValueError(msg)
            return value

        @field_validator("password", mode="before")
        @classmethod
        def coerce_password(cls, value: object) -> SecretStr:
            """Convert password to SecretStr."""
            if isinstance(value, SecretStr):
                return value
            if not value or not str(value).strip():
                msg = "Password cannot be empty"
                raise ValueError(msg)
            return SecretStr(str(value))

        @model_validator(mode="after")
        def validate_pool_settings(self) -> Self:
            """Validate pool configuration consistency."""
            if self.pool_max < self.pool_min:
                msg = "pool_max must be >= pool_min"
                raise ValueError(msg)
            return self

        @model_validator(mode="after")
        def validate_connection_identifiers(self) -> Self:
            """Validate that either SID or service_name is provided."""
            if not self.sid and not self.service_name:
                msg = "Either SID or service_name must be provided"
                raise ValueError(msg)
            return self

        @classmethod
        def from_env(cls, prefix: str = "FLEXT_TARGET_ORACLE") -> FlextResult[Self]:
            """Create configuration from environment variables."""
            try:
                config_data = {
                    "host": os.getenv(f"{prefix}_HOST", "localhost"),
                    "port": int(os.getenv(f"{prefix}_PORT", "1521")),
                    "username": os.getenv(f"{prefix}_USERNAME", "system"),
                    "password": SecretStr(os.getenv(f"{prefix}_PASSWORD", "oracle")),
                    "service_name": os.getenv(f"{prefix}_SERVICE_NAME", "XEPDB1"),
                    "ssl_server_cert_dn": os.getenv(f"{prefix}_SSL_CERT_DN"),
                }
                # Known Pydantic BaseSettings + MyPy incompatibility issue
                instance = cls(**config_data)
                return FlextResult[Self].ok(instance)
            except Exception as e:
                return FlextResult[Self].fail(
                    f"Failed to create config from environment: {e}"
                )

        @classmethod
        def from_url(cls, database_url: str) -> FlextResult[Self]:
            """Create configuration from database URL."""
            try:
                # Simple URL parsing for Oracle connections
                # Format: oracle://username:password@host:port/service_name
                if not database_url.startswith("oracle://"):
                    msg = "URL must start with 'oracle://'"
                    raise ValueError(msg)

                url_part = database_url[9:]  # Remove oracle://
                if "@" not in url_part:
                    msg = "Invalid URL format: missing credentials"
                    raise ValueError(msg)

                credentials, host_part = url_part.split("@", 1)
                username, password = credentials.split(":", 1)

                if "/" in host_part:
                    host_port, service_name = host_part.split("/", 1)
                else:
                    host_port = host_part
                    service_name = "XE"

                if ":" in host_port:
                    host, port_str = host_port.split(":", 1)
                    port = int(port_str)
                else:
                    host = host_port
                    port = 1521

                config_data = {
                    "host": host,
                    "port": port,
                    "username": username,
                    "password": SecretStr(password),
                    "service_name": service_name,
                }
                # Known Pydantic BaseSettings + MyPy incompatibility issue
                instance = cls(**config_data)
                return FlextResult[Self].ok(instance)
            except Exception as e:
                return FlextResult[Self].fail(f"Failed to parse database URL: {e}")

        def get_connection_string(self) -> str:
            """Get Oracle connection string for logging purposes."""
            if self.service_name:
                return f"{self.host}:{self.port}/{self.service_name}"
            if self.sid:
                return f"{self.host}:{self.port}:{self.sid}"
            return f"{self.host}:{self.port}"

        def build_sqlalchemy_url(self) -> str:
            """Build SQLAlchemy connection URL."""
            password_value = self.password.get_secret_value()
            if self.service_name:
                return f"oracle+oracledb://{self.username}:{password_value}@{self.host}:{self.port}/?service_name={self.service_name}"
            if self.sid:
                return f"oracle+oracledb://{self.username}:{password_value}@{self.host}:{self.port}/{self.sid}"
            msg = "Either service_name or sid must be provided"
            raise ValueError(msg)

    @dataclass
    class MergeStatement:
        """Configuration for Oracle MERGE statement generation."""

        target_table: str
        source_columns: FlextTypes.Core.StringList
        merge_keys: FlextTypes.Core.StringList
        update_columns: FlextTypes.Core.StringList | None = None
        insert_columns: FlextTypes.Core.StringList | None = None
        schema_name: str | None = None
        hints: FlextTypes.Core.StringList | None = None

    @dataclass
    class CreateIndex:
        """Configuration for Oracle CREATE INDEX statement generation."""

        index_name: str
        table_name: str
        columns: FlextTypes.Core.StringList
        unique: bool = False
        schema_name: str | None = None
        tablespace: str | None = None
        parallel: int | None = None

        def validate(self) -> FlextResult[None]:
            """Validate index configuration."""
            if not self.index_name or not self.index_name.strip():
                return FlextResult[None].fail("Index name cannot be empty")
            if not self.table_name or not self.table_name.strip():
                return FlextResult[None].fail("Table name cannot be empty")
            if not self.columns or len(self.columns) == 0:
                return FlextResult[None].fail("Index must have at least one column")
            for column in self.columns:
                if not column or not column.strip():
                    return FlextResult[None].fail("Column names cannot be empty")
            return FlextResult[None].ok(None)

    # Type definitions
    class OracleColumnInfo(TypedDict, total=False):
        """TypedDict for Oracle column information from database queries."""

        column_name: str
        data_type: str
        nullable: bool
        data_length: int | None
        data_precision: int | None
        data_scale: int | None
        column_id: int
        default_value: str | None
        comments: str | None

    class OracleConnectionInfo(TypedDict, total=False):
        """TypedDict for Oracle connection information."""

        host: str
        port: int
        service_name: str
        username: str
        password: str
        charset: str | None
        pool_min: int | None
        pool_max: int | None
        connect_timeout: int | None

    class OracleTableInfo(TypedDict, total=False):
        """TypedDict for Oracle table information from database queries."""

        table_name: str
        schema_name: str
        tablespace_name: str | None
        table_comment: str | None
        column_count: int | None
        row_count: int | None
        created_date: str | None
        last_analyzed: str | None

    # Type guards
    @staticmethod
    def is_plugin_like(obj: object) -> TypeGuard[object]:
        """Type guard to check if object has plugin-like attributes."""
        return (
            hasattr(obj, "name")
            and hasattr(obj, "version")
            and hasattr(obj, "get_info")
            and callable(getattr(obj, "get_info", None))
        )

    @staticmethod
    def is_dict_like(obj: object) -> TypeGuard[FlextTypes.Core.Dict]:
        """Type guard for dict-like objects."""
        return hasattr(obj, "get") and hasattr(obj, "items") and hasattr(obj, "keys")

    @staticmethod
    def is_string_list(obj: object) -> TypeGuard[FlextTypes.Core.StringList]:
        """Type guard for list of strings."""
        return isinstance(obj, list) and all(isinstance(item, str) for item in obj)


# Compatibility aliases for backward compatibility
Column = FlextDbOracleModels.ColumnInfo
Table = FlextDbOracleModels.TableInfo
Schema = FlextDbOracleModels.SchemaInfo
QueryResult = FlextDbOracleModels.QueryResult
ConnectionStatus = FlextDbOracleModels.ConnectionStatus
OracleConfig = FlextDbOracleModels.OracleConfig
CreateIndexConfig = FlextDbOracleModels.CreateIndex
MergeStatementConfig = FlextDbOracleModels.MergeStatement


__all__ = [
    "Column",
    "ConnectionStatus",
    "CreateIndexConfig",
    "FlextDbOracleModels",
    "MergeStatementConfig",
    "OracleConfig",
    "QueryResult",
    "Schema",
    "Table",
]
