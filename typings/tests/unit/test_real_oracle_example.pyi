from flext_db_oracle import FlextDbOracleApi, FlextDbOracleConfig

class TestRealOracleConnection:
    def test_real_connection_connect_disconnect(
        self, real_oracle_config: FlextDbOracleConfig
    ) -> None: ...
    def test_real_connection_execute_query(
        self, real_oracle_config: FlextDbOracleConfig
    ) -> None: ...
    def test_real_connection_fetch_one(
        self, real_oracle_config: FlextDbOracleConfig
    ) -> None: ...
    def test_real_connection_execute_many(
        self, real_oracle_config: FlextDbOracleConfig
    ) -> None: ...

class TestRealOracleApi:
    def test_real_api_connect_context_manager(
        self, real_oracle_config: FlextDbOracleConfig
    ) -> None: ...
    def test_real_api_get_schemas(
        self, connected_oracle_api: FlextDbOracleApi
    ) -> None: ...
    def test_real_api_get_tables(
        self, connected_oracle_api: FlextDbOracleApi
    ) -> None: ...
    def test_real_api_get_columns(
        self, connected_oracle_api: FlextDbOracleApi
    ) -> None: ...
    def test_real_api_query_with_timing(
        self, connected_oracle_api: FlextDbOracleApi
    ) -> None: ...
    def test_real_api_singer_type_conversion(
        self, connected_oracle_api: FlextDbOracleApi
    ) -> None: ...
    def test_real_api_table_operations(
        self, connected_oracle_api: FlextDbOracleApi
    ) -> None: ...

class TestRealOracleErrorHandling:
    def test_real_connection_invalid_credentials(self) -> None: ...
    def test_real_connection_invalid_sql(
        self, real_oracle_config: FlextDbOracleConfig
    ) -> None: ...
    def test_real_api_not_connected_operations(
        self, real_oracle_config: FlextDbOracleConfig
    ) -> None: ...
