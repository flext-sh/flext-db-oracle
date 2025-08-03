"""Test configuration for flext-db-oracle - ORACLE REAL TESTING ONLY."""

from __future__ import annotations

import os
import subprocess
import time
from collections.abc import Generator
from pathlib import Path

import pytest

from flext_db_oracle import FlextDbOracleApi, FlextDbOracleConfig


def pytest_configure(config: pytest.Config) -> None:
    """Configure pytest with Oracle container for ALL tests - NO MOCKS ALLOWED."""
    # FORCE Oracle container usage for ALL tests - no mocks, only real testing
    os.environ["SKIP_E2E_TESTS"] = "false"
    os.environ["ORACLE_INTEGRATION_TESTS"] = "1"
    os.environ["USE_REAL_ORACLE"] = "true"

    # Oracle connection configuration for ALL tests
    os.environ["TEST_ORACLE_HOST"] = "localhost"
    os.environ["TEST_ORACLE_PORT"] = "1521"
    os.environ["TEST_ORACLE_SERVICE"] = "XEPDB1"
    os.environ["TEST_ORACLE_USER"] = "flexttest"
    os.environ["TEST_ORACLE_PASSWORD"] = "FlextTest123"

    # Set FLEXT target environment variables for consistency across ALL tests
    os.environ["FLEXT_TARGET_ORACLE_HOST"] = "localhost"
    os.environ["FLEXT_TARGET_ORACLE_PORT"] = "1521"
    os.environ["FLEXT_TARGET_ORACLE_SERVICE_NAME"] = "XEPDB1"
    os.environ["FLEXT_TARGET_ORACLE_USERNAME"] = "flexttest"
    os.environ["FLEXT_TARGET_ORACLE_PASSWORD"] = "FlextTest123"

    print("🔥 PYTEST CONFIGURADO PARA USAR ORACLE REAL - SEM MOCKS!")


@pytest.fixture(scope="session", autouse=True)
def oracle_container() -> Generator[None]:
    """Ensure Oracle container is running for ALL tests - MANDATORY."""
    project_root = Path(__file__).parent.parent
    compose_file = project_root / "docker-compose.oracle.yml"

    if not compose_file.exists():
        pytest.skip("Docker compose file not found - skipping Oracle container tests")

    try:
        # Check if Docker is available
        subprocess.run(["docker", "version"], capture_output=True, check=True)
        subprocess.run(["docker-compose", "version"], capture_output=True, check=True)

        print("🐳 Verificando status do container Oracle...")

        # Check if container is already running and healthy
        result = subprocess.run(
            ["docker-compose", "-f", str(compose_file), "ps", "-q", "oracle-xe"],
            capture_output=True,
            text=True,
            check=False,
        )

        container_running = bool(result.stdout.strip())

        if container_running:
            # Check if container is healthy
            health_result = subprocess.run(
                ["docker", "inspect", "flext-oracle-test", "--format", "{{.State.Health.Status}}"],
                capture_output=True,
                text=True,
                check=False,
            )
            is_healthy = "healthy" in health_result.stdout
            print(f"📊 Container encontrado - Status de saúde: {health_result.stdout.strip()}")
        else:
            is_healthy = False
            print("⚠️ Container Oracle não está rodando")

        if not container_running or not is_healthy:
            print("🚀 Iniciando container Oracle (isso pode levar alguns minutos)...")

            # Start the container
            start_result = subprocess.run(
                ["docker-compose", "-f", str(compose_file), "up", "-d", "oracle-xe"],
                capture_output=True,
                text=True,
                check=True,
            )
            print("✅ Container Oracle iniciado!")

            # Wait for container to be healthy with better feedback
            max_attempts = 120  # 10 minutes max (Oracle can be slow)
            print("⏳ Aguardando Oracle ficar saudável...")

            for attempt in range(max_attempts):
                health_result = subprocess.run(
                    ["docker", "inspect", "flext-oracle-test", "--format", "{{.State.Health.Status}}"],
                    capture_output=True,
                    text=True,
                    check=False,
                )

                health_status = health_result.stdout.strip()

                if health_status == "healthy":
                    print("🎉 Oracle container está saudável!")

                    # Run setup script to create test user and schema
                    print("🔧 Executando script de setup do banco...")
                    setup_result = subprocess.run(
                        ["docker-compose", "-f", str(compose_file), "up", "--no-deps", "oracle-setup"],
                        capture_output=True,
                        text=True,
                        check=False,
                    )

                    if setup_result.returncode == 0:
                        print("✅ Setup do banco completado com sucesso!")
                    else:
                        print(f"⚠️ Setup do banco falhou (pode já estar configurado): {setup_result.stderr}")

                    # Extra time for full initialization
                    time.sleep(5)
                    break
                elif health_status == "unhealthy":
                    print(f"❌ Container não saudável na tentativa {attempt + 1}/{max_attempts}")
                else:
                    print(f"⏳ Status: {health_status} - Tentativa {attempt + 1}/{max_attempts}")

                time.sleep(5)
            else:
                pytest.exit("Oracle container failed to become healthy - cannot run tests without Oracle")
        else:
            print("✅ Container Oracle já está saudável e pronto!")

        yield

    except subprocess.CalledProcessError as e:
        pytest.exit(f"Failed to manage Oracle container: {e}")
    except FileNotFoundError:
        pytest.exit("Docker/Docker Compose not available - cannot run tests without Docker")
    except Exception as e:
        pytest.exit(f"Unexpected error managing Oracle container: {e}")


@pytest.fixture
def real_oracle_config(oracle_container: None) -> FlextDbOracleConfig:
    """Return real Oracle configuration for ALL tests."""
    return FlextDbOracleConfig(
        host=os.getenv("TEST_ORACLE_HOST", "localhost"),
        port=int(os.getenv("TEST_ORACLE_PORT", "1521")),
        service_name=os.getenv("TEST_ORACLE_SERVICE", "XEPDB1"),
        username=os.getenv("TEST_ORACLE_USER", "flexttest"),
        password=os.getenv("TEST_ORACLE_PASSWORD", "FlextTest123"),
        pool_min=1,
        pool_max=5,
        timeout=30,
    )


@pytest.fixture
def oracle_api(real_oracle_config: FlextDbOracleConfig) -> FlextDbOracleApi:
    """Return connected Oracle API for ALL tests."""
    return FlextDbOracleApi(real_oracle_config)


@pytest.fixture
def connected_oracle_api(oracle_api: FlextDbOracleApi) -> FlextDbOracleApi:
    """Return Oracle API that is already connected."""
    connected_api = oracle_api.connect()
    yield connected_api
    try:
        connected_api.disconnect()
    except Exception:
        pass  # Best effort cleanup


# REMOVE ALL MOCK FIXTURES - ONLY REAL ORACLE TESTING ALLOWED
