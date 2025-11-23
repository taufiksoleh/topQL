# Makefile for TopQL - Learning SQL Database

.PHONY: help install test lint format clean coverage run

# Default target
help:
	@echo "TopQL - Makefile Commands"
	@echo "=========================="
	@echo ""
	@echo "Development:"
	@echo "  make install        - Install development dependencies"
	@echo "  make test           - Run all unit tests"
	@echo "  make coverage       - Run tests with coverage report"
	@echo "  make lint           - Run all linters"
	@echo "  make format         - Format code with black and isort"
	@echo "  make run            - Run example queries"
	@echo ""
	@echo "Linting (individual):"
	@echo "  make flake8         - Run flake8 linter"
	@echo "  make pylint         - Run pylint linter"
	@echo "  make black-check    - Check code formatting with black"
	@echo "  make isort-check    - Check import sorting with isort"
	@echo ""
	@echo "Cleanup:"
	@echo "  make clean          - Remove generated files and cache"
	@echo ""

# Install development dependencies
install:
	pip install --upgrade pip
	pip install -r requirements-dev.txt

# Run all tests
test:
	python -m unittest test_topql -v

# Run tests with pytest
test-pytest:
	pytest test_topql.py -v

# Run tests with coverage
coverage:
	coverage run -m unittest test_topql
	coverage report -m
	coverage html
	@echo ""
	@echo "Coverage report generated in htmlcov/index.html"

# Run all linters
lint: flake8 pylint black-check isort-check
	@echo ""
	@echo "✓ All linting checks completed!"

# Run flake8
flake8:
	@echo "Running Flake8..."
	flake8 topql.py examples.py test_topql.py

# Run pylint
pylint:
	@echo "Running Pylint..."
	pylint topql.py examples.py test_topql.py --exit-zero

# Check code formatting with black
black-check:
	@echo "Checking code formatting with Black..."
	black --check --diff topql.py examples.py test_topql.py

# Check import sorting
isort-check:
	@echo "Checking import sorting with isort..."
	isort --check-only --diff topql.py examples.py test_topql.py

# Format code with black
format:
	@echo "Formatting code with Black..."
	black topql.py examples.py test_topql.py
	@echo "Sorting imports with isort..."
	isort topql.py examples.py test_topql.py
	@echo ""
	@echo "✓ Code formatted successfully!"

# Run the example script
run:
	python examples.py

# Run quick database test
quick-test:
	@python -c "\
	from topql import Database; \
	db = Database(); \
	db.execute('CREATE TABLE test (id INT, name VARCHAR(50))'); \
	db.execute('INSERT INTO test VALUES (1, \"Test\")'); \
	result = db.execute('SELECT * FROM test'); \
	assert result['count'] == 1; \
	print('✓ Quick test passed!')"

# Clean generated files
clean:
	@echo "Cleaning generated files..."
	rm -rf __pycache__
	rm -rf .pytest_cache
	rm -rf .coverage
	rm -rf htmlcov
	rm -rf .mypy_cache
	rm -rf *.egg-info
	rm -rf dist
	rm -rf build
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	@echo "✓ Cleanup completed!"

# Run CI checks locally (same as GitHub Actions)
ci: clean install lint test coverage
	@echo ""
	@echo "✓ All CI checks passed!"
