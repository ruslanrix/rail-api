from __future__ import annotations

import httpx
from fastapi.testclient import TestClient

import app.main as main_mod


def test_external_ping_ok(monkeypatch):
    async def handler(request: httpx.Request) -> httpx.Response:
        assert request.method == "GET"
        assert request.url.path == "/ping"
        return httpx.Response(200, json={"pong": True})

    transport = httpx.MockTransport(handler)
    # Важно: base_url для MockTransport тоже нужен, но сеть не используется
    monkeypatch.setenv("EXTERNAL_BASE_URL", "http://external.test")
    monkeypatch.setenv("EXTERNAL_TIMEOUT_S", "1.0")

    # Подменяем httpx на уровне клиента через monkeypatch: проще всего — подменить base_url
    # а реальный вызов уйдет в MockTransport только если мы подложим его в httpx.AsyncClient.
    #
    # Чтобы не ломать твой код, делаем трюк: подменяем httpx.AsyncClient внутри ExternalClient через monkeypatch.
    from app.integrations import external_client as ext_mod

    real_async_client = httpx.AsyncClient

    class PatchedAsyncClient(httpx.AsyncClient):
        def __init__(self, *args, **kwargs):
            kwargs["transport"] = transport
            super().__init__(*args, **kwargs)

    monkeypatch.setattr(ext_mod.httpx, "AsyncClient", PatchedAsyncClient)

    client = TestClient(main_mod.app)
    r = client.get("/external/ping")
    assert r.status_code == 200
    assert r.json() == {"ok": True, "data": {"pong": True}}

    # возвращаем назад (не обязательно, но пусть будет чисто)
    monkeypatch.setattr(ext_mod.httpx, "AsyncClient", real_async_client)


def test_external_ping_timeout(monkeypatch):
    async def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.TimeoutException("timeout")

    transport = httpx.MockTransport(handler)
    monkeypatch.setenv("EXTERNAL_BASE_URL", "http://external.test")
    monkeypatch.setenv("EXTERNAL_TIMEOUT_S", "0.01")

    from app.integrations import external_client as ext_mod

    real_async_client = httpx.AsyncClient

    class PatchedAsyncClient(httpx.AsyncClient):
        def __init__(self, *args, **kwargs):
            kwargs["transport"] = transport
            super().__init__(*args, **kwargs)

    monkeypatch.setattr(ext_mod.httpx, "AsyncClient", PatchedAsyncClient)

    client = TestClient(main_mod.app)
    r = client.get("/external/ping")
    assert r.status_code == 502
    assert r.json()["detail"].lower().find("timed") != -1

    monkeypatch.setattr(ext_mod.httpx, "AsyncClient", real_async_client)


def test_external_ping_5xx(monkeypatch):
    async def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(503, text="nope")

    transport = httpx.MockTransport(handler)
    monkeypatch.setenv("EXTERNAL_BASE_URL", "http://external.test")

    from app.integrations import external_client as ext_mod

    real_async_client = httpx.AsyncClient

    class PatchedAsyncClient(httpx.AsyncClient):
        def __init__(self, *args, **kwargs):
            kwargs["transport"] = transport
            super().__init__(*args, **kwargs)

    monkeypatch.setattr(ext_mod.httpx, "AsyncClient", PatchedAsyncClient)

    client = TestClient(main_mod.app)
    r = client.get("/external/ping")
    assert r.status_code == 502

    monkeypatch.setattr(ext_mod.httpx, "AsyncClient", real_async_client)
