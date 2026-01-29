from __future__ import annotations

from uuid import uuid4

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Request

from app.auth import (
    auth_error_responses,
    create_access_token,
    require_auth,
    require_basic_auth,
)
from app.notification import deliver_notification
from app.schemas import (
    ErrorResponse,
    HealthResponse,
    NotifyRequest,
    OkResponse,
    ResultResponse,
    TokenResponse,
)

from app.core.settings import get_settings
from app.integrations.external_client import (
    ExternalClient,
    ExternalClientConfig,
    ExternalUpstreamError,
)

router = APIRouter()


@router.get("/", response_model=dict)
def root():
    return {"message": "hello"}


@router.get("/health", response_model=HealthResponse)
def health():
    return {"status": "ok"}


@router.get("/add", response_model=ResultResponse)
def add(a: int, b: int):
    return {"result": float(a + b)}


@router.get("/mul", response_model=ResultResponse)
def mul(a: int, b: int):
    return {"result": float(a * b)}


@router.get(
    "/sub",
    response_model=ResultResponse,
    responses={400: {"model": ErrorResponse}},
)
def sub(a: int, b: int):
    return {"result": float(a - b)}


@router.get(
    "/div",
    response_model=ResultResponse,
    responses={400: {"model": ErrorResponse}},
)
def div(a: int, b: int):
    if b == 0:
        raise HTTPException(status_code=400, detail="Division by zero")
    return {"result": a / b}


@router.post("/notify", response_model=OkResponse)
async def notify(
    payload: NotifyRequest,
    background_tasks: BackgroundTasks,
    request: Request,
    _: str | None = Depends(require_auth),
):
    request_id = request.headers.get("x-request-id")
    background_tasks.add_task(deliver_notification, payload.message, request_id)
    return {"ok": True}


@router.post(
    "/token",
    response_model=TokenResponse,
    responses=auth_error_responses,
)
def token(subject: str = Depends(require_basic_auth)):
    access_token = create_access_token(subject)
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/_debug/request-id", response_model=dict)
def debug_request_id(request: Request):
    # Convenience endpoint for local verification (can be removed later)
    return {"request_id": request.headers.get("x-request-id") or str(uuid4())}


@router.get("/external/ping")
async def external_ping():
    s = get_settings()
    cfg = ExternalClientConfig(
        base_url=s.external_base_url,
        timeout_s=float(s.external_timeout_s),
    )
    client = ExternalClient(cfg)

    try:
        data = await client.ping()
    except ExternalUpstreamError as e:
        raise HTTPException(status_code=502, detail=str(e)) from e

    return {"ok": True, "data": data}
