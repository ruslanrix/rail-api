from __future__ import annotations

from fastapi.testclient import TestClient


def test_notify_schedules_background_delivery(monkeypatch, client: TestClient):
    monkeypatch.setenv("AUTH_MODE", "none")

    calls: list[tuple[str, str | None]] = []

    def fake_deliver_notification(message: str, request_id: str | None) -> None:
        calls.append((message, request_id))

    # routes.py imports deliver_notification from app.notification -> patch in routes module
    import app.api.routes as routes_mod

    monkeypatch.setattr(routes_mod, "deliver_notification", fake_deliver_notification)

    r = client.post("/notify", json={"message": "hello"}, headers={"x-request-id": "rid-123"})
    assert r.status_code == 200
    assert r.json() == {"ok": True}

    # In TestClient, background tasks execute during response finalization.
    assert calls == [("hello", "rid-123")]
