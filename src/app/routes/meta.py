"""Meta endpoints such as health checks and version info."""

from __future__ import annotations

from fastapi import APIRouter, Depends

from ..config import Settings, get_settings
from ..services.vessels import VesselRegistry, get_vessel_registry

router = APIRouter(tags=["meta"])



@router.get("/health")
async def health(
    vessels: VesselRegistry = Depends(get_vessel_registry)
) -> dict[str, str]:
    """Return application health status."""
    
    if vessels.is_empty:
         return {"status": "degraded", "reason": "vessel registry empty"}

    return {"status": "ok", "vessels_loaded": str(len(vessels))}


@router.get("/version")
async def version(settings: Settings = Depends(get_settings)) -> dict[str, str]:
    """Return the application version."""

    return {"version": settings.version}


__all__ = ["router"]
