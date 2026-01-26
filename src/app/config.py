"""Application configuration using pydantic-settings."""

from functools import lru_cache
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables and .env files."""

    model_config = SettingsConfigDict(
        env_file=(".env", ".env.local"),
        env_file_encoding="utf-8",
        env_prefix="APP_",
        extra="ignore",
    )

    env: Literal["dev", "test", "prod"] = "dev"
    version: str = "0.1.0"
    log_level: str = "INFO"


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return cached application settings instance.
    
    Thread-safety: This function uses @lru_cache which is thread-safe for reads.
    Settings are immutable after creation, making them safe for concurrent access.
    """
    return Settings()


__all__ = ["Settings", "get_settings"]
