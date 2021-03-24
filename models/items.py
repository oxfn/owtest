from pydantic import BaseModel
from . import IdMixin


class Item(IdMixin, BaseModel):
    """Item model."""

    title: str
