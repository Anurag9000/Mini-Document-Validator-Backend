from __future__ import annotations

import os

import uvicorn


def main() -> None:
    host = os.getenv("APP_HOST", "127.0.0.1")
    port = int(os.getenv("APP_PORT", "8000"))
    reload = os.getenv("APP_RELOAD", "1") not in {"0", "false", "False"}
    uvicorn.run("app.main:app", host=host, port=port, reload=reload)


if __name__ == "__main__":
    main()

