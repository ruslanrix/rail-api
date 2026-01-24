from __future__ import annotations

import base64
import hashlib
import hmac
import json
from datetime import datetime, timedelta, timezone
import pytest
from fastapi.testclient import TestClient

import app.main as main_mod


@pytest.fixture()
def client():
    return TestClient(main_mod.app)


def _b64url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("utf-8")


def _sign(message: bytes, secret: str) -> str:
    digest = hmac.new(secret.encode("utf-8"), message, hashlib.sha256).digest()
    return _b64url_encode(digest)


def _encode_jwt(payload: dict, secret: str) -> str:
    header = {"alg": "HS256", "typ": "JWT"}
    header_b64 = _b64url_encode(json.dumps(header, separators=(",", ":")).encode("utf-8"))
    payload_b64 = _b64url_encode(json.dumps(payload, separators=(",", ":")).encode("utf-8"))
    signing_input = f"{header_b64}.{payload_b64}".encode("utf-8")
    signature = _sign(signing_input, secret)
    return f"{header_b64}.{payload_b64}.{signature}"


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

    payload = {
        "sub": "demo",
        "exp": int((datetime.now(timezone.utc) + timedelta(minutes=5)).timestamp()),
    }
    token = _encode_jwt(payload, "secret")

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

    payload = {
        "sub": "demo",
        "exp": int((datetime.now(timezone.utc) - timedelta(minutes=1)).timestamp()),
    }
    token = _encode_jwt(payload, "secret")

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
