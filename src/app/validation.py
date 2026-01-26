"""Validation rules for extracted insurance document fields."""

from __future__ import annotations

from datetime import date
from typing import Optional


def validate_date_order(start: Optional[date], end: Optional[date]) -> bool:
    """Return ``True`` if the end date is after or equal to the start date.
    
    Examples:
        >>> validate_date_order(date(2023, 1, 1), date(2023, 1, 2))
        True
        >>> validate_date_order(date(2023, 1, 2), date(2023, 1, 1))
        False
    """

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
    return bool(policy_number.strip())


def validate_vessel_name(vessel_name: Optional[str]) -> bool:
    """Return ``True`` if the vessel name is non-empty."""

    if vessel_name is None:
        return False
    return bool(vessel_name.strip())


__all__ = [
    "validate_date_order",
    "validate_insured_value",
    "validate_policy_number",
    "validate_vessel_name",
]
