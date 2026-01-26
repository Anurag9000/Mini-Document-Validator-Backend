from __future__ import annotations

from collections.abc import AsyncIterator, Iterator
from typing import Any

import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport

from app.main import app
from app.ai_extractor import get_default_extractor
from app.models import ExtractedFields


class _MockExtractor:
    def __init__(self, fields: ExtractedFields):
        self._fields = fields

    def extract(self, text: str) -> ExtractedFields:  # pragma: no cover - simple passthrough
        return self._fields


@pytest.fixture(autouse=True)
def restore_overrides() -> Iterator[None]:
    """Restore app dependency overrides after each test."""
    original = app.dependency_overrides.copy()
    yield
    app.dependency_overrides = original


@pytest_asyncio.fixture
async def client() -> AsyncIterator[AsyncClient]:
    """Provide an async HTTP client for testing."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as async_client:
        yield async_client


@pytest.mark.asyncio
async def test_validate_happy_path(client: AsyncClient):
    fields = ExtractedFields(
        policy_number="POL-123",
        vessel_name="Sea Breeze",
        policy_start_date="2024-01-01",
        policy_end_date="2024-06-30",
        insured_value="1000000",
    )
    app.dependency_overrides[get_default_extractor] = lambda: _MockExtractor(fields)

    response = await client.post("/validate", json={"text": "ignored"})
    payload = response.json()

    assert response.status_code == 200
    assert payload["is_valid"] is True
    assert payload["errors"] == []
    assert payload["validations"]["date_order_ok"] is True
    assert payload["extracted"]["policy_number"] == "POL-123"
