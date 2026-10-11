.PHONY: help install test eval lint build dev docker-up docker-down clean

PYTHON ?= python3
VENV ?= backend/venv
PYTEST ?= $(VENV)/bin/pytest
VENV_PYTHON ?= $(VENV)/bin/python3

help: ## Show this help message
	@echo "Multi-Agent Workflow & Document Intelligence Orchestrator"
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-16s\033[0m %s\n", $$1, $$2}'

install: ## Setup backend virtual environment and install all dependencies
	@echo "Installing backend dependencies..."
	@test -d $(VENV) || $(PYTHON) -m venv $(VENV)
	@$(VENV)/bin/pip install --upgrade pip
	@$(VENV)/bin/pip install -r backend/requirements.txt
	@echo "Installing frontend dependencies..."
	@cd frontend && npm install

test: ## Run backend unit and integration test suite
	@echo "Running backend test suite..."
	@$(VENV_PYTHON) -m pytest backend/tests

eval: ## Run 25-case regression evaluation benchmark harness
	@echo "Running regression evaluation pipeline..."
	@$(VENV_PYTHON) eval_runner.py

lint: ## Lint frontend (oxlint) and check codebase
	@echo "Linting frontend..."
	@cd frontend && npm run lint

build: ## Build production frontend bundle
	@echo "Building frontend bundle..."
	@cd frontend && npm run build

dev-backend: ## Run FastAPI backend development server
	@$(VENV_PYTHON) -m uvicorn app.main:app --app-dir backend --host 0.0.0.0 --port 8000 --reload

dev-frontend: ## Run Vite frontend development server
	@cd frontend && npm run dev

dev: ## Launch backend and frontend development servers concurrently
	@echo "Starting backend on :8000 and frontend on :3000..."
	@$(MAKE) -j2 dev-backend dev-frontend

docker-up: ## Build and start full stack via Docker Compose
	@docker compose up --build -d
	@echo "Dashboard: http://localhost:3000 | API Docs: http://localhost:8000/docs"

docker-down: ## Stop all Docker Compose containers
	@docker compose down

clean: ## Clean cached build artifacts and bytecode
	@find . -type d -name "__pycache__" -exec rm -rf {} +
	@find . -type d -name ".pytest_cache" -exec rm -rf {} +
	@rm -rf frontend/dist
