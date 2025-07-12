# FLEXT DB Oracle

Oracle Database adapter para o framework FLEXT - Ferramentas empresariais para análise, comparação e manutenção de bancos Oracle.

[![Python 3.13+](https://img.shields.io/badge/python-3.13+-blue.svg)](https://www.python.org/downloads/)
[![FLEXT Framework](https://img.shields.io/badge/framework-FLEXT-green.svg)](https://github.com/flext/flext-core)

## Visão Geral

O `flext-db-oracle` é um componente do ecossistema FLEXT que fornece funcionalidades avançadas para trabalhar com bancos de dados Oracle. Utiliza a arquitetura limpa do flext-core e oferece ferramentas para análise de schema, comparação de dados, otimização de consultas e monitoramento de saúde.

## Funcionalidades

### 🔍 Análise de Schema

- Extração completa de metadados Oracle (tabelas, views, sequences, procedures)
- Análise de dependências e estruturas complexas
- Geração automática de DDL

### 📊 Comparação de Dados

- Comparação eficiente entre tabelas e schemas
- Suporte a grandes volumes com processamento em lotes
- Detecção de diferenças com algoritmos otimizados

### ⚡ Otimização de Performance

- Análise de planos de execução Oracle
- Estatísticas de performance com v$views
- Sugestões de otimização e índices

### 🔧 Monitoramento de Saúde

- Verificação de saúde do banco Oracle
- Análise de tablespaces e sessões
- Métricas de performance em tempo real

## Instalação

```bash
# Clone do repositório FLEXT
git clone https://github.com/flext/flext-db-oracle.git
cd flext-db-oracle

# Instalação com Poetry
poetry install

# Ativação do ambiente
poetry shell
```

## Uso Básico

### Configuração

```python
from flext_db_oracle.config import OracleConfig

config = OracleConfig(
    username="usuario",
    password="senha",
    service_name="ORCL",
    host="localhost",
    port=1521
)
```

### Análise de Schema

```python
from flext_db_oracle.application.services import OracleConnectionService
from flext_db_oracle.schema.analyzer import SchemaAnalyzer

# Conectar ao Oracle
connection_service = OracleConnectionService(config)
analyzer = SchemaAnalyzer(connection_service)

# Analisar schema
result = await analyzer.analyze_schema("HR")
if result.is_success:
    schema_data = result.value
    print(f"Encontradas {len(schema_data['tables'])} tabelas")
```

### Comparação de Dados

```python
from flext_db_oracle.compare.differ import DataDiffer

differ = DataDiffer()

# Comparar dados entre tabelas
result = await differ.compare_table_data(
    source_connection, 
    target_connection, 
    "EMPLOYEES", 
    ["EMPLOYEE_ID"]
)

if result.is_success:
    differences = result.value
    print(f"Encontradas {len(differences)} diferenças")
```

### Geração de DDL

```python
from flext_db_oracle.schema.ddl import DDLGenerator

generator = DDLGenerator(include_comments=True)

# Gerar DDL para tabela
result = await generator.generate_table_ddl(table_metadata)
if result.is_success:
    ddl_script = result.value
    print(ddl_script)
```

### Monitoramento de Saúde

```python
from flext_db_oracle.maintenance.health import HealthChecker

health_checker = HealthChecker(connection_service)

# Verificar saúde geral
result = await health_checker.check_overall_health()
if result.is_success:
    health = result.value
    print(f"Status: {health.overall_status}")
```

## API Simples

Para uso direto sem configuração complexa:

```python
from flext_db_oracle.simple_api import setup_oracle_db

# Configuração automática
result = setup_oracle_db()
if result.is_success:
    config = result.value
    print("Oracle configurado com sucesso")
```

## CLI

Ferramentas de linha de comando para operações rápidas:

```bash
# Verificar conexão
python -m flext_db_oracle.cli.main test-connection

# Analisar schema
python -m flext_db_oracle.cli.main analyze-schema --schema HR

# Verificar saúde do banco
python -m flext_db_oracle.cli.main health-check
```

## Estrutura do Projeto

```
src/flext_db_oracle/
├── application/          # Serviços de aplicação
├── cli/                 # Interface de linha de comando
├── compare/             # Ferramentas de comparação
├── connection/          # Gerenciamento de conexões
├── domain/              # Modelos de domínio
├── maintenance/         # Ferramentas de manutenção
├── schema/              # Análise e DDL de schema
├── sql/                 # Otimização e parsing SQL
└── utils/               # Utilitários compartilhados
```

## Integração FLEXT

Este projeto utiliza:

- **flext-core**: Fundação com ServiceResult e patterns DDD
- **flext-observability**: Logging estruturado e métricas
- **Arquitetura limpa**: Separação clara entre domínio e infraestrutura

## Configuração de Ambiente

```bash
# Variáveis Oracle
export ORACLE_USERNAME=usuario
export ORACLE_PASSWORD=senha
export ORACLE_SERVICE_NAME=ORCL
export ORACLE_HOST=localhost
export ORACLE_PORT=1521

# Configurações FLEXT
export FLEXT_LOG_LEVEL=INFO
export FLEXT_ENVIRONMENT=development
```

## Desenvolvimento

### Executar Testes

```bash
# Testes unitários
pytest tests/unit/ -v

# Testes de integração (requer Oracle)
export ORACLE_INTEGRATION_TESTS=1
pytest tests/integration/ -v

# Cobertura
pytest --cov=flext_db_oracle --cov-report=html
```

### Qualidade de Código

```bash
# Linting
ruff check src/ tests/

# Verificação de tipos
mypy src/

# Formatação
ruff format src/ tests/
```

### Requisitos

- Python 3.13+
- Oracle Database 19c+ ou Oracle XE
- Driver `oracledb` (moderno Python driver da Oracle)
- Dependências FLEXT (flext-core, flext-observability)

## Contribuição

1. Faça fork do repositório
2. Crie uma branch para sua feature (`git checkout -b feature/nova-funcionalidade`)
3. Implemente seguindo os padrões FLEXT
4. Adicione testes apropriados
5. Execute verificações de qualidade
6. Submeta um pull request

## Licença

Este projeto é parte do framework FLEXT e segue a mesma licença.

## Suporte

- **Issues**: [GitHub Issues](https://github.com/flext/flext-db-oracle/issues)
- **Documentação FLEXT**: Framework principal
- **Oracle Docs**: Documentação oficial Oracle disponível em `docs/oracle-resources/`

---

**Parte do ecossistema FLEXT** - Ferramentas empresariais para desenvolvimento e integração.
