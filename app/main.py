import asyncio

from fastapi import Depends, FastAPI, HTTPException

from app.auth import auth_basic, create_access_token, require_auth, verify_basic
from app.schemas import (
    ErrorResponse,
    HealthResponse,
    NotifyRequest,
    OkResponse,
    ResultResponse,
    SleepResponse,
    TokenResponse,
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


@app.post("/token", response_model=TokenResponse, responses={401: {"model": ErrorResponse}})
def token(credentials=Depends(auth_basic)):
    username = verify_basic(credentials)
    return {"access_token": create_access_token(username), "token_type": "bearer"}


@app.post("/notify", response_model=OkResponse, dependencies=[Depends(require_auth)])
async def notify(payload: NotifyRequest):
    # Validation is handled by Pydantic (message length 1..200)
    _ = payload.message
    return {"ok": True}
