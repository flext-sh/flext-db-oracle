# flext-db-oracle - Oracle Database Utilities
PROJECT_NAME := flext-db-oracle
include ../base.mk

# === PROJECT-SPECIFIC TARGETS ===
.PHONY: test-unit test-integration build shell

.DEFAULT_GOAL := help
