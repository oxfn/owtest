from pydantic import BaseSettings


class Settings(BaseSettings):
    """Settings model."""

    secret_key: str = "the_great_hack#1337"
