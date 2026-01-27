"""Meta endpoints such as health checks and version info."""

from __future__ import annotations

from typing import Union

from fastapi import APIRouter, Depends

from ..config import Settings, get_settings
from ..services.vessels import VesselRegistry, get_vessel_registry

router = APIRouter(tags=["meta"])



@router.get("/health")
async def health(
    vessels: VesselRegistry = Depends(get_vessel_registry)
) -> dict[str, Union[str, int]]:
    """Return application health status."""
    
    try:
        if vessels.is_empty:
            return {"status": "degraded", "reason": "vessel registry empty"}

        return {"status": "ok", "vessels_loaded": len(vessels)}
    except Exception as e:
        # Return degraded status instead of crashing
        return {"status": "degraded", "reason": f"health check error: {str(e)}"}



@router.get("/version")
async def version(settings: Settings = Depends(get_settings)) -> dict[str, str]:
    """Return the application version."""
    
    try:
        return {"version": settings.version}
    except Exception as e:
        # Return error version instead of crashing
        return {"version": "unknown", "error": str(e)}


__all__ = ["router"]
