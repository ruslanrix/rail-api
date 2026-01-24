import asyncio
import logging

from fastapi import Depends, FastAPI, HTTPException, Request, Response
from fastapi.responses import JSONResponse

from app.auth import auth_basic, create_access_token, require_auth, verify_basic
from app.observability import (
    configure_logging,
    get_or_create_request_id,
    metrics,
    now,
    request_id_var,
)
from app.schemas import (
    ErrorResponse,
    HealthResponse,
    NotifyRequest,
    OkResponse,
    ResultResponse,
    SleepResponse,
    TokenResponse,
)

configure_logging()
logger = logging.getLogger(__name__)

app = FastAPI(title="hello-api")


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    request_id = getattr(request.state, "request_id", request_id_var.get("-"))
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal Server Error"},
        headers={"X-Request-ID": request_id},
    )


@app.middleware("http")
async def observability_middleware(request: Request, call_next):
    request_id = get_or_create_request_id(request.headers.get("X-Request-ID"))
    request.state.request_id = request_id
    token = request_id_var.set(request_id)

    start = now()
    response: Response | None = None
    status_code = 500
    duration_s = 0.0
    try:
        response = await call_next(request)
        status_code = response.status_code
        return response
    except Exception:
        duration_s = now() - start
        metrics.record(
            method=request.method,
            path=request.url.path,
            status=status_code,
            duration_s=duration_s,
        )
        logger.exception(
            "request failed method=%s path=%s status=%s duration_ms=%.2f",
            request.method,
            request.url.path,
            status_code,
            duration_s * 1000,
        )
        raise
    finally:
        if response is not None:
            response.headers["X-Request-ID"] = request_id
            duration_s = now() - start
            metrics.record(
                method=request.method,
                path=request.url.path,
                status=status_code,
                duration_s=duration_s,
            )
            logger.info(
                "request complete method=%s path=%s status=%s duration_ms=%.2f",
                request.method,
                request.url.path,
                status_code,
                duration_s * 1000,
            )
        request_id_var.reset(token)


@app.get("/", response_model=dict)
def root():
    return {"message": "hello"}


@app.get("/health", response_model=HealthResponse)
def health():
    return {"status": "ok"}


@app.get("/metrics", response_model=None)
def metrics_endpoint():
    return Response(
        content=metrics.render_prometheus(),
        media_type="text/plain; version=0.0.4; charset=utf-8",
    )


@app.get("/add", response_model=ResultResponse)
def add(a: int, b: int):
    return {"result": a + b}


@app.get("/mul", response_model=ResultResponse)
def mul(a: int, b: int):
    return {"result": a * b}


@app.get("/sub", response_model=ResultResponse)
def sub(a: int, b: int):
    return {"result": a - b}


@app.get(
    "/div",
    response_model=ResultResponse,
    responses={400: {"model": ErrorResponse}},
)
def div(a: int, b: int):
    if b == 0:
        raise HTTPException(status_code=400, detail="Division by zero")
    return {"result": a / b}


@app.get("/sleep", response_model=SleepResponse)
async def sleep(seconds: float = 1):
    # clamp 0..5 (float/int allowed)
    s = float(seconds)
    if s < 0:
        s = 0.0
    elif s > 5:
        s = 5.0

    if s > 0:
        await asyncio.sleep(s)

    return {"slept": s}


@app.post("/token", response_model=TokenResponse, responses={401: {"model": ErrorResponse}})
def token(credentials=Depends(auth_basic)):
    username = verify_basic(credentials)
    return {"access_token": create_access_token(username), "token_type": "bearer"}


@app.post("/notify", response_model=OkResponse, dependencies=[Depends(require_auth)])
async def notify(payload: NotifyRequest):
    # Validation is handled by Pydantic (message length 1..200)
    _ = payload.message
    return {"ok": True}
