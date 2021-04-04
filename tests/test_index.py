from http import HTTPStatus as status

from . import client


def test_index():
    res = client.get("/")
    assert res.status_code == status.OK
    assert "Hello" in res.text
