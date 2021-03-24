from pydantic import BaseModel

from . import IdMixin


class User(IdMixin, BaseModel):
    """User model."""

    email: str
    password: str
