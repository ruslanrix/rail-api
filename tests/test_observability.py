from __future__ import annotations

import importlib
import os

from fastapi.testclient import TestClient


def make_client(*, obs_enabled: bool) -> TestClient:
    # важно: env должен быть выставлен ДО импорта app.main
    if obs_enabled:
        os.environ["OBS_ENABLED"] = "1"
    else:
        os.environ.pop("OBS_ENABLED", None)

    import app.main as main_mod

    importlib.reload(main_mod)
    return TestClient(main_mod.app)


def test_request_id_generated_and_propagated():
    client = make_client(obs_enabled=False)

    r = client.get("/health")
    assert r.status_code == 200
    assert r.headers.get("X-Request-ID")


def test_request_id_respected_when_provided():
    client = make_client(obs_enabled=False)

    r = client.get("/health", headers={"X-Request-ID": "req-123"})
    assert r.status_code == 200
    assert r.headers.get("X-Request-ID") == "req-123"


def test_starts_without_observability_env():
    client = make_client(obs_enabled=False)

    r = client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}
    assert "X-Request-ID" in r.headers


def test_metrics_disabled_by_default():
    client = make_client(obs_enabled=False)

    r = client.get("/metrics")
    assert r.status_code == 404


def test_metrics_endpoint_prometheus_format_when_enabled():
    client = make_client(obs_enabled=True)

    client.get("/health")
    metrics_response = client.get("/metrics")

    assert metrics_response.status_code == 200
    assert metrics_response.headers["content-type"].startswith("text/plain")
    body = metrics_response.text
    assert "# HELP http_requests_total" in body
    assert 'http_requests_total{method="GET",path="/health",status="200"}' in body


def test_request_id_and_metrics_on_unhandled_exception_when_enabled():
    client = make_client(obs_enabled=True)

    # добавляем маршрут на "свежий" app, созданный через reload,
    # поэтому не загрязняем другие тесты
    import app.main as main_mod

    @main_mod.app.get("/boom")
    def boom():
        raise RuntimeError("boom")

    client = TestClient(main_mod.app, raise_server_exceptions=False)

    response = client.get("/boom")
    assert response.status_code == 500
    assert response.headers.get("X-Request-ID")
    assert response.json() == {"detail": "Internal Server Error"}

    metrics_response = client.get("/metrics")
    assert metrics_response.status_code == 200
    assert 'http_requests_total{method="GET",path="/boom",status="500"}' in metrics_response.text
