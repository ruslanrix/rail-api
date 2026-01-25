import pytest

AUTH_ENV_KEYS = [
    "AUTH_MODE",
    "BASIC_USER",
    "BASIC_PASS",
    "JWT_SECRET",
    "JWT_TTL_SECONDS",
]


@pytest.fixture(autouse=True)
def _default_auth_mode_none(monkeypatch: pytest.MonkeyPatch) -> None:
    # Make tests deterministic: do not depend on developer shell/.env
    monkeypatch.setenv("AUTH_MODE", "none")
    for key in AUTH_ENV_KEYS[1:]:
        monkeypatch.delenv(key, raising=False)
