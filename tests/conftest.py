import pytest

AUTH_ENV_KEYS = [
    "AUTH_MODE",
    "BASIC_USER",
    "BASIC_PASS",
    "JWT_SECRET",
    "JWT_TTL_SECONDS",
]


@pytest.fixture(autouse=True)
def _clear_auth_env(monkeypatch: pytest.MonkeyPatch):
    for key in AUTH_ENV_KEYS:
        monkeypatch.delenv(key, raising=False)
