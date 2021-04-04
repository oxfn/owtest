from bson import ObjectId
from faker import Faker

from app.models.users import User, UserRepository


def test_repository_construct(faker: Faker, users: UserRepository):
    user_data = {
        "_id": ObjectId(),
        "email": faker.email(),
    }
    user = users._construct(user_data.copy())
    assert user == User(id=str(user_data["_id"]), email=user_data["email"])


def test_repository_deconstruct(faker: Faker, users: UserRepository):
    user = User(id=str(ObjectId()), email=faker.email())
    user_data = users._deconstruct(user)
    assert user_data == {
        "_id": ObjectId(user.id),
        "email": user.email,
    }
