from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_mul():
    r = client.get("/mul", params={"a": 2, "b": 3})
    assert r.status_code == 200
    assert r.json() == {"result": 6}
