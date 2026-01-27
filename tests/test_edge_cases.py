"""Comprehensive edge case tests for the validation system."""

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

    def extract(self, text: str) -> ExtractedFields:
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
async def test_extremely_large_text_input(client: AsyncClient):
    """Test that extremely large text input is handled gracefully."""
    # Create 2MB of text (exceeds the 1MB limit in ai_extractor)
    large_text = "x" * (2 * 1024 * 1024)
    
    response = await client.post("/validate", json={"text": large_text})
    
    # Should not crash, should return a response
    assert response.status_code == 200
    payload = response.json()
    # Extraction returns empty fields for text that's too large
    assert payload["is_valid"] is False
    # Should have errors about missing fields
    assert len(payload["errors"]) > 0


@pytest.mark.asyncio
async def test_extremely_long_policy_number(client: AsyncClient):
    """Test that extremely long policy numbers are rejected."""
    fields = ExtractedFields(
        policy_number="A" * 150,  # Exceeds 100 char limit
        vessel_name="Sea Breeze",
        policy_start_date="2024-05-01",
        policy_end_date="2024-06-01",
        insured_value="100000",
    )
    app.dependency_overrides[get_default_extractor] = lambda: _MockExtractor(fields)

    response = await client.post("/validate", json={"text": "ignored"})
    payload = response.json()

    # Policy number should be rejected as None
    assert payload["extracted"]["policy_number"] is None
    assert payload["validations"]["policy_number_ok"] is False


@pytest.mark.asyncio
async def test_vessel_name_only_special_characters(client: AsyncClient):
    """Test that vessel names with only special characters are rejected."""
    fields = ExtractedFields(
        policy_number="POL-001",
        vessel_name="@#$%^&*()",  # Only special characters
        policy_start_date="2024-05-01",
        policy_end_date="2024-06-01",
        insured_value="100000",
    )
    app.dependency_overrides[get_default_extractor] = lambda: _MockExtractor(fields)

    response = await client.post("/validate", json={"text": "ignored"})
    payload = response.json()

    # Vessel name should be rejected as None
    assert payload["extracted"]["vessel_name"] is None
    assert payload["validations"]["vessel_allowed"] is False


@pytest.mark.asyncio
async def test_policy_duration_exceeds_50_years(client: AsyncClient):
    """Test that policy durations exceeding 50 years are rejected."""
    fields = ExtractedFields(
        policy_number="POL-001",
        vessel_name="Sea Breeze",
        policy_start_date="2024-01-01",
        policy_end_date="2100-01-01",  # 76 years
        insured_value="100000",
    )
    app.dependency_overrides[get_default_extractor] = lambda: _MockExtractor(fields)

    response = await client.post("/validate", json={"text": "ignored"})
    payload = response.json()
    
    # Check that validation failed
    assert payload["is_valid"] is False

    # Check for duration error in errors list
    errors_text = " ".join(payload["errors"])
    assert "policy duration" in errors_text or "exceeds maximum" in errors_text or "50 years" in errors_text


@pytest.mark.asyncio
async def test_date_outside_reasonable_range(client: AsyncClient):
    """Test that dates outside 1900-2100 range are rejected."""
    fields = ExtractedFields(
        policy_number="POL-001",
        vessel_name="Sea Breeze",
        policy_start_date="1800-01-01",  # Before 1900
        policy_end_date="2024-06-01",
        insured_value="100000",
    )
    app.dependency_overrides[get_default_extractor] = lambda: _MockExtractor(fields)

    response = await client.post("/validate", json={"text": "ignored"})
    payload = response.json()
    
    # Check that validation failed
    assert payload["is_valid"] is False
    # Check for range error in errors list
    errors_text = " ".join(payload["errors"])
    assert "outside reasonable range" in errors_text or "1900-2100" in errors_text


@pytest.mark.asyncio
async def test_insured_value_at_boundary(client: AsyncClient):
    """Test insured value at exactly $1 (minimum valid)."""
    fields = ExtractedFields(
        policy_number="POL-001",
        vessel_name="Sea Breeze",
        policy_start_date="2024-05-01",
        policy_end_date="2024-06-01",
        insured_value="1.0",
    )
    app.dependency_overrides[get_default_extractor] = lambda: _MockExtractor(fields)

    response = await client.post("/validate", json={"text": "ignored"})
    payload = response.json()

    assert payload["extracted"]["insured_value"] == 1.0
    assert payload["validations"]["insured_value_ok"] is True
    assert payload["is_valid"] is True


@pytest.mark.asyncio
async def test_empty_request_text(client: AsyncClient):
    """Test validation with empty text."""
    response = await client.post("/validate", json={"text": ""})
    
    # Should fail validation due to min_length constraint
    assert response.status_code == 422  # Validation error


@pytest.mark.asyncio
async def test_whitespace_only_text(client: AsyncClient):
    """Test validation with whitespace-only text."""
    # Whitespace counts towards min_length in Pydantic, so this will pass validation
    # but extraction will return empty fields
    response = await client.post("/validate", json={"text": "   \n\t  "})
    
    # Should pass validation but fail business logic validation
    assert response.status_code == 200
    payload = response.json()
    assert payload["is_valid"] is False
    # All fields should be missing
    assert "policy_number is missing or empty" in payload["errors"]


@pytest.mark.asyncio
async def test_multiple_spaces_in_vessel_name_normalization(client: AsyncClient):
    """Test that vessel names with multiple spaces are normalized correctly."""
    fields = ExtractedFields(
        policy_number="POL-001",
        vessel_name="Sea    Breeze",  # Multiple spaces
        policy_start_date="2024-05-01",
        policy_end_date="2024-06-01",
        insured_value="100000",
    )
    app.dependency_overrides[get_default_extractor] = lambda: _MockExtractor(fields)

    response = await client.post("/validate", json={"text": "ignored"})
    payload = response.json()

    # Should normalize to "Sea Breeze" and match in registry
    assert payload["extracted"]["vessel_name"] == "Sea Breeze"
    assert payload["validations"]["vessel_allowed"] is True
    assert payload["is_valid"] is True


@pytest.mark.asyncio
async def test_multiple_spaces_in_policy_number_normalization(client: AsyncClient):
    """Test that policy numbers with multiple spaces are normalized."""
    fields = ExtractedFields(
        policy_number="POL   001",  # Multiple spaces
        vessel_name="Sea Breeze",
        policy_start_date="2024-05-01",
        policy_end_date="2024-06-01",
        insured_value="100000",
    )
    app.dependency_overrides[get_default_extractor] = lambda: _MockExtractor(fields)

    response = await client.post("/validate", json={"text": "ignored"})
    payload = response.json()

    # Should normalize to "POL 001"
    assert payload["extracted"]["policy_number"] == "POL 001"
    assert payload["validations"]["policy_number_ok"] is True


@pytest.mark.asyncio
async def test_health_endpoint_error_handling(client: AsyncClient):
    """Test that health endpoint doesn't crash on errors."""
    response = await client.get("/health")
    
    assert response.status_code == 200
    data = response.json()
    # Should return either ok or degraded, not crash
    assert "status" in data
    assert data["status"] in ["ok", "degraded"]


@pytest.mark.asyncio
async def test_version_endpoint_error_handling(client: AsyncClient):
    """Test that version endpoint doesn't crash on errors."""
    response = await client.get("/version")
    
    assert response.status_code == 200
    data = response.json()
    # Should return version, not crash
    assert "version" in data


@pytest.mark.asyncio
async def test_validation_endpoint_with_extraction_exception(client: AsyncClient):
    """Test that validation endpoint handles extraction exceptions gracefully."""
    
    class FailingExtractor:
        def extract(self, text: str) -> ExtractedFields:
            raise RuntimeError("Simulated extraction failure")
    
    app.dependency_overrides[get_default_extractor] = FailingExtractor

    response = await client.post("/validate", json={"text": "some text"})
    
    # Should not crash, should return error response
    assert response.status_code == 200
    payload = response.json()
    assert payload["is_valid"] is False
    assert any("extraction encountered errors" in error for error in payload["errors"])
