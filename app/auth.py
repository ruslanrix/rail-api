from __future__ import annotations

import os
import secrets
from datetime import datetime, timedelta, timezone

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import (
    HTTPAuthorizationCredentials,
    HTTPBasic,
    HTTPBasicCredentials,
    HTTPBearer,
)


auth_basic = HTTPBasic(auto_error=False)
auth_bearer = HTTPBearer(auto_error=False)


VALID_AUTH_MODES = {"none", "basic", "jwt"}


def get_auth_mode() -> str:
    mode = os.getenv("AUTH_MODE", "none").lower()
    if mode not in VALID_AUTH_MODES:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Invalid AUTH_MODE",
        )
    return mode


def get_basic_config() -> tuple[str, str]:
    username = os.getenv("BASIC_USER")
    password = os.getenv("BASIC_PASS")
    if not username or not password:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="BASIC_USER and BASIC_PASS are required",
        )
    return username, password


def get_jwt_secret() -> str:
    secret = os.getenv("JWT_SECRET")
    if not secret:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="JWT_SECRET is required",
        )
    return secret


def get_jwt_ttl_seconds() -> int:
    raw = os.getenv("JWT_TTL_SECONDS", "3600")
    try:
        return int(raw)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="JWT_TTL_SECONDS must be an integer",
        ) from exc


def verify_basic(credentials: HTTPBasicCredentials | None) -> str:
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Basic"},
        )
    username, password = get_basic_config()
    is_user_ok = secrets.compare_digest(credentials.username, username)
    is_pass_ok = secrets.compare_digest(credentials.password, password)
    if not (is_user_ok and is_pass_ok):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username


def create_access_token(subject: str) -> str:
    secret = get_jwt_secret()
    ttl_seconds = get_jwt_ttl_seconds()
    expires_at = datetime.now(timezone.utc) + timedelta(seconds=ttl_seconds)
    payload = {"sub": subject, "exp": expires_at}
    return jwt.encode(payload, secret, algorithm="HS256")


def verify_bearer(credentials: HTTPAuthorizationCredentials | None) -> dict:
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    secret = get_jwt_secret()
    try:
        return jwt.decode(credentials.credentials, secret, algorithms=["HS256"])
    except jwt.ExpiredSignatureError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expired",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc
    except jwt.InvalidTokenError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc


def require_auth(
    basic_credentials: HTTPBasicCredentials | None = Depends(auth_basic),
    bearer_credentials: HTTPAuthorizationCredentials | None = Depends(auth_bearer),
) -> None:
    mode = get_auth_mode()
    if mode == "none":
        return None
    if mode == "basic":
        verify_basic(basic_credentials)
        return None
    if mode == "jwt":
        verify_bearer(bearer_credentials)
        return None
    return None
