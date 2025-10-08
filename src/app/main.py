"""Application entry point for the FastAPI service."""

from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI

from .ai_extractor import AIExtractor, get_default_extractor
from .config import Settings, get_settings
from .routes import meta as meta_routes
from .routes import validate as validate_routes
from .services.vessels import VesselRegistry, get_vessel_registry


@asynccontextmanager
def lifespan(_: FastAPI):
    """Warm up caches on startup."""

    get_vessel_registry()
    yield


def get_extractor() -> AIExtractor:
    """Dependency provider for the default extractor."""

    return get_default_extractor()


def get_vessel_registry_dependency() -> VesselRegistry:
    """Dependency provider for the vessel registry."""

    return get_vessel_registry()


def get_app_settings() -> Settings:
    """Dependency provider for application settings."""

    return get_settings()


def create_app() -> FastAPI:
    """Create and configure the FastAPI application instance."""

    settings = get_settings()
    app = FastAPI(
        title="Genoshi Backend Validator",
        version=settings.version,
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan,
    )

    app.dependency_overrides[validate_routes.get_extractor_dependency] = get_extractor
    app.dependency_overrides[validate_routes.get_vessel_registry_dependency] = (
        get_vessel_registry_dependency
    )
    app.dependency_overrides[meta_routes.get_settings_dependency] = get_app_settings

    app.include_router(meta_routes.router)
    app.include_router(validate_routes.router)

    return app


app = create_app()


__all__ = [
    "app",
    "create_app",
    "get_extractor",
    "get_vessel_registry_dependency",
    "get_app_settings",
]
