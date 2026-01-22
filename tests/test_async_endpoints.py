from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

import app.main as main_mod


@pytest.fixture()
def client():
    return TestClient(main_mod.app)


@pytest.mark.parametrize(
    "seconds, expected",
    [
        (-10, 0.0),
        (0, 0.0),
        (1, 1.0),
        (10, 5.0),  # clamp high
    ],
)
def test_sleep_clamp_and_response(
    client: TestClient, monkeypatch: pytest.MonkeyPatch, seconds: float, expected: float
):
    async def fake_sleep(_):
        return None

    monkeypatch.setattr(main_mod.asyncio, "sleep", fake_sleep)

    r = client.get("/sleep", params={"seconds": seconds})
    assert r.status_code == 200
    assert r.json() == {"slept": expected}


def test_notify_ok(client: TestClient):
    r = client.post("/notify", json={"message": "hello"})
    assert r.status_code == 200
    assert r.json() == {"ok": True}


@pytest.mark.parametrize(
    "message",
    [
        "",
        "x" * 201,
    ],
)
def test_notify_validation(client: TestClient, message: str):
    r = client.post("/notify", json={"message": message})
    # Pydantic validation error
    assert r.status_code == 422
