from __future__ import annotations

import asyncio
import logging

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse, PlainTextResponse

from app.api.routes import router
from app.observability import (
    configure_logging,
    get_or_create_request_id,
    metrics,
    now,
    request_id_var,
)

app = FastAPI(title="hello-api")

configure_logging()
logger = logging.getLogger(__name__)


@app.middleware("http")
async def request_id_and_timing(request: Request, call_next):
    request_id = get_or_create_request_id(request.headers.get("x-request-id"))
    token = request_id_var.set(request_id)

    start = now()
    status_code = 500

    try:
        response = await call_next(request)
        status_code = response.status_code
    except Exception:
        # важно: чтобы X-Request-ID был даже на 500
        response = JSONResponse(status_code=500, content={"detail": "Internal Server Error"})
        status_code = 500
    finally:
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
        response.headers["X-Request-ID"] = request_id
        request_id_var.reset(token)

    return response


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):  # pragma: no cover
    # критично: не потерять WWW-Authenticate
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
        headers=exc.headers,
    )


@app.get("/metrics", response_class=PlainTextResponse)
def metrics_endpoint():
    return PlainTextResponse(
        metrics.render_prometheus(),
        media_type="text/plain; version=0.0.4",
    )


@app.get("/sleep")
async def sleep(seconds: float = 1):
    s = float(seconds)
    if s < 0:
        s = 0.0
    if s > 5:
        s = 5.0

    await asyncio.sleep(s)
    return {"slept": s}


app.include_router(router)
