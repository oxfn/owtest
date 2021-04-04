from http import HTTPStatus as status
from fastapi import Depends, HTTPException
from fastapi.responses import Response
from fastapi.routing import APIRouter

from app.core.auth import get_user
from app.models.users import (
    DuplicateEmailException,
    Token,
    User,
    UserAuth,
    UserRepository,
)

router = APIRouter(tags=["users"])


@router.post("/registration", status_code=status.CREATED, response_model=User)
async def register(
    user: UserAuth,
    users: UserRepository = Depends(),
):
    """Register new user."""
    try:
        user = await users.register(user)
    except DuplicateEmailException:
        raise HTTPException(
            status_code=status.BAD_REQUEST, detail="This email is already registered"
        )
    else:
        return user


@router.post("/login", response_model=Token)
async def login(user: UserAuth, users: UserRepository = Depends()):
    """Authenticate user."""
    token = await users.authenticate(user)
    if not token:
        raise HTTPException(
            status_code=status.UNAUTHORIZED, detail="Invalid credentials"
        )
    return Token(token=token)


@router.post(
    "/logout",
)
async def logout(users: UserRepository = Depends(), me=Depends(get_user)):
    """Log out current user."""
    await users.logout(me)
    return Response()
