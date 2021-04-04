from http import HTTPStatus as status

from bson import ObjectId
from faker import Faker

from . import client, db, AuthData
from .conftest import CreateUserFunc

REGISTRATION_PATH = "/registration"
LOGIN_PATH = "/login"
LOGOUT_PATH = "/logout"


def test_registration(faker):
    req = {"email": faker.email(), "password": faker.password()}
    res = client.post(REGISTRATION_PATH, json=req)
    assert res.status_code == status.CREATED
    data = res.json()
    assert data.get("id")
    assert data.get("email") == req["email"]
    user = db.users.find_one({"_id": ObjectId(data["id"])})
    assert user
    assert user["salt"]
    assert user["password"] != req["password"]
    db.users.delete_one({"_id": ObjectId(data["id"])})


def test_duplicate_email(faker: Faker, create_user: CreateUserFunc):
    user = create_user()[0]
    req = {"email": user["email"], "password": faker.password()}
    res = client.post(REGISTRATION_PATH, json=req)
    assert res.status_code == status.BAD_REQUEST
    assert res.json() == {"detail": "This email is already registered"}


def test_login(auth: AuthData):
    req = {"email": auth.email, "password": auth.password}
    res = client.post(LOGIN_PATH, json=req)
    assert res.status_code == status.OK
    data = res.json()
    assert data.get("token")


def test_login_failed(faker: Faker):
    req = {"email": faker.email(), "password": faker.password()}
    res = client.post(LOGIN_PATH, json=req)
    assert res.status_code == status.UNAUTHORIZED
    assert res.json() == {"detail": "Invalid credentials"}


def test_logout(auth: AuthData):
    res = client.post(LOGOUT_PATH, headers=auth.headers)
    assert res.status_code == status.OK
    user = db.users.find_one({"_id": ObjectId(auth.id)})
    assert "token" not in user


def test_invalid_token():
    res = client.post(LOGOUT_PATH, headers={"Authorization": "bearer qwertyasdfg"})
    assert res.status_code == status.FORBIDDEN
    assert res.json() == {"detail": "Invalid token"}
