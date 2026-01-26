"""Pydantic models for requests and responses."""

from __future__ import annotations

from datetime import date
from typing import List, Optional

from pydantic import BaseModel, Field, field_validator


class ValidationRequest(BaseModel):
    """Request body for validation endpoint."""

    text: str = Field(..., min_length=1, max_length=100_000, description="Raw insurance document text")


class ExtractedFields(BaseModel):
    """Fields extracted from the document."""

    policy_number: Optional[str] = Field(default=None, description="Policy identifier")
    vessel_name: Optional[str] = Field(default=None, description="Name of the vessel")
    policy_start_date: Optional[date] = Field(
        default=None, description="Policy start date in ISO format"
    )
    policy_end_date: Optional[date] = Field(
        default=None, description="Policy end date in ISO format"
    )
    insured_value: Optional[float] = Field(
        default=None, description="Insured value in monetary units"
    )

    @field_validator("policy_start_date", "policy_end_date", mode="before")
    @classmethod
    def parse_date(cls, value: Optional[str | date]) -> Optional[date]:
        """Convert ISO date strings to :class:`datetime.date`."""

        if value in (None, ""):
            return None
        if isinstance(value, date):
            return value
        
        # Strip potential surrounding whitespace or quotes
        if isinstance(value, str):
            value = value.strip().strip("'\"")
            
        try:
            return date.fromisoformat(str(value))
        except (ValueError, TypeError):
            return None

    @field_validator("insured_value", mode="before")
    @classmethod
    def parse_insured_value(cls, value: Optional[float | str]) -> Optional[float]:
        if value in (None, ""):
            return None
        if isinstance(value, (int, float)):
            return float(value)
        
        # Remove currency symbols, commas and other non-numeric chars (except . and -)
        # We handle cases like "$1,234.56" -> "1234.56"
        clean_value = "".join(c for c in str(value) if c.isdigit() or c in ".-")
        
        # Handle multiple dots if any (take the last one as separator)
        if clean_value.count(".") > 1:
            parts = clean_value.split(".")
            clean_value = "".join(parts[:-1]) + "." + parts[-1]

        try:
            return float(clean_value)
        except (ValueError, TypeError):
            return None


class ValidationChecks(BaseModel):
    """Represents the boolean results of each validation rule."""

    date_order_ok: bool
    insured_value_ok: bool
    vessel_allowed: bool
    policy_number_ok: bool


class ValidationResponse(BaseModel):
    """Response payload for validation results."""

    extracted: ExtractedFields
    validations: ValidationChecks
    is_valid: bool
    errors: List[str]


__all__ = [
    "ValidationRequest",
    "ValidationResponse",
    "ValidationChecks",
    "ExtractedFields",
]
