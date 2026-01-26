"""Manual test script for health endpoint."""

from __future__ import annotations

import asyncio
import sys

sys.path.insert(0, "src")

from httpx import ASGITransport, AsyncClient

from app.main import app


async def test_health() -> None:
    """Test the health endpoint using AsyncClient with ASGITransport."""
    try:
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            response = await client.get("/health")
            print(f"Status: {response.status_code}")
            print(f"Response: {response.json()}")
    except Exception as e:
        print(f"Error during health check: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(test_health())
