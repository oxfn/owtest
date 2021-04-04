import logging
from typing import Iterable, Type

from bson import ObjectId
from fastapi import Depends
from motor.core import AgnosticClient, AgnosticCollection, AgnosticDatabase
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.results import InsertOneResult

from app.models import IdentityModel
from .settings import Settings, get_settings

logger = logging.getLogger(__name__)


async def get_db(settings: Settings = Depends(get_settings)):
    """Initialize database."""
    try:
        client: AgnosticClient = AsyncIOMotorClient(settings.mongo_url)
        yield client.get_database()
    finally:
        client.close()


class BaseRepository:
    """Base repository class."""

    collection_name: str = ""
    model_type: Type[IdentityModel] = IdentityModel

    def __init__(self, db: AgnosticDatabase = Depends(get_db, use_cache=True)):
        """Initializer."""
        self.col: AgnosticCollection = db[self.collection_name]

    def _construct(self, attrs: dict) -> model_type:
        """Construct Pydantic model from Mongo object dict."""
        attrs["id"] = str(attrs["_id"])
        return self.model_type(**attrs)

    def _deconstruct(self, obj: model_type) -> dict:
        """Deconstructs model for Mongo."""
        attrs = obj.dict()
        if attrs.get("id"):
            attrs["_id"] = ObjectId(attrs["id"])
        del attrs["id"]
        return attrs

    async def get(self, **attrs) -> model_type:
        """Get one item."""
        db_item: dict = await self.col.find_one(attrs)
        return self._construct(db_item) if db_item else None

    async def get_all(self, **attrs) -> Iterable[model_type]:
        """Get one item."""
        db_items: Iterable[dict] = self.col.find(attrs)
        return [self._construct(i) async for i in db_items]

    async def create(self, obj: model_type) -> model_type:
        """Create item."""
        res: InsertOneResult = await self.col.insert_one(self._deconstruct(obj))
        db_item = await self.col.find_one(res.inserted_id)
        return self._construct(db_item)
