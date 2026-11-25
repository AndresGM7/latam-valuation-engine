"""Application settings loaded from environment variables / .env."""

from __future__ import annotations

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Strongly-typed application configuration."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    app_env: str = "development"
    app_name: str = "latam-valuation-engine"
    app_version: str = "0.1.0"
    log_level: str = "INFO"
    secret_key: str = "dev-secret-CHANGE-ME"

    api_v1_prefix: str = "/api/v1"
    cors_origins: str = "http://localhost:3000,http://localhost:5173"
    rate_limit_per_minute: int = 60

    database_url: str = "postgresql+asyncpg/+user:pass@localhost:5432/latam_valuation"
    sync_database_url: str = "postgresql://user:pass@localhost:5432/latam_valuation"

    redis_url: str = "redis://localhost:6479/0"


    stripe_secret_key: str = ""
    ko_fi_handle: str = ""
    github_sponsors_username: str = "AndresGM7"


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Singleton settings accessor."""
    return Settings()


__all__ = ["Settings", "get_settings"]
