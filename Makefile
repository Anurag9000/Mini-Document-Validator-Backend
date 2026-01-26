.PHONY: setup fmt lint typecheck test run dev build up install-hooks clean help

# Detect OS
ifeq ($(OS),Windows_NT)
    # Windows
    VENV := .venv
    PYTHON := $(VENV)\\Scripts\\python.exe
    PIP := $(VENV)\\Scripts\\pip.exe
    UVICORN := $(VENV)\\Scripts\\uvicorn.exe
    BLACK := $(VENV)\\Scripts\\black.exe
    RUFF := $(VENV)\\Scripts\\ruff.exe
    MYPY := $(VENV)\\Scripts\\mypy.exe
    PYTEST := $(VENV)\\Scripts\\pytest.exe
    PRECOMMIT := $(VENV)\\Scripts\\pre-commit.exe
    RM := del /Q
    RMDIR := rmdir /S /Q
else
    # Unix-like (Linux, macOS)
    VENV := .venv
    PYTHON := $(VENV)/bin/python
    PIP := $(VENV)/bin/pip
    UVICORN := $(VENV)/bin/uvicorn
    BLACK := $(VENV)/bin/black
    RUFF := $(VENV)/bin/ruff
    MYPY := $(VENV)/bin/mypy
    PYTEST := $(VENV)/bin/pytest
    PRECOMMIT := $(VENV)/bin/pre-commit
    RM := rm -f
    RMDIR := rm -rf
endif

help:
\t@echo \"Available targets:\"
\t@echo \"  setup       - Create venv and install dependencies\"
\t@echo \"  fmt         - Format code with black and ruff\"
\t@echo \"  lint        - Lint code with ruff\"
\t@echo \"  typecheck   - Type check with mypy\"
\t@echo \"  test        - Run tests with pytest\"
\t@echo \"  run         - Run the application\"
\t@echo \"  dev         - Run with auto-reload\"
\t@echo \"  build       - Build Docker image\"
\t@echo \"  up          - Run with docker-compose\"
\t@echo \"  clean       - Remove build artifacts and cache\"
\t@echo \"  install-hooks - Install pre-commit hooks\"

setup:
\t@if not exist $(VENV) python -m venv $(VENV) || python3 -m venv $(VENV)
\t$(PIP) install --upgrade pip
\t$(PIP) install -e \".[dev]\"
\t$(PRECOMMIT) install

fmt:
\t$(BLACK) src tests
\t$(RUFF) check --fix src tests

lint:
\t$(RUFF) check src tests

typecheck:
\t$(MYPY) src

test:
\t$(PYTEST)

run:
\t$(UVICORN) app.main:app --host 0.0.0.0 --port 8000

dev:
\t$(UVICORN) app.main:app --reload --host 0.0.0.0 --port 8000

build:
\tdocker build -t genoshi-backend-validator .

up:
\tdocker-compose up --build

clean:
ifeq ($(OS),Windows_NT)
\t@if exist __pycache__ $(RMDIR) __pycache__
\t@if exist .pytest_cache $(RMDIR) .pytest_cache
\t@if exist .mypy_cache $(RMDIR) .mypy_cache
\t@if exist .ruff_cache $(RMDIR) .ruff_cache
\t@if exist dist $(RMDIR) dist
\t@if exist build $(RMDIR) build
\t@if exist *.egg-info $(RMDIR) *.egg-info
\t@for /d /r . %%d in (__pycache__) do @if exist \"%%d\" $(RMDIR) \"%%d\"
else
\t$(RMDIR) __pycache__ .pytest_cache .mypy_cache .ruff_cache dist build *.egg-info
\tfind . -type d -name __pycache__ -exec rm -rf {} +
\tfind . -type f -name \"*.pyc\" -delete
endif

install-hooks:
\t$(PRECOMMIT) install
