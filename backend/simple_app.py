from fastapi import FastAPI

app = FastAPI()

@app.get("/health")
def health():
    return {"status": "ok", "note": "simple app ok"}

@app.get("/ping")
def ping():
    return {"pong": True}