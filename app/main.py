from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.routers import evidence, organizations, users


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    yield


app = FastAPI(
    title="AKUP Evidence API",
    description="Record evidence for autorskie koszty uzyskania przychodu",
    version="0.1.0",
    lifespan=lifespan,
)

app.include_router(organizations.router)
app.include_router(users.router)
app.include_router(evidence.router)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}
