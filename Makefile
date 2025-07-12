#!/usr/bin/make -f
# FLEXT DB Oracle - Makefile for development and operations
# Uses Poetry for dependency management and provides CLI shortcuts

.PHONY: help install test lint format clean cli-help cli-test cli-tables cli-health

# Variables
PYTHON := poetry run python
CLI := ./flext-db-oracle

# Default target
help: ## Show this help message
	@echo "FLEXT DB Oracle - Development & Operations Commands"
	@echo ""
	@echo "📦 Development Commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | grep -v "CLI Commands" | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'
	@echo ""
	@echo "🔧 CLI Commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*CLI.*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[33m%-15s\033[0m %s\n", $$1, $$2}'
	@echo ""
	@echo "💡 Examples:"
	@echo "  make cli-test HOST=localhost PORT=1521 SERVICE=XE USER=hr PASS=hr"
	@echo "  make cli-tables URL=oracle://hr:hr@localhost:1521/XE"
	@echo "  make cli-health HOST=localhost USER=system PASS=oracle"

install: ## Install dependencies
	@echo "📦 Installing dependencies..."
	poetry install --no-dev
	@echo "✅ Dependencies installed"

install-dev: ## Install development dependencies
	@echo "📦 Installing development dependencies..."
	poetry install
	@echo "✅ Development dependencies installed"

test: ## Run tests
	@echo "🧪 Running tests..."
	$(PYTHON) -m pytest tests/ -v
	@echo "✅ Tests completed"

test-cov: ## Run tests with coverage
	@echo "🧪 Running tests with coverage..."
	$(PYTHON) -m pytest tests/ -v --cov=src/flext_db_oracle --cov-report=html --cov-report=term
	@echo "✅ Tests with coverage completed"

lint: ## Run linting
	@echo "🔍 Running maximum strictness linting for flext-db-oracle..."
	poetry run ruff check . --output-format=full
	@echo "✅ Linting completed"

lint-fix: ## Run linting with auto-fix
	@echo "🔧 Running linting with auto-fix..."
	poetry run ruff check . --fix
	@echo "✅ Linting with auto-fix completed"

format: ## Format code
	@echo "🎨 Formatting code..."
	poetry run ruff format .
	@echo "✅ Code formatting completed"

clean: ## Clean build artifacts
	@echo "🧹 Cleaning build artifacts..."
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .pytest_cache/
	rm -rf htmlcov/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	@echo "✅ Clean completed"

build: ## Build package
	@echo "📦 Building package..."
	poetry build
	@echo "✅ Package built"

# CLI Commands
cli-help: ## CLI - Show CLI help
	@echo "🔧 FLEXT DB Oracle CLI Help:"
	$(CLI) --help

cli-test: ## CLI - Test database connection
	@echo "🔍 Testing database connection..."
	$(CLI) --host $(or $(HOST),localhost) --port $(or $(PORT),1521) --service-name $(or $(SERVICE),XE) --username $(or $(USER),user) --password $(or $(PASS),password) test

cli-tables: ## CLI - List database tables
	@echo "📋 Listing database tables..."
	@if [ -n "$(URL)" ]; then \
		$(CLI) --url $(URL) tables; \
	else \
		$(CLI) --host $(or $(HOST),localhost) --port $(or $(PORT),1521) --service-name $(or $(SERVICE),XE) --username $(or $(USER),user) --password $(or $(PASS),password) tables; \
	fi

cli-describe: ## CLI - Describe table structure
	@echo "📋 Describing table: $(TABLE)"
	@if [ -z "$(TABLE)" ]; then \
		echo "❌ Error: TABLE parameter is required. Usage: make cli-describe TABLE=table_name"; \
		exit 1; \
	fi
	@if [ -n "$(URL)" ]; then \
		$(CLI) --url $(URL) describe $(TABLE); \
	else \
		$(CLI) --host $(or $(HOST),localhost) --port $(or $(PORT),1521) --service-name $(or $(SERVICE),XE) --username $(or $(USER),user) --password $(or $(PASS),password) describe $(TABLE); \
	fi

cli-health: ## CLI - Perform database health check
	@echo "🏥 Performing database health check..."
	@if [ -n "$(URL)" ]; then \
		$(CLI) --url $(URL) health; \
	else \
		$(CLI) --host $(or $(HOST),localhost) --port $(or $(PORT),1521) --service-name $(or $(SERVICE),XE) --username $(or $(USER),user) --password $(or $(PASS),password) health; \
	fi

cli-query: ## CLI - Execute SQL query
	@echo "⚡ Executing SQL query: $(SQL)"
	@if [ -z "$(SQL)" ]; then \
		echo "❌ Error: SQL parameter is required. Usage: make cli-query SQL='SELECT * FROM dual'"; \
		exit 1; \
	fi
	@if [ -n "$(URL)" ]; then \
		$(CLI) --url $(URL) query "$(SQL)" --limit $(or $(LIMIT),10); \
	else \
		$(CLI) --host $(or $(HOST),localhost) --port $(or $(PORT),1521) --service-name $(or $(SERVICE),XE) --username $(or $(USER),user) --password $(or $(PASS),password) query "$(SQL)" --limit $(or $(LIMIT),10); \
	fi

# Development shortcuts
dev-setup: install-dev ## Setup development environment
	@echo "🚀 Development environment setup completed"

dev-test: test-cov lint ## Run full development tests

dev-clean: clean ## Clean development environment
	@echo "🧹 Development environment cleaned"

# Docker shortcuts (if needed)
docker-build: ## Build Docker image
	@echo "🐳 Building Docker image..."
	docker build -t flext-db-oracle .
	@echo "✅ Docker image built"

docker-run: ## Run Docker container
	@echo "🐳 Running Docker container..."
	docker run -it --rm flext-db-oracle
	@echo "✅ Docker container finished"

# Documentation
docs: ## Generate documentation
	@echo "📚 Generating documentation..."
	@echo "Documentation available in README.md and FLEXT_CORE_MIGRATION_APPLIED.md"
	@echo "✅ Documentation ready"

# Version management
version: ## Show current version
	@echo "📊 Current version:"
	@poetry version
	
bump-patch: ## Bump patch version
	@echo "🔢 Bumping patch version..."
	poetry version patch
	@echo "✅ Patch version bumped"

bump-minor: ## Bump minor version
	@echo "🔢 Bumping minor version..."
	poetry version minor
	@echo "✅ Minor version bumped"

bump-major: ## Bump major version
	@echo "🔢 Bumping major version..."
	poetry version major
	@echo "✅ Major version bumped"
