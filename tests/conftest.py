from __future__ import annotations

from pathlib import Path

import os

import pytest
from fastapi.testclient import TestClient

from app.core.settings import get_settings
from app.main import app
from app.models import Base

# Keep list explicit so tests are deterministic.
_ENV_KEYS_TO_CLEAR = [
    "APP_NAME",
    "AUTH_MODE",
    "BASIC_USER",
    "BASIC_PASS",
    "JWT_SECRET",
    "JWT_TTL_SECONDS",
    "DATABASE_URL",
    "DB_ECHO",
    "EXTERNAL_BASE_URL",
    "EXTERNAL_TIMEOUT_S",
]


@pytest.fixture(autouse=True)
def _clear_settings_cache():
    # Tests rely on Settings being cached but resettable between cases.
    get_settings.cache_clear()

    # Avoid environment leaking across tests.
    for k in _ENV_KEYS_TO_CLEAR:
        os.environ.pop(k, None)

    yield

    # Defensive cleanup after test as well.
    get_settings.cache_clear()
    for k in _ENV_KEYS_TO_CLEAR:
        os.environ.pop(k, None)


@pytest.fixture()
def client() -> TestClient:
    return TestClient(app)


@pytest.fixture()
def db_url(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> str:
    # Изолированная БД на каждый тест/набор — без зависимости от rail_api.db
    url = f"sqlite+pysqlite:///{tmp_path / 'test.db'}"
    monkeypatch.setenv("DATABASE_URL", url)

    # Важно: settings закешированы через lru_cache
    get_settings.cache_clear()
    return url


@pytest.fixture()
def init_db(db_url: str) -> None:
    # Импортим после подмены env, чтобы engine взял правильный URL
    from app.core.db import engine

    Base.metadata.create_all(bind=engine)
