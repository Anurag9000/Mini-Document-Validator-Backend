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


def validate_date_range(policy_date: Optional[date]) -> bool:
    """Return ``True`` if the date is within a reasonable range (1900-2100).
    
    Prevents absurd dates like year 3000 or negative years.
    """
    if policy_date is None:
        return False
    
    # Reasonable range: 1900 to 2100
    min_year = 1900
    max_year = 2100
    
    return min_year <= policy_date.year <= max_year


def validate_policy_duration(start: Optional[date], end: Optional[date]) -> bool:
    """Return ``True`` if policy duration is reasonable (not more than 50 years).
    
    Prevents absurd policy durations like 1000 years.
    """
    if start is None or end is None:
        return False
    
    if end < start:
        return False
    
    # Maximum reasonable policy duration: 50 years
    duration_days = (end - start).days
    max_duration_days = 50 * 365  # ~50 years
    
    return duration_days <= max_duration_days


def validate_insured_value(value: Optional[float]) -> bool:
    """Return ``True`` if the insured value is present and positive."""

    return value is not None and value > 0


def validate_insured_value_range(value: Optional[float]) -> bool:
    """Return ``True`` if insured value is within reasonable range.
    
    Minimum: $1 (prevents zero or near-zero values)
    Maximum: $1 quadrillion (prevents overflow and absurd values)
    """
    if value is None:
        return False
    
    min_value = 1.0
    max_value = 1e15  # 1 quadrillion
    
    return min_value <= value <= max_value


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
    "validate_date_range",
    "validate_policy_duration",
    "validate_insured_value",
    "validate_insured_value_range",
    "validate_policy_number",
    "validate_vessel_name",
]
