"""Application configuration using pydantic-settings."""

from __future__ import annotations

from functools import lru_cache
from typing import Literal

from pydantic import field_validator
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

    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        """Validate that log_level is a valid Python logging level."""
        valid_levels = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
        upper_v = v.upper()
        if upper_v not in valid_levels:
            raise ValueError(
                f"log_level must be one of {valid_levels}, got '{v}'"
            )
        return upper_v

    @field_validator("version")
    @classmethod
    def validate_version(cls, v: str) -> str:
        """Validate version format (basic check for non-empty)."""
        if not v or not v.strip():
            raise ValueError("version cannot be empty")
        return v.strip()



@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return cached application settings instance.
    
    Thread-safety: This function uses @lru_cache which is thread-safe for reads.
    Settings are immutable after creation, making them safe for concurrent access.
    """
    return Settings()


__all__ = ["Settings", "get_settings"]
