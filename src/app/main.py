"""Application entry point for the FastAPI service."""

from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import RedirectResponse

import logging
import sys

from .ai_extractor import AIExtractor, get_default_extractor
from .config import Settings, get_settings
from .routes import meta as meta_routes
from .routes import validate as validate_routes
from .services.vessels import VesselRegistry, get_vessel_registry

logger = logging.getLogger(__name__)


def setup_logging(settings: Settings) -> None:
    """Configure structured logging for the application."""

    logging.basicConfig(
        level=settings.log_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        stream=sys.stdout,
        force=True,
    )
    logger.info("Logging initialized with level: %s", settings.log_level)


@asynccontextmanager
async def lifespan(_: FastAPI):
    """Warm up caches and handle startup/shutdown."""
    settings = get_settings()
    setup_logging(settings)
    
    logger.info("Starting up Genoshi Backend Validator v%s", settings.version)
    try:
        registry = get_vessel_registry()
        if registry.is_empty:
            logger.warning(
                "⚠️  Vessel registry is EMPTY - all vessel validations will fail! "
                "Check that src/app/data/valid_vessels.json exists and contains vessel names."
            )
        else:
            logger.info("Vessel registry warmed up with %d vessels", len(registry))
    except Exception as e:
        logger.error("Failed to warm up vessel registry: %s", e)
    
    yield
    logger.info("Shutting down Genoshi Backend Validator")


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

    app.include_router(meta_routes.router)
    app.include_router(validate_routes.router)

    @app.get("/", include_in_schema=False)
    async def root() -> RedirectResponse:
        """Redirect the root path to the interactive docs."""
        return RedirectResponse(url="/docs")

    return app


app = create_app()


__all__ = [
    "app",
    "create_app",
    "get_extractor",
    "get_vessel_registry_dependency",
    "get_app_settings",
]
