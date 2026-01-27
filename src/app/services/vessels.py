"""Vessel registry service for validation dependencies."""

from __future__ import annotations

import logging
import json
from functools import lru_cache
from pathlib import Path
from typing import Iterable

logger = logging.getLogger(__name__)


class VesselRegistry:
    """Stores the set of valid vessel names."""

    def __init__(self, vessels: Iterable[str]):
        # Normalize whitespace: strip, convert to upper, and normalize internal spaces
        self._vessels: set[str] = {
            " ".join(v.split()).upper() 
            for v in vessels 
            if v and v.strip()
        }
        logger.debug("Vessel registry initialized with %d vessels", len(self._vessels))

    def is_allowed(self, name: str | None) -> bool:
        """Return ``True`` when the vessel name is registered.
        
        Vessel name matching is case-insensitive and normalizes whitespace
        (multiple spaces are treated as single spaces).
        """
        if name is None:
            return False
        # Normalize whitespace in input to match how we store vessels
        normalized_name = " ".join(name.split()).upper()
        return normalized_name in self._vessels

    def all(self) -> set[str]:
        """Return a copy of the known vessel names."""
        return set(self._vessels)

    def __len__(self) -> int:
        """Return the number of registered vessels."""
        return len(self._vessels)

    @property
    def is_empty(self) -> bool:
        """Return ``True`` if the registry contains no vessels."""
        return len(self._vessels) == 0


def _default_data_path() -> Path:
    """Return the default path to the vessel data file.
    
    Resolves to src/app/data/valid_vessels.json relative to this module.
    """
    # src/app/services/vessels.py -> src/app/data/valid_vessels.json
    return Path(__file__).resolve().parent.parent / "data" / "valid_vessels.json"


def _load_vessel_names(path: Path) -> set[str]:
    """Load vessel names from a JSON file.
    
    Args:
        path: Path to the JSON file containing vessel names
        
    Returns:
        Set of vessel name strings, empty set on error
    """
    logger.info("Loading vessel names from %s", path)
    if not path.exists():
        logger.error("Vessel data file not found: %s", path)
        return set()
    
    try:
        with path.open("r", encoding="utf-8") as fp:
            items = json.load(fp)
    except json.JSONDecodeError as e:
        logger.error("Vessel data file contains invalid JSON at %s: %s", path, e)
        return set()
    except (OSError, IOError) as e:
        logger.error("Failed to read vessel data file %s: %s", path, e)
        return set()
    except Exception as e:
        logger.exception("Unexpected error loading vessel names from %s: %s", path, e)
        return set()
    
    if not isinstance(items, list):
        logger.error("Vessel data file must contain a JSON array, got %s: %s", type(items).__name__, path)
        return set()
    
    # Validate and clean vessel names
    valid_vessels = set()
    normalized_vessels = set()  # Track normalized names for duplicate detection
    empty_count = 0
    duplicate_count = 0
    
    for item in items:
        if not isinstance(item, str):
            logger.warning("Skipping non-string vessel entry: %s (type: %s)", item, type(item).__name__)
            continue
        
        vessel_name = str(item).strip()
        if not vessel_name:
            empty_count += 1
            continue
        
        # Normalize for duplicate detection (case-insensitive, whitespace normalized)
        normalized = " ".join(vessel_name.split()).upper()
        
        # Check for duplicates using normalized form
        if normalized in normalized_vessels:
            duplicate_count += 1
            logger.warning("Duplicate vessel name found (case-insensitive): %s", vessel_name)
            continue
        
        valid_vessels.add(vessel_name)
        normalized_vessels.add(normalized)
    
    if empty_count > 0:
        logger.warning("Filtered out %d empty vessel names", empty_count)
    if duplicate_count > 0:
        logger.warning("Filtered out %d duplicate vessel names", duplicate_count)
    
    logger.info("Successfully loaded %d unique vessel names", len(valid_vessels))
    return valid_vessels



@lru_cache(maxsize=1)
def get_vessel_registry(path: Path | None = None) -> VesselRegistry:
    """Load the vessel registry from disk with caching.
    
    Thread-safety: This function uses @lru_cache which is thread-safe for reads.
    The VesselRegistry instance is immutable after creation, making it safe
    for concurrent access across multiple requests.
    """
    data_path = path or _default_data_path()
    vessels = _load_vessel_names(data_path)
    if not vessels:
        logger.warning("Vessel registry is empty!")
    return VesselRegistry(vessels)


__all__ = ["VesselRegistry", "get_vessel_registry"]
