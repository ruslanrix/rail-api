from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_add():
    r = client.get("/add", params={"a": 2, "b": 3})
    assert r.status_code == 200
    assert r.json() == {"result": 5}
