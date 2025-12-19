# flext-db-oracle - Oracle Database Utilities
PROJECT_NAME := flext-db-oracle
COV_DIR := flext_db_oracle
MIN_COVERAGE := 90

include ../base.mk

# === PROJECT-SPECIFIC TARGETS ===
.PHONY: test-unit test-integration build shell

.DEFAULT_GOAL := help
