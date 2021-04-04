from bson import ObjectId

from pydantic import BaseModel, EmailStr, HttpUrl
from pydantic.fields import Field

from app.core.db import BaseRepository
from . import EntityModel


class Item(EntityModel):
    """Item model."""


class ItemCreate(Item):
    """Item model for creation."""

    user_id: str


class ItemSendRequest(BaseModel):
    """Item send request."""

    item_id: str = Field(regex=r"[0-9a-f]{,64}")
    email: EmailStr


class ItemSendResponse(BaseModel):
    """Model for sending item response."""

    url: HttpUrl


class ItemRepository(BaseRepository):
    collection_name = "items"
    model_type = Item

    async def send(self, item_id: str, user_id: str):
        """Rebind item to another user."""
        await self.col.update_one(
            {"_id": ObjectId(item_id)}, {"$set": {"user_id": ObjectId(user_id)}}
        )
        db_item = await self.col.find_one({"_id": ObjectId(item_id)})
        return self._construct(db_item)
