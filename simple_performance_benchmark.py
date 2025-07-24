#!/usr/bin/env python3
"""SIMPLIFIED PERFORMANCE BENCHMARK - FLEXT DB ORACLE.

Real Oracle performance testing focusing on core functionality.
Avoids Oracle version compatibility issues while testing real performance.

Usage:
    ORACLE_USERNAME=flexttest ORACLE_PASSWORD=FlextTest123 python simple_performance_benchmark.py
"""

import asyncio
import gc
import json
import subprocess
import sys
import time
import traceback
import tracemalloc
from contextlib import asynccontextmanager
from datetime import UTC, datetime
from statistics import mean, median
from typing import Any, AsyncIterator

from flext_db_oracle.application.services import FlextDbOracleConnectionService
from flext_db_oracle.config import FlextDbOracleConfig
from flext_db_oracle.logging_utils import get_logger

logger = get_logger(__name__)


class SimplifiedPerformanceBenchmark:
    """Simplified performance benchmark for Oracle database operations."""

    def __init__(self) -> None:
        self.config = FlextDbOracleConfig(
            host="localhost",
            port=1521,
            service_name="XEPDB1",
            username="flexttest",
            password="FlextTest123",
            pool_min_size=2,
            pool_max_size=10,
            pool_increment=2,
        )
        self.results: dict[str, Any] = {}

    @asynccontextmanager
    async def measure_performance(self, test_name: str) -> AsyncIterator[None]:
        """Context manager to measure performance metrics."""
        tracemalloc.start()
        gc.collect()

        start_time = time.perf_counter()
        start_memory = tracemalloc.get_traced_memory()[0]

        try:
            yield
        finally:
            end_time = time.perf_counter()
            end_memory = tracemalloc.get_traced_memory()[0]
            peak_memory = tracemalloc.get_traced_memory()[1]

            execution_time = end_time - start_time
            memory_used = end_memory - start_memory

            self.results[test_name] = {
                "execution_time_seconds": execution_time,
                "memory_used_bytes": memory_used,
                "peak_memory_bytes": peak_memory,
                "timestamp": datetime.now(UTC).isoformat(),
            }

            tracemalloc.stop()

    async def benchmark_connection_performance(self) -> None:
        """Benchmark connection-related performance."""
        service = FlextDbOracleConnectionService(self.config)

        # Test 1: Pool initialization
        async with self.measure_performance("connection_pool_init"):
            result = await service.initialize_pool()
            assert result.success, f"Pool init failed: {result.error}"

        # Test 2: Single connection test
        async with self.measure_performance("single_connection_test"):
            result = await service.test_connection()
            assert result.success, f"Connection test failed: {result.error}"

        # Test 3: Multiple sequential connections
        async with self.measure_performance("sequential_connections"):
            for _ in range(10):
                result = await service.test_connection()
                assert result.success

        # Test 4: Concurrent connections
        async with self.measure_performance("concurrent_connections"):

            async def test_connection():
                return await service.test_connection()

            tasks = [test_connection() for _ in range(20)]
            results = await asyncio.gather(*tasks)
            successful = sum(1 for r in results if r.success)
            assert successful == 20

        await service.close_pool()

    async def benchmark_query_performance(self) -> None:
        """Benchmark query execution performance."""
        service = FlextDbOracleConnectionService(self.config)
        await service.initialize_pool()

        try:
            # Test 1: Simple queries
            async with self.measure_performance("simple_queries_x1000"):
                for _ in range(1000):
                    result = await service.execute_query("SELECT 1 FROM DUAL")
                    assert result.success

            # Test 2: Parameterized queries
            async with self.measure_performance("parameterized_queries_x100"):
                for i in range(100):
                    result = await service.execute_query(
                        "SELECT :param FROM DUAL", {"param": i}
                    )
                    assert result.success

            # Test 3: Real table queries with our test data
            async with self.measure_performance("real_table_queries_x100"):
                for _ in range(100):
                    result = await service.execute_query(
                        "SELECT employee_id, first_name, last_name FROM employees"
                    )
                    assert result.success

            # Test 4: Join queries with test data
            async with self.measure_performance("join_queries_x50"):
                for _ in range(50):
                    result = await service.execute_query("""
                        SELECT e.first_name, e.last_name, d.department_name
                        FROM employees e
                        LEFT JOIN departments d ON e.department_id = d.department_id
                    """)
                    assert result.success

        finally:
            await service.close_pool()

    async def benchmark_memory_usage(self) -> None:
        """Benchmark memory usage patterns."""
        service = FlextDbOracleConnectionService(self.config)
        await service.initialize_pool()

        try:
            # Test 1: Memory usage with small queries
            async with self.measure_performance("memory_small_queries"):
                results = []
                for i in range(500):
                    result = await service.execute_query(
                        "SELECT :param FROM DUAL", {"param": i}
                    )
                    results.append(result)
                    if i % 100 == 0:
                        gc.collect()

            # Test 2: Memory usage with larger result sets
            async with self.measure_performance("memory_table_scans"):
                for _ in range(20):
                    result = await service.execute_query("""
                        SELECT e.*, d.department_name, j.job_title
                        FROM employees e
                        CROSS JOIN departments d
                        CROSS JOIN jobs j
                    """)
                    assert result.success
                    gc.collect()

        finally:
            await service.close_pool()

    async def benchmark_stress_testing(self) -> None:
        """Benchmark stress scenarios."""
        service = FlextDbOracleConnectionService(self.config)
        await service.initialize_pool()

        try:
            # Test 1: Rapid fire queries
            async with self.measure_performance("rapid_fire_queries"):

                async def rapid_query(query_id: int):
                    return await service.execute_query(
                        "SELECT :id, SYSDATE FROM DUAL", {"id": query_id}
                    )

                tasks = [rapid_query(i) for i in range(200)]
                results = await asyncio.gather(*tasks)
                successful = sum(1 for r in results if r.success)
                assert successful == 200

            # Test 2: Connection pool stress
            async with self.measure_performance("connection_pool_stress"):

                async def pool_stress_query() -> None:
                    for _ in range(10):
                        result = await service.execute_query("SELECT 1 FROM DUAL")
                        assert result.success

                tasks = [pool_stress_query() for _ in range(10)]
                await asyncio.gather(*tasks)

        finally:
            await service.close_pool()

    async def run_all_benchmarks(self) -> dict[str, Any]:
        """Run all performance benchmarks."""
        start_time = time.perf_counter()

        try:
            await self.benchmark_connection_performance()

            await self.benchmark_query_performance()

            await self.benchmark_memory_usage()

            await self.benchmark_stress_testing()

        except Exception as e:
            traceback.print_exc()
            return {"error": str(e), "results": self.results}

        total_time = time.perf_counter() - start_time

        # Calculate statistics
        execution_times = [r["execution_time_seconds"] for r in self.results.values()]
        memory_usages = [r["memory_used_bytes"] for r in self.results.values()]

        summary = {
            "total_benchmarks": len(self.results),
            "total_execution_time": total_time,
            "average_test_time": mean(execution_times) if execution_times else 0,
            "median_test_time": median(execution_times) if execution_times else 0,
            "total_memory_used": sum(memory_usages),
            "average_memory_per_test": mean(memory_usages) if memory_usages else 0,
            "peak_memory_usage": max(
                r["peak_memory_bytes"] for r in self.results.values()
            )
            if self.results
            else 0,
            "detailed_results": self.results,
        }

        # Identify performance insights
        slowest_tests = sorted(
            self.results.items(),
            key=lambda x: x[1]["execution_time_seconds"],
            reverse=True,
        )[:3]

        memory_intensive_tests = sorted(
            self.results.items(), key=lambda x: x[1]["peak_memory_bytes"], reverse=True
        )[:3]

        for _i, (_test_name, metrics) in enumerate(slowest_tests, 1):
            pass

        for _i, (_test_name, metrics) in enumerate(memory_intensive_tests, 1):
            metrics["peak_memory_bytes"] / 1024 / 1024

        return summary


async def main() -> None:
    """Main benchmark execution."""
    import subprocess
    import sys

    # Check if Oracle is running
    result = subprocess.run(
        [
            "docker",
            "ps",
            "--filter",
            "name=flext-oracle-test",
            "--format",
            "{{.Status}}",
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    if "Up" not in result.stdout:
        sys.exit(1)

    # Wait for Oracle to be fully ready
    await asyncio.sleep(2)

    benchmark = SimplifiedPerformanceBenchmark()
    summary = await benchmark.run_all_benchmarks()

    if "error" in summary:
        sys.exit(1)
    else:
        # Save results to file
        import json

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_file = f"benchmark_results_{timestamp}.json"
        with open(results_file, "w") as f:
            json.dump(summary, f, indent=2, default=str)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        sys.exit(130)
    except Exception:
        sys.exit(1)
