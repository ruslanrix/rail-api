from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_div_ok():
    r = client.get("/div", params={"a": 10, "b": 2})
    assert r.status_code == 200
    assert r.json() == {"result": 5.0}


def test_div_by_zero():
    r = client.get("/div", params={"a": 10, "b": 0})
    assert r.status_code == 400
    assert r.json() == {"detail": "Division by zero"}
