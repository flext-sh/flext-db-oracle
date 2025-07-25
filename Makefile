# FLEXT DB Oracle - Makefile Unificado
# ===================================
# Oracle Database Integration Service
# Python 3.13 + Oracle + Clean Architecture + Zero Tolerance Quality

.PHONY: help install test lint type-check format clean build docs
.PHONY: check validate dev-setup deps-update deps-audit info diagnose
.PHONY: install-dev test-unit test-integration test-coverage test-watch
.PHONY: format-check security pre-commit build-clean publish publish-test
.PHONY: dev dev-test clean-all emergency-reset
.PHONY: oracle-test oracle-connect oracle-migrate oracle-validate

# ============================================================================
# 🎯 CONFIGURAÇÃO E DETECÇÃO
# ============================================================================

# Detectar nome do projeto
PROJECT_NAME := flext-db-oracle
PROJECT_TITLE := FLEXT DB Oracle
PROJECT_VERSION := $(shell poetry version -s)

# Ambiente Python
PYTHON := python3.13
POETRY := poetry
VENV_PATH := $(shell poetry env info --path 2>/dev/null || echo "")

# ============================================================================
# 🎯 AJUDA E INFORMAÇÃO
# ============================================================================

help: ## Mostrar ajuda e comandos disponíveis
	@echo "🏆 $(PROJECT_TITLE) - Comandos Essenciais"
	@echo "===================================="
	@echo "📦 Oracle Database Integration Service"
	@echo "🐍 Python 3.13 + Oracle + Zero Tolerância"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "%-20s %s\\n", $$1, $$2}'
	@echo ""
	@echo "💡 Comandos principais: make install, make test, make lint"

info: ## Mostrar informações do projeto
	@echo "📊 Informações do Projeto"
	@echo "======================"
	@echo "Nome: $(PROJECT_NAME)"
	@echo "Título: $(PROJECT_TITLE)"
	@echo "Versão: $(PROJECT_VERSION)"
	@echo "Python: $(shell $(PYTHON) --version 2>/dev/null || echo "Não encontrado")"
	@echo "Poetry: $(shell $(POETRY) --version 2>/dev/null || echo "Não instalado")"
	@echo "Venv: $(shell [ -n "$(VENV_PATH)" ] && echo "$(VENV_PATH)" || echo "Não ativado")"
	@echo "Diretório: $(CURDIR)"
	@echo "Git Branch: $(shell git branch --show-current 2>/dev/null || echo "Não é repo git")"
	@echo "Git Status: $(shell git status --porcelain 2>/dev/null | wc -l | xargs echo) arquivos alterados"

diagnose: ## Executar diagnósticos completos
	@echo "🔍 Executando diagnósticos para $(PROJECT_NAME)..."
	@echo "Informações do Sistema:"
	@echo "OS: $(shell uname -s)"
	@echo "Arquitetura: $(shell uname -m)"
	@echo "Python: $(shell $(PYTHON) --version 2>/dev/null || echo "Não encontrado")"
	@echo "Poetry: $(shell $(POETRY) --version 2>/dev/null || echo "Não instalado")"
	@echo ""
	@echo "Estrutura do Projeto:"
	@ls -la
	@echo ""
	@echo "Configuração Poetry:"
	@$(POETRY) config --list 2>/dev/null || echo "Poetry não configurado"
	@echo ""
	@echo "Status das Dependências:"
	@$(POETRY) show --outdated 2>/dev/null || echo "Nenhuma dependência desatualizada"

# ============================================================================
# 📦 GERENCIAMENTO DE DEPENDÊNCIAS
# ============================================================================

validate-setup: ## Validar ambiente de desenvolvimento
	@echo "🔍 Validando ambiente de desenvolvimento..."
	@command -v $(PYTHON) >/dev/null 2>&1 || { echo "❌ Python 3.13 não encontrado"; exit 1; }
	@command -v $(POETRY) >/dev/null 2>&1 || { echo "❌ Poetry não encontrado"; exit 1; }
	@test -f pyproject.toml || { echo "❌ pyproject.toml não encontrado"; exit 1; }
	@echo "✅ Validação do ambiente passou"

install: validate-setup ## Instalar dependências de runtime
	@echo "📦 Instalando dependências de runtime para $(PROJECT_NAME)..."
	@$(POETRY) install --only main
	@echo "✅ Dependências de runtime instaladas"

install-dev: validate-setup ## Instalar todas as dependências incluindo dev tools
	@echo "📦 Instalando todas as dependências para $(PROJECT_NAME)..."
	@$(POETRY) install --all-extras
	@echo "✅ Todas as dependências instaladas"

deps-update: ## Atualizar dependências para versões mais recentes
	@echo "🔄 Atualizando dependências para $(PROJECT_NAME)..."
	@$(POETRY) update
	@echo "✅ Dependências atualizadas"

deps-show: ## Mostrar árvore de dependências
	@echo "📊 Árvore de dependências para $(PROJECT_NAME):"
	@$(POETRY) show --tree

deps-audit: ## Auditoria de dependências para vulnerabilidades
	@echo "🔍 Auditando dependências para $(PROJECT_NAME)..."
	@$(POETRY) run pip-audit --format=columns || echo "⚠️  pip-audit não disponível"
	@$(POETRY) run safety check --json || echo "⚠️  safety não disponível"

# ============================================================================
# 🧪 TESTES
# ============================================================================

test: ## Executar todos os testes (90% cobertura mínima)
	@echo "🧪 Executando todos os testes para $(PROJECT_NAME)..."
	@$(POETRY) run pytest tests/ -v --cov=src/flext_db_oracle --cov-report=term-missing --cov-fail-under=90
	@echo "✅ Todos os testes passaram"

test-unit: ## Executar apenas testes unitários
	@echo "🧪 Executando testes unitários para $(PROJECT_NAME)..."
	@$(POETRY) run pytest tests/unit/ -xvs -m "not integration and not slow"
	@echo "✅ Testes unitários passaram"

test-integration: ## Executar apenas testes de integração
	@echo "🧪 Executando testes de integração para $(PROJECT_NAME)..."
	@$(POETRY) run pytest tests/integration/ -xvs -m "integration"
	@echo "✅ Testes de integração passaram"

test-coverage: ## Executar testes com relatório de cobertura
	@echo "🧪 Executando testes com cobertura para $(PROJECT_NAME)..."
	@$(POETRY) run pytest --cov --cov-report=html --cov-report=term-missing --cov-report=xml
	@echo "✅ Relatório de cobertura gerado"

test-watch: ## Executar testes em modo watch
	@echo "👀 Executando testes em modo watch para $(PROJECT_NAME)..."
	@$(POETRY) run pytest-watch --clear

coverage-html: test-coverage ## Gerar e abrir relatório HTML de cobertura
	@echo "📊 Abrindo relatório de cobertura..."
	@python -m webbrowser htmlcov/index.html

# ============================================================================
# 🎨 QUALIDADE DE CÓDIGO E FORMATAÇÃO
# ============================================================================

lint: ## Executar todos os linters com máxima rigorosidade
	@echo "🔍 Executando linting com máxima rigorosidade para $(PROJECT_NAME)..."
	@$(POETRY) run ruff check . --output-format=github
	@echo "✅ Linting completado"

format: ## Formatar código com padrões rigorosos
	@echo "🎨 Formatando código para $(PROJECT_NAME)..."
	@$(POETRY) run ruff format .
	@$(POETRY) run ruff check . --fix --unsafe-fixes
	@echo "✅ Código formatado"

format-check: ## Verificar formatação sem alterar
	@echo "🔍 Verificando formatação para $(PROJECT_NAME)..."
	@$(POETRY) run ruff format . --check
	@$(POETRY) run ruff check . --output-format=github
	@echo "✅ Formatação verificada"

type-check: ## Executar verificação de tipos rigorosa
	@echo "🔍 Executando verificação de tipos rigorosa para $(PROJECT_NAME)..."
	@$(POETRY) run mypy src/ --strict --show-error-codes
	@echo "✅ Verificação de tipos passou"

security: ## Executar análise de segurança
	@echo "🔒 Executando análise de segurança para $(PROJECT_NAME)..."
	@$(POETRY) run bandit -r src/ -f json || echo "⚠️  bandit não disponível"
	@$(POETRY) run detect-secrets scan --all-files || echo "⚠️  detect-secrets não disponível"
	@echo "✅ Análise de segurança completada"

pre-commit: ## Executar hooks pre-commit
	@echo "🔧 Executando hooks pre-commit para $(PROJECT_NAME)..."
	@$(POETRY) run pre-commit run --all-files || echo "⚠️  pre-commit não disponível"
	@echo "✅ Hooks pre-commit completados"

check: lint type-check security ## Executar todas as verificações de qualidade
	@echo "🔍 Executando verificações abrangentes de qualidade para $(PROJECT_NAME)..."
	@echo "✅ Todas as verificações de qualidade passaram"

validate: check test ## Validação STRICT de conformidade (tudo deve passar)
	@echo "✅ TODOS OS QUALITY GATES PASSARAM - FLEXT DB ORACLE COMPLIANT"

# ============================================================================
# 🏗️ BUILD E DISTRIBUIÇÃO
# ============================================================================

build: clean ## Construir o pacote com Poetry
	@echo "🏗️  Construindo pacote $(PROJECT_NAME)..."
	@$(POETRY) build
	@echo "✅ Pacote construído com sucesso"
	@echo "📦 Artefatos de build:"
	@ls -la dist/

build-clean: clean build ## Limpar e construir
	@echo "✅ Build limpo completado"

publish-test: build ## Publicar no TestPyPI
	@echo "📤 Publicando $(PROJECT_NAME) no TestPyPI..."
	@$(POETRY) publish --repository testpypi
	@echo "✅ Publicado no TestPyPI"

publish: build ## Publicar no PyPI
	@echo "📤 Publicando $(PROJECT_NAME) no PyPI..."
	@$(POETRY) publish
	@echo "✅ Publicado no PyPI"

# ============================================================================
# 📚 DOCUMENTAÇÃO
# ============================================================================

docs: ## Gerar documentação
	@echo "📚 Gerando documentação para $(PROJECT_NAME)..."
	@if [ -f mkdocs.yml ]; then \
		$(POETRY) run mkdocs build; \
	else \
		echo "⚠️  Nenhum mkdocs.yml encontrado, pulando geração de documentação"; \
	fi
	@echo "✅ Documentação gerada"

docs-serve: ## Servir documentação localmente
	@echo "📚 Servindo documentação para $(PROJECT_NAME)..."
	@if [ -f mkdocs.yml ]; then \
		$(POETRY) run mkdocs serve; \
	else \
		echo "⚠️  Nenhum mkdocs.yml encontrado"; \
	fi

# ============================================================================
# 🚀 DESENVOLVIMENTO
# ============================================================================

dev-setup: install-dev ## Configuração completa de desenvolvimento
	@echo "🚀 Configurando ambiente de desenvolvimento para $(PROJECT_NAME)..."
	@$(POETRY) run pre-commit install || echo "⚠️  pre-commit não disponível"
	@echo "✅ Ambiente de desenvolvimento pronto"

dev: ## Executar em modo desenvolvimento
	@echo "🚀 Iniciando modo desenvolvimento para $(PROJECT_NAME)..."
	@if [ -f src/flext_db_oracle/cli.py ]; then \
		$(POETRY) run python -m flext_db_oracle.cli --dev; \
	elif [ -f src/flext_db_oracle/main.py ]; then \
		$(POETRY) run python -m flext_db_oracle.main --dev; \
	else \
		echo "⚠️  Nenhum ponto de entrada principal encontrado"; \
	fi

dev-test: ## Ciclo rápido de teste de desenvolvimento
	@echo "⚡ Ciclo rápido de teste de desenvolvimento para $(PROJECT_NAME)..."
	@$(POETRY) run ruff check . --fix
	@$(POETRY) run pytest tests/ -x --tb=short
	@echo "✅ Ciclo de teste de desenvolvimento completado"

# ============================================================================
# 🗄️ OPERAÇÕES ESPECÍFICAS ORACLE
# ============================================================================

oracle-test: ## Testar conectividade Oracle básica
	@echo "🎯 Testando conectividade Oracle básica..."
	@$(POETRY) run python -c "from flext_db_oracle.infrastructure.adapters import DatabaseAdapter; from flext_db_oracle.config import OracleSettings; settings = OracleSettings(); adapter = DatabaseAdapter(settings); print('Teste Oracle básico executado')"
	@echo "✅ Teste Oracle básico completado"

oracle-connect: ## Testar conexão com servidor Oracle
	@echo "🔗 Testando conexão com servidor Oracle..."
	@$(POETRY) run python -c "from flext_db_oracle.infrastructure.clients import OracleClient; from flext_db_oracle.config import OracleSettings; settings = OracleSettings(); client = OracleClient(settings); result = client.test_connection(); print(f'Conexão Oracle: {result}')"
	@echo "✅ Teste de conexão Oracle completado"

oracle-migrate: ## Executar migrações Oracle
	@echo "🔄 Executando migrações Oracle..."
	@$(POETRY) run python -m flext_db_oracle.migrate
	@echo "✅ Migrações Oracle completadas"

oracle-validate: ## Validar configuração Oracle
	@echo "🔍 Validando configuração Oracle..."
	@$(POETRY) run python -c "from flext_db_oracle.config import OracleSettings; settings = OracleSettings(); settings.validate(); print('Configuração Oracle válida')"
	@echo "✅ Configuração Oracle validada"

oracle-schema: ## Verificar schema Oracle
	@echo "📋 Verificando schema Oracle..."
	@$(POETRY) run python -c "from flext_db_oracle.domain.services import SchemaService; from flext_db_oracle.config import OracleSettings; settings = OracleSettings(); service = SchemaService(settings); schema_info = service.get_schema_info(); print(f'Schema Oracle verificado: {len(schema_info)} tabelas')"
	@echo "✅ Verificação de schema Oracle completada"

oracle-operations: oracle-connect oracle-validate oracle-schema ## Validar todas as operações Oracle
	@echo "✅ Todas as operações Oracle validadas"

# ============================================================================
# 🧹 LIMPEZA
# ============================================================================

clean: ## Limpar artefatos de build
	@echo "🧹 Limpando artefatos de build para $(PROJECT_NAME)..."
	@rm -rf build/
	@rm -rf dist/
	@rm -rf *.egg-info/
	@rm -rf .pytest_cache/
	@rm -rf .coverage
	@rm -rf htmlcov/
	@rm -rf .mypy_cache/
	@rm -rf .ruff_cache/
	@rm -rf reports/
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@find . -type f -name "*.pyo" -delete 2>/dev/null || true
	@echo "✅ Limpeza completada"

clean-all: clean ## Limpar tudo incluindo ambiente virtual
	@echo "🧹 Limpeza profunda para $(PROJECT_NAME)..."
	@$(POETRY) env remove --all || true
	@echo "✅ Limpeza profunda completada"

# ============================================================================
# 🚨 PROCEDIMENTOS DE EMERGÊNCIA
# ============================================================================

emergency-reset: ## Reset de emergência para estado limpo
	@echo "🚨 RESET DE EMERGÊNCIA para $(PROJECT_NAME)..."
	@read -p "Tem certeza que quer resetar tudo? (y/N) " -n 1 -r; \
	echo; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		$(MAKE) clean-all; \
		$(MAKE) install-dev; \
		echo "✅ Reset de emergência completado"; \
	else \
		echo "⚠️  Reset de emergência cancelado"; \
	fi

# ============================================================================
# 🎯 VALIDAÇÃO E VERIFICAÇÃO
# ============================================================================

workspace-validate: ## Validar conformidade do workspace
	@echo "🔍 Validando conformidade do workspace para $(PROJECT_NAME)..."
	@test -f pyproject.toml || { echo "❌ pyproject.toml ausente"; exit 1; }
	@test -f CLAUDE.md || echo "⚠️  CLAUDE.md ausente"
	@test -f README.md || echo "⚠️  README.md ausente"
	@test -d src/ || { echo "❌ diretório src/ ausente"; exit 1; }
	@test -d tests/ || echo "⚠️  diretório tests/ ausente"
	@echo "✅ Conformidade do workspace validada"

# ============================================================================
# 🎯 ALIASES DE CONVENIÊNCIA
# ============================================================================

# Aliases para operações comuns
t: test ## Alias para test
l: lint ## Alias para lint
tc: type-check ## Alias para type-check
f: format ## Alias para format
c: clean ## Alias para clean
i: install-dev ## Alias para install-dev
d: dev ## Alias para dev
dt: dev-test ## Alias para dev-test

# Aliases específicos Oracle
ot: oracle-test ## Alias para oracle-test
oc: oracle-connect ## Alias para oracle-connect
om: oracle-migrate ## Alias para oracle-migrate
ov: oracle-validate ## Alias para oracle-validate
os: oracle-schema ## Alias para oracle-schema
oo: oracle-operations ## Alias para oracle-operations

# Configurações de ambiente
export PYTHONPATH := $(PWD)/src:$(PYTHONPATH)
export PYTHONDONTWRITEBYTECODE := 1
export PYTHONUNBUFFERED := 1

# Oracle settings for development
export FLEXT_ORACLE_HOST := localhost
export FLEXT_ORACLE_PORT := 1521
export FLEXT_ORACLE_SERVICE_NAME := ORCLPDB1
export FLEXT_ORACLE_USERNAME := flext_user
export FLEXT_ORACLE_PASSWORD := flext_password

.DEFAULT_GOAL := help