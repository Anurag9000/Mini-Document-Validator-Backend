from __future__ import annotations

import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport

from app.main import app


@pytest_asyncio.fixture
async def client() -> AsyncClient:
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as async_client:
        yield async_client


@pytest.mark.asyncio
async def test_health_endpoint(client: AsyncClient) -> None:
    response = await client.get("/health")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "vessels_loaded" in data


@pytest.mark.asyncio
async def test_version_endpoint(client: AsyncClient) -> None:
    response = await client.get("/version")

    assert response.status_code == 200
    payload = response.json()
    assert "version" in payload
    assert isinstance(payload["version"], str)