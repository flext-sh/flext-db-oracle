"""Test configuration for flext-db-oracle.

Provides pytest fixtures and configuration for testing Oracle database functionality
using real Oracle connections and flext-core patterns.
"""

from __future__ import annotations

import math
import os
from typing import TYPE_CHECKING, Any

import pytest

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator, Generator


# Test environment setup
@pytest.fixture(autouse=True)
def set_test_environment() -> Generator[None]:
    """Set test environment variables."""
    os.environ["FLEXT_ENV"] = "test"
    os.environ["FLEXT_LOG_LEVEL"] = "debug"
    os.environ["ORACLE_TEST_MODE"] = "true"
    yield
    # Cleanup
    os.environ.pop("FLEXT_ENV", None)
    os.environ.pop("FLEXT_LOG_LEVEL", None)
    os.environ.pop("ORACLE_TEST_MODE", None)


# Oracle connection fixtures
@pytest.fixture
def oracle_connection_config() -> dict[str, Any]:
    """Oracle database connection configuration for testing."""
    return {
        "host": "localhost",
        "port": 1521,
        "sid": "XEPDB1",
        "service_name": "XEPDB1",
        "username": "test_user",
        "password": "test_pass",
        "encoding": "UTF-8",
        "thick_mode": False,
        "pool_min": 1,
        "pool_max": 10,
        "pool_increment": 1,
    }


@pytest.fixture
async def oracle_connection(
    oracle_connection_config: dict[str, Any],
) -> AsyncGenerator[Any]:
    """Oracle database connection for testing."""
    from flext_db_oracle.application.services import OracleConnectionService
    from flext_db_oracle.config import OracleConfig

    config = OracleConfig(**oracle_connection_config)
    return OracleConnectionService(config)
    # Mock connection initialization for testing


@pytest.fixture
async def oracle_pool(oracle_connection_config: dict[str, Any]) -> AsyncGenerator[Any]:
    """Oracle connection pool for testing."""
    from flext_db_oracle.application.services import OracleConnectionService
    from flext_db_oracle.config import OracleConfig

    config = OracleConfig(**oracle_connection_config)
    return OracleConnectionService(config)
    # Mock pool for testing


# Schema fixtures
@pytest.fixture
def oracle_schema_config() -> dict[str, Any]:
    """Oracle schema configuration for testing."""
    return {
        "schema_name": "TEST_SCHEMA",
        "tables": [
            {
                "name": "EMPLOYEES",
                "columns": [
                    {"name": "ID", "type": "NUMBER", "primary_key": True},
                    {"name": "NAME", "type": "VARCHAR2(100)", "nullable": False},
                    {"name": "EMAIL", "type": "VARCHAR2(255)", "nullable": True},
                    {"name": "DEPARTMENT_ID", "type": "NUMBER", "nullable": True},
                    {
                        "name": "CREATED_AT",
                        "type": "TIMESTAMP",
                        "default": "CURRENT_TIMESTAMP",
                    },
                ],
                "indexes": [
                    {
                        "name": "IDX_EMPLOYEES_EMAIL",
                        "columns": ["EMAIL"],
                        "unique": True,
                    },
                    {"name": "IDX_EMPLOYEES_DEPT", "columns": ["DEPARTMENT_ID"]},
                ],
            },
            {
                "name": "DEPARTMENTS",
                "columns": [
                    {"name": "ID", "type": "NUMBER", "primary_key": True},
                    {"name": "NAME", "type": "VARCHAR2(100)", "nullable": False},
                    {"name": "MANAGER_ID", "type": "NUMBER", "nullable": True},
                ],
            },
        ],
        "sequences": [
            {"name": "SEQ_EMPLOYEES", "start": 1, "increment": 1},
            {"name": "SEQ_DEPARTMENTS", "start": 1, "increment": 1},
        ],
    }


# Sample data fixtures
@pytest.fixture
def sample_employee_data() -> list[dict[str, Any]]:
    """Sample employee data for testing."""
    return [
        {
            "id": 1,
            "name": "John Doe",
            "email": "john.doe@example.com",
            "department_id": 1,
        },
        {
            "id": 2,
            "name": "Jane Smith",
            "email": "jane.smith@example.com",
            "department_id": 2,
        },
        {
            "id": 3,
            "name": "Bob Johnson",
            "email": "bob.johnson@example.com",
            "department_id": 1,
        },
    ]


@pytest.fixture
def sample_department_data() -> list[dict[str, Any]]:
    """Sample department data for testing."""
    return [
        {"id": 1, "name": "Engineering", "manager_id": 1},
        {"id": 2, "name": "Marketing", "manager_id": 2},
        {"id": 3, "name": "Sales", "manager_id": None},
    ]


# Query fixtures
@pytest.fixture
def oracle_queries() -> dict[str, str]:
    """Oracle SQL queries for testing."""
    return {
        "select_employees": """
            SELECT id, name, email, department_id, created_at
            FROM employees
            ORDER BY id
        """,
        "select_employee_by_id": """
            SELECT id, name, email, department_id, created_at
            FROM employees
            WHERE id = :employee_id
        """,
        "insert_employee": """
            INSERT INTO employees (id, name, email, department_id)
            VALUES (seq_employees.nextval, :name, :email, :department_id)
        """,
        "update_employee": """
            UPDATE employees
            SET name = :name, email = :email, department_id = :department_id
            WHERE id = :employee_id
        """,
        "delete_employee": """
            DELETE FROM employees
            WHERE id = :employee_id
        """,
        "select_with_join": """
            SELECT e.id, e.name, e.email, d.name as department_name
            FROM employees e
            LEFT JOIN departments d ON e.department_id = d.id
            ORDER BY e.id
        """,
    }


# Transaction fixtures
@pytest.fixture
def transaction_test_data() -> dict[str, Any]:
    """Test data for transaction testing."""
    return {
        "employees": [
            {"name": "Alice Johnson", "email": "alice@example.com", "department_id": 1},
            {"name": "Bob Smith", "email": "bob@example.com", "department_id": 2},
        ],
        "departments": [
            {"name": "Research", "manager_id": None},
            {"name": "Development", "manager_id": None},
        ],
    }


# Performance testing fixtures
@pytest.fixture
def performance_test_config() -> dict[str, Any]:
    """Configuration for performance testing."""
    return {
        "batch_size": 1000,
        "concurrent_connections": 5,
        "test_duration_seconds": 30,
        "query_iterations": 10000,
        "insert_batch_size": 100,
    }


@pytest.fixture
def large_dataset_config() -> dict[str, Any]:
    """Configuration for large dataset testing."""
    return {
        "record_count": 10000,
        "batch_size": 1000,
        "parallel_workers": 4,
        "memory_limit_mb": 512,
    }


# Error testing fixtures
@pytest.fixture
def oracle_error_scenarios() -> list[dict[str, Any]]:
    """Oracle error scenarios for testing."""
    return [
        {
            "name": "invalid_sql",
            "query": "SELECT * FROM non_existent_table",
            "expected_error": "ORA-00942",
            "error_type": "TableNotFoundError",
        },
        {
            "name": "constraint_violation",
            "query": "INSERT INTO employees (id, name) VALUES (1, NULL)",
            "expected_error": "ORA-01400",
            "error_type": "ConstraintViolationError",
        },
        {
            "name": "invalid_datatype",
            "query": "INSERT INTO employees (id, name) VALUES ('invalid', 'test')",
            "expected_error": "ORA-01722",
            "error_type": "InvalidDataTypeError",
        },
        {
            "name": "connection_timeout",
            "config": {"connect_timeout": 0.001},
            "expected_error": "DPI-1080",
            "error_type": "ConnectionTimeoutError",
        },
    ]


# Data type testing fixtures
@pytest.fixture
def oracle_data_types() -> dict[str, Any]:
    """Oracle data type testing configurations."""
    return {
        "numeric_types": {
            "NUMBER": [1, 1.5, 999999999999],
            "INTEGER": [1, 100, -50],
            "FLOAT": [1.1, math.pi, -math.e],
        },
        "string_types": {
            "VARCHAR2": ["test", "longer test string", ""],
            "CHAR": ["A", "FIXED", "12345"],
            "CLOB": ["small text", "x" * 4000, "unicode: éñ中文"],
        },
        "date_types": {
            "DATE": ["2023-01-01", "2023-12-31"],
            "TIMESTAMP": ["2023-01-01 12:00:00", "2023-12-31 23:59:59.999"],
        },
        "binary_types": {
            "RAW": [b"binary data", b"\x00\x01\x02\x03"],
            "BLOB": [b"small blob", b"x" * 4000],
        },
    }


# Pagination fixtures
@pytest.fixture
def pagination_test_config() -> dict[str, Any]:
    """Configuration for pagination testing."""
    return {
        "total_records": 1000,
        "page_sizes": [10, 25, 50, 100],
        "ordering_columns": ["id", "name", "created_at"],
        "filter_conditions": [
            {"column": "department_id", "operator": "=", "value": 1},
            {"column": "name", "operator": "LIKE", "value": "%John%"},
            {"column": "created_at", "operator": ">", "value": "2023-01-01"},
        ],
    }


# Pytest markers for test categorization
def pytest_configure(config: pytest.Config) -> None:
    """Configure pytest markers."""
    config.addinivalue_line("markers", "unit: Unit tests")
    config.addinivalue_line("markers", "integration: Integration tests")
    config.addinivalue_line("markers", "e2e: End-to-end tests")
    config.addinivalue_line("markers", "oracle: Oracle database tests")
    config.addinivalue_line("markers", "connection: Connection management tests")
    config.addinivalue_line("markers", "transaction: Transaction tests")
    config.addinivalue_line("markers", "performance: Performance tests")
    config.addinivalue_line("markers", "schema: Schema management tests")
    config.addinivalue_line("markers", "slow: Slow tests")


# Mock services
@pytest.fixture
def mock_oracle_service() -> Any:
    """Mock Oracle service for testing."""

    class MockOracleService:
        def __init__(self) -> None:
            self.connected = False
            self.transactions: list[dict[str, Any]] = []
            self.queries_executed: list[dict[str, Any]] = []

        async def connect(self) -> bool:
            self.connected = True
            return True

        async def disconnect(self) -> bool:
            self.connected = False
            return True

        async def execute_query(
            self,
            query: str,
            params: dict[str, Any] | None = None,
        ) -> list[dict[str, Any]]:
            self.queries_executed.append({"query": query, "params": params})
            return [{"id": 1, "name": "test"}]

        async def execute_non_query(
            self,
            query: str,
            params: dict[str, Any] | None = None,
        ) -> int:
            self.queries_executed.append({"query": query, "params": params})
            return 1

        async def begin_transaction(self) -> str:
            transaction_id = f"txn_{len(self.transactions) + 1}"
            self.transactions.append({"id": transaction_id, "status": "active"})
            return transaction_id

        async def commit_transaction(self, transaction_id: str) -> None:
            for txn in self.transactions:
                if txn["id"] == transaction_id:
                    txn["status"] = "committed"

        async def rollback_transaction(self, transaction_id: str) -> None:
            for txn in self.transactions:
                if txn["id"] == transaction_id:
                    txn["status"] = "rolled_back"

    return MockOracleService()


@pytest.fixture
def mock_oracle_pool() -> Any:
    """Mock Oracle connection pool for testing."""

    class MockOraclePool:
        def __init__(self, config: dict[str, Any]) -> None:
            self.config = config
            self.pool_size = 0
            self.active_connections = 0

        async def create_pool(self) -> None:
            self.pool_size = self.config.get("pool_max", 10)

        async def close_pool(self) -> None:
            self.pool_size = 0
            self.active_connections = 0

        async def acquire_connection(self) -> str:
            if self.active_connections < self.pool_size:
                self.active_connections += 1
                return f"connection_{self.active_connections}"
            msg = "Pool exhausted"
            raise RuntimeError(msg)

        async def release_connection(self, connection: Any) -> None:
            self.active_connections -= 1

    return MockOraclePool
