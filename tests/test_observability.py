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
