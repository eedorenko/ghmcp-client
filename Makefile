# GitHub MCP Client - Makefile

.PHONY: help setup install test interactive example hello clean

help:
	@echo "GitHub MCP Client"
	@echo "=================="
	@echo ""
	@echo "Available commands:"
	@echo "  setup       - Run initial setup wizard"
	@echo "  install     - Install Python dependencies"
	@echo "  test        - Test the setup and connection"
	@echo "  interactive - Run client in interactive mode"
	@echo "  example     - Run usage example"
	@echo "  hello       - Run Hello World shell demo"
	@echo "  clean       - Clean up generated files"
	@echo ""
	@echo "Environment:"
	@echo "  GITHUB_TOKEN - Set your GitHub token (required)"

setup:
	@echo "🚀 Running setup wizard..."
	python setup.py

install:
	@echo "📦 Installing dependencies..."
	pip install -r requirements.txt

test:
	@echo "🧪 Testing setup..."
	python test_setup.py

interactive:
	@echo "💬 Starting interactive client..."
	python github_mcp_client.py --interactive

example:
	@echo "📝 Running example..."
	python example.py

hello:
	@echo "👋 Running Hello World shell demo..."
	./hello_world.sh

clean:
	@echo "🧹 Cleaning up..."
	rm -f .env
	rm -rf __pycache__
	rm -rf *.pyc
	@echo "✅ Cleaned up generated files"

# Development targets
dev-install:
	@echo "📦 Installing development dependencies..."
	pip install -r requirements.txt
	pip install pylint black isort mypy

lint:
	@echo "🔍 Running linting..."
	pylint github_mcp_client.py
	black --check github_mcp_client.py
	isort --check-only github_mcp_client.py

format:
	@echo "🎨 Formatting code..."
	black github_mcp_client.py example.py test_setup.py setup.py
	isort github_mcp_client.py example.py test_setup.py setup.py

check:
	@echo "✅ Running all checks..."
	@make lint
	@make test
