from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_sub():
    r = client.get("/sub", params={"a": 5, "b": 3})
    assert r.status_code == 200
    assert r.json() == {"result": 2}
