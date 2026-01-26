"""Rule-based AI extractor implementation.

The module exposes a simple protocol for extracting insurance policy
information from raw text. The default implementation relies on
regular expressions so that the service can run fully offline while
remaining easy to swap out for a real LLM-backed extractor in the
future.
"""

from __future__ import annotations

import logging
import re
from typing import Protocol

from .models import ExtractedFields

logger = logging.getLogger(__name__)


class AIExtractor(Protocol):
    """Protocol describing an extractor implementation."""

    def extract(self, text: str) -> ExtractedFields:
        """Extract structured fields from the provided text."""


class RuleBasedAIExtractor:
    """Deterministic extractor based on regular expressions."""

    # Improved regex to handle optional labels and more variations
    _policy_number_pattern = re.compile(
        r"(?:policy\s*number|policy\s*id|contract\s*no)[:\-]?\s*(?P<value>[\w\-\./]+)", 
        re.IGNORECASE
    )
    _vessel_name_pattern = re.compile(
        r"(?:vessel\s*name|ship\s*name|vessel)[:\-]?\s*(?P<value>[\w \t\.\-']+)", 
        re.IGNORECASE
    )
    # Support both YYYY-MM-DD and DD/MM/YYYY or similar if needed, but sticking to ISO as per goal
    _start_date_pattern = re.compile(
        r"(?:policy\s*start|effective\s*date|from)[:\-]?\s*(?P<value>\d{4}-\d{2}-\d{2})",
        re.IGNORECASE,
    )
    _end_date_pattern = re.compile(
        r"(?:policy\s*end|expiry\s*date|to)[:\-]?\s*(?P<value>\d{4}-\d{2}-\d{2})",
        re.IGNORECASE,
    )
    # Improved currency handling and whitespace
    _insured_value_pattern = re.compile(
        r"(?:insured\s*value|sum\s*insured|limit)[:\-]?\s*(?P<currency>[$€£\w]{1,3})?\s*(?P<value>\-?[0-9,]+(?:\.\d{2})?)",
        re.IGNORECASE,
    )

    def extract(self, text: str) -> ExtractedFields:
        """Extract fields from document text using regex heuristics."""

        logger.debug("Starting extraction from text (length: %d)", len(text))
        data: dict[str, object] = {}
        
        policy_match = self._policy_number_pattern.search(text)
        if policy_match:
            data["policy_number"] = policy_match.group("value").strip()
            logger.debug("Found policy number: %s", data["policy_number"])

        vessel_match = self._vessel_name_pattern.search(text)
        if vessel_match:
            data["vessel_name"] = vessel_match.group("value").strip()
            logger.debug("Found vessel name: %s", data["vessel_name"])

        start_match = self._start_date_pattern.search(text)
        if start_match:
            data["policy_start_date"] = start_match.group("value")
            logger.debug("Found start date: %s", data["policy_start_date"])

        end_match = self._end_date_pattern.search(text)
        if end_match:
            data["policy_end_date"] = end_match.group("value")
            logger.debug("Found end date: %s", data["policy_end_date"])

        insured_match = self._insured_value_pattern.search(text)
        if insured_match:
            data["insured_value"] = insured_match.group("value")
            logger.debug("Found insured value: %s", data["insured_value"])

        if not data:
            logger.warning("No fields were extracted from the document")

        return ExtractedFields.model_validate(data)


def get_default_extractor() -> AIExtractor:
    """Return the default extractor implementation."""

    return RuleBasedAIExtractor()


__all__ = ["AIExtractor", "RuleBasedAIExtractor", "get_default_extractor"]
