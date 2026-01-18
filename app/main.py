from fastapi import FastAPI

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
