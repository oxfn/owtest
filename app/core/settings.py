from functools import lru_cache

from pydantic import BaseSettings


class Settings(BaseSettings):
    """Settings model."""

    secret_key: str = ""
    mongo_url: str = ""
    testing: bool = False


@lru_cache(typed=False)
def get_settings() -> Settings:
    """Initialize settings."""
    return Settings()
