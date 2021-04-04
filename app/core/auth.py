from fastapi import Depends
from fastapi.exceptions import HTTPException
from fastapi.security import OAuth2PasswordBearer

from app.models.users import User, UserRepository

get_token = OAuth2PasswordBearer(tokenUrl="/login")


async def get_user(
    token: str = Depends(get_token), users: UserRepository = Depends()
) -> User:
    """Get current authenticated user."""
    user = await users.get(token=token)
    if user:
        return user
    raise HTTPException(status_code=403, detail="Invalid token")
