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
        try:
            return date.fromisoformat(value)
        except ValueError:
            return None

    @field_validator("insured_value", mode="before")
    @classmethod
    def parse_insured_value(cls, value: Optional[float | str]) -> Optional[float]:
        if value in (None, ""):
            return None
        if isinstance(value, (int, float)):
            return float(value)
        # Remove currency symbols and other non-numeric chars (except . and -)
        clean_value = "".join(c for c in value if c.isdigit() or c in ".-")
        try:
            return float(clean_value)
        except ValueError:
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
