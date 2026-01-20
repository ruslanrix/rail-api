from fastapi import FastAPI
from fastapi import HTTPException

app = FastAPI(title="hello-api")


@app.get("/")
def root():
    return {"message": "hello"}


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/add")
def add(a: int, b: int):
    return {"result": a + b}


@app.get("/mul")
def mul(a: int, b: int):
    return {"result": a * b}


@app.get("/sub")
def sub(a: int, b: int):
    return {"result": a - b}


@app.get("/div")
def div(a: int, b: int):
    if b == 0:
        raise HTTPException(status_code=400, detail="Division by zero")
    return {"result": a / b}
