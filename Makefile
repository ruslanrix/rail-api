SHELL := /bin/bash
.DEFAULT_GOAL := help

PY := poetry run
APP := app.main:app

HOST ?= 127.0.0.1
PORT ?= 8000

.PHONY: help install dev run test lint fmt typecheck health curl-add curl-mul clean

help: ## Show available commands
	@grep -E '^[a-zA-Z_-]+:.*## ' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*## "}; {printf "\033[36m%-14s\033[0m %s\n", $$1, $$2}'

install: ## Install dependencies
	poetry install

dev: ## Run API locally (reload)
	$(PY) uvicorn $(APP) --reload --host $(HOST) --port $(PORT)

run: ## Run API locally (no reload)
	$(PY) uvicorn $(APP) --host $(HOST) --port $(PORT)

test: ## Run tests
	$(PY) pytest -q

lint: ## Lint (requires ruff)
	$(PY) ruff check .

fmt: ## Format (requires ruff)
	$(PY) ruff format .

typecheck: ## Typecheck (optional, requires mypy)
	$(PY) mypy .

health: ## Check /health on local server
	curl -fsS "http://$(HOST):$(PORT)/health" && echo

curl-add: ## Call /add?a=2&b=3 on local server
	curl -fsS "http://$(HOST):$(PORT)/add?a=2&b=3" && echo

curl-mul: ## Call /mul?a=2&b=3 on local server
	curl -fsS "http://$(HOST):$(PORT)/mul?a=2&b=3" && echo

clean: ## Remove caches
	rm -rf .pytest_cache .ruff_cache __pycache__ **/__pycache__