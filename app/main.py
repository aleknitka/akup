from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles

from app.routers import evidence, organizations, users

STATIC_DIR = Path(__file__).parent / "static"


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
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.get("/")
async def root() -> RedirectResponse:
    return RedirectResponse(url="/static/index.html")


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}
