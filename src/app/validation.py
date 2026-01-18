"""Validation rules for extracted insurance document fields."""

from __future__ import annotations

from datetime import date
from typing import Optional


def validate_date_order(start: Optional[date], end: Optional[date]) -> bool:
    """Return ``True`` if the end date is after the start date."""

    if start is None or end is None:
        return False
    return end >= start


def validate_insured_value(value: Optional[float]) -> bool:
    """Return ``True`` if the insured value is present and positive."""

    return value is not None and value > 0





def validate_policy_number(policy_number: Optional[str]) -> bool:
    """Return ``True`` if the policy number is non-empty."""

    if policy_number is None:
        return False
    return policy_number.strip() != ""


__all__ = [
    "validate_date_order",
    "validate_insured_value",
    "validate_policy_number",
]
