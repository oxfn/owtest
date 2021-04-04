from collections import namedtuple
import pymongo
from fastapi.testclient import TestClient

from app import app
from app.core.settings import get_settings

settings = get_settings()
db = pymongo.MongoClient(settings.mongo_url).get_database()

# Drop existing test collections
if settings.testing:
    for c in ["items", "users"]:
        db.get_collection(c).drop()

# TestAuth type for authentication fixture
AuthData = namedtuple("TestAuth", ["id", "email", "password", "token", "headers"])

client = TestClient(app, base_url="http://test.com")
