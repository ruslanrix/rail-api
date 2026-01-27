from __future__ import annotations

import base64
import hashlib
import hmac
import json
from datetime import datetime, timedelta, timezone
from secrets import compare_digest

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import (
    HTTPAuthorizationCredentials,
    HTTPBasic,
    HTTPBasicCredentials,
    HTTPBearer,
)

from app.core.settings import get_settings
from app.schemas import ErrorResponse

auth_basic = HTTPBasic(auto_error=False)
auth_bearer = HTTPBearer(auto_error=False)

VALID_AUTH_MODES = {"none", "basic", "jwt"}


def get_auth_mode() -> str:
    mode = (get_settings().auth_mode or "none").lower()
    if mode not in VALID_AUTH_MODES:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Invalid AUTH_MODE",
        )
    return mode


def get_basic_config() -> tuple[str, str]:
    s = get_settings()
    username = (s.basic_user or "").strip()
    password = s.basic_pass or ""
    if not username or not password:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="BASIC_USER and BASIC_PASS are required",
        )
    return username, password


def get_jwt_secret() -> str:
    secret = get_settings().jwt_secret or ""
    if not secret:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="JWT_SECRET is required",
        )
    return secret


def get_jwt_ttl_seconds() -> int:
    ttl = get_settings().jwt_ttl_seconds
    if not isinstance(ttl, int):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="JWT_TTL_SECONDS must be an integer",
        )
    return ttl


def verify_basic(credentials: HTTPBasicCredentials | None) -> str:
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Basic"},
        )

    username, password = get_basic_config()
    is_user_ok = compare_digest(credentials.username, username)
    is_pass_ok = compare_digest(credentials.password, password)

    if not (is_user_ok and is_pass_ok):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username


def _b64url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("utf-8")


def _b64url_decode(data: str) -> bytes:
    padding = "=" * (-len(data) % 4)
    return base64.urlsafe_b64decode(data + padding)


def _sign(message: bytes, secret: str) -> str:
    digest = hmac.new(secret.encode("utf-8"), message, hashlib.sha256).digest()
    return _b64url_encode(digest)


def create_access_token(subject: str) -> str:
    secret = get_jwt_secret()
    ttl_seconds = get_jwt_ttl_seconds()
    expires_at = datetime.now(timezone.utc) + timedelta(seconds=ttl_seconds)

    payload = {"sub": subject, "exp": int(expires_at.timestamp())}
    header = {"alg": "HS256", "typ": "JWT"}

    header_b64 = _b64url_encode(json.dumps(header, separators=(",", ":")).encode("utf-8"))
    payload_b64 = _b64url_encode(json.dumps(payload, separators=(",", ":")).encode("utf-8"))

    signing_input = f"{header_b64}.{payload_b64}".encode("utf-8")
    signature = _sign(signing_input, secret)
    return f"{header_b64}.{payload_b64}.{signature}"


def verify_bearer(credentials: HTTPAuthorizationCredentials | None) -> dict:
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    secret = get_jwt_secret()
    token = credentials.credentials
    parts = token.split(".")
    if len(parts) != 3:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    header_b64, payload_b64, signature = parts
    signing_input = f"{header_b64}.{payload_b64}".encode("utf-8")
    expected_sig = _sign(signing_input, secret)

    if not compare_digest(signature, expected_sig):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        payload_raw = _b64url_decode(payload_b64)
        payload = json.loads(payload_raw)
    except (json.JSONDecodeError, ValueError, TypeError) as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc

    exp = payload.get("exp")
    if exp is None or not isinstance(exp, int):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if datetime.now(timezone.utc).timestamp() >= exp:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expired",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return payload


async def require_auth(request: Request) -> None:
    mode = get_auth_mode()

    if mode == "none":
        return None

    if mode == "basic":
        credentials = await auth_basic(request)
        verify_basic(credentials)
        return None

    if mode == "jwt":
        credentials = await auth_bearer(request)
        verify_bearer(credentials)
        return None

    # на всякий: get_auth_mode уже валидирует
    return None


# FastAPI responses schema for auth-protected endpoints
auth_error_responses = {
    401: {"model": ErrorResponse},
}


_basic_auth_scheme = HTTPBasic(auto_error=False)


def require_basic_auth(
    credentials: HTTPBasicCredentials | None = Depends(_basic_auth_scheme),
) -> str:
    """
    Require Basic auth regardless of AUTH_MODE (used by /token).
    Важно: всегда отдаём WWW-Authenticate: Basic на 401, как ждут тесты.
    """
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Basic"},
        )

    username, password = get_basic_config()
    valid = compare_digest(credentials.username, username) and compare_digest(
        credentials.password, password
    )

    if not valid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Basic"},
        )

    return credentials.username
