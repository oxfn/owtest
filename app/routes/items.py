from http import HTTPStatus as status
from typing import List

from bson import ObjectId
from fastapi import Depends, Body
from fastapi.exceptions import HTTPException
from fastapi.param_functions import Query
from fastapi.routing import APIRouter
from starlette.requests import Request

from app.core.auth import get_user
from app.core.utils import encode_share_key, decode_share_key
from app.models.items import (
    Item,
    ItemCreate,
    ItemRepository,
    ItemSendRequest,
    ItemSendResponse,
)
from app.models.users import User, UserRepository

router = APIRouter(tags=["items"])


@router.post("/items/new", response_model=Item, status_code=status.CREATED)
async def create_item(
    item: Item = Body(...),
    items: ItemRepository = Depends(),
    me: User = Depends(get_user),
):
    """Create new item."""
    return await items.create(ItemCreate(**item.dict(), user_id=me.id))


@router.get("/items", response_model=List[Item])
async def get_items(
    items: ItemRepository = Depends(),
    me: User = Depends(get_user),
):
    """Get user's items list."""
    data = await items.get_all(user_id=ObjectId(me.id))
    return data


@router.get("/items/{item_id}", response_model=Item)
async def get_item(
    item_id: str,
    items: ItemRepository = Depends(),
    me: User = Depends(get_user),
):
    item = await items.get(_id=ObjectId(item_id), user_id=ObjectId(me.id))
    if item:
        return item
    raise HTTPException(status_code=404)


@router.post("/send", response_model=ItemSendResponse)
async def send_item(
    request: Request,
    body: ItemSendRequest = Body(...),
    me: User = Depends(get_user),
    items: ItemRepository = Depends(),
    users: UserRepository = Depends(),
):
    """Send item to another user."""
    item = await items.get(_id=ObjectId(body.item_id), user_id=ObjectId(me.id))
    if not item:
        raise HTTPException(status_code=status.NOT_FOUND, detail="Item not found")
    user = await users.get(email=body.email)
    if not user:
        raise HTTPException(status_code=status.NOT_FOUND, detail="User not found")
    key = encode_share_key(body.item_id, user.id)
    url = f"{request.url_for('receive_item')}?key={key}"
    return ItemSendResponse(url=url)


@router.get("/get", response_model=Item)
async def receive_item(
    key: str = Query(...),
    me: User = Depends(get_user),
    items: ItemRepository = Depends(),
):
    """Receive item by secret key."""
    try:
        item_id, user_id = decode_share_key(key)
    except Exception:
        raise HTTPException(status_code=status.BAD_REQUEST, detail="Invalid key")
    else:
        if user_id != me.id:
            raise HTTPException(status_code=status.FORBIDDEN, detail="Access denied")
        item = await items.send(item_id, user_id)
        return item
