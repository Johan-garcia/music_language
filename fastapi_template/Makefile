.PHONY: help install dev test lint format clean docker-build docker-up docker-down setup

# Default target
help:
	@echo "🎵 Music Recommendation API - Available Commands:"
	@echo ""
	@echo "Setup & Installation:"
	@echo "  setup          Setup API keys interactively"
	@echo "  install        Install dependencies"
	@echo "  dev            Run development server"
	@echo ""
	@echo "Testing & Quality:"
	@echo "  test           Run all tests"
	@echo "  test-auth      Run authentication tests"
	@echo "  test-music     Run music functionality tests"
	@echo "  test-admin     Run admin functionality tests"
	@echo "  lint           Run linting checks"
	@echo "  format         Format code with black and isort"
	@echo ""
	@echo "Docker:"
	@echo "  docker-build   Build Docker images"
	@echo "  docker-up      Start services with Docker Compose"
	@echo "  docker-down    Stop Docker services"
	@echo "  docker-logs    View Docker logs"
	@echo ""
	@echo "Utilities:"
	@echo "  clean          Clean cache and temporary files"
	@echo "  requirements   Update requirements.txt"

# Setup API keys
setup:
	@echo "🔧 Setting up API keys..."
	python setup_api_keys.py

# Install dependencies
install:
	@echo "📦 Installing dependencies..."
	pip install -r requirements.txt

# Development server
dev:
	@echo "🚀 Starting development server..."
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Testing
test:
	@echo "🧪 Running all tests..."
	pytest

test-auth:
	@echo "🔐 Running authentication tests..."
	pytest tests/test_auth.py -v

test-music:
	@echo "🎵 Running music tests..."
	pytest tests/test_music.py -v

test-admin:
	@echo "👑 Running admin tests..."
	pytest tests/test_admin.py -v

test-recommendations:
	@echo "🎯 Running recommendation tests..."
	pytest tests/test_recommendations.py -v

# Code quality
lint:
	@echo "🔍 Running linting checks..."
	flake8 app tests
	black --check app tests
	isort --check-only app tests

format:
	@echo "✨ Formatting code..."
	black app tests
	isort app tests

# Docker commands
docker-build:
	@echo "🐳 Building Docker images..."
	docker-compose build

docker-up:
	@echo "🚀 Starting Docker services..."
	docker-compose up -d

docker-down:
	@echo "🛑 Stopping Docker services..."
	docker-compose down

docker-logs:
	@echo "📋 Viewing Docker logs..."
	docker-compose logs -f

# Utilities
clean:
	@echo "🧹 Cleaning cache and temporary files..."
	find . -type d -name "__pycache__" -delete
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	rm -rf .coverage htmlcov/

requirements:
	@echo "📋 Updating requirements.txt..."
	pip freeze > requirements.txt

# Database migrations (if using Alembic)
migrate:
	@echo "🗄️ Running database migrations..."
	alembic upgrade head

migrate-create:
	@echo "📝 Creating new migration..."
	alembic revision --autogenerate -m "$(name)"