# Contributing Guidelines

Thank you for your interest in contributing to the Genoshi Backend Validator!
This document describes how to get started and the conventions followed in the
project.

## Development workflow

1. Fork and clone the repository.
2. Install dependencies and git hooks:
   ```bash
   make setup
   ```
3. Create a feature branch from `main`.
4. Implement your changes with accompanying tests.
5. Run the quality gates locally:
   ```bash
   make fmt lint typecheck test
   ```
6. Commit using conventional messages when possible and open a pull request.

## Coding standards

- Python 3.11+ with type hints everywhere; `mypy --strict` must pass.
- Format code with Black (`make fmt`).
- Keep imports sorted; Ruff enforces lint rules.
- Avoid introducing additional runtime dependencies without discussion.
- Prefer pure functions in `src/app/validation.py` to simplify testing.

## Testing

- Use `pytest` and `pytest-asyncio` for async tests.
- Mock the extractor (`AIExtractor`) interface to produce deterministic
  scenarios.
- Ensure new features include unit tests covering happy and failure paths.

## Documentation

- Update `README.md` with any new commands or architectural changes.
- Document environment variables in `.env.example` when adding new settings.

## Code of Conduct

Participation in this project is governed by the
[Code of Conduct](CODE_OF_CONDUCT.md). By contributing you agree to uphold
these standards.
