# =============================================================================
# FLEXT-DB-ORACLE - Oracle Database Integration Library Makefile
# =============================================================================
# Python 3.13+ Oracle Database Framework - Clean Architecture + DDD + Zero Tolerance
# =============================================================================

# Project Configuration
PROJECT_NAME := flext-db-oracle
PYTHON_VERSION := 3.13
POETRY := poetry
SRC_DIR := src
TESTS_DIR := tests
COV_DIR := flext_db_oracle

# Quality Standards
MIN_COVERAGE := 100

# Oracle Configuration
ORACLE_HOST := localhost
ORACLE_PORT := 1521
ORACLE_SERVICE := XEPDB1

# Export Configuration
export PROJECT_NAME PYTHON_VERSION MIN_COVERAGE ORACLE_HOST ORACLE_PORT ORACLE_SERVICE

# =============================================================================
# HELP & INFORMATION
# =============================================================================

.PHONY: help
help: ## Show available commands
	@echo "FLEXT-DB-ORACLE - Oracle Database Integration Library"
	@echo "===================================================="
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

.PHONY: info
info: ## Show project information
	@echo "Project: $(PROJECT_NAME)"
	@echo "Python: $(PYTHON_VERSION)+"
	@echo "Poetry: $(POETRY)"
	@echo "Coverage: $(MIN_COVERAGE)% minimum (MANDATORY)"
	@echo "Oracle: $(ORACLE_HOST):$(ORACLE_PORT)/$(ORACLE_SERVICE)"
	@echo "Architecture: Clean Architecture + DDD + SQLAlchemy 2"

# =============================================================================
# SETUP & INSTALLATION
# =============================================================================

.PHONY: install
install: ## Install dependencies
	$(POETRY) install

.PHONY: install-dev
install-dev: ## Install dev dependencies
	$(POETRY) install --with dev,test,docs

.PHONY: setup
setup: install-dev ## Complete project setup
	$(POETRY) run pre-commit install

# =============================================================================
# QUALITY GATES (MANDATORY - ZERO TOLERANCE)
# =============================================================================

.PHONY: validate
validate: lint type-check security test ## Run all quality gates (MANDATORY ORDER)

.PHONY: check
check: lint type-check ## Quick health check

.PHONY: lint
lint: ## Run linting (ZERO TOLERANCE)
	$(POETRY) run ruff check .

.PHONY: format
format: ## Format code
	$(POETRY) run ruff format .

.PHONY: type-check
type-check: ## Run type checking with Pyrefly (ZERO TOLERANCE)
	PYTHONPATH=$(SRC_DIR) $(POETRY) run pyrefly check .

.PHONY: security
security: ## Run security scanning
	$(POETRY) run bandit -r $(SRC_DIR) --skip B608
	$(POETRY) run pip-audit --ignore-vuln GHSA-mw26-5g2v-hqw3 --ignore-vuln GHSA-wj6h-64fc-37mp

.PHONY: fix
fix: ## Auto-fix issues
	$(POETRY) run ruff check . --fix
	$(POETRY) run ruff format .

# =============================================================================
# TESTING (MANDATORY - 100% COVERAGE)
# =============================================================================

.PHONY: test
test: ## Run tests with 100% coverage (MANDATORY)
	$(POETRY) run pytest -q --maxfail=10000 --cov=$(COV_DIR) --cov-report=term-missing:skip-covered --cov-fail-under=$(MIN_COVERAGE)

.PHONY: test-unit
test-unit: ## Run unit tests
	PYTHONPATH=$(SRC_DIR) $(POETRY) run pytest -m "not integration" -v

.PHONY: test-integration
test-integration: ## Run integration tests with Docker
	PYTHONPATH=$(SRC_DIR) $(POETRY) run pytest -m integration -v

.PHONY: test-e2e
test-e2e: ## Run end-to-end tests
	$(POETRY) run pytest $(TESTS_DIR) -m e2e -v

.PHONY: test-fast
test-fast: ## Run tests without coverage
	PYTHONPATH=$(SRC_DIR) $(POETRY) run pytest -v

.PHONY: coverage-html
coverage-html: ## Generate HTML coverage report
	PYTHONPATH=$(SRC_DIR) $(POETRY) run pytest --cov=$(COV_DIR) --cov-report=html

# =============================================================================
# BUILD & DISTRIBUTION
# =============================================================================

.PHONY: build
build: ## Build package
	$(POETRY) build

.PHONY: build-clean
build-clean: clean build ## Clean and build

# =============================================================================
# ORACLE OPERATIONS
# =============================================================================

.PHONY: oracle-test
oracle-test: ## Test Oracle connection
	PYTHONPATH=$(SRC_DIR) $(POETRY) run python -c "from flext_db_oracle import FlextDbOracleApi; print('Oracle test passed')"

.PHONY: oracle-connect
oracle-connect: ## Test Oracle connection
	PYTHONPATH=$(SRC_DIR) $(POETRY) run python -c "from flext_db_oracle.connection import test_connection; test_connection()"

.PHONY: oracle-schema
oracle-schema: ## Validate Oracle schema access
	PYTHONPATH=$(SRC_DIR) $(POETRY) run python -c "from flext_db_oracle.metadata import get_schema_info; print('Schema access OK')"

.PHONY: oracle-validate
oracle-validate: ## Validate Oracle configuration
	PYTHONPATH=$(SRC_DIR) $(POETRY) run python -c "from flext_db_oracle.config import FlextDbOracleSettings; print('Config valid')"

.PHONY: oracle-operations
oracle-operations: oracle-validate oracle-connect oracle-schema ## Run all Oracle validations

# =============================================================================
# DOCUMENTATION
# =============================================================================

.PHONY: docs
docs: ## Build documentation
	$(POETRY) run mkdocs build

.PHONY: docs-serve
docs-serve: ## Serve documentation
	$(POETRY) run mkdocs serve

# =============================================================================
# DEPENDENCIES
# =============================================================================

.PHONY: deps-update
deps-update: ## Update dependencies
	$(POETRY) update

.PHONY: deps-show
deps-show: ## Show dependency tree
	$(POETRY) show --tree

.PHONY: deps-audit
deps-audit: ## Audit dependencies
	$(POETRY) run pip-audit

# =============================================================================
# DEVELOPMENT
# =============================================================================

.PHONY: shell
shell: ## Open Python shell
	PYTHONPATH=$(SRC_DIR) $(POETRY) run python

.PHONY: pre-commit
pre-commit: ## Run pre-commit hooks
	$(POETRY) run pre-commit run --all-files

# =============================================================================
# MAINTENANCE
# =============================================================================

.PHONY: clean
clean: ## Clean build artifacts.PHONY: clean
clean: ## Clean build artifacts and cruft
	@echo "🧹 Cleaning $(PROJECT_NAME) - removing build artifacts, cache files, and cruft..."

	# Build artifacts
	rm -rf build/ dist/ *.egg-info/

	# Test artifacts
	rm -rf .pytest_cache/ htmlcov/ .coverage .coverage.* coverage.xml

	# Python cache directories
	rm -rf .mypy_cache/ .pyrefly_cache/ .ruff_cache/

	# Python bytecode
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type f -name "*.pyo" -delete 2>/dev/null || true

	# Temporary files
	find . -type f -name "*.tmp" -delete 2>/dev/null || true
	find . -type f -name "*.temp" -delete 2>/dev/null || true
	find . -type f -name ".DS_Store" -delete 2>/dev/null || true

	# Log files
	find . -type f -name "*.log" -delete 2>/dev/null || true

	# Editor files
	find . -type f -name ".vscode/settings.json" -delete 2>/dev/null || true
	find . -type f -name ".idea/" -type d -exec rm -rf {} + 2>/dev/null || true

	@echo "✅ $(PROJECT_NAME) cleanup complete"

.PHONY: clean-all
clean-all: clean ## Deep clean including venv
	rm -rf .venv/

.PHONY: reset
reset: clean-all setup ## Reset project

# =============================================================================
# DOCUMENTATION MAINTENANCE
# =============================================================================

.PHONY: docs-audit
docs-audit: ## Run comprehensive documentation audit
	PYTHONPATH=$(SRC_DIR) $(POETRY) run python scripts/docs_maintenance.py --audit

.PHONY: docs-validate
docs-validate: ## Run documentation validation checks
	PYTHONPATH=$(SRC_DIR) $(POETRY) run python scripts/docs_maintenance.py --validate

.PHONY: docs-optimize
docs-optimize: ## Run documentation content optimization
	PYTHONPATH=$(SRC_DIR) $(POETRY) run python scripts/docs_maintenance.py --optimize

.PHONY: docs-maintenance
docs-maintenance: ## Run complete documentation maintenance suite
	PYTHONPATH=$(SRC_DIR) $(POETRY) run python scripts/docs_maintenance.py --comprehensive

.PHONY: docs-health
docs-health: ## Quick documentation health check
	@echo "Documentation Health Check:"
	@echo "=========================="
	@echo "Files: $$(find . -name "*.md" | wc -l) markdown files"
	@echo "Status indicators: $$(grep -r "✅\|❌\|⚠️" docs/ 2>/dev/null | wc -l) found"
	@echo "External links: $$(grep -r "http" --include="*.md" . | wc -l) to validate"
	@echo "Reports directory: $$(ls docs/reports/ 2>/dev/null | wc -l || echo 0) reports generated"

# =============================================================================
# DIAGNOSTICS
# =============================================================================

.PHONY: diagnose
diagnose: ## Project diagnostics
	@echo "Python: $$(python --version)"
	@echo "Poetry: $$($(POETRY) --version)"
	@echo "Oracle Client: $$(PYTHONPATH=$(SRC_DIR) $(POETRY) run python -c 'import oracledb; print(oracledb.__version__)' 2>/dev/null || echo 'Not available')"
	@$(POETRY) env info

.PHONY: doctor
doctor: diagnose check docs-health ## Comprehensive health check

# =============================================================================

# =============================================================================

.PHONY: t l f tc c i v
t: test
l: lint
f: format
tc: type-check
c: clean
i: install
v: validate

# =============================================================================
# CONFIGURATION
# =============================================================================

.DEFAULT_GOAL := help
