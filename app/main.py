import asyncio

from fastapi import FastAPI, HTTPException

from app.schemas import (
    ErrorResponse,
    HealthResponse,
    ResultResponse,
    SleepResponse,
    NotifyRequest,
    OkResponse,
)

app = FastAPI(title="hello-api")


@app.get("/", response_model=dict)
def root():
    return {"message": "hello"}


@app.get("/health", response_model=HealthResponse)
def health():
    return {"status": "ok"}


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


@app.post("/notify", response_model=OkResponse)
async def notify(payload: NotifyRequest):
    # Validation is handled by Pydantic (message length 1..200)
    _ = payload.message
    return {"ok": True}
