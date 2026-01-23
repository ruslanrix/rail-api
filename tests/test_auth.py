from __future__ import annotations

from datetime import datetime, timedelta, timezone

import jwt
import pytest
from fastapi.testclient import TestClient

import app.main as main_mod


@pytest.fixture()
def client():
    return TestClient(main_mod.app)


def test_basic_required(client: TestClient, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("AUTH_MODE", "basic")
    monkeypatch.setenv("BASIC_USER", "demo")
    monkeypatch.setenv("BASIC_PASS", "secret")

    r = client.post("/notify", json={"message": "hello"})
    assert r.status_code == 401
    assert r.headers.get("www-authenticate") == "Basic"


def test_basic_valid(client: TestClient, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("AUTH_MODE", "basic")
    monkeypatch.setenv("BASIC_USER", "demo")
    monkeypatch.setenv("BASIC_PASS", "secret")

    r = client.post("/notify", json={"message": "hello"}, auth=("demo", "secret"))
    assert r.status_code == 200
    assert r.json() == {"ok": True}


def test_basic_invalid(client: TestClient, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("AUTH_MODE", "basic")
    monkeypatch.setenv("BASIC_USER", "demo")
    monkeypatch.setenv("BASIC_PASS", "secret")

    r = client.post("/notify", json={"message": "hello"}, auth=("demo", "wrong"))
    assert r.status_code == 401


def test_jwt_required(client: TestClient, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("AUTH_MODE", "jwt")
    monkeypatch.setenv("JWT_SECRET", "secret")

    r = client.post("/notify", json={"message": "hello"})
    assert r.status_code == 401
    assert r.headers.get("www-authenticate") == "Bearer"


def test_jwt_valid(client: TestClient, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("AUTH_MODE", "jwt")
    monkeypatch.setenv("JWT_SECRET", "secret")

    payload = {"sub": "demo", "exp": datetime.now(timezone.utc) + timedelta(minutes=5)}
    token = jwt.encode(payload, "secret", algorithm="HS256")

    r = client.post(
        "/notify",
        json={"message": "hello"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == 200
    assert r.json() == {"ok": True}


def test_jwt_invalid(client: TestClient, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("AUTH_MODE", "jwt")
    monkeypatch.setenv("JWT_SECRET", "secret")

    r = client.post(
        "/notify",
        json={"message": "hello"},
        headers={"Authorization": "Bearer not-a-token"},
    )
    assert r.status_code == 401


def test_jwt_expired(client: TestClient, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("AUTH_MODE", "jwt")
    monkeypatch.setenv("JWT_SECRET", "secret")

    payload = {"sub": "demo", "exp": datetime.now(timezone.utc) - timedelta(minutes=1)}
    token = jwt.encode(payload, "secret", algorithm="HS256")

    r = client.post(
        "/notify",
        json={"message": "hello"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == 401


def test_token_success(client: TestClient, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("BASIC_USER", "demo")
    monkeypatch.setenv("BASIC_PASS", "secret")
    monkeypatch.setenv("JWT_SECRET", "secret")

    r = client.post("/token", auth=("demo", "secret"))
    assert r.status_code == 200
    body = r.json()
    assert body["token_type"] == "bearer"
    assert "access_token" in body


def test_token_failure(client: TestClient, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("BASIC_USER", "demo")
    monkeypatch.setenv("BASIC_PASS", "secret")
    monkeypatch.setenv("JWT_SECRET", "secret")

    r = client.post("/token", auth=("demo", "wrong"))
    assert r.status_code == 401
