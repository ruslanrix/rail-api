from __future__ import annotations

from fastapi.testclient import TestClient

import app.main as main_mod
from app.core import settings as settings_mod


def _reset_settings_cache() -> None:
    # если у тебя get_settings() с кешем — сбрось его
    if hasattr(settings_mod.get_settings, "cache_clear"):
        settings_mod.get_settings.cache_clear()  # type: ignore[attr-defined]


def test_cors_disabled_by_default_no_cors_headers():
    client = TestClient(main_mod.app)
    r = client.get("/health", headers={"Origin": "https://example.com"})
    assert "access-control-allow-origin" not in r.headers


def test_cors_enabled_allows_origin(monkeypatch):
    monkeypatch.setenv("CORS_ALLOW_ORIGINS", "https://example.com")
    _reset_settings_cache()

    # импортировать app заново нельзя красиво, поэтому проще:
    # если у тебя есть create_app() — используй его.
    # если нет, делаем минимально: перезагружаем модуль.
    import importlib

    import app.main as reloaded

    importlib.reload(reloaded)

    client = TestClient(reloaded.app)

    r = client.get("/health", headers={"Origin": "https://example.com"})
    assert r.headers.get("access-control-allow-origin") == "https://example.com"
