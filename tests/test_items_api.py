from http import HTTPStatus as status
from random import randint
from typing import Callable, Optional

import pytest
from bson import ObjectId
from faker import Faker
from pymongo.results import InsertOneResult

from app.core.utils import encode_share_key
from . import AuthData, client, db
from .conftest import CreateUserFunc

CREATE_PATH = "/items/new"
LIST_PATH = "/items"
DETAIL_PATH = "/items/{id}"
SEND_PATH = "/send"
RECEIVE_PATH = "/get?key={key}"

CreateItemFunc = Callable[[Optional[str]], dict]


@pytest.fixture
def create_item(request, faker: Faker) -> CreateItemFunc:
    def _create(user_id: Optional[str] = None) -> dict:
        _uid = ObjectId(user_id) if user_id else ObjectId()
        res: InsertOneResult = db.items.insert_one(
            {
                "user_id": _uid,
                "title": faker.sentence(),
            }
        )
        _item = db.items.find_one({"_id": res.inserted_id})
        return _item

    yield _create


def test_item_new(faker: Faker, auth: AuthData):
    req = {"title": faker.sentence()}
    res = client.post(CREATE_PATH, json=req, headers=auth.headers)
    assert res.status_code == status.CREATED
    data = res.json()
    assert "id" in data and data["id"]
    assert data["title"] == req["title"]
    db_item = db.items.find_one({"_id": ObjectId(data["id"])})
    assert db_item and db_item["title"] == req["title"]


def test_items_list(create_item: CreateItemFunc, auth: AuthData):
    items = [create_item(auth.id) for _ in range(randint(2, 4))]
    [create_item() for _ in range(1, 3)]  # noise
    res = client.get(LIST_PATH, headers=auth.headers)
    assert res.status_code == status.OK
    data = res.json()
    assert type(data) is list
    assert len(items) == len(data)
    assert [i["title"] for i in data] == [i["title"] for i in items]


def test_item_detail(create_item: CreateItemFunc, auth: AuthData):
    item = create_item(auth.id)
    url = DETAIL_PATH.format(id=str(item["_id"]))
    res = client.get(url, headers=auth.headers)
    assert res.status_code == status.OK
    assert res.json() == {"id": str(item["_id"]), "title": item["title"]}


def test_foreign_item_not_found(create_item: CreateItemFunc, auth: AuthData):
    item = create_item()
    url = DETAIL_PATH.format(id=str(item["_id"]))
    res = client.get(url, headers=auth.headers)
    assert res.status_code == status.NOT_FOUND


def test_send_item(
    create_item: CreateItemFunc, create_user: CreateUserFunc, auth: AuthData
):
    item = create_item(auth.id)
    user, _, __ = create_user()
    res = client.post(
        SEND_PATH,
        json={
            "item_id": str(item["_id"]),
            "email": user["email"],
        },
        headers=auth.headers,
    )
    assert res.status_code == status.OK
    data = res.json()
    assert "url" in data and data["url"]


def test_item_not_found(auth: AuthData, create_user: CreateUserFunc):
    user = create_user()[0]
    req = {"item_id": str(ObjectId()), "email": user["email"]}
    res = client.post(SEND_PATH, json=req, headers=auth.headers)
    assert res.status_code == status.NOT_FOUND
    assert res.json() == {"detail": "Item not found"}


def test_user_not_found(auth: AuthData, create_item: CreateUserFunc, faker: Faker):
    item = create_item(auth.id)
    req = {"item_id": str(item["_id"]), "email": faker.email()}
    res = client.post(SEND_PATH, json=req, headers=auth.headers)
    assert res.status_code == status.NOT_FOUND
    assert res.json() == {"detail": "User not found"}


def test_receive_item(
    create_user: CreateUserFunc, create_item: CreateItemFunc, auth: AuthData
):
    user = create_user()[0]
    item = create_item(user["_id"])
    key = encode_share_key(str(item["_id"]), auth.id)
    url = RECEIVE_PATH.format(key=key)
    res = client.get(url, headers=auth.headers)
    assert res.status_code == status.OK
    assert res.json() == {"id": str(item["_id"]), "title": item["title"]}
    item = db.items.find_one({"_id": item["_id"]})
    assert str(item["user_id"]) == auth.id


def test_receive_item_invalid_key(auth: AuthData, faker: Faker):
    url = RECEIVE_PATH.format(key=faker.hexify("^" * 64))
    res = client.get(url, headers=auth.headers)
    assert res.status_code == status.BAD_REQUEST
    assert res.json() == {"detail": "Invalid key"}


def test_receive_item_access_denied(auth: AuthData, create_item: CreateItemFunc):
    item = create_item(auth.id)
    key = encode_share_key(str(item["_id"]), str(ObjectId()))
    url = RECEIVE_PATH.format(key=key)
    res = client.get(url, headers=auth.headers)
    assert res.status_code == status.FORBIDDEN
