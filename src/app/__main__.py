from __future__ import annotations

import os

import uvicorn


def main() -> None:
    """Run the application using uvicorn with configuration from environment variables."""
    host = os.getenv("APP_HOST", "127.0.0.1")
    
    # Safely parse port with error handling
    try:
        port = int(os.getenv("APP_PORT", "8000"))
    except ValueError:
        port = 8000
        print(f"Warning: Invalid APP_PORT value, using default port {port}")
    
    reload = os.getenv("APP_RELOAD", "1") not in {"0", "false", "False"}
    uvicorn.run("app.main:app", host=host, port=port, reload=reload)


if __name__ == "__main__":
    main()

