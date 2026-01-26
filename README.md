Genoshi Backend Validator (FastAPI)

Simple FastAPI service that extracts fields from insurance documents and validates them with deterministic rules. Includes tests, Docker support, and Windows-friendly scripts.

Quick Start (Windows)

- Install Python 3.11 (add Python to PATH) and optionally Docker Desktop.
- Create a virtual environment and install deps:
  - PowerShell
    - `py -3.11 -m venv .venv`
    - `.\.venv\Scripts\Activate.ps1`
    - `pip install -U pip`
    - `pip install -e ".[dev]"`

Run Locally

- Option 1: Module entry point
  - `python -m app` (serves on http://127.0.0.1:8000 with reload)
- Option 2: Uvicorn directly
  - `uvicorn app.main:app --reload --host 127.0.0.1 --port 8000`
- Option 3: PowerShell helper scripts
  - `powershell -ExecutionPolicy Bypass -File scripts\dev.ps1`

API Endpoints

- `GET /health` → `{ "status": "ok", "vessels_loaded": 15 }`
- `GET /version` → `{ "version": "0.1.0" }` (or APP_VERSION)
- `POST /validate`
  - Body: `{ "text": "Policy Number: POL-123\nVessel Name: Sea Breeze\nPolicy Start Date: 2024-01-01\nPolicy End Date: 2024-06-30\nInsured Value: 1000000" }`
  - Response contains `extracted`, `validations`, `is_valid`, and `errors`.

Run Tests

- Activate venv then run: `pytest -q`
- Or: `powershell -ExecutionPolicy Bypass -File scripts\test.ps1`

Docker

- Build and run:
  - `docker build -t genoshi-backend-validator .`
  - `docker run -p 8000:8000 genoshi-backend-validator`
- With Docker Compose: `docker compose up --build`

Configuration

- Optional `.env` (see `.env.example`):
  - `APP_ENV=dev`
  - `APP_VERSION=0.1.0`
  - `APP_LOG_LEVEL=INFO` (DEBUG, INFO, WARNING, ERROR, CRITICAL)

Project Layout

- `src/app` – FastAPI app and modules
- `src/app/data/valid_vessels.json` – Vessel allowlist
- `samples/` – Sample documents
- `tests/` – Pytest suite

CI (GitHub Actions)

- On push, tests run on Python 3.11 (see `.github/workflows/ci.yml`).

Troubleshooting

- **Import errors**: Ensure you've installed with `pip install -e ".[dev]"` and activated the virtual environment
- **Port already in use**: Change the port with `--port 8001` or set `APP_PORT=8001` environment variable
- **Vessel registry empty**: Check that `src/app/data/valid_vessels.json` exists and contains valid JSON array
- **Tests failing**: Run `python scripts/check_env.py` to verify all dependencies are installed

Deploy Options

- Quick Docker deploy anywhere that runs containers.
- For a one-click hosted demo, services like Render, Railway, Fly.io, or Azure App Service work well:
  - Command: `uvicorn app.main:app --host 0.0.0.0 --port 8000`
  - Build: use Python 3.11 and `pip install -e .` or `pip install -r <generated requirements>`
- If you want, share your GitHub repo URL and I can add a Render/Railway config tuned to it.

