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

    def extract(self, text: str) -> ExtractedFields:  # pragma: no cover
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
async def test_invalid_date_order(client: AsyncClient):
    fields = ExtractedFields(
        policy_number="POL-001",
        vessel_name="Sea Breeze",
        policy_start_date="2024-06-01",
        policy_end_date="2024-05-01",
        insured_value="100000",
    )
    app.dependency_overrides[get_default_extractor] = lambda: _MockExtractor(fields)

    response = await client.post("/validate", json={"text": "ignored"})
    payload = response.json()

    assert payload["validations"]["date_order_ok"] is False
    assert (
        "policy_end_date (2024-05-01) must be on or after policy_start_date (2024-06-01)" in payload["errors"]
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
    app.dependency_overrides[get_default_extractor] = lambda: _MockExtractor(fields)

    response = await client.post("/validate", json={"text": "ignored"})
    payload = response.json()

    assert payload["validations"]["insured_value_ok"] is False
    assert "insured_value (0.0) must be greater than zero" in payload["errors"]


@pytest.mark.asyncio
async def test_invalid_vessel_name(client: AsyncClient):
    fields = ExtractedFields(
        policy_number="POL-001",
        vessel_name="Unknown Vessel",
        policy_start_date="2024-05-01",
        policy_end_date="2024-06-01",
        insured_value="100000",
    )
    app.dependency_overrides[get_default_extractor] = lambda: _MockExtractor(fields)

    response = await client.post("/validate", json={"text": "ignored"})
    payload = response.json()

    assert payload["validations"]["vessel_allowed"] is False
    assert "vessel_name 'Unknown Vessel' is not in the allowed list" in payload["errors"]


@pytest.mark.asyncio
async def test_invalid_policy_number(client: AsyncClient):
    fields = ExtractedFields(
        policy_number=" ",
        vessel_name="Sea Breeze",
        policy_start_date="2024-05-01",
        policy_end_date="2024-06-01",
        insured_value="100000",
    )
    app.dependency_overrides[get_default_extractor] = lambda: _MockExtractor(fields)

    response = await client.post("/validate", json={"text": "ignored"})
    payload = response.json()

    assert payload["validations"]["policy_number_ok"] is False
    assert "policy_number is missing or empty" in payload["errors"]


@pytest.mark.asyncio
async def test_thousand_separator_and_currency(client: AsyncClient):
    # Test that model_validate handles $1,234.56 correctly
    from app.models import ExtractedFields
    data = {
        "policy_number": "POL-123",
        "vessel_name": "Sea Breeze",
        "policy_start_date": "2024-01-01",
        "policy_end_date": "2024-12-31",
        "insured_value": "$1,234,567.89"
    }
    fields = ExtractedFields.model_validate(data)
    assert fields.insured_value == 1234567.89


@pytest.mark.asyncio
async def test_malformed_date(client: AsyncClient):
    fields = ExtractedFields(
        policy_number="POL-001",
        vessel_name="Sea Breeze",
        policy_start_date="not-a-date",
        policy_end_date="2024-06-01",
        insured_value="100000",
    )
    app.dependency_overrides[get_default_extractor] = lambda: _MockExtractor(fields)

    response = await client.post("/validate", json={"text": "ignored"})
    payload = response.json()

    assert payload["validations"]["date_order_ok"] is False
    assert "policy_start_date is missing or invalid format (YYYY-MM-DD)" in payload["errors"]


@pytest.mark.asyncio
async def test_vessel_name_case_insensitive(client: AsyncClient):
    fields = ExtractedFields(
        policy_number="POL-001",
        vessel_name="sea breeze",  # lower case
        policy_start_date="2024-05-01",
        policy_end_date="2024-06-01",
        insured_value="100000",
    )
    app.dependency_overrides[get_default_extractor] = lambda: _MockExtractor(fields)

    response = await client.post("/validate", json={"text": "ignored"})
    payload = response.json()

    assert payload["validations"]["vessel_allowed"] is True
    assert payload["is_valid"] is True


@pytest.mark.asyncio
async def test_real_extractor_integration(client: AsyncClient) -> None:
    # Test with the actual extractor to verify regex + parsing
    from app.ai_extractor import RuleBasedAIExtractor
    app.dependency_overrides[get_default_extractor] = RuleBasedAIExtractor

    doc_text = """
    CONTRACT NO: AXA-777-B
    SHIP NAME: Oceanic Star
    EFFECTIVE DATE: 2024-10-01
    EXPIRY DATE: 2025-10-01
    LIMIT: $5,000,000.5
    """
    response = await client.post("/validate", json={"text": doc_text})
    payload = response.json()

    assert payload["extracted"]["policy_number"] == "AXA-777-B"
    assert payload["extracted"]["vessel_name"] == "Oceanic Star"
    assert payload["extracted"]["policy_start_date"] == "2024-10-01"
    assert payload["extracted"]["policy_end_date"] == "2025-10-01"
    # $5,000,000.5 -> 5000000.5
    assert payload["extracted"]["insured_value"] == 5000000.5
    assert payload["is_valid"] is True


@pytest.mark.asyncio
async def test_negative_insured_value(client: AsyncClient):
    """Test that negative insured values are rejected."""
    fields = ExtractedFields(
        policy_number="POL-001",
        vessel_name="Sea Breeze",
        policy_start_date="2024-05-01",
        policy_end_date="2024-06-01",
        insured_value="-100000",
    )
    app.dependency_overrides[get_default_extractor] = lambda: _MockExtractor(fields)

    response = await client.post("/validate", json={"text": "ignored"})
    payload = response.json()

    # Negative values should be parsed as None
    assert payload["extracted"]["insured_value"] is None
    assert payload["validations"]["insured_value_ok"] is False
    assert "insured_value is missing or invalid" in payload["errors"]


@pytest.mark.asyncio
async def test_all_fields_missing(client: AsyncClient):
    """Test validation when all fields are missing."""
    fields = ExtractedFields()
    app.dependency_overrides[get_default_extractor] = lambda: _MockExtractor(fields)

    response = await client.post("/validate", json={"text": "ignored"})
    payload = response.json()

    assert payload["is_valid"] is False
    assert "policy_number is missing or empty" in payload["errors"]
    assert "vessel_name is missing or empty" in payload["errors"]
    assert "policy_start_date is missing or invalid format" in payload["errors"]
    assert "policy_end_date is missing or invalid format" in payload["errors"]
    assert "insured_value is missing or invalid" in payload["errors"]


@pytest.mark.asyncio
async def test_extremely_large_insured_value(client: AsyncClient):
    """Test that extremely large insured values are handled."""
    # Value larger than 1 quadrillion should be rejected
    fields = ExtractedFields(
        policy_number="POL-001",
        vessel_name="Sea Breeze",
        policy_start_date="2024-05-01",
        policy_end_date="2024-06-01",
        insured_value=str(1e16),  # 10 quadrillion
    )
    app.dependency_overrides[get_default_extractor] = lambda: _MockExtractor(fields)

    response = await client.post("/validate", json={"text": "ignored"})
    payload = response.json()

    # Should be rejected as None due to overflow protection
    assert payload["extracted"]["insured_value"] is None
    assert payload["validations"]["insured_value_ok"] is False


@pytest.mark.asyncio
async def test_same_start_and_end_date(client: AsyncClient):
    """Test that same start and end date is valid."""
    fields = ExtractedFields(
        policy_number="POL-001",
        vessel_name="Sea Breeze",
        policy_start_date="2024-05-01",
        policy_end_date="2024-05-01",  # Same as start
        insured_value="100000",
    )
    app.dependency_overrides[get_default_extractor] = lambda: _MockExtractor(fields)

    response = await client.post("/validate", json={"text": "ignored"})
    payload = response.json()

    assert payload["validations"]["date_order_ok"] is True
    assert payload["is_valid"] is True


@pytest.mark.asyncio
async def test_whitespace_in_vessel_name(client: AsyncClient):
    """Test that vessel names with extra whitespace are handled."""
    fields = ExtractedFields(
        policy_number="POL-001",
        vessel_name="  Sea   Breeze  ",  # Extra whitespace
        policy_start_date="2024-05-01",
        policy_end_date="2024-06-01",
        insured_value="100000",
    )
    app.dependency_overrides[get_default_extractor] = lambda: _MockExtractor(fields)

    response = await client.post("/validate", json={"text": "ignored"})
    payload = response.json()

    # Should still match "Sea Breeze" in registry (case-insensitive, whitespace normalized)
    assert payload["validations"]["vessel_allowed"] is True
    assert payload["is_valid"] is True
