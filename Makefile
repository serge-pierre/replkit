# Makefile — Development commands for replkit

PYTHON ?= python
PIP ?= $(PYTHON) -m pip

.PHONY: install test lint format clean check

install:
	$(PIP) install -e .[dev]

test:
	$(PYTHON) -m pytest

lint:
	$(PYTHON) -m ruff replkit tests

format:
	$(PYTHON) -m black replkit tests

check: lint test

clean:
	find . -type d -name "__pycache__" -exec rm -r {} +
	rm -rf .pytest_cache .mypy_cache .ruff_cache
