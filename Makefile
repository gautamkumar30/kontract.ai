# Contract Drift Detector - Makefile
# Comprehensive development and deployment commands

.PHONY: help setup install docker-build docker-up docker-down docker-restart docker-logs docker-logs-db docker-logs-n8n docker-status clean test lint format db-migrate db-reset dev-backend dev-frontend

# Default target
.DEFAULT_GOAL := help

# Colors for output
BLUE := \033[0;34m
GREEN := \033[0;32m
YELLOW := \033[1;33m
RED := \033[0;31m
NC := \033[0m # No Color

##@ Help

help: ## Display this help message
	@echo "$(BLUE)Contract Drift Detector - Available Commands$(NC)"
	@echo ""
	@awk 'BEGIN {FS = ":.*##"; printf "Usage:\n  make $(GREEN)<target>$(NC)\n"} /^[a-zA-Z_0-9-]+:.*?##/ { printf "  $(GREEN)%-20s$(NC) %s\n", $$1, $$2 } /^##@/ { printf "\n$(BLUE)%s$(NC)\n", substr($$0, 5) } ' $(MAKEFILE_LIST)

##@ Setup & Installation

setup: ## Initial project setup (copy .env, install dependencies)
	@echo "$(BLUE)Setting up project...$(NC)"
	@if [ ! -f .env ]; then \
		cp .env.example .env; \
		echo "$(GREEN)✓ Created .env file from .env.example$(NC)"; \
		echo "$(YELLOW)⚠ Please update .env with your API keys!$(NC)"; \
	else \
		echo "$(YELLOW).env file already exists$(NC)"; \
	fi
	@echo "$(GREEN)✓ Setup complete!$(NC)"

install: ## Install all dependencies (backend + frontend)
	@echo "$(BLUE)Installing backend dependencies...$(NC)"
	cd backend && pip install -r requirements.txt
	@echo "$(BLUE)Installing frontend dependencies...$(NC)"
	cd frontend && pnpm install
	@echo "$(GREEN)✓ All dependencies installed!$(NC)"

install-backend: ## Install backend dependencies only
	@echo "$(BLUE)Installing backend dependencies...$(NC)"
	cd backend && pip install -r requirements.txt
	@echo "$(GREEN)✓ Backend dependencies installed!$(NC)"

install-frontend: ## Install frontend dependencies only
	@echo "$(BLUE)Installing frontend dependencies...$(NC)"
	cd frontend && pnpm install
	@echo "$(GREEN)✓ Frontend dependencies installed!$(NC)"

##@ Docker Commands

docker-build: ## Build all Docker containers
	@echo "$(BLUE)Building Docker containers...$(NC)"
	sudo docker compose build
	@echo "$(GREEN)✓ Build complete!$(NC)"

# Backend and frontend are now run locally, not in Docker

docker-up: ## Start Docker services (PostgreSQL + n8n)
	@echo "$(BLUE)Starting Docker services...$(NC)"
	sudo docker compose up -d
	@echo "$(GREEN)✓ Docker services started!$(NC)"
	@echo ""
	@echo "$(BLUE)Services available at:$(NC)"
	@echo "  n8n:       $(GREEN)http://localhost:5678$(NC) (admin/admin123)"
	@echo "  Database:  $(GREEN)localhost:5432$(NC)"
	@echo ""
	@echo "$(YELLOW)Note: Run backend and frontend locally with:$(NC)"
	@echo "  Backend:  $(GREEN)make dev-backend$(NC)"
	@echo "  Frontend: $(GREEN)make dev-frontend$(NC)"

docker-down: ## Stop all services
	@echo "$(BLUE)Stopping all services...$(NC)"
	sudo docker compose down
	@echo "$(GREEN)✓ All services stopped!$(NC)"

docker-restart: ## Restart all services
	@echo "$(BLUE)Restarting all services...$(NC)"
	sudo docker compose restart
	@echo "$(GREEN)✓ All services restarted!$(NC)"

# Backend and frontend run locally - use Ctrl+C and restart manually

##@ Logs & Monitoring

docker-logs: ## View logs from all services
	sudo docker compose logs -f

# Backend and frontend logs are in your terminal where you ran dev-backend/dev-frontend

docker-logs-db: ## View database logs
	sudo docker compose logs -f postgres

docker-logs-n8n: ## View n8n logs
	sudo docker compose logs -f n8n

docker-status: ## Show status of all services
	@echo "$(BLUE)Service Status:$(NC)"
	@sudo docker compose ps

##@ Database Commands

db-migrate: ## Run database migrations
	@echo "$(BLUE)Running database migrations...$(NC)"
	cd backend && alembic upgrade head
	@echo "$(GREEN)✓ Migrations complete!$(NC)"

db-migrate-create: ## Create a new migration (usage: make db-migrate-create MSG="description")
	@if [ -z "$(MSG)" ]; then \
		echo "$(RED)Error: Please provide a message$(NC)"; \
		echo "Usage: make db-migrate-create MSG=\"your migration description\""; \
		exit 1; \
	fi
	@echo "$(BLUE)Creating new migration: $(MSG)$(NC)"
	cd backend && alembic revision --autogenerate -m "$(MSG)"
	@echo "$(GREEN)✓ Migration created!$(NC)"

db-downgrade: ## Rollback last migration
	@echo "$(BLUE)Rolling back last migration...$(NC)"
	cd backend && alembic downgrade -1
	@echo "$(GREEN)✓ Migration rolled back!$(NC)"

db-reset: ## Reset database (WARNING: destroys all data)
	@echo "$(RED)WARNING: This will destroy all data!$(NC)"
	@read -p "Are you sure? [y/N] " -n 1 -r; \
	echo; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		echo "$(BLUE)Resetting database...$(NC)"; \
		sudo docker compose down -v; \
		sudo docker compose up -d; \
		sleep 5; \
		cd backend && alembic upgrade head; \
		echo "$(GREEN)✓ Database reset complete!$(NC)"; \
	else \
		echo "$(YELLOW)Cancelled$(NC)"; \
	fi

db-shell: ## Open PostgreSQL shell
	@echo "$(BLUE)Opening database shell...$(NC)"
	sudo docker compose exec postgres psql -U postgres -d contract_drifter

##@ Development Commands

dev: ## Start development environment (all services)
	@echo "$(BLUE)Starting development environment...$(NC)"
	@make docker-up
	@make db-migrate

dev-backend: ## Run backend in development mode (local)
	@echo "$(BLUE)Starting backend development server...$(NC)"
	cd backend && . venv/bin/activate && uvicorn main:app --reload --host 0.0.0.0 --port 8000

stop-backend: ## Stop backend development server
	@echo "$(BLUE)Stopping backend server...$(NC)"
	@lsof -ti:8000 | xargs kill -9 2>/dev/null || echo "$(YELLOW)No backend server running on port 8000$(NC)"
	@echo "$(GREEN)✓ Backend stopped$(NC)"

dev-frontend: ## Run frontend in development mode (local)
	@echo "$(BLUE)Starting frontend development server...$(NC)"
	cd frontend && pnpm dev

stop-frontend: ## Stop frontend development server
	@echo "$(BLUE)Stopping frontend server...$(NC)"
	@lsof -ti:3000 | xargs kill -9 2>/dev/null || echo "$(YELLOW)No frontend server running on port 3000$(NC)"
	@echo "$(GREEN)✓ Frontend stopped$(NC)"

dev-local: ## Run both backend and frontend locally (not in Docker)
	@echo "$(BLUE)Starting local development...$(NC)"
	@echo "$(YELLOW)Note: Make sure PostgreSQL and n8n are running via Docker$(NC)"
	@make -j2 dev-backend dev-frontend

stop-all: ## Stop both backend and frontend servers
	@echo "$(BLUE)Stopping all local servers...$(NC)"
	@make stop-backend
	@make stop-frontend
	@echo "$(GREEN)✓ All servers stopped$(NC)"

##@ Testing Commands

test: ## Run all tests
	@echo "$(BLUE)Running all tests...$(NC)"
	@make test-backend
	@make test-frontend

test-backend: ## Run backend tests
	@echo "$(BLUE)Running backend tests...$(NC)"
	cd backend && pytest
	@echo "$(GREEN)✓ Backend tests complete!$(NC)"

test-frontend: ## Run frontend tests
	@echo "$(BLUE)Running frontend tests...$(NC)"
	cd frontend && pnpm test
	@echo "$(GREEN)✓ Frontend tests complete!$(NC)"

test-coverage: ## Run tests with coverage report
	@echo "$(BLUE)Running tests with coverage...$(NC)"
	cd backend && pytest --cov=. --cov-report=html
	@echo "$(GREEN)✓ Coverage report generated in backend/htmlcov/$(NC)"

##@ Code Quality

lint: ## Run linters on all code
	@echo "$(BLUE)Running linters...$(NC)"
	@make lint-backend
	@make lint-frontend

lint-backend: ## Lint backend code
	@echo "$(BLUE)Linting backend...$(NC)"
	cd backend && flake8 . --max-line-length=120 --exclude=venv,alembic
	@echo "$(GREEN)✓ Backend linting complete!$(NC)"

lint-frontend: ## Lint frontend code
	@echo "$(BLUE)Linting frontend...$(NC)"
	cd frontend && pnpm lint
	@echo "$(GREEN)✓ Frontend linting complete!$(NC)"

format: ## Format all code
	@echo "$(BLUE)Formatting code...$(NC)"
	@make format-backend
	@make format-frontend

format-backend: ## Format backend code with black
	@echo "$(BLUE)Formatting backend...$(NC)"
	cd backend && black . --exclude=venv
	@echo "$(GREEN)✓ Backend formatting complete!$(NC)"

format-frontend: ## Format frontend code
	@echo "$(BLUE)Formatting frontend...$(NC)"
	cd frontend && pnpm format || echo "$(YELLOW)No format script defined$(NC)"

##@ Cleanup Commands

clean: ## Clean up temporary files and caches
	@echo "$(BLUE)Cleaning up...$(NC)"
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".next" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "node_modules" -exec rm -rf {} + 2>/dev/null || true
	@echo "$(GREEN)✓ Cleanup complete!$(NC)"

clean-docker: ## Remove all Docker containers, volumes, and images
	@echo "$(RED)WARNING: This will remove all Docker data!$(NC)"
	@read -p "Are you sure? [y/N] " -n 1 -r; \
	echo; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		echo "$(BLUE)Cleaning Docker...$(NC)"; \
		sudo docker compose down -v --rmi all; \
		echo "$(GREEN)✓ Docker cleanup complete!$(NC)"; \
	else \
		echo "$(YELLOW)Cancelled$(NC)"; \
	fi

##@ Production Commands

prod-build: ## Build for production
	@echo "$(BLUE)Building for production...$(NC)"
	cd frontend && pnpm build
	@echo "$(GREEN)✓ Production build complete!$(NC)"

prod-start: ## Start production server
	@echo "$(BLUE)Starting production server...$(NC)"
	cd frontend && pnpm start

##@ Utility Commands

# Backend and frontend run locally - just open a new terminal

health: ## Check health of all services
	@echo "$(BLUE)Checking service health...$(NC)"
	@echo ""
	@echo "$(BLUE)Backend API (if running):$(NC)"
	@curl -s http://localhost:8000/health | python3 -m json.tool 2>/dev/null || echo "$(YELLOW)Backend not running (start with: make dev-backend)$(NC)"
	@echo ""
	@echo "$(BLUE)Frontend (if running):$(NC)"
	@curl -s -o /dev/null -w "Status: %{http_code}\n" http://localhost:3000 2>/dev/null || echo "$(YELLOW)Frontend not running (start with: make dev-frontend)$(NC)"
	@echo ""
	@echo "$(BLUE)Database:$(NC)"
	@sudo docker compose exec postgres pg_isready -U postgres || echo "$(RED)✗ Database not responding$(NC)"

backup-db: ## Backup database to file
	@echo "$(BLUE)Backing up database...$(NC)"
	@mkdir -p backups
	@sudo docker compose exec -T postgres pg_dump -U postgres contract_drifter > backups/backup_$$(date +%Y%m%d_%H%M%S).sql
	@echo "$(GREEN)✓ Database backed up to backups/$(NC)"

restore-db: ## Restore database from backup (usage: make restore-db FILE=backups/backup.sql)
	@if [ -z "$(FILE)" ]; then \
		echo "$(RED)Error: Please provide a backup file$(NC)"; \
		echo "Usage: make restore-db FILE=backups/backup_20231216_120000.sql"; \
		exit 1; \
	fi
	@echo "$(BLUE)Restoring database from $(FILE)...$(NC)"
	@sudo docker compose exec -T postgres psql -U postgres -d contract_drifter < $(FILE)
	@echo "$(GREEN)✓ Database restored!$(NC)"

##@ Quick Start

quickstart: ## Complete setup and start (for first time)
	@echo "$(BLUE)========================================$(NC)"
	@echo "$(BLUE)Contract Drift Detector - Quick Start$(NC)"
	@echo "$(BLUE)========================================$(NC)"
	@echo ""
	@make setup
	@echo ""
	@make docker-up
	@echo ""
	@sleep 5
	@make db-migrate
	@echo ""
	@echo "$(GREEN)========================================$(NC)"
	@echo "$(GREEN)✓ Docker Setup Complete!$(NC)"
	@echo "$(GREEN)========================================$(NC)"
	@echo ""
	@echo "$(BLUE)Docker services running:$(NC)"
	@echo "  n8n:       $(GREEN)http://localhost:5678$(NC) (admin/admin123)"
	@echo "  Database:  $(GREEN)localhost:5432$(NC)"
	@echo ""
	@echo "$(YELLOW)Next steps:$(NC)"
	@echo "  1. Update .env file with API keys"
	@echo "  2. Start backend:  $(GREEN)make dev-backend$(NC)"
	@echo "  3. Start frontend: $(GREEN)make dev-frontend$(NC) (in new terminal)"
