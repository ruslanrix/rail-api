from __future__ import annotations

import os

import pytest

from app.core.settings import get_settings

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