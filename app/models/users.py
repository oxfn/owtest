from bson import ObjectId
from pydantic import BaseModel

from app.core.db import BaseRepository
from app.core.utils import get_password_hash, get_random_string
from . import IdentityModel


class User(IdentityModel):
    """Base User model."""

    email: str


class UserAuth(User):
    """User model for registration and authentication."""

    password: str


class UserCreate(UserAuth):
    """User model for creation."""

    salt: str


class Token(BaseModel):
    """Token response model."""

    token: str


class DuplicateEmailException(Exception):
    pass


class UserRepository(BaseRepository):
    collection_name = "users"
    model_type = User

    async def register(self, user: UserAuth) -> User:
        """Register user."""
        db_user = await self.col.find_one({"email": user.email})
        if db_user:
            raise DuplicateEmailException()
        attrs = user.dict()
        attrs["salt"], attrs["password"] = get_password_hash(user.password)
        return await self.create(UserCreate(**attrs))

    async def authenticate(self, user: UserAuth) -> str:
        """Authenticate user."""
        db_user = await self.col.find_one({"email": user.email})
        if db_user:
            _, password_hash = get_password_hash(user.password, db_user["salt"])
            if db_user["password"] == password_hash:
                await self.col.update_one(
                    {"_id": db_user["_id"]}, {"$set": {"token": get_random_string()}}
                )
                db_user = await self.col.find_one({"_id": db_user["_id"]})
                return db_user["token"]

    async def logout(self, user: User):
        """Log out user by token."""
        db_user = await self.col.find_one({"_id": ObjectId(user.id)})
        if db_user:
            await self.col.update_one(
                {"_id": db_user["_id"]}, {"$unset": {"token": None}}
            )
