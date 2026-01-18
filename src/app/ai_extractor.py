"""Rule-based AI extractor implementation.

The module exposes a simple protocol for extracting insurance policy
information from raw text. The default implementation relies on
regular expressions so that the service can run fully offline while
remaining easy to swap out for a real LLM-backed extractor in the
future.
"""

from __future__ import annotations

import re
from typing import Protocol

from .models import ExtractedFields


class AIExtractor(Protocol):
    """Protocol describing an extractor implementation."""

    def extract(self, text: str) -> ExtractedFields:
        """Extract structured fields from the provided text."""


class RuleBasedAIExtractor:
    """Deterministic extractor based on regular expressions."""

    _policy_number_pattern = re.compile(
        r"policy\s*number[:\-]?\s*(?P<value>[\w\-\./]+)", re.IGNORECASE
    )
    _vessel_name_pattern = re.compile(
        r"vessel\s*name[:\-]?\s*(?P<value>[\w\s\.\-']+)", re.IGNORECASE
    )
    _start_date_pattern = re.compile(
        r"policy\s*start\s*date[:\-]?\s*(?P<value>\d{4}-\d{2}-\d{2})",
        re.IGNORECASE,
    )
    _end_date_pattern = re.compile(
        r"policy\s*end\s*date[:\-]?\s*(?P<value>\d{4}-\d{2}-\d{2})",
        re.IGNORECASE,
    )
    _insured_value_pattern = re.compile(
        r"insured\s*value[:\-]?\s*(?P<currency>[$€£])?\s*(?P<value>[0-9,]+(?:\.\d{2})?)",
        re.IGNORECASE,
    )

    def extract(self, text: str) -> ExtractedFields:
        """Extract fields from document text using regex heuristics."""

        data: dict[str, object] = {}
        policy_match = self._policy_number_pattern.search(text)
        if policy_match:
            data["policy_number"] = policy_match.group("value").strip()

        vessel_match = self._vessel_name_pattern.search(text)
        if vessel_match:
            data["vessel_name"] = vessel_match.group("value").strip()

        start_match = self._start_date_pattern.search(text)
        if start_match:
            data["policy_start_date"] = start_match.group("value")

        end_match = self._end_date_pattern.search(text)
        if end_match:
            data["policy_end_date"] = end_match.group("value")

        insured_match = self._insured_value_pattern.search(text)
        if insured_match:
            data["insured_value"] = insured_match.group("value")

        return ExtractedFields.model_validate(data)


def get_default_extractor() -> AIExtractor:
    """Return the default extractor implementation."""

    return RuleBasedAIExtractor()


__all__ = ["AIExtractor", "RuleBasedAIExtractor", "get_default_extractor"]
