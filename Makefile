.PHONY: help install install-all install-backend install-frontend install-agent clean dev start stop

help:
	@echo "🧠 MNEMO Platform - Make Commands"
	@echo ""
	@echo "Installation:"
	@echo "  make install          - Install all dependencies (interactive)"
	@echo "  make install-all      - Install all dependencies (automatic)"
	@echo "  make install-backend  - Install backend dependencies only"
	@echo "  make install-frontend - Install frontend dependencies only"
	@echo "  make install-agent    - Install node agent dependencies only"
	@echo ""
	@echo "Development:"
	@echo "  make dev              - Start all services with Docker Compose"
	@echo "  make start            - Start all services in background"
	@echo "  make stop             - Stop all services"
	@echo "  make logs             - View Docker logs"
	@echo "  make init-db          - Initialize database with test data"
	@echo ""
	@echo "Backend:"
	@echo "  make backend          - Run backend server (development)"
	@echo "  make backend-test     - Run backend tests"
	@echo ""
	@echo "Frontend:"
	@echo "  make frontend         - Run frontend (development)"
	@echo "  make frontend-build   - Build frontend for production"
	@echo ""
	@echo "Node Agent:"
	@echo "  make agent            - Run node agent"
	@echo ""
	@echo "Cleanup:"
	@echo "  make clean            - Remove build artifacts and caches"
	@echo "  make clean-all        - Remove everything including dependencies"
	@echo ""

# Installation targets
install:
	@./install.sh

install-all:
	@echo "Installing all dependencies..."
	@cd backend && pip install -r requirements.txt
	@cd node-agent && pip install -r requirements.txt
	@cd frontend && npm install
	@echo "✅ All dependencies installed!"

install-backend:
	@echo "Installing backend dependencies..."
	@cd backend && pip install -r requirements.txt
	@echo "✅ Backend dependencies installed!"

install-frontend:
	@echo "Installing frontend dependencies..."
	@cd frontend && npm install
	@echo "✅ Frontend dependencies installed!"

install-agent:
	@echo "Installing node agent dependencies..."
	@cd node-agent && pip install -r requirements.txt
	@echo "✅ Node agent dependencies installed!"

# Docker Compose targets
dev:
	docker-compose up

start:
	docker-compose up -d
	@echo "✅ Services started!"
	@echo "Backend API: http://localhost:8000"
	@echo "API Docs:    http://localhost:8000/docs"
	@echo "Frontend:    http://localhost:3000"

stop:
	docker-compose down
	@echo "✅ Services stopped!"

logs:
	docker-compose logs -f

init-db:
	docker-compose exec backend python scripts/init_db.py

# Development servers
backend:
	@cd backend && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

backend-test:
	@cd backend && pytest tests/

frontend:
	@cd frontend && npm start

frontend-build:
	@cd frontend && npm run build

agent:
	@cd node-agent && python node_agent.py

# Cleanup targets
clean:
	@echo "Cleaning build artifacts..."
	@find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	@cd frontend && rm -rf build 2>/dev/null || true
	@echo "✅ Cleaned!"

clean-all: clean
	@echo "Removing all dependencies..."
	@rm -rf backend/venv node-agent/venv frontend/node_modules
	@docker-compose down -v
	@echo "✅ Everything cleaned!"
