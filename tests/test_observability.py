from __future__ import annotations

from fastapi.testclient import TestClient

import app.main as main_mod


def test_request_id_generated_and_propagated():
    client = TestClient(main_mod.app)

    response = client.get("/")
    assert response.status_code == 200
    request_id = response.headers.get("X-Request-ID")
    assert request_id


def test_request_id_respected_when_provided():
    client = TestClient(main_mod.app)

    response = client.get("/health", headers={"X-Request-ID": "req-123"})
    assert response.status_code == 200
    assert response.headers.get("X-Request-ID") == "req-123"


def test_metrics_endpoint_prometheus_format():
    client = TestClient(main_mod.app)

    client.get("/")
    metrics_response = client.get("/metrics")

    assert metrics_response.status_code == 200
    assert metrics_response.headers["content-type"].startswith("text/plain")
    body = metrics_response.text
    assert "# HELP http_requests_total" in body
    assert 'http_requests_total{method="GET",path="/",status="200"}' in body


@main_mod.app.get("/boom")
def boom():
    raise RuntimeError("boom")


def test_request_id_and_metrics_on_unhandled_exception():
    client = TestClient(main_mod.app, raise_server_exceptions=False)

    response = client.get("/boom")
    assert response.status_code == 500
    request_id = response.headers.get("X-Request-ID")
    assert request_id
    assert response.json() == {"detail": "Internal Server Error"}

    metrics_response = client.get("/metrics")
    assert metrics_response.status_code == 200
    assert 'http_requests_total{method="GET",path="/boom",status="500"}' in metrics_response.text
