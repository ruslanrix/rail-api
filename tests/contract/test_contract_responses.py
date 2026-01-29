from __future__ import annotations

from fastapi.testclient import TestClient

from app.schemas import HealthResponse, OkResponse, ResultResponse
import pytest

pytestmark = pytest.mark.contract


def test_contract_health(client: TestClient):
    r = client.get("/health")
    assert r.status_code == 200
    HealthResponse.model_validate(r.json())


def test_contract_math_endpoints(client: TestClient):
    r = client.get("/add", params={"a": 1, "b": 2})
    assert r.status_code == 200
    ResultResponse.model_validate(r.json())

    r = client.get("/mul", params={"a": 2, "b": 3})
    assert r.status_code == 200
    ResultResponse.model_validate(r.json())

    r = client.get("/sub", params={"a": 5, "b": 1})
    assert r.status_code == 200
    ResultResponse.model_validate(r.json())


def test_contract_notify_ok(client: TestClient, monkeypatch):
    # стабилизируем auth для теста (у тебя это уже принято)
    monkeypatch.setenv("AUTH_MODE", "none")

    r = client.post("/notify", json={"message": "hello"})
    assert r.status_code == 200
    OkResponse.model_validate(r.json())
