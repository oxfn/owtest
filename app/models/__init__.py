from typing import Optional

from pydantic import BaseModel


class IdentityModel(BaseModel):
    """Adds 'id' field to model."""

    id: Optional[str]


class EntityModel(IdentityModel):
    """Adds 'title' field to model."""

    title: str
