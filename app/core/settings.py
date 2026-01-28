from __future__ import annotations

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Centralized, env-first settings.

    IMPORTANT:
    - This object is cached via get_settings() to avoid re-reading env many times.
    - Tests rely on get_settings.cache_clear().
    """

    # External integrations (Module N)
    external_base_url: str = ""
    external_timeout_s: float = 3.0

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # App
    app_name: str = Field(default="rail-api", alias="APP_NAME")

    # Auth (keep behavior compatible with current tests and WWW-Authenticate)
    auth_mode: str = Field(default="none", alias="AUTH_MODE")  # none|basic|jwt
    basic_user: str = Field(default="", alias="BASIC_USER")
    basic_pass: str = Field(default="", alias="BASIC_PASS")
    jwt_secret: str = Field(default="", alias="JWT_SECRET")
    jwt_ttl_seconds: int = Field(default=3600, alias="JWT_TTL_SECONDS")

    # DB (Module M)
    database_url: str = Field(
        default="sqlite+pysqlite:///./rail_api.db",
        alias="DATABASE_URL",
    )
    db_echo: bool = Field(default=False, alias="DB_ECHO")


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
