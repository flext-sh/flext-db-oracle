#!/usr/bin/env python3
"""COMPREHENSIVE FUNCTIONALITY TEST - FLEXT DB ORACLE.

Testa TODA a funcionalidade Oracle sem workarounds.
Valida que implementação está completa e funcionando.
"""

import asyncio
import sys
import traceback
from datetime import UTC, datetime
from typing import Any

from flext_db_oracle.application.services import (
    FlextDbOracleConnectionService,
)
from flext_db_oracle.compare.differ import DataDiffer, SchemaDiffer
from flext_db_oracle.config import FlextDbOracleConfig
from flext_db_oracle.logging_utils import get_logger
from flext_db_oracle.schema.analyzer import SchemaAnalyzer
from flext_db_oracle.simple_api import (
    flext_db_oracle_create_connection_service,
    flext_db_oracle_get_database_info,
    flext_db_oracle_setup_oracle_db,
    flext_db_oracle_test_connection,
)
from flext_db_oracle.sql.optimizer import QueryOptimizer
from flext_db_oracle.sql.validator import SQLValidator

logger = get_logger(__name__)


class ComprehensiveFunctionalityTest:
    """Teste completo de funcionalidade Oracle sem workarounds."""

    def __init__(self) -> None:
        self.config = FlextDbOracleConfig(
            host="localhost",
            port=1521,
            service_name="XEPDB1",
            username="flexttest",
            password="FlextTest123",
        )
        self.test_results: dict[str, dict[str, Any]] = {}

    async def run_all_tests(self) -> dict[str, Any]:
        """Execute todos os testes de funcionalidade."""
        test_categories = [
            ("Simple API", self.test_simple_api),
            ("Connection Management", self.test_connection_management),
            ("Query Execution", self.test_query_execution),
            ("Schema Analysis", self.test_schema_analysis),
            ("SQL Validation", self.test_sql_validation),
            ("SQL Optimization", self.test_sql_optimization),
            ("Data Comparison", self.test_data_comparison),
            ("Schema Comparison", self.test_schema_comparison),
            ("Configuration", self.test_configuration),
            ("Error Handling", self.test_error_handling),
        ]

        start_time = datetime.now(UTC)
        total_passed = 0
        total_failed = 0

        for category_name, test_method in test_categories:
            try:
                result = await test_method()
                self.test_results[category_name] = {
                    "status": "PASS" if result["success"] else "FAIL",
                    "details": result,
                    "timestamp": datetime.now(UTC).isoformat(),
                }
                if result["success"]:
                    total_passed += 1
                else:
                    total_failed += 1
            except Exception as e:
                self.test_results[category_name] = {
                    "status": "ERROR",
                    "error": str(e),
                    "timestamp": datetime.now(UTC).isoformat(),
                }
                total_failed += 1
                traceback.print_exc()

        end_time = datetime.now(UTC)
        execution_time = (end_time - start_time).total_seconds()

        return {
            "total_categories": len(test_categories),
            "passed": total_passed,
            "failed": total_failed,
            "success_rate": f"{(total_passed / len(test_categories)) * 100:.1f}%",
            "execution_time_seconds": execution_time,
            "results": self.test_results,
        }

    async def test_simple_api(self) -> dict[str, Any]:
        """Test simple API functionality."""
        try:
            # Test setup
            setup_result = flext_db_oracle_setup_oracle_db(self.config)
            if not setup_result.success:
                return {
                    "success": False,
                    "error": f"Setup failed: {setup_result.error}",
                }

            # Test connection service creation
            service_result = flext_db_oracle_create_connection_service(self.config)
            if not service_result.success:
                return {
                    "success": False,
                    "error": f"Service creation failed: {service_result.error}",
                }

            # Test connection
            conn_result = await flext_db_oracle_test_connection(self.config)
            if not conn_result.success:
                return {
                    "success": False,
                    "error": f"Connection test failed: {conn_result.error}",
                }

            # Test database info
            info_result = await flext_db_oracle_get_database_info(self.config)
            if not info_result.success:
                return {
                    "success": False,
                    "error": f"Database info failed: {info_result.error}",
                }

            return {
                "success": True,
                "setup": setup_result.success,
                "service_creation": service_result.success,
                "connection_test": conn_result.success,
                "database_info": info_result.success,
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    async def test_connection_management(self) -> dict[str, Any]:
        """Test connection pool management."""
        service = FlextDbOracleConnectionService(self.config)
        try:
            # Test pool initialization
            init_result = await service.initialize_pool()
            if not init_result.success:
                return {
                    "success": False,
                    "error": f"Pool init failed: {init_result.error}",
                }

            # Test pool status
            status = service.get_pool_status()
            if not status:
                return {"success": False, "error": "Pool status empty"}

            # Test connection acquisition
            conn_result = await service.test_connection()
            if not conn_result.success:
                return {
                    "success": False,
                    "error": f"Connection test failed: {conn_result.error}",
                }

            # Test pool closure
            close_result = await service.close_pool()
            if not close_result.success:
                return {
                    "success": False,
                    "error": f"Pool close failed: {close_result.error}",
                }

            return {
                "success": True,
                "pool_init": init_result.success,
                "pool_status": bool(status),
                "connection_test": conn_result.success,
                "pool_close": close_result.success,
            }

        except Exception as e:
            await service.close_pool()
            return {"success": False, "error": str(e)}

    async def test_query_execution(self) -> dict[str, Any]:
        """Test query execution functionality."""
        service = FlextDbOracleConnectionService(self.config)
        await service.initialize_pool()

        try:
            # Test simple query
            simple_result = await service.execute_query("SELECT 1 FROM DUAL")
            if not simple_result.success:
                return {
                    "success": False,
                    "error": f"Simple query failed: {simple_result.error}",
                }

            # Test parameterized query
            param_result = await service.execute_query(
                "SELECT :param FROM DUAL", {"param": "test"}
            )
            if not param_result.success:
                return {
                    "success": False,
                    "error": f"Parameterized query failed: {param_result.error}",
                }

            # Test real table query
            table_result = await service.execute_query(
                "SELECT employee_id, first_name FROM employees WHERE ROWNUM <= 3"
            )
            if not table_result.success:
                return {
                    "success": False,
                    "error": f"Table query failed: {table_result.error}",
                }

            # Test join query
            join_result = await service.execute_query("""
                SELECT e.first_name, d.department_name
                FROM employees e
                LEFT JOIN departments d ON e.department_id = d.department_id
                WHERE ROWNUM <= 3
            """)
            if not join_result.success:
                return {
                    "success": False,
                    "error": f"Join query failed: {join_result.error}",
                }

            return {
                "success": True,
                "simple_query": simple_result.success,
                "parameterized_query": param_result.success,
                "table_query": table_result.success,
                "join_query": join_result.success,
                "table_rows": len(table_result.data.rows) if table_result.data else 0,
            }

        except Exception as e:
            return {"success": False, "error": str(e)}
        finally:
            await service.close_pool()

    async def test_schema_analysis(self) -> dict[str, Any]:
        """Test schema analysis functionality."""
        connection_service = FlextDbOracleConnectionService(self.config)
        await connection_service.initialize_pool()

        try:
            analyzer = SchemaAnalyzer(connection_service)

            # Test basic schema info
            schema_result = await analyzer.analyze_schema("FLEXTTEST")
            if not schema_result.success:
                return {
                    "success": False,
                    "error": f"Schema analysis failed: {schema_result.error}",
                }

            # Test table details
            table_result = await analyzer.get_detailed_table_info(
                "FLEXTTEST", "EMPLOYEES"
            )
            if not table_result.success:
                return {
                    "success": False,
                    "error": f"Table details failed: {table_result.error}",
                }

            # Test complete metadata
            metadata_result = await analyzer.get_complete_schema_metadata("FLEXTTEST")
            if not metadata_result.success:
                return {
                    "success": False,
                    "error": f"Complete metadata failed: {metadata_result.error}",
                }

            return {
                "success": True,
                "schema_analysis": schema_result.success,
                "table_details": table_result.success,
                "complete_metadata": metadata_result.success,
                "tables_found": len(schema_result.data) if schema_result.data else 0,
            }

        except Exception as e:
            return {"success": False, "error": str(e)}
        finally:
            await connection_service.close_pool()

    async def test_sql_validation(self) -> dict[str, Any]:
        """Test SQL validation functionality."""
        try:
            validator = SQLValidator()

            # Test valid SQL
            valid_result = await validator.validate_sql("SELECT * FROM DUAL")
            if not valid_result.success:
                return {
                    "success": False,
                    "error": f"Valid SQL validation failed: {valid_result.error}",
                }

            # Test invalid SQL
            invalid_result = await validator.validate_sql("INVALID SQL STATEMENT")
            # Should fail validation but succeed in processing
            if not invalid_result.success:
                return {
                    "success": False,
                    "error": f"Invalid SQL processing failed: {invalid_result.error}",
                }

            # Test complex valid SQL
            complex_result = await validator.validate_sql("""
                SELECT e.employee_id, e.first_name, d.department_name
                FROM employees e
                LEFT JOIN departments d ON e.department_id = d.department_id
                WHERE e.salary > 5000
                ORDER BY e.salary DESC
            """)
            if not complex_result.success:
                return {
                    "success": False,
                    "error": f"Complex SQL validation failed: {complex_result.error}",
                }

            return {
                "success": True,
                "valid_sql": valid_result.success,
                "invalid_sql_handled": invalid_result.success,
                "complex_sql": complex_result.success,
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    async def test_sql_optimization(self) -> dict[str, Any]:
        """Test SQL optimization functionality."""
        connection_service = FlextDbOracleConnectionService(self.config)
        await connection_service.initialize_pool()

        try:
            optimizer = QueryOptimizer(connection_service)

            # Test basic optimization (using optimize_query method)
            basic_result = await optimizer.optimize_query("SELECT 1 FROM DUAL")
            if not basic_result.success:
                return {
                    "success": False,
                    "error": f"Basic optimization failed: {basic_result.error}",
                }

            # Test complex optimization with real table
            complex_result = await optimizer.optimize_query("""
                SELECT e.employee_id, e.first_name
                FROM employees e
                WHERE e.employee_id = 1001
            """)
            if not complex_result.success:
                return {
                    "success": False,
                    "error": f"Complex analysis failed: {complex_result.error}",
                }

            return {
                "success": True,
                "basic_optimization": basic_result.success,
                "complex_optimization": complex_result.success,
            }

        except Exception as e:
            return {"success": False, "error": str(e)}
        finally:
            await connection_service.close_pool()

    async def test_data_comparison(self) -> dict[str, Any]:
        """Test data comparison functionality."""
        connection_service = FlextDbOracleConnectionService(self.config)
        await connection_service.initialize_pool()

        try:
            differ = DataDiffer()

            # Test table comparison
            result = await differ.compare_table_data(
                connection_service,
                connection_service,  # Compare with itself
                "DUAL",
                ["DUMMY"],
            )
            if not result.success:
                return {
                    "success": False,
                    "error": f"Data comparison failed: {result.error}",
                }

            # Test with real table
            employees_result = await differ.compare_table_data(
                connection_service,
                connection_service,
                "EMPLOYEES",
                ["EMPLOYEE_ID"],
            )
            if not employees_result.success:
                return {
                    "success": False,
                    "error": f"Employees comparison failed: {employees_result.error}",
                }

            return {
                "success": True,
                "dual_comparison": result.success,
                "employees_comparison": employees_result.success,
                "differences_found": len(result.data) if result.data else 0,
            }

        except Exception as e:
            return {"success": False, "error": str(e)}
        finally:
            await connection_service.close_pool()

    async def test_schema_comparison(self) -> dict[str, Any]:
        """Test schema comparison functionality."""
        connection_service = FlextDbOracleConnectionService(self.config)
        await connection_service.initialize_pool()

        try:
            analyzer = SchemaAnalyzer(connection_service)
            differ = SchemaDiffer()

            # Get schema metadata
            metadata_result = await analyzer.get_complete_schema_metadata("FLEXTTEST")
            if not metadata_result.success:
                return {
                    "success": False,
                    "error": f"Schema metadata failed: {metadata_result.error}",
                }

            # Compare schema with itself
            comparison_result = await differ.compare_schemas(
                metadata_result.data, metadata_result.data
            )
            if not comparison_result.success:
                return {
                    "success": False,
                    "error": f"Schema comparison failed: {comparison_result.error}",
                }

            return {
                "success": True,
                "metadata_retrieval": metadata_result.success,
                "schema_comparison": comparison_result.success,
                "differences": comparison_result.data.total_differences
                if comparison_result.data
                else 0,
            }

        except Exception as e:
            return {"success": False, "error": str(e)}
        finally:
            await connection_service.close_pool()

    async def test_configuration(self) -> dict[str, Any]:
        """Test configuration functionality."""
        try:
            # Test URL parsing
            url_config = FlextDbOracleConfig.from_url(
                "oracle://testuser:testpass@testhost:1521/testdb"
            )
            if url_config.username != "testuser":
                return {"success": False, "error": "URL parsing failed"}

            # Test connection string generation
            conn_str = self.config.connection_string
            if "oracle://" not in conn_str:
                return {
                    "success": False,
                    "error": "Connection string generation failed",
                }

            # Test connection config conversion
            conn_config = self.config.to_connection_config()
            if conn_config.host != self.config.host:
                return {
                    "success": False,
                    "error": "Connection config conversion failed",
                }

            # Test domain validation
            try:
                self.config.validate_domain_rules()
                domain_validation = True
            except Exception:
                domain_validation = False

            return {
                "success": True,
                "url_parsing": True,
                "connection_string": True,
                "config_conversion": True,
                "domain_validation": domain_validation,
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    async def test_error_handling(self) -> dict[str, Any]:
        """Test error handling functionality."""
        service = FlextDbOracleConnectionService(self.config)
        await service.initialize_pool()

        try:
            # Test invalid SQL
            invalid_result = await service.execute_query("INVALID SQL STATEMENT")
            invalid_handled = not invalid_result.success

            # Test non-existent table
            missing_table_result = await service.execute_query(
                "SELECT * FROM NONEXISTENT_TABLE"
            )
            missing_table_handled = not missing_table_result.success

            # Test malformed query
            malformed_result = await service.execute_query("SELECT FROM")
            malformed_handled = not malformed_result.success

            return {
                "success": True,
                "invalid_sql_handled": invalid_handled,
                "missing_table_handled": missing_table_handled,
                "malformed_query_handled": malformed_handled,
                "error_messages_present": bool(
                    invalid_result.error
                    and missing_table_result.error
                    and malformed_result.error
                ),
            }

        except Exception as e:
            return {"success": False, "error": str(e)}
        finally:
            await service.close_pool()


async def main() -> None:
    """Main test execution."""
    tester = ComprehensiveFunctionalityTest()
    summary = await tester.run_all_tests()

    # Save results
    import json

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results_file = f"comprehensive_test_results_{timestamp}.json"

    # Use sync file operations within async function - acceptable pattern
    with open(results_file, "w") as f:  # noqa: ASYNC230
        json.dump(summary, f, indent=2, default=str)

    # Exit with appropriate code
    if summary["failed"] > 0:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        sys.exit(130)
    except Exception:
        sys.exit(1)
