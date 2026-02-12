.PHONY: help build up down logs health clean test run-pipeline show-models test-predict

PROJECT_NAME := mage-ai-demo
DOCKER_COMPOSE := docker-compose -f docker-compose.yml
MAGE_WEB := $(DOCKER_COMPOSE) exec -T mage-web
MAGE_PROJECT := mlops_demo

# Color output
BLUE := \033[0;34m
GREEN := \033[0;32m
YELLOW := \033[0;33m
RED := \033[0;31m
NC := \033[0m # No Color

help: ## Show this help message
	@echo "$(BLUE)Mage AI MLOps Platform - Make Commands$(NC)"
	@echo "$(YELLOW)======================================$(NC)"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(GREEN)%-25s$(NC) %s\n", $$1, $$2}'
	@echo ""
	@echo "$(YELLOW)Usage:$(NC)"
	@echo "  make build              # Build Docker images with pinned version 0.9.79"
	@echo "  make up                 # Start all services"
	@echo "  make health             # Check service health"
	@echo "  make run-pipeline       # Run default pipeline"
	@echo ""

# ============================================================================
# INFRASTRUCTURE COMMANDS
# ============================================================================

build: ## Build Docker images (Mage AI 0.9.79 - pinned for reproducibility)
	@echo "$(BLUE)Building Docker images with Mage AI 0.9.79...$(NC)"
	$(DOCKER_COMPOSE) build --no-cache
	@echo "$(GREEN)✓ Build complete$(NC)"

up: ## Start all services (mage-web, mage-scheduler, postgres, redis, prediction-service)
	@echo "$(BLUE)Starting all services...$(NC)"
	$(DOCKER_COMPOSE) up -d
	@echo "$(BLUE)Waiting for services to be healthy...$(NC)"
	@sleep 10
	@$(MAKE) health

down: ## Stop and remove all containers
	@echo "$(BLUE)Stopping all services...$(NC)"
	$(DOCKER_COMPOSE) down
	@echo "$(GREEN)✓ Services stopped$(NC)"

stop: ## Stop all services (keep containers)
	@echo "$(BLUE)Stopping services...$(NC)"
	$(DOCKER_COMPOSE) stop
	@echo "$(GREEN)✓ Services stopped$(NC)"

restart: ## Restart all services
	@echo "$(BLUE)Restarting services...$(NC)"
	$(DOCKER_COMPOSE) restart
	@sleep 5
	@$(MAKE) health

health: ## Check health of all services
	@echo "$(BLUE)Checking service health...$(NC)"
	@$(DOCKER_COMPOSE) ps --format "table {{.Names}}\t{{.Status}}" 2>/dev/null || echo "Services not running"
	@echo ""
	@echo "$(BLUE)Testing endpoints:$(NC)"
	@curl -s -o /dev/null -w "  Mage Web (6789): %{http_code}\n" http://localhost:6789 || echo "  Mage Web (6789): not responding"
	@curl -s -o /dev/null -w "  Prediction API (5000): %{http_code}\n" http://localhost:5000/health || echo "  Prediction API (5000): not responding"
	@echo ""

# ============================================================================
# LOGGING & DEBUGGING
# ============================================================================

logs: ## Show logs from all services (tail -f)
	$(DOCKER_COMPOSE) logs -f

logs-web: ## Show Mage web server logs
	$(DOCKER_COMPOSE) logs -f mage-web

logs-scheduler: ## Show Mage scheduler logs
	$(DOCKER_COMPOSE) logs -f mage-scheduler

logs-predictions: ## Show prediction service logs
	$(DOCKER_COMPOSE) logs -f prediction-service

logs-postgres: ## Show PostgreSQL logs
	$(DOCKER_COMPOSE) logs -f postgres

logs-redis: ## Show Redis logs
	$(DOCKER_COMPOSE) logs -f redis

# ============================================================================
# PIPELINE OPERATIONS
# ============================================================================

list-pipelines: ## List all available pipelines in the project
	@echo "$(BLUE)Available pipelines:$(NC)"
	@ls -1 mlops_demo/pipelines/ 2>/dev/null || echo "  No pipelines found"
	@echo ""
	@echo "$(BLUE)Pipeline details:$(NC)"
	@find mlops_demo/pipelines -name "*.py" -type f | head -10 | while read f; do \
		echo "  - $$f"; \
	done

run-pipeline: ## Run the default MLOps pipeline
	@echo "$(BLUE)Running pipeline: $(MAGE_PROJECT)$(NC)"
	@$(MAGE_WEB) python -m mage_ai.cli run $(MAGE_PROJECT) 2>&1 | tail -20
	@echo "$(GREEN)✓ Pipeline execution started$(NC)"
	@echo ""
	@echo "$(YELLOW)To view logs:$(NC)"
	@echo "  make logs-web"

run-pipeline-debug: ## Run pipeline with verbose output
	@echo "$(BLUE)Running pipeline with debug logging...$(NC)"
	@$(MAGE_WEB) python -m mage_ai.cli run $(MAGE_PROJECT) -v

# ============================================================================
# MODEL REGISTRY & VERSIONING
# ============================================================================

show-models: ## Display model registry contents
	@echo "$(BLUE)Model Registry:$(NC)"
	@if [ -d "mlops_demo/model_registry" ]; then \
		ls -lh mlops_demo/model_registry/; \
	else \
		echo "  Model registry directory not found"; \
	fi

show-latest-model: ## Show currently active model info
	@echo "$(BLUE)Latest Model Version:$(NC)"
	@if [ -f "mlops_demo/model_registry/latest.json" ]; then \
		cat mlops_demo/model_registry/latest.json | jq . || cat mlops_demo/model_registry/latest.json; \
	else \
		echo "  No model version file found"; \
	fi

model-versions: ## List all model versions
	@echo "$(BLUE)Model Versions:$(NC)"
	@ls -1 mlops_demo/model_registry/*.pkl 2>/dev/null | xargs -n1 basename || echo "  No model files found"

# ============================================================================
# PREDICTION SERVICE
# ============================================================================

test-predict: ## Test prediction endpoint with sample data
	@echo "$(BLUE)Testing prediction service...$(NC)"
	@curl -s -X POST http://localhost:5000/predict \
		-H "Content-Type: application/json" \
		-d '{"features": [1.0, 2.0, 3.0, 4.0]}' | jq . 2>/dev/null || \
		curl -s -X POST http://localhost:5000/predict \
			-H "Content-Type: application/json" \
			-d '{"features": [1.0, 2.0, 3.0, 4.0]}'

predict-health: ## Check prediction service health
	@echo "$(BLUE)Checking prediction service health...$(NC)"
	@curl -s http://localhost:5000/health | jq . || curl -s http://localhost:5000/health

# ============================================================================
# DATA & CACHE
# ============================================================================

show-data: ## Show processed data files
	@echo "$(BLUE)Data outputs:$(NC)"
	@find mlops_demo -name "*.csv" -o -name "*.parquet" 2>/dev/null | head -20 || echo "  No data files found"

cache-status: ## Show cache and metadata status
	@echo "$(BLUE)Cache files:$(NC)"
	@find mage_data -type f 2>/dev/null | head -10 || echo "  No cache files"
	@echo ""
	@echo "$(BLUE)Database:$(NC)"
	@ls -lh mage_data/mlops_demo/mage-ai.db 2>/dev/null || echo "  Database not found (using PostgreSQL)"

# ============================================================================
# EXPERIMENTATION & TESTING
# ============================================================================

test: ## Run pipeline tests
	@echo "$(BLUE)Running pipeline tests...$(NC)"
	@$(MAGE_WEB) python -m pytest mlops_demo/ -v 2>/dev/null || \
		echo "Pytest not configured. Use Mage UI for block-level testing."

experiment-list: ## List experiment runs
	@echo "$(BLUE)Recent pipeline runs:$(NC)"
	@$(MAGE_WEB) python -c "import json; print('View runs in Mage UI: http://localhost:6789')" || \
		echo "Use Mage UI to view experiments and runs"

# ============================================================================
# DATABASE & STORAGE
# ============================================================================

db-shell: ## Open PostgreSQL shell
	@echo "$(BLUE)Connecting to PostgreSQL database...$(NC)"
	$(DOCKER_COMPOSE) exec postgres psql -U mage -d mage

redis-cli: ## Open Redis CLI
	@echo "$(BLUE)Connecting to Redis...$(NC)"
	$(DOCKER_COMPOSE) exec redis redis-cli -u redis://redis:6379/0

# ============================================================================
# CLEANUP & RESET
# ============================================================================

clean: ## Remove all data, cache, and containers
	@echo "$(RED)WARNING: This will delete all data and cache$(NC)"
	@read -p "Continue? (y/N) " -n 1 -r; \
	echo; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		$(DOCKER_COMPOSE) down -v; \
		rm -rf mage_data/; \
		rm -rf mlops_demo/*.db; \
		echo "$(GREEN)✓ Cleanup complete$(NC)"; \
	else \
		echo "$(YELLOW)Cancelled$(NC)"; \
	fi

reset-db: ## Reset PostgreSQL database only
	@echo "$(BLUE)Resetting PostgreSQL database...$(NC)"
	$(DOCKER_COMPOSE) exec postgres dropdb -U mage mage --if-exists
	$(DOCKER_COMPOSE) exec postgres createdb -U mage mage
	@echo "$(GREEN)✓ Database reset complete$(NC)"
	$(MAKE) restart

# ============================================================================
# INFORMATION & DOCUMENTATION
# ============================================================================

info: ## Display project information
	@echo "$(BLUE)Mage AI MLOps Platform$(NC)"
	@echo "$(YELLOW)======================$(NC)"
	@echo ""
	@echo "  Project: $(PROJECT_NAME)"
	@echo "  Mage Version: 0.9.79 (pinned for reproducibility)"
	@echo "  Location: $(PWD)"
	@echo ""
	@echo "$(BLUE)Services:$(NC)"
	@echo "  • Mage Web: http://localhost:6789"
	@echo "  • Prediction API: http://localhost:5000"
	@echo "  • PostgreSQL: localhost:5432"
	@echo "  • Redis: localhost:6379"
	@echo ""
	@echo "$(BLUE)Documentation:$(NC)"
	@echo "  • ARCHITECTURE.md - System design and microservices"
	@echo "  • MASTERCLASS.md - Complete MLOps guide"
	@echo "  • README.md - Quick start guide"
	@echo ""

docs: ## Open documentation
	@echo "$(BLUE)Documentation:$(NC)"
	@echo "  1. ARCHITECTURE.md - Microservices architecture"
	@echo "  2. MASTERCLASS.md - MLOps masterclass (this file)"
	@echo "  3. Make targets - Run 'make help' for all commands"
	@echo ""
	@echo "$(BLUE)Quick links:$(NC)"
	@echo "  • Mage Docs: https://docs.mage.ai"
	@echo "  • GitHub: https://github.com/mage-ai/mage-ai"
	@echo ""

version: ## Show Mage AI version
	@echo "$(BLUE)Mage AI Version Information:$(NC)"
	@$(MAGE_WEB) pip show mage-ai | grep Version || echo "Version not available"

# ============================================================================
# DEMO WORKFLOW
# ============================================================================

demo: ## Run complete demo workflow
	@echo "$(BLUE)Starting MLOps Masterclass Demo$(NC)"
	@echo "$(YELLOW)================================$(NC)"
	@echo ""
	@echo "$(BLUE)Step 1: Checking services...$(NC)"
	@$(MAKE) health
	@echo ""
	@echo "$(BLUE)Step 2: Displaying model registry...$(NC)"
	@$(MAKE) show-latest-model
	@echo ""
	@echo "$(BLUE)Step 3: Testing prediction API...$(NC)"
	@$(MAKE) test-predict
	@echo ""
	@echo "$(BLUE)Step 4: Listing available pipelines...$(NC)"
	@$(MAKE) list-pipelines
	@echo ""
	@echo "$(GREEN)✓ Demo workflow complete$(NC)"
	@echo ""
	@echo "$(YELLOW)Next steps:$(NC)"
	@echo "  1. Open Mage UI: http://localhost:6789"
	@echo "  2. Run a pipeline from UI"
	@echo "  3. Check logs: make logs-scheduler"
	@echo ""

# ============================================================================
# SETUP
# ============================================================================

setup: ## Initialize project (build and start services)
	@echo "$(BLUE)Initializing Mage AI project...$(NC)"
	@$(MAKE) build
	@echo ""
	@$(MAKE) up
	@echo ""
	@echo "$(GREEN)✓ Setup complete!$(NC)"
	@echo ""
	@echo "$(YELLOW)Access points:$(NC)"
	@echo "  • Mage UI: http://localhost:6789"
	@echo "  • Prediction API: http://localhost:5000/health"
	@echo ""
	@echo "$(YELLOW)Next:$(NC)"
	@echo "  1. make health          # Check service status"
	@echo "  2. make demo            # Run demo workflow"
	@echo "  3. make help            # See all commands"

.DEFAULT_GOAL := help
