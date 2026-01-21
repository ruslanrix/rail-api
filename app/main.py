from fastapi import FastAPI, HTTPException

from app.schemas import ErrorResponse, HealthResponse, ResultResponse

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
        # Важно: FastAPI отдаст {"detail": "..."} — мы это документируем через ErrorResponse
        raise HTTPException(status_code=400, detail="Division by zero")
    return {"result": a / b}