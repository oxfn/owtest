from datetime import datetime
from typing import Callable, Tuple

import pytest
from faker import Faker
from pymongo.results import InsertOneResult

from app.core.utils import get_password_hash
from app.models.users import UserRepository
from . import AuthData, db


CreateUserFunc = Callable[[], Tuple[dict, str, str]]


@pytest.fixture(autouse=True)
def random_seed(faker: Faker):
    faker.seed_instance(int(datetime.utcnow().timestamp() * 10 ** 6))


@pytest.fixture
def users():
    return UserRepository(db)


@pytest.fixture
def create_user(request, faker: Faker) -> CreateUserFunc:
    def _create():
        global _user
        password = faker.password()
        token = faker.hexify("^" * 32)
        salt, password_hash = get_password_hash(password)
        res: InsertOneResult = db.users.insert_one(
            {
                "email": faker.email(),
                "password": password_hash,
                "salt": salt,
                "token": token,
            }
        )
        _user = db.users.find_one({"_id": res.inserted_id})
        return _user, password, token

    yield _create


@pytest.fixture
def auth(create_user: CreateUserFunc):
    user, password, token = create_user()
    yield AuthData(
        id=str(user["_id"]),
        email=user["email"],
        password=password,
        token=token,
        headers={"Authorization": f"bearer {token}"},
    )
