from __future__ import annotations

import pytest
import pytest_asyncio
from httpx import AsyncClient

from app.main import app
from app.models import ExtractedFields
from app.routes.validate import get_extractor_dependency


class _MockExtractor:
    def __init__(self, fields: ExtractedFields):
        self._fields = fields

    def extract(self, text: str) -> ExtractedFields:  # pragma: no cover
        return self._fields


@pytest.fixture(autouse=True)
def restore_overrides():
    original = app.dependency_overrides.copy()
    yield
    app.dependency_overrides = original


@pytest_asyncio.fixture
async def client() -> AsyncClient:
    async with AsyncClient(app=app, base_url="http://test") as async_client:
        yield async_client


@pytest.mark.asyncio
async def test_invalid_date_order(client: AsyncClient):
    fields = ExtractedFields(
        policy_number="POL-001",
        vessel_name="Sea Breeze",
        policy_start_date="2024-06-01",
        policy_end_date="2024-05-01",
        insured_value="100000",
    )
    app.dependency_overrides[get_extractor_dependency] = lambda: _MockExtractor(fields)

    response = await client.post("/validate", json={"text": "ignored"})
    payload = response.json()

    assert payload["validations"]["date_order_ok"] is False
    assert (
        "policy_end_date must be after policy_start_date" in payload["errors"]
    )


@pytest.mark.asyncio
async def test_invalid_insured_value(client: AsyncClient):
    fields = ExtractedFields(
        policy_number="POL-001",
        vessel_name="Sea Breeze",
        policy_start_date="2024-05-01",
        policy_end_date="2024-06-01",
        insured_value="0",
    )
    app.dependency_overrides[get_extractor_dependency] = lambda: _MockExtractor(fields)

    response = await client.post("/validate", json={"text": "ignored"})
    payload = response.json()

    assert payload["validations"]["insured_value_ok"] is False
    assert "insured_value must be greater than zero" in payload["errors"]


@pytest.mark.asyncio
async def test_invalid_vessel_name(client: AsyncClient):
    fields = ExtractedFields(
        policy_number="POL-001",
        vessel_name="Unknown Vessel",
        policy_start_date="2024-05-01",
        policy_end_date="2024-06-01",
        insured_value="100000",
    )
    app.dependency_overrides[get_extractor_dependency] = lambda: _MockExtractor(fields)

    response = await client.post("/validate", json={"text": "ignored"})
    payload = response.json()

    assert payload["validations"]["vessel_allowed"] is False
    assert "vessel_name is not in the list of allowed vessels" in payload["errors"]


@pytest.mark.asyncio
async def test_invalid_policy_number(client: AsyncClient):
    fields = ExtractedFields(
        policy_number=" ",
        vessel_name="Sea Breeze",
        policy_start_date="2024-05-01",
        policy_end_date="2024-06-01",
        insured_value="100000",
    )
    app.dependency_overrides[get_extractor_dependency] = lambda: _MockExtractor(fields)

    response = await client.post("/validate", json={"text": "ignored"})
    payload = response.json()

    assert payload["validations"]["policy_number_ok"] is False
    assert "policy_number must be provided" in payload["errors"]
