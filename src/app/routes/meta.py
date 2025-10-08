"""Meta endpoints such as health checks and version info."""

from __future__ import annotations

from fastapi import APIRouter, Depends

from ..config import Settings, get_settings

router = APIRouter(tags=["meta"])


def get_settings_dependency() -> Settings:
    return get_settings()


@router.get("/health")
async def health() -> dict[str, str]:
    """Return application health status."""

    return {"status": "ok"}


@router.get("/version")
async def version(settings: Settings = Depends(get_settings_dependency)) -> dict[str, str]:
    """Return the application version."""

    return {"version": settings.version}


__all__ = ["router", "get_settings_dependency"]
