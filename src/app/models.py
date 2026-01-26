"""Pydantic models for requests and responses."""

from __future__ import annotations

from datetime import date
from typing import List, Optional, Union

from pydantic import BaseModel, Field, field_validator


class ValidationRequest(BaseModel):
    """Request body for validation endpoint."""

    text: str = Field(..., min_length=1, max_length=100_000, description="Raw insurance document text")


class ExtractedFields(BaseModel):
    """Fields extracted from the document."""

    policy_number: Optional[str] = Field(
        default=None, 
        description="The unique identifier for the insurance policy (e.g., 'AXA-123')."
    )
    vessel_name: Optional[str] = Field(
        default=None, 
        description="The name of the vessel covered by the policy."
    )
    policy_start_date: Optional[date] = Field(
        default=None, 
        description="The date when the policy coverage becomes effective (ISO 8601 format)."
    )
    policy_end_date: Optional[date] = Field(
        default=None, 
        description="The date when the policy coverage expires (ISO 8601 format)."
    )
    insured_value: Optional[float] = Field(
        default=None, 
        description="Insured value in monetary units (must be positive; negative values are rejected)"
    )

    @field_validator("policy_start_date", "policy_end_date", mode="before")
    @classmethod
    def parse_date(cls, value: Union[str, date, None]) -> Optional[date]:
        """Convert ISO date strings to :class:`datetime.date`.
        
        Accepts ISO 8601 format (YYYY-MM-DD). Returns None for invalid formats,
        empty strings, or None values. Strips whitespace and quotes.
        """

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
    def parse_insured_value(cls, value: Union[float, str, None]) -> Optional[float]:
        """Parse insured value from string or numeric input.
        
        Handles currency symbols, thousand separators (commas), and various formats.
        Rejects negative values. Returns None for invalid or missing values.
        """
        if value in (None, ""):
            return None
        if isinstance(value, (int, float)):
            return float(value)
        
        # Remove currency symbols, commas and other non-numeric chars (except . and -)
        # We handle cases like "$1,234.56" -> "1234.56"
        clean_value = "".join(c for c in str(value) if c.isdigit() or c in ".-")
        
        # Filter out negative values - insured value should always be positive
        if clean_value.startswith("-"):
            return None
        
        # Handle multiple dots if any (likely thousand separators)
        # For "1.234.567.89", we want "1234567.89"
        if clean_value.count(".") > 1:
            # Remove all dots except the last one (decimal separator)
            parts = clean_value.split(".")
            # Join all parts except last, then add decimal point and last part
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
