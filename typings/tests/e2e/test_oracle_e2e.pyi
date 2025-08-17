import pytest

from flext_db_oracle import FlextDbOracleConfig

class TestOracleE2E:
    @pytest.mark.e2e
    def test_complete_oracle_workflow(
        self, real_oracle_config: FlextDbOracleConfig
    ) -> None: ...
    @pytest.mark.e2e
    def test_singer_type_conversion_e2e(
        self, real_oracle_config: FlextDbOracleConfig
    ) -> None: ...
    @pytest.mark.e2e
    def test_configuration_from_environment_e2e(self) -> None: ...
    @pytest.mark.e2e
    def test_error_handling_e2e(self) -> None: ...
    @pytest.mark.e2e
    def test_concurrent_operations_e2e(
        self, real_oracle_config: FlextDbOracleConfig
    ) -> None: ...
    @pytest.mark.e2e
    @pytest.mark.benchmark
    def test_performance_benchmark_e2e(
        self, real_oracle_config: FlextDbOracleConfig
    ) -> None: ...
