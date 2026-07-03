from fastapi import FastAPI

app = FastAPI(title="Codebase Intelligence API")

@app.get("/health")
def health():
    return {"status": "ok"}