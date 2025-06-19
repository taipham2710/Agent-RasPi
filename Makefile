# Makefile for IoT Agent Management

.PHONY: help build start stop restart status logs clean dev-start dev-stop dev-logs test

# Default target
help:
	@echo "IoT Agent Management Commands:"
	@echo ""
	@echo "Production Commands:"
	@echo "  make build     - Build agent images"
	@echo "  make start     - Start production agents"
	@echo "  make stop      - Stop production agents"
	@echo "  make restart   - Restart production agents"
	@echo "  make status    - Show production agents status"
	@echo "  make logs      - Show production agents logs"
	@echo ""
	@echo "Development Commands:"
	@echo "  make dev-start  - Start development agents"
	@echo "  make dev-stop   - Stop development agents"
	@echo "  make dev-logs   - Show development agents logs"
	@echo ""
	@echo "Utility Commands:"
	@echo "  make clean      - Clean up all containers and images"
	@echo "  make test       - Run agent tests"
	@echo "  make install    - Install Python dependencies"

# Production commands
build:
	@echo "🔨 Building agent images..."
	docker-compose build

start:
	@echo "🚀 Starting production agents..."
	docker-compose up -d

stop:
	@echo "⏹️  Stopping production agents..."
	docker-compose down

restart: stop
	@echo "🔄 Restarting production agents..."
	docker-compose up -d

status:
	@echo "📊 Production agents status:"
	docker-compose ps
	@echo ""
	@echo "📈 System resources:"
	docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}"

logs:
	@echo "📝 Production agents logs:"
	docker-compose logs -f

# Development commands
dev-start:
	@echo "🚀 Starting development agents..."
	docker-compose -f docker-compose.dev.yml up -d

dev-stop:
	@echo "⏹️  Stopping development agents..."
	docker-compose -f docker-compose.dev.yml down

dev-restart: dev-stop
	@echo "🔄 Restarting development agents..."
	docker-compose -f docker-compose.dev.yml up -d

dev-status:
	@echo "📊 Development agents status:"
	docker-compose -f docker-compose.dev.yml ps

dev-logs:
	@echo "📝 Development agents logs:"
	docker-compose -f docker-compose.dev.yml logs -f

# Utility commands
clean:
	@echo "🧹 Cleaning up containers and images..."
	docker-compose down -v --rmi all
	docker-compose -f docker-compose.dev.yml down -v --rmi all
	docker system prune -f
	@echo "✅ Cleanup completed!"

test:
	@echo "🧪 Running agent tests..."
	python test_agent.py

install:
	@echo "📦 Installing Python dependencies..."
	pip install -r requirements.txt

# Quick commands for specific agents
logs-agent-01:
	@echo "📝 Agent 01 logs:"
	docker-compose logs -f agent-01

logs-agent-02:
	@echo "📝 Agent 02 logs:"
	docker-compose logs -f agent-02

logs-agent-03:
	@echo "📝 Agent 03 logs:"
	docker-compose logs -f agent-03

# Development quick commands
dev-logs-01:
	@echo "📝 Dev Agent 01 logs:"
	docker-compose -f docker-compose.dev.yml logs -f agent-dev-01

dev-logs-02:
	@echo "📝 Dev Agent 02 logs:"
	docker-compose -f docker-compose.dev.yml logs -f agent-dev-02

dev-logs-03:
	@echo "📝 Dev Agent 03 logs:"
	docker-compose -f docker-compose.dev.yml logs -f agent-dev-03 