# app/main.py
from fastapi import FastAPI

from app.api.v1.endpoints import auth

app = FastAPI(
    title="Rubika Bot SaaS",
    version="0.1.0",
)

app.include_router(auth.router, prefix="/api/v1")


@app.get("/")
async def root():
    return {"status": "ok"}


@app.get("/health")
async def health():
    return {"status": "healthy"}
