.PHONY: setup fmt lint typecheck test run dev build up install-hooks

VENV := .venv
PYTHON := $(VENV)/bin/python
PIP := $(VENV)/bin/pip
UVICORN := $(VENV)/bin/uvicorn
BLACK := $(VENV)/bin/black
RUFF := $(VENV)/bin/ruff
MYPY := $(VENV)/bin/mypy
PYTEST := $(VENV)/bin/pytest
PRECOMMIT := $(VENV)/bin/pre-commit

setup:
	@test -d $(VENV) || python3 -m venv $(VENV)
	$(PIP) install --upgrade pip
	$(PIP) install -e ".[dev]"
	$(PRECOMMIT) install

fmt:
	$(BLACK) src tests
	$(RUFF) check --fix src tests

lint:
	$(RUFF) check src tests

typecheck:
	$(MYPY) src

test:
	$(PYTEST)

run:
	$(UVICORN) app.main:app --host 0.0.0.0 --port 8000

dev:
	$(UVICORN) app.main:app --reload --host 0.0.0.0 --port 8000

build:
	docker build -t genoshi-backend-validator .

up:
	docker-compose up --build

install-hooks:
	$(PRECOMMIT) install
