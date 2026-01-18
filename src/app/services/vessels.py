"""Vessel registry service for validation dependencies."""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Iterable


class VesselRegistry:
    """Stores the set of valid vessel names."""

    def __init__(self, vessels: Iterable[str]):
        self._vessels: set[str] = {v.upper().strip() for v in vessels if v.strip()}

    def is_allowed(self, name: str | None) -> bool:
        """Return ``True`` when the vessel name is registered."""

        if name is None:
            return False
        return name.upper().strip() in self._vessels

    def all(self) -> set[str]:
        """Return a copy of the known vessel names."""

        return set(self._vessels)


def _default_data_path() -> Path:
    # src/app/services/vessels.py -> src/app/data/valid_vessels.json
    return Path(__file__).resolve().parent.parent / "data" / "valid_vessels.json"


def _load_vessel_names(path: Path) -> set[str]:
    with path.open("r", encoding="utf-8") as fp:
        items = json.load(fp)
    if not isinstance(items, list):
        raise ValueError("valid_vessels.json must contain a list of strings")
    return {str(item).strip() for item in items if str(item).strip()}


@lru_cache(maxsize=1)
def get_vessel_registry(path: Path | None = None) -> VesselRegistry:
    """Load the vessel registry from disk with caching."""

    data_path = path or _default_data_path()
    vessels = _load_vessel_names(data_path)
    return VesselRegistry(vessels)


__all__ = ["VesselRegistry", "get_vessel_registry"]
