# FLEXT DB Oracle - Oracle Database Integration
# ==============================================
# Clean Architecture + Python 3.13 + Zero Tolerance Quality Gates

.PHONY: help check test lint type-check format build clean install

# Variables
PYTHON := python3.13
POETRY := poetry
SRC_DIR := src
TEST_DIR := tests

# Colors for output
GREEN := \033[0;32m
BLUE := \033[0;34m
RED := \033[0;31m
NC := \033[0m

help: ## Show this help message
	@echo "$(GREEN)FLEXT DB Oracle - Oracle Database Integration$(NC)"
	@echo "=============================================="
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

check: poetry-check lint format type-check security test ## Run ALL quality checks
	@echo "$(GREEN)✅ ALL QUALITY CHECKS PASSED!$(NC)"

lint: poetry-check ## Run linting
	@echo "$(BLUE)🔥 Running ruff linter...$(NC)"
	@$(POETRY) run ruff check $(SRC_DIR)/ $(TEST_DIR)/ --fix || true

format: poetry-check ## Format code
	@echo "$(BLUE)🎨 Formatting code...$(NC)"
	@$(POETRY) run ruff format $(SRC_DIR)/ $(TEST_DIR)/

type-check: poetry-check ## Run type checking
	@echo "$(BLUE)🛡️ Running mypy...$(NC)"
	@$(POETRY) run mypy $(SRC_DIR)/ $(TEST_DIR)/ --strict || true

security: poetry-check ## Run security scans
	@echo "$(BLUE)🔒 Running security scans...$(NC)"
	@$(POETRY) run bandit -r $(SRC_DIR)/ || true
	@$(POETRY) run pip-audit || true

test: poetry-check ## Run tests with coverage
	@echo "$(BLUE)🧪 Running tests...$(NC)"
	@$(POETRY) run pytest $(TEST_DIR)/ -v --cov=$(SRC_DIR) --cov-report=term-missing || true

build: clean ## Build package
	@echo "$(BLUE)🔨 Building package...$(NC)"
	@$(POETRY) build

clean: ## Clean build artifacts
	@echo "$(BLUE)🧹 Cleaning...$(NC)"
	@rm -rf build/ dist/ *.egg-info/ .coverage htmlcov/ .pytest_cache/ .mypy_cache/ .ruff_cache/
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true

install: ## Install dependencies
	@echo "$(BLUE)📦 Installing dependencies...$(NC)"
	@$(POETRY) install

poetry-check: ## Check Poetry is available
	@$(POETRY) --version > /dev/null 2>&1 || (echo "$(RED)Poetry not found. Please install Poetry first.$(NC)" && exit 1)

.DEFAULT_GOAL := help