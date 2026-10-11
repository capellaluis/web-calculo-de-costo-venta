"""
config.py — Environment-driven configuration.

All settings are read from environment variables or a .env file.
Use get_settings() everywhere — never instantiate Settings directly.
The @lru_cache ensures a singleton: env is parsed only once per process.
"""
from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application-wide configuration loaded from .env or environment."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_prefix="SKILL_",       # <- change per project, e.g. RECON_
        case_sensitive=False,
    )

    # ------------------------------------------------------------------ #
    #  Add your settings below. All are overridable via env vars.         #
    # ------------------------------------------------------------------ #
    max_connections: int = Field(default=50, gt=0)
    global_timeout: int = Field(default=20, gt=0)
    log_level: str = Field(default="INFO", pattern="^(DEBUG|INFO|WARNING|ERROR|CRITICAL)$")

    # Example: optional API keys
    # api_key: str | None = Field(default=None)


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return the cached Settings singleton. Safe to call anywhere."""
    return Settings()
