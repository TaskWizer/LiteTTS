# Kokoro TTS Quality Assurance Makefile

.PHONY: help install-dev lint test format check-format security type-check all clean

help:
	@echo "Available targets:"
	@echo "  install-dev    Install development dependencies"
	@echo "  lint          Run all linting tools"
	@echo "  test          Run test suite with coverage"
	@echo "  format        Format code with black and isort"
	@echo "  check-format  Check code formatting without changes"
	@echo "  security      Run security checks with bandit"
	@echo "  type-check    Run type checking with mypy"
	@echo "  all           Run all quality checks"
	@echo "  clean         Clean up generated files"

install-dev:
	pip install black isort flake8 pylint mypy bandit pytest pytest-cov pre-commit

lint:
	@echo "Running linting tools..."
	flake8 --max-line-length=88 --extend-ignore=E203,W503 .
	pylint --max-line-length=88 --disable=C0114,C0115,C0116 *.py scripts/*.py || true

test:
	@echo "Running test suite..."
	pytest -v --cov=. --cov-report=term-missing --cov-report=html

format:
	@echo "Formatting code..."
	black --line-length=88 .
	isort --profile=black --line-length=88 .

check-format:
	@echo "Checking code formatting..."
	black --check --diff --line-length=88 .
	isort --check-only --diff --profile=black --line-length=88 .

security:
	@echo "Running security checks..."
	bandit -r . -f json -o bandit-report.json || true
	bandit -r . || true

type-check:
	@echo "Running type checks..."
	mypy --ignore-missing-imports . || true

all: check-format lint security type-check test
	@echo "All quality checks completed!"

clean:
	@echo "Cleaning up..."
	rm -rf .pytest_cache/
	rm -rf htmlcov/
	rm -rf .coverage
	rm -rf coverage.json
	rm -rf bandit-report.json
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
